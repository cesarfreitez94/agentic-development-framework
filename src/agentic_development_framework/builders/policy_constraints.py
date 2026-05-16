import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import jsonschema

from .intent import SchemaValidationError

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "schemas"
    / "meta"
    / "policy_constraints.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "POLICY-"

_VALID_OPERATIONS = frozenset(
    {
        "design_schema",
        "read_contract",
        "validate_schema",
        "create_task_packet",
        "build_context_bundle",
        "run_tests",
        "create_review_report",
        "request_git_operation",
        "execute_git_operation",
        "create_agent",
        "create_prompt",
        "modify_generator",
        "write_markdown_operational",
        "commit",
        "push",
        "open_pr",
        "merge_pr",
    }
)

_VALID_CHECKS = frozenset(
    {
        "issue_required_before_code",
        "no_direct_commit_to_main",
        "tests_required_before_pr",
        "changelog_required",
        "manual_review_before_main_pr",
    }
)

_INTENT_ID_RE = r"^INTENT-[0-9]{8}-[0-9]{3}$"


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


def build_policy_constraints(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build a policy_constraints artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            intent_id (str, required): Intent ID matching ^INTENT-[0-9]{8}-[0-9]{3}$.
            policy_refs (list[str], required): Non-empty list of policy references.
            allowed_operations (list[str], required): Non-empty list of allowed operations.
            blocked_operations (list[str], required): List of blocked operations.
            required_checks (list[str], required): Non-empty list of required checks.
            requires_user_confirmation (bool, required): Whether user confirmation is needed.
            rationale (str, optional): Rationale for the constraints.
            human_summary (str, optional): Human-readable summary.
        output_path: Optional filesystem path. If provided, writes JSON artifact.

    Returns:
        Dict representing the complete, schema-valid policy_constraints artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.
    """
    # --- Validate required inputs ---
    required = {
        "intent_id",
        "policy_refs",
        "allowed_operations",
        "blocked_operations",
        "required_checks",
        "requires_user_confirmation",
    }
    for key in sorted(required):
        if key not in inputs:
            raise ValueError(f"Missing required input: {key!r}")

    intent_id = inputs["intent_id"]
    _validate_non_empty_string(intent_id, "intent_id")
    import re

    if not re.match(_INTENT_ID_RE, intent_id):
        raise ValueError(
            f"intent_id {intent_id!r} must match pattern {_INTENT_ID_RE}"
        )

    policy_refs = inputs["policy_refs"]
    _validate_string_list(policy_refs, "policy_refs", min_items=1)

    allowed_operations = inputs["allowed_operations"]
    _validate_string_list(allowed_operations, "allowed_operations", min_items=1)
    for i, op in enumerate(allowed_operations):
        if op not in _VALID_OPERATIONS:
            raise ValueError(
                f"Invalid operation {op!r} in allowed_operations[{i}], "
                f"must be one of: {', '.join(sorted(_VALID_OPERATIONS))}"
            )

    blocked_operations = inputs["blocked_operations"]
    if not isinstance(blocked_operations, list):
        raise ValueError("blocked_operations must be a list")
    for i, op in enumerate(blocked_operations):
        if not isinstance(op, str) or len(op) < 1:
            raise ValueError(f"blocked_operations[{i}] must be a non-empty string")
        if op not in _VALID_OPERATIONS:
            raise ValueError(
                f"Invalid operation {op!r} in blocked_operations[{i}], "
                f"must be one of: {', '.join(sorted(_VALID_OPERATIONS))}"
            )

    allowed_set = frozenset(allowed_operations)
    blocked_set = frozenset(blocked_operations)
    overlap = allowed_set & blocked_set
    if overlap:
        raise ValueError(
            f"allowed_operations and blocked_operations overlap: "
            f"{', '.join(sorted(overlap))}"
        )

    required_checks = inputs["required_checks"]
    _validate_string_list(required_checks, "required_checks", min_items=1)
    for i, check in enumerate(required_checks):
        if check not in _VALID_CHECKS:
            raise ValueError(
                f"Invalid required check {check!r} in required_checks[{i}], "
                f"must be one of: {', '.join(sorted(_VALID_CHECKS))}"
            )

    requires_user_confirmation = inputs["requires_user_confirmation"]
    if not isinstance(requires_user_confirmation, bool):
        raise ValueError("requires_user_confirmation must be a boolean")

    # --- Validate optional inputs ---
    rationale = inputs.get("rationale")
    if rationale is not None and not isinstance(rationale, str):
        raise ValueError("rationale must be a string if provided")

    human_summary = inputs.get("human_summary")
    if human_summary is not None and not isinstance(human_summary, str):
        raise ValueError("human_summary must be a string if provided")

    # --- Build deterministic artifact fields ---
    constraints_id = _generate_deterministic_id(inputs)
    created_at = _generate_deterministic_created_at(inputs)

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "policy_constraints",
        "contract_version": "2.0",
        "constraints_id": constraints_id,
        "intent_id": intent_id,
        "created_at": created_at,
        "policy_refs": policy_refs,
        "allowed_operations": allowed_operations,
        "blocked_operations": blocked_operations,
        "required_checks": required_checks,
        "requires_user_confirmation": requires_user_confirmation,
    }

    if rationale is not None:
        artifact["rationale"] = rationale
    if human_summary is not None:
        artifact["human_summary"] = human_summary

    # --- Validate against policy_constraints schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Policy constraints artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return artifact
