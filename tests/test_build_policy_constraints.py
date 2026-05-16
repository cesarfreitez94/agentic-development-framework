import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.policy_constraints import (
    SchemaValidationError,
    build_policy_constraints,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "policy_constraints.schema.json"

VALID_INPUTS: dict[str, object] = {
    "intent_id": "INTENT-12345678-001",
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
    "required_checks": [
        "issue_required_before_code",
        "tests_required_before_pr",
        "manual_review_before_main_pr",
    ],
    "requires_user_confirmation": True,
    "rationale": "Standard agentic pipeline constraints.",
    "human_summary": "Policy constraints for agentic development pipeline.",
}


def test_build_policy_constraints_schema_valid():
    artifact = build_policy_constraints(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_policy_constraints_is_deterministic():
    a = build_policy_constraints(VALID_INPUTS)
    b = build_policy_constraints(VALID_INPUTS)
    c = build_policy_constraints(VALID_INPUTS)

    assert a == b == c


def test_build_policy_constraints_rejects_missing_required_input():
    for missing_key in (
        "intent_id",
        "policy_refs",
        "allowed_operations",
        "blocked_operations",
        "required_checks",
        "requires_user_confirmation",
    ):
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_policy_constraints(inputs)


def test_build_policy_constraints_writes_output_path(tmp_path):
    output_path = tmp_path / "policy_constraints.json"

    artifact = build_policy_constraints(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_policy_constraints_rejects_invalid_intent_id():
    inputs = dict(VALID_INPUTS)
    inputs["intent_id"] = "bad-format"
    with pytest.raises(ValueError, match="intent_id"):
        build_policy_constraints(inputs)


def test_build_policy_constraints_rejects_invalid_operation():
    inputs = dict(VALID_INPUTS)
    inputs["allowed_operations"] = ["design_schema", "invalid_op"]
    with pytest.raises(ValueError, match="invalid_op"):
        build_policy_constraints(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["blocked_operations"] = ["commit", "not_an_op"]
    with pytest.raises(ValueError, match="not_an_op"):
        build_policy_constraints(inputs)


def test_build_policy_constraints_rejects_overlapping_operations():
    inputs = dict(VALID_INPUTS)
    inputs["allowed_operations"] = ["design_schema", "run_tests"]
    inputs["blocked_operations"] = ["run_tests", "push"]
    with pytest.raises(ValueError, match="overlap"):
        build_policy_constraints(inputs)


def test_build_policy_constraints_rejects_invalid_required_check():
    inputs = dict(VALID_INPUTS)
    inputs["required_checks"] = [
        "issue_required_before_code",
        "invalid_check",
    ]
    with pytest.raises(ValueError, match="invalid_check"):
        build_policy_constraints(inputs)


def test_build_policy_constraints_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_policy_constraints(VALID_INPUTS)
