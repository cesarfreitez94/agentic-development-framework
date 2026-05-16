import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import jsonschema

from .intent import SchemaValidationError

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "schemas" / "meta" / "plan.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "PLAN-"

_INTENT_ID_RE = r"^INTENT-[0-9]{8}-[0-9]{3}$"
_RSLICE_ID_RE = r"^RSLICE-[0-9]{8}-[0-9]{3}$"
_TASK_ID_RE = r"^TASK-[0-9]{8}-[0-9]{3}$"

_VALID_TASK_TYPES = frozenset(
    {
        "schema_design",
        "policy_constraints",
        "roadmap_slice",
        "plan",
        "task_packet",
        "context_bundle",
        "implementation",
        "test",
        "review",
        "git_operation",
    }
)

_ALLOWED_TASK_KEYS = frozenset(
    {"task_id", "title", "type", "depends_on", "inputs", "outputs", "owner_hint"}
)

_ALLOWED_RISK_KEYS = frozenset({"risk", "impact", "mitigation"})


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


def _validate_task(
    task: object, index: int, task_id_set: set[str]
) -> str:
    """Validate a single task dict. Returns the task_id."""
    if not isinstance(task, dict):
        raise ValueError(f"tasks[{index}] must be a dict")

    for key in ("task_id", "title", "type", "depends_on"):
        if key not in task:
            raise ValueError(f"tasks[{index}] must have a {key!r} key")

    extra = set(task.keys()) - _ALLOWED_TASK_KEYS
    if extra:
        raise ValueError(
            f"tasks[{index}] has extra keys: {', '.join(sorted(extra))}"
        )

    task_id = task["task_id"]
    _validate_non_empty_string(task_id, f"tasks[{index}].task_id")
    if not re.match(_TASK_ID_RE, task_id):
        raise ValueError(
            f"tasks[{index}].task_id {task_id!r} must match pattern {_TASK_ID_RE}"
        )

    if task_id in task_id_set:
        raise ValueError(f"Duplicate task_id {task_id!r} in tasks")
    task_id_set.add(task_id)

    title = task["title"]
    _validate_non_empty_string(title, f"tasks[{index}].title")

    task_type = task["type"]
    if task_type not in _VALID_TASK_TYPES:
        raise ValueError(
            f"tasks[{index}].type {task_type!r} must be one of: "
            + ", ".join(sorted(_VALID_TASK_TYPES))
        )

    depends_on = task["depends_on"]
    if not isinstance(depends_on, list):
        raise ValueError(f"tasks[{index}].depends_on must be a list")
    for j, dep in enumerate(depends_on):
        if not isinstance(dep, str) or not re.match(_TASK_ID_RE, dep):
            raise ValueError(
                f"tasks[{index}].depends_on[{j}] {dep!r} must match pattern {_TASK_ID_RE}"
            )
        if dep == task_id:
            raise ValueError(
                f"tasks[{index}] depends on itself: {dep!r}"
            )

    inputs = task.get("inputs")
    if inputs is not None:
        if not isinstance(inputs, list):
            raise ValueError(f"tasks[{index}].inputs must be a list if provided")
        for j, inp in enumerate(inputs):
            if not isinstance(inp, str):
                raise ValueError(f"tasks[{index}].inputs[{j}] must be a string")

    outputs = task.get("outputs")
    if outputs is not None:
        if not isinstance(outputs, list):
            raise ValueError(f"tasks[{index}].outputs must be a list if provided")
        for j, out in enumerate(outputs):
            if not isinstance(out, str):
                raise ValueError(f"tasks[{index}].outputs[{j}] must be a string")

    owner_hint = task.get("owner_hint")
    if owner_hint is not None and not isinstance(owner_hint, str):
        raise ValueError(f"tasks[{index}].owner_hint must be a string if provided")

    return task_id


def _validate_tasks(tasks: object) -> set[str]:
    """Validate the tasks list. Returns the set of valid task IDs."""
    if not isinstance(tasks, list):
        raise ValueError("tasks must be a list")
    if len(tasks) < 1:
        raise ValueError("tasks must be a non-empty list")

    task_id_set: set[str] = set()
    for i, task in enumerate(tasks):
        _validate_task(task, i, task_id_set)

    # Cross-reference: every depends_on entry must reference a known task_id
    for i, task in enumerate(tasks):
        for dep in task["depends_on"]:
            if dep not in task_id_set:
                raise ValueError(
                    f"tasks[{i}].depends_on references unknown task_id {dep!r}"
                )

    return task_id_set


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


def build_plan(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build a plan artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            intent_id (str, required): Intent ID matching ^INTENT-[0-9]{8}-[0-9]{3}$.
            roadmap_slice_id (str, required): Roadmap slice ID matching ^RSLICE-[0-9]{8}-[0-9]{3}$.
            goal (str, required): Non-empty description of the plan goal.
            tasks (list[dict], required): Non-empty list of task dicts.
            acceptance_criteria (list[str], required): Non-empty list of acceptance criteria.
            constraints (list[str], required): Non-empty list of constraints.
            requires_user_confirmation (bool, required): Whether user confirmation is needed.
            estimated_order (list[str], optional): Ordered list of TASK IDs.
            assumptions (list[str], optional): List of assumptions.
            out_of_scope (list[str], optional): List of out-of-scope items.
            risk_register (list[dict], optional): List of risk entries.
            human_summary (str, optional): Human-readable summary.
        output_path: Optional filesystem path. If provided, writes JSON artifact.

    Returns:
        Dict representing the complete, schema-valid plan artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.
    """
    # --- Validate required inputs ---
    required = {
        "intent_id",
        "roadmap_slice_id",
        "goal",
        "tasks",
        "acceptance_criteria",
        "constraints",
        "requires_user_confirmation",
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

    roadmap_slice_id = inputs["roadmap_slice_id"]
    _validate_non_empty_string(roadmap_slice_id, "roadmap_slice_id")
    if not re.match(_RSLICE_ID_RE, roadmap_slice_id):
        raise ValueError(
            f"roadmap_slice_id {roadmap_slice_id!r} must match pattern {_RSLICE_ID_RE}"
        )

    goal = inputs["goal"]
    _validate_non_empty_string(goal, "goal")

    tasks = inputs["tasks"]
    task_id_set = _validate_tasks(tasks)

    acceptance_criteria = inputs["acceptance_criteria"]
    _validate_string_list(acceptance_criteria, "acceptance_criteria", min_items=1)

    constraints = inputs["constraints"]
    _validate_string_list(constraints, "constraints", min_items=1)

    requires_user_confirmation = inputs["requires_user_confirmation"]
    if not isinstance(requires_user_confirmation, bool):
        raise ValueError("requires_user_confirmation must be a boolean")

    # --- Validate optional inputs ---
    estimated_order = inputs.get("estimated_order")
    if estimated_order is not None:
        if not isinstance(estimated_order, list):
            raise ValueError("estimated_order must be a list if provided")
        seen: set[str] = set()
        for i, eid in enumerate(estimated_order):
            if not isinstance(eid, str) or not re.match(_TASK_ID_RE, eid):
                raise ValueError(
                    f"estimated_order[{i}] {eid!r} must match pattern {_TASK_ID_RE}"
                )
            if eid in seen:
                raise ValueError(
                    f"Duplicate task_id {eid!r} in estimated_order"
                )
            seen.add(eid)
            if eid not in task_id_set:
                raise ValueError(
                    f"estimated_order[{i}] {eid!r} is not a known task_id"
                )

    assumptions = inputs.get("assumptions")
    if assumptions is not None:
        if not isinstance(assumptions, list):
            raise ValueError("assumptions must be a list if provided")
        for i, item in enumerate(assumptions):
            if not isinstance(item, str):
                raise ValueError(f"assumptions[{i}] must be a string")

    out_of_scope = inputs.get("out_of_scope")
    if out_of_scope is not None:
        if not isinstance(out_of_scope, list):
            raise ValueError("out_of_scope must be a list if provided")
        for i, item in enumerate(out_of_scope):
            if not isinstance(item, str):
                raise ValueError(f"out_of_scope[{i}] must be a string")

    risk_register = inputs.get("risk_register")
    if risk_register is not None:
        if not isinstance(risk_register, list):
            raise ValueError("risk_register must be a list if provided")
        for i, entry in enumerate(risk_register):
            if not isinstance(entry, dict):
                raise ValueError(f"risk_register[{i}] must be a dict")
            for key in ("risk", "impact"):
                if key not in entry:
                    raise ValueError(
                        f"risk_register[{i}] must have a {key!r} key"
                    )
            extra = set(entry.keys()) - _ALLOWED_RISK_KEYS
            if extra:
                raise ValueError(
                    f"risk_register[{i}] has extra keys: {', '.join(sorted(extra))}"
                )
            if not isinstance(entry["risk"], str):
                raise ValueError(f"risk_register[{i}].risk must be a string")
            if not isinstance(entry["impact"], str):
                raise ValueError(f"risk_register[{i}].impact must be a string")
            mitigation = entry.get("mitigation")
            if mitigation is not None and not isinstance(mitigation, str):
                raise ValueError(f"risk_register[{i}].mitigation must be a string if provided")

    human_summary = inputs.get("human_summary")
    if human_summary is not None and not isinstance(human_summary, str):
        raise ValueError("human_summary must be a string if provided")

    # --- Build deterministic artifact fields ---
    plan_id = _generate_deterministic_id(inputs)
    created_at = _generate_deterministic_created_at(inputs)

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "plan",
        "contract_version": "2.0",
        "plan_id": plan_id,
        "intent_id": intent_id,
        "roadmap_slice_id": roadmap_slice_id,
        "created_at": created_at,
        "goal": goal,
        "tasks": tasks,
        "acceptance_criteria": acceptance_criteria,
        "constraints": constraints,
        "requires_user_confirmation": requires_user_confirmation,
    }

    if estimated_order is not None:
        artifact["estimated_order"] = estimated_order
    if assumptions is not None:
        artifact["assumptions"] = assumptions
    if out_of_scope is not None:
        artifact["out_of_scope"] = out_of_scope
    if risk_register is not None:
        artifact["risk_register"] = risk_register
    if human_summary is not None:
        artifact["human_summary"] = human_summary

    # --- Validate against plan schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Plan artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return artifact
