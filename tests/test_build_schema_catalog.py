import json
from pathlib import Path
from unittest import mock

import pytest

from agentic_development_framework.builders.schema_catalog import (
    SchemaValidationError,
    build_schema_catalog,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "meta" / "schema_catalog.schema.json"

VALID_INPUTS: dict[str, object] = {
    "contracts": [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent.schema.json",
            "status": "active",
        },
        {
            "contract_name": "plan",
            "contract_version": "2.0",
            "path": "schemas/meta/plan.schema.json",
            "status": "active",
            "owner": "coordinator",
            "depends_on": ["intent@2.0"],
        },
    ],
    "global_policies": [
        {"policy_id": "POL-001", "path": "policies/commit.gpg", "mode": "reference"},
        {"policy_id": "POL-002", "path": "policies/review.gpg", "mode": "reference"},
    ],
    "compatibility_matrix": [
        {
            "from": "intent@2.0",
            "to": "plan@2.0",
            "status": "compatible",
        },
    ],
    "human_summary": "Initial catalog of meta contracts",
}

VALID_INPUTS_NO_OPTIONAL: dict[str, object] = {
    "contracts": [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent.schema.json",
            "status": "active",
        },
        {
            "contract_name": "plan",
            "contract_version": "2.0",
            "path": "schemas/meta/plan.schema.json",
            "status": "active",
        },
    ],
    "global_policies": [
        {"policy_id": "POL-001", "path": "policies/commit.gpg", "mode": "reference"},
        {"policy_id": "POL-002", "path": "policies/review.gpg", "mode": "reference"},
    ],
    "compatibility_matrix": [
        {
            "from": "intent@2.0",
            "to": "plan@2.0",
            "status": "compatible",
        },
    ],
}

VALID_INPUTS_FULL: dict[str, object] = {
    "contracts": [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent.schema.json",
            "status": "active",
            "owner": "coordinator",
            "consumers": ["orchestrator", "planner"],
            "depends_on": [],
        },
        {
            "contract_name": "plan",
            "contract_version": "2.0",
            "path": "schemas/meta/plan.schema.json",
            "status": "active",
            "owner": "planner",
            "consumers": ["packetizer"],
            "depends_on": ["intent@2.0"],
        },
        {
            "contract_name": "task_packet",
            "contract_version": "2.0",
            "path": "schemas/meta/task_packet.schema.json",
            "status": "experimental",
            "depends_on": ["plan@2.0"],
        },
    ],
    "global_policies": [
        {"policy_id": "POL-001", "path": "policies/commit.gpg", "mode": "reference"},
        {"policy_id": "POL-002", "path": "policies/review.gpg", "mode": "reference"},
        {"policy_id": "POL-003", "path": "policies/tests.gpg", "mode": "reference"},
    ],
    "compatibility_matrix": [
        {
            "from": "intent@2.0",
            "to": "plan@2.0",
            "status": "compatible",
        },
        {
            "from": "plan@2.0",
            "to": "task_packet@2.0",
            "status": "compatible",
            "notes": "Plan must be active before task packet is generated.",
        },
        {
            "from": "intent@2.0",
            "to": "task_packet@2.0",
            "status": "compatible",
        },
    ],
    "human_summary": "Full catalog with all metadata populated.",
}


def test_build_schema_catalog_schema_valid():
    artifact = build_schema_catalog(VALID_INPUTS)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    jsonschema.validate(instance=artifact, schema=schema)


def test_build_schema_catalog_is_deterministic():
    a = build_schema_catalog(VALID_INPUTS)
    b = build_schema_catalog(VALID_INPUTS)
    c = build_schema_catalog(VALID_INPUTS)

    assert a == b == c


def test_build_schema_catalog_rejects_missing_required_input():
    for missing_key in ("contracts", "global_policies", "compatibility_matrix"):
        inputs = {k: v for k, v in VALID_INPUTS.items() if k != missing_key}
        with pytest.raises(ValueError, match=missing_key):
            build_schema_catalog(inputs)


def test_build_schema_catalog_writes_output_path(tmp_path):
    output_path = tmp_path / "schema_catalog.json"

    artifact = build_schema_catalog(VALID_INPUTS, output_path=str(output_path))

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == artifact


def test_build_schema_catalog_rejects_invalid_contracts():
    # contracts not a list
    inputs: dict[str, object] = dict(VALID_INPUTS)
    inputs["contracts"] = "not-a-list"
    with pytest.raises(ValueError, match="contracts must be a list"):
        build_schema_catalog(inputs)

    # empty contracts
    inputs["contracts"] = []
    with pytest.raises(ValueError, match="contracts"):
        build_schema_catalog(inputs)

    # item not a dict
    inputs["contracts"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="contracts"):
        build_schema_catalog(inputs)

    # missing contract_name
    inputs["contracts"] = [
        {"contract_version": "2.0", "path": "schemas/meta/x.json", "status": "active"}
    ]
    with pytest.raises(ValueError, match="contract_name"):
        build_schema_catalog(inputs)

    # missing contract_version
    inputs["contracts"] = [
        {"contract_name": "intent", "path": "schemas/meta/x.json", "status": "active"}
    ]
    with pytest.raises(ValueError, match="contract_version"):
        build_schema_catalog(inputs)

    # missing path
    inputs["contracts"] = [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "status": "active",
        }
    ]
    with pytest.raises(ValueError, match="path"):
        build_schema_catalog(inputs)

    # missing status
    inputs["contracts"] = [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent.schema.json",
        }
    ]
    with pytest.raises(ValueError, match="status"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_duplicate_contract_identity():
    inputs: dict[str, object] = dict(VALID_INPUTS)
    inputs["contracts"] = VALID_INPUTS["contracts"] + [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent_v2.schema.json",
            "status": "active",
        }
    ]
    with pytest.raises(ValueError, match="Duplicate contract"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_duplicate_contract_path():
    inputs: dict[str, object] = dict(VALID_INPUTS)
    inputs["contracts"] = VALID_INPUTS["contracts"] + [
        {
            "contract_name": "intent_v2",
            "contract_version": "1.0",
            "path": "schemas/meta/intent.schema.json",
            "status": "deprecated",
        }
    ]
    with pytest.raises(ValueError, match="Duplicate contract.path"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_invalid_contract_consumers():
    # consumers not a list
    inputs: dict[str, object] = dict(VALID_INPUTS)
    inputs["contracts"] = [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent.schema.json",
            "status": "active",
            "consumers": "not-a-list",
        },
        {
            "contract_name": "plan",
            "contract_version": "2.0",
            "path": "schemas/meta/plan.schema.json",
            "status": "active",
        },
    ]
    with pytest.raises(ValueError, match="consumers"):
        build_schema_catalog(inputs)

    # consumers with duplicate entries
    inputs["contracts"] = [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent.schema.json",
            "status": "active",
            "consumers": ["orchestrator", "orchestrator"],
        },
        {
            "contract_name": "plan",
            "contract_version": "2.0",
            "path": "schemas/meta/plan.schema.json",
            "status": "active",
        },
    ]
    with pytest.raises(ValueError, match="consumers"):
        build_schema_catalog(inputs)

    # consumers with non-string item
    inputs["contracts"] = [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent.schema.json",
            "status": "active",
            "consumers": [42],
        },
        {
            "contract_name": "plan",
            "contract_version": "2.0",
            "path": "schemas/meta/plan.schema.json",
            "status": "active",
        },
    ]
    with pytest.raises(ValueError, match="consumers"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_invalid_contract_depends_on():
    # depends_on not a list
    inputs: dict[str, object] = dict(VALID_INPUTS)
    inputs["contracts"] = [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent.schema.json",
            "status": "active",
            "depends_on": "not-a-list",
        },
        {
            "contract_name": "plan",
            "contract_version": "2.0",
            "path": "schemas/meta/plan.schema.json",
            "status": "active",
        },
    ]
    with pytest.raises(ValueError, match="depends_on"):
        build_schema_catalog(inputs)

    # depends_on with duplicate entries
    inputs["contracts"] = [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent.schema.json",
            "status": "active",
        },
        {
            "contract_name": "plan",
            "contract_version": "2.0",
            "path": "schemas/meta/plan.schema.json",
            "status": "active",
            "depends_on": ["intent@2.0", "intent@2.0"],
        },
    ]
    with pytest.raises(ValueError, match="depends_on"):
        build_schema_catalog(inputs)

    # depends_on with non-string item
    inputs["contracts"] = [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent.schema.json",
            "status": "active",
        },
        {
            "contract_name": "plan",
            "contract_version": "2.0",
            "path": "schemas/meta/plan.schema.json",
            "status": "active",
            "depends_on": [42],
        },
    ]
    with pytest.raises(ValueError, match="depends_on"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_unknown_contract_dependency():
    inputs: dict[str, object] = dict(VALID_INPUTS_NO_OPTIONAL)
    inputs["contracts"] = [
        {
            "contract_name": "intent",
            "contract_version": "2.0",
            "path": "schemas/meta/intent.schema.json",
            "status": "active",
        },
        {
            "contract_name": "plan",
            "contract_version": "2.0",
            "path": "schemas/meta/plan.schema.json",
            "status": "active",
            "depends_on": ["roadmap_slice@2.0"],
        },
    ]
    with pytest.raises(ValueError, match="depends_on"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_invalid_global_policies():
    # not a list
    inputs: dict[str, object] = dict(VALID_INPUTS)
    inputs["global_policies"] = "not-a-list"
    with pytest.raises(ValueError, match="global_policies"):
        build_schema_catalog(inputs)

    # less than 2
    inputs["global_policies"] = [
        {"policy_id": "POL-001", "path": "policies/commit.gpg", "mode": "reference"},
    ]
    with pytest.raises(ValueError, match="global_policies"):
        build_schema_catalog(inputs)

    # item not a dict
    inputs["global_policies"] = ["not-a-dict", "not-a-dict-either"]
    with pytest.raises(ValueError, match="global_policies"):
        build_schema_catalog(inputs)

    # missing policy_id
    inputs["global_policies"] = [
        {"path": "policies/commit.gpg", "mode": "reference"},
        {"policy_id": "POL-002", "path": "policies/review.gpg", "mode": "reference"},
    ]
    with pytest.raises(ValueError, match="policy_id"):
        build_schema_catalog(inputs)

    # missing path
    inputs["global_policies"] = [
        {"policy_id": "POL-001", "mode": "reference"},
        {"policy_id": "POL-002", "path": "policies/review.gpg", "mode": "reference"},
    ]
    with pytest.raises(ValueError, match="path"):
        build_schema_catalog(inputs)

    # missing mode
    inputs["global_policies"] = [
        {"policy_id": "POL-001", "path": "policies/commit.gpg"},
        {"policy_id": "POL-002", "path": "policies/review.gpg", "mode": "reference"},
    ]
    with pytest.raises(ValueError, match="mode"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_duplicate_global_policy_id():
    inputs: dict[str, object] = dict(VALID_INPUTS)
    inputs["global_policies"] = [
        {"policy_id": "POL-001", "path": "policies/commit.gpg", "mode": "reference"},
        {"policy_id": "POL-001", "path": "policies/review.gpg", "mode": "reference"},
        {"policy_id": "POL-002", "path": "policies/tests.gpg", "mode": "reference"},
    ]
    with pytest.raises(ValueError, match="Duplicate global_policies.policy_id"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_invalid_compatibility_matrix():
    # not a list
    inputs: dict[str, object] = dict(VALID_INPUTS)
    inputs["compatibility_matrix"] = "not-a-list"
    with pytest.raises(ValueError, match="compatibility_matrix"):
        build_schema_catalog(inputs)

    # empty
    inputs["compatibility_matrix"] = []
    with pytest.raises(ValueError, match="compatibility_matrix"):
        build_schema_catalog(inputs)

    # item not a dict
    inputs["compatibility_matrix"] = ["not-a-dict"]
    with pytest.raises(ValueError, match="compatibility_matrix"):
        build_schema_catalog(inputs)

    # missing from
    inputs["compatibility_matrix"] = [
        {"to": "plan@2.0", "status": "compatible"}
    ]
    with pytest.raises(ValueError, match="from"):
        build_schema_catalog(inputs)

    # missing to
    inputs["compatibility_matrix"] = [
        {"from": "intent@2.0", "status": "compatible"}
    ]
    with pytest.raises(ValueError, match="to"):
        build_schema_catalog(inputs)

    # missing status
    inputs["compatibility_matrix"] = [
        {"from": "intent@2.0", "to": "plan@2.0"}
    ]
    with pytest.raises(ValueError, match="status"):
        build_schema_catalog(inputs)

    # invalid status
    inputs["compatibility_matrix"] = [
        {"from": "intent@2.0", "to": "plan@2.0", "status": "unknown"}
    ]
    with pytest.raises(ValueError, match="status"):
        build_schema_catalog(inputs)

    # invalid from pattern
    inputs["compatibility_matrix"] = [
        {"from": "not-a-ref", "to": "plan@2.0", "status": "compatible"}
    ]
    with pytest.raises(ValueError, match="from"):
        build_schema_catalog(inputs)

    # invalid to pattern
    inputs["compatibility_matrix"] = [
        {"from": "intent@2.0", "to": "not-a-ref", "status": "compatible"}
    ]
    with pytest.raises(ValueError, match="to"):
        build_schema_catalog(inputs)

    # extra keys
    inputs["compatibility_matrix"] = [
        {
            "from": "intent@2.0",
            "to": "plan@2.0",
            "status": "compatible",
            "extra": "nope",
        }
    ]
    with pytest.raises(ValueError, match="compatibility_matrix"):
        build_schema_catalog(inputs)

    # notes not a string
    inputs["compatibility_matrix"] = [
        {
            "from": "intent@2.0",
            "to": "plan@2.0",
            "status": "compatible",
            "notes": 42,
        }
    ]
    with pytest.raises(ValueError, match="notes"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_duplicate_compatibility_pair():
    inputs: dict[str, object] = dict(VALID_INPUTS)
    inputs["compatibility_matrix"] = VALID_INPUTS["compatibility_matrix"] + [
        {
            "from": "intent@2.0",
            "to": "plan@2.0",
            "status": "requires_migration",
        }
    ]
    with pytest.raises(ValueError, match="Duplicate compatibility matrix pair"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_unknown_compatibility_contract_ref():
    inputs: dict[str, object] = dict(VALID_INPUTS_NO_OPTIONAL)
    inputs["compatibility_matrix"] = [
        {
            "from": "intent@2.0",
            "to": "roadmap_slice@2.0",
            "status": "compatible",
        }
    ]
    with pytest.raises(ValueError, match="does not reference an existing contract"):
        build_schema_catalog(inputs)

    inputs["compatibility_matrix"] = [
        {
            "from": "roadmap_slice@2.0",
            "to": "plan@2.0",
            "status": "compatible",
        }
    ]
    with pytest.raises(ValueError, match="does not reference an existing contract"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_invalid_human_summary():
    inputs: dict[str, object] = dict(VALID_INPUTS)
    inputs["human_summary"] = 42
    with pytest.raises(ValueError, match="human_summary"):
        build_schema_catalog(inputs)

    inputs["human_summary"] = ["not", "a", "string"]
    with pytest.raises(ValueError, match="human_summary"):
        build_schema_catalog(inputs)


def test_build_schema_catalog_rejects_invalid_output():
    with mock.patch("jsonschema.validate") as mock_validate:
        import jsonschema as _jsonschema_module

        mock_validate.side_effect = _jsonschema_module.ValidationError("forced failure")

        with pytest.raises(SchemaValidationError, match="forced failure"):
            build_schema_catalog(VALID_INPUTS)
