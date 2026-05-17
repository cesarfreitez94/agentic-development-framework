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
    / "schema_catalog.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "SCAT-"

_CONTRACT_REQUIRED_KEYS = frozenset(
    {"contract_name", "contract_version", "path", "status"}
)
_CONTRACT_ALLOWED_KEYS = frozenset(
    {
        "contract_name",
        "contract_version",
        "path",
        "status",
        "owner",
        "consumers",
        "depends_on",
    }
)

_POLICY_REQUIRED_KEYS = frozenset({"policy_id", "path", "mode"})
_POLICY_ALLOWED_KEYS = frozenset({"policy_id", "path", "mode"})

_COMPATIBILITY_REQUIRED_KEYS = frozenset({"from", "to", "status"})
_COMPATIBILITY_ALLOWED_KEYS = frozenset({"from", "to", "status", "notes"})

_VALID_CONTRACT_STATUSES = frozenset({"active", "deprecated", "experimental"})
_VALID_COMPATIBILITY_STATUSES = frozenset(
    {"compatible", "requires_migration", "incompatible"}
)

_CONTRACT_PATH_RE = re.compile(r"^schemas/meta/[a-z0-9_.-]+\.json$")
_COMPATIBILITY_REF_RE = re.compile(r"^[a-z0-9_]+@[0-9]+\.[0-9]+$")


def _validate_non_empty_string(value: object, label: str) -> None:
    if not isinstance(value, str) or len(value) < 1:
        raise ValueError(f"{label} must be a non-empty string")


def _generate_deterministic_id(inputs: dict[str, object]) -> str:
    stable = json.dumps(inputs, sort_keys=True, default=str, ensure_ascii=True)
    digest = hashlib.sha256(stable.encode("utf-8")).digest()
    numeric = int.from_bytes(digest[:11], "big")
    part1 = numeric % (10**8)
    part2 = (numeric // (10**8)) % (10**3)
    return f"{_ID_PREFIX}{part1:08d}-{part2:03d}"


def _generate_deterministic_updated_at(inputs: dict[str, object]) -> str:
    stable = json.dumps(inputs, sort_keys=True, default=str, ensure_ascii=True)
    digest = hashlib.sha256(stable.encode("utf-8")).digest()
    seconds_offset = int.from_bytes(digest[:4], "big") % (365 * 24 * 60 * 60)
    created = _BASE_EPOCH + timedelta(seconds=seconds_offset)
    return created.isoformat()


def _validate_contracts(value: object) -> set[str]:
    """Validate contracts list, returns set of 'contract_name@contract_version' refs."""
    if not isinstance(value, list):
        raise ValueError("contracts must be a list")
    if len(value) < 1:
        raise ValueError("contracts must be a non-empty list")

    seen_identities: set[tuple[str, str]] = set()
    seen_paths: set[str] = set()
    refs: set[str] = set()

    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"contracts[{i}] must be a dict")

        missing = _CONTRACT_REQUIRED_KEYS - set(item.keys())
        if missing:
            raise ValueError(
                f"contracts[{i}] missing required key(s): "
                f"{', '.join(sorted(missing))}"
            )

        extra = set(item.keys()) - _CONTRACT_ALLOWED_KEYS
        if extra:
            raise ValueError(
                f"contracts[{i}] has extra key(s): {', '.join(sorted(extra))}"
            )

        contract_name = item["contract_name"]
        _validate_non_empty_string(contract_name, f"contracts[{i}].contract_name")

        contract_version = item["contract_version"]
        _validate_non_empty_string(
            contract_version, f"contracts[{i}].contract_version"
        )

        path = item["path"]
        if not isinstance(path, str) or not _CONTRACT_PATH_RE.match(path):
            raise ValueError(
                f"contracts[{i}].path {path!r} must match pattern "
                f"'^schemas/meta/[a-z0-9_.-]+\\.json$'"
            )

        status = item["status"]
        if status not in _VALID_CONTRACT_STATUSES:
            raise ValueError(
                f"contracts[{i}].status {status!r} must be one of: "
                f"{', '.join(sorted(_VALID_CONTRACT_STATUSES))}"
            )

        identity = (contract_name, contract_version)
        if identity in seen_identities:
            raise ValueError(
                f"Duplicate contract (contract_name={contract_name!r}, "
                f"contract_version={contract_version!r})"
            )
        seen_identities.add(identity)

        if path in seen_paths:
            raise ValueError(f"Duplicate contract.path {path!r}")
        seen_paths.add(path)

        ref = f"{contract_name}@{contract_version}"
        refs.add(ref)

        owner = item.get("owner")
        if owner is not None and not isinstance(owner, str):
            raise ValueError(f"contracts[{i}].owner must be a string if provided")

        consumers = item.get("consumers")
        if consumers is not None:
            if not isinstance(consumers, list):
                raise ValueError(f"contracts[{i}].consumers must be a list")
            if len(consumers) != len(set(consumers)):
                raise ValueError(
                    f"contracts[{i}].consumers must not contain duplicates"
                )
            for j, c in enumerate(consumers):
                if not isinstance(c, str) or len(c) < 1:
                    raise ValueError(
                        f"contracts[{i}].consumers[{j}] must be a non-empty string"
                    )

        depends_on = item.get("depends_on")
        if depends_on is not None:
            if not isinstance(depends_on, list):
                raise ValueError(f"contracts[{i}].depends_on must be a list")
            if len(depends_on) != len(set(depends_on)):
                raise ValueError(
                    f"contracts[{i}].depends_on must not contain duplicates"
                )
            for j, dep in enumerate(depends_on):
                if not isinstance(dep, str) or len(dep) < 1:
                    raise ValueError(
                        f"contracts[{i}].depends_on[{j}] must be a non-empty string"
                    )

    return refs


def _validate_global_policies(value: object) -> None:
    if not isinstance(value, list):
        raise ValueError("global_policies must be a list")
    if len(value) < 2:
        raise ValueError("global_policies must have at least 2 items")

    seen_ids: set[str] = set()

    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"global_policies[{i}] must be a dict")

        missing = _POLICY_REQUIRED_KEYS - set(item.keys())
        if missing:
            raise ValueError(
                f"global_policies[{i}] missing required key(s): "
                f"{', '.join(sorted(missing))}"
            )

        extra = set(item.keys()) - _POLICY_ALLOWED_KEYS
        if extra:
            raise ValueError(
                f"global_policies[{i}] has extra key(s): "
                f"{', '.join(sorted(extra))}"
            )

        policy_id = item["policy_id"]
        _validate_non_empty_string(policy_id, f"global_policies[{i}].policy_id")

        if policy_id in seen_ids:
            raise ValueError(
                f"Duplicate global_policies.policy_id {policy_id!r}"
            )
        seen_ids.add(policy_id)

        path = item["path"]
        _validate_non_empty_string(path, f"global_policies[{i}].path")

        mode = item["mode"]
        if mode != "reference":
            raise ValueError(
                f"global_policies[{i}].mode {mode!r} must be 'reference'"
            )


def _validate_compatibility_matrix(
    value: object, contract_refs: set[str]
) -> None:
    if not isinstance(value, list):
        raise ValueError("compatibility_matrix must be a list")
    if len(value) < 1:
        raise ValueError("compatibility_matrix must be a non-empty list")

    seen_pairs: set[tuple[str, str]] = set()

    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"compatibility_matrix[{i}] must be a dict")

        missing = _COMPATIBILITY_REQUIRED_KEYS - set(item.keys())
        if missing:
            raise ValueError(
                f"compatibility_matrix[{i}] missing required key(s): "
                f"{', '.join(sorted(missing))}"
            )

        extra = set(item.keys()) - _COMPATIBILITY_ALLOWED_KEYS
        if extra:
            raise ValueError(
                f"compatibility_matrix[{i}] has extra key(s): "
                f"{', '.join(sorted(extra))}"
            )

        from_ref = item["from"]
        if (
            not isinstance(from_ref, str)
            or not _COMPATIBILITY_REF_RE.match(from_ref)
        ):
            raise ValueError(
                f"compatibility_matrix[{i}].from {from_ref!r} must match "
                f"pattern '^[a-z0-9_]+@[0-9]+\\.[0-9]+$'"
            )

        if from_ref not in contract_refs:
            raise ValueError(
                f"compatibility_matrix[{i}].from {from_ref!r} does not "
                f"reference an existing contract in contracts"
            )

        to_ref = item["to"]
        if (
            not isinstance(to_ref, str)
            or not _COMPATIBILITY_REF_RE.match(to_ref)
        ):
            raise ValueError(
                f"compatibility_matrix[{i}].to {to_ref!r} must match "
                f"pattern '^[a-z0-9_]+@[0-9]+\\.[0-9]+$'"
            )

        if to_ref not in contract_refs:
            raise ValueError(
                f"compatibility_matrix[{i}].to {to_ref!r} does not "
                f"reference an existing contract in contracts"
            )

        status = item["status"]
        if status not in _VALID_COMPATIBILITY_STATUSES:
            raise ValueError(
                f"compatibility_matrix[{i}].status {status!r} must be "
                f"one of: {', '.join(sorted(_VALID_COMPATIBILITY_STATUSES))}"
            )

        pair = (from_ref, to_ref)
        if pair in seen_pairs:
            raise ValueError(
                f"Duplicate compatibility matrix pair "
                f"(from={from_ref!r}, to={to_ref!r})"
            )
        seen_pairs.add(pair)

        notes = item.get("notes")
        if notes is not None and not isinstance(notes, str):
            raise ValueError(
                f"compatibility_matrix[{i}].notes must be a string if provided"
            )


def _validate_cross_refs(
    contracts: list[dict[str, object]], contract_refs: set[str]
) -> None:
    """Validate that contract.depends_on entries reference existing contracts."""
    for i, item in enumerate(contracts):
        depends_on = item.get("depends_on")
        if depends_on is not None:
            for j, dep in enumerate(depends_on):
                if not isinstance(dep, str):
                    continue
                if dep not in contract_refs:
                    raise ValueError(
                        f"contracts[{i}].depends_on[{j}] {dep!r} does not "
                        f"reference an existing contract in contracts"
                    )


def build_schema_catalog(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build a schema_catalog artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            contracts (list[dict], required): Non-empty list of contract
                entries with keys contract_name, contract_version, path,
                status (and optional owner, consumers, depends_on).
            global_policies (list[dict], required): List of policy entries
                with keys policy_id, path, mode (at least 2 items, mode
                must be "reference").
            compatibility_matrix (list[dict], required): Non-empty list of
                compatibility entries with keys from, to, status (and
                optional notes).
            human_summary (str, optional): Human-readable summary.
        output_path: Optional filesystem path. If provided, writes JSON
            artifact.

    Returns:
        Dict representing the complete, schema-valid schema_catalog artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema
            validation.
    """
    required = {"contracts", "global_policies", "compatibility_matrix"}
    for key in sorted(required):
        if key not in inputs:
            raise ValueError(f"Missing required input: {key!r}")

    contracts = inputs["contracts"]
    contract_refs = _validate_contracts(contracts)

    global_policies = inputs["global_policies"]
    _validate_global_policies(global_policies)

    compatibility_matrix = inputs["compatibility_matrix"]
    _validate_compatibility_matrix(compatibility_matrix, contract_refs)

    _validate_cross_refs(contracts, contract_refs)

    human_summary = inputs.get("human_summary")
    if human_summary is not None:
        if not isinstance(human_summary, str):
            raise ValueError("human_summary must be a string if provided")

    catalog_id = _generate_deterministic_id(inputs)
    updated_at = _generate_deterministic_updated_at(inputs)

    artifact: dict[str, object] = {
        "contract_name": "schema_catalog",
        "contract_version": "2.0",
        "catalog_id": catalog_id,
        "updated_at": updated_at,
        "contracts": contracts,
        "global_policies": global_policies,
        "compatibility_matrix": compatibility_matrix,
    }

    if human_summary is not None:
        artifact["human_summary"] = human_summary

    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Schema catalog artifact failed schema validation: {exc.message}"
        ) from exc

    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )

    return artifact
