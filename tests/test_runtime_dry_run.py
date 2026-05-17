from agentic_development_framework.runtime import invoke_builder

VALID_INTENT_INPUTS: dict[str, object] = {
    "source": "user",
    "objective": "Dry-run a minimal runtime invocation",
    "scope_include": ["Return evidence without persistence"],
    "constraints": ["No writes", "No git"],
    "requested_outputs": ["Dry-run evidence"],
    "requires_user_confirmation": False,
}


def test_dry_run_produces_evidence_and_writes_nothing(tmp_path):
    artifact_root = tmp_path / ".adf" / "artifacts"
    output_path = artifact_root / "intent" / "dry-run.json"

    result = invoke_builder(
        "build_intent",
        VALID_INTENT_INPUTS,
        dry_run=True,
        store=True,
        artifact_root=artifact_root,
        output_path=output_path,
    )

    assert result["success"] is True
    assert result["dry_run"] is True
    assert result["artifact"]["contract_name"] == "intent"
    assert result["artifact_preview"]
    assert result["validation"]["outcome"] == "pass"
    assert result["state_update_proposal_preview"]["preview_only"] is True
    assert not output_path.exists()
    assert not artifact_root.exists()


def test_dry_run_no_write_and_no_git_confirmations_are_true():
    result = invoke_builder("build_intent", VALID_INTENT_INPUTS, dry_run=True)

    assert result["no_write_confirmation"] is True
    assert result["no_git_confirmation"] is True


def test_dry_run_deterministic_check_when_explicitly_requested():
    result = invoke_builder(
        "build_intent",
        VALID_INTENT_INPUTS,
        dry_run=True,
        deterministic_check=True,
    )

    assert result["success"] is True
    assert result["deterministic_check"] == {
        "performed": True,
        "result": "identical",
    }


def test_dry_run_comparison_uses_m7_categories():
    baseline = invoke_builder("build_intent", VALID_INTENT_INPUTS, dry_run=True)

    result = invoke_builder(
        "build_intent",
        VALID_INTENT_INPUTS,
        dry_run=True,
        comparison_target=baseline["artifact"],
    )

    assert result["comparison"] == {"outcome": "equivalent", "details": []}
