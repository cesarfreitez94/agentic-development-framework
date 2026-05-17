import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

import jsonschema

from agentic_development_framework.builders import (
    build_context_bundle,
    build_decisions,
    build_framework_state,
    build_git_operation,
    build_implementation_report,
    build_intent,
    build_plan,
    build_policy_constraints,
    build_review_report,
    build_roadmap_slice,
    build_schema_catalog,
    build_task_packet,
    build_test_report,
)

_ROOT = Path(__file__).resolve().parents[3]
_SCHEMA_ROOT = _ROOT / "schemas" / "meta"

_SUPPORTED_BUILDERS: dict[str, dict[str, Any]] = {
    "build_intent": {
        "callable": build_intent,
        "schema_path": _SCHEMA_ROOT / "intent.schema.json",
        "artifact_type": "intent",
        "id_field": "intent_id",
        "store_dir": "intent",
    },
    "build_policy_constraints": {
        "callable": build_policy_constraints,
        "schema_path": _SCHEMA_ROOT / "policy_constraints.schema.json",
        "artifact_type": "policy_constraints",
        "id_field": "constraints_id",
        "store_dir": "policy",
    },
    "build_roadmap_slice": {
        "callable": build_roadmap_slice,
        "schema_path": _SCHEMA_ROOT / "roadmap_slice.schema.json",
        "artifact_type": "roadmap_slice",
        "id_field": "slice_id",
        "store_dir": "roadmap",
    },
    "build_plan": {
        "callable": build_plan,
        "schema_path": _SCHEMA_ROOT / "plan.schema.json",
        "artifact_type": "plan",
        "id_field": "plan_id",
        "store_dir": "plan",
    },
    "build_task_packet": {
        "callable": build_task_packet,
        "schema_path": _SCHEMA_ROOT / "task_packet.schema.json",
        "artifact_type": "task_packet",
        "id_field": "packet_id",
        "store_dir": "task_packet",
    },
    "build_context_bundle": {
        "callable": build_context_bundle,
        "schema_path": _SCHEMA_ROOT / "context_bundle.schema.json",
        "artifact_type": "context_bundle",
        "id_field": "bundle_id",
        "store_dir": "context",
    },
    "build_implementation_report": {
        "callable": build_implementation_report,
        "schema_path": _SCHEMA_ROOT / "implementation_report.schema.json",
        "artifact_type": "implementation_report",
        "id_field": "report_id",
        "store_dir": "implementation",
    },
    "build_test_report": {
        "callable": build_test_report,
        "schema_path": _SCHEMA_ROOT / "test_report.schema.json",
        "artifact_type": "test_report",
        "id_field": "report_id",
        "store_dir": "test",
    },
    "build_review_report": {
        "callable": build_review_report,
        "schema_path": _SCHEMA_ROOT / "review_report.schema.json",
        "artifact_type": "review_report",
        "id_field": "report_id",
        "store_dir": "review",
    },
    "build_git_operation": {
        "callable": build_git_operation,
        "schema_path": _SCHEMA_ROOT / "git_operation.schema.json",
        "artifact_type": "git_operation",
        "id_field": "operation_id",
        "store_dir": "git",
    },
    "build_decisions": {
        "callable": build_decisions,
        "schema_path": _SCHEMA_ROOT / "decisions.schema.json",
        "artifact_type": "decisions",
        "id_field": "decision_id",
        "store_dir": "decisions",
    },
    "build_framework_state": {
        "callable": build_framework_state,
        "schema_path": _SCHEMA_ROOT / "framework_state.schema.json",
        "artifact_type": "framework_state",
        "id_field": "state_id",
        "store_dir": "state",
    },
    "build_schema_catalog": {
        "callable": build_schema_catalog,
        "schema_path": _SCHEMA_ROOT / "schema_catalog.schema.json",
        "artifact_type": "schema_catalog",
        "id_field": "catalog_id",
        "store_dir": "catalog",
    },
}


def invoke_builder(
    builder_name: str,
    inputs: dict[str, Any],
    *,
    dry_run: bool = False,
    store: bool = False,
    artifact_root: Optional[str | Path] = None,
    output_path: Optional[str | Path] = None,
    state_context: Optional[dict[str, Any]] = None,
    current_framework_state: Optional[dict[str, Any]] = None,
    deterministic_check: bool = False,
    comparison_target: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Invoke one explicitly selected ADF builder and return evidence.

    The runtime does not select builders, synthesize inputs, invoke agents, run git,
    mutate framework_state, or write dry-run evidence to disk.
    """
    timestamp = _timestamp()
    builder_config = _SUPPORTED_BUILDERS.get(builder_name)
    if builder_config is None:
        return _failure(
            builder_name=builder_name,
            error_type="BuilderNotFoundError",
            error_message=f"Unknown builder: {builder_name}",
            timestamp=timestamp,
            dry_run=dry_run,
        )

    if not isinstance(inputs, dict):
        return _failure(
            builder_name=builder_name,
            error_type="InvalidInputError",
            error_message="inputs must be a dict",
            timestamp=timestamp,
            dry_run=dry_run,
        )

    path_error = _storage_path_error(
        dry_run=dry_run,
        store=store,
        artifact_root=artifact_root,
        output_path=output_path,
    )
    if path_error is not None:
        return _failure(
            builder_name=builder_name,
            error_type=path_error[0],
            error_message=path_error[1],
            timestamp=timestamp,
            dry_run=dry_run,
            attempted_path=str(output_path) if output_path is not None else None,
        )

    builder = builder_config["callable"]
    try:
        artifact = builder(copy.deepcopy(inputs))
    except Exception as exc:  # noqa: BLE001 - structured evidence is the runtime contract.
        error_type = "InvalidInputError" if isinstance(exc, (TypeError, ValueError)) else "BuilderError"
        if exc.__class__.__name__ == "SchemaValidationError":
            error_type = "SchemaValidationError"
        return _failure(
            builder_name=builder_name,
            error_type=error_type,
            error_message=f"{exc.__class__.__name__}: {exc}",
            timestamp=timestamp,
            dry_run=dry_run,
        )

    if not isinstance(artifact, dict):
        return _failure(
            builder_name=builder_name,
            error_type="InvalidReturnType",
            error_message=f"Builder returned {type(artifact).__name__}, expected dict",
            timestamp=timestamp,
            dry_run=dry_run,
        )

    schema = _load_schema(builder_config["schema_path"])
    validation = _validate_artifact(
        artifact=artifact,
        schema=schema,
        schema_path=builder_config["schema_path"],
        timestamp=timestamp,
    )
    artifact_id = artifact.get(builder_config["id_field"])
    artifact_path = str(output_path) if store and not dry_run and output_path is not None else None

    determinism = _deterministic_check(
        builder=builder,
        inputs=inputs,
        performed=deterministic_check,
    )
    comparison = _compare_artifacts(
        produced_artifact=artifact,
        comparison_target=comparison_target,
        schema=schema,
    )

    if validation["outcome"] != "pass":
        return _failure(
            builder_name=builder_name,
            error_type="SchemaValidationError",
            error_message="Produced artifact failed schema validation",
            timestamp=timestamp,
            dry_run=dry_run,
            validation=validation,
            produced_artifact=artifact,
            deterministic_check_result=determinism,
            comparison=comparison,
        )

    if store and not dry_run and output_path is not None:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

    state_update_proposal = _build_state_update_proposal(
        artifact_id=artifact_id,
        artifact_type=builder_config["artifact_type"],
        artifact_path=artifact_path,
        validation=validation,
        state_context=state_context,
        current_framework_state=current_framework_state,
    )

    return {
        "success": True,
        "builder_name": builder_name,
        "dry_run": dry_run,
        "stored": bool(store and not dry_run),
        "artifact": artifact,
        "artifact_id": artifact_id,
        "artifact_type": builder_config["artifact_type"],
        "artifact_path": artifact_path,
        "validation": validation,
        "deterministic_check": determinism,
        "comparison": comparison,
        "state_update_proposal": state_update_proposal,
        "state_update_proposal_preview": state_update_proposal if dry_run else None,
        "no_write_confirmation": dry_run,
        "no_git_confirmation": dry_run,
        "timestamp": timestamp,
        "input_summary": {"keys": sorted(inputs.keys())},
        "artifact_preview": _artifact_preview(artifact),
    }


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_schema(schema_path: Path) -> dict[str, Any]:
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _validate_artifact(
    *, artifact: dict[str, Any], schema: dict[str, Any], schema_path: Path, timestamp: str
) -> dict[str, Any]:
    validator = jsonschema.Draft7Validator(schema)
    findings = [
        {
            "field": ".".join(str(part) for part in error.absolute_path) or "$",
            "issue": error.message,
            "severity": "error",
        }
        for error in sorted(validator.iter_errors(artifact), key=lambda err: list(err.path))
    ]
    return {
        "schema_ref": str(schema_path.relative_to(_ROOT)),
        "validated_at": timestamp,
        "outcome": "fail" if findings else "pass",
        "findings": findings,
    }


def _storage_path_error(
    *,
    dry_run: bool,
    store: bool,
    artifact_root: Optional[str | Path],
    output_path: Optional[str | Path],
) -> Optional[tuple[str, str]]:
    if dry_run or not store:
        return None
    if artifact_root is None or output_path is None:
        return (
            "OutputPathRequired",
            "artifact_root and output_path are required when store=true",
        )
    root = Path(artifact_root).resolve(strict=False)
    output = Path(output_path).resolve(strict=False)
    try:
        output.relative_to(root)
    except ValueError:
        return (
            "PathNotAllowedError",
            f"output_path must be under artifact_root: {root}",
        )
    return None


def _deterministic_check(
    *, builder: Callable[[dict[str, Any]], dict[str, Any]], inputs: dict[str, Any], performed: bool
) -> dict[str, Any]:
    if not performed:
        return {"performed": False, "result": None}
    try:
        first = builder(copy.deepcopy(inputs))
        second = builder(copy.deepcopy(inputs))
    except Exception as exc:  # noqa: BLE001 - diagnostic evidence only.
        return {
            "performed": True,
            "result": "error",
            "error": f"{exc.__class__.__name__}: {exc}",
        }
    return {
        "performed": True,
        "result": "identical" if first == second else "different",
    }


def _compare_artifacts(
    *,
    produced_artifact: dict[str, Any],
    comparison_target: Optional[dict[str, Any]],
    schema: dict[str, Any],
) -> Optional[dict[str, Any]]:
    if comparison_target is None:
        return None
    if not isinstance(comparison_target, dict):
        return {
            "outcome": "schema_invalid",
            "details": [{"field": "$", "issue": "comparison_target must be a dict"}],
        }

    validator = jsonschema.Draft7Validator(schema)
    target_findings = [
        {
            "field": ".".join(str(part) for part in error.absolute_path) or "$",
            "issue": error.message,
        }
        for error in sorted(
            validator.iter_errors(comparison_target), key=lambda err: list(err.path)
        )
    ]
    if target_findings:
        return {"outcome": "schema_invalid", "details": target_findings}
    if produced_artifact == comparison_target:
        return {"outcome": "equivalent", "details": []}
    if set(produced_artifact) == set(comparison_target):
        return {
            "outcome": "schema_valid_but_semantically_different",
            "details": _top_level_differences(produced_artifact, comparison_target),
        }
    return {
        "outcome": "partial_equivalence",
        "details": _top_level_differences(produced_artifact, comparison_target),
    }


def _top_level_differences(
    produced_artifact: dict[str, Any], comparison_target: dict[str, Any]
) -> list[dict[str, Any]]:
    details = []
    for key in sorted(set(produced_artifact) | set(comparison_target)):
        if produced_artifact.get(key) != comparison_target.get(key):
            details.append({"field": key, "issue": "values differ"})
    return details


def _build_state_update_proposal(
    *,
    artifact_id: Any,
    artifact_type: str,
    artifact_path: Optional[str],
    validation: dict[str, Any],
    state_context: Optional[dict[str, Any]],
    current_framework_state: Optional[dict[str, Any]],
) -> dict[str, Any]:
    proposal = {
        "preview_only": True,
        "applied": False,
        "conflicted": False,
        "conflicts": [],
        "validation_evidence": validation,
        "add_artifact_refs": [
            {
                "type": artifact_type,
                "id": artifact_id,
                "path": artifact_path,
                "validation_outcome": validation["outcome"],
            }
        ],
    }

    if state_context is not None:
        if "current_phase" in state_context:
            proposal["set_current_phase"] = state_context["current_phase"]
        if "statuses" in state_context:
            proposal["update_statuses"] = copy.deepcopy(state_context["statuses"])

    if current_framework_state is not None:
        artifact_refs = current_framework_state.get("artifact_refs", [])
        for artifact_ref in artifact_refs:
            if isinstance(artifact_ref, dict) and artifact_ref.get("artifact_id") == artifact_id:
                proposal["conflicted"] = True
                proposal["conflicts"].append(
                    f"artifact_id already exists in framework_state: {artifact_id}"
                )

    return proposal


def _failure(
    *,
    builder_name: str,
    error_type: str,
    error_message: str,
    timestamp: str,
    dry_run: bool,
    validation: Optional[dict[str, Any]] = None,
    produced_artifact: Optional[dict[str, Any]] = None,
    attempted_path: Optional[str] = None,
    deterministic_check_result: Optional[dict[str, Any]] = None,
    comparison: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "builder_name": builder_name,
        "dry_run": dry_run,
        "stored": False,
        "error_type": error_type,
        "error_message": error_message,
        "validation": validation,
        "produced_artifact": produced_artifact,
        "attempted_path": attempted_path,
        "deterministic_check": deterministic_check_result
        or {"performed": False, "result": None},
        "comparison": comparison,
        "state_update_proposal": None,
        "state_update_proposal_preview": None,
        "no_write_confirmation": dry_run,
        "no_git_confirmation": dry_run,
        "timestamp": timestamp,
    }


def _artifact_preview(artifact: dict[str, Any]) -> str:
    preview = json.dumps(artifact, sort_keys=True, ensure_ascii=True)
    if len(preview) > 500:
        return preview[:497] + "..."
    return preview
