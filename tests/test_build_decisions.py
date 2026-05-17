import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.decisions import (
    SchemaValidationError,
    build_decisions,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "decisions.schema.json"

VALID_INPUTS_PENDING: dict[str, object] = {
    "decision_type": "user_confirmation",
    "status": "pending",
    "question": "Should we proceed with the database migration?",
    "options": ["Yes, proceed now", "Wait for approval", "Defer to next milestone"],
    "selected_option": None,
    "required_by": ["orchestrator", "review_gate"],
}

VALID_INPUTS_RESOLVED: dict[str, object] = {
    "decision_type": "policy_gate",
    "status": "resolved",
    "question": "Does this change comply with governance policy POL-GOV-001?",
    "options": ["Yes", "No"],
    "selected_option": "Yes",
    "required_by": ["policy_check"],
    "resolved_at": "2025-06-15T10:30:00+00:00",
    "rationale": "All governance checks passed.",
    "related_artifacts": [
        {"contract_name": "policy_constraints", "artifact_id": "POLICY-12345678-001"},
        {"contract_name": "review_report", "path": "artifacts/review_report.json"},
    ],
    "expires_at": "2025-07-15T00:00:00+00:00",
    "supersedes_decision_id": "DEC-00000001-001",
    "human_summary": "Policy gate cleared for database migration.",
}

VALID_INPUTS_CANCELLED: dict[str, object] = {
    "decision_type": "review_gate",
    "status": "cancelled",
    "question": "Should we merge PR #42?",
    "options": ["Merge", "Close PR", "Request changes"],
    "selected_option": "Close PR",
    "required_by": ["reviewer"],
    "rationale": "PR superseded by PR #43.",
}

VALID_INPUTS_CANCELLED_NULL: dict[str, object] = {
    "decision_type": "workflow",
    "status": "cancelled",
    "question": "Should we run the full CI pipeline?",
    "options": ["Run full pipeline", "Run only unit tests", "Skip"],
    "selected_option": None,
    "required_by": ["orchestrator"],
}


def test_build_decisions_schema_valid():
    artifact = build_decisions(VALID_INPUTS_PENDING)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_decisions_is_deterministic():
    a = build_decisions(VALID_INPUTS_RESOLVED)
    b = build_decisions(VALID_INPUTS_RESOLVED)
    c = build_decisions(VALID_INPUTS_RESOLVED)

    assert a == b == c


def test_build_decisions_rejects_missing_required_input():
    required_keys = {
        "decision_type",
        "status",
        "question",
        "options",
        "selected_option",
        "required_by",
    }
    for missing_key in required_keys:
        inputs = {k: v for k, v in VALID_INPUTS_PENDING.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_decisions(inputs)


def test_build_decisions_writes_output_path(tmp_path):
    output_path = tmp_path / "decisions.json"

    artifact = build_decisions(VALID_INPUTS_PENDING, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_decisions_rejects_invalid_decision_type():
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["decision_type"] = "invalid_type"
    with pytest.raises(ValueError, match="decision_type"):
        build_decisions(inputs)

    inputs["decision_type"] = ""
    with pytest.raises(ValueError, match="decision_type"):
        build_decisions(inputs)

    inputs["decision_type"] = 42
    with pytest.raises(ValueError, match="decision_type"):
        build_decisions(inputs)


def test_build_decisions_rejects_invalid_status():
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["status"] = "unknown"
    with pytest.raises(ValueError, match="status"):
        build_decisions(inputs)

    inputs["status"] = ""
    with pytest.raises(ValueError, match="status"):
        build_decisions(inputs)

    inputs["status"] = 42
    with pytest.raises(ValueError, match="status"):
        build_decisions(inputs)


def test_build_decisions_rejects_invalid_question():
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["question"] = ""
    with pytest.raises(ValueError, match="question"):
        build_decisions(inputs)

    inputs["question"] = 42
    with pytest.raises(ValueError, match="question"):
        build_decisions(inputs)


def test_build_decisions_rejects_invalid_options():
    # not a list
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["options"] = "not-a-list"
    with pytest.raises(ValueError, match="options"):
        build_decisions(inputs)

    # fewer than 2 items
    inputs["options"] = ["Only one"]
    with pytest.raises(ValueError, match="options"):
        build_decisions(inputs)

    # empty list
    inputs["options"] = []
    with pytest.raises(ValueError, match="options"):
        build_decisions(inputs)

    # non-string item
    inputs["options"] = [42, "ok"]
    with pytest.raises(ValueError, match="options"):
        build_decisions(inputs)

    # empty string item
    inputs["options"] = ["", "ok"]
    with pytest.raises(ValueError, match="options"):
        build_decisions(inputs)

    # duplicate items
    inputs["options"] = ["duplicate", "duplicate"]
    with pytest.raises(ValueError, match="options"):
        build_decisions(inputs)


def test_build_decisions_rejects_selected_option_not_in_options():
    inputs = dict(VALID_INPUTS_RESOLVED)
    inputs["selected_option"] = "Not in list"
    with pytest.raises(ValueError, match="not in options"):
        build_decisions(inputs)


def test_build_decisions_rejects_pending_with_selected_option():
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["selected_option"] = "Yes, proceed now"
    with pytest.raises(ValueError, match="pending"):
        build_decisions(inputs)


def test_build_decisions_rejects_pending_with_resolved_at():
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["resolved_at"] = "2025-06-15T10:30:00+00:00"
    with pytest.raises(ValueError, match="pending"):
        build_decisions(inputs)


def test_build_decisions_generates_resolved_at_for_resolved_status():
    inputs = dict(VALID_INPUTS_RESOLVED)
    inputs.pop("resolved_at", None)

    artifact = build_decisions(inputs)

    assert "resolved_at" in artifact
    assert isinstance(artifact["resolved_at"], str)
    assert len(artifact["resolved_at"]) > 0

    # verify schema validates
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)

    # verify deterministic
    a = build_decisions(inputs)
    b = build_decisions(inputs)
    assert a["resolved_at"] == b["resolved_at"]


def test_build_decisions_rejects_resolved_without_selected_option():
    inputs = dict(VALID_INPUTS_RESOLVED)
    inputs["selected_option"] = None
    with pytest.raises(ValueError, match="resolved"):
        build_decisions(inputs)

    inputs = dict(VALID_INPUTS_RESOLVED)
    del inputs["selected_option"]
    with pytest.raises(ValueError, match="selected_option"):
        build_decisions(inputs)


def test_build_decisions_rejects_invalid_required_by():
    # not a list
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["required_by"] = "not-a-list"
    with pytest.raises(ValueError, match="required_by"):
        build_decisions(inputs)

    # empty list
    inputs["required_by"] = []
    with pytest.raises(ValueError, match="required_by"):
        build_decisions(inputs)

    # non-string item
    inputs["required_by"] = [42]
    with pytest.raises(ValueError, match="required_by"):
        build_decisions(inputs)

    # empty string item
    inputs["required_by"] = [""]
    with pytest.raises(ValueError, match="required_by"):
        build_decisions(inputs)


def test_build_decisions_rejects_duplicate_required_by():
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["required_by"] = ["orchestrator", "orchestrator"]
    with pytest.raises(ValueError, match="Duplicate"):
        build_decisions(inputs)


def test_build_decisions_rejects_invalid_related_artifacts():
    # not a list
    inputs = dict(VALID_INPUTS_RESOLVED)
    inputs["related_artifacts"] = "not-a-list"
    with pytest.raises(ValueError, match="related_artifacts"):
        build_decisions(inputs)

    # item not a dict
    inputs["related_artifacts"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="related_artifacts"):
        build_decisions(inputs)

    # missing contract_name
    inputs["related_artifacts"] = [
        {"artifact_id": "POLICY-12345678-001"},
    ]
    with pytest.raises(ValueError, match="related_artifacts"):
        build_decisions(inputs)

    # empty contract_name
    inputs["related_artifacts"] = [
        {"contract_name": ""},
    ]
    with pytest.raises(ValueError, match="related_artifacts"):
        build_decisions(inputs)

    # extra keys
    inputs["related_artifacts"] = [
        {"contract_name": "policy_constraints", "extra": "nope"},
    ]
    with pytest.raises(ValueError, match="related_artifacts"):
        build_decisions(inputs)

    # artifact_id not a string
    inputs["related_artifacts"] = [
        {"contract_name": "policy_constraints", "artifact_id": 42},
    ]
    with pytest.raises(ValueError, match="related_artifacts"):
        build_decisions(inputs)

    # path not a string
    inputs["related_artifacts"] = [
        {"contract_name": "review_report", "path": 42},
    ]
    with pytest.raises(ValueError, match="related_artifacts"):
        build_decisions(inputs)


def test_build_decisions_rejects_duplicate_related_artifacts():
    inputs = dict(VALID_INPUTS_RESOLVED)
    inputs["related_artifacts"] = [
        {"contract_name": "policy_constraints", "artifact_id": "POLICY-12345678-001"},
        {"contract_name": "policy_constraints", "artifact_id": "POLICY-12345678-001"},
    ]
    with pytest.raises(ValueError, match="Duplicate related_artifact"):
        build_decisions(inputs)


def test_build_decisions_rejects_invalid_supersedes_decision_id():
    # not a string
    inputs = dict(VALID_INPUTS_RESOLVED)
    inputs["supersedes_decision_id"] = 42
    with pytest.raises(ValueError, match="supersedes_decision_id"):
        build_decisions(inputs)

    # wrong pattern
    inputs["supersedes_decision_id"] = "bad-format"
    with pytest.raises(ValueError, match="supersedes_decision_id"):
        build_decisions(inputs)

    # empty string
    inputs["supersedes_decision_id"] = ""
    with pytest.raises(ValueError, match="supersedes_decision_id"):
        build_decisions(inputs)


def test_build_decisions_rejects_invalid_optional_strings():
    # rationale not a string
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["rationale"] = 42
    with pytest.raises(ValueError, match="rationale"):
        build_decisions(inputs)

    # resolved_at not a string
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["resolved_at"] = 42
    with pytest.raises(ValueError, match="resolved_at"):
        build_decisions(inputs)

    # expires_at not a string
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["expires_at"] = 42
    with pytest.raises(ValueError, match="expires_at"):
        build_decisions(inputs)

    # human_summary not a string
    inputs = dict(VALID_INPUTS_PENDING)
    inputs["human_summary"] = 42
    with pytest.raises(ValueError, match="human_summary"):
        build_decisions(inputs)


def test_build_decisions_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_decisions(VALID_INPUTS_PENDING)
