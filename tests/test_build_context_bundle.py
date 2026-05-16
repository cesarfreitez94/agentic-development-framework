import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.context_bundle import (
    SchemaValidationError,
    build_context_bundle,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "context_bundle.schema.json"

VALID_INPUTS: dict[str, object] = {
    "packet_id": "TPACKET-12345678-001",
    "context_items": [
        {
            "type": "source_file",
            "path": "src/main.py",
            "section": "main",
            "line_ranges": [{"start": 1, "end": 50}],
            "reason": "Core logic",
        },
        {
            "type": "test_file",
            "path": "tests/test_main.py",
            "line_ranges": [{"start": 1, "end": 30}],
            "reason": "Test for core logic",
        },
        {
            "type": "schema",
            "path": "schemas/meta/intent.schema.json",
            "line_ranges": [{"start": 1, "end": 50}, {"start": 100, "end": 120}],
            "reason": "Intent contract",
        },
    ],
    "excluded_context": [
        {
            "path": "src/legacy.py",
            "reason": "Legacy code not in scope",
        },
        {
            "path": "config/secrets.env",
            "line_ranges": [{"start": 1, "end": 10}],
            "reason": "Sensitive config excluded",
        },
    ],
    "policy_refs": ["POL-001", "POL-002", "POL-003"],
    "integrity": {
        "source_count": 3,
        "truncated": False,
    },
    "human_summary": "Context bundle for M5.6 implementation.",
}


def test_build_context_bundle_schema_valid():
    artifact = build_context_bundle(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_context_bundle_is_deterministic():
    a = build_context_bundle(VALID_INPUTS)
    b = build_context_bundle(VALID_INPUTS)
    c = build_context_bundle(VALID_INPUTS)

    assert a == b == c


def test_build_context_bundle_rejects_missing_required_input():
    for missing_key in (
        "packet_id",
        "context_items",
        "excluded_context",
        "policy_refs",
        "integrity",
    ):
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_context_bundle(inputs)


def test_build_context_bundle_writes_output_path(tmp_path):
    output_path = tmp_path / "context_bundle.json"

    artifact = build_context_bundle(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_context_bundle_rejects_invalid_packet_id():
    inputs = dict(VALID_INPUTS)
    inputs["packet_id"] = "bad-format"
    with pytest.raises(ValueError, match="packet_id"):
        build_context_bundle(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["packet_id"] = ""
    with pytest.raises(ValueError, match="packet_id"):
        build_context_bundle(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["packet_id"] = 42
    with pytest.raises(ValueError, match="packet_id"):
        build_context_bundle(inputs)


def test_build_context_bundle_rejects_invalid_context_items():
    # empty list
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = []
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = "not-a-list"
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # missing required key
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "path": "src/main.py",
            "line_ranges": [{"start": 1, "end": 10}],
            "reason": "Missing type",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # invalid type enum
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "invalid_type",
            "path": "src/main.py",
            "line_ranges": [{"start": 1, "end": 10}],
            "reason": "Invalid type",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # invalid path (empty string)
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "source_file",
            "path": "",
            "line_ranges": [{"start": 1, "end": 10}],
            "reason": "Empty path",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # invalid path (non-string)
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "source_file",
            "path": 42,
            "line_ranges": [{"start": 1, "end": 10}],
            "reason": "Non-string path",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # invalid section (non-string if provided)
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "source_file",
            "path": "src/main.py",
            "section": 42,
            "line_ranges": [{"start": 1, "end": 10}],
            "reason": "Non-string section",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # invalid line_ranges (empty list)
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "source_file",
            "path": "src/main.py",
            "line_ranges": [],
            "reason": "Empty line ranges",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # invalid line_ranges (start not integer)
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "source_file",
            "path": "src/main.py",
            "line_ranges": [{"start": "1", "end": 10}],
            "reason": "start not integer",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # invalid line_ranges (start < 1)
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "source_file",
            "path": "src/main.py",
            "line_ranges": [{"start": 0, "end": 10}],
            "reason": "start < 1",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # invalid line_ranges (start > end)
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "source_file",
            "path": "src/main.py",
            "line_ranges": [{"start": 20, "end": 10}],
            "reason": "start > end",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # invalid reason (empty string)
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "source_file",
            "path": "src/main.py",
            "line_ranges": [{"start": 1, "end": 10}],
            "reason": "",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "source_file",
            "path": "src/main.py",
            "line_ranges": [{"start": 1, "end": 10}],
            "reason": "Extra keys",
            "extra_key": "not allowed",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)

    # missing line_ranges key
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "source_file",
            "path": "src/main.py",
            "reason": "Missing line_ranges",
        },
    ]
    with pytest.raises(ValueError, match="context_items"):
        build_context_bundle(inputs)


def test_build_context_bundle_rejects_duplicate_context_items():
    inputs = dict(VALID_INPUTS)
    inputs["context_items"] = [
        {
            "type": "source_file",
            "path": "src/main.py",
            "line_ranges": [{"start": 1, "end": 10}],
            "reason": "First",
        },
        {
            "type": "source_file",
            "path": "src/main.py",
            "line_ranges": [{"start": 1, "end": 10}],
            "reason": "Duplicate",
        },
    ]
    with pytest.raises(ValueError, match="Duplicate"):
        build_context_bundle(inputs)


def test_build_context_bundle_rejects_invalid_excluded_context():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["excluded_context"] = "not-a-list"
    with pytest.raises(ValueError, match="excluded_context"):
        build_context_bundle(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["excluded_context"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="excluded_context"):
        build_context_bundle(inputs)

    # missing required key (path)
    inputs = dict(VALID_INPUTS)
    inputs["excluded_context"] = [
        {
            "reason": "Missing path",
        },
    ]
    with pytest.raises(ValueError, match="excluded_context"):
        build_context_bundle(inputs)

    # missing required key (reason)
    inputs = dict(VALID_INPUTS)
    inputs["excluded_context"] = [
        {
            "path": "src/missing_reason.py",
        },
    ]
    with pytest.raises(ValueError, match="excluded_context"):
        build_context_bundle(inputs)

    # empty path
    inputs = dict(VALID_INPUTS)
    inputs["excluded_context"] = [
        {
            "path": "",
            "reason": "Empty path",
        },
    ]
    with pytest.raises(ValueError, match="excluded_context"):
        build_context_bundle(inputs)

    # empty reason
    inputs = dict(VALID_INPUTS)
    inputs["excluded_context"] = [
        {
            "path": "src/file.py",
            "reason": "",
        },
    ]
    with pytest.raises(ValueError, match="excluded_context"):
        build_context_bundle(inputs)

    # non-string section
    inputs = dict(VALID_INPUTS)
    inputs["excluded_context"] = [
        {
            "path": "src/file.py",
            "section": 42,
            "reason": "Non-string section",
        },
    ]
    with pytest.raises(ValueError, match="excluded_context"):
        build_context_bundle(inputs)

    # invalid line_ranges if provided
    inputs = dict(VALID_INPUTS)
    inputs["excluded_context"] = [
        {
            "path": "src/file.py",
            "line_ranges": [],
            "reason": "Empty line ranges",
        },
    ]
    with pytest.raises(ValueError, match="excluded_context"):
        build_context_bundle(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["excluded_context"] = [
        {
            "path": "src/file.py",
            "reason": "Extra keys",
            "extra_key": "not allowed",
        },
    ]
    with pytest.raises(ValueError, match="excluded_context"):
        build_context_bundle(inputs)


def test_build_context_bundle_rejects_invalid_policy_refs():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["policy_refs"] = "not-a-list"
    with pytest.raises(ValueError, match="policy_refs"):
        build_context_bundle(inputs)

    # empty list
    inputs = dict(VALID_INPUTS)
    inputs["policy_refs"] = []
    with pytest.raises(ValueError, match="policy_refs"):
        build_context_bundle(inputs)

    # item not a string
    inputs = dict(VALID_INPUTS)
    inputs["policy_refs"] = ["POL-001", 42]
    with pytest.raises(ValueError, match="policy_refs"):
        build_context_bundle(inputs)

    # empty string item
    inputs = dict(VALID_INPUTS)
    inputs["policy_refs"] = ["POL-001", ""]
    with pytest.raises(ValueError, match="policy_refs"):
        build_context_bundle(inputs)

    # duplicate items
    inputs = dict(VALID_INPUTS)
    inputs["policy_refs"] = ["POL-001", "POL-002", "POL-001"]
    with pytest.raises(ValueError, match="Duplicate"):
        build_context_bundle(inputs)


def test_build_context_bundle_rejects_invalid_integrity():
    # not a dict
    inputs = dict(VALID_INPUTS)
    inputs["integrity"] = "not-a-dict"
    with pytest.raises(ValueError, match="integrity"):
        build_context_bundle(inputs)

    # missing required key
    inputs = dict(VALID_INPUTS)
    inputs["integrity"] = {
        "source_count": 3,
    }
    with pytest.raises(ValueError, match="integrity"):
        build_context_bundle(inputs)

    # source_count not an integer
    inputs = dict(VALID_INPUTS)
    inputs["integrity"] = {
        "source_count": "3",
        "truncated": False,
    }
    with pytest.raises(ValueError, match="integrity"):
        build_context_bundle(inputs)

    # source_count negative
    inputs = dict(VALID_INPUTS)
    inputs["integrity"] = {
        "source_count": -1,
        "truncated": False,
    }
    with pytest.raises(ValueError, match="integrity"):
        build_context_bundle(inputs)

    # truncated not a boolean
    inputs = dict(VALID_INPUTS)
    inputs["integrity"] = {
        "source_count": 3,
        "truncated": "yes",
    }
    with pytest.raises(ValueError, match="integrity"):
        build_context_bundle(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["integrity"] = {
        "source_count": 3,
        "truncated": False,
        "extra": "not allowed",
    }
    with pytest.raises(ValueError, match="integrity"):
        build_context_bundle(inputs)


def test_build_context_bundle_rejects_source_count_mismatch():
    inputs = dict(VALID_INPUTS)
    inputs["integrity"] = {
        "source_count": 5,
        "truncated": False,
    }
    with pytest.raises(ValueError, match="source_count"):
        build_context_bundle(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["integrity"] = {
        "source_count": 0,
        "truncated": False,
    }
    with pytest.raises(ValueError, match="source_count"):
        build_context_bundle(inputs)


def test_build_context_bundle_rejects_invalid_human_summary():
    inputs = dict(VALID_INPUTS)
    inputs["human_summary"] = 42
    with pytest.raises(ValueError, match="human_summary"):
        build_context_bundle(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["human_summary"] = ""
    # empty string is technically a string, so it shouldn't be rejected by the
    # isinstance check. But the schema may allow empty strings.
    # We'll just check the non-string case.
    artifact = build_context_bundle(inputs)
    assert artifact["human_summary"] == ""


def test_build_context_bundle_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_context_bundle(VALID_INPUTS)
