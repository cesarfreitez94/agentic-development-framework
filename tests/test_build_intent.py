import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.intent import (
    SchemaValidationError,
    build_intent,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "intent.schema.json"

VALID_INPUTS: dict[str, object] = {
    "source": "user",
    "objective": "Implement login feature",
    "scope_include": ["Add login page", "Add authentication API"],
    "scope_exclude": ["Password reset", "OAuth integration"],
    "constraints": ["Must use existing auth library", "Must pass all tests"],
    "requested_outputs": ["Working login page", "Auth API endpoint"],
    "non_goals": ["Social login", "Two-factor auth"],
    "urgency": "high",
    "requires_user_confirmation": True,
    "related_milestone": {
        "id": "M5",
        "status": "in_progress",
        "branch": "feature/login",
    },
    "human_summary": "Add authentication functionality",
}


def test_build_intent_schema_valid():
    artifact = build_intent(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_intent_is_deterministic():
    a = build_intent(VALID_INPUTS)
    b = build_intent(VALID_INPUTS)
    c = build_intent(VALID_INPUTS)

    assert a == b == c


def test_build_intent_rejects_missing_required_input():
    for missing_key in ("source", "objective", "scope_include", "constraints", "requested_outputs"):
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_intent(inputs)


def test_build_intent_writes_output_path(tmp_path):
    output_path = tmp_path / "intent.json"

    artifact = build_intent(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_intent_rejects_invalid_source():
    inputs = dict(VALID_INPUTS)
    inputs["source"] = "invalid_source"
    with pytest.raises(ValueError, match="source"):
        build_intent(inputs)


def test_build_intent_rejects_empty_scope_include():
    inputs = dict(VALID_INPUTS)
    inputs["scope_include"] = []
    with pytest.raises(ValueError, match="scope_include"):
        build_intent(inputs)


def test_build_intent_rejects_invalid_urgency():
    inputs = dict(VALID_INPUTS)
    inputs["urgency"] = "extreme"
    with pytest.raises(ValueError, match="urgency"):
        build_intent(inputs)


def test_build_intent_rejects_invalid_milestone_id():
    inputs = dict(VALID_INPUTS)
    inputs["related_milestone"] = {"id": "invalid"}
    with pytest.raises(ValueError, match="milestone"):
        build_intent(inputs)


def test_build_intent_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_intent(VALID_INPUTS)
