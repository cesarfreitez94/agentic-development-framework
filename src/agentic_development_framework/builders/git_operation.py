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
    / "git_operation.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "GIT-"

_VALID_PRODUCED_BY = frozenset({"orchestrator", "review_gate"})
_EXECUTED_BY = "git_operator"
_VALID_OPERATION_TYPES = frozenset(
    {"status_check", "create_branch", "commit", "push", "open_pr", "merge_pr"}
)
_VALID_STATUSES = frozenset({"requested", "executed", "failed", "cancelled"})
_VALID_POLICY_STATUSES = frozenset({"passed", "failed", "not_applicable"})

_REVIEW_REPORT_ID_RE = re.compile(r"^REV-[0-9]{8}-[0-9]{3}$")
_IMPL_REPORT_ID_RE = re.compile(r"^IMPL-[0-9]{8}-[0-9]{3}$")
_TEST_REPORT_ID_RE = re.compile(r"^TEST-[0-9]{8}-[0-9]{3}$")
_DECISION_ID_RE = re.compile(r"^DEC-[0-9]{8}-[0-9]{3}$")
_PLAN_ID_RE = re.compile(r"^PLAN-[0-9]{8}-[0-9]{3}$")
_TASK_PACKET_ID_RE = re.compile(r"^TPACKET-[0-9]{8}-[0-9]{3}$")

_SOURCE_REFS_KEYS = frozenset(
    {
        "review_report_id",
        "implementation_report_id",
        "test_report_id",
        "decision_id",
        "plan_id",
        "task_packet_id",
    }
)
_BRANCH_KEYS = frozenset({"current", "base", "target"})
_POLICY_CHECK_KEYS = frozenset({"policy_ref", "status", "details"})
_COMMIT_KEYS = frozenset({"sha", "message", "issue_ref"})
_PULL_REQUEST_KEYS = frozenset({"number", "url", "title"})
_RESULT_KEYS = frozenset({"summary", "exit_code", "details"})


def _validate_non_empty_string(value: object, label: str) -> None:
    if not isinstance(value, str) or len(value) < 1:
        raise ValueError(f"{label} must be a non-empty string")


def _validate_source_refs(source_refs: object) -> None:
    if not isinstance(source_refs, dict):
        raise ValueError("source_refs must be a dict")

    if "review_report_id" not in source_refs:
        raise ValueError("source_refs must have a 'review_report_id' key")

    extra = set(source_refs.keys()) - _SOURCE_REFS_KEYS
    if extra:
        raise ValueError(
            f"source_refs has extra keys: {', '.join(sorted(extra))}"
        )

    review_report_id = source_refs["review_report_id"]
    _validate_non_empty_string(review_report_id, "source_refs.review_report_id")
    if not _REVIEW_REPORT_ID_RE.match(review_report_id):
        raise ValueError(
            f"source_refs.review_report_id {review_report_id!r} must match pattern "
            f"'^REV-[0-9]{{8}}-[0-9]{{3}}$'"
        )

    optional_refs = [
        ("implementation_report_id", _IMPL_REPORT_ID_RE),
        ("test_report_id", _TEST_REPORT_ID_RE),
        ("decision_id", _DECISION_ID_RE),
        ("plan_id", _PLAN_ID_RE),
        ("task_packet_id", _TASK_PACKET_ID_RE),
    ]
    for key, pattern in optional_refs:
        value = source_refs.get(key)
        if value is not None:
            _validate_non_empty_string(value, f"source_refs.{key}")
            if not pattern.match(value):
                raise ValueError(
                    f"source_refs.{key} {value!r} must match pattern "
                    f"{pattern.pattern!r}"
                )


def _validate_branch(branch: object) -> None:
    if not isinstance(branch, dict):
        raise ValueError("branch must be a dict")

    for key in ("current", "base"):
        if key not in branch:
            raise ValueError(f"branch must have a {key!r} key")

    extra = set(branch.keys()) - _BRANCH_KEYS
    if extra:
        raise ValueError(
            f"branch has extra keys: {', '.join(sorted(extra))}"
        )

    current = branch["current"]
    _validate_non_empty_string(current, "branch.current")

    base = branch["base"]
    _validate_non_empty_string(base, "branch.base")

    target = branch.get("target")
    if target is not None:
        _validate_non_empty_string(target, "branch.target")


def _validate_policy_checks(policy_checks: object) -> None:
    if not isinstance(policy_checks, list):
        raise ValueError("policy_checks must be a list")
    if len(policy_checks) < 1:
        raise ValueError("policy_checks must have at least 1 item(s)")

    seen_policy_refs: set[str] = set()
    for i, item in enumerate(policy_checks):
        if not isinstance(item, dict):
            raise ValueError(f"policy_checks[{i}] must be a dict")

        for key in ("policy_ref", "status"):
            if key not in item:
                raise ValueError(f"policy_checks[{i}] must have a {key!r} key")

        extra = set(item.keys()) - _POLICY_CHECK_KEYS
        if extra:
            raise ValueError(
                f"policy_checks[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        policy_ref = item["policy_ref"]
        _validate_non_empty_string(policy_ref, f"policy_checks[{i}].policy_ref")

        if policy_ref in seen_policy_refs:
            raise ValueError(
                f"Duplicate policy_ref {policy_ref!r} in policy_checks"
            )
        seen_policy_refs.add(policy_ref)

        status = item["status"]
        if status not in _VALID_POLICY_STATUSES:
            raise ValueError(
                f"policy_checks[{i}].status {status!r} must be one of: "
                f"{', '.join(sorted(_VALID_POLICY_STATUSES))}"
            )

        details = item.get("details")
        if details is not None and not isinstance(details, str):
            raise ValueError(
                f"policy_checks[{i}].details must be a string if provided"
            )


def _validate_commit(commit: object) -> None:
    if not isinstance(commit, dict):
        raise ValueError("commit must be a dict if provided")

    extra = set(commit.keys()) - _COMMIT_KEYS
    if extra:
        raise ValueError(
            f"commit has extra keys: {', '.join(sorted(extra))}"
        )

    sha = commit.get("sha")
    if sha is not None:
        _validate_non_empty_string(sha, "commit.sha")

    message = commit.get("message")
    if message is not None:
        _validate_non_empty_string(message, "commit.message")

    issue_ref = commit.get("issue_ref")
    if issue_ref is not None:
        _validate_non_empty_string(issue_ref, "commit.issue_ref")


def _validate_pull_request(pull_request: object) -> None:
    if not isinstance(pull_request, dict):
        raise ValueError("pull_request must be a dict if provided")

    extra = set(pull_request.keys()) - _PULL_REQUEST_KEYS
    if extra:
        raise ValueError(
            f"pull_request has extra keys: {', '.join(sorted(extra))}"
        )

    number = pull_request.get("number")
    if number is not None:
        if not isinstance(number, int) or number < 1:
            raise ValueError("pull_request.number must be an integer >= 1 if provided")

    url = pull_request.get("url")
    if url is not None:
        _validate_non_empty_string(url, "pull_request.url")

    title = pull_request.get("title")
    if title is not None:
        _validate_non_empty_string(title, "pull_request.title")


def _validate_result(result: object) -> None:
    if not isinstance(result, dict):
        raise ValueError("result must be a dict if provided")

    extra = set(result.keys()) - _RESULT_KEYS
    if extra:
        raise ValueError(
            f"result has extra keys: {', '.join(sorted(extra))}"
        )

    summary = result.get("summary")
    if summary is not None and not isinstance(summary, str):
        raise ValueError("result.summary must be a string if provided")

    exit_code = result.get("exit_code")
    if exit_code is not None and not isinstance(exit_code, int):
        raise ValueError("result.exit_code must be an integer if provided")

    details = result.get("details")
    if details is not None and not isinstance(details, str):
        raise ValueError("result.details must be a string if provided")


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


def build_git_operation(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build a git_operation artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            produced_by (str, required): One of "orchestrator", "review_gate".
            executed_by (str, required): Must be "git_operator".
            operation_type (str, required): One of "status_check", "create_branch",
                "commit", "push", "open_pr", "merge_pr".
            status (str, required): One of "requested", "executed", "failed",
                "cancelled".
            source_refs (dict, required): Dict with required review_report_id
                matching ^REV-[0-9]{8}-[0-9]{3}$ and optional
                implementation_report_id, test_report_id, decision_id, plan_id,
                task_packet_id.
            branch (dict, required): Dict with required current and base
                (non-empty strings) and optional target.
            policy_checks (list[dict], required): Non-empty list of policy check
                entries, each with policy_ref and status.
            commit (dict, optional): Dict with optional sha, message, issue_ref.
            pull_request (dict, optional): Dict with optional number, url, title.
            remote (str, optional): Remote name.
            requires_user_confirmation (bool, optional): Whether user confirmation
                is required.
            result (dict, optional): Dict with optional summary, exit_code, details.
            execution_notes (str, optional): Execution notes.
            human_summary (str, optional): Human-readable summary.
        output_path: Optional filesystem path. If provided, writes JSON artifact.

    Returns:
        Dict representing the complete, schema-valid git_operation artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.
    """
    # --- Validate required inputs ---
    required = {
        "produced_by",
        "executed_by",
        "operation_type",
        "status",
        "source_refs",
        "branch",
        "policy_checks",
    }
    for key in sorted(required):
        if key not in inputs:
            raise ValueError(f"Missing required input: {key!r}")

    produced_by = inputs["produced_by"]
    _validate_non_empty_string(produced_by, "produced_by")
    if produced_by not in _VALID_PRODUCED_BY:
        raise ValueError(
            f"Invalid produced_by {produced_by!r}, must be one of: "
            f"{', '.join(sorted(_VALID_PRODUCED_BY))}"
        )

    executed_by = inputs["executed_by"]
    _validate_non_empty_string(executed_by, "executed_by")
    if executed_by != _EXECUTED_BY:
        raise ValueError(
            f"Invalid executed_by {executed_by!r}, must be {_EXECUTED_BY!r}"
        )

    operation_type = inputs["operation_type"]
    _validate_non_empty_string(operation_type, "operation_type")
    if operation_type not in _VALID_OPERATION_TYPES:
        raise ValueError(
            f"Invalid operation_type {operation_type!r}, must be one of: "
            f"{', '.join(sorted(_VALID_OPERATION_TYPES))}"
        )

    status = inputs["status"]
    _validate_non_empty_string(status, "status")
    if status not in _VALID_STATUSES:
        raise ValueError(
            f"Invalid status {status!r}, must be one of: "
            f"{', '.join(sorted(_VALID_STATUSES))}"
        )

    source_refs = inputs["source_refs"]
    _validate_source_refs(source_refs)

    branch = inputs["branch"]
    _validate_branch(branch)

    policy_checks = inputs["policy_checks"]
    _validate_policy_checks(policy_checks)

    # --- Validate optional inputs ---
    commit = inputs.get("commit")
    if commit is not None:
        _validate_commit(commit)

    pull_request = inputs.get("pull_request")
    if pull_request is not None:
        _validate_pull_request(pull_request)

    remote = inputs.get("remote")
    if remote is not None and not isinstance(remote, str):
        raise ValueError("remote must be a string if provided")

    requires_user_confirmation = inputs.get("requires_user_confirmation")
    if requires_user_confirmation is not None and not isinstance(
        requires_user_confirmation, bool
    ):
        raise ValueError(
            "requires_user_confirmation must be a boolean if provided"
        )

    result = inputs.get("result")
    if result is not None:
        _validate_result(result)

    execution_notes = inputs.get("execution_notes")
    if execution_notes is not None and not isinstance(execution_notes, str):
        raise ValueError("execution_notes must be a string if provided")

    human_summary = inputs.get("human_summary")
    if human_summary is not None and not isinstance(human_summary, str):
        raise ValueError("human_summary must be a string if provided")

    # --- Consistency checks ---
    # Failed policy checks should not allow executed status
    has_failed_policy = any(
        pc["status"] == "failed" for pc in policy_checks
    )
    if has_failed_policy and status == "executed":
        raise ValueError(
            "status cannot be 'executed' when any policy_check has status 'failed'"
        )

    # operation_type commit should require commit.message
    if operation_type == "commit":
        if commit is None or commit.get("message") is None:
            raise ValueError(
                "operation_type 'commit' requires commit.message"
            )

    # operation_type push should require remote
    if operation_type == "push":
        if remote is None:
            raise ValueError("operation_type 'push' requires remote")

    # operation_type open_pr or merge_pr should require pull_request
    if operation_type in ("open_pr", "merge_pr"):
        if pull_request is None:
            raise ValueError(
                f"operation_type {operation_type!r} requires pull_request"
            )

    # operation_type merge_pr should require pull_request.number
    if operation_type == "merge_pr":
        if pull_request is not None and pull_request.get("number") is None:
            raise ValueError(
                "operation_type 'merge_pr' requires pull_request.number"
            )

    # status requested should not include result
    if status == "requested" and result is not None:
        raise ValueError(
            "result must not be provided when status is 'requested'"
        )

    # --- Build deterministic artifact fields ---
    operation_id = _generate_deterministic_id(inputs)
    created_at = _generate_deterministic_created_at(inputs)

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "git_operation",
        "contract_version": "2.0",
        "operation_id": operation_id,
        "created_at": created_at,
        "produced_by": produced_by,
        "executed_by": executed_by,
        "operation_type": operation_type,
        "status": status,
        "source_refs": source_refs,
        "branch": branch,
        "policy_checks": policy_checks,
    }

    if commit is not None:
        artifact["commit"] = commit
    if pull_request is not None:
        artifact["pull_request"] = pull_request
    if remote is not None:
        artifact["remote"] = remote
    if requires_user_confirmation is not None:
        artifact["requires_user_confirmation"] = requires_user_confirmation
    if result is not None:
        artifact["result"] = result
    if execution_notes is not None:
        artifact["execution_notes"] = execution_notes
    if human_summary is not None:
        artifact["human_summary"] = human_summary

    # --- Validate against git_operation schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Git operation artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return artifact
