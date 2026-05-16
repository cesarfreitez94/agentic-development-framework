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
    / "task_packet.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "TPACKET-"

_PLAN_ID_RE = r"^PLAN-[0-9]{8}-[0-9]{3}$"
_TASK_ID_RE = r"^TASK-[0-9]{8}-[0-9]{3}$"

_VALID_OPERATIONS = frozenset(
    {
        "read",
        "create_schema",
        "modify_schema",
        "validate_schema",
        "run_tests",
        "request_git_operation",
    }
)


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


def _check_no_duplicates(value: list[object], label: str) -> None:
    seen: set[str] = set()
    for item in value:
        s = str(item)
        if s in seen:
            raise ValueError(f"Duplicate value {s!r} in {label}")
        seen.add(s)


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


def build_task_packet(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    # --- Validate required inputs ---
    required = {
        "plan_id",
        "task_id",
        "objective",
        "allowed_files",
        "forbidden_files",
        "allowed_operations",
        "acceptance_criteria",
        "inputs_required",
    }
    for key in sorted(required):
        if key not in inputs:
            raise ValueError(f"Missing required input: {key!r}")

    plan_id = inputs["plan_id"]
    _validate_non_empty_string(plan_id, "plan_id")
    if not re.match(_PLAN_ID_RE, plan_id):
        raise ValueError(
            f"plan_id {plan_id!r} must match pattern {_PLAN_ID_RE}"
        )

    task_id = inputs["task_id"]
    _validate_non_empty_string(task_id, "task_id")
    if not re.match(_TASK_ID_RE, task_id):
        raise ValueError(
            f"task_id {task_id!r} must match pattern {_TASK_ID_RE}"
        )

    objective = inputs["objective"]
    _validate_non_empty_string(objective, "objective")

    allowed_files = inputs["allowed_files"]
    _validate_string_list(allowed_files, "allowed_files", min_items=1)
    _check_no_duplicates(allowed_files, "allowed_files")

    forbidden_files = inputs["forbidden_files"]
    _validate_string_list(forbidden_files, "forbidden_files")
    _check_no_duplicates(forbidden_files, "forbidden_files")

    allowed_set = frozenset(allowed_files)
    forbidden_set = frozenset(forbidden_files)
    overlap = allowed_set & forbidden_set
    if overlap:
        raise ValueError(
            f"allowed_files and forbidden_files overlap: "
            f"{', '.join(sorted(overlap))}"
        )

    allowed_operations = inputs["allowed_operations"]
    _validate_string_list(allowed_operations, "allowed_operations", min_items=1)
    _check_no_duplicates(allowed_operations, "allowed_operations")
    for i, op in enumerate(allowed_operations):
        if op not in _VALID_OPERATIONS:
            raise ValueError(
                f"Invalid operation {op!r} in allowed_operations[{i}], "
                f"must be one of: {', '.join(sorted(_VALID_OPERATIONS))}"
            )

    acceptance_criteria = inputs["acceptance_criteria"]
    _validate_string_list(acceptance_criteria, "acceptance_criteria", min_items=1)
    _check_no_duplicates(acceptance_criteria, "acceptance_criteria")

    inputs_required = inputs["inputs_required"]
    _validate_string_list(inputs_required, "inputs_required", min_items=1)
    _check_no_duplicates(inputs_required, "inputs_required")

    # --- Validate optional inputs ---
    dependencies = inputs.get("dependencies")
    if dependencies is not None:
        if not isinstance(dependencies, list):
            raise ValueError("dependencies must be a list if provided")
        dep_seen: set[str] = set()
        for i, dep in enumerate(dependencies):
            if not isinstance(dep, str) or not re.match(_TASK_ID_RE, dep):
                raise ValueError(
                    f"dependencies[{i}] {dep!r} must match pattern {_TASK_ID_RE}"
                )
            if dep == task_id:
                raise ValueError(
                    f"dependencies includes self-dependency on {dep!r}"
                )
            if dep in dep_seen:
                raise ValueError(
                    f"Duplicate dependency {dep!r} in dependencies"
                )
            dep_seen.add(dep)

    test_requirements = inputs.get("test_requirements")
    if test_requirements is not None:
        _validate_string_list(test_requirements, "test_requirements")

    policy_refs = inputs.get("policy_refs")
    if policy_refs is not None:
        _validate_string_list(policy_refs, "policy_refs")

    risk_notes = inputs.get("risk_notes")
    if risk_notes is not None:
        _validate_string_list(risk_notes, "risk_notes")

    human_summary = inputs.get("human_summary")
    if human_summary is not None and not isinstance(human_summary, str):
        raise ValueError("human_summary must be a string if provided")

    # --- Build deterministic artifact fields ---
    packet_id = _generate_deterministic_id(inputs)
    created_at = _generate_deterministic_created_at(inputs)

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "task_packet",
        "contract_version": "2.0",
        "packet_id": packet_id,
        "plan_id": plan_id,
        "task_id": task_id,
        "created_at": created_at,
        "objective": objective,
        "allowed_files": allowed_files,
        "forbidden_files": forbidden_files,
        "allowed_operations": allowed_operations,
        "acceptance_criteria": acceptance_criteria,
        "inputs_required": inputs_required,
    }

    if dependencies is not None:
        artifact["dependencies"] = dependencies
    if test_requirements is not None:
        artifact["test_requirements"] = test_requirements
    if policy_refs is not None:
        artifact["policy_refs"] = policy_refs
    if risk_notes is not None:
        artifact["risk_notes"] = risk_notes
    if human_summary is not None:
        artifact["human_summary"] = human_summary

    # --- Validate against task_packet schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Task packet artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )

    return artifact
