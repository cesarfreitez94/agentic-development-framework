import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import jsonschema

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "schemas" / "meta" / "intent.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)
_VALID_SOURCES = frozenset({"user", "system", "decision"})
_VALID_URGENCIES = frozenset({"low", "medium", "high", "critical"})
_VALID_MILESTONE_STATUSES = frozenset({"planned", "in_progress", "completed", "paused"})


class SchemaValidationError(ValueError):
    """A produced artifact failed schema validation."""


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
    part1 = numeric % (10 ** 8)
    part2 = (numeric // (10 ** 8)) % (10 ** 3)
    return f"INTENT-{part1:08d}-{part2:03d}"


def _generate_deterministic_created_at(inputs: dict[str, object]) -> str:
    stable = json.dumps(inputs, sort_keys=True, default=str, ensure_ascii=True)
    digest = hashlib.sha256(stable.encode("utf-8")).digest()
    seconds_offset = int.from_bytes(digest[:4], "big") % (365 * 24 * 60 * 60)
    created = _BASE_EPOCH + timedelta(seconds=seconds_offset)
    return created.isoformat()


def build_intent(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build an intent artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            source (str, required): One of "user", "system", "decision".
            objective (str, required): Non-empty description of the intent.
            scope_include (list[str], required): Non-empty list of in-scope items.
            scope_exclude (list[str], optional): List of out-of-scope items.
            constraints (list[str], required): Non-empty list of constraints.
            requested_outputs (list[str], required): Non-empty list of desired outputs.
            non_goals (list[str], optional): List of non-goals.
            urgency (str, optional): One of "low", "medium", "high", "critical".
            requires_user_confirmation (bool, optional): Whether user confirmation is needed.
            related_milestone (dict, optional): Milestone info with required "id" key.
            human_summary (str, optional): Human-readable summary.
        output_path: Optional filesystem path. If provided, writes JSON artifact.

    Returns:
        Dict representing the complete, schema-valid intent artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.
    """
    # --- Validate required inputs ---
    required = {"source", "objective", "scope_include", "constraints", "requested_outputs"}
    for key in sorted(required):
        if key not in inputs:
            raise ValueError(f"Missing required input: {key!r}")

    source = inputs["source"]
    if source not in _VALID_SOURCES:
        raise ValueError(
            f"Invalid source {source!r}, must be one of: "
            + ", ".join(sorted(_VALID_SOURCES))
        )

    objective = inputs["objective"]
    _validate_non_empty_string(objective, "objective")

    scope_include = inputs["scope_include"]
    _validate_string_list(scope_include, "scope_include", min_items=1)

    scope_exclude = inputs.get("scope_exclude")
    if scope_exclude is not None:
        _validate_string_list(scope_exclude, "scope_exclude")

    constraints = inputs["constraints"]
    _validate_string_list(constraints, "constraints", min_items=1)

    requested_outputs = inputs["requested_outputs"]
    _validate_string_list(requested_outputs, "requested_outputs", min_items=1)

    # --- Validate optional inputs ---
    urgency = inputs.get("urgency")
    if urgency is not None and urgency not in _VALID_URGENCIES:
        raise ValueError(
            f"Invalid urgency {urgency!r}, must be one of: "
            + ", ".join(sorted(_VALID_URGENCIES))
        )

    non_goals = inputs.get("non_goals")
    if non_goals is not None:
        _validate_string_list(non_goals, "non_goals")

    related_milestone = inputs.get("related_milestone")
    if related_milestone is not None:
        if not isinstance(related_milestone, dict):
            raise ValueError("related_milestone must be a dict")
        if "id" not in related_milestone:
            raise ValueError("related_milestone must have an 'id' key")
        import re

        if not re.match(r"^M[0-9]+$", str(related_milestone["id"])):
            raise ValueError(
                "related_milestone.id must match pattern ^M[0-9]+$"
            )
        status = related_milestone.get("status")
        if status is not None and status not in _VALID_MILESTONE_STATUSES:
            raise ValueError(
                f"Invalid milestone status {status!r}, must be one of: "
                + ", ".join(sorted(_VALID_MILESTONE_STATUSES))
            )

    # --- Build deterministic artifact fields ---
    intent_id = _generate_deterministic_id(inputs)
    created_at = _generate_deterministic_created_at(inputs)

    # --- Assemble scope ---
    scope: dict[str, object] = {"include": scope_include}
    if scope_exclude is not None:
        scope["exclude"] = scope_exclude

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "intent",
        "contract_version": "2.0",
        "intent_id": intent_id,
        "created_at": created_at,
        "source": source,
        "objective": objective,
        "scope": scope,
        "constraints": constraints,
        "requested_outputs": requested_outputs,
    }

    if non_goals is not None:
        artifact["non_goals"] = non_goals
    if "urgency" in inputs and inputs["urgency"] is not None:
        artifact["urgency"] = inputs["urgency"]
    if (
        "requires_user_confirmation" in inputs
        and inputs["requires_user_confirmation"] is not None
    ):
        artifact["requires_user_confirmation"] = inputs["requires_user_confirmation"]
    if related_milestone is not None:
        artifact["related_milestone"] = related_milestone
    if "human_summary" in inputs and inputs.get("human_summary") is not None:
        artifact["human_summary"] = inputs["human_summary"]

    # --- Validate against intent schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Intent artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return artifact
