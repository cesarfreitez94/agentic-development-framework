import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import jsonschema

from .intent import SchemaValidationError

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "schemas"
    / "meta"
    / "review_report.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "REV-"

_IMPL_REPORT_ID_RE = r"^IMPL-[0-9]{8}-[0-9]{3}$"
_TEST_REPORT_ID_RE = r"^TEST-[0-9]{8}-[0-9]{3}$"

_VALID_STATUSES = frozenset(
    {"approved", "approved_with_risks", "changes_requested", "blocked"}
)
_VALID_RECOMMENDATIONS = frozenset(
    {"proceed_to_git", "fix_required", "ask_user", "stop"}
)
_VALID_SEVERITIES = frozenset({"low", "medium", "high", "critical"})
_VALID_POLICY_STATUSES = frozenset({"passed", "failed", "not_applicable"})

_FINDING_KEYS = frozenset({"severity", "location", "message", "recommendation"})
_LOCATION_KEYS = frozenset({"path", "line_start", "line_end"})
_POLICY_COMPLIANCE_KEYS = frozenset({"policy_ref", "status", "details"})


def _validate_non_empty_string(value: object, label: str) -> None:
    if not isinstance(value, str) or len(value) < 1:
        raise ValueError(f"{label} must be a non-empty string")


def _validate_string_list_no_duplicates(
    value: object, label: str, min_items: int = 0
) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    if len(value) < min_items:
        raise ValueError(f"{label} must have at least {min_items} item(s)")
    seen: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, str) or len(item) < 1:
            raise ValueError(f"{label}[{i}] must be a non-empty string")
        if item in seen:
            raise ValueError(f"Duplicate value {item!r} in {label}")
        seen.add(item)


def _validate_location(location: object, label: str) -> None:
    if not isinstance(location, dict):
        raise ValueError(f"{label} must be a dict")

    if "path" not in location:
        raise ValueError(f"{label} must have a 'path' key")

    extra = set(location.keys()) - _LOCATION_KEYS
    if extra:
        raise ValueError(
            f"{label} has extra keys: {', '.join(sorted(extra))}"
        )

    path_val = location["path"]
    _validate_non_empty_string(path_val, f"{label}.path")

    line_start = location.get("line_start")
    if line_start is not None:
        if not isinstance(line_start, int) or line_start < 1:
            raise ValueError(
                f"{label}.line_start must be an integer >= 1 if provided"
            )

    line_end = location.get("line_end")
    if line_end is not None:
        if not isinstance(line_end, int) or line_end < 1:
            raise ValueError(
                f"{label}.line_end must be an integer >= 1 if provided"
            )

    if line_start is not None and line_end is not None and line_start > line_end:
        raise ValueError(
            f"{label}: line_start ({line_start}) must be <= line_end ({line_end})"
        )


def _validate_findings(findings: object) -> None:
    if not isinstance(findings, list):
        raise ValueError("findings must be a list")

    seen_tuples: set[tuple[str, str, str]] = set()
    for i, item in enumerate(findings):
        if not isinstance(item, dict):
            raise ValueError(f"findings[{i}] must be a dict")

        for key in ("severity", "location", "message"):
            if key not in item:
                raise ValueError(f"findings[{i}] must have a {key!r} key")

        extra = set(item.keys()) - _FINDING_KEYS
        if extra:
            raise ValueError(
                f"findings[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        severity = item["severity"]
        if severity not in _VALID_SEVERITIES:
            raise ValueError(
                f"findings[{i}].severity {severity!r} must be one of: "
                f"{', '.join(sorted(_VALID_SEVERITIES))}"
            )

        location = item["location"]
        _validate_location(location, f"findings[{i}].location")

        message = item["message"]
        _validate_non_empty_string(message, f"findings[{i}].message")

        recommendation = item.get("recommendation")
        if recommendation is not None and not isinstance(recommendation, str):
            raise ValueError(
                f"findings[{i}].recommendation must be a string if provided"
            )

        dup_key = (severity, location["path"], message)
        if dup_key in seen_tuples:
            raise ValueError(
                f"Duplicate finding (severity={severity!r}, "
                f"path={location['path']!r}, message={message!r}) in findings"
            )
        seen_tuples.add(dup_key)


def _validate_policy_compliance(policy_compliance: object) -> None:
    if not isinstance(policy_compliance, list):
        raise ValueError("policy_compliance must be a list")
    if len(policy_compliance) < 1:
        raise ValueError("policy_compliance must have at least 1 item(s)")

    seen_policy_refs: set[str] = set()
    for i, item in enumerate(policy_compliance):
        if not isinstance(item, dict):
            raise ValueError(f"policy_compliance[{i}] must be a dict")

        for key in ("policy_ref", "status"):
            if key not in item:
                raise ValueError(f"policy_compliance[{i}] must have a {key!r} key")

        extra = set(item.keys()) - _POLICY_COMPLIANCE_KEYS
        if extra:
            raise ValueError(
                f"policy_compliance[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        policy_ref = item["policy_ref"]
        _validate_non_empty_string(policy_ref, f"policy_compliance[{i}].policy_ref")

        if policy_ref in seen_policy_refs:
            raise ValueError(
                f"Duplicate policy_ref {policy_ref!r} in policy_compliance"
            )
        seen_policy_refs.add(policy_ref)

        status = item["status"]
        if status not in _VALID_POLICY_STATUSES:
            raise ValueError(
                f"policy_compliance[{i}].status {status!r} must be one of: "
                f"{', '.join(sorted(_VALID_POLICY_STATUSES))}"
            )

        details = item.get("details")
        if details is not None and not isinstance(details, str):
            raise ValueError(
                f"policy_compliance[{i}].details must be a string if provided"
            )


def _generate_deterministic_id(inputs: dict[str, object]) -> str:
    stable = json.dumps(inputs, sort_keys=True, default=str, ensure_ascii=True)
    digest = hashlib.sha256(stable.encode("utf-8")).digest()
    numeric = int.from_bytes(digest[:11], "big")
    part1 = numeric % (10**8)
    part2 = (numeric // (10**8)) % (10**3)
    return f"{_ID_PREFIX}{part1:08d}-{part2:03d}"


def _generate_deterministic_created_at(inputs: dict[str, object]) -> str:
    stable = json.dumps(inputs, sort_keys=True, default=str, ensure_ascii=True)
    digest = hashlib.sha256(stable.encode("utf-8")).digest()
    seconds_offset = int.from_bytes(digest[:4], "big") % (365 * 24 * 60 * 60)
    created = _BASE_EPOCH + timedelta(seconds=seconds_offset)
    return created.isoformat()


def build_review_report(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build a review_report artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            implementation_report_id (str, required): ID matching ^IMPL-[0-9]{8}-[0-9]{3}$.
            test_report_id (str, required): ID matching ^TEST-[0-9]{8}-[0-9]{3}$.
            status (str, required): One of "approved", "approved_with_risks",
                "changes_requested", "blocked".
            findings (list[dict], required): List of finding entries.
            policy_compliance (list[dict], required): Non-empty list of policy checks.
            recommendation (str, required): One of "proceed_to_git", "fix_required",
                "ask_user", "stop".
            residual_risks (list[str], optional): List of residual risks.
            required_fixes (list[str], optional): List of required fixes.
            approved_with_notes (str, optional): Notes for approved status.
            human_summary (str, optional): Human-readable summary.
        output_path: Optional filesystem path. If provided, writes JSON artifact.

    Returns:
        Dict representing the complete, schema-valid review_report artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.
    """
    # --- Validate required inputs ---
    required = {
        "implementation_report_id",
        "test_report_id",
        "status",
        "findings",
        "policy_compliance",
        "recommendation",
    }
    for key in sorted(required):
        if key not in inputs:
            raise ValueError(f"Missing required input: {key!r}")

    implementation_report_id = inputs["implementation_report_id"]
    _validate_non_empty_string(implementation_report_id, "implementation_report_id")
    if not re.match(_IMPL_REPORT_ID_RE, implementation_report_id):
        raise ValueError(
            f"implementation_report_id {implementation_report_id!r} must match pattern "
            f"{_IMPL_REPORT_ID_RE}"
        )

    test_report_id = inputs["test_report_id"]
    _validate_non_empty_string(test_report_id, "test_report_id")
    if not re.match(_TEST_REPORT_ID_RE, test_report_id):
        raise ValueError(
            f"test_report_id {test_report_id!r} must match pattern "
            f"{_TEST_REPORT_ID_RE}"
        )

    status = inputs["status"]
    if status not in _VALID_STATUSES:
        raise ValueError(
            f"Invalid status {status!r}, must be one of: "
            f"{', '.join(sorted(_VALID_STATUSES))}"
        )

    findings = inputs["findings"]
    _validate_findings(findings)

    policy_compliance = inputs["policy_compliance"]
    _validate_policy_compliance(policy_compliance)

    recommendation = inputs["recommendation"]
    if recommendation not in _VALID_RECOMMENDATIONS:
        raise ValueError(
            f"Invalid recommendation {recommendation!r}, must be one of: "
            f"{', '.join(sorted(_VALID_RECOMMENDATIONS))}"
        )

    # --- Validate optional inputs ---
    residual_risks = inputs.get("residual_risks")
    if residual_risks is not None:
        _validate_string_list_no_duplicates(residual_risks, "residual_risks")

    required_fixes = inputs.get("required_fixes")
    if required_fixes is not None:
        _validate_string_list_no_duplicates(required_fixes, "required_fixes")

    approved_with_notes = inputs.get("approved_with_notes")
    if approved_with_notes is not None and not isinstance(approved_with_notes, str):
        raise ValueError("approved_with_notes must be a string if provided")

    human_summary = inputs.get("human_summary")
    if human_summary is not None and not isinstance(human_summary, str):
        raise ValueError("human_summary must be a string if provided")

    # --- Consistency checks ---
    if status == "approved":
        if recommendation != "proceed_to_git":
            raise ValueError(
                f"status is 'approved' but recommendation is {recommendation!r}; "
                f"must be 'proceed_to_git'"
            )
        for i, finding in enumerate(findings):
            sev = finding["severity"]
            if sev in ("high", "critical"):
                raise ValueError(
                    f"status is 'approved' but findings[{i}].severity is {sev!r}; "
                    f"approved reports must not contain high or critical findings"
                )
        for pc_item in policy_compliance:
            if pc_item["status"] == "failed":
                raise ValueError(
                    f"status is 'approved' but policy_ref {pc_item['policy_ref']!r} "
                    f"has status 'failed'"
                )

    if status == "blocked":
        if recommendation != "stop":
            raise ValueError(
                f"status is 'blocked' but recommendation is {recommendation!r}; "
                f"must be 'stop'"
            )

    if status == "changes_requested":
        if recommendation not in ("fix_required", "ask_user"):
            raise ValueError(
                f"status is 'changes_requested' but recommendation is "
                f"{recommendation!r}; must be 'fix_required' or 'ask_user'"
            )

    if status == "approved_with_risks":
        if residual_risks is None or len(residual_risks) < 1:
            raise ValueError(
                "status is 'approved_with_risks' but residual_risks is missing or empty"
            )

    # --- Build deterministic artifact fields ---
    report_id = _generate_deterministic_id(inputs)
    created_at = _generate_deterministic_created_at(inputs)

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "review_report",
        "contract_version": "2.0",
        "report_id": report_id,
        "implementation_report_id": implementation_report_id,
        "test_report_id": test_report_id,
        "created_at": created_at,
        "status": status,
        "findings": findings,
        "policy_compliance": policy_compliance,
        "recommendation": recommendation,
    }

    if residual_risks is not None:
        artifact["residual_risks"] = residual_risks
    if required_fixes is not None:
        artifact["required_fixes"] = required_fixes
    if approved_with_notes is not None:
        artifact["approved_with_notes"] = approved_with_notes
    if human_summary is not None:
        artifact["human_summary"] = human_summary

    # --- Validate against review_report schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Review report artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return artifact
