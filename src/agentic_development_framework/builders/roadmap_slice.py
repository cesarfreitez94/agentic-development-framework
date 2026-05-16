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
    / "roadmap_slice.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "RSLICE-"

_INTENT_ID_RE = r"^INTENT-[0-9]{8}-[0-9]{3}$"
_MILESTONE_ID_RE = r"^M[0-9]+$"

_VALID_MILESTONE_STATUSES = frozenset(
    {"planned", "in_progress", "completed", "paused"}
)

_ACTIVE_MILESTONE_KEYS = frozenset({"id", "name", "status", "branch"})
_RELEVANT_MILESTONE_KEYS = frozenset(
    {"id", "name", "status", "branch", "capabilities"}
)

_SOURCE_REF_KEYS = frozenset({"path", "section", "line_ranges"})

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


def _validate_active_milestone(milestone: object, label: str) -> None:
    if not isinstance(milestone, dict):
        raise ValueError(f"{label} must be a dict")

    for key in ("id", "status", "branch"):
        if key not in milestone:
            raise ValueError(f"{label} must have a {key!r} key")

    extra = set(milestone.keys()) - _ACTIVE_MILESTONE_KEYS
    if extra:
        raise ValueError(
            f"{label} has extra keys: {', '.join(sorted(extra))}"
        )

    mid = milestone["id"]
    if not isinstance(mid, str) or not re.match(_MILESTONE_ID_RE, mid):
        raise ValueError(
            f"{label}.id {mid!r} must match pattern {_MILESTONE_ID_RE}"
        )

    name = milestone.get("name")
    if name is not None and not isinstance(name, str):
        raise ValueError(f"{label}.name must be a string if provided")

    status = milestone["status"]
    if status not in _VALID_MILESTONE_STATUSES:
        raise ValueError(
            f"{label}.status {status!r} must be one of: "
            + ", ".join(sorted(_VALID_MILESTONE_STATUSES))
        )

    branch = milestone["branch"]
    if not isinstance(branch, str):
        raise ValueError(f"{label}.branch must be a string")


def _validate_relevant_milestone(milestone: object, label: str) -> None:
    if not isinstance(milestone, dict):
        raise ValueError(f"{label} must be a dict")

    for key in ("id", "status"):
        if key not in milestone:
            raise ValueError(f"{label} must have a {key!r} key")

    extra = set(milestone.keys()) - _RELEVANT_MILESTONE_KEYS
    if extra:
        raise ValueError(
            f"{label} has extra keys: {', '.join(sorted(extra))}"
        )

    mid = milestone["id"]
    if not isinstance(mid, str) or not re.match(_MILESTONE_ID_RE, mid):
        raise ValueError(
            f"{label}.id {mid!r} must match pattern {_MILESTONE_ID_RE}"
        )

    name = milestone.get("name")
    if name is not None and not isinstance(name, str):
        raise ValueError(f"{label}.name must be a string if provided")

    status = milestone["status"]
    if status not in _VALID_MILESTONE_STATUSES:
        raise ValueError(
            f"{label}.status {status!r} must be one of: "
            + ", ".join(sorted(_VALID_MILESTONE_STATUSES))
        )

    branch = milestone.get("branch")
    if branch is not None and not isinstance(branch, str):
        raise ValueError(f"{label}.branch must be a string if provided")

    capabilities = milestone.get("capabilities")
    if capabilities is not None:
        if not isinstance(capabilities, list):
            raise ValueError(f"{label}.capabilities must be a list if provided")
        for i, cap in enumerate(capabilities):
            if not isinstance(cap, str):
                raise ValueError(
                    f"{label}.capabilities[{i}] must be a string"
                )


def _validate_source_ref(source_ref: object, label: str) -> None:
    if not isinstance(source_ref, dict):
        raise ValueError(f"{label} must be a dict")

    if "path" not in source_ref:
        raise ValueError(f"{label} must have a 'path' key")

    extra = set(source_ref.keys()) - _SOURCE_REF_KEYS
    if extra:
        raise ValueError(
            f"{label} has extra keys: {', '.join(sorted(extra))}"
        )

    _validate_non_empty_string(source_ref["path"], f"{label}.path")

    section = source_ref.get("section")
    if section is not None and not isinstance(section, str):
        raise ValueError(f"{label}.section must be a string if provided")

    line_ranges = source_ref.get("line_ranges")
    if line_ranges is not None:
        if not isinstance(line_ranges, list):
            raise ValueError(
                f"{label}.line_ranges must be a list if provided"
            )
        for i, lr in enumerate(line_ranges):
            if not isinstance(lr, dict):
                raise ValueError(
                    f"{label}.line_ranges[{i}] must be a dict"
                )
            for key in ("start", "end"):
                if key not in lr:
                    raise ValueError(
                        f"{label}.line_ranges[{i}] must have a {key!r} key"
                    )
            start = lr["start"]
            end = lr["end"]
            if not isinstance(start, int):
                raise ValueError(
                    f"{label}.line_ranges[{i}].start must be an integer"
                )
            if not isinstance(end, int):
                raise ValueError(
                    f"{label}.line_ranges[{i}].end must be an integer"
                )
            if start < 1:
                raise ValueError(
                    f"{label}.line_ranges[{i}].start must be >= 1"
                )
            if end < 1:
                raise ValueError(
                    f"{label}.line_ranges[{i}].end must be >= 1"
                )
            if start > end:
                raise ValueError(
                    f"{label}.line_ranges[{i}].start must be <= end"
                )


def build_roadmap_slice(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build a roadmap_slice artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            intent_id (str, required): Intent ID matching ^INTENT-[0-9]{8}-[0-9]{3}$.
            active_milestone (dict, required): Active milestone with id, status, branch.
            relevant_milestones (list[dict], required): Non-empty list of milestones.
            policy_refs (list[str], required): Non-empty list of policy references.
            allowed_operations (list[str], required): Non-empty list of allowed operations.
            blocked_operations (list[str], required): List of blocked operations.
            source_refs (list[dict], required): Non-empty list of source references.
            open_issues (list[dict], optional): List of open issues.
            branch_context (dict, optional): Branch context with current and base.
            recent_changes (list[str], optional): List of recent changes.
            risk_notes (list[str], optional): List of risk notes.
            human_summary (str, optional): Human-readable summary.
        output_path: Optional filesystem path. If provided, writes JSON artifact.

    Returns:
        Dict representing the complete, schema-valid roadmap_slice artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.
    """
    # --- Validate required inputs ---
    required = {
        "intent_id",
        "active_milestone",
        "relevant_milestones",
        "policy_refs",
        "allowed_operations",
        "blocked_operations",
        "source_refs",
    }
    for key in sorted(required):
        if key not in inputs:
            raise ValueError(f"Missing required input: {key!r}")

    intent_id = inputs["intent_id"]
    _validate_non_empty_string(intent_id, "intent_id")
    if not re.match(_INTENT_ID_RE, intent_id):
        raise ValueError(
            f"intent_id {intent_id!r} must match pattern {_INTENT_ID_RE}"
        )

    _validate_active_milestone(inputs["active_milestone"], "active_milestone")

    relevant_milestones = inputs["relevant_milestones"]
    if not isinstance(relevant_milestones, list):
        raise ValueError("relevant_milestones must be a list")
    if len(relevant_milestones) < 1:
        raise ValueError("relevant_milestones must have at least 1 item(s)")
    for i, rm in enumerate(relevant_milestones):
        _validate_relevant_milestone(rm, f"relevant_milestones[{i}]")

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

    source_refs = inputs["source_refs"]
    if not isinstance(source_refs, list):
        raise ValueError("source_refs must be a list")
    if len(source_refs) < 1:
        raise ValueError("source_refs must have at least 1 item(s)")
    for i, sr in enumerate(source_refs):
        _validate_source_ref(sr, f"source_refs[{i}]")

    # --- Validate optional inputs ---
    open_issues = inputs.get("open_issues")
    if open_issues is not None:
        if not isinstance(open_issues, list):
            raise ValueError("open_issues must be a list if provided")
        for i, oi in enumerate(open_issues):
            if not isinstance(oi, dict):
                raise ValueError(f"open_issues[{i}] must be a dict")
            for key in ("issue_id", "title", "status"):
                if key not in oi:
                    raise ValueError(
                        f"open_issues[{i}] must have a {key!r} key"
                    )
            extra = set(oi.keys()) - {"issue_id", "title", "status", "url"}
            if extra:
                raise ValueError(
                    f"open_issues[{i}] has extra keys: {', '.join(sorted(extra))}"
                )
            if not isinstance(oi["issue_id"], str):
                raise ValueError(
                    f"open_issues[{i}].issue_id must be a string"
                )
            if not isinstance(oi["title"], str):
                raise ValueError(
                    f"open_issues[{i}].title must be a string"
                )
            if not isinstance(oi["status"], str):
                raise ValueError(
                    f"open_issues[{i}].status must be a string"
                )
            url = oi.get("url")
            if url is not None and not isinstance(url, str):
                raise ValueError(
                    f"open_issues[{i}].url must be a string if provided"
                )

    branch_context = inputs.get("branch_context")
    if branch_context is not None:
        if not isinstance(branch_context, dict):
            raise ValueError(
                "branch_context must be a dict if provided"
            )
        for key in ("current", "base"):
            if key not in branch_context:
                raise ValueError(
                    f"branch_context must have a {key!r} key"
                )
        extra = set(branch_context.keys()) - {"current", "base"}
        if extra:
            raise ValueError(
                f"branch_context has extra keys: {', '.join(sorted(extra))}"
            )
        if not isinstance(branch_context["current"], str):
            raise ValueError("branch_context.current must be a string")
        if not isinstance(branch_context["base"], str):
            raise ValueError("branch_context.base must be a string")

    recent_changes = inputs.get("recent_changes")
    if recent_changes is not None:
        _validate_string_list(recent_changes, "recent_changes")

    risk_notes = inputs.get("risk_notes")
    if risk_notes is not None:
        _validate_string_list(risk_notes, "risk_notes")

    human_summary = inputs.get("human_summary")
    if human_summary is not None and not isinstance(human_summary, str):
        raise ValueError("human_summary must be a string if provided")

    # --- Build deterministic artifact fields ---
    slice_id = _generate_deterministic_id(inputs)
    created_at = _generate_deterministic_created_at(inputs)

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "roadmap_slice",
        "contract_version": "2.0",
        "slice_id": slice_id,
        "intent_id": intent_id,
        "created_at": created_at,
        "active_milestone": inputs["active_milestone"],
        "relevant_milestones": relevant_milestones,
        "policy_refs": policy_refs,
        "allowed_operations": allowed_operations,
        "blocked_operations": blocked_operations,
        "source_refs": source_refs,
    }

    if open_issues is not None:
        artifact["open_issues"] = open_issues
    if branch_context is not None:
        artifact["branch_context"] = branch_context
    if recent_changes is not None:
        artifact["recent_changes"] = recent_changes
    if risk_notes is not None:
        artifact["risk_notes"] = risk_notes
    if human_summary is not None:
        artifact["human_summary"] = human_summary

    # --- Validate against roadmap_slice schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Roadmap slice artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return artifact
