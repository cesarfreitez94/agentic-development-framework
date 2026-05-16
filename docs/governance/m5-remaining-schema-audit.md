# M5 Remaining Schema Audit (M5.7–M5.13)

## Purpose

Validate whether the remaining schemas needed for M5.7–M5.13 already exist in ADF's `schemas/meta/`, compare them against the FBA source schemas, and determine whether a schema-alignment phase is needed before continuing builder extraction.

## Sources Inspected

| Source | Path |
|--------|------|
| ADF schemas | `schemas/meta/` (this repo) |
| FBA schemas | `/home/cafl/projects/factory-build-agent/schemas/meta/` |
| Governance docs | `docs/governance/builder-runtime-extraction-strategy.md` |
| Governance docs | `docs/governance/extraction-handoff.md` |

## Current ADF Schema Inventory

13 schema files present in `schemas/meta/`:

```
schemas/meta/context_bundle.schema.json
schemas/meta/decisions.schema.json
schemas/meta/framework_state.schema.json
schemas/meta/git_operation.schema.json
schemas/meta/implementation_report.schema.json
schemas/meta/intent.schema.json
schemas/meta/plan.schema.json
schemas/meta/policy_constraints.schema.json
schemas/meta/review_report.schema.json
schemas/meta/roadmap_slice.schema.json
schemas/meta/schema_catalog.schema.json
schemas/meta/task_packet.schema.json
schemas/meta/test_report.schema.json
```

## FBA Schema Inventory

13 schema files present in FBA's `schemas/meta/`:

```
schemas/meta/context_bundle.schema.json
schemas/meta/decisions.schema.json
schemas/meta/framework_state.v2.schema.json
schemas/meta/git_operation.schema.json
schemas/meta/implementation_report.schema.json
schemas/meta/intent.schema.json
schemas/meta/plan.schema.json
schemas/meta/policy_constraints.schema.json
schemas/meta/review_report.schema.json
schemas/meta/roadmap_slice.schema.json
schemas/meta/schema_catalog.schema.json
schemas/meta/task_packet.schema.json
schemas/meta/test_report.schema.json
```

## Builder-by-Builder Comparison Table

### M5.7 — build_implementation_report

| Criterion | ADF | FBA | Match |
|-----------|-----|-----|-------|
| Filename | `implementation_report.schema.json` | `implementation_report.schema.json` | EXACT |
| contract_name | `implementation_report` | `implementation_report` | IDENTICAL |
| contract_version | `2.0` | `2.0` | IDENTICAL |
| required fields | report_id, packet_id, created_at, status, changed_files, created_artifacts, acceptance_status, blockers | same | IDENTICAL |
| artifact ID pattern | `^IMPL-[0-9]{8}-[0-9]{3}$` | same | IDENTICAL |
| status enum | completed, partial, failed, blocked | same | IDENTICAL |
| additionalProperties | false | false | IDENTICAL |
| conditional rules (allOf) | 1 rule (blockers required when failed/blocked) | same | IDENTICAL |
| FBA/Odoo coupling | None | None | CLEAN |
| Project-agnostic | Yes | Yes | YES |
| Verdict | — | — | **IDENTICAL** (only $id/title differ) |

**Recommendation: PROCEED_WITH_ADF_SCHEMA**

---

### M5.8 — build_test_report

| Criterion | ADF | FBA | Match |
|-----------|-----|-----|-------|
| Filename | `test_report.schema.json` | `test_report.schema.json` | EXACT |
| contract_name | `test_report` | `test_report` | IDENTICAL |
| contract_version | `2.0` | `2.0` | IDENTICAL |
| required fields | report_id, implementation_report_id, created_at, status, test_runs, failures, coverage | same | IDENTICAL |
| artifact ID pattern | `^TEST-[0-9]{8}-[0-9]{3}$` | same | IDENTICAL |
| status enum | passed, failed, partial, not_run | same | IDENTICAL |
| test_runs.kind enum | pytest, jsonschema, lint, security, custom | same | IDENTICAL |
| additionalProperties | false | false | IDENTICAL |
| conditional rules | 2 rules (failures minItems when failed, not_run_reason required when not_run) | same | IDENTICAL |
| FBA/Odoo coupling | None | None | CLEAN |
| Project-agnostic | Yes | Yes | YES |
| Verdict | — | — | **IDENTICAL** (only $id/title differ) |

**Recommendation: PROCEED_WITH_ADF_SCHEMA**

---

### M5.9 — build_review_report

| Criterion | ADF | FBA | Match |
|-----------|-----|-----|-------|
| Filename | `review_report.schema.json` | `review_report.schema.json` | EXACT |
| contract_name | `review_report` | `review_report` | IDENTICAL |
| contract_version | `2.0` | `2.0` | IDENTICAL |
| required fields | report_id, implementation_report_id, test_report_id, created_at, status, findings, policy_compliance, recommendation | same | IDENTICAL |
| artifact ID pattern | `^REV-[0-9]{8}-[0-9]{3}$` | same | IDENTICAL |
| status enum | approved, approved_with_risks, changes_requested, blocked | same | IDENTICAL |
| recommendation enum | proceed_to_git, fix_required, ask_user, stop | same | IDENTICAL |
| findings.severity enum | low, medium, high, critical | same | IDENTICAL |
| additionalProperties | false | false | IDENTICAL |
| conditional rules | 1 rule (required_fixes required when changes_requested) | same | IDENTICAL |
| FBA/Odoo coupling | None | None | CLEAN |
| Project-agnostic | Yes | Yes | YES |
| Verdict | — | — | **IDENTICAL** (only $id/title differ) |

**Recommendation: PROCEED_WITH_ADF_SCHEMA**

---

### M5.10 — build_git_operation

| Criterion | ADF | FBA | Match |
|-----------|-----|-----|-------|
| Filename | `git_operation.schema.json` | `git_operation.schema.json` | EXACT |
| contract_name | `git_operation` | `git_operation` | IDENTICAL |
| contract_version | `2.0` | `2.0` | IDENTICAL |
| required fields | operation_id, created_at, produced_by, executed_by, operation_type, status, source_refs, branch, policy_checks | same | IDENTICAL |
| artifact ID pattern | `^GIT-[0-9]{8}-[0-9]{3}$` | same | IDENTICAL |
| operation_type enum | status_check, create_branch, commit, push, open_pr, merge_pr | same | IDENTICAL |
| status enum | requested, executed, failed, cancelled | same | IDENTICAL |
| additionalProperties | false | false | IDENTICAL |
| conditional rules | 2 rules (result required when executed/failed/cancelled, user confirmation required for merge_pr) | same | IDENTICAL |
| FBA/Odoo coupling | None | None | CLEAN |
| Project-agnostic | Yes | Yes | YES |
| Verdict | — | — | **IDENTICAL** (only $id/title differ) |

**Recommendation: PROCEED_WITH_ADF_SCHEMA**

---

### M5.11 — build_decisions

| Criterion | ADF | FBA | Match |
|-----------|-----|-----|-------|
| Filename | `decisions.schema.json` | `decisions.schema.json` | EXACT |
| contract_name | `decisions` | `decisions` | IDENTICAL |
| contract_version | `2.0` | `2.0` | IDENTICAL |
| required fields | decision_id, created_at, decision_type, status, question, options, selected_option, required_by | same | IDENTICAL |
| artifact ID pattern | `^DEC-[0-9]{8}-[0-9]{3}$` | same | IDENTICAL |
| decision_type enum | user_confirmation, policy_gate, review_gate, git_gate, workflow, architecture | same | IDENTICAL |
| status enum | pending, resolved, cancelled | same | IDENTICAL |
| additionalProperties | false | false | IDENTICAL |
| conditional rules | 2 rules (selected_option/resolved_at required when resolved, selected_option nullable when cancelled) | same | IDENTICAL |
| FBA/Odoo coupling | None | None | CLEAN |
| Project-agnostic | Yes | Yes | YES |
| Verdict | — | — | **IDENTICAL** (only $id/title differ) |

**Recommendation: PROCEED_WITH_ADF_SCHEMA**

---

### M5.12 — build_framework_state

| Criterion | ADF | FBA | Match |
|-----------|-----|-----|-------|
| Filename | `framework_state.schema.json` | `framework_state.v2.schema.json` | **DIFFERENT** |
| contract_name | `framework_state_v2` | `framework_state_v2` | IDENTICAL |
| contract_version | `2.0` | `2.0` | IDENTICAL |
| required fields | state_id, updated_at, workflow_version, current_phase, artifacts, pending_decisions | same | IDENTICAL |
| artifact ID pattern | `^FWSTATE-[0-9]{8}-[0-9]{3}$` | same | IDENTICAL |
| current_phase enum | idle, intent, policy_constraints, roadmap_slice, planning, tasking, context, implementation, testing, review, git_operation, completed, blocked | same | IDENTICAL |
| artifacts.status enum | draft, valid, published | same | IDENTICAL |
| active_milestone.id pattern | `^M[0-9]+$` | same | IDENTICAL |
| additionalProperties | false | false | IDENTICAL |
| conditional rules | None (no allOf) | None | IDENTICAL |
| FBA/Odoo coupling | None | None | CLEAN |
| Project-agnostic | Yes | Yes | YES |
| Verdict | — | — | **EQUIVALENT** (filename differs, content identical) |

**Recommendation: PROCEED_WITH_ADF_SCHEMA**

Note: The filename difference (`framework_state.schema.json` vs `framework_state.v2.schema.json`) is a naming convention choice. ADF chose the simpler name since the schema's `contract_name` already encodes `v2`. No alignment needed.

---

### M5.13 — build_schema_catalog

| Criterion | ADF | FBA | Match |
|-----------|-----|-----|-------|
| Filename | `schema_catalog.schema.json` | `schema_catalog.schema.json` | EXACT |
| contract_name | `schema_catalog` | `schema_catalog` | IDENTICAL |
| contract_version | `2.0` | `2.0` | IDENTICAL |
| required fields | catalog_id, updated_at, contracts, global_policies, compatibility_matrix | same | IDENTICAL |
| artifact ID pattern | `^SCAT-[0-9]{8}-[0-9]{3}$` | same | IDENTICAL |
| contracts.status enum | active, deprecated, experimental | same | IDENTICAL |
| contracts.path pattern | `^schemas/meta/[a-z0-9_.-]+\\.json$` | same | IDENTICAL |
| compatibility status enum | compatible, requires_migration, incompatible | same | IDENTICAL |
| global_policies mode enum | reference | same | IDENTICAL |
| additionalProperties | false | false | IDENTICAL |
| conditional rules | None (no allOf) | None | IDENTICAL |
| FBA/Odoo coupling | None | None | CLEAN |
| Project-agnostic | Yes | Yes | YES |
| Verdict | — | — | **IDENTICAL** (only $id/title differ) |

**Recommendation: PROCEED_WITH_ADF_SCHEMA**

---

## Per-Builder Recommendation Summary

| Builder | Phase | Required Schema | ADF Present | FBA Present | FBA Filename Match | Content Match | Recommendation |
|---------|-------|-----------------|-------------|-------------|--------------------|---------------|----------------|
| build_implementation_report | M5.7 | implementation_report | YES | YES | EXACT | IDENTICAL | PROCEED_WITH_ADF_SCHEMA |
| build_test_report | M5.8 | test_report | YES | YES | EXACT | IDENTICAL | PROCEED_WITH_ADF_SCHEMA |
| build_review_report | M5.9 | review_report | YES | YES | EXACT | IDENTICAL | PROCEED_WITH_ADF_SCHEMA |
| build_git_operation | M5.10 | git_operation | YES | YES | EXACT | IDENTICAL | PROCEED_WITH_ADF_SCHEMA |
| build_decisions | M5.11 | decisions | YES | YES | EXACT | IDENTICAL | PROCEED_WITH_ADF_SCHEMA |
| build_framework_state | M5.12 | framework_state | YES | YES | DIFFERENT* | EQUIVALENT | PROCEED_WITH_ADF_SCHEMA |
| build_schema_catalog | M5.13 | schema_catalog | YES | YES | EXACT | IDENTICAL | PROCEED_WITH_ADF_SCHEMA |

* `framework_state.schema.json` vs `framework_state.v2.schema.json` — structurally identical, only filename convention differs.

## Findings

### 1. All Required Schemas Exist in ADF
All 7 schemas needed for M5.7–M5.13 are present, validated, and at contract_version 2.0 in `schemas/meta/`.

### 2. Near-Complete Structural Identity with FBA
For 6 of 7 schemas, ADF and FBA versions are structurally identical. The only differences are:
- `$id` URI (ADF uses `https://agentic-development-framework.local/...`, FBA uses `https://opencode.ai/fba/...`)
- `title` string (ADF prefix vs FBA prefix)

These are namespace-only differences with zero structural impact.

### 3. One Filename Convention Difference (framework_state)
ADF uses `framework_state.schema.json` (without `.v2` suffix). FBA uses `framework_state.v2.schema.json`. The content is identical; the version is encoded in the `contract_name` field (`framework_state_v2`). This is a cosmetic naming choice with no impact on builder implementation.

### 4. No FBA/Odoo/Project-Specific Coupling
- No schema references `factory-build-agent`, `fba`, or `opencode.ai` in structural fields.
- No Odoo-specific terms, generator references, or template references.
- No project-specific directory assumptions in path patterns.
- All artifact ID patterns use generic prefixes (IMPL-, TEST-, REV-, GIT-, DEC-, FWSTATE-, SCAT-).

### 5. All Schemas Use Strict Validation
- `additionalProperties: false` on all schemas — no unknown fields tolerated.
- `const` for `contract_name` in all schemas — no ambiguity.
- `contract_version: "2.0"` consistently across all schemas.
- Conditional rules via `allOf/if/then` for contextual validation.

### 6. Zero Schemas Are Missing
No builder lacks its required schema. No schema is in draft, deprecated, or experimental status within ADF.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| ADF schemas are older than FBA schemas | None | — | All schemas are at contract_version 2.0, identical to FBA. No divergence detected. |
| FBA has evolved schemas with additional fields | None | — | Complete structural comparison shows zero field divergence. |
| Schema naming mismatches cause builder confusion | Low | Low | Only framework_state filename differs; content is identical. Builder references schema by `contract_name`, not filename. |
| Hidden FBA coupling in schema metadata | None | — | Only $id and title carry namespace differences. No structural coupling. |
| Builder needs fields not in ADF schema | Low | Low | Schemas are comprehensive for their artifact types. If a builder reveals gaps, that becomes a schema-governance phase, not an M5.x scope creep. |

## Recommendation

**CONTINUE WITH M5.7 AS PLANNED — NO SCHEMA ALIGNMENT PHASE REQUIRED.**

All 7 schemas for M5.7–M5.13 are present in ADF, structurally equivalent to the FBA originals, and free of project-specific coupling. A separate schema-alignment phase is unnecessary because:

1. Zero schemas are missing.
2. Zero schemas have diverged structurally.
3. Zero schemas contain FBA/Odoo coupling.
4. All schemas are at contract_version 2.0.
5. The only differences are namespace identifiers ($id, title) that do not affect builder contract shape.

## Next Phase Decision

| Decision | Rationale |
|----------|-----------|
| **Proceed to M5.7** | No blocking schema gaps. All M5.7–M5.13 schemas are ready. |
| ~~Insert schema-alignment phase~~ | Not needed. No misalignment detected. |
| ~~Block pending schema changes~~ | Not needed. All schemas are stable at v2.0. |

The next step is **M5.7** (build_implementation_report), followed sequentially through M5.13. The audit confirms M5.7–M5.13 can proceed without any preparatory schema work.

---

*Audit performed: 2026-05-16.*
*Scope: Read-only analysis. No schemas, builders, runtime, adapters, or source code modified.*
