import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.review_report import (
    SchemaValidationError,
    build_review_report,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "review_report.schema.json"

VALID_INPUTS: dict[str, object] = {
    "implementation_report_id": "IMPL-12345678-001",
    "test_report_id": "TEST-12345678-001",
    "status": "approved",
    "findings": [
        {
            "severity": "low",
            "location": {"path": "src/builders/review_report.py", "line_start": 42},
            "message": "Minor style inconsistency in docstring formatting.",
            "recommendation": "Standardize docstring format.",
        },
        {
            "severity": "low",
            "location": {"path": "tests/test_build_review_report.py", "line_start": 10, "line_end": 15},
            "message": "Test could use additional edge case coverage.",
        },
    ],
    "policy_compliance": [
        {"policy_ref": "POL-GOV-001", "status": "passed", "details": "All governance checks pass."},
        {"policy_ref": "POL-SEC-001", "status": "passed"},
        {"policy_ref": "POL-ARCH-001", "status": "not_applicable", "details": "No architecture changes."},
    ],
    "recommendation": "proceed_to_git",
    "residual_risks": [],
    "approved_with_notes": "All checks passed. Ready for git.",
    "human_summary": "Review report: approved with no issues.",
}

VALID_INPUTS_APPROVED_WITH_RISKS: dict[str, object] = {
    "implementation_report_id": "IMPL-87654321-001",
    "test_report_id": "TEST-87654321-001",
    "status": "approved_with_risks",
    "findings": [
        {
            "severity": "medium",
            "location": {"path": "src/module.py", "line_start": 100},
            "message": "Performance concern with large inputs.",
            "recommendation": "Add input size validation.",
        },
    ],
    "policy_compliance": [
        {"policy_ref": "POL-GOV-001", "status": "passed"},
        {"policy_ref": "POL-PERF-001", "status": "failed", "details": "Performance benchmark not met."},
    ],
    "recommendation": "ask_user",
    "residual_risks": ["Performance regression under high load", "Missing input validation"],
    "human_summary": "Approved with noted risks.",
}

VALID_INPUTS_CHANGES_REQUESTED: dict[str, object] = {
    "implementation_report_id": "IMPL-11112222-001",
    "test_report_id": "TEST-11112222-001",
    "status": "changes_requested",
    "findings": [
        {
            "severity": "high",
            "location": {"path": "src/core.py", "line_start": 200, "line_end": 200},
            "message": "Missing error handling for edge case.",
            "recommendation": "Add try/except block.",
        },
    ],
    "policy_compliance": [
        {"policy_ref": "POL-GOV-001", "status": "failed", "details": "Missing required test coverage."},
    ],
    "recommendation": "fix_required",
    "required_fixes": ["Add error handling in src/core.py:200", "Increase test coverage"],
    "human_summary": "Changes requested: fix error handling and test coverage.",
}

VALID_INPUTS_BLOCKED: dict[str, object] = {
    "implementation_report_id": "IMPL-99999999-001",
    "test_report_id": "TEST-99999999-001",
    "status": "blocked",
    "findings": [
        {
            "severity": "critical",
            "location": {"path": "src/database.py", "line_start": 50},
            "message": "Data loss risk in migration script.",
        },
    ],
    "policy_compliance": [
        {"policy_ref": "POL-GOV-001", "status": "passed"},
        {"policy_ref": "POL-DATA-001", "status": "failed", "details": "Data integrity check failed."},
    ],
    "recommendation": "stop",
    "human_summary": "Blocked: data integrity issue.",
}


def test_build_review_report_schema_valid():
    artifact = build_review_report(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_review_report_is_deterministic():
    a = build_review_report(VALID_INPUTS)
    b = build_review_report(VALID_INPUTS)
    c = build_review_report(VALID_INPUTS)

    assert a == b == c


def test_build_review_report_rejects_missing_required_input():
    required_keys = {
        "implementation_report_id",
        "test_report_id",
        "status",
        "findings",
        "policy_compliance",
        "recommendation",
    }
    for missing_key in required_keys:
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_review_report(inputs)


def test_build_review_report_writes_output_path(tmp_path):
    output_path = tmp_path / "review_report.json"

    artifact = build_review_report(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_review_report_rejects_invalid_implementation_report_id():
    inputs = dict(VALID_INPUTS)
    inputs["implementation_report_id"] = "bad-format"
    with pytest.raises(ValueError, match="implementation_report_id"):
        build_review_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["implementation_report_id"] = ""
    with pytest.raises(ValueError, match="implementation_report_id"):
        build_review_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["implementation_report_id"] = 42
    with pytest.raises(ValueError, match="implementation_report_id"):
        build_review_report(inputs)


def test_build_review_report_rejects_invalid_test_report_id():
    inputs = dict(VALID_INPUTS)
    inputs["test_report_id"] = "bad-format"
    with pytest.raises(ValueError, match="test_report_id"):
        build_review_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["test_report_id"] = ""
    with pytest.raises(ValueError, match="test_report_id"):
        build_review_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["test_report_id"] = 42
    with pytest.raises(ValueError, match="test_report_id"):
        build_review_report(inputs)


def test_build_review_report_rejects_invalid_status():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "unknown"
    with pytest.raises(ValueError, match="status"):
        build_review_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["status"] = ""
    with pytest.raises(ValueError, match="status"):
        build_review_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["status"] = 42
    with pytest.raises(ValueError, match="status"):
        build_review_report(inputs)


def test_build_review_report_rejects_invalid_findings():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = "not-a-list"
    with pytest.raises(ValueError, match="findings"):
        build_review_report(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="findings"):
        build_review_report(inputs)

    # missing required key (message)
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {"path": "src/file.py"}},
    ]
    with pytest.raises(ValueError, match="findings"):
        build_review_report(inputs)

    # missing location key (path)
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {}, "message": "A message"},
    ]
    with pytest.raises(ValueError, match="findings"):
        build_review_report(inputs)

    # invalid severity enum
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "unknown", "location": {"path": "src/file.py"}, "message": "A message"},
    ]
    with pytest.raises(ValueError, match="findings"):
        build_review_report(inputs)

    # empty path
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {"path": ""}, "message": "A message"},
    ]
    with pytest.raises(ValueError, match="findings"):
        build_review_report(inputs)

    # empty message
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {"path": "src/file.py"}, "message": ""},
    ]
    with pytest.raises(ValueError, match="findings"):
        build_review_report(inputs)

    # line_start not integer
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {"path": "src/file.py", "line_start": "5"}, "message": "A message"},
    ]
    with pytest.raises(ValueError, match="line_start"):
        build_review_report(inputs)

    # line_start < 1
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {"path": "src/file.py", "line_start": 0}, "message": "A message"},
    ]
    with pytest.raises(ValueError, match="line_start"):
        build_review_report(inputs)

    # line_end not integer
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {"path": "src/file.py", "line_start": 1, "line_end": "5"}, "message": "A message"},
    ]
    with pytest.raises(ValueError, match="line_end"):
        build_review_report(inputs)

    # line_end < 1
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {"path": "src/file.py", "line_start": 1, "line_end": 0}, "message": "A message"},
    ]
    with pytest.raises(ValueError, match="line_end"):
        build_review_report(inputs)

    # line_start > line_end
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {"path": "src/file.py", "line_start": 10, "line_end": 5}, "message": "A message"},
    ]
    with pytest.raises(ValueError, match="line_start"):
        build_review_report(inputs)

    # location extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {"path": "src/file.py", "extra": "nope"}, "message": "A message"},
    ]
    with pytest.raises(ValueError, match="findings"):
        build_review_report(inputs)

    # finding extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {"path": "src/file.py"}, "message": "A message", "extra": "nope"},
    ]
    with pytest.raises(ValueError, match="findings"):
        build_review_report(inputs)

    # recommendation not a string
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {"severity": "low", "location": {"path": "src/file.py"}, "message": "A message", "recommendation": 42},
    ]
    with pytest.raises(ValueError, match="findings"):
        build_review_report(inputs)


def test_build_review_report_rejects_duplicate_findings():
    inputs = dict(VALID_INPUTS)
    inputs["findings"] = [
        {
            "severity": "low",
            "location": {"path": "src/file.py"},
            "message": "Duplicate finding",
        },
        {
            "severity": "low",
            "location": {"path": "src/file.py"},
            "message": "Duplicate finding",
        },
    ]
    with pytest.raises(ValueError, match="Duplicate"):
        build_review_report(inputs)


def test_build_review_report_rejects_invalid_policy_compliance():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["policy_compliance"] = "not-a-list"
    with pytest.raises(ValueError, match="policy_compliance"):
        build_review_report(inputs)

    # empty list
    inputs = dict(VALID_INPUTS)
    inputs["policy_compliance"] = []
    with pytest.raises(ValueError, match="policy_compliance"):
        build_review_report(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["policy_compliance"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="policy_compliance"):
        build_review_report(inputs)

    # missing required key (status)
    inputs = dict(VALID_INPUTS)
    inputs["policy_compliance"] = [
        {"policy_ref": "POL-001"},
    ]
    with pytest.raises(ValueError, match="policy_compliance"):
        build_review_report(inputs)

    # empty policy_ref
    inputs = dict(VALID_INPUTS)
    inputs["policy_compliance"] = [
        {"policy_ref": "", "status": "passed"},
    ]
    with pytest.raises(ValueError, match="policy_compliance"):
        build_review_report(inputs)

    # invalid status enum
    inputs = dict(VALID_INPUTS)
    inputs["policy_compliance"] = [
        {"policy_ref": "POL-001", "status": "unknown"},
    ]
    with pytest.raises(ValueError, match="policy_compliance"):
        build_review_report(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["policy_compliance"] = [
        {"policy_ref": "POL-001", "status": "passed", "extra": "nope"},
    ]
    with pytest.raises(ValueError, match="policy_compliance"):
        build_review_report(inputs)

    # details not a string
    inputs = dict(VALID_INPUTS)
    inputs["policy_compliance"] = [
        {"policy_ref": "POL-001", "status": "passed", "details": 42},
    ]
    with pytest.raises(ValueError, match="policy_compliance"):
        build_review_report(inputs)


def test_build_review_report_rejects_duplicate_policy_refs():
    inputs = dict(VALID_INPUTS)
    inputs["policy_compliance"] = [
        {"policy_ref": "POL-001", "status": "passed"},
        {"policy_ref": "POL-001", "status": "passed"},
        {"policy_ref": "POL-002", "status": "passed"},
    ]
    with pytest.raises(ValueError, match="Duplicate policy_ref"):
        build_review_report(inputs)


def test_build_review_report_rejects_invalid_recommendation():
    inputs = dict(VALID_INPUTS)
    inputs["recommendation"] = "unknown"
    with pytest.raises(ValueError, match="recommendation"):
        build_review_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["recommendation"] = ""
    with pytest.raises(ValueError, match="recommendation"):
        build_review_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["recommendation"] = 42
    with pytest.raises(ValueError, match="recommendation"):
        build_review_report(inputs)


def test_build_review_report_rejects_changes_requested_without_required_fixes():
    inputs = dict(VALID_INPUTS_CHANGES_REQUESTED)
    inputs.pop("required_fixes", None)
    with pytest.raises(SchemaValidationError, match="required_fixes"):
        build_review_report(inputs)

    # Fix: make required_fixes empty - also should fail
    inputs = dict(VALID_INPUTS_CHANGES_REQUESTED)
    inputs["required_fixes"] = []
    with pytest.raises(SchemaValidationError, match="non-empty"):
        build_review_report(inputs)


def test_build_review_report_rejects_status_recommendation_mismatch():
    # approved must have proceed_to_git
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "approved"
    inputs["recommendation"] = "fix_required"
    with pytest.raises(ValueError, match="approved"):
        build_review_report(inputs)

    # blocked must have stop
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "blocked"
    inputs["recommendation"] = "proceed_to_git"
    with pytest.raises(ValueError, match="blocked"):
        build_review_report(inputs)

    # changes_requested must have fix_required or ask_user
    inputs = dict(VALID_INPUTS_CHANGES_REQUESTED)
    inputs["recommendation"] = "proceed_to_git"
    with pytest.raises(ValueError, match="changes_requested"):
        build_review_report(inputs)

    inputs = dict(VALID_INPUTS_CHANGES_REQUESTED)
    inputs["recommendation"] = "stop"
    with pytest.raises(ValueError, match="changes_requested"):
        build_review_report(inputs)


def test_build_review_report_rejects_approved_with_high_or_critical_findings():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "approved"
    inputs["recommendation"] = "proceed_to_git"
    inputs["findings"] = [
        {
            "severity": "high",
            "location": {"path": "src/file.py"},
            "message": "A high-severity finding in approved report",
        },
    ]
    with pytest.raises(ValueError, match="approved"):
        build_review_report(inputs)

    inputs["findings"] = [
        {
            "severity": "critical",
            "location": {"path": "src/file.py"},
            "message": "A critical finding in approved report",
        },
    ]
    with pytest.raises(ValueError, match="approved"):
        build_review_report(inputs)


def test_build_review_report_rejects_approved_with_failed_policy():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "approved"
    inputs["recommendation"] = "proceed_to_git"
    inputs["policy_compliance"] = [
        {"policy_ref": "POL-001", "status": "failed", "details": "Policy check failed."},
    ]
    with pytest.raises(ValueError, match="approved"):
        build_review_report(inputs)


def test_build_review_report_rejects_approved_with_risks_without_residual_risks():
    inputs = dict(VALID_INPUTS_APPROVED_WITH_RISKS)
    inputs.pop("residual_risks", None)
    with pytest.raises(ValueError, match="approved_with_risks"):
        build_review_report(inputs)

    inputs = dict(VALID_INPUTS_APPROVED_WITH_RISKS)
    inputs["residual_risks"] = []
    with pytest.raises(ValueError, match="approved_with_risks"):
        build_review_report(inputs)


def test_build_review_report_rejects_invalid_optional_collections():
    # residual_risks not a list
    inputs = dict(VALID_INPUTS)
    inputs["residual_risks"] = "not-a-list"
    with pytest.raises(ValueError, match="residual_risks"):
        build_review_report(inputs)

    # residual_risks with non-string item
    inputs = dict(VALID_INPUTS)
    inputs["residual_risks"] = [42]
    with pytest.raises(ValueError, match="residual_risks"):
        build_review_report(inputs)

    # residual_risks with empty string
    inputs = dict(VALID_INPUTS)
    inputs["residual_risks"] = [""]
    with pytest.raises(ValueError, match="residual_risks"):
        build_review_report(inputs)

    # required_fixes not a list
    inputs = dict(VALID_INPUTS)
    inputs["required_fixes"] = "not-a-list"
    with pytest.raises(ValueError, match="required_fixes"):
        build_review_report(inputs)

    # required_fixes with non-string item
    inputs = dict(VALID_INPUTS)
    inputs["required_fixes"] = [42]
    with pytest.raises(ValueError, match="required_fixes"):
        build_review_report(inputs)

    # required_fixes with empty string
    inputs = dict(VALID_INPUTS)
    inputs["required_fixes"] = [""]
    with pytest.raises(ValueError, match="required_fixes"):
        build_review_report(inputs)

    # approved_with_notes not a string
    inputs = dict(VALID_INPUTS)
    inputs["approved_with_notes"] = 42
    with pytest.raises(ValueError, match="approved_with_notes"):
        build_review_report(inputs)

    # human_summary not a string
    inputs = dict(VALID_INPUTS)
    inputs["human_summary"] = 42
    with pytest.raises(ValueError, match="human_summary"):
        build_review_report(inputs)


def test_build_review_report_rejects_duplicate_optional_values():
    # duplicate residual_risks
    inputs = dict(VALID_INPUTS)
    inputs["residual_risks"] = ["risk_a", "risk_a"]
    with pytest.raises(ValueError, match="Duplicate"):
        build_review_report(inputs)

    # duplicate required_fixes
    inputs = dict(VALID_INPUTS)
    inputs["required_fixes"] = ["fix_a", "fix_a"]
    with pytest.raises(ValueError, match="Duplicate"):
        build_review_report(inputs)


def test_build_review_report_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_review_report(VALID_INPUTS)
