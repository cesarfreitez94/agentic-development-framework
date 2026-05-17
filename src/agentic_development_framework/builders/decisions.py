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
    / "decisions.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "DEC-"
_ID_PATTERN = re.compile(r"^DEC-[0-9]{8}-[0-9]{3}$")

_VALID_DECISION_TYPES = frozenset(
    {"user_confirmation", "policy_gate", "review_gate", "git_gate", "workflow", "architecture"}
)
_VALID_STATUSES = frozenset({"pending", "resolved", "cancelled"})

_RELATED_ARTIFACT_KEYS = frozenset({"contract_name", "artifact_id", "path"})


def _validate_non_empty_string(value: object, label: str) -> None:
    if not isinstance(value, str) or len(value) < 1:
        raise ValueError(f"{label} must be a non-empty string")


def _validate_options(value: object) -> None:
    if not isinstance(value, list):
        raise ValueError("options must be a list")
    if len(value) < 2:
        raise ValueError("options must have at least 2 item(s)")
    seen: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, str) or len(item) < 1:
            raise ValueError(f"options[{i}] must be a non-empty string")
        if item in seen:
            raise ValueError(f"Duplicate value {item!r} in options")
        seen.add(item)


def _validate_required_by(value: object) -> None:
    if not isinstance(value, list):
        raise ValueError("required_by must be a list")
    if len(value) < 1:
        raise ValueError("required_by must have at least 1 item(s)")
    seen: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, str) or len(item) < 1:
            raise ValueError(f"required_by[{i}] must be a non-empty string")
        if item in seen:
            raise ValueError(f"Duplicate value {item!r} in required_by")
        seen.add(item)


def _validate_related_artifacts(value: object) -> None:
    if not isinstance(value, list):
        raise ValueError("related_artifacts must be a list")
    seen_tuples: set[tuple[str, Optional[str], Optional[str]]] = set()
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"related_artifacts[{i}] must be a dict")

        extra = set(item.keys()) - _RELATED_ARTIFACT_KEYS
        if extra:
            raise ValueError(
                f"related_artifacts[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        contract_name = item.get("contract_name")
        if contract_name is None:
            raise ValueError(
                f"related_artifacts[{i}] must have a 'contract_name' key"
            )
        _validate_non_empty_string(contract_name, f"related_artifacts[{i}].contract_name")

        artifact_id = item.get("artifact_id")
        if artifact_id is not None and not isinstance(artifact_id, str):
            raise ValueError(
                f"related_artifacts[{i}].artifact_id must be a string if provided"
            )

        path = item.get("path")
        if path is not None and not isinstance(path, str):
            raise ValueError(
                f"related_artifacts[{i}].path must be a string if provided"
            )

        dup_key = (contract_name, artifact_id, path)
        if dup_key in seen_tuples:
            raise ValueError(
                f"Duplicate related_artifact (contract_name={contract_name!r}, "
                f"artifact_id={artifact_id!r}, path={path!r})"
            )
        seen_tuples.add(dup_key)


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


def _generate_deterministic_resolved_at(inputs: dict[str, object]) -> str:
    stable = json.dumps(
        {"_salt": "resolved", **inputs}, sort_keys=True, default=str, ensure_ascii=True
    )
    digest = hashlib.sha256(stable.encode("utf-8")).digest()
    seconds_offset = int.from_bytes(digest[:4], "big") % (365 * 24 * 60 * 60)
    created = _BASE_EPOCH + timedelta(seconds=seconds_offset)
    return created.isoformat()


def build_decisions(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build a decisions artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            decision_type (str, required): One of "user_confirmation", "policy_gate",
                "review_gate", "git_gate", "workflow", "architecture".
            status (str, required): One of "pending", "resolved", "cancelled".
            question (str, required): Non-empty decision question.
            options (list[str], required): List of at least 2 unique non-empty strings.
            selected_option (str | None, required): Selected option or None.
            required_by (list[str], required): Non-empty list of non-empty strings.
            resolved_at (str, optional): ISO 8601 date-time string.
            rationale (str, optional): Decision rationale.
            related_artifacts (list[dict], optional): List of related artifact refs.
            expires_at (str, optional): ISO 8601 date-time string.
            supersedes_decision_id (str, optional): ID matching ^DEC-[0-9]{8}-[0-9]{3}$.
            human_summary (str, optional): Human-readable summary.
        output_path: Optional filesystem path. If provided, writes JSON artifact.

    Returns:
        Dict representing the complete, schema-valid decisions artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.
    """
    # --- Validate required inputs ---
    required = {
        "decision_type",
        "status",
        "question",
        "options",
        "selected_option",
        "required_by",
    }
    for key in sorted(required):
        if key not in inputs:
            raise ValueError(f"Missing required input: {key!r}")

    decision_type = inputs["decision_type"]
    _validate_non_empty_string(decision_type, "decision_type")
    if decision_type not in _VALID_DECISION_TYPES:
        raise ValueError(
            f"Invalid decision_type {decision_type!r}, must be one of: "
            f"{', '.join(sorted(_VALID_DECISION_TYPES))}"
        )

    status = inputs["status"]
    _validate_non_empty_string(status, "status")
    if status not in _VALID_STATUSES:
        raise ValueError(
            f"Invalid status {status!r}, must be one of: "
            f"{', '.join(sorted(_VALID_STATUSES))}"
        )

    question = inputs["question"]
    _validate_non_empty_string(question, "question")

    options = inputs["options"]
    _validate_options(options)

    selected_option = inputs["selected_option"]
    if selected_option is not None and not isinstance(selected_option, str):
        raise ValueError("selected_option must be a string or None")

    required_by = inputs["required_by"]
    _validate_required_by(required_by)

    # --- Validate optional inputs ---
    resolved_at = inputs.get("resolved_at")
    if resolved_at is not None and not isinstance(resolved_at, str):
        raise ValueError("resolved_at must be a string if provided")

    rationale = inputs.get("rationale")
    if rationale is not None and not isinstance(rationale, str):
        raise ValueError("rationale must be a string if provided")

    related_artifacts = inputs.get("related_artifacts")
    if related_artifacts is not None:
        _validate_related_artifacts(related_artifacts)

    expires_at = inputs.get("expires_at")
    if expires_at is not None and not isinstance(expires_at, str):
        raise ValueError("expires_at must be a string if provided")

    supersedes_decision_id = inputs.get("supersedes_decision_id")
    if supersedes_decision_id is not None:
        if not isinstance(supersedes_decision_id, str):
            raise ValueError("supersedes_decision_id must be a string if provided")
        if not _ID_PATTERN.match(supersedes_decision_id):
            raise ValueError(
                f"supersedes_decision_id {supersedes_decision_id!r} must match pattern "
                f"'^DEC-[0-9]{{8}}-[0-9]{{3}}$'"
            )

    human_summary = inputs.get("human_summary")
    if human_summary is not None and not isinstance(human_summary, str):
        raise ValueError("human_summary must be a string if provided")

    # --- Consistency checks ---
    if isinstance(selected_option, str):
        if selected_option not in options:
            raise ValueError(
                f"selected_option {selected_option!r} is not in options"
            )

    if status == "pending":
        if selected_option is not None:
            raise ValueError(
                "selected_option must be None when status is 'pending'"
            )
        if resolved_at is not None:
            raise ValueError(
                "resolved_at must not be provided when status is 'pending'"
            )

    if status == "resolved":
        if not isinstance(selected_option, str):
            raise ValueError(
                "selected_option must be a string when status is 'resolved'"
            )
        if selected_option not in options:
            raise ValueError(
                f"selected_option {selected_option!r} is not in options"
            )

    if status == "cancelled" and isinstance(selected_option, str):
        if selected_option not in options:
            raise ValueError(
                f"selected_option {selected_option!r} is not in options"
            )

    # --- Build deterministic artifact fields ---
    decision_id = _generate_deterministic_id(inputs)

    if supersedes_decision_id is not None and supersedes_decision_id == decision_id:
        raise ValueError(
            "supersedes_decision_id must not equal the generated decision_id"
        )

    created_at = _generate_deterministic_created_at(inputs)

    # --- Resolve resolved_at ---
    if status == "resolved" and resolved_at is None:
        resolved_at = _generate_deterministic_resolved_at(inputs)

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "decisions",
        "contract_version": "2.0",
        "decision_id": decision_id,
        "created_at": created_at,
        "decision_type": decision_type,
        "status": status,
        "question": question,
        "options": options,
        "selected_option": selected_option,
        "required_by": required_by,
    }

    if resolved_at is not None:
        artifact["resolved_at"] = resolved_at
    if rationale is not None:
        artifact["rationale"] = rationale
    if related_artifacts is not None:
        artifact["related_artifacts"] = related_artifacts
    if expires_at is not None:
        artifact["expires_at"] = expires_at
    if supersedes_decision_id is not None:
        artifact["supersedes_decision_id"] = supersedes_decision_id
    if human_summary is not None:
        artifact["human_summary"] = human_summary

    # --- Validate against decisions schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Decisions artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return artifact
