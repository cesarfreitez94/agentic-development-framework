# Extraction Handoff

## Purpose

This document preserves the current state, immediate roadmap, and continuation rules for `agentic-development-framework`, originally extracted from `factory-build-agent` and now governed as an agnostic framework. It is intended to let a future LLM/coordinator continue in a new session without relying on prior conversational context.

## Current Repository

- repo: `/home/cafl/projects/agentic-development-framework`
- branch: `main`
- current mode: bootstrap/shadow
- candidate mode: not active
- primary mode: not active
- controlled_inspect: not active
- controlled_commit: not active
- latest HEAD/origin main at M8.3 start: `b2b18fb` (`Update extraction handoff after M8.1 completion`)

## Current Milestone State

- M8.1 is complete, committed, and pushed as `7d6608f`.
- M8.2 is complete, committed, and pushed as `b2b18fb`.
- M8.3 persisted the repository assessment roadmap and coordinator protocol before any implementation or adapter work.
- M9 is repository assessment and ADF readiness review; recent repository history records follow-up M9 assessment work.
- M10.0 persists the OpenCode-operated, contract-driven, project-agnostic ADF direction in this handoff.
- The next phase is an agnostic OpenCode-compatible audit/adaptation phase, not FBA integration and not autonomous-runtime evaluation.

## Source Repository

- source repo: `/home/cafl/projects/factory-build-agent`
- source status: original birthplace of the meta-framework
- future role: historical birthplace and possible consumer-project example only; not core, not dependency, and not exclusive target

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
- M8.2 — Update extraction handoff after M8.1 completion: complete, committed, and pushed as `b2b18fb` (`Update extraction handoff after M8.1 completion`). Latest HEAD/origin main was `b2b18fb` when M8.3 began.
- M8.3 — Persist repository assessment roadmap and coordinator protocol: documentation/governance-only phase that records M9 as repository assessment/readiness review before any adapter or specific consumer-project work. No runtime features, adapters, CLI, tests, schemas, agents, README update, assessment files, or `.adf/` artifact store are created by M8.3.
- M10.0 — Persist OpenCode-operated ADF direction in handoff: documentation/governance-only phase that records ADF as an agnostic, contract-driven framework operated through OpenCode conventions. No commands, agents, templates, CLI, runner, git automation, candidate/primary mode, `.opencode/`, or `.adf/` structure are implemented by M10.0.

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

### Latest HEAD / Origin Main Baseline

- `b2b18fb` — 2026-05-17 — Update extraction handoff after M8.1 completion. This was the latest `HEAD`/`origin/main` when M8.3 began.

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

M8.1 implemented the minimal ADF runtime invocation (`invoke_builder`). It is complete, committed, and pushed as `7d6608f`.

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

## M8.2 Completion Record

M8.2 updated this extraction handoff after M8.1 completion. It is complete, committed, and pushed as `b2b18fb` (`Update extraction handoff after M8.1 completion`). At the start of M8.3, `b2b18fb` was the latest `HEAD`/`origin/main`.

### What M8.2 Produced

- Updated `docs/governance/extraction-handoff.md` to preserve M8.1 status, runtime boundaries, and next-phase gates.
- No source, test, schema, agent, adapter, CLI, or runtime behavior changes.

## M8.3 Completion Record

M8.3 persists the owner/coordinator decision that repository assessment/readiness review must precede any adapter or specific consumer-project work. M8.3 is documentation/governance only and does not authorize implementation.

### What M8.3 Produces

- Updates `coordinator-contract.md` with a repository assessment protocol for clean-context assessment phases.
- Updates this handoff to define M9 as repository assessment and ADF readiness review.
- Moves previous adapter-focused work out of M9 and keeps it unauthorized until a separate owner decision.
- Creates no assessment artifacts, runtime features, adapters, CLI, `.adf/` artifact store, source changes, test changes, schema changes, agent changes, or README update.

### Key M8.3 Decisions

1. M9 is now `M9 — Repository assessment and ADF readiness review`.
2. Previous adapter-focused work is not part of M9 and remains unauthorized until a separate owner decision.
3. Before connecting ADF to any consumer project or adapter, the repo needs an evidence-based assessment of actual current capabilities, gaps, risks, readiness, documentation accuracy, and governance consistency.
4. M9 is review/governance/documentation only unless explicitly authorized otherwise.
5. M9.1 is the next proposed phase, but it is not automatically implemented by this handoff.

## M10.0 Architectural Direction Record

M10.0 persists the owner/coordinator decision that ADF must be a project-agnostic, contract-driven framework operated through OpenCode conventions. This is a documentation/governance-only phase and does not authorize implementation.

### Official OpenCode Rules Confirmed

The M10.0 decision was checked against the official OpenCode documentation for agents, commands, rules, and config:

- `https://opencode.ai/docs/agents/`
- `https://opencode.ai/docs/commands/`
- `https://opencode.ai/docs/rules/`
- `https://opencode.ai/docs/config/`

Relevant confirmed rules:

1. OpenCode distinguishes primary agents and subagents.
2. Markdown agents may exist globally in `~/.config/opencode/agents/` or per project in `.opencode/agents/`.
3. The markdown agent file name defines the agent name.
4. Markdown commands may exist globally in `~/.config/opencode/commands/` or per project in `.opencode/commands/`.
5. The markdown command file name defines the command name.
6. Project rules may live in `AGENTS.md` at the project root.
7. Global rules may live in `~/.config/opencode/AGENTS.md`.
8. OpenCode config supports global config, project config, and `.opencode` directories, with plural subdirectories such as `agents/` and `commands/`.

### M10.0 Direction

1. **ADF is OpenCode-operated, not an OpenCode replacement.** ADF must use OpenCode's existing rules, agents, commands, and config conventions instead of defining a competing control plane.
2. **ADF is contract-driven and project-agnostic.** ADF contracts, governance, and future guidance must apply to any consumer project. FBA remains a historical birthplace and possible example only, not a dependency or exclusive target.
3. **ADF is not evaluated as an autonomous runtime in this stage.** Existing `invoke_builder` behavior remains a minimal, caller-directed builder invocation capability. Any broader runtime, runner, orchestration, or artifact-store behavior is future optional work and requires separate authorization.
4. **Consumer projects should stay OpenCode-compatible.** ADF should be usable through project rules in `AGENTS.md`, project agents in `.opencode/agents/`, project commands in `.opencode/commands/`, global agents in `~/.config/opencode/agents/`, global commands in `~/.config/opencode/commands/`, and future local traceability under a project-owned structure such as `.adf/`.
5. **Traceability is future local project state, not current implementation.** A future `.adf/`-style structure may hold project-local traceability if separately authorized. M10.0 does not create it.
6. **The next phase is agnostic OpenCode-compatible audit/adaptation.** The next phase must audit and adapt ADF governance/documentation against OpenCode-compatible usage for any consumer project. It is not FBA integration.

### M10.0 Non-Authorization

M10.0 does not authorize commands, agents, templates, CLI, runner, git automation, candidate mode, primary mode, autonomous runtime behavior, adapter implementation, `.opencode/` creation, `.adf/` creation, schema changes, code changes, tests, README changes, or global OpenCode installation/configuration.

## Current Commits

Recent relevant commits:

- `b2b18fb` Update extraction handoff after M8.1 completion (M8.2; latest HEAD/origin main when M8.3 began)
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
- Remaining M8 runtime/persistence scope is not authorized by this handoff: artifact store layout (`.adf/`), `metadata.json` inventory, and persistence beyond optional `store=True` remain gated.
- M10.0 does not create or modify repository assessment artifacts; any M9 assessment artifacts remain governed by their own completed phases.
- Adapters are not created. Consumer-project adapter or integration work is future optional and is not authorized by this handoff.
- ADF is not claimed production-ready and is not claimed ready for integration into any specific consumer project.
- ADF is not FBA-specific. FBA is only a historical birthplace and possible example consumer project.
- Candidate mode is not active.
- `controlled_inspect` is not implemented.
- `controlled_commit` is not implemented.
- Builder invocation/runtime strategy document exists (`docs/governance/minimal-builder-invocation-runtime-strategy.md`). M8.1 minimal runtime invocation is complete; broader runtime persistence/store capabilities remain incomplete and require separate authorization.
- Dry-run design and evidence strategy exists as a design/governance document only (`docs/governance/agnostic-dry-run-design-and-evidence.md`). Dry-run evidence production is implemented in M8.1 as an in-memory mode of `invoke_builder`; no persistent dry-run artifact store exists.

## Next Phase

M10.0 is the current documentation/governance-only handoff update. It records that ADF is an OpenCode-operated, contract-driven, project-agnostic framework.

The next proposed phase is an agnostic OpenCode-compatible audit/adaptation phase. Its purpose is to check ADF governance, documentation, contracts, and future guidance against official OpenCode conventions for any consumer project.

The next phase is not FBA integration. It must not implement runtime features, create adapters, create commands, create agents, create templates, create CLI, create a runner, activate candidate or primary mode, add git automation, add agent invocation, mutate `framework_state`, or create `.opencode/` or `.adf/` structures unless separately authorized.

FBA may remain a historical example, but no next-phase work may treat FBA as a dependency, exclusive target, or required integration path.

## Explicit Do Not Do Yet

- Do not create more M5 builders (all 13 are complete).
- Do not modify existing builders.
- Do not modify builder tests.
- Do not modify schemas.
- Do not modify agents.
- Do not modify pyproject.toml.
- Do not create `.adf/` artifact store directories or `metadata.json` unless separately authorized.
- Do not create assessment files before an explicit M9 subphase prompt authorizes them.
- Do not create `docs/governance/assessment/**` or `docs/governance/repository-assessment.md` during M8.3.
- Do not start any next phase unless the owner explicitly authorizes it.
- Do not treat M9 as an implementation phase.
- Do not implement runtime features during M9 unless explicitly authorized otherwise.
- Do not create adapters or integrations for any specific consumer project.
- Do not create OpenCode commands, agents, templates, CLI, runner, or git automation.
- Do not create `.opencode/` or install/write global OpenCode config.
- Do not create builder registry.
- Do not create builder CLI.
- Do not activate candidate.
- Do not activate primary.
- Do not add git execution.
- Do not add agent invocation.
- Do not mutate `framework_state`.
- Do not implement `controlled_inspect`.
- Do not implement `controlled_commit`.
- Do not continue V2 development inside `factory-build-agent`.
- Do not copy FBA/Odoo-specific semantics into ADF core.
- Do not inspect FBA source or treat FBA as a dependency, exclusive target, or required integration path.
- Do not begin further M8 sub-phases without explicit owner authorization.
- Do not begin consumer-project adapter boundary or adapter notes without explicit owner authorization.
- Do not claim the repository is production-ready.
- Do not claim ADF is ready for any specific consumer-project integration.

## Recommended Order

- M6.1 — Define minimal builder invocation/runtime strategy (design/governance only, no implementation). **COMPLETE.**
- M7 — Agnostic dry-run design and evidence (design/governance only). **COMPLETE.**
- M8.1 — Minimal runtime invocation. **COMPLETE, COMMITTED, PUSHED.**
- M8.2 — Extraction handoff update after M8.1. **COMPLETE, COMMITTED, PUSHED.**
- M8.3 — Repository assessment roadmap and coordinator protocol. Documentation/governance only; no runtime behavior changes. **COMPLETE when this handoff and coordinator contract are reviewed, committed, and pushed.**
- M9 — Repository assessment and ADF readiness review. Assessment history is outside M10.0 scope and is not modified here.
- M9.1 — Repository map assessment.
- M9.2 — Governance and milestone consistency assessment.
- M9.3 — Code/runtime/schema assessment.
- M9.4 — Tests/agents/documentation assessment.
- M9.5 — Consolidated repository assessment + README/handoff update.
- M10.0 — Persist OpenCode-operated ADF direction in handoff. Documentation/governance only; no implementation. **CURRENT PHASE.**
- Next proposed phase — Agnostic OpenCode-compatible audit/adaptation. **NOT AUTOMATICALLY STARTED; NOT FBA INTEGRATION.**
- Consumer-project adapter or integration work. **FUTURE OPTIONAL; NOT AUTHORIZED.**

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
- M6.1 complete (commit `ab023d6`). M7.1 complete (commit `3b811a5`). M8.1 complete and pushed (commit `7d6608f`). M8.2 complete and pushed (commit `b2b18fb`). Next proposed phase: M9 repository assessment and ADF readiness review. M9.1 requires explicit owner authorization and is not automatically started.
- Tests: 227 passed (M5: 215 builder/schema tests; M8.1: +12 runtime/dry-run tests).

## First Prompt For Next Session

```text
Read coordinator-contract.md and docs/governance/extraction-handoff.md.

Continue from M10.0 — OpenCode-operated ADF direction persisted in handoff.

M8.1 is complete and pushed: minimal ADF runtime invocation.
M8.2 is complete and pushed: extraction handoff updated after M8.1.
M8.3 is complete and pushed: repository assessment roadmap and coordinator protocol persisted.
M10.0 is documentation/governance only: ADF is now explicitly recorded as an OpenCode-operated, contract-driven, project-agnostic framework.

ADF is not FBA-specific, not an OpenCode replacement, and not being evaluated as an autonomous runtime in this stage. FBA is a historical birthplace and possible example only, not a dependency or exclusive target.

Before authorizing the next phase:
1. Verify branch and git status.
2. Read the current coordinator contract and handoff.
3. Confirm the scope is agnostic OpenCode-compatible audit/adaptation:
   - contrast ADF governance/documentation/contracts against official OpenCode conventions,
   - preserve OpenCode-compatible project rules, agents, commands, and config structure,
   - no README update,
   - no source/test/schema/agent changes,
   - no implementation,
   - no commands, agents, templates, CLI, runner, git automation, `.opencode/`, or `.adf/` creation,
   - no adapter work and no FBA integration.
4. Produce or approve the exact next-phase OpenCode prompt.
5. Do not allow the next phase to proceed unless owner explicitly authorizes it.

Repo:
https://github.com/cesarfreitez94/agentic-development-framework
```

## Risks

- Losing context and restarting wrong phase.
- Starting M9.1 without explicit owner authorization.
- Treating M9 repository assessment as implementation work.
- Running one giant all-context assessment instead of clean-context subphases.
- Creating assessment artifacts before a specific M9 subphase authorizes them.
- Starting further M8 runtime/persistence sub-phases without owner authorization.
- Starting consumer-project adapter work without owner authorization.
- Creating `.adf/` artifact store or registry prematurely.
- Copying FBA/Odoo coupling into runtime design.
- Treating FBA as a dependency, exclusive target, or required integration path.
- Treating ADF as a replacement for OpenCode instead of an OpenCode-operated framework.
- Evaluating or presenting ADF as an autonomous runtime at this stage.
- Accidentally activating candidate or primary.
- Overengineering the runtime/invocation layer beyond M6.1/M7.1 design.
- Modifying builders, tests, or schemas during runtime phases.
- Skipping M8 sub-phase authorization gate and implementing artifact store without owner approval.
- Inventing issues, gaps, readiness claims, or production-readiness conclusions without evidence.
- Claiming ADF is production-ready or ready for any specific consumer-project integration without code, tests, docs, and governance support.
- Skipping coordinator review before committing an assessment subphase.

## Usage

Read this document at the start of any new session until the extraction reaches candidate planning. It is a strict operational handoff, not an activation document, and it does not authorize new commitments outside the roadmap.
