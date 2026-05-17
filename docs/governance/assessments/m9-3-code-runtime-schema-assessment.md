# M9.3 Code Runtime Schema Assessment

## Scope Statement

This is a code/runtime/schema assessment only. It is not implementation, not remediation, not readiness approval, and not adapter work.

No source, tests, schemas, agents, runtime modules, builder modules, package config, README, or existing governance documents were modified. This assessment does not authorize fixes, refactors, new tests, schema changes, adapters, CLI, registry, `.adf/` artifact store, git execution, agent invocation, `framework_state` mutation, candidate mode, or primary mode.

## Evidence Commands

Commands executed before assessment work:

- `git branch --show-current`
  - Output: `main`.
- `git status --short`
  - Output: clean before starting.
- `git log --oneline -5`
  - Output:

```text
05045df Add M9.2 governance consistency assessment
ef97b4a Add M9.1 repository map assessment
d620175 Realign roadmap for repository assessment
b2b18fb Update extraction handoff after M8.1 completion
7d6608f Implement minimal ADF runtime invocation
```

Bounded inventory commands executed:

- `find schemas/meta -maxdepth 1 -type f | sort`
  - Relevant output: 13 meta schema files were listed under `schemas/meta/`.
- `find src/agentic_development_framework/builders -maxdepth 1 -type f | sort`
  - Relevant output: 13 builder modules plus `__init__.py` were listed.
- `find src/agentic_development_framework/runtime -maxdepth 1 -type f | sort`
  - Relevant output: `__init__.py` and `invocation.py` were listed.
- `find tests -maxdepth 1 -type f | sort`
  - Relevant output: 13 builder test files, schema/package tests, and runtime invocation/dry-run tests were listed.

Tests were not run during this assessment to avoid creating or updating pytest cache or other runtime side-effect files during a governance/documentation-only review. The assessment relies on read-only inspection of the existing tests and prior documented passing-test evidence.

## Source Documents Reviewed

Source of truth:

- `coordinator-contract.md`
- `docs/governance/extraction-handoff.md`
- `docs/governance/assessments/m9-1-repository-map-assessment.md`
- `docs/governance/assessments/m9-2-governance-milestone-consistency-assessment.md`

Design/governance support:

- `docs/governance/builder-runtime-extraction-strategy.md`
- `docs/governance/minimal-builder-invocation-runtime-strategy.md`
- `docs/governance/agnostic-dry-run-design-and-evidence.md`

Schemas:

- `schemas/meta/context_bundle.schema.json`
- `schemas/meta/decisions.schema.json`
- `schemas/meta/framework_state.schema.json`
- `schemas/meta/git_operation.schema.json`
- `schemas/meta/implementation_report.schema.json`
- `schemas/meta/intent.schema.json`
- `schemas/meta/plan.schema.json`
- `schemas/meta/policy_constraints.schema.json`
- `schemas/meta/review_report.schema.json`
- `schemas/meta/roadmap_slice.schema.json`
- `schemas/meta/schema_catalog.schema.json`
- `schemas/meta/task_packet.schema.json`
- `schemas/meta/test_report.schema.json`

Builders:

- `src/agentic_development_framework/builders/__init__.py`
- `src/agentic_development_framework/builders/context_bundle.py`
- `src/agentic_development_framework/builders/decisions.py`
- `src/agentic_development_framework/builders/framework_state.py`
- `src/agentic_development_framework/builders/git_operation.py`
- `src/agentic_development_framework/builders/implementation_report.py`
- `src/agentic_development_framework/builders/intent.py`
- `src/agentic_development_framework/builders/plan.py`
- `src/agentic_development_framework/builders/policy_constraints.py`
- `src/agentic_development_framework/builders/review_report.py`
- `src/agentic_development_framework/builders/roadmap_slice.py`
- `src/agentic_development_framework/builders/schema_catalog.py`
- `src/agentic_development_framework/builders/task_packet.py`
- `src/agentic_development_framework/builders/test_report.py`

Runtime:

- `src/agentic_development_framework/runtime/__init__.py`
- `src/agentic_development_framework/runtime/invocation.py`
- `src/agentic_development_framework/__init__.py`

Tests:

- `tests/test_build_context_bundle.py`
- `tests/test_build_decisions.py`
- `tests/test_build_framework_state.py`
- `tests/test_build_git_operation.py`
- `tests/test_build_implementation_report.py`
- `tests/test_build_intent.py`
- `tests/test_build_plan.py`
- `tests/test_build_policy_constraints.py`
- `tests/test_build_review_report.py`
- `tests/test_build_roadmap_slice.py`
- `tests/test_build_schema_catalog.py`
- `tests/test_build_task_packet.py`
- `tests/test_build_test_report.py`
- `tests/test_meta_schemas.py`
- `tests/test_package_import.py`
- `tests/test_runtime_dry_run.py`
- `tests/test_runtime_invocation.py`

## Schema Inventory Assessment

The visible schema inventory contains 13 Draft-07 JSON Schema contracts under `schemas/meta/`:

- `intent`, `policy_constraints`, `roadmap_slice`, `plan`, `task_packet`, `context_bundle`, `implementation_report`, `test_report`, `review_report`, `git_operation`, `decisions`, `framework_state`, and `schema_catalog`.

This aligns with the M9.1 documented inventory and the M9.2 governance timeline, which both describe 13 meta schemas. The schema set also aligns with the M5 strategy inventory, which planned one builder per meta schema and no additional builders without a schema.

Observed schema characteristics:

- Each reviewed schema declares Draft-07 via `$schema`.
- Each reviewed schema uses `additionalProperties: false` at the top level.
- Each reviewed schema uses `contract_name` and `contract_version` fields, with version `2.0` as the visible contract version.
- ID patterns are visibly distinct by artifact type, such as `INTENT-*`, `PLAN-*`, `TPACKET-*`, `REV-*`, `GIT-*`, `DEC-*`, `FWSTATE-*`, and `SCAT-*`.

No schemas were edited.

## Builder Inventory Assessment

The visible builder inventory contains 13 programmatic builder modules plus `builders/__init__.py`. The module set matches the 13 schema files and the M5/M9.1 claim that all programmatic builders are present:

- `build_intent` -> `intent.schema.json`
- `build_policy_constraints` -> `policy_constraints.schema.json`
- `build_roadmap_slice` -> `roadmap_slice.schema.json`
- `build_plan` -> `plan.schema.json`
- `build_task_packet` -> `task_packet.schema.json`
- `build_context_bundle` -> `context_bundle.schema.json`
- `build_implementation_report` -> `implementation_report.schema.json`
- `build_test_report` -> `test_report.schema.json`
- `build_review_report` -> `review_report.schema.json`
- `build_git_operation` -> `git_operation.schema.json`
- `build_decisions` -> `decisions.schema.json`
- `build_framework_state` -> `framework_state.schema.json`
- `build_schema_catalog` -> `schema_catalog.schema.json`

Observed builder characteristics:

- Builders are plain Python callables accepting explicit `inputs` dictionaries and optional `output_path` parameters.
- Builders generate deterministic IDs and timestamps from input content rather than wall-clock time.
- Builders validate produced artifacts against their corresponding schema using `jsonschema` before returning.
- Builders write only when `output_path` is explicitly supplied.
- `builders/__init__.py` exports all 13 builder callables and `SchemaValidationError`.

The visible builder set aligns with schemas and the M5/M9.1 inventory claims. No builders were edited.

## Runtime Invocation Assessment

The runtime exposes `invoke_builder` from `src/agentic_development_framework/runtime/__init__.py`, implemented in `runtime/invocation.py`.

Assessment against the documented M8.1 boundary:

- Static builder mapping: aligned. `_SUPPORTED_BUILDERS` is a hardcoded mapping for all 13 builder names with callable, schema path, artifact type, ID field, and store directory metadata. No dynamic discovery or plugin registry is visible.
- Validation evidence: aligned at the visible behavior level. The runtime loads the mapped schema, validates produced artifacts with `jsonschema.Draft7Validator`, and returns structured findings with field, issue, and severity.
- Dry-run evidence: aligned at the visible behavior level. `dry_run=True` returns produced artifact/evidence in memory, sets `state_update_proposal_preview`, and tests assert no output path or artifact root is created.
- Optional explicit persistence only: aligned at the visible behavior level. Persistence requires `store=True`, `artifact_root`, and `output_path`; paths outside `artifact_root` are rejected before writing.
- `framework_state` proposal/preview only: aligned in intent. The runtime returns `preview_only: True` and `applied: False`, and tests assert caller-provided framework state is not mutated.
- No CLI: aligned. No CLI entry point or argument parser is visible in the reviewed runtime/package files.
- No registry: aligned for dynamic registry scope. The visible runtime has a static mapping, not dynamic discovery, plugin loading, or registry infrastructure.
- No adapters: aligned. No adapter code or project-specific adapter invocation is visible in reviewed runtime files.
- No git execution: aligned. The runtime constructs evidence only and contains no subprocess/git command execution. `build_git_operation` is an artifact builder, not git execution.
- No agent invocation: aligned. The runtime imports builders only and does not invoke OpenCode/LLM agents.
- No mode activation: aligned. No candidate/primary activation or controlled mode mutation is visible in reviewed runtime files.

No runtime files were edited.

## Test Coverage Map

Visible test coverage related to schemas, builders, package import, runtime invocation, and dry-run:

- `tests/test_meta_schemas.py`: checks schema files are JSON with `$schema` and checks schemas do not contain listed adapter/FBA-specific references.
- `tests/test_package_import.py`: checks package import and `__version__`.
- `tests/test_build_*.py`: 13 builder test files, each visibly covering schema-valid output, determinism, missing required inputs, explicit output-path writing, invalid input cases, and forced schema-validation failures.
- `tests/test_runtime_invocation.py`: covers successful explicit `build_intent` invocation, unknown builder failure, schema validation pass evidence, invalid input failure, invalid artifact non-storage, path boundary refusal, `framework_state` non-mutation/proposal behavior, and no modification of selected builder/schema/agent files during invocation.
- `tests/test_runtime_dry_run.py`: covers dry-run evidence, no artifact-root/output creation, no-write/no-git confirmations, explicit deterministic check, and equivalent comparison category.

Tests were not run during M9.3 to avoid creating or updating pytest cache or other runtime side-effect files during a governance/documentation-only assessment.

## Alignment Findings

Aligned:

- The visible schema inventory is 13 files, matching M9.1/M9.2 and M5 inventory claims.
- The visible builder inventory is 13 modules plus exports, matching the 13 schema contracts.
- Each builder visibly validates output against its mapped schema and uses deterministic artifact fields.
- Runtime `_SUPPORTED_BUILDERS` visibly maps all 13 builder names to corresponding schemas and ID fields.
- Runtime invocation is caller-selected through `builder_name`; no autonomous builder selection or chaining is visible.
- Runtime validation and dry-run evidence behavior are present and covered by runtime tests.
- Runtime optional persistence is explicit and path-bounded.
- Runtime returns `framework_state` proposals/previews and does not visibly mutate state.
- No reviewed runtime code shows CLI, dynamic registry, adapters, git execution, agent invocation, or mode activation.

Unclear or requires deeper later review:

- Runtime comparison uses M7 category names, but the visible implementation is shallow top-level dictionary comparison rather than a full semantic comparison across the dimensions described in M7.1.
- Runtime conflict detection checks `current_framework_state.get("artifact_refs", [])`, while the current `framework_state.schema.json` and `build_framework_state` use `artifacts`. This may be a proposal-vs-persistent-schema naming distinction, or it may limit conflict detection when a schema-shaped `framework_state` artifact is passed.
- Runtime tests visibly exercise `invoke_builder` primarily through `build_intent`; builder tests cover all builders directly, but runtime invocation coverage does not visibly invoke all 13 mapped builders end-to-end.
- The runtime storage path uses caller-supplied output paths and creates parent directories. This matches optional explicit persistence, but it is not the full `.adf/` artifact store or metadata inventory described as still unauthorized/incomplete.

Risks/gaps:

- Write failure handling is not visibly converted into structured runtime failure evidence. After validation, `output_file.parent.mkdir(...)` and `output_file.write_text(...)` are not wrapped in a runtime failure response, while the M6.1 failure model described structured write failures.
- Runtime conflict detection may miss duplicate artifact IDs if callers pass a `framework_state` artifact shaped according to the current schema's `artifacts` field rather than an `artifact_refs` field.
- Runtime semantic comparison evidence appears intentionally minimal and may not support deeper semantic equivalence claims without later expansion or documentation clarification.
- Runtime tests do not visibly include a direct inventory assertion that `_SUPPORTED_BUILDERS` stays synchronized with the schema and builder inventory.

Explicitly out of scope for M9.3:

- Implementing any correction.
- Refactoring runtime comparison, write failure handling, or conflict detection.
- Adding tests for the observed risks.
- Updating schemas, builders, runtime, README, pyproject, agents, or existing governance documents.
- Creating adapters, CLI, registry, `.adf/` artifact store, git execution, agent invocation, or mode activation.
- Inspecting FBA or external repositories.

## Required Corrections or Documentation Updates For Later Phases

Safe documentation clarifications for M9.5:

- Clarify that M8.1 implements minimal optional persistence only and does not implement the full `.adf/` artifact store or `metadata.json` inventory.
- Clarify whether runtime `state_update_proposal.add_artifact_refs` and conflict detection should intentionally use proposal-only naming or align terminology with `framework_state.schema.json` `artifacts`.
- Clarify that current runtime comparison is category-based and shallow unless later implementation expands it to M7.1 semantic-comparison depth.
- Preserve the M9.2 note that older M5/M6 adapter-roadmap language is historical and superseded by M8.3 moving adapter work to M10.

Implementation items requiring explicit owner authorization:

- Add or change structured write-failure handling in runtime persistence.
- Add runtime tests that exercise all 13 builder mappings through `invoke_builder`.
- Add inventory synchronization tests between schemas, builders, runtime mapping, and exports.
- Change conflict detection to recognize schema-shaped `framework_state.artifacts`, if that is the desired contract.
- Expand comparison behavior beyond shallow top-level comparison, if deeper M7.1 semantic comparison is required.

Items deferred to M10 or later:

- FBA adapter boundary notes.
- Any adapter implementation.
- Any downstream FBA integration behavior.
- Any project-specific translation layer, Odoo behavior, or FBA source inspection.

## Non-Readiness Statement

M9.3 does not certify production readiness.

M9.3 does not certify FBA integration readiness.

M9.3 does not authorize adapters, CLI, registry, `.adf` store, git execution, agent invocation, source/test/schema changes, or candidate/primary mode.

M9.3 also does not authorize runtime/builder/schema/test remediation, README updates, existing governance document edits, or adapter-related work.

## Risks / Gaps Observed From Code Runtime Schema Review Only

- Runtime write failures during explicit persistence are not visibly returned as structured failure evidence.
- Runtime conflict detection appears tied to `artifact_refs`, while current framework state schema and builder use `artifacts`.
- Runtime comparison behavior is shallow relative to the richer M7.1 semantic-comparison design language.
- Runtime tests visibly focus invocation behavior on `build_intent`; all builders are tested directly, but all 13 runtime mapping entries are not visibly invoked end-to-end through runtime tests.
- The full `.adf/` artifact store and metadata inventory remain unimplemented/unauthorized; optional explicit file persistence should not be described as full artifact-store readiness.

## Coordinator Review Checklist

- [ ] scope respected
- [ ] only allowed file changed
- [ ] no README update
- [ ] no source/test/schema/agent/runtime/builder changes
- [ ] no implementation
- [ ] no adapter/CLI/registry work
- [ ] no .adf store
- [ ] no git execution
- [ ] no agent invocation
- [ ] no readiness claims
- [ ] no mode activation
- [ ] git status reviewed
- [ ] diff reviewed
