import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import jsonschema

from .intent import SchemaValidationError

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "schemas"
    / "meta"
    / "implementation_report.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "IMPL-"

_PACKET_ID_RE = r"^TPACKET-[0-9]{8}-[0-9]{3}$"

_VALID_STATUSES = frozenset({"completed", "partial", "failed", "blocked"})
_VALID_CHANGE_TYPES = frozenset({"created", "modified", "deleted", "renamed"})
_VALID_ACCEPTANCE_STATUSES = frozenset({"passed", "failed", "not_evaluated"})
_VALID_COMMAND_STATUSES = frozenset({"passed", "failed", "skipped"})

_CHANGED_FILE_KEYS = frozenset({"path", "change_type"})
_CREATED_ARTIFACT_KEYS = frozenset(
    {"contract_name", "contract_version", "artifact_id", "path"}
)
_BLOCKER_KEYS = frozenset({"code", "message", "path"})
_COMMAND_RUN_KEYS = frozenset({"command", "exit_code", "status"})


def _validate_non_empty_string(value: object, label: str) -> None:
    if not isinstance(value, str) or len(value) < 1:
        raise ValueError(f"{label} must be a non-empty string")


def _validate_string_list(value: object, label: str, min_items: int = 0) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    if len(value) < min_items:
        raise ValueError(f"{label} must have at least {min_items} item(s)")
    for i, item in enumerate(value):
        if not isinstance(item, str) or len(item) < 1:
            raise ValueError(f"{label}[{i}] must be a non-empty string")


def _validate_changed_files(changed_files: object) -> None:
    if not isinstance(changed_files, list):
        raise ValueError("changed_files must be a list")
    if len(changed_files) < 1:
        raise ValueError("changed_files must have at least 1 item(s)")

    seen_pairs: set[tuple[str, str]] = set()
    for i, item in enumerate(changed_files):
        if not isinstance(item, dict):
            raise ValueError(f"changed_files[{i}] must be a dict")

        for key in ("path", "change_type"):
            if key not in item:
                raise ValueError(f"changed_files[{i}] must have a {key!r} key")

        extra = set(item.keys()) - _CHANGED_FILE_KEYS
        if extra:
            raise ValueError(
                f"changed_files[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        item_path = item["path"]
        _validate_non_empty_string(item_path, f"changed_files[{i}].path")

        change_type = item["change_type"]
        if change_type not in _VALID_CHANGE_TYPES:
            raise ValueError(
                f"changed_files[{i}].change_type {change_type!r} must be one of: "
                f"{', '.join(sorted(_VALID_CHANGE_TYPES))}"
            )

        pair = (item_path, change_type)
        if pair in seen_pairs:
            raise ValueError(
                f"Duplicate changed_file (path={item_path!r}, "
                f"change_type={change_type!r}) in changed_files"
            )
        seen_pairs.add(pair)


def _validate_created_artifacts(created_artifacts: object) -> None:
    if not isinstance(created_artifacts, list):
        raise ValueError("created_artifacts must be a list")
    if len(created_artifacts) < 1:
        raise ValueError("created_artifacts must have at least 1 item(s)")

    seen_pairs: set[tuple[str, str]] = set()
    for i, item in enumerate(created_artifacts):
        if not isinstance(item, dict):
            raise ValueError(f"created_artifacts[{i}] must be a dict")

        for key in ("contract_name", "artifact_id", "path"):
            if key not in item:
                raise ValueError(f"created_artifacts[{i}] must have a {key!r} key")

        extra = set(item.keys()) - _CREATED_ARTIFACT_KEYS
        if extra:
            raise ValueError(
                f"created_artifacts[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        contract_name = item["contract_name"]
        _validate_non_empty_string(
            contract_name, f"created_artifacts[{i}].contract_name"
        )

        artifact_id = item["artifact_id"]
        _validate_non_empty_string(
            artifact_id, f"created_artifacts[{i}].artifact_id"
        )

        item_path = item["path"]
        _validate_non_empty_string(item_path, f"created_artifacts[{i}].path")

        contract_version = item.get("contract_version")
        if contract_version is not None and not isinstance(contract_version, str):
            raise ValueError(
                f"created_artifacts[{i}].contract_version must be a string if provided"
            )

        pair = (contract_name, artifact_id)
        if pair in seen_pairs:
            raise ValueError(
                f"Duplicate created_artifact (contract_name={contract_name!r}, "
                f"artifact_id={artifact_id!r}) in created_artifacts"
            )
        seen_pairs.add(pair)


def _validate_blockers(blockers: object) -> None:
    if not isinstance(blockers, list):
        raise ValueError("blockers must be a list")

    seen_codes: set[str] = set()
    for i, item in enumerate(blockers):
        if not isinstance(item, dict):
            raise ValueError(f"blockers[{i}] must be a dict")

        for key in ("code", "message"):
            if key not in item:
                raise ValueError(f"blockers[{i}] must have a {key!r} key")

        extra = set(item.keys()) - _BLOCKER_KEYS
        if extra:
            raise ValueError(
                f"blockers[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        code = item["code"]
        _validate_non_empty_string(code, f"blockers[{i}].code")

        if code in seen_codes:
            raise ValueError(f"Duplicate blocker code {code!r} in blockers")
        seen_codes.add(code)

        message = item["message"]
        _validate_non_empty_string(message, f"blockers[{i}].message")

        path_val = item.get("path")
        if path_val is not None and not isinstance(path_val, str):
            raise ValueError(f"blockers[{i}].path must be a string if provided")


def _validate_commands_run(commands_run: object) -> None:
    if not isinstance(commands_run, list):
        raise ValueError("commands_run must be a list if provided")

    seen_commands: set[str] = set()
    for i, item in enumerate(commands_run):
        if not isinstance(item, dict):
            raise ValueError(f"commands_run[{i}] must be a dict")

        for key in ("command", "exit_code"):
            if key not in item:
                raise ValueError(f"commands_run[{i}] must have a {key!r} key")

        extra = set(item.keys()) - _COMMAND_RUN_KEYS
        if extra:
            raise ValueError(
                f"commands_run[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        command = item["command"]
        _validate_non_empty_string(command, f"commands_run[{i}].command")

        if command in seen_commands:
            raise ValueError(
                f"Duplicate command {command!r} in commands_run"
            )
        seen_commands.add(command)

        exit_code = item["exit_code"]
        if not isinstance(exit_code, int):
            raise ValueError(
                f"commands_run[{i}].exit_code must be an integer"
            )
        if exit_code < 0:
            raise ValueError(
                f"commands_run[{i}].exit_code must be >= 0"
            )

        status = item.get("status")
        if status is not None and status not in _VALID_COMMAND_STATUSES:
            raise ValueError(
                f"commands_run[{i}].status {status!r} must be one of: "
                f"{', '.join(sorted(_VALID_COMMAND_STATUSES))}"
            )


def _generate_deterministic_id(inputs: dict[str, object]) -> str:
    stable = json.dumps(inputs, sort_keys=True, default=str, ensure_ascii=True)
    digest = hashlib.sha256(stable.encode("utf-8")).digest()
    numeric = int.from_bytes(digest[:11], "big")
    part1 = numeric % (10**8)
    part2 = (numeric // (10**8)) % (10**3)
    return f"{_ID_PREFIX}{part1:08d}-{part2:03d}"


def _generate_deterministic_created_at(inputs: dict[str, object]) -> str:
    stable = json.dumps(inputs, sort_keys=True, default=str, ensure_ascii=True)
    digest = hashlib.sha256(stable.encode("utf-8")).digest()
    seconds_offset = int.from_bytes(digest[:4], "big") % (365 * 24 * 60 * 60)
    created = _BASE_EPOCH + timedelta(seconds=seconds_offset)
    return created.isoformat()


def build_implementation_report(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build an implementation_report artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            packet_id (str, required): Packet ID matching ^TPACKET-[0-9]{8}-[0-9]{3}$.
            status (str, required): One of "completed", "partial", "failed", "blocked".
            changed_files (list[dict], required): Non-empty list of changed file entries.
            created_artifacts (list[dict], required): Non-empty list of created artifact entries.
            acceptance_status (str, required): One of "passed", "failed", "not_evaluated".
            blockers (list[dict], required): List of blocker entries.
            commands_run (list[dict], optional): List of command run entries.
            deviations (list[str], optional): List of non-empty strings.
            follow_up_tasks (list[str], optional): List of non-empty strings.
            human_summary (str, optional): Human-readable summary.
        output_path: Optional filesystem path. If provided, writes JSON artifact.

    Returns:
        Dict representing the complete, schema-valid implementation_report artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.
    """
    # --- Validate required inputs ---
    required = {
        "packet_id",
        "status",
        "changed_files",
        "created_artifacts",
        "acceptance_status",
        "blockers",
    }
    for key in sorted(required):
        if key not in inputs:
            raise ValueError(f"Missing required input: {key!r}")

    packet_id = inputs["packet_id"]
    _validate_non_empty_string(packet_id, "packet_id")
    if not re.match(_PACKET_ID_RE, packet_id):
        raise ValueError(
            f"packet_id {packet_id!r} must match pattern {_PACKET_ID_RE}"
        )

    status = inputs["status"]
    if status not in _VALID_STATUSES:
        raise ValueError(
            f"Invalid status {status!r}, must be one of: "
            f"{', '.join(sorted(_VALID_STATUSES))}"
        )

    changed_files = inputs["changed_files"]
    _validate_changed_files(changed_files)

    created_artifacts = inputs["created_artifacts"]
    _validate_created_artifacts(created_artifacts)

    acceptance_status = inputs["acceptance_status"]
    if acceptance_status not in _VALID_ACCEPTANCE_STATUSES:
        raise ValueError(
            f"Invalid acceptance_status {acceptance_status!r}, must be one of: "
            f"{', '.join(sorted(_VALID_ACCEPTANCE_STATUSES))}"
        )

    blockers = inputs["blockers"]
    _validate_blockers(blockers)

    # --- Consistency checks ---
    if status in ("failed", "blocked") and len(blockers) < 1:
        raise ValueError(
            f"status is {status!r} but blockers is empty; "
            f"at least one blocker is required when status is failed or blocked"
        )

    if status == "completed" and acceptance_status == "failed":
        raise ValueError(
            "status 'completed' with acceptance_status 'failed' is inconsistent"
        )

    # --- Validate optional inputs ---
    commands_run = inputs.get("commands_run")
    if commands_run is not None:
        _validate_commands_run(commands_run)

    deviations = inputs.get("deviations")
    if deviations is not None:
        _validate_string_list(deviations, "deviations")

    follow_up_tasks = inputs.get("follow_up_tasks")
    if follow_up_tasks is not None:
        _validate_string_list(follow_up_tasks, "follow_up_tasks")

    human_summary = inputs.get("human_summary")
    if human_summary is not None and not isinstance(human_summary, str):
        raise ValueError("human_summary must be a string if provided")

    # --- Build deterministic artifact fields ---
    report_id = _generate_deterministic_id(inputs)
    created_at = _generate_deterministic_created_at(inputs)

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "implementation_report",
        "contract_version": "2.0",
        "report_id": report_id,
        "packet_id": packet_id,
        "created_at": created_at,
        "status": status,
        "changed_files": changed_files,
        "created_artifacts": created_artifacts,
        "acceptance_status": acceptance_status,
        "blockers": blockers,
    }

    if commands_run is not None:
        artifact["commands_run"] = commands_run
    if deviations is not None:
        artifact["deviations"] = deviations
    if follow_up_tasks is not None:
        artifact["follow_up_tasks"] = follow_up_tasks
    if human_summary is not None:
        artifact["human_summary"] = human_summary

    # --- Validate against implementation_report schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Implementation report artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return artifact
