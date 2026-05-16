import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.plan import (
    SchemaValidationError,
    build_plan,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "plan.schema.json"

VALID_INPUTS: dict[str, object] = {
    "intent_id": "INTENT-12345678-001",
    "roadmap_slice_id": "RSLICE-12345678-002",
    "goal": "Implement the build_plan builder for ADF M5.4",
    "tasks": [
        {
            "task_id": "TASK-10000000-001",
            "title": "Read schema and governance docs",
            "type": "plan",
            "depends_on": [],
            "inputs": ["plan.schema.json"],
            "outputs": ["Understanding of plan schema"],
        },
        {
            "task_id": "TASK-10000000-002",
            "title": "Implement build_plan function",
            "type": "implementation",
            "depends_on": ["TASK-10000000-001"],
            "inputs": ["Schema understanding"],
            "outputs": ["plan.py"],
            "owner_hint": "developer",
        },
        {
            "task_id": "TASK-10000000-003",
            "title": "Write tests for build_plan",
            "type": "test",
            "depends_on": ["TASK-10000000-002"],
            "outputs": ["test_build_plan.py"],
        },
        {
            "task_id": "TASK-10000000-004",
            "title": "Review and validate",
            "type": "review",
            "depends_on": ["TASK-10000000-003"],
        },
    ],
    "acceptance_criteria": [
        "build_plan produces schema-valid output",
        "build_plan is deterministic",
        "build_plan rejects invalid inputs",
        "All 16 tests pass",
    ],
    "constraints": [
        "Do not create runtime",
        "Do not create adapters",
        "Do not modify schemas",
        "Do not add dependencies",
    ],
    "requires_user_confirmation": False,
    "estimated_order": [
        "TASK-10000000-001",
        "TASK-10000000-002",
        "TASK-10000000-003",
        "TASK-10000000-004",
    ],
    "assumptions": [
        "Schema is stable",
        "Existing builders serve as reference",
    ],
    "out_of_scope": [
        "Creating runtime",
        "Creating adapters",
    ],
    "risk_register": [
        {
            "risk": "Schema validation failure",
            "impact": "Builder cannot produce valid output",
            "mitigation": "Test early with jsonschema validation",
        },
        {
            "risk": "Task dependency cycle",
            "impact": "Execution may deadlock",
            "mitigation": "Validate dependencies are acyclic",
        },
    ],
    "human_summary": "Implementation of the build_plan builder.",
}


def test_build_plan_schema_valid():
    artifact = build_plan(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_plan_is_deterministic():
    a = build_plan(VALID_INPUTS)
    b = build_plan(VALID_INPUTS)
    c = build_plan(VALID_INPUTS)

    assert a == b == c


def test_build_plan_rejects_missing_required_input():
    for missing_key in (
        "intent_id",
        "roadmap_slice_id",
        "goal",
        "tasks",
        "acceptance_criteria",
        "constraints",
        "requires_user_confirmation",
    ):
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_plan(inputs)


def test_build_plan_writes_output_path(tmp_path):
    output_path = tmp_path / "plan.json"

    artifact = build_plan(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_plan_rejects_invalid_intent_id():
    inputs = dict(VALID_INPUTS)
    inputs["intent_id"] = "bad-format"
    with pytest.raises(ValueError, match="intent_id"):
        build_plan(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["intent_id"] = ""
    with pytest.raises(ValueError, match="intent_id"):
        build_plan(inputs)


def test_build_plan_rejects_invalid_roadmap_slice_id():
    inputs = dict(VALID_INPUTS)
    inputs["roadmap_slice_id"] = "bad-format"
    with pytest.raises(ValueError, match="roadmap_slice_id"):
        build_plan(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["roadmap_slice_id"] = ""
    with pytest.raises(ValueError, match="roadmap_slice_id"):
        build_plan(inputs)


def test_build_plan_rejects_invalid_goal():
    inputs = dict(VALID_INPUTS)
    inputs["goal"] = ""
    with pytest.raises(ValueError, match="goal"):
        build_plan(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["goal"] = 42
    with pytest.raises(ValueError, match="goal"):
        build_plan(inputs)


def test_build_plan_rejects_invalid_task():
    # empty tasks
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = []
    with pytest.raises(ValueError, match="tasks"):
        build_plan(inputs)

    # tasks not a list
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = "not-a-list"
    with pytest.raises(ValueError, match="tasks"):
        build_plan(inputs)

    # task not a dict
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="tasks"):
        build_plan(inputs)

    # missing task_id
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"title": "Do something", "type": "implementation", "depends_on": []}]
    with pytest.raises(ValueError, match="'task_id'"):
        build_plan(inputs)

    # missing title
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "TASK-10000000-001", "type": "implementation", "depends_on": []}]
    with pytest.raises(ValueError, match="'title'"):
        build_plan(inputs)

    # missing type
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "TASK-10000000-001", "title": "Do", "depends_on": []}]
    with pytest.raises(ValueError, match="'type'"):
        build_plan(inputs)

    # missing depends_on
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "TASK-10000000-001", "title": "Do", "type": "implementation"}]
    with pytest.raises(ValueError, match="'depends_on'"):
        build_plan(inputs)

    # invalid task_id pattern
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "bad", "title": "Do", "type": "implementation", "depends_on": []}]
    with pytest.raises(ValueError, match="task_id"):
        build_plan(inputs)

    # invalid task type
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "TASK-10000000-001", "title": "Do", "type": "invalid_type", "depends_on": []}]
    with pytest.raises(ValueError, match="type"):
        build_plan(inputs)

    # depends_on not a list
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "TASK-10000000-001", "title": "Do", "type": "implementation", "depends_on": "not-a-list"}]
    with pytest.raises(ValueError, match="depends_on"):
        build_plan(inputs)

    # depends_on item invalid pattern
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "TASK-10000000-001", "title": "Do", "type": "implementation", "depends_on": ["bad"]}]
    with pytest.raises(ValueError, match="depends_on"):
        build_plan(inputs)

    # extra task keys
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "TASK-10000000-001", "title": "Do", "type": "implementation", "depends_on": [], "extra": "nope"}]
    with pytest.raises(ValueError, match="extra keys"):
        build_plan(inputs)

    # inputs not a list
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "TASK-10000000-001", "title": "Do", "type": "implementation", "depends_on": [], "inputs": "not-a-list"}]
    with pytest.raises(ValueError, match="inputs"):
        build_plan(inputs)

    # inputs item not a string
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "TASK-10000000-001", "title": "Do", "type": "implementation", "depends_on": [], "inputs": [42]}]
    with pytest.raises(ValueError, match="inputs"):
        build_plan(inputs)

    # outputs item not a string
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "TASK-10000000-001", "title": "Do", "type": "implementation", "depends_on": [], "outputs": [42]}]
    with pytest.raises(ValueError, match="outputs"):
        build_plan(inputs)

    # owner_hint not a string
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [{"task_id": "TASK-10000000-001", "title": "Do", "type": "implementation", "depends_on": [], "owner_hint": 42}]
    with pytest.raises(ValueError, match="owner_hint"):
        build_plan(inputs)


def test_build_plan_rejects_duplicate_task_id():
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [
        {"task_id": "TASK-10000000-001", "title": "First", "type": "implementation", "depends_on": []},
        {"task_id": "TASK-10000000-001", "title": "Second", "type": "test", "depends_on": []},
    ]
    with pytest.raises(ValueError, match="Duplicate task_id"):
        build_plan(inputs)


def test_build_plan_rejects_unknown_dependency():
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [
        {"task_id": "TASK-10000000-001", "title": "First", "type": "implementation", "depends_on": ["TASK-99999999-999"]},
    ]
    with pytest.raises(ValueError, match="unknown task_id"):
        build_plan(inputs)


def test_build_plan_rejects_self_dependency():
    inputs = dict(VALID_INPUTS)
    inputs["tasks"] = [
        {"task_id": "TASK-10000000-001", "title": "Self-referential", "type": "implementation", "depends_on": ["TASK-10000000-001"]},
    ]
    with pytest.raises(ValueError, match="depends on itself"):
        build_plan(inputs)


def test_build_plan_rejects_invalid_estimated_order():
    # contains unknown task_id
    inputs = dict(VALID_INPUTS)
    inputs["estimated_order"] = ["TASK-10000000-001", "TASK-99999999-999"]
    with pytest.raises(ValueError, match="not a known task_id"):
        build_plan(inputs)

    # contains duplicate
    inputs = dict(VALID_INPUTS)
    inputs["estimated_order"] = ["TASK-10000000-001", "TASK-10000000-001"]
    with pytest.raises(ValueError, match="Duplicate task_id"):
        build_plan(inputs)

    # invalid pattern
    inputs = dict(VALID_INPUTS)
    inputs["estimated_order"] = ["bad-pattern"]
    with pytest.raises(ValueError, match="estimated_order"):
        build_plan(inputs)

    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["estimated_order"] = "not-a-list"
    with pytest.raises(ValueError, match="estimated_order"):
        build_plan(inputs)


def test_build_plan_rejects_invalid_acceptance_criteria_or_constraints():
    # empty acceptance_criteria
    inputs = dict(VALID_INPUTS)
    inputs["acceptance_criteria"] = []
    with pytest.raises(ValueError, match="acceptance_criteria"):
        build_plan(inputs)

    # acceptance_criteria not a list
    inputs = dict(VALID_INPUTS)
    inputs["acceptance_criteria"] = "not-a-list"
    with pytest.raises(ValueError, match="acceptance_criteria"):
        build_plan(inputs)

    # acceptance_criteria with empty string item
    inputs = dict(VALID_INPUTS)
    inputs["acceptance_criteria"] = ["valid", ""]
    with pytest.raises(ValueError, match="acceptance_criteria"):
        build_plan(inputs)

    # empty constraints
    inputs = dict(VALID_INPUTS)
    inputs["constraints"] = []
    with pytest.raises(ValueError, match="constraints"):
        build_plan(inputs)

    # constraints not a list
    inputs = dict(VALID_INPUTS)
    inputs["constraints"] = "not-a-list"
    with pytest.raises(ValueError, match="constraints"):
        build_plan(inputs)


def test_build_plan_rejects_invalid_risk_register():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["risk_register"] = "not-a-list"
    with pytest.raises(ValueError, match="risk_register"):
        build_plan(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["risk_register"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="risk_register"):
        build_plan(inputs)

    # missing risk
    inputs = dict(VALID_INPUTS)
    inputs["risk_register"] = [{"impact": "high"}]
    with pytest.raises(ValueError, match="'risk'"):
        build_plan(inputs)

    # missing impact
    inputs = dict(VALID_INPUTS)
    inputs["risk_register"] = [{"risk": "failure"}]
    with pytest.raises(ValueError, match="'impact'"):
        build_plan(inputs)

    # extra keys
    inputs = dict(VALID_INPUTS)
    inputs["risk_register"] = [
        {"risk": "failure", "impact": "high", "extra": "nope"}
    ]
    with pytest.raises(ValueError, match="extra keys"):
        build_plan(inputs)

    # risk not a string
    inputs = dict(VALID_INPUTS)
    inputs["risk_register"] = [{"risk": 42, "impact": "high"}]
    with pytest.raises(ValueError, match="risk"):
        build_plan(inputs)

    # mitigation not a string
    inputs = dict(VALID_INPUTS)
    inputs["risk_register"] = [
        {"risk": "failure", "impact": "high", "mitigation": 42}
    ]
    with pytest.raises(ValueError, match="mitigation"):
        build_plan(inputs)


def test_build_plan_rejects_invalid_optional_collections():
    # assumptions not a list
    inputs = dict(VALID_INPUTS)
    inputs["assumptions"] = "not-a-list"
    with pytest.raises(ValueError, match="assumptions"):
        build_plan(inputs)

    # assumptions item not a string
    inputs = dict(VALID_INPUTS)
    inputs["assumptions"] = ["valid", 42]
    with pytest.raises(ValueError, match="assumptions"):
        build_plan(inputs)

    # out_of_scope not a list
    inputs = dict(VALID_INPUTS)
    inputs["out_of_scope"] = "not-a-list"
    with pytest.raises(ValueError, match="out_of_scope"):
        build_plan(inputs)

    # out_of_scope item not a string
    inputs = dict(VALID_INPUTS)
    inputs["out_of_scope"] = ["valid", 42]
    with pytest.raises(ValueError, match="out_of_scope"):
        build_plan(inputs)

    # human_summary not a string
    inputs = dict(VALID_INPUTS)
    inputs["human_summary"] = 42
    with pytest.raises(ValueError, match="human_summary"):
        build_plan(inputs)

    # requires_user_confirmation not a boolean
    inputs = dict(VALID_INPUTS)
    inputs["requires_user_confirmation"] = "yes"
    with pytest.raises(ValueError, match="requires_user_confirmation"):
        build_plan(inputs)


def test_build_plan_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_plan(VALID_INPUTS)
