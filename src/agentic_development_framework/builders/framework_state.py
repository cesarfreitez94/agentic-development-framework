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
    / "framework_state.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "FWSTATE-"
_ID_PATTERN = re.compile(r"^FWSTATE-[0-9]{8}-[0-9]{3}$")

_INTENT_ID_RE = re.compile(r"^INTENT-[0-9]{8}-[0-9]{3}$")
_PLAN_ID_RE = re.compile(r"^PLAN-[0-9]{8}-[0-9]{3}$")
_TASK_ID_RE = re.compile(r"^TASK-[0-9]{8}-[0-9]{3}$")
_DECISION_ID_RE = re.compile(r"^DEC-[0-9]{8}-[0-9]{3}$")

_VALID_PHASES = frozenset(
    {
        "idle",
        "intent",
        "policy_constraints",
        "roadmap_slice",
        "planning",
        "tasking",
        "context",
        "implementation",
        "testing",
        "review",
        "git_operation",
        "completed",
        "blocked",
    }
)

_VALID_ARTIFACT_STATUSES = frozenset({"draft", "valid", "published"})
_VALID_DECISION_STATUSES = frozenset({"pending", "resolved", "cancelled"})
_VALID_MILESTONE_STATUSES = frozenset({"planned", "in_progress", "completed", "paused"})
_VALID_COMPLETED_STEPS = frozenset(
    {
        "intent",
        "policy_constraints",
        "roadmap_slice",
        "plan",
        "task_packet",
        "context_bundle",
        "implementation_report",
        "test_report",
        "review_report",
        "git_operation",
    }
)

_MILESTONE_ID_RE = re.compile(r"^M[0-9]+$")

_ARTIFACT_REQUIRED_KEYS = frozenset({"contract_name", "artifact_id", "path", "status"})
_ARTIFACT_ALLOWED_KEYS = frozenset(
    {"contract_name", "contract_version", "artifact_id", "path", "status", "version"}
)

_DECISION_REQUIRED_KEYS = frozenset({"decision_id", "status"})
_DECISION_ALLOWED_KEYS = frozenset({"decision_id", "status", "question"})

_MILESTONE_REQUIRED_KEYS = frozenset({"id", "status", "branch"})
_MILESTONE_ALLOWED_KEYS = frozenset({"id", "name", "status", "branch"})


def _validate_non_empty_string(value: object, label: str) -> None:
    if not isinstance(value, str) or len(value) < 1:
        raise ValueError(f"{label} must be a non-empty string")


def _generate_deterministic_id(inputs: dict[str, object]) -> str:
    stable = json.dumps(inputs, sort_keys=True, default=str, ensure_ascii=True)
    digest = hashlib.sha256(stable.encode("utf-8")).digest()
    numeric = int.from_bytes(digest[:11], "big")
    part1 = numeric % (10**8)
    part2 = (numeric // (10**8)) % (10**3)
    return f"{_ID_PREFIX}{part1:08d}-{part2:03d}"


def _generate_deterministic_updated_at(inputs: dict[str, object]) -> str:
    stable = json.dumps(inputs, sort_keys=True, default=str, ensure_ascii=True)
    digest = hashlib.sha256(stable.encode("utf-8")).digest()
    seconds_offset = int.from_bytes(digest[:4], "big") % (365 * 24 * 60 * 60)
    created = _BASE_EPOCH + timedelta(seconds=seconds_offset)
    return created.isoformat()


def _validate_artifacts(value: object) -> None:
    if not isinstance(value, list):
        raise ValueError("artifacts must be a list")

    seen_triples: set[tuple[str, str, str]] = set()
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"artifacts[{i}] must be a dict")

        missing = _ARTIFACT_REQUIRED_KEYS - set(item.keys())
        if missing:
            raise ValueError(
                f"artifacts[{i}] missing required key(s): {', '.join(sorted(missing))}"
            )

        extra = set(item.keys()) - _ARTIFACT_ALLOWED_KEYS
        if extra:
            raise ValueError(
                f"artifacts[{i}] has extra key(s): {', '.join(sorted(extra))}"
            )

        contract_name = item["contract_name"]
        _validate_non_empty_string(contract_name, f"artifacts[{i}].contract_name")

        contract_version = item.get("contract_version")
        if contract_version is not None and not isinstance(contract_version, str):
            raise ValueError(
                f"artifacts[{i}].contract_version must be a string if provided"
            )

        artifact_id = item["artifact_id"]
        if not isinstance(artifact_id, str):
            raise ValueError(f"artifacts[{i}].artifact_id must be a string")

        path = item["path"]
        if not isinstance(path, str):
            raise ValueError(f"artifacts[{i}].path must be a string")

        status = item["status"]
        if status not in _VALID_ARTIFACT_STATUSES:
            raise ValueError(
                f"artifacts[{i}].status {status!r} must be one of: "
                f"{', '.join(sorted(_VALID_ARTIFACT_STATUSES))}"
            )

        version = item.get("version")
        if version is not None:
            if not isinstance(version, int) or version < 0:
                raise ValueError(
                    f"artifacts[{i}].version must be an integer >= 0 if provided"
                )

        dup_key = (contract_name, artifact_id, path)
        if dup_key in seen_triples:
            raise ValueError(
                f"Duplicate artifact (contract_name={contract_name!r}, "
                f"artifact_id={artifact_id!r}, path={path!r})"
            )
        seen_triples.add(dup_key)


def _validate_pending_decisions(value: object) -> None:
    if not isinstance(value, list):
        raise ValueError("pending_decisions must be a list")

    seen_ids: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"pending_decisions[{i}] must be a dict")

        missing = _DECISION_REQUIRED_KEYS - set(item.keys())
        if missing:
            raise ValueError(
                f"pending_decisions[{i}] missing required key(s): "
                f"{', '.join(sorted(missing))}"
            )

        extra = set(item.keys()) - _DECISION_ALLOWED_KEYS
        if extra:
            raise ValueError(
                f"pending_decisions[{i}] has extra key(s): {', '.join(sorted(extra))}"
            )

        decision_id = item["decision_id"]
        if not isinstance(decision_id, str):
            raise ValueError(f"pending_decisions[{i}].decision_id must be a string")
        if not _DECISION_ID_RE.match(decision_id):
            raise ValueError(
                f"pending_decisions[{i}].decision_id {decision_id!r} must match "
                f"pattern '^DEC-[0-9]{{8}}-[0-9]{{3}}$'"
            )

        if decision_id in seen_ids:
            raise ValueError(
                f"Duplicate decision_id {decision_id!r} in pending_decisions"
            )
        seen_ids.add(decision_id)

        status = item["status"]
        if status not in _VALID_DECISION_STATUSES:
            raise ValueError(
                f"pending_decisions[{i}].status {status!r} must be one of: "
                f"{', '.join(sorted(_VALID_DECISION_STATUSES))}"
            )

        question = item.get("question")
        if question is not None and not isinstance(question, str):
            raise ValueError(
                f"pending_decisions[{i}].question must be a string if provided"
            )


def _validate_active_milestone(value: object) -> None:
    if value is None:
        return

    if not isinstance(value, dict):
        raise ValueError("active_milestone must be a dict or None")

    missing = _MILESTONE_REQUIRED_KEYS - set(value.keys())
    if missing:
        raise ValueError(
            f"active_milestone missing required key(s): "
            f"{', '.join(sorted(missing))}"
        )

    extra = set(value.keys()) - _MILESTONE_ALLOWED_KEYS
    if extra:
        raise ValueError(
            f"active_milestone has extra key(s): {', '.join(sorted(extra))}"
        )

    milestone_id = value["id"]
    if not isinstance(milestone_id, str) or not _MILESTONE_ID_RE.match(milestone_id):
        raise ValueError(
            f"active_milestone.id {milestone_id!r} must match pattern '^M[0-9]+$'"
        )

    milestone_name = value.get("name")
    if milestone_name is not None and not isinstance(milestone_name, str):
        raise ValueError("active_milestone.name must be a string if provided")

    milestone_status = value["status"]
    if milestone_status not in _VALID_MILESTONE_STATUSES:
        raise ValueError(
            f"active_milestone.status {milestone_status!r} must be one of: "
            f"{', '.join(sorted(_VALID_MILESTONE_STATUSES))}"
        )

    milestone_branch = value["branch"]
    if not isinstance(milestone_branch, str):
        raise ValueError("active_milestone.branch must be a string")


def build_framework_state(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build a framework_state_v2 artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            current_phase (str, required): One of "idle", "intent",
                "policy_constraints", "roadmap_slice", "planning", "tasking",
                "context", "implementation", "testing", "review", "git_operation",
                "completed", "blocked".
            artifacts (list[dict], required): List of artifact entries with
                keys contract_name, artifact_id, path, status (and optional
                contract_version, version).
            pending_decisions (list[dict], required): List of pending decision
                entries with keys decision_id, status (and optional question).
            active_intent_id (str | None, optional).
            active_plan_id (str | None, optional).
            active_task_id (str | None, optional).
            active_milestone (dict | None, optional).
            last_completed_step (str | None, optional).
            human_summary (str, optional).
        output_path: Optional filesystem path. If provided, writes JSON artifact.

    Returns:
        Dict representing the complete, schema-valid framework_state_v2 artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.
    """
    required = {"current_phase", "artifacts", "pending_decisions"}
    for key in sorted(required):
        if key not in inputs:
            raise ValueError(f"Missing required input: {key!r}")

    current_phase = inputs["current_phase"]
    _validate_non_empty_string(current_phase, "current_phase")
    if current_phase not in _VALID_PHASES:
        raise ValueError(
            f"Invalid current_phase {current_phase!r}, must be one of: "
            f"{', '.join(sorted(_VALID_PHASES))}"
        )

    artifacts = inputs["artifacts"]
    _validate_artifacts(artifacts)

    pending_decisions = inputs["pending_decisions"]
    _validate_pending_decisions(pending_decisions)

    active_intent_id = inputs.get("active_intent_id")
    if active_intent_id is not None:
        if not isinstance(active_intent_id, str):
            raise ValueError("active_intent_id must be a string or None")
        if not _INTENT_ID_RE.match(active_intent_id):
            raise ValueError(
                f"active_intent_id {active_intent_id!r} must match pattern "
                f"'^INTENT-[0-9]{{8}}-[0-9]{{3}}$'"
            )

    active_plan_id = inputs.get("active_plan_id")
    if active_plan_id is not None:
        if not isinstance(active_plan_id, str):
            raise ValueError("active_plan_id must be a string or None")
        if not _PLAN_ID_RE.match(active_plan_id):
            raise ValueError(
                f"active_plan_id {active_plan_id!r} must match pattern "
                f"'^PLAN-[0-9]{{8}}-[0-9]{{3}}$'"
            )

    active_task_id = inputs.get("active_task_id")
    if active_task_id is not None:
        if not isinstance(active_task_id, str):
            raise ValueError("active_task_id must be a string or None")
        if not _TASK_ID_RE.match(active_task_id):
            raise ValueError(
                f"active_task_id {active_task_id!r} must match pattern "
                f"'^TASK-[0-9]{{8}}-[0-9]{{3}}$'"
            )

    active_milestone = inputs.get("active_milestone")
    if active_milestone is not None:
        _validate_active_milestone(active_milestone)

    last_completed_step = inputs.get("last_completed_step")
    if last_completed_step is not None:
        if not isinstance(last_completed_step, str):
            raise ValueError("last_completed_step must be a string or None")
        if last_completed_step not in _VALID_COMPLETED_STEPS:
            raise ValueError(
                f"last_completed_step {last_completed_step!r} must be one of: "
                f"{', '.join(sorted(_VALID_COMPLETED_STEPS))}"
            )

    human_summary = inputs.get("human_summary")
    if human_summary is not None:
        if not isinstance(human_summary, str):
            raise ValueError("human_summary must be a string if provided")

    # --- Consistency checks ---
    if current_phase == "completed":
        if len(pending_decisions) > 0:
            raise ValueError(
                "current_phase is 'completed' but pending_decisions is not empty"
            )

    if current_phase == "blocked":
        has_pending = any(
            isinstance(pd, dict) and pd.get("status") == "pending"
            for pd in pending_decisions
        )
        has_summary = human_summary is not None
        if not has_pending and not has_summary:
            raise ValueError(
                "current_phase is 'blocked' but no pending decision with status "
                "'pending' and no human_summary provided"
            )

    # --- Build deterministic artifact fields ---
    state_id = _generate_deterministic_id(inputs)
    updated_at = _generate_deterministic_updated_at(inputs)

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "framework_state_v2",
        "contract_version": "2.0",
        "state_id": state_id,
        "updated_at": updated_at,
        "workflow_version": "meta_v2",
        "current_phase": current_phase,
        "artifacts": artifacts,
        "pending_decisions": pending_decisions,
    }

    if active_intent_id is not None:
        artifact["active_intent_id"] = active_intent_id
    if active_plan_id is not None:
        artifact["active_plan_id"] = active_plan_id
    if active_task_id is not None:
        artifact["active_task_id"] = active_task_id
    if active_milestone is not None:
        artifact["active_milestone"] = active_milestone
    if last_completed_step is not None:
        artifact["last_completed_step"] = last_completed_step
    if human_summary is not None:
        artifact["human_summary"] = human_summary

    # --- Validate against framework_state schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Framework state artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return artifact
