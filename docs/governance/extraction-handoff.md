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

- `ab023d6` — 2026-05-16 — Define minimal builder invocation runtime strategy

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

## Current Commits

Recent relevant commits (M6.1, plus full M5 chain):

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
- Runtime is not created.
- Adapters are not created.
- Candidate mode is not active.
- `controlled_inspect` is not implemented.
- `controlled_commit` is not implemented.
- Builder invocation/runtime strategy exists as a design/governance document only (`docs/governance/minimal-builder-invocation-runtime-strategy.md`). No implementation.

## Next Phase

M7 — Agnostic dry-run design and evidence.

M6.1 is complete (design/governance document committed as `ab023d6`). The next phase must design the dry-run mode for the runtime before any implementation begins. M7 should:

- Design a dry-run mode that invokes builders without writing artifacts to disk.
- Define evidence collection: what traces, diffs, and validation reports a dry-run produces.
- Design the comparison method between agent-produced outputs and builder-produced outputs (semantic equivalence, not byte equality).
- Define how dry-run results inform future implementation decisions.
- Remain a design/governance phase: no runtime implementation yet.
- Follow the runtime boundary defined in `docs/governance/minimal-builder-invocation-runtime-strategy.md`.
- Not activate candidate or primary mode.
- Not modify builders, schemas, agents, or tests.

M8 remains the earliest proposed minimal runtime implementation phase, gated behind M7 approval and explicit owner authorization to write code outside `docs/governance/`.

## Explicit Do Not Do Yet

- Do not create more M5 builders (all 13 are complete).
- Do not modify existing builders.
- Do not modify tests.
- Do not modify schemas.
- Do not modify agents.
- Do not modify pyproject.toml.
- Do not create runtime.
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

## Recommended Order After M5

- M6.1 — Define minimal builder invocation/runtime strategy (design/governance only, no implementation). **COMPLETE.**
- M7 — Agnostic dry-run design and evidence (design/governance only).
- M8 — Minimal runtime implementation (earliest code phase after M7).
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
- M6.1 complete (commit `ab023d6`). Next phase: M7 (agnostic dry-run design/evidence).

## First Prompt For Next Session

```text
Read coordinator-contract.md and docs/governance/extraction-handoff.md. Continue from M7 — Agnostic dry-run design and evidence. M6.1 is complete (docs/governance/minimal-builder-invocation-runtime-strategy.md, commit ab023d6). Do not modify builders, tests, schemas, agents, or pyproject.toml. Do not create runtime or adapters. Do not activate candidate or primary mode. Follow the runtime boundary defined in docs/governance/minimal-builder-invocation-runtime-strategy.md.
```

## Risks

- Losing context and restarting wrong phase.
- Prematurely creating runtime before invocation strategy is designed.
- Copying FBA/Odoo coupling into runtime design.
- Accidentally activating candidate.
- Overengineering the runtime/invocation layer.
- Modifying builders, tests, or schemas during M6 (out of scope).
- Push remaining pending too long without review/commit.

## Usage

Read this document at the start of any new session until the extraction reaches candidate planning. It is a strict operational handoff, not an activation document, and it does not authorize new commitments outside the roadmap.
