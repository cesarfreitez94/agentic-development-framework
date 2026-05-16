import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "meta"
FORBIDDEN_STRINGS = (
    "factory-build-agent",
    "src/fba",
    ".factory/framework-state.json",
    "fba-agent-observer",
    "opencode.ai/fba",
    "FBA",
    "Odoo",
    "odoo",
)


def test_meta_schemas_are_json_with_schema_uri():
    schema_paths = sorted(SCHEMA_DIR.glob("*.schema.json"))

    assert schema_paths

    for schema_path in schema_paths:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        assert "$schema" in schema, schema_path


def test_meta_schemas_do_not_contain_adapter_specific_references():
    schema_paths = sorted(SCHEMA_DIR.glob("*.schema.json"))

    assert schema_paths

    for schema_path in schema_paths:
        content = schema_path.read_text(encoding="utf-8")

        for forbidden_string in FORBIDDEN_STRINGS:
            assert forbidden_string not in content, (schema_path, forbidden_string)
