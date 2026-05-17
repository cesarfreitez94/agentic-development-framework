import copy
from pathlib import Path

from agentic_development_framework.runtime import invoke_builder
from agentic_development_framework.runtime import invocation

ROOT = Path(__file__).resolve().parents[1]

VALID_INTENT_INPUTS: dict[str, object] = {
    "source": "user",
    "objective": "Implement minimal runtime invocation",
    "scope_include": ["Invoke an explicitly selected builder"],
    "scope_exclude": ["Create CLI", "Invoke agents"],
    "constraints": ["Use explicit inputs only"],
    "requested_outputs": ["Structured invocation evidence"],
    "urgency": "medium",
    "requires_user_confirmation": False,
    "human_summary": "Minimal runtime invocation test input",
}


def test_successful_explicit_builder_invocation():
    result = invoke_builder("build_intent", VALID_INTENT_INPUTS)

    assert result["success"] is True
    assert result["builder_name"] == "build_intent"
    assert result["artifact"]["contract_name"] == "intent"
    assert result["artifact_id"] == result["artifact"]["intent_id"]
    assert result["stored"] is False


def test_unknown_builder_failure_is_structured():
    result = invoke_builder("build_missing", VALID_INTENT_INPUTS)

    assert result["success"] is False
    assert result["error_type"] == "BuilderNotFoundError"
    assert result["state_update_proposal"] is None


def test_schema_validation_pass_evidence():
    result = invoke_builder("build_intent", VALID_INTENT_INPUTS)

    assert result["validation"]["outcome"] == "pass"
    assert result["validation"]["findings"] == []
    assert result["validation"]["schema_ref"] == "schemas/meta/intent.schema.json"


def test_invalid_input_failure_is_structured():
    inputs = dict(VALID_INTENT_INPUTS)
    inputs.pop("source")

    result = invoke_builder("build_intent", inputs)

    assert result["success"] is False
    assert result["error_type"] == "InvalidInputError"
    assert result["stored"] is False


def test_invalid_artifact_is_not_canonically_stored(monkeypatch, tmp_path):
    def invalid_builder(inputs):
        return {"contract_name": "intent"}

    monkeypatch.setitem(
        invocation._SUPPORTED_BUILDERS["build_intent"], "callable", invalid_builder
    )
    artifact_root = tmp_path / ".adf" / "artifacts"
    output_path = artifact_root / "intent" / "invalid.json"

    result = invoke_builder(
        "build_intent",
        VALID_INTENT_INPUTS,
        store=True,
        artifact_root=artifact_root,
        output_path=output_path,
    )

    assert result["success"] is False
    assert result["error_type"] == "SchemaValidationError"
    assert result["validation"]["outcome"] == "fail"
    assert not output_path.exists()
    assert result["state_update_proposal"] is None


def test_non_dry_run_refuses_output_outside_allowed_artifact_root(tmp_path):
    artifact_root = tmp_path / ".adf" / "artifacts"
    outside_path = tmp_path / "outside" / "intent.json"

    result = invoke_builder(
        "build_intent",
        VALID_INTENT_INPUTS,
        store=True,
        artifact_root=artifact_root,
        output_path=outside_path,
    )

    assert result["success"] is False
    assert result["error_type"] == "PathNotAllowedError"
    assert result["attempted_path"] == str(outside_path)
    assert not outside_path.exists()


def test_framework_state_is_not_mutated_only_proposal_preview():
    framework_state = {
        "current_phase": "M8",
        "artifact_refs": [],
    }
    original_framework_state = copy.deepcopy(framework_state)
    state_context = {
        "current_phase": "M8.1",
        "statuses": {"M8.1": "in_progress"},
        "pending_decisions": ["must not be copied"],
        "mode": "candidate",
        "gates": ["must not be copied"],
        "git_state": {"must": "not be copied"},
        "acceptance_decision": "must not be copied",
    }

    result = invoke_builder(
        "build_intent",
        VALID_INTENT_INPUTS,
        state_context=state_context,
        current_framework_state=framework_state,
    )

    assert framework_state == original_framework_state
    proposal = result["state_update_proposal"]
    assert proposal["preview_only"] is True
    assert proposal["applied"] is False
    assert proposal["set_current_phase"] == "M8.1"
    assert proposal["update_statuses"] == {"M8.1": "in_progress"}
    assert proposal["add_artifact_refs"][0]["type"] == "intent"
    assert "pending_decisions" not in proposal
    assert "mode" not in proposal
    assert "gates" not in proposal
    assert "git_state" not in proposal
    assert "acceptance_decision" not in proposal


def test_runtime_invocation_does_not_modify_builder_schema_or_agent_files():
    watched_paths = [
        ROOT / "src" / "agentic_development_framework" / "builders" / "intent.py",
        ROOT / "schemas" / "meta" / "intent.schema.json",
        ROOT / "agents" / "opencode" / "orchestrator.md",
    ]
    before = {path: path.read_bytes() for path in watched_paths}

    invoke_builder("build_intent", VALID_INTENT_INPUTS)

    assert {path: path.read_bytes() for path in watched_paths} == before
