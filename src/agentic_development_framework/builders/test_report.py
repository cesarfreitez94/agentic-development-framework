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
    / "test_report.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "TEST-"

_IMPL_REPORT_ID_RE = r"^IMPL-[0-9]{8}-[0-9]{3}$"

_VALID_STATUSES = frozenset({"passed", "failed", "partial", "not_run"})
_VALID_TEST_RUN_STATUSES = frozenset({"passed", "failed", "skipped"})
_VALID_TEST_RUN_KINDS = frozenset(
    {"pytest", "jsonschema", "lint", "security", "custom"}
)

_TEST_RUN_KEYS = frozenset({"command", "status", "exit_code", "kind"})
_FAILURE_KEYS = frozenset({"test_name", "message", "path", "line"})
_COVERAGE_KEYS = frozenset({"required", "satisfied", "details"})
_ENVIRONMENT_KEYS = frozenset({"runtime", "os", "python_version"})
_PERFORMANCE_KEYS = frozenset({"duration_ms", "memory_mb"})


def _validate_non_empty_string(value: object, label: str) -> None:
    if not isinstance(value, str) or len(value) < 1:
        raise ValueError(f"{label} must be a non-empty string")


def _validate_test_runs(test_runs: object) -> None:
    if not isinstance(test_runs, list):
        raise ValueError("test_runs must be a list")
    if len(test_runs) < 1:
        raise ValueError("test_runs must have at least 1 item(s)")

    seen_commands: set[str] = set()
    for i, item in enumerate(test_runs):
        if not isinstance(item, dict):
            raise ValueError(f"test_runs[{i}] must be a dict")

        for key in ("command", "status", "exit_code"):
            if key not in item:
                raise ValueError(f"test_runs[{i}] must have a {key!r} key")

        extra = set(item.keys()) - _TEST_RUN_KEYS
        if extra:
            raise ValueError(
                f"test_runs[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        command = item["command"]
        _validate_non_empty_string(command, f"test_runs[{i}].command")

        if command in seen_commands:
            raise ValueError(
                f"Duplicate test_run command {command!r} in test_runs"
            )
        seen_commands.add(command)

        status = item["status"]
        if status not in _VALID_TEST_RUN_STATUSES:
            raise ValueError(
                f"test_runs[{i}].status {status!r} must be one of: "
                f"{', '.join(sorted(_VALID_TEST_RUN_STATUSES))}"
            )

        exit_code = item["exit_code"]
        if not isinstance(exit_code, int):
            raise ValueError(
                f"test_runs[{i}].exit_code must be an integer"
            )
        if exit_code < 0:
            raise ValueError(
                f"test_runs[{i}].exit_code must be >= 0"
            )

        kind = item.get("kind")
        if kind is not None and kind not in _VALID_TEST_RUN_KINDS:
            raise ValueError(
                f"test_runs[{i}].kind {kind!r} must be one of: "
                f"{', '.join(sorted(_VALID_TEST_RUN_KINDS))}"
            )


def _validate_failures(failures: object) -> None:
    if not isinstance(failures, list):
        raise ValueError("failures must be a list")

    seen_pairs: set[tuple[str, str]] = set()
    for i, item in enumerate(failures):
        if not isinstance(item, dict):
            raise ValueError(f"failures[{i}] must be a dict")

        for key in ("test_name", "message"):
            if key not in item:
                raise ValueError(f"failures[{i}] must have a {key!r} key")

        extra = set(item.keys()) - _FAILURE_KEYS
        if extra:
            raise ValueError(
                f"failures[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        test_name = item["test_name"]
        _validate_non_empty_string(test_name, f"failures[{i}].test_name")

        message = item["message"]
        _validate_non_empty_string(message, f"failures[{i}].message")

        path_val = item.get("path")
        if path_val is not None and not isinstance(path_val, str):
            raise ValueError(f"failures[{i}].path must be a string if provided")

        line_val = item.get("line")
        if line_val is not None:
            if not isinstance(line_val, int) or line_val < 1:
                raise ValueError(f"failures[{i}].line must be an integer >= 1 if provided")

        pair = (test_name, message)
        if pair in seen_pairs:
            raise ValueError(
                f"Duplicate failure (test_name={test_name!r}, "
                f"message={message!r}) in failures"
            )
        seen_pairs.add(pair)


def _validate_coverage(coverage: object) -> None:
    if not isinstance(coverage, dict):
        raise ValueError("coverage must be a dict")

    for key in ("required", "satisfied"):
        if key not in coverage:
            raise ValueError(f"coverage must have a {key!r} key")

    extra = set(coverage.keys()) - _COVERAGE_KEYS
    if extra:
        raise ValueError(
            f"coverage has extra keys: {', '.join(sorted(extra))}"
        )

    if not isinstance(coverage["required"], bool):
        raise ValueError("coverage.required must be a boolean")

    if not isinstance(coverage["satisfied"], bool):
        raise ValueError("coverage.satisfied must be a boolean")

    details = coverage.get("details")
    if details is not None and not isinstance(details, str):
        raise ValueError("coverage.details must be a string if provided")


def _validate_environment(environment: object) -> None:
    if not isinstance(environment, dict):
        raise ValueError("environment must be a dict if provided")

    extra = set(environment.keys()) - _ENVIRONMENT_KEYS
    if extra:
        raise ValueError(
            f"environment has extra keys: {', '.join(sorted(extra))}"
        )

    for key in ("runtime", "os", "python_version"):
        value = environment.get(key)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"environment.{key} must be a string if provided")


def _validate_performance(performance: object) -> None:
    if not isinstance(performance, dict):
        raise ValueError("performance must be a dict if provided")

    extra = set(performance.keys()) - _PERFORMANCE_KEYS
    if extra:
        raise ValueError(
            f"performance has extra keys: {', '.join(sorted(extra))}"
        )

    duration_ms = performance.get("duration_ms")
    if duration_ms is not None:
        if not isinstance(duration_ms, int) or duration_ms < 0:
            raise ValueError(
                "performance.duration_ms must be an integer >= 0 if provided"
            )

    memory_mb = performance.get("memory_mb")
    if memory_mb is not None:
        if not isinstance(memory_mb, (int, float)) or memory_mb < 0:
            raise ValueError(
                "performance.memory_mb must be a number >= 0 if provided"
            )


def _validate_string_list_no_duplicates(
    value: object, label: str
) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    seen: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, str) or len(item) < 1:
            raise ValueError(f"{label}[{i}] must be a non-empty string")
        if item in seen:
            raise ValueError(f"Duplicate value {item!r} in {label}")
        seen.add(item)


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


def build_test_report(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build a test_report artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            implementation_report_id (str, required): ID matching ^IMPL-[0-9]{8}-[0-9]{3}$.
            status (str, required): One of "passed", "failed", "partial", "not_run".
            test_runs (list[dict], required): Non-empty list of test run entries.
            failures (list[dict], required): List of failure entries.
            coverage (dict, required): Coverage info with required/satisfied booleans.
            skipped_tests (list[str], optional): List of skipped test names.
            environment (dict, optional): Runtime environment info.
            performance (dict, optional): Performance metrics.
            not_run_reason (str, optional): Reason if status is "not_run".
            human_summary (str, optional): Human-readable summary.
        output_path: Optional filesystem path. If provided, writes JSON artifact.

    Returns:
        Dict representing the complete, schema-valid test_report artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.
    """
    # --- Validate required inputs ---
    required = {
        "implementation_report_id",
        "status",
        "test_runs",
        "failures",
        "coverage",
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

    status = inputs["status"]
    if status not in _VALID_STATUSES:
        raise ValueError(
            f"Invalid status {status!r}, must be one of: "
            f"{', '.join(sorted(_VALID_STATUSES))}"
        )

    test_runs = inputs["test_runs"]
    _validate_test_runs(test_runs)

    failures = inputs["failures"]
    _validate_failures(failures)

    coverage = inputs["coverage"]
    _validate_coverage(coverage)

    # --- Consistency checks ---
    test_run_statuses = [tr["status"] for tr in test_runs]

    if status == "passed":
        if len(failures) > 0:
            raise ValueError(
                "status is 'passed' but failures is non-empty; "
                "failures must be empty when status is passed"
            )
        for i, tr_status in enumerate(test_run_statuses):
            if tr_status == "failed":
                raise ValueError(
                    f"status is 'passed' but test_runs[{i}].status is 'failed'"
                )

    if status == "failed":
        if not any(tr_status == "failed" for tr_status in test_run_statuses):
            raise ValueError(
                "status is 'failed' but no test_run has status 'failed'"
            )

    if status == "not_run":
        for i, tr_status in enumerate(test_run_statuses):
            if tr_status != "skipped":
                raise ValueError(
                    f"status is 'not_run' but test_runs[{i}].status is "
                    f"{tr_status!r}, must be 'skipped'"
                )

    # --- Validate optional inputs ---
    skipped_tests = inputs.get("skipped_tests")
    if skipped_tests is not None:
        _validate_string_list_no_duplicates(skipped_tests, "skipped_tests")

    environment = inputs.get("environment")
    if environment is not None:
        _validate_environment(environment)

    performance = inputs.get("performance")
    if performance is not None:
        _validate_performance(performance)

    not_run_reason = inputs.get("not_run_reason")
    if not_run_reason is not None and not isinstance(not_run_reason, str):
        raise ValueError("not_run_reason must be a string if provided")

    human_summary = inputs.get("human_summary")
    if human_summary is not None and not isinstance(human_summary, str):
        raise ValueError("human_summary must be a string if provided")

    # --- Build deterministic artifact fields ---
    report_id = _generate_deterministic_id(inputs)
    created_at = _generate_deterministic_created_at(inputs)

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "test_report",
        "contract_version": "2.0",
        "report_id": report_id,
        "implementation_report_id": implementation_report_id,
        "created_at": created_at,
        "status": status,
        "test_runs": test_runs,
        "failures": failures,
        "coverage": coverage,
    }

    if skipped_tests is not None:
        artifact["skipped_tests"] = skipped_tests
    if environment is not None:
        artifact["environment"] = environment
    if performance is not None:
        artifact["performance"] = performance
    if not_run_reason is not None:
        artifact["not_run_reason"] = not_run_reason
    if human_summary is not None:
        artifact["human_summary"] = human_summary

    # --- Validate against test_report schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Test report artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return artifact
