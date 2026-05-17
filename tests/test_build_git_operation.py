import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.git_operation import (
    SchemaValidationError,
    build_git_operation,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "git_operation.schema.json"

VALID_INPUTS: dict[str, object] = {
    "produced_by": "orchestrator",
    "executed_by": "git_operator",
    "operation_type": "create_branch",
    "status": "requested",
    "source_refs": {
        "review_report_id": "REV-12345678-001",
    },
    "branch": {
        "current": "feature/test-branch",
        "base": "main",
    },
    "policy_checks": [
        {"policy_ref": "POL-GOV-001", "status": "passed"},
        {"policy_ref": "POL-SEC-001", "status": "not_applicable"},
    ],
}

VALID_INPUTS_EXECUTED: dict[str, object] = {
    "produced_by": "review_gate",
    "executed_by": "git_operator",
    "operation_type": "push",
    "status": "executed",
    "source_refs": {
        "review_report_id": "REV-12345678-001",
        "implementation_report_id": "IMPL-12345678-001",
        "test_report_id": "TEST-12345678-001",
    },
    "branch": {
        "current": "feature/test-branch",
        "base": "main",
        "target": "main",
    },
    "policy_checks": [
        {"policy_ref": "POL-GOV-001", "status": "passed"},
    ],
    "commit": {
        "sha": "abc123def456",
        "message": "Implement feature X",
        "issue_ref": "ISSUE-42",
    },
    "remote": "origin",
    "result": {
        "summary": "Push successful",
        "exit_code": 0,
    },
    "execution_notes": "Executed without issues.",
    "human_summary": "Git push operation completed successfully.",
}

VALID_INPUTS_FAILED: dict[str, object] = {
    "produced_by": "orchestrator",
    "executed_by": "git_operator",
    "operation_type": "commit",
    "status": "failed",
    "source_refs": {
        "review_report_id": "REV-12345678-001",
    },
    "branch": {
        "current": "feature/test-branch",
        "base": "main",
    },
    "policy_checks": [
        {"policy_ref": "POL-GOV-001", "status": "failed", "details": "Pre-commit hooks failed."},
    ],
    "commit": {
        "sha": "def789abc123",
        "message": "Fix bug in module",
    },
    "result": {
        "summary": "Commit failed due to policy check failure",
        "exit_code": 1,
        "details": "Pre-commit hooks detected formatting issues.",
    },
    "human_summary": "Git commit failed.",
}

VALID_INPUTS_CANCELLED: dict[str, object] = {
    "produced_by": "review_gate",
    "executed_by": "git_operator",
    "operation_type": "status_check",
    "status": "cancelled",
    "source_refs": {
        "review_report_id": "REV-12345678-001",
    },
    "branch": {
        "current": "feature/test-branch",
        "base": "main",
    },
    "policy_checks": [
        {"policy_ref": "POL-GOV-001", "status": "passed"},
    ],
    "result": {
        "summary": "Operation cancelled by user",
    },
}

VALID_INPUTS_MERGE_PR: dict[str, object] = {
    "produced_by": "orchestrator",
    "executed_by": "git_operator",
    "operation_type": "merge_pr",
    "status": "executed",
    "source_refs": {
        "review_report_id": "REV-12345678-001",
    },
    "branch": {
        "current": "feature/test-branch",
        "base": "main",
        "target": "main",
    },
    "policy_checks": [
        {"policy_ref": "POL-GOV-001", "status": "passed"},
    ],
    "pull_request": {
        "number": 42,
        "url": "https://github.com/example/repo/pull/42",
        "title": "Merge feature X",
    },
    "requires_user_confirmation": True,
    "result": {
        "summary": "PR merged successfully",
        "exit_code": 0,
    },
    "human_summary": "Merge PR completed.",
}


def test_build_git_operation_schema_valid():
    artifact = build_git_operation(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_git_operation_is_deterministic():
    a = build_git_operation(VALID_INPUTS)
    b = build_git_operation(VALID_INPUTS)
    c = build_git_operation(VALID_INPUTS)

    assert a == b == c


def test_build_git_operation_rejects_missing_required_input():
    required_keys = {
        "produced_by",
        "executed_by",
        "operation_type",
        "status",
        "source_refs",
        "branch",
        "policy_checks",
    }
    for missing_key in required_keys:
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_git_operation(inputs)


def test_build_git_operation_writes_output_path(tmp_path):
    output_path = tmp_path / "git_operation.json"

    artifact = build_git_operation(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_git_operation_rejects_invalid_produced_by():
    inputs = dict(VALID_INPUTS)
    inputs["produced_by"] = "unknown"
    with pytest.raises(ValueError, match="produced_by"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["produced_by"] = ""
    with pytest.raises(ValueError, match="produced_by"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["produced_by"] = 42
    with pytest.raises(ValueError, match="produced_by"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_invalid_executed_by():
    inputs = dict(VALID_INPUTS)
    inputs["executed_by"] = "orchestrator"
    with pytest.raises(ValueError, match="executed_by"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["executed_by"] = ""
    with pytest.raises(ValueError, match="executed_by"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["executed_by"] = 42
    with pytest.raises(ValueError, match="executed_by"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_invalid_operation_type():
    inputs = dict(VALID_INPUTS)
    inputs["operation_type"] = "unknown"
    with pytest.raises(ValueError, match="operation_type"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["operation_type"] = ""
    with pytest.raises(ValueError, match="operation_type"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["operation_type"] = 42
    with pytest.raises(ValueError, match="operation_type"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_invalid_status():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "unknown"
    with pytest.raises(ValueError, match="status"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["status"] = ""
    with pytest.raises(ValueError, match="status"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["status"] = 42
    with pytest.raises(ValueError, match="status"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_invalid_source_refs():
    # not a dict
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = "not-a-dict"
    with pytest.raises(ValueError, match="source_refs"):
        build_git_operation(inputs)

    # missing review_report_id
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = {"implementation_report_id": "IMPL-12345678-001"}
    with pytest.raises(ValueError, match="review_report_id"):
        build_git_operation(inputs)

    # invalid review_report_id pattern
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = {"review_report_id": "bad-format"}
    with pytest.raises(ValueError, match="review_report_id"):
        build_git_operation(inputs)

    # empty review_report_id
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = {"review_report_id": ""}
    with pytest.raises(ValueError, match="review_report_id"):
        build_git_operation(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = {
        "review_report_id": "REV-12345678-001",
        "extra_key": "nope",
    }
    with pytest.raises(ValueError, match="source_refs"):
        build_git_operation(inputs)

    # invalid optional ref patterns
    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = {
        "review_report_id": "REV-12345678-001",
        "implementation_report_id": "bad",
    }
    with pytest.raises(ValueError, match="implementation_report_id"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = {
        "review_report_id": "REV-12345678-001",
        "test_report_id": "bad",
    }
    with pytest.raises(ValueError, match="test_report_id"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = {
        "review_report_id": "REV-12345678-001",
        "decision_id": "bad",
    }
    with pytest.raises(ValueError, match="decision_id"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = {
        "review_report_id": "REV-12345678-001",
        "plan_id": "bad",
    }
    with pytest.raises(ValueError, match="plan_id"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["source_refs"] = {
        "review_report_id": "REV-12345678-001",
        "task_packet_id": "bad",
    }
    with pytest.raises(ValueError, match="task_packet_id"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_invalid_branch():
    # not a dict
    inputs = dict(VALID_INPUTS)
    inputs["branch"] = "not-a-dict"
    with pytest.raises(ValueError, match="branch"):
        build_git_operation(inputs)

    # missing current
    inputs = dict(VALID_INPUTS)
    inputs["branch"] = {"base": "main"}
    with pytest.raises(ValueError, match="current"):
        build_git_operation(inputs)

    # missing base
    inputs = dict(VALID_INPUTS)
    inputs["branch"] = {"current": "feature/x"}
    with pytest.raises(ValueError, match="base"):
        build_git_operation(inputs)

    # empty current
    inputs = dict(VALID_INPUTS)
    inputs["branch"] = {"current": "", "base": "main"}
    with pytest.raises(ValueError, match="branch.current"):
        build_git_operation(inputs)

    # empty base
    inputs = dict(VALID_INPUTS)
    inputs["branch"] = {"current": "feature/x", "base": ""}
    with pytest.raises(ValueError, match="branch.base"):
        build_git_operation(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["branch"] = {"current": "feature/x", "base": "main", "extra": "nope"}
    with pytest.raises(ValueError, match="branch"):
        build_git_operation(inputs)

    # empty target if provided
    inputs = dict(VALID_INPUTS)
    inputs["branch"] = {"current": "feature/x", "base": "main", "target": ""}
    with pytest.raises(ValueError, match="branch.target"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_invalid_policy_checks():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["policy_checks"] = "not-a-list"
    with pytest.raises(ValueError, match="policy_checks"):
        build_git_operation(inputs)

    # empty list
    inputs = dict(VALID_INPUTS)
    inputs["policy_checks"] = []
    with pytest.raises(ValueError, match="policy_checks"):
        build_git_operation(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["policy_checks"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="policy_checks"):
        build_git_operation(inputs)

    # missing required key (status)
    inputs = dict(VALID_INPUTS)
    inputs["policy_checks"] = [{"policy_ref": "POL-001"}]
    with pytest.raises(ValueError, match="policy_checks"):
        build_git_operation(inputs)

    # missing required key (policy_ref)
    inputs = dict(VALID_INPUTS)
    inputs["policy_checks"] = [{"status": "passed"}]
    with pytest.raises(ValueError, match="policy_checks"):
        build_git_operation(inputs)

    # empty policy_ref
    inputs = dict(VALID_INPUTS)
    inputs["policy_checks"] = [{"policy_ref": "", "status": "passed"}]
    with pytest.raises(ValueError, match="policy_checks"):
        build_git_operation(inputs)

    # invalid status enum
    inputs = dict(VALID_INPUTS)
    inputs["policy_checks"] = [{"policy_ref": "POL-001", "status": "unknown"}]
    with pytest.raises(ValueError, match="policy_checks"):
        build_git_operation(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["policy_checks"] = [
        {"policy_ref": "POL-001", "status": "passed", "extra": "nope"}
    ]
    with pytest.raises(ValueError, match="policy_checks"):
        build_git_operation(inputs)

    # details not a string
    inputs = dict(VALID_INPUTS)
    inputs["policy_checks"] = [
        {"policy_ref": "POL-001", "status": "passed", "details": 42}
    ]
    with pytest.raises(ValueError, match="policy_checks"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_duplicate_policy_refs():
    inputs = dict(VALID_INPUTS)
    inputs["policy_checks"] = [
        {"policy_ref": "POL-001", "status": "passed"},
        {"policy_ref": "POL-001", "status": "passed"},
        {"policy_ref": "POL-002", "status": "passed"},
    ]
    with pytest.raises(ValueError, match="Duplicate policy_ref"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_invalid_commit():
    # not a dict
    inputs = dict(VALID_INPUTS)
    inputs["commit"] = "not-a-dict"
    with pytest.raises(ValueError, match="commit"):
        build_git_operation(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["commit"] = {"extra": "nope"}
    with pytest.raises(ValueError, match="commit"):
        build_git_operation(inputs)

    # sha not a non-empty string
    inputs = dict(VALID_INPUTS)
    inputs["commit"] = {"sha": ""}
    with pytest.raises(ValueError, match="commit.sha"):
        build_git_operation(inputs)

    # message not a non-empty string
    inputs = dict(VALID_INPUTS)
    inputs["commit"] = {"message": ""}
    with pytest.raises(ValueError, match="commit.message"):
        build_git_operation(inputs)

    # issue_ref not a non-empty string
    inputs = dict(VALID_INPUTS)
    inputs["commit"] = {"issue_ref": ""}
    with pytest.raises(ValueError, match="commit.issue_ref"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_invalid_pull_request():
    # not a dict
    inputs = dict(VALID_INPUTS)
    inputs["pull_request"] = "not-a-dict"
    with pytest.raises(ValueError, match="pull_request"):
        build_git_operation(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["pull_request"] = {"extra": "nope"}
    with pytest.raises(ValueError, match="pull_request"):
        build_git_operation(inputs)

    # number not integer >= 1
    inputs = dict(VALID_INPUTS)
    inputs["pull_request"] = {"number": 0}
    with pytest.raises(ValueError, match="pull_request.number"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["pull_request"] = {"number": "not-an-int"}
    with pytest.raises(ValueError, match="pull_request.number"):
        build_git_operation(inputs)

    # url not non-empty string
    inputs = dict(VALID_INPUTS)
    inputs["pull_request"] = {"url": ""}
    with pytest.raises(ValueError, match="pull_request.url"):
        build_git_operation(inputs)

    # title not non-empty string
    inputs = dict(VALID_INPUTS)
    inputs["pull_request"] = {"title": ""}
    with pytest.raises(ValueError, match="pull_request.title"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_invalid_result():
    # not a dict
    inputs = dict(VALID_INPUTS)
    inputs["result"] = "not-a-dict"
    with pytest.raises(ValueError, match="result"):
        build_git_operation(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["result"] = {"extra": "nope"}
    with pytest.raises(ValueError, match="result"):
        build_git_operation(inputs)

    # summary not a string
    inputs = dict(VALID_INPUTS)
    inputs["result"] = {"summary": 42}
    with pytest.raises(ValueError, match="result.summary"):
        build_git_operation(inputs)

    # exit_code not an integer
    inputs = dict(VALID_INPUTS)
    inputs["result"] = {"exit_code": "not-an-int"}
    with pytest.raises(ValueError, match="result.exit_code"):
        build_git_operation(inputs)

    # details not a string
    inputs = dict(VALID_INPUTS)
    inputs["result"] = {"details": 42}
    with pytest.raises(ValueError, match="result.details"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_status_result_mismatch():
    # status requested with result
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "requested"
    inputs["result"] = {"summary": "Should not be here"}
    with pytest.raises(ValueError, match="result"):
        build_git_operation(inputs)

    # status executed without result → schema catches it
    inputs = dict(VALID_INPUTS_EXECUTED)
    inputs.pop("result", None)
    with pytest.raises(SchemaValidationError, match="result"):
        build_git_operation(inputs)

    # status failed without result → schema catches it
    inputs = dict(VALID_INPUTS_FAILED)
    inputs.pop("result", None)
    with pytest.raises(SchemaValidationError, match="result"):
        build_git_operation(inputs)

    # status cancelled without result → schema catches it
    inputs = dict(VALID_INPUTS_CANCELLED)
    inputs.pop("result", None)
    with pytest.raises(SchemaValidationError, match="result"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_merge_pr_without_confirmation():
    # operation_type merge_pr without requires_user_confirmation
    inputs = dict(VALID_INPUTS_MERGE_PR)
    inputs.pop("requires_user_confirmation", None)
    with pytest.raises(SchemaValidationError, match="requires_user_confirmation"):
        build_git_operation(inputs)

    # operation_type merge_pr with requires_user_confirmation false
    inputs = dict(VALID_INPUTS_MERGE_PR)
    inputs["requires_user_confirmation"] = False
    with pytest.raises(SchemaValidationError, match="True was expected"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_operation_specific_missing_fields():
    # commit operation without commit.message
    inputs = dict(VALID_INPUTS)
    inputs["operation_type"] = "commit"
    inputs.pop("commit", None)
    with pytest.raises(ValueError, match="commit.message"):
        build_git_operation(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["operation_type"] = "commit"
    inputs["commit"] = {"sha": "abc123"}
    with pytest.raises(ValueError, match="commit.message"):
        build_git_operation(inputs)

    # push operation without remote
    inputs = dict(VALID_INPUTS)
    inputs["operation_type"] = "push"
    inputs.pop("remote", None)
    with pytest.raises(ValueError, match="remote"):
        build_git_operation(inputs)

    # open_pr operation without pull_request
    inputs = dict(VALID_INPUTS)
    inputs["operation_type"] = "open_pr"
    inputs.pop("pull_request", None)
    with pytest.raises(ValueError, match="pull_request"):
        build_git_operation(inputs)

    # merge_pr operation without pull_request
    inputs = dict(VALID_INPUTS)
    inputs["operation_type"] = "merge_pr"
    inputs.pop("pull_request", None)
    inputs["requires_user_confirmation"] = True
    with pytest.raises(ValueError, match="pull_request"):
        build_git_operation(inputs)

    # merge_pr operation without pull_request.number
    inputs = dict(VALID_INPUTS)
    inputs["operation_type"] = "merge_pr"
    inputs["pull_request"] = {"title": "No number"}
    inputs["requires_user_confirmation"] = True
    with pytest.raises(ValueError, match="pull_request.number"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_failed_policy_with_executed_status():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "executed"
    inputs["policy_checks"] = [
        {"policy_ref": "POL-001", "status": "failed", "details": "Policy violation."},
    ]
    with pytest.raises(ValueError, match="cannot be 'executed'"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_invalid_optional_strings():
    # remote not a string
    inputs = dict(VALID_INPUTS)
    inputs["remote"] = 42
    with pytest.raises(ValueError, match="remote"):
        build_git_operation(inputs)

    # requires_user_confirmation not a bool
    inputs = dict(VALID_INPUTS)
    inputs["requires_user_confirmation"] = "yes"
    with pytest.raises(ValueError, match="requires_user_confirmation"):
        build_git_operation(inputs)

    # execution_notes not a string
    inputs = dict(VALID_INPUTS)
    inputs["execution_notes"] = 42
    with pytest.raises(ValueError, match="execution_notes"):
        build_git_operation(inputs)

    # human_summary not a string
    inputs = dict(VALID_INPUTS)
    inputs["human_summary"] = 42
    with pytest.raises(ValueError, match="human_summary"):
        build_git_operation(inputs)


def test_build_git_operation_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_git_operation(VALID_INPUTS)
