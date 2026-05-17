import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.framework_state import (
    SchemaValidationError,
    build_framework_state,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "framework_state.schema.json"

VALID_INPUTS: dict[str, object] = {
    "current_phase": "planning",
    "artifacts": [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "artifact_id": "INTENT-12345678-001",
            "path": "artifacts/intent.json",
            "status": "valid",
            "version": 1,
        },
        {
            "contract_name": "plan",
            "artifact_id": "PLAN-12345678-001",
            "path": "artifacts/plan.json",
            "status": "draft",
        },
    ],
    "pending_decisions": [
        {
            "decision_id": "DEC-12345678-001",
            "status": "pending",
            "question": "Should we proceed with the implementation?",
        }
    ],
    "active_intent_id": "INTENT-12345678-001",
    "active_plan_id": "PLAN-12345678-001",
    "active_task_id": "TASK-12345678-001",
    "active_milestone": {
        "id": "M5",
        "name": "Builder Extraction",
        "status": "in_progress",
        "branch": "m5/builders",
    },
    "last_completed_step": "intent",
    "human_summary": "Building the framework_state builder",
}

VALID_INPUTS_COMPLETED: dict[str, object] = {
    "current_phase": "completed",
    "artifacts": [
        {
            "contract_name": "intent",
            "artifact_id": "INTENT-12345678-001",
            "path": "artifacts/intent.json",
            "status": "published",
        }
    ],
    "pending_decisions": [],
    "human_summary": "All phases completed successfully.",
}

VALID_INPUTS_BLOCKED: dict[str, object] = {
    "current_phase": "blocked",
    "artifacts": [
        {
            "contract_name": "intent",
            "artifact_id": "INTENT-12345678-001",
            "path": "artifacts/intent.json",
            "status": "draft",
        }
    ],
    "pending_decisions": [
        {
            "decision_id": "DEC-12345678-001",
            "status": "pending",
            "question": "Should we change the architecture?",
        }
    ],
}

VALID_INPUTS_BLOCKED_WITH_SUMMARY: dict[str, object] = {
    "current_phase": "blocked",
    "artifacts": [],
    "pending_decisions": [],
    "human_summary": "Blocked waiting for schema-governance approval.",
}


def test_build_framework_state_schema_valid():
    artifact = build_framework_state(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_framework_state_is_deterministic():
    a = build_framework_state(VALID_INPUTS)
    b = build_framework_state(VALID_INPUTS)
    c = build_framework_state(VALID_INPUTS)

    assert a == b == c


def test_build_framework_state_rejects_missing_required_input():
    for missing_key in ("current_phase", "artifacts", "pending_decisions"):
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_framework_state(inputs)


def test_build_framework_state_writes_output_path(tmp_path):
    output_path = tmp_path / "framework_state.json"

    artifact = build_framework_state(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_framework_state_rejects_invalid_current_phase():
    inputs = dict(VALID_INPUTS)
    inputs["current_phase"] = "invalid_phase"
    with pytest.raises(ValueError, match="current_phase"):
        build_framework_state(inputs)

    inputs["current_phase"] = ""
    with pytest.raises(ValueError, match="current_phase"):
        build_framework_state(inputs)

    inputs["current_phase"] = 42
    with pytest.raises(ValueError, match="current_phase"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_invalid_active_intent_id():
    inputs = dict(VALID_INPUTS)
    inputs["active_intent_id"] = "bad-format"
    with pytest.raises(ValueError, match="active_intent_id"):
        build_framework_state(inputs)

    inputs["active_intent_id"] = ""
    with pytest.raises(ValueError, match="active_intent_id"):
        build_framework_state(inputs)

    inputs["active_intent_id"] = 42
    with pytest.raises(ValueError, match="active_intent_id"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_invalid_active_plan_id():
    inputs = dict(VALID_INPUTS)
    inputs["active_plan_id"] = "bad-format"
    with pytest.raises(ValueError, match="active_plan_id"):
        build_framework_state(inputs)

    inputs["active_plan_id"] = ""
    with pytest.raises(ValueError, match="active_plan_id"):
        build_framework_state(inputs)

    inputs["active_plan_id"] = 42
    with pytest.raises(ValueError, match="active_plan_id"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_invalid_active_task_id():
    inputs = dict(VALID_INPUTS)
    inputs["active_task_id"] = "bad-format"
    with pytest.raises(ValueError, match="active_task_id"):
        build_framework_state(inputs)

    inputs["active_task_id"] = ""
    with pytest.raises(ValueError, match="active_task_id"):
        build_framework_state(inputs)

    inputs["active_task_id"] = 42
    with pytest.raises(ValueError, match="active_task_id"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_invalid_active_milestone():
    # not a dict
    inputs = dict(VALID_INPUTS)
    inputs["active_milestone"] = "not-a-dict"
    with pytest.raises(ValueError, match="active_milestone"):
        build_framework_state(inputs)

    # missing id
    inputs["active_milestone"] = {"status": "in_progress", "branch": "m5/builders"}
    with pytest.raises(ValueError, match="active_milestone"):
        build_framework_state(inputs)

    # missing status
    inputs["active_milestone"] = {"id": "M5", "branch": "m5/builders"}
    with pytest.raises(ValueError, match="active_milestone"):
        build_framework_state(inputs)

    # missing branch
    inputs["active_milestone"] = {"id": "M5", "status": "in_progress"}
    with pytest.raises(ValueError, match="active_milestone"):
        build_framework_state(inputs)

    # invalid id pattern
    inputs["active_milestone"] = {
        "id": "bad",
        "status": "in_progress",
        "branch": "m5/builders",
    }
    with pytest.raises(ValueError, match="active_milestone"):
        build_framework_state(inputs)

    # invalid status
    inputs["active_milestone"] = {
        "id": "M5",
        "status": "unknown",
        "branch": "m5/builders",
    }
    with pytest.raises(ValueError, match="active_milestone"):
        build_framework_state(inputs)

    # branch not a string
    inputs["active_milestone"] = {
        "id": "M5",
        "status": "in_progress",
        "branch": 42,
    }
    with pytest.raises(ValueError, match="active_milestone"):
        build_framework_state(inputs)

    # extra keys
    inputs["active_milestone"] = {
        "id": "M5",
        "status": "in_progress",
        "branch": "m5/builders",
        "extra": "nope",
    }
    with pytest.raises(ValueError, match="active_milestone"):
        build_framework_state(inputs)

    # name not a string
    inputs["active_milestone"] = {
        "id": "M5",
        "name": 42,
        "status": "in_progress",
        "branch": "m5/builders",
    }
    with pytest.raises(ValueError, match="active_milestone"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_invalid_last_completed_step():
    inputs = dict(VALID_INPUTS)
    inputs["last_completed_step"] = "invalid_step"
    with pytest.raises(ValueError, match="last_completed_step"):
        build_framework_state(inputs)

    inputs["last_completed_step"] = ""
    with pytest.raises(ValueError, match="last_completed_step"):
        build_framework_state(inputs)

    inputs["last_completed_step"] = 42
    with pytest.raises(ValueError, match="last_completed_step"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_invalid_artifacts():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["artifacts"] = "not-a-list"
    with pytest.raises(ValueError, match="artifacts"):
        build_framework_state(inputs)

    # item not a dict
    inputs["artifacts"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="artifacts"):
        build_framework_state(inputs)

    # missing required contract_name
    inputs["artifacts"] = [
        {"artifact_id": "INTENT-12345678-001", "path": "x.json", "status": "draft"}
    ]
    with pytest.raises(ValueError, match="contract_name"):
        build_framework_state(inputs)

    # missing required artifact_id
    inputs["artifacts"] = [
        {"contract_name": "intent", "path": "x.json", "status": "draft"}
    ]
    with pytest.raises(ValueError, match="artifact_id"):
        build_framework_state(inputs)

    # missing required path
    inputs["artifacts"] = [
        {
            "contract_name": "intent",
            "artifact_id": "INTENT-12345678-001",
            "status": "draft",
        }
    ]
    with pytest.raises(ValueError, match="path"):
        build_framework_state(inputs)

    # missing required status
    inputs["artifacts"] = [
        {
            "contract_name": "intent",
            "artifact_id": "INTENT-12345678-001",
            "path": "x.json",
        }
    ]
    with pytest.raises(ValueError, match="status"):
        build_framework_state(inputs)

    # empty contract_name
    inputs["artifacts"] = [
        {
            "contract_name": "",
            "artifact_id": "INTENT-12345678-001",
            "path": "x.json",
            "status": "draft",
        }
    ]
    with pytest.raises(ValueError, match="contract_name"):
        build_framework_state(inputs)

    # non-string contract_name
    inputs["artifacts"] = [
        {
            "contract_name": 42,
            "artifact_id": "INTENT-12345678-001",
            "path": "x.json",
            "status": "draft",
        }
    ]
    with pytest.raises(ValueError, match="contract_name"):
        build_framework_state(inputs)

    # invalid status
    inputs["artifacts"] = [
        {
            "contract_name": "intent",
            "artifact_id": "INTENT-12345678-001",
            "path": "x.json",
            "status": "unknown",
        }
    ]
    with pytest.raises(ValueError, match="status"):
        build_framework_state(inputs)

    # non-string artifact_id
    inputs["artifacts"] = [
        {
            "contract_name": "intent",
            "artifact_id": 42,
            "path": "x.json",
            "status": "draft",
        }
    ]
    with pytest.raises(ValueError, match="artifact_id"):
        build_framework_state(inputs)

    # non-string path
    inputs["artifacts"] = [
        {
            "contract_name": "intent",
            "artifact_id": "INTENT-12345678-001",
            "path": 42,
            "status": "draft",
        }
    ]
    with pytest.raises(ValueError, match="path"):
        build_framework_state(inputs)

    # extra keys
    inputs["artifacts"] = [
        {
            "contract_name": "intent",
            "artifact_id": "INTENT-12345678-001",
            "path": "x.json",
            "status": "draft",
            "extra": "nope",
        }
    ]
    with pytest.raises(ValueError, match="artifacts"):
        build_framework_state(inputs)

    # contract_version not a string
    inputs["artifacts"] = [
        {
            "contract_name": "intent",
            "contract_version": 42,
            "artifact_id": "INTENT-12345678-001",
            "path": "x.json",
            "status": "draft",
        }
    ]
    with pytest.raises(ValueError, match="contract_version"):
        build_framework_state(inputs)

    # version not an integer
    inputs["artifacts"] = [
        {
            "contract_name": "intent",
            "artifact_id": "INTENT-12345678-001",
            "path": "x.json",
            "status": "draft",
            "version": "1",
        }
    ]
    with pytest.raises(ValueError, match="version"):
        build_framework_state(inputs)

    # version < 0
    inputs["artifacts"] = [
        {
            "contract_name": "intent",
            "artifact_id": "INTENT-12345678-001",
            "path": "x.json",
            "status": "draft",
            "version": -1,
        }
    ]
    with pytest.raises(ValueError, match="version"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_duplicate_artifacts():
    inputs = dict(VALID_INPUTS)
    inputs["artifacts"] = [
        {
            "contract_name": "intent",
            "artifact_id": "INTENT-12345678-001",
            "path": "x.json",
            "status": "draft",
        },
        {
            "contract_name": "intent",
            "artifact_id": "INTENT-12345678-001",
            "path": "x.json",
            "status": "valid",
        },
    ]
    with pytest.raises(ValueError, match="Duplicate artifact"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_invalid_pending_decisions():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["pending_decisions"] = "not-a-list"
    with pytest.raises(ValueError, match="pending_decisions"):
        build_framework_state(inputs)

    # item not a dict
    inputs["pending_decisions"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="pending_decisions"):
        build_framework_state(inputs)

    # missing decision_id
    inputs["pending_decisions"] = [{"status": "pending"}]
    with pytest.raises(ValueError, match="decision_id"):
        build_framework_state(inputs)

    # missing status
    inputs["pending_decisions"] = [{"decision_id": "DEC-12345678-001"}]
    with pytest.raises(ValueError, match="status"):
        build_framework_state(inputs)

    # invalid decision_id pattern
    inputs["pending_decisions"] = [
        {"decision_id": "bad-format", "status": "pending"}
    ]
    with pytest.raises(ValueError, match="decision_id"):
        build_framework_state(inputs)

    # non-string decision_id
    inputs["pending_decisions"] = [{"decision_id": 42, "status": "pending"}]
    with pytest.raises(ValueError, match="decision_id"):
        build_framework_state(inputs)

    # invalid status
    inputs["pending_decisions"] = [
        {"decision_id": "DEC-12345678-001", "status": "unknown"}
    ]
    with pytest.raises(ValueError, match="status"):
        build_framework_state(inputs)

    # extra keys
    inputs["pending_decisions"] = [
        {
            "decision_id": "DEC-12345678-001",
            "status": "pending",
            "extra": "nope",
        }
    ]
    with pytest.raises(ValueError, match="pending_decisions"):
        build_framework_state(inputs)

    # non-string question
    inputs["pending_decisions"] = [
        {
            "decision_id": "DEC-12345678-001",
            "status": "pending",
            "question": 42,
        }
    ]
    with pytest.raises(ValueError, match="question"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_duplicate_pending_decisions():
    inputs = dict(VALID_INPUTS)
    inputs["pending_decisions"] = [
        {"decision_id": "DEC-12345678-001", "status": "pending"},
        {"decision_id": "DEC-12345678-001", "status": "resolved"},
    ]
    with pytest.raises(ValueError, match="Duplicate decision_id"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_completed_with_pending_decisions():
    inputs = dict(VALID_INPUTS_COMPLETED)
    inputs["pending_decisions"] = [
        {"decision_id": "DEC-12345678-001", "status": "pending"}
    ]
    with pytest.raises(ValueError, match="completed"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_blocked_without_pending_or_summary():
    inputs = dict(VALID_INPUTS_BLOCKED)
    inputs["pending_decisions"] = [
        {"decision_id": "DEC-12345678-001", "status": "resolved"}
    ]
    inputs.pop("human_summary", None)
    with pytest.raises(ValueError, match="blocked"):
        build_framework_state(inputs)

    inputs = dict(VALID_INPUTS_BLOCKED)
    inputs["pending_decisions"] = []
    inputs.pop("human_summary", None)
    with pytest.raises(ValueError, match="blocked"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_invalid_human_summary():
    inputs = dict(VALID_INPUTS)
    inputs["human_summary"] = 42
    with pytest.raises(ValueError, match="human_summary"):
        build_framework_state(inputs)


def test_build_framework_state_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_framework_state(VALID_INPUTS)
