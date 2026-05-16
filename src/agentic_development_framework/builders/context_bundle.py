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
    / "context_bundle.schema.json"
)

_BASE_EPOCH = datetime(2024, 1, 1, tzinfo=timezone.utc)

_ID_PREFIX = "CTX-"

_PACKET_ID_RE = r"^TPACKET-[0-9]{8}-[0-9]{3}$"

_VALID_CONTEXT_ITEM_TYPES = frozenset(
    {
        "schema",
        "policy",
        "roadmap",
        "state",
        "source_file",
        "test_file",
        "decision",
        "git",
    }
)

_CONTEXT_ITEM_KEYS = frozenset({"type", "path", "section", "line_ranges", "reason"})
_EXCLUDED_CONTEXT_KEYS = frozenset({"path", "section", "line_ranges", "reason"})
_INTEGRITY_KEYS = frozenset({"source_count", "truncated"})


def _validate_non_empty_string(value: object, label: str) -> None:
    if not isinstance(value, str) or len(value) < 1:
        raise ValueError(f"{label} must be a non-empty string")


def _validate_string_list(value: object, label: str, min_items: int = 0) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    if len(value) < min_items:
        raise ValueError(f"{label} must have at least {min_items} item(s)")
    for i, item in enumerate(value):
        if not isinstance(item, str) or len(item) < 1:
            raise ValueError(f"{label}[{i}] must be a non-empty string")


def _validate_line_ranges(line_ranges: object, label: str) -> None:
    if not isinstance(line_ranges, list):
        raise ValueError(f"{label} must be a list")
    if len(line_ranges) < 1:
        raise ValueError(f"{label} must have at least 1 item(s)")
    for i, lr in enumerate(line_ranges):
        if not isinstance(lr, dict):
            raise ValueError(f"{label}[{i}] must be a dict")
        for key in ("start", "end"):
            if key not in lr:
                raise ValueError(f"{label}[{i}] must have a {key!r} key")
        extra = set(lr.keys()) - {"start", "end"}
        if extra:
            raise ValueError(
                f"{label}[{i}] has extra keys: {', '.join(sorted(extra))}"
            )
        start = lr["start"]
        end = lr["end"]
        if not isinstance(start, int):
            raise ValueError(f"{label}[{i}].start must be an integer")
        if not isinstance(end, int):
            raise ValueError(f"{label}[{i}].end must be an integer")
        if start < 1:
            raise ValueError(f"{label}[{i}].start must be >= 1")
        if end < 1:
            raise ValueError(f"{label}[{i}].end must be >= 1")
        if start > end:
            raise ValueError(f"{label}[{i}].start must be <= end")


def _validate_context_items(context_items: object) -> None:
    if not isinstance(context_items, list):
        raise ValueError("context_items must be a list")
    if len(context_items) < 1:
        raise ValueError("context_items must have at least 1 item(s)")

    seen_triples: set[str] = set()
    for i, item in enumerate(context_items):
        if not isinstance(item, dict):
            raise ValueError(f"context_items[{i}] must be a dict")

        for key in ("type", "path", "line_ranges", "reason"):
            if key not in item:
                raise ValueError(f"context_items[{i}] must have a {key!r} key")

        extra = set(item.keys()) - _CONTEXT_ITEM_KEYS
        if extra:
            raise ValueError(
                f"context_items[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        item_type = item["type"]
        if item_type not in _VALID_CONTEXT_ITEM_TYPES:
            raise ValueError(
                f"context_items[{i}].type {item_type!r} must be one of: "
                + ", ".join(sorted(_VALID_CONTEXT_ITEM_TYPES))
            )

        item_path = item["path"]
        _validate_non_empty_string(item_path, f"context_items[{i}].path")

        section = item.get("section")
        if section is not None and not isinstance(section, str):
            raise ValueError(f"context_items[{i}].section must be a string if provided")

        line_ranges = item["line_ranges"]
        _validate_line_ranges(line_ranges, f"context_items[{i}].line_ranges")

        item_reason = item["reason"]
        _validate_non_empty_string(item_reason, f"context_items[{i}].reason")

        triple_key = json.dumps(
            (item_type, item_path, line_ranges), sort_keys=True, ensure_ascii=True
        )
        if triple_key in seen_triples:
            raise ValueError(
                f"Duplicate context item (type={item_type!r}, path={item_path!r}) "
                f"in context_items"
            )
        seen_triples.add(triple_key)


def _validate_excluded_context(excluded_context: object) -> None:
    if not isinstance(excluded_context, list):
        raise ValueError("excluded_context must be a list")
    for i, item in enumerate(excluded_context):
        if not isinstance(item, dict):
            raise ValueError(f"excluded_context[{i}] must be a dict")

        for key in ("path", "reason"):
            if key not in item:
                raise ValueError(f"excluded_context[{i}] must have a {key!r} key")

        extra = set(item.keys()) - _EXCLUDED_CONTEXT_KEYS
        if extra:
            raise ValueError(
                f"excluded_context[{i}] has extra keys: {', '.join(sorted(extra))}"
            )

        item_path = item["path"]
        _validate_non_empty_string(item_path, f"excluded_context[{i}].path")

        section = item.get("section")
        if section is not None and not isinstance(section, str):
            raise ValueError(
                f"excluded_context[{i}].section must be a string if provided"
            )

        line_ranges = item.get("line_ranges")
        if line_ranges is not None:
            _validate_line_ranges(
                line_ranges, f"excluded_context[{i}].line_ranges"
            )

        item_reason = item["reason"]
        _validate_non_empty_string(item_reason, f"excluded_context[{i}].reason")


def _validate_integrity(integrity: object) -> None:
    if not isinstance(integrity, dict):
        raise ValueError("integrity must be a dict")

    for key in ("source_count", "truncated"):
        if key not in integrity:
            raise ValueError(f"integrity must have a {key!r} key")

    extra = set(integrity.keys()) - _INTEGRITY_KEYS
    if extra:
        raise ValueError(
            f"integrity has extra keys: {', '.join(sorted(extra))}"
        )

    source_count = integrity["source_count"]
    if not isinstance(source_count, int):
        raise ValueError("integrity.source_count must be an integer")
    if source_count < 0:
        raise ValueError("integrity.source_count must be >= 0")

    truncated = integrity["truncated"]
    if not isinstance(truncated, bool):
        raise ValueError("integrity.truncated must be a boolean")


def _check_no_duplicate_policy_refs(value: list[str], label: str) -> None:
    seen: set[str] = set()
    for item in value:
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


def build_context_bundle(
    inputs: dict[str, object], output_path: Optional[str] = None
) -> dict[str, object]:
    """Build a context_bundle artifact from typed inputs.

    Args:
        inputs: Typed dict with keys:
            packet_id (str, required): Packet ID matching ^TPACKET-[0-9]{8}-[0-9]{3}$.
            context_items (list[dict], required): Non-empty list of context items.
            excluded_context (list[dict], required): List of excluded context items.
            policy_refs (list[str], required): Non-empty list of policy references.
            integrity (dict, required): Integrity metadata with source_count and truncated.
            human_summary (str, optional): Human-readable summary.
        output_path: Optional filesystem path. If provided, writes JSON artifact.

    Returns:
        Dict representing the complete, schema-valid context_bundle artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.
    """
    # --- Validate required inputs ---
    required = {
        "packet_id",
        "context_items",
        "excluded_context",
        "policy_refs",
        "integrity",
    }
    for key in sorted(required):
        if key not in inputs:
            raise ValueError(f"Missing required input: {key!r}")

    packet_id = inputs["packet_id"]
    _validate_non_empty_string(packet_id, "packet_id")
    if not re.match(_PACKET_ID_RE, packet_id):
        raise ValueError(
            f"packet_id {packet_id!r} must match pattern {_PACKET_ID_RE}"
        )

    context_items = inputs["context_items"]
    _validate_context_items(context_items)

    excluded_context = inputs["excluded_context"]
    _validate_excluded_context(excluded_context)

    policy_refs = inputs["policy_refs"]
    _validate_string_list(policy_refs, "policy_refs", min_items=1)
    _check_no_duplicate_policy_refs(policy_refs, "policy_refs")

    integrity = inputs["integrity"]
    _validate_integrity(integrity)

    # --- Consistency checks ---
    if integrity["source_count"] != len(context_items):
        raise ValueError(
            f"integrity.source_count ({integrity['source_count']}) "
            f"does not match len(context_items) ({len(context_items)})"
        )

    # --- Validate optional inputs ---
    human_summary = inputs.get("human_summary")
    if human_summary is not None and not isinstance(human_summary, str):
        raise ValueError("human_summary must be a string if provided")

    # --- Build deterministic artifact fields ---
    bundle_id = _generate_deterministic_id(inputs)
    created_at = _generate_deterministic_created_at(inputs)

    # --- Assemble artifact ---
    artifact: dict[str, object] = {
        "contract_name": "context_bundle",
        "contract_version": "2.0",
        "bundle_id": bundle_id,
        "packet_id": packet_id,
        "created_at": created_at,
        "context_items": context_items,
        "excluded_context": excluded_context,
        "policy_refs": policy_refs,
        "integrity": integrity,
    }

    if human_summary is not None:
        artifact["human_summary"] = human_summary

    # --- Validate against context_bundle schema ---
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=artifact, schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(
            f"Context bundle artifact failed schema validation: {exc.message}"
        ) from exc

    # --- Write output if path provided ---
    if output_path is not None:
        output_file = Path(output_path)
        output_file.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return artifact
