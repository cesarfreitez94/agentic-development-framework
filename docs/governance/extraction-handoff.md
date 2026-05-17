# Extraction Handoff

## Purpose

This document preserves the current state, immediate roadmap, and continuation rules for extracting the meta-framework from `factory-build-agent` into `agentic-development-framework`. It is intended to let a future LLM/coordinator continue in a new session without relying on prior conversational context.

## Current Repository

- repo: `/home/cafl/projects/agentic-development-framework`
- branch: `main`
- current mode: bootstrap/shadow
- candidate mode: not active
- primary mode: not active
- controlled_inspect: not active
- controlled_commit: not active

## Source Repository

- source repo: `/home/cafl/projects/factory-build-agent`
- source status: original birthplace of the meta-framework
- future role: FBA adapter/use case, not core

## Completed Phases

- M1 — Bootstrap agentic-development-framework: created the independent ADF repo foundation and initial package/test structure.
- M1.5 — Strengthen coordinator contract: clarified coordinator authority, review gates, git lifecycle rules, and operating boundaries.
- M2 — Add ADF governance documents: added governance plans and implementation protocol for safe framework evolution.
- M3 — Add agnostic meta schemas: added project-agnostic schemas for meta-framework artifacts and schema tests.
- M4 — Migrate ADF OpenCode agents: 9 agents migrated, all tests pass, M4.final approved.
- M5 — Define ADF builder/runtime extraction strategy: design document produced.
- M5.audit — Remaining schema audit (M5.7–M5.13): confirmed all 7 schemas structurally identical to FBA originals, no alignment phase needed.
- M5.1 — build_intent: implemented and tested.
- M5.2 — build_policy_constraints: implemented and tested.
- M5.3 — build_roadmap_slice: implemented and tested.
- M5.4 — build_plan: implemented and tested.
- M5.5 — build_task_packet: implemented and tested.
- M5.6 — build_context_bundle: implemented and tested.
- M5.7 — build_implementation_report: implemented and tested.
- M5.8 — build_test_report: implemented and tested.
- M5.9 — build_review_report: implemented and tested.
- M5.10 — build_git_operation: implemented and tested.
- M5.11 — build_decisions: implemented and tested.
- M5.12 — build_framework_state: implemented and tested.
- M5.13 — build_schema_catalog: implemented and tested.
- M5 — FULLY COMPLETE. All 13 programmatic builders extracted, tested, and reviewed.
- M6.1 — Define minimal builder invocation/runtime strategy: design/governance document committed as `ab023d6`. Created `docs/governance/minimal-builder-invocation-runtime-strategy.md`. Defines the future minimal runtime as builder executor + artifact store + validation/evidence producer + framework_state update proposal producer. Runtime is explicitly non-autonomous and non-decision-making. No code, no runtime, no registry, no CLI, no adapters were created.
- M7.1 — Define agnostic dry-run design and evidence: design/governance document created as `docs/governance/agnostic-dry-run-design-and-evidence.md`. Defines a future/conceptual dry-run as caller-driven, non-persistent, evidence-producing only. M7 is complete as design/governance. Dry-run is design-only: no builder invocation, no artifact writes, no framework_state mutation, no git execution, no agent invocation, no mode activation. Semantic comparison is review-oriented and not automatic acceptance. Pipeline scenario is illustrative, not an autonomous runtime plan. M8 requires explicit owner authorization before any code-producing work.
- M8.1 — Implement minimal ADF runtime invocation: added `src/agentic_development_framework/runtime/__init__.py`, `src/agentic_development_framework/runtime/invocation.py`, `tests/test_runtime_invocation.py`, `tests/test_runtime_dry_run.py`. Runtime exposes `invoke_builder`. Runtime invokes explicitly selected builders via a static `_SUPPORTED_BUILDERS` mapping. Runtime validates produced artifacts against schemas and returns structured invocation evidence. Runtime supports dry-run evidence in memory without persistence, confirms no-write/no-git in dry-run evidence, and can optionally persist valid artifacts only when caller explicitly provides `store=True`, `artifact_root`, and `output_path`. Runtime produces `framework_state` proposal/preview only and does not mutate `framework_state`. Runtime remains minimal, non-autonomous, and does not invoke agents, execute git, or activate candidate or primary mode. Tests passed: 227.

## M4 Completion Record

- 9/9 agents present in `agents/opencode/`.
- Working tree clean after all M4 sub-phases.
- Forbidden grep clean (no FBA/Odoo coupling).
- Dangerous permissions safe (no edit/bash allow expansion).
- pytest 3 passed.
- Recommendation: APPROVE_M4_COMPLETE.

### M4 Commits

- `87c919f` M4.1 migrate foundational ADF opencode agents
- `4c38940` M4.2 migrate control planning ADF opencode agents
- `14b6370` M4.3 migrate context review ADF opencode agents
- `58faf54` M4.4 migrate ADF git operator opencode agent

### Migrated Agents

- `agents/opencode/orchestrator.md`
- `agents/opencode/intake.md`
- `agents/opencode/roadmap.md`
- `agents/opencode/policy.md`
- `agents/opencode/planner.md`
- `agents/opencode/packetizer.md`
- `agents/opencode/context-broker.md`
- `agents/opencode/reviewer.md`
- `agents/opencode/git-operator.md`

### Known Non-Blocking Gap

- `context-broker.md` lacks reciprocal "Relacion Con" sections for upstream/downstream documentation consistency.
- This is polish only and must not block M5.

## M5 Completion Record

All M5 phases complete. The full builder test suite passes with 215 tests.

### What M5 Produced (Programmatic Builders Only)

- 13 programmatic builders in `src/agentic_development_framework/builders/`
- 13 corresponding test files in `tests/test_build_*.py`
- All builders are pure, deterministic Python callables conforming to the contract shape in `docs/governance/builder-runtime-extraction-strategy.md`
- No runtime created.
- No adapters created.
- No registry created.
- No CLI created.
- No direct FBA builder copy (all builders derived from ADF schema contracts only).
- No schema mutation during builder phases (schemas untouched since M3).
- No agents modified.
- No pyproject.toml modified.

### M5 Commits

- `5bc29bf` Implement ADF schema catalog builder
- `d55e550` Implement ADF framework state builder
- `50b7a2e` Implement ADF decisions builder
- `f0efb16` Implement ADF git operation builder
- `aed76fb` Implement ADF review report builder
- `e47bf0c` Implement ADF test report builder
- `8fc124b` Implement ADF implementation report builder
- `98d7e6f` Audit remaining ADF meta schemas
- `288e05a` Implement ADF context bundle builder
- `55c1dcc` Implement ADF task packet builder
- `f10b123` Implement ADF plan builder
- `ef7dd0b` Implement ADF roadmap slice builder
- `6a56e1b` Implement ADF policy constraints builder
- `09742ca` Implement ADF intent builder
- `d28b620` Define ADF builder runtime extraction strategy

### Test Suite Evidence

- 215 tests passed (all tests in `tests/`).
- 212 builder tests across 13 test files.
- 3 schema/package tests (test_meta_schemas.py, test_package_import.py).
- All tests deterministic; all builders produce idempotent outputs.
- Zero FBA source references in any builder or test file.
- Zero forbidden files touched during any M5.x phase.

### Latest Local HEAD

- `7d6608f` — 2026-05-17 — Implement minimal ADF runtime invocation

## M6.1 Completion Record

M6.1 created `docs/governance/minimal-builder-invocation-runtime-strategy.md`, defining the design-only, governance-only strategy for a future minimal runtime. Committed as `ab023d6`.

### What M6.1 Produced

- One design/governance document (`docs/governance/minimal-builder-invocation-runtime-strategy.md`).
- No code, no runtime, no registry, no CLI, no adapters, no tests.

### Key M6.1 Decisions

1. **Runtime executes explicit caller-selected builder invocations only.** The runtime never selects builders, decides scope, gates, priority, or acceptance, nor invokes agents or activates modes.
2. **Inputs are explicit only.** No ambient reads, env vars, repo scanning, or hidden state.
3. **Invalid artifacts are not stored as canonical artifacts.** They may only be failure evidence or quarantine output.
4. **Runtime never mutates `framework_state` directly.** It produces update proposals only.
5. **Runtime may include `current_phase`/`status` updates only if explicitly supplied by caller/orchestrator.**
6. **Candidate and primary remain inactive.**
7. **No runtime, registry, CLI, adapters, tests, schemas, agents, or builders were changed.**

## M7.1 Completion Record

M7.1 created `docs/governance/agnostic-dry-run-design-and-evidence.md`, defining the design-only, governance-only plan for a future agnostic dry-run capability. M7 is complete as design/governance.

### What M7.1 Produced

- One design/governance document (`docs/governance/agnostic-dry-run-design-and-evidence.md`).
- No code, no runtime, no registry, no CLI, no adapters, no tests.
- No builder invocation, no artifact writes, no `.adf/` creation.

### Key M7.1 Decisions

1. **Dry-run is future/conceptual and design-only in M7.** No implementation exists and none is authorized.
2. **Dry-run evidence is in-memory / returned-to-caller only.** No canonical artifact writes, no persistent evidence files.
3. **No `framework_state` mutation.** State update proposals are previews only; nothing is applied.
4. **No git execution.** The dry-run must not run `git add`, `git commit`, `git push`, or any git command.
5. **No agent invocation.** No LLM agent invocation, no reasoning delegation.
6. **No mode activation.** Candidate and primary remain inactive; dry-run does not enable or imply any mode activation.
7. **Semantic comparison is review-oriented, not automatic acceptance.** Mismatch categories support human review; the dry-run never selects or substitutes artifacts automatically.
8. **Pipeline scenario is illustrative, not an autonomous runtime plan.** The 13-builder sequence in Section 8 is conceptual only; sequencing is always caller-directed.
9. **M8 requires explicit owner authorization before any code-producing work.** M7 approval does not automatically authorize M8 implementation.
10. **All M5 and M6 prohibitions remain active.** No runtime implementation, no registry, no CLI, no adapters, no builder/schema/agent/test modification, no FBA source inspection, no candidate or primary activation, no `controlled_inspect` or `controlled_commit` implementation.

## M8.1 Completion Record

M8.1 implemented the minimal ADF runtime invocation (`invoke_builder`). Committed as `7d6608f`.

### What M8.1 Produced

- `src/agentic_development_framework/runtime/__init__.py` — exports `invoke_builder`.
- `src/agentic_development_framework/runtime/invocation.py` — 478-line module implementing the full invocation contract.
- `tests/test_runtime_invocation.py` — tests for builder invocation, schema validation, evidence, failure model, persistence.
- `tests/test_runtime_dry_run.py` — tests for dry-run evidence, no-write/no-git confirmation.

### Key M8.1 Implementation Decisions

1. **Runtime exposes `invoke_builder` as single entry point.** The runtime is a Python callable, not an autonomous system.
2. **Runtime uses explicit static `_SUPPORTED_BUILDERS` mapping.** All 13 builders are registered in a hardcoded dict with callable, schema_path, artifact_type, id_field, and store_dir. No dynamic discovery, no registry infrastructure, no plugin loading.
3. **Runtime invokes explicitly selected builders only.** `builder_name` is a required parameter. The runtime never selects, discovers, or chains builders.
4. **Runtime validates produced artifacts against schemas.** Uses `jsonschema` Draft-07 validation with structured findings output (field, issue, severity).
5. **Runtime returns structured invocation evidence.** Success responses include artifact, validation, deterministic_check, comparison, state_update_proposal, no_write_confirmation, no_git_confirmation, timestamp. Failure responses include error_type and error_message with full structured evidence.
6. **Runtime supports dry-run evidence in memory without persistence.** When `dry_run=True`, no artifacts, validation reports, or state are written to disk. Evidence is returned to caller only. `no_write_confirmation` and `no_git_confirmation` are always `true` in dry-run mode.
7. **Runtime can optionally persist valid artifacts only when caller explicitly provides `store=True`, `artifact_root`, and `output_path`.** All three are required for persistence; missing any is an `OutputPathRequired` error. Output path must be under `artifact_root` or a `PathNotAllowedError` is raised.
8. **Runtime only produces `framework_state` proposal/preview and does not mutate `framework_state`.** The `state_update_proposal` includes `preview_only: true` and `applied: false`. Proposals include `add_artifact_refs` and optionally `set_current_phase`/`update_statuses` only when explicitly supplied by caller. Conflict detection records existing artifact IDs.
9. **Runtime follows M6.1 and M7.1 design.** The invocation contract (M6.1 Section 3.3), failure model (M6.1 Section 9), dry-run evidence model (M7.1 Section 5), non-persistence rules (M7.1 Section 6), and comparison model (M7.1 Section 7) are implemented as specified.

### Boundaries Preserved

- Runtime does **not** select builders, chain builders, or decide scope.
- Runtime does **not** invoke agents or LLM reasoning.
- Runtime does **not** execute git (`git add`, `git commit`, `git push`, or any git command).
- Runtime does **not** activate candidate mode or primary mode.
- Runtime does **not** implement `controlled_inspect` or `controlled_commit`.
- Runtime does **not** create a CLI, adapters, or builder registry.
- Runtime does **not** inspect or copy builders directly from FBA.
- Runtime does **not** create `.adf/` directories or `metadata.json`.
- Runtime does **not** mutate `framework_state` directly — only produces proposal/preview.

### Test Suite Evidence

- 227 tests passed (all tests in `tests/`).
- 212 builder tests across 13 test files.
- 3 schema/package tests.
- 12 runtime tests (test_runtime_invocation.py: 149 lines, test_runtime_dry_run.py: 68 lines).
- All tests deterministic. Zero forbidden files touched.

## Current Commits

Recent relevant commits (M7.1, M6.1, plus full M5 chain):

- `7d6608f` Implement minimal ADF runtime invocation (M8.1)
- `3b811a5` Define agnostic dry-run design and evidence (M7.1)
- `c300802` Update extraction handoff after M6.1 completion
- `ab023d6` Define minimal builder invocation runtime strategy (M6.1)
- `5bc29bf` Implement ADF schema catalog builder (M5.13)
- `d55e550` Implement ADF framework state builder (M5.12)
- `50b7a2e` Implement ADF decisions builder (M5.11)
- `f0efb16` Implement ADF git operation builder (M5.10)
- `aed76fb` Implement ADF review report builder (M5.9)
- `e47bf0c` Implement ADF test report builder (M5.8)
- `8fc124b` Implement ADF implementation report builder (M5.7)
- `98d7e6f` Audit remaining ADF meta schemas (M5.audit)
- `288e05a` Implement ADF context bundle builder (M5.6)
- `55c1dcc` Implement ADF task packet builder (M5.5)
- `f10b123` Implement ADF plan builder (M5.4)
- `ef7dd0b` Implement ADF roadmap slice builder (M5.3)
- `6a56e1b` Implement ADF policy constraints builder (M5.2)
- `09742ca` Implement ADF intent builder (M5.1)
- `d28b620` Define ADF builder runtime extraction strategy (M5)

## Current Assets In ADF

- `coordinator-contract.md`
- `docs/agents/agent-contract.md`
- `docs/governance/candidate-mode-plan.md`
- `docs/governance/implementation-protocol.md`
- `docs/governance/minimal-builder-invocation-runtime-strategy.md`
- `docs/governance/agnostic-dry-run-design-and-evidence.md`
- `docs/governance/builder-runtime-extraction-strategy.md`
- `docs/governance/m5-remaining-schema-audit.md`
- `schemas/meta/*.schema.json` (13 schema contracts)
- `src/agentic_development_framework/builders/__init__.py`
- `src/agentic_development_framework/builders/intent.py`
- `src/agentic_development_framework/builders/policy_constraints.py`
- `src/agentic_development_framework/builders/roadmap_slice.py`
- `src/agentic_development_framework/builders/plan.py`
- `src/agentic_development_framework/builders/task_packet.py`
- `src/agentic_development_framework/builders/context_bundle.py`
- `src/agentic_development_framework/builders/implementation_report.py`
- `src/agentic_development_framework/builders/test_report.py`
- `src/agentic_development_framework/builders/review_report.py`
- `src/agentic_development_framework/builders/git_operation.py`
- `src/agentic_development_framework/builders/decisions.py`
- `src/agentic_development_framework/builders/framework_state.py`
- `src/agentic_development_framework/builders/schema_catalog.py`
- `tests/test_meta_schemas.py`
- `tests/test_package_import.py`
- `tests/test_build_intent.py`
- `tests/test_build_policy_constraints.py`
- `tests/test_build_roadmap_slice.py`
- `tests/test_build_plan.py`
- `tests/test_build_task_packet.py`
- `tests/test_build_context_bundle.py`
- `tests/test_build_implementation_report.py`
- `tests/test_build_test_report.py`
- `tests/test_build_review_report.py`
- `tests/test_build_git_operation.py`
- `tests/test_build_decisions.py`
- `tests/test_build_framework_state.py`
- `tests/test_build_schema_catalog.py`
- `src/agentic_development_framework/runtime/__init__.py`
- `src/agentic_development_framework/runtime/invocation.py`
- `tests/test_runtime_invocation.py`
- `tests/test_runtime_dry_run.py`
- `agents/opencode/orchestrator.md`
- `agents/opencode/intake.md`
- `agents/opencode/roadmap.md`
- `agents/opencode/policy.md`
- `agents/opencode/planner.md`
- `agents/opencode/packetizer.md`
- `agents/opencode/context-broker.md`
- `agents/opencode/reviewer.md`
- `agents/opencode/git-operator.md`

## Not Yet Migrated / Not Yet Created

- Python programmatic builders are **fully migrated** (M5.1–M5.13 complete).
- Minimal runtime exists (M8.1): `invoke_builder` with static builder mapping, schema validation, structured evidence, dry-run support, and optional artifact persistence. No registry, no CLI, no adapters, no git execution, no agent invocation, no mode activation.
- Remaining M8 scope not yet implemented: artifact store layout (`.adf/`), `metadata.json` inventory, persistence beyond optional `store=True`.
- Adapters are not created.
- Candidate mode is not active.
- `controlled_inspect` is not implemented.
- `controlled_commit` is not implemented.
- Builder invocation/runtime strategy document exists (`docs/governance/minimal-builder-invocation-runtime-strategy.md`). M8.1 minimal runtime invocation is complete; broader runtime persistence/store capabilities remain incomplete and require separate authorization.
- Dry-run design and evidence strategy exists as a design/governance document only (`docs/governance/agnostic-dry-run-design-and-evidence.md`). Dry-run evidence production is implemented in M8.1 as an in-memory mode of `invoke_builder`; no persistent dry-run artifact store exists.

## Next Phase

M8.1 is complete as minimal runtime invocation (`7d6608f`). The runtime exposes `invoke_builder` with explicit static builder mapping, schema validation, structured evidence, dry-run support, and optional artifact persistence. Remaining M8 scope (artifact store layout, `metadata.json` inventory, full persistence) is proposed but **requires explicit owner authorization** before any further code-producing work.

**M8.1 does not automatically authorize further M8 sub-phases.** Any additional M8 implementation — artifact store layout (`.adf/`) creation, `metadata.json` inventory, builder registry, CLI, adapters, git execution, agent invocation, or mode activation — remains gated behind explicit owner authorization.

Until further M8 sub-phases are authorized, the next session continues with the existing minimal runtime boundaries. Do NOT create `.adf/` directories, registry, CLI, or adapters. Do NOT add git execution, agent invocation, or mode activation. Do NOT claim candidate or primary readiness.

Proposed M8 remainder scope (candidate, not authorized by this handoff):
- Implement the artifact store layout from M6.1 Section 4 (`.adf/artifacts/`, `metadata.json`).
- Implement cross-invocation artifact referencing and resolution.
- Implement validation report file persistence.
- Extend runtime tests for multi-invocation scenarios.
- No autonomous execution, no agent invocation, no git, no mode activation.

## Explicit Do Not Do Yet

- Do not create more M5 builders (all 13 are complete).
- Do not modify existing builders.
- Do not modify builder tests.
- Do not modify schemas.
- Do not modify agents.
- Do not modify pyproject.toml.
- Do not create `.adf/` artifact store directories or `metadata.json`.
- Do not create adapters.
- Do not create builder registry.
- Do not create builder CLI.
- Do not activate candidate.
- Do not activate primary.
- Do not implement `controlled_inspect`.
- Do not implement `controlled_commit`.
- Do not continue V2 development inside `factory-build-agent`.
- Do not copy FBA/Odoo-specific semantics into ADF core.
- Do not inspect FBA source.
- Do not begin further M8 sub-phases without explicit owner authorization.

## Recommended Order After M5

- M6.1 — Define minimal builder invocation/runtime strategy (design/governance only, no implementation). **COMPLETE.**
- M7 — Agnostic dry-run design and evidence (design/governance only). **COMPLETE.**
- M8 — Minimal runtime implementation (earliest code phase after M7). **M8.1 COMPLETE.** Remaining M8 sub-phases **require explicit owner authorization.**
- M9 — FBA adapter notes (adapter layer, not core).

## Coordination Rules

- Follow `coordinator-contract.md`.
- Owner controls product direction and promotion.
- Coordinator designs phases, prompts, gates, review, and git instructions.
- Agents execute bounded tasks.
- No commits without review.
- No `git add .`.
- Stop on forbidden files.
- Declare `capability_gap` if no capability fits.
- Block out-of-context requests.
- Keep changes small and reversible.

## M5 Closeout Notes

- Push remains pending by owner policy until M5 closeout is reviewed and committed.
- All 13 builders follow the contract shape in `docs/governance/builder-runtime-extraction-strategy.md`.
- No builder violates the anti-overengineering rules (no base class, no DI, no plugin system, no middleware, no CLI, no async, no web API, no caching).
- Working tree is clean.
- M6.1 complete (commit `ab023d6`). M7.1 complete (commit `3b811a5`). M8.1 complete (commit `7d6608f`). Next phase: remaining M8 sub-phases (proposed, requires explicit owner authorization).
- Tests: 227 passed (M5: 215 builder/schema tests; M8.1: +12 runtime/dry-run tests).

## First Prompt For Next Session

```text
Read coordinator-contract.md and docs/governance/extraction-handoff.md. M8.1 is complete as minimal runtime invocation (commit 7d6608f). The runtime exposes invoke_builder with explicit static builder mapping, schema validation, structured evidence, dry-run support, and optional artifact persistence. Runtime remains minimal and non-autonomous. Remaining M8 sub-phases (artifact store layout, .adf/ creation, metadata.json, full persistence) are proposed but require explicit owner authorization before any further code-producing work. If the owner has not authorized further M8 sub-phases, do NOT create .adf/ directories, registry, CLI, or adapters. Do NOT add git execution, agent invocation, or mode activation. Do NOT claim production, candidate, primary, stable, autonomous, or canonical readiness.
```

## Risks

- Losing context and restarting wrong phase.
- Starting further M8 sub-phases without owner authorization (gated).
- Creating `.adf/` artifact store or registry prematurely.
- Copying FBA/Odoo coupling into runtime design.
- Accidentally activating candidate or primary.
- Overengineering the runtime/invocation layer beyond M6.1/M7.1 design.
- Modifying builders, tests, or schemas during runtime phases.
- Push remaining pending too long without review/commit.
- Skipping M8 sub-phase authorization gate and implementing artifact store without owner approval.

## Usage

Read this document at the start of any new session until the extraction reaches candidate planning. It is a strict operational handoff, not an activation document, and it does not authorize new commitments outside the roadmap.
