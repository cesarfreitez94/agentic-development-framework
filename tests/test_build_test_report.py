import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.test_report import (
    SchemaValidationError,
    build_test_report,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "test_report.schema.json"

VALID_INPUTS: dict[str, object] = {
    "implementation_report_id": "IMPL-12345678-001",
    "status": "passed",
    "test_runs": [
        {
            "command": "pytest tests/ -v",
            "status": "passed",
            "exit_code": 0,
            "kind": "pytest",
        },
        {
            "command": "flake8 src/",
            "status": "passed",
            "exit_code": 0,
            "kind": "lint",
        },
    ],
    "failures": [],
    "coverage": {"required": True, "satisfied": True},
    "skipped_tests": ["test_future_feature", "test_not_ready"],
    "environment": {
        "runtime": "python",
        "os": "linux",
        "python_version": "3.11",
    },
    "performance": {"duration_ms": 1234, "memory_mb": 45.6},
    "human_summary": "All tests passed. Coverage satisfied.",
}


def test_build_test_report_schema_valid():
    artifact = build_test_report(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_test_report_is_deterministic():
    a = build_test_report(VALID_INPUTS)
    b = build_test_report(VALID_INPUTS)
    c = build_test_report(VALID_INPUTS)

    assert a == b == c


def test_build_test_report_rejects_missing_required_input():
    required_keys = {
        "implementation_report_id",
        "status",
        "test_runs",
        "failures",
        "coverage",
    }
    for missing_key in required_keys:
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_test_report(inputs)


def test_build_test_report_writes_output_path(tmp_path):
    output_path = tmp_path / "test_report.json"

    artifact = build_test_report(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_test_report_rejects_invalid_implementation_report_id():
    inputs = dict(VALID_INPUTS)
    inputs["implementation_report_id"] = "bad-format"
    with pytest.raises(ValueError, match="implementation_report_id"):
        build_test_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["implementation_report_id"] = ""
    with pytest.raises(ValueError, match="implementation_report_id"):
        build_test_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["implementation_report_id"] = 42
    with pytest.raises(ValueError, match="implementation_report_id"):
        build_test_report(inputs)


def test_build_test_report_rejects_invalid_status():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "unknown"
    with pytest.raises(ValueError, match="status"):
        build_test_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["status"] = ""
    with pytest.raises(ValueError, match="status"):
        build_test_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["status"] = 42
    with pytest.raises(ValueError, match="status"):
        build_test_report(inputs)


def test_build_test_report_rejects_invalid_test_runs():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["test_runs"] = "not-a-list"
    with pytest.raises(ValueError, match="test_runs"):
        build_test_report(inputs)

    # empty list
    inputs = dict(VALID_INPUTS)
    inputs["test_runs"] = []
    with pytest.raises(ValueError, match="test_runs"):
        build_test_report(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["test_runs"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="test_runs"):
        build_test_report(inputs)

    # missing required key (exit_code)
    inputs = dict(VALID_INPUTS)
    inputs["test_runs"] = [
        {"command": "pytest", "status": "passed"},
    ]
    with pytest.raises(ValueError, match="test_runs"):
        build_test_report(inputs)

    # empty command
    inputs = dict(VALID_INPUTS)
    inputs["test_runs"] = [
        {"command": "", "status": "passed", "exit_code": 0},
    ]
    with pytest.raises(ValueError, match="test_runs"):
        build_test_report(inputs)

    # invalid status enum
    inputs = dict(VALID_INPUTS)
    inputs["test_runs"] = [
        {"command": "pytest", "status": "unknown", "exit_code": 0},
    ]
    with pytest.raises(ValueError, match="test_runs"):
        build_test_report(inputs)

    # exit_code not an integer
    inputs = dict(VALID_INPUTS)
    inputs["test_runs"] = [
        {"command": "pytest", "status": "passed", "exit_code": "0"},
    ]
    with pytest.raises(ValueError, match="test_runs"):
        build_test_report(inputs)

    # negative exit_code
    inputs = dict(VALID_INPUTS)
    inputs["test_runs"] = [
        {"command": "pytest", "status": "passed", "exit_code": -1},
    ]
    with pytest.raises(ValueError, match="test_runs"):
        build_test_report(inputs)

    # invalid kind enum
    inputs = dict(VALID_INPUTS)
    inputs["test_runs"] = [
        {"command": "pytest", "status": "passed", "exit_code": 0, "kind": "unknown"},
    ]
    with pytest.raises(ValueError, match="test_runs"):
        build_test_report(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["test_runs"] = [
        {"command": "pytest", "status": "passed", "exit_code": 0, "extra": "nope"},
    ]
    with pytest.raises(ValueError, match="test_runs"):
        build_test_report(inputs)


def test_build_test_report_rejects_duplicate_test_run_commands():
    inputs = dict(VALID_INPUTS)
    inputs["test_runs"] = [
        {"command": "pytest", "status": "passed", "exit_code": 0},
        {"command": "pytest", "status": "passed", "exit_code": 0},
        {"command": "flake8", "status": "passed", "exit_code": 0},
    ]
    with pytest.raises(ValueError, match="Duplicate"):
        build_test_report(inputs)


def test_build_test_report_rejects_invalid_failures():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["failures"] = "not-a-list"
    with pytest.raises(ValueError, match="failures"):
        build_test_report(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["failures"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="failures"):
        build_test_report(inputs)

    # missing required key (message)
    inputs = dict(VALID_INPUTS)
    inputs["failures"] = [
        {"test_name": "test_foo"},
    ]
    with pytest.raises(ValueError, match="failures"):
        build_test_report(inputs)

    # empty test_name
    inputs = dict(VALID_INPUTS)
    inputs["failures"] = [
        {"test_name": "", "message": "A failure message"},
    ]
    with pytest.raises(ValueError, match="failures"):
        build_test_report(inputs)

    # empty message
    inputs = dict(VALID_INPUTS)
    inputs["failures"] = [
        {"test_name": "test_foo", "message": ""},
    ]
    with pytest.raises(ValueError, match="failures"):
        build_test_report(inputs)

    # non-string path if provided
    inputs = dict(VALID_INPUTS)
    inputs["failures"] = [
        {"test_name": "test_foo", "message": "fail", "path": 42},
    ]
    with pytest.raises(ValueError, match="failures"):
        build_test_report(inputs)

    # line not an integer
    inputs = dict(VALID_INPUTS)
    inputs["failures"] = [
        {"test_name": "test_foo", "message": "fail", "line": "5"},
    ]
    with pytest.raises(ValueError, match="failures"):
        build_test_report(inputs)

    # line less than 1
    inputs = dict(VALID_INPUTS)
    inputs["failures"] = [
        {"test_name": "test_foo", "message": "fail", "line": 0},
    ]
    with pytest.raises(ValueError, match="failures"):
        build_test_report(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["failures"] = [
        {"test_name": "test_foo", "message": "fail", "extra": "nope"},
    ]
    with pytest.raises(ValueError, match="failures"):
        build_test_report(inputs)


def test_build_test_report_rejects_duplicate_failures():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "failed"
    inputs["test_runs"] = [
        {"command": "pytest", "status": "failed", "exit_code": 1},
    ]
    inputs["failures"] = [
        {"test_name": "test_foo", "message": "Assertion failed: expected True"},
        {"test_name": "test_foo", "message": "Assertion failed: expected True"},
        {"test_name": "test_bar", "message": "Timeout"},
    ]
    with pytest.raises(ValueError, match="Duplicate"):
        build_test_report(inputs)


def test_build_test_report_rejects_invalid_coverage():
    # not a dict
    inputs = dict(VALID_INPUTS)
    inputs["coverage"] = "not-a-dict"
    with pytest.raises(ValueError, match="coverage"):
        build_test_report(inputs)

    # missing required key (satisfied)
    inputs = dict(VALID_INPUTS)
    inputs["coverage"] = {"required": True}
    with pytest.raises(ValueError, match="coverage"):
        build_test_report(inputs)

    # required not boolean
    inputs = dict(VALID_INPUTS)
    inputs["coverage"] = {"required": "yes", "satisfied": True}
    with pytest.raises(ValueError, match="coverage"):
        build_test_report(inputs)

    # satisfied not boolean
    inputs = dict(VALID_INPUTS)
    inputs["coverage"] = {"required": True, "satisfied": "yes"}
    with pytest.raises(ValueError, match="coverage"):
        build_test_report(inputs)

    # details not string
    inputs = dict(VALID_INPUTS)
    inputs["coverage"] = {"required": True, "satisfied": False, "details": 42}
    with pytest.raises(ValueError, match="coverage"):
        build_test_report(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["coverage"] = {"required": True, "satisfied": True, "extra": "nope"}
    with pytest.raises(ValueError, match="coverage"):
        build_test_report(inputs)


def test_build_test_report_rejects_failed_without_failures():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "failed"
    inputs["test_runs"] = [
        {"command": "pytest", "status": "failed", "exit_code": 1},
    ]
    inputs["failures"] = []
    # Schema requires minItems 1 when status is failed, so it fails schema validation
    with pytest.raises(SchemaValidationError, match="non-empty"):
        build_test_report(inputs)


def test_build_test_report_rejects_not_run_without_reason():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "not_run"
    inputs["test_runs"] = [
        {"command": "pytest", "status": "skipped", "exit_code": 0},
    ]
    inputs.pop("not_run_reason", None)
    # Schema requires not_run_reason when status is not_run, so it fails schema validation
    with pytest.raises(SchemaValidationError, match="not_run_reason"):
        build_test_report(inputs)


def test_build_test_report_rejects_passed_with_failures():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "passed"
    inputs["test_runs"] = [
        {"command": "pytest", "status": "passed", "exit_code": 0},
    ]
    inputs["failures"] = [
        {"test_name": "test_foo", "message": "Should have failed"},
    ]
    with pytest.raises(ValueError, match="passed"):
        build_test_report(inputs)


def test_build_test_report_rejects_status_inconsistent_with_test_runs():
    # status passed but a test_run is failed
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "passed"
    inputs["test_runs"] = [
        {"command": "pytest", "status": "passed", "exit_code": 0},
        {"command": "flake8", "status": "failed", "exit_code": 2},
    ]
    with pytest.raises(ValueError, match="passed"):
        build_test_report(inputs)

    # status failed but no test_run has status failed
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "failed"
    inputs["failures"] = [
        {"test_name": "test_foo", "message": "Failed"},
    ]
    inputs["test_runs"] = [
        {"command": "pytest", "status": "passed", "exit_code": 0},
    ]
    with pytest.raises(ValueError, match="failed"):
        build_test_report(inputs)

    # status not_run but a test_run is not skipped
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "not_run"
    inputs["not_run_reason"] = "Infrastructure unavailable"
    inputs["failures"] = []
    inputs["test_runs"] = [
        {"command": "pytest", "status": "skipped", "exit_code": 0},
        {"command": "flake8", "status": "passed", "exit_code": 0},
    ]
    with pytest.raises(ValueError, match="not_run"):
        build_test_report(inputs)


def test_build_test_report_rejects_invalid_skipped_tests():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["skipped_tests"] = "not-a-list"
    with pytest.raises(ValueError, match="skipped_tests"):
        build_test_report(inputs)

    # non-string item
    inputs = dict(VALID_INPUTS)
    inputs["skipped_tests"] = [42]
    with pytest.raises(ValueError, match="skipped_tests"):
        build_test_report(inputs)

    # empty string item
    inputs = dict(VALID_INPUTS)
    inputs["skipped_tests"] = [""]
    with pytest.raises(ValueError, match="skipped_tests"):
        build_test_report(inputs)

    # duplicate values
    inputs = dict(VALID_INPUTS)
    inputs["skipped_tests"] = ["test_a", "test_a"]
    with pytest.raises(ValueError, match="Duplicate"):
        build_test_report(inputs)


def test_build_test_report_rejects_invalid_environment():
    # not a dict
    inputs = dict(VALID_INPUTS)
    inputs["environment"] = "not-a-dict"
    with pytest.raises(ValueError, match="environment"):
        build_test_report(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["environment"] = {"runtime": "python", "extra": "nope"}
    with pytest.raises(ValueError, match="environment"):
        build_test_report(inputs)

    # non-string value
    inputs = dict(VALID_INPUTS)
    inputs["environment"] = {"runtime": 42}
    with pytest.raises(ValueError, match="environment"):
        build_test_report(inputs)


def test_build_test_report_rejects_invalid_performance():
    # not a dict
    inputs = dict(VALID_INPUTS)
    inputs["performance"] = "not-a-dict"
    with pytest.raises(ValueError, match="performance"):
        build_test_report(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["performance"] = {"duration_ms": 100, "extra": "nope"}
    with pytest.raises(ValueError, match="performance"):
        build_test_report(inputs)

    # duration_ms not integer
    inputs = dict(VALID_INPUTS)
    inputs["performance"] = {"duration_ms": "fast"}
    with pytest.raises(ValueError, match="performance"):
        build_test_report(inputs)

    # duration_ms negative
    inputs = dict(VALID_INPUTS)
    inputs["performance"] = {"duration_ms": -1}
    with pytest.raises(ValueError, match="performance"):
        build_test_report(inputs)

    # memory_mb negative
    inputs = dict(VALID_INPUTS)
    inputs["performance"] = {"memory_mb": -1.5}
    with pytest.raises(ValueError, match="performance"):
        build_test_report(inputs)


def test_build_test_report_rejects_invalid_human_summary():
    inputs = dict(VALID_INPUTS)
    inputs["human_summary"] = 42
    with pytest.raises(ValueError, match="human_summary"):
        build_test_report(inputs)


def test_build_test_report_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_test_report(VALID_INPUTS)
