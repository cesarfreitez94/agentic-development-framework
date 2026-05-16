import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.roadmap_slice import (
    SchemaValidationError,
    build_roadmap_slice,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "roadmap_slice.schema.json"

VALID_INPUTS: dict[str, object] = {
    "intent_id": "INTENT-12345678-001",
    "active_milestone": {
        "id": "M5",
        "name": "Builders extraction",
        "status": "in_progress",
        "branch": "feature/builders",
    },
    "relevant_milestones": [
        {
            "id": "M4",
            "name": "Agent migration",
            "status": "completed",
            "branch": "main",
            "capabilities": ["agent_migration"],
        },
        {
            "id": "M5",
            "name": "Builders extraction",
            "status": "in_progress",
            "branch": "feature/builders",
        },
    ],
    "policy_refs": ["POL-001", "POL-002"],
    "allowed_operations": [
        "design_schema",
        "read_contract",
        "validate_schema",
        "run_tests",
        "create_review_report",
    ],
    "blocked_operations": [
        "commit",
        "push",
        "open_pr",
        "merge_pr",
    ],
    "source_refs": [
        {
            "path": "schemas/meta/roadmap_slice.schema.json",
            "section": "properties",
        },
        {
            "path": "src/agentic_development_framework/builders/intent.py",
            "line_ranges": [{"start": 1, "end": 50}],
        },
    ],
    "open_issues": [
        {
            "issue_id": "ISSUE-001",
            "title": "Test coverage for roadmap builder",
            "status": "open",
            "url": "https://example.com/issues/1",
        },
    ],
    "branch_context": {"current": "feature/roadmap-builder", "base": "main"},
    "recent_changes": ["Added intent builder", "Added policy constraints builder"],
    "risk_notes": ["No runtime yet", "Schema validation depends on jsonschema"],
    "human_summary": "Roadmap slice for M5.3 builder extraction.",
}


def test_build_roadmap_slice_schema_valid():
    artifact = build_roadmap_slice(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_roadmap_slice_is_deterministic():
    a = build_roadmap_slice(VALID_INPUTS)
    b = build_roadmap_slice(VALID_INPUTS)
    c = build_roadmap_slice(VALID_INPUTS)

    assert a == b == c


def test_build_roadmap_slice_rejects_missing_required_input():
    for missing_key in (
        "intent_id",
        "active_milestone",
        "relevant_milestones",
        "policy_refs",
        "allowed_operations",
        "blocked_operations",
        "source_refs",
    ):
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_roadmap_slice(inputs)


def test_build_roadmap_slice_writes_output_path(tmp_path):
    output_path = tmp_path / "roadmap_slice.json"

    artifact = build_roadmap_slice(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_roadmap_slice_rejects_invalid_intent_id():
    inputs = dict(VALID_INPUTS)
    inputs["intent_id"] = "bad-format"
    with pytest.raises(ValueError, match="intent_id"):
        build_roadmap_slice(inputs)


def test_build_roadmap_slice_rejects_invalid_active_milestone():
    # Not a dict
    inputs = dict(VALID_INPUTS)
    inputs["active_milestone"] = "not-a-dict"
    with pytest.raises(ValueError, match="active_milestone"):
        build_roadmap_slice(inputs)

    # Missing id
    inputs = dict(VALID_INPUTS)
    inputs["active_milestone"] = {"status": "planned", "branch": "main"}
    with pytest.raises(ValueError, match="'id'"):
        build_roadmap_slice(inputs)

    # Invalid id pattern
    inputs = dict(VALID_INPUTS)
    inputs["active_milestone"] = {
        "id": "invalid",
        "status": "planned",
        "branch": "main",
    }
    with pytest.raises(ValueError, match="active_milestone"):
        build_roadmap_slice(inputs)

    # Invalid status
    inputs = dict(VALID_INPUTS)
    inputs["active_milestone"] = {
        "id": "M5",
        "status": "unknown",
        "branch": "main",
    }
    with pytest.raises(ValueError, match="status"):
        build_roadmap_slice(inputs)

    # Extra keys
    inputs = dict(VALID_INPUTS)
    inputs["active_milestone"] = {
        "id": "M5",
        "status": "planned",
        "branch": "main",
        "extra": "nope",
    }
    with pytest.raises(ValueError, match="extra keys"):
        build_roadmap_slice(inputs)


def test_build_roadmap_slice_rejects_invalid_relevant_milestone():
    # Not a list
    inputs = dict(VALID_INPUTS)
    inputs["relevant_milestones"] = "not-a-list"
    with pytest.raises(ValueError, match="relevant_milestones"):
        build_roadmap_slice(inputs)

    # Empty list
    inputs = dict(VALID_INPUTS)
    inputs["relevant_milestones"] = []
    with pytest.raises(ValueError, match="relevant_milestones"):
        build_roadmap_slice(inputs)

    # Item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["relevant_milestones"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="relevant_milestones"):
        build_roadmap_slice(inputs)

    # Item missing id
    inputs = dict(VALID_INPUTS)
    inputs["relevant_milestones"] = [{"status": "planned"}]
    with pytest.raises(ValueError, match="'id'"):
        build_roadmap_slice(inputs)

    # Item missing status
    inputs = dict(VALID_INPUTS)
    inputs["relevant_milestones"] = [{"id": "M5"}]
    with pytest.raises(ValueError, match="'status'"):
        build_roadmap_slice(inputs)

    # Invalid status
    inputs = dict(VALID_INPUTS)
    inputs["relevant_milestones"] = [{"id": "M5", "status": "unknown"}]
    with pytest.raises(ValueError, match="status"):
        build_roadmap_slice(inputs)

    # Extra keys
    inputs = dict(VALID_INPUTS)
    inputs["relevant_milestones"] = [
        {"id": "M5", "status": "planned", "extra": "nope"},
    ]
    with pytest.raises(ValueError, match="extra keys"):
        build_roadmap_slice(inputs)

    # Invalid capabilities (not a list)
    inputs = dict(VALID_INPUTS)
    inputs["relevant_milestones"] = [
        {"id": "M5", "status": "planned", "capabilities": "not-a-list"},
    ]
    with pytest.raises(ValueError, match="capabilities"):
        build_roadmap_slice(inputs)

    # Invalid capabilities item (not a string)
    inputs = dict(VALID_INPUTS)
    inputs["relevant_milestones"] = [
        {"id": "M5", "status": "planned", "capabilities": [42]},
    ]
    with pytest.raises(ValueError, match="capabilities"):
        build_roadmap_slice(inputs)


def test_build_roadmap_slice_rejects_invalid_operation():
    # Invalid operation in allowed_operations
    inputs = dict(VALID_INPUTS)
    inputs["allowed_operations"] = ["design_schema", "invalid_op"]
    with pytest.raises(ValueError, match="invalid_op"):
        build_roadmap_slice(inputs)

    # Invalid operation in blocked_operations
    inputs = dict(VALID_INPUTS)
    inputs["blocked_operations"] = ["commit", "not_an_op"]
    with pytest.raises(ValueError, match="not_an_op"):
        build_roadmap_slice(inputs)


def test_build_roadmap_slice_rejects_overlapping_operations():
    inputs = dict(VALID_INPUTS)
    inputs["allowed_operations"] = ["design_schema", "run_tests"]
    inputs["blocked_operations"] = ["run_tests", "push"]
    with pytest.raises(ValueError, match="overlap"):
        build_roadmap_slice(inputs)


def test_build_roadmap_slice_rejects_invalid_source_ref():
    # Not a list
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = "not-a-list"
    with pytest.raises(ValueError, match="source_refs"):
        build_roadmap_slice(inputs)

    # Empty list
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = []
    with pytest.raises(ValueError, match="source_refs"):
        build_roadmap_slice(inputs)

    # Item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="source_refs"):
        build_roadmap_slice(inputs)

    # Missing path
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = [{"section": "intro"}]
    with pytest.raises(ValueError, match="'path'"):
        build_roadmap_slice(inputs)

    # Empty path
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = [{"path": ""}]
    with pytest.raises(ValueError, match="source_refs"):
        build_roadmap_slice(inputs)

    # Extra keys
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = [{"path": "doc.md", "extra": "nope"}]
    with pytest.raises(ValueError, match="extra keys"):
        build_roadmap_slice(inputs)

    # Invalid line_ranges: start not integer
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = [
        {"path": "doc.md", "line_ranges": [{"start": "1", "end": 5}]},
    ]
    with pytest.raises(ValueError, match="start"):
        build_roadmap_slice(inputs)

    # Invalid line_ranges: start < 1
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = [
        {"path": "doc.md", "line_ranges": [{"start": 0, "end": 5}]},
    ]
    with pytest.raises(ValueError, match="start"):
        build_roadmap_slice(inputs)

    # Invalid line_ranges: start > end
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = [
        {"path": "doc.md", "line_ranges": [{"start": 10, "end": 5}]},
    ]
    with pytest.raises(ValueError, match="start"):
        build_roadmap_slice(inputs)


def test_build_roadmap_slice_rejects_invalid_optional_collections():
    # open_issues: missing issue_id
    inputs = dict(VALID_INPUTS)
    inputs["open_issues"] = [{"title": "Test", "status": "open"}]
    with pytest.raises(ValueError, match="issue_id"):
        build_roadmap_slice(inputs)

    # open_issues: extra keys
    inputs = dict(VALID_INPUTS)
    inputs["open_issues"] = [
        {"issue_id": "1", "title": "T", "status": "open", "extra": "nope"},
    ]
    with pytest.raises(ValueError, match="extra keys"):
        build_roadmap_slice(inputs)

    # branch_context: missing current
    inputs = dict(VALID_INPUTS)
    inputs["branch_context"] = {"base": "main"}
    with pytest.raises(ValueError, match="current"):
        build_roadmap_slice(inputs)

    # branch_context: extra keys
    inputs = dict(VALID_INPUTS)
    inputs["branch_context"] = {
        "current": "feat/x",
        "base": "main",
        "extra": "nope",
    }
    with pytest.raises(ValueError, match="extra keys"):
        build_roadmap_slice(inputs)

    # recent_changes: not a list
    inputs = dict(VALID_INPUTS)
    inputs["recent_changes"] = "not-a-list"
    with pytest.raises(ValueError, match="recent_changes"):
        build_roadmap_slice(inputs)

    # recent_changes: item not string
    inputs = dict(VALID_INPUTS)
    inputs["recent_changes"] = ["valid", 42]
    with pytest.raises(ValueError, match="recent_changes"):
        build_roadmap_slice(inputs)

    # risk_notes: not a list
    inputs = dict(VALID_INPUTS)
    inputs["risk_notes"] = "not-a-list"
    with pytest.raises(ValueError, match="risk_notes"):
        build_roadmap_slice(inputs)

    # human_summary: not a string
    inputs = dict(VALID_INPUTS)
    inputs["human_summary"] = 42
    with pytest.raises(ValueError, match="human_summary"):
        build_roadmap_slice(inputs)


def test_build_roadmap_slice_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_roadmap_slice(VALID_INPUTS)
