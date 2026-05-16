import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.task_packet import (
    SchemaValidationError,
    build_task_packet,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "task_packet.schema.json"

VALID_INPUTS: dict[str, object] = {
    "plan_id": "PLAN-12345678-001",
    "task_id": "TASK-12345678-005",
    "objective": "Implement the build_task_packet builder for ADF M5.5",
    "allowed_files": [
        "src/agentic_development_framework/builders/task_packet.py",
        "src/agentic_development_framework/builders/__init__.py",
        "tests/test_build_task_packet.py",
    ],
    "forbidden_files": [
        "agents/opencode/",
        "schemas/meta/",
        "pyproject.toml",
    ],
    "allowed_operations": [
        "read",
        "create_schema",
        "validate_schema",
        "run_tests",
        "request_git_operation",
    ],
    "acceptance_criteria": [
        "Output matches task_packet.schema.json",
        "All tests pass",
        "Builder is deterministic",
    ],
    "inputs_required": [
        "plan_id",
        "task_id",
        "objective",
        "allowed_files",
        "allowed_operations",
        "acceptance_criteria",
    ],
    "dependencies": ["TASK-12345678-001", "TASK-12345678-002"],
    "test_requirements": [
        "pytest must pass",
        "coverage above 80%",
    ],
    "policy_refs": ["POL-001", "POL-002"],
    "risk_notes": ["Schema may evolve in future phases"],
    "human_summary": "Build the task_packet builder for M5.5.",
}


def test_build_task_packet_schema_valid():
    artifact = build_task_packet(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_task_packet_is_deterministic():
    a = build_task_packet(VALID_INPUTS)
    b = build_task_packet(VALID_INPUTS)
    c = build_task_packet(VALID_INPUTS)

    assert a == b == c


def test_build_task_packet_rejects_missing_required_input():
    for missing_key in (
        "plan_id",
        "task_id",
        "objective",
        "allowed_files",
        "forbidden_files",
        "allowed_operations",
        "acceptance_criteria",
        "inputs_required",
    ):
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_task_packet(inputs)


def test_build_task_packet_writes_output_path(tmp_path):
    output_path = tmp_path / "task_packet.json"

    artifact = build_task_packet(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_task_packet_rejects_invalid_plan_id():
    inputs = dict(VALID_INPUTS)
    inputs["plan_id"] = "bad-format"
    with pytest.raises(ValueError, match="plan_id"):
        build_task_packet(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["plan_id"] = ""
    with pytest.raises(ValueError, match="plan_id"):
        build_task_packet(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["plan_id"] = 42
    with pytest.raises(ValueError, match="plan_id"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_invalid_task_id():
    inputs = dict(VALID_INPUTS)
    inputs["task_id"] = "bad-format"
    with pytest.raises(ValueError, match="task_id"):
        build_task_packet(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["task_id"] = ""
    with pytest.raises(ValueError, match="task_id"):
        build_task_packet(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["task_id"] = 42
    with pytest.raises(ValueError, match="task_id"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_invalid_objective():
    inputs = dict(VALID_INPUTS)
    inputs["objective"] = ""
    with pytest.raises(ValueError, match="objective"):
        build_task_packet(inputs)

    inputs = dict(VALID_INPUTS)
    inputs["objective"] = 42
    with pytest.raises(ValueError, match="objective"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_invalid_allowed_files():
    # empty list
    inputs = dict(VALID_INPUTS)
    inputs["allowed_files"] = []
    with pytest.raises(ValueError, match="allowed_files"):
        build_task_packet(inputs)

    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["allowed_files"] = "not-a-list"
    with pytest.raises(ValueError, match="allowed_files"):
        build_task_packet(inputs)

    # item not a string
    inputs = dict(VALID_INPUTS)
    inputs["allowed_files"] = ["valid", 42]
    with pytest.raises(ValueError, match="allowed_files"):
        build_task_packet(inputs)

    # empty string item
    inputs = dict(VALID_INPUTS)
    inputs["allowed_files"] = ["valid", ""]
    with pytest.raises(ValueError, match="allowed_files"):
        build_task_packet(inputs)

    # duplicate items
    inputs = dict(VALID_INPUTS)
    inputs["allowed_files"] = ["file_a.py", "file_b.py", "file_a.py"]
    with pytest.raises(ValueError, match="Duplicate"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_invalid_forbidden_files():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["forbidden_files"] = "not-a-list"
    with pytest.raises(ValueError, match="forbidden_files"):
        build_task_packet(inputs)

    # item not a string
    inputs = dict(VALID_INPUTS)
    inputs["forbidden_files"] = ["valid", 42]
    with pytest.raises(ValueError, match="forbidden_files"):
        build_task_packet(inputs)

    # empty string item
    inputs = dict(VALID_INPUTS)
    inputs["forbidden_files"] = ["valid", ""]
    with pytest.raises(ValueError, match="forbidden_files"):
        build_task_packet(inputs)

    # duplicate items
    inputs = dict(VALID_INPUTS)
    inputs["forbidden_files"] = ["file_x.py", "file_y.py", "file_x.py"]
    with pytest.raises(ValueError, match="Duplicate"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_overlapping_allowed_and_forbidden_files():
    inputs = dict(VALID_INPUTS)
    inputs["allowed_files"] = ["file_a.py", "file_b.py", "file_c.py"]
    inputs["forbidden_files"] = ["file_a.py", "file_d.py"]
    with pytest.raises(ValueError, match="overlap"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_invalid_operation():
    inputs = dict(VALID_INPUTS)
    inputs["allowed_operations"] = ["read", "invalid_op"]
    with pytest.raises(ValueError, match="invalid_op"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_duplicate_operation():
    inputs = dict(VALID_INPUTS)
    inputs["allowed_operations"] = ["read", "read", "validate_schema"]
    with pytest.raises(ValueError, match="Duplicate"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_invalid_acceptance_criteria_or_inputs_required():
    # empty acceptance_criteria
    inputs = dict(VALID_INPUTS)
    inputs["acceptance_criteria"] = []
    with pytest.raises(ValueError, match="acceptance_criteria"):
        build_task_packet(inputs)

    # acceptance_criteria not a list
    inputs = dict(VALID_INPUTS)
    inputs["acceptance_criteria"] = "not-a-list"
    with pytest.raises(ValueError, match="acceptance_criteria"):
        build_task_packet(inputs)

    # acceptance_criteria with empty string item
    inputs = dict(VALID_INPUTS)
    inputs["acceptance_criteria"] = ["valid", ""]
    with pytest.raises(ValueError, match="acceptance_criteria"):
        build_task_packet(inputs)

    # duplicate acceptance_criteria
    inputs = dict(VALID_INPUTS)
    inputs["acceptance_criteria"] = ["Test passes", "Test passes"]
    with pytest.raises(ValueError, match="Duplicate"):
        build_task_packet(inputs)

    # empty inputs_required
    inputs = dict(VALID_INPUTS)
    inputs["inputs_required"] = []
    with pytest.raises(ValueError, match="inputs_required"):
        build_task_packet(inputs)

    # inputs_required not a list
    inputs = dict(VALID_INPUTS)
    inputs["inputs_required"] = "not-a-list"
    with pytest.raises(ValueError, match="inputs_required"):
        build_task_packet(inputs)

    # inputs_required with empty string item
    inputs = dict(VALID_INPUTS)
    inputs["inputs_required"] = ["valid", ""]
    with pytest.raises(ValueError, match="inputs_required"):
        build_task_packet(inputs)

    # duplicate inputs_required
    inputs = dict(VALID_INPUTS)
    inputs["inputs_required"] = ["plan_id", "plan_id"]
    with pytest.raises(ValueError, match="Duplicate"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_invalid_dependencies():
    # not a list
    inputs = dict(VALID_INPUTS)
    inputs["dependencies"] = "not-a-list"
    with pytest.raises(ValueError, match="dependencies"):
        build_task_packet(inputs)

    # invalid pattern
    inputs = dict(VALID_INPUTS)
    inputs["dependencies"] = ["bad-format"]
    with pytest.raises(ValueError, match="dependencies"):
        build_task_packet(inputs)

    # item not a string
    inputs = dict(VALID_INPUTS)
    inputs["dependencies"] = [42]
    with pytest.raises(ValueError, match="dependencies"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_self_dependency():
    inputs = dict(VALID_INPUTS)
    inputs["dependencies"] = [
        "TASK-12345678-001",
        "TASK-12345678-005",
    ]
    with pytest.raises(ValueError, match="self-dependency"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_duplicate_dependencies():
    inputs = dict(VALID_INPUTS)
    inputs["dependencies"] = [
        "TASK-12345678-001",
        "TASK-12345678-003",
        "TASK-12345678-001",
    ]
    with pytest.raises(ValueError, match="Duplicate dependency"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_invalid_optional_collections():
    # test_requirements not a list
    inputs = dict(VALID_INPUTS)
    inputs["test_requirements"] = "not-a-list"
    with pytest.raises(ValueError, match="test_requirements"):
        build_task_packet(inputs)

    # test_requirements item not a string
    inputs = dict(VALID_INPUTS)
    inputs["test_requirements"] = ["valid", 42]
    with pytest.raises(ValueError, match="test_requirements"):
        build_task_packet(inputs)

    # policy_refs not a list
    inputs = dict(VALID_INPUTS)
    inputs["policy_refs"] = "not-a-list"
    with pytest.raises(ValueError, match="policy_refs"):
        build_task_packet(inputs)

    # policy_refs item not a string
    inputs = dict(VALID_INPUTS)
    inputs["policy_refs"] = ["valid", 42]
    with pytest.raises(ValueError, match="policy_refs"):
        build_task_packet(inputs)

    # risk_notes not a list
    inputs = dict(VALID_INPUTS)
    inputs["risk_notes"] = "not-a-list"
    with pytest.raises(ValueError, match="risk_notes"):
        build_task_packet(inputs)

    # risk_notes item not a string
    inputs = dict(VALID_INPUTS)
    inputs["risk_notes"] = ["valid", 42]
    with pytest.raises(ValueError, match="risk_notes"):
        build_task_packet(inputs)

    # human_summary not a string
    inputs = dict(VALID_INPUTS)
    inputs["human_summary"] = 42
    with pytest.raises(ValueError, match="human_summary"):
        build_task_packet(inputs)


def test_build_task_packet_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_task_packet(VALID_INPUTS)
