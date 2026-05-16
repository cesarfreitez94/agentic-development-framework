import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.implementation_report import (
    SchemaValidationError,
    build_implementation_report,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "implementation_report.schema.json"

VALID_INPUTS: dict[str, object] = {
    "packet_id": "TPACKET-12345678-001",
    "status": "completed",
    "changed_files": [
        {
            "path": "src/agentic_development_framework/builders/implementation_report.py",
            "change_type": "created",
        },
        {
            "path": "src/agentic_development_framework/builders/__init__.py",
            "change_type": "modified",
        },
        {
            "path": "tests/test_build_implementation_report.py",
            "change_type": "created",
        },
    ],
    "created_artifacts": [
        {
            "contract_name": "implementation_report",
            "artifact_id": "IMPL-87654321-001",
            "path": ".adf/artifacts/implementation_report.json",
            "contract_version": "2.0",
        },
    ],
    "acceptance_status": "passed",
    "blockers": [],
    "commands_run": [
        {"command": "pytest tests/test_build_implementation_report.py", "exit_code": 0, "status": "passed"},
        {"command": "git diff --stat", "exit_code": 0, "status": "passed"},
    ],
    "deviations": [],
    "follow_up_tasks": [
        "Proceed to M5.8 build_test_report",
        "Run full test suite",
    ],
    "human_summary": "Implementation report builder for M5.7.",
}


def test_build_implementation_report_schema_valid():
    artifact = build_implementation_report(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_implementation_report_is_deterministic():
    a = build_implementation_report(VALID_INPUTS)
    b = build_implementation_report(VALID_INPUTS)
    c = build_implementation_report(VALID_INPUTS)

    assert a == b == c


def test_build_implementation_report_rejects_missing_required_input():
    required_keys = {
        "packet_id",
        "status",
        "changed_files",
        "created_artifacts",
        "acceptance_status",
        "blockers",
    }
    for missing_key in required_keys:
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_implementation_report(inputs)


def test_build_implementation_report_writes_output_path(tmp_path):
    output_path = tmp_path / "implementation_report.json"

    artifact = build_implementation_report(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_implementation_report_rejects_invalid_packet_id():
    inputs = dict(VALID_INPUTS)
    inputs["packet_id"] = "bad-format"
    with pytest.raises(ValueError, match="packet_id"):
        build_implementation_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["packet_id"] = ""
    with pytest.raises(ValueError, match="packet_id"):
        build_implementation_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["packet_id"] = 42
    with pytest.raises(ValueError, match="packet_id"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_invalid_status():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "unknown"
    with pytest.raises(ValueError, match="status"):
        build_implementation_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["status"] = ""
    with pytest.raises(ValueError, match="status"):
        build_implementation_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["status"] = 42
    with pytest.raises(ValueError, match="status"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_invalid_changed_files():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["changed_files"] = "not-a-list"
    with pytest.raises(ValueError, match="changed_files"):
        build_implementation_report(inputs)

    # empty list
    inputs = dict(VALID_INPUTS)
    inputs["changed_files"] = []
    with pytest.raises(ValueError, match="changed_files"):
        build_implementation_report(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["changed_files"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="changed_files"):
        build_implementation_report(inputs)

    # missing required key (change_type)
    inputs = dict(VALID_INPUTS)
    inputs["changed_files"] = [
        {"path": "src/file.py"},
    ]
    with pytest.raises(ValueError, match="changed_files"):
        build_implementation_report(inputs)

    # invalid change_type enum
    inputs = dict(VALID_INPUTS)
    inputs["changed_files"] = [
        {"path": "src/file.py", "change_type": "updated"},
    ]
    with pytest.raises(ValueError, match="changed_files"):
        build_implementation_report(inputs)

    # empty path
    inputs = dict(VALID_INPUTS)
    inputs["changed_files"] = [
        {"path": "", "change_type": "created"},
    ]
    with pytest.raises(ValueError, match="changed_files"):
        build_implementation_report(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["changed_files"] = [
        {"path": "src/file.py", "change_type": "created", "extra": "nope"},
    ]
    with pytest.raises(ValueError, match="changed_files"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_duplicate_changed_files():
    inputs = dict(VALID_INPUTS)
    inputs["changed_files"] = [
        {"path": "src/file.py", "change_type": "created"},
        {"path": "src/file.py", "change_type": "created"},
        {"path": "src/other.py", "change_type": "modified"},
    ]
    with pytest.raises(ValueError, match="Duplicate"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_invalid_created_artifacts():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["created_artifacts"] = "not-a-list"
    with pytest.raises(ValueError, match="created_artifacts"):
        build_implementation_report(inputs)

    # empty list
    inputs = dict(VALID_INPUTS)
    inputs["created_artifacts"] = []
    with pytest.raises(ValueError, match="created_artifacts"):
        build_implementation_report(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["created_artifacts"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="created_artifacts"):
        build_implementation_report(inputs)

    # missing required key (artifact_id)
    inputs = dict(VALID_INPUTS)
    inputs["created_artifacts"] = [
        {"contract_name": "test", "path": "path.json"},
    ]
    with pytest.raises(ValueError, match="created_artifacts"):
        build_implementation_report(inputs)

    # empty contract_name
    inputs = dict(VALID_INPUTS)
    inputs["created_artifacts"] = [
        {"contract_name": "", "artifact_id": "ID-1", "path": "path.json"},
    ]
    with pytest.raises(ValueError, match="created_artifacts"):
        build_implementation_report(inputs)

    # non-string contract_version
    inputs = dict(VALID_INPUTS)
    inputs["created_artifacts"] = [
        {
            "contract_name": "test",
            "artifact_id": "ID-1",
            "path": "path.json",
            "contract_version": 42,
        },
    ]
    with pytest.raises(ValueError, match="created_artifacts"):
        build_implementation_report(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["created_artifacts"] = [
        {
            "contract_name": "test",
            "artifact_id": "ID-1",
            "path": "path.json",
            "extra": "nope",
        },
    ]
    with pytest.raises(ValueError, match="created_artifacts"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_duplicate_created_artifacts():
    inputs = dict(VALID_INPUTS)
    inputs["created_artifacts"] = [
        {"contract_name": "test", "artifact_id": "ID-1", "path": "a.json"},
        {"contract_name": "test", "artifact_id": "ID-1", "path": "b.json"},
        {"contract_name": "other", "artifact_id": "ID-2", "path": "c.json"},
    ]
    with pytest.raises(ValueError, match="Duplicate"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_invalid_acceptance_status():
    inputs = dict(VALID_INPUTS)
    inputs["acceptance_status"] = "unknown"
    with pytest.raises(ValueError, match="acceptance_status"):
        build_implementation_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["acceptance_status"] = ""
    with pytest.raises(ValueError, match="acceptance_status"):
        build_implementation_report(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["acceptance_status"] = 42
    with pytest.raises(ValueError, match="acceptance_status"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_failed_or_blocked_without_blockers():
    for bad_status in ("failed", "blocked"):
        inputs = dict(VALID_INPUTS)
        inputs["status"] = bad_status
        inputs["blockers"] = []
        with pytest.raises(ValueError, match="blockers"):
            build_implementation_report(inputs)


def test_build_implementation_report_rejects_completed_with_failed_acceptance():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "completed"
    inputs["acceptance_status"] = "failed"
    with pytest.raises(ValueError, match="completed"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_invalid_blockers():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["blockers"] = "not-a-list"
    with pytest.raises(ValueError, match="blockers"):
        build_implementation_report(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["blockers"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="blockers"):
        build_implementation_report(inputs)

    # missing required key (message)
    inputs = dict(VALID_INPUTS)
    inputs["blockers"] = [
        {"code": "BLOCK-001"},
    ]
    with pytest.raises(ValueError, match="blockers"):
        build_implementation_report(inputs)

    # empty code
    inputs = dict(VALID_INPUTS)
    inputs["blockers"] = [
        {"code": "", "message": "A blocker message"},
    ]
    with pytest.raises(ValueError, match="blockers"):
        build_implementation_report(inputs)

    # non-string path if provided
    inputs = dict(VALID_INPUTS)
    inputs["blockers"] = [
        {"code": "BLOCK-001", "message": "A blocker message", "path": 42},
    ]
    with pytest.raises(ValueError, match="blockers"):
        build_implementation_report(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["blockers"] = [
        {"code": "BLOCK-001", "message": "A blocker message", "extra": "nope"},
    ]
    with pytest.raises(ValueError, match="blockers"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_duplicate_blocker_codes():
    inputs = dict(VALID_INPUTS)
    inputs["status"] = "blocked"
    inputs["blockers"] = [
        {"code": "BLOCK-001", "message": "First blocker"},
        {"code": "BLOCK-001", "message": "Duplicate blocker"},
        {"code": "BLOCK-002", "message": "Another blocker"},
    ]
    with pytest.raises(ValueError, match="Duplicate"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_invalid_commands_run():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["commands_run"] = "not-a-list"
    with pytest.raises(ValueError, match="commands_run"):
        build_implementation_report(inputs)

    # item not a dict
    inputs = dict(VALID_INPUTS)
    inputs["commands_run"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="commands_run"):
        build_implementation_report(inputs)

    # missing required key (exit_code)
    inputs = dict(VALID_INPUTS)
    inputs["commands_run"] = [
        {"command": "ls"},
    ]
    with pytest.raises(ValueError, match="commands_run"):
        build_implementation_report(inputs)

    # empty command
    inputs = dict(VALID_INPUTS)
    inputs["commands_run"] = [
        {"command": "", "exit_code": 0},
    ]
    with pytest.raises(ValueError, match="commands_run"):
        build_implementation_report(inputs)

    # exit_code not an integer
    inputs = dict(VALID_INPUTS)
    inputs["commands_run"] = [
        {"command": "ls", "exit_code": "0"},
    ]
    with pytest.raises(ValueError, match="commands_run"):
        build_implementation_report(inputs)

    # negative exit_code
    inputs = dict(VALID_INPUTS)
    inputs["commands_run"] = [
        {"command": "ls", "exit_code": -1},
    ]
    with pytest.raises(ValueError, match="commands_run"):
        build_implementation_report(inputs)

    # invalid status enum
    inputs = dict(VALID_INPUTS)
    inputs["commands_run"] = [
        {"command": "ls", "exit_code": 0, "status": "unknown"},
    ]
    with pytest.raises(ValueError, match="commands_run"):
        build_implementation_report(inputs)

    # extra keys not allowed
    inputs = dict(VALID_INPUTS)
    inputs["commands_run"] = [
        {"command": "ls", "exit_code": 0, "extra": "nope"},
    ]
    with pytest.raises(ValueError, match="commands_run"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_duplicate_commands():
    inputs = dict(VALID_INPUTS)
    inputs["commands_run"] = [
        {"command": "pytest", "exit_code": 0},
        {"command": "pytest", "exit_code": 0},
        {"command": "flake8", "exit_code": 0},
    ]
    with pytest.raises(ValueError, match="Duplicate"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_invalid_optional_collections():
    # deviations not a list
    inputs = dict(VALID_INPUTS)
    inputs["deviations"] = "not-a-list"
    with pytest.raises(ValueError, match="deviations"):
        build_implementation_report(inputs)

    # deviations with non-string item
    inputs = dict(VALID_INPUTS)
    inputs["deviations"] = [42]
    with pytest.raises(ValueError, match="deviations"):
        build_implementation_report(inputs)

    # deviations with empty string
    inputs = dict(VALID_INPUTS)
    inputs["deviations"] = [""]
    with pytest.raises(ValueError, match="deviations"):
        build_implementation_report(inputs)

    # follow_up_tasks not a list
    inputs = dict(VALID_INPUTS)
    inputs["follow_up_tasks"] = "not-a-list"
    with pytest.raises(ValueError, match="follow_up_tasks"):
        build_implementation_report(inputs)

    # follow_up_tasks with non-string item
    inputs = dict(VALID_INPUTS)
    inputs["follow_up_tasks"] = [42]
    with pytest.raises(ValueError, match="follow_up_tasks"):
        build_implementation_report(inputs)

    # follow_up_tasks with empty string
    inputs = dict(VALID_INPUTS)
    inputs["follow_up_tasks"] = [""]
    with pytest.raises(ValueError, match="follow_up_tasks"):
        build_implementation_report(inputs)

    # human_summary not a string
    inputs = dict(VALID_INPUTS)
    inputs["human_summary"] = 42
    with pytest.raises(ValueError, match="human_summary"):
        build_implementation_report(inputs)


def test_build_implementation_report_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_implementation_report(VALID_INPUTS)
