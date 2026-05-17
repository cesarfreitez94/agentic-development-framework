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

## Current Commits

Recent relevant commits (M7.1, M6.1, plus full M5 chain):

- *(pending)* Docs/governance/agnostic-dry-run-design-and-evidence (M7.1) — uncommitted, on disk
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
- Dry-run design and evidence strategy exists as a design/governance document only (`docs/governance/agnostic-dry-run-design-and-evidence.md`). No implementation.

## Next Phase

M8 — Minimal runtime implementation (candidate/proposed, not authorized by this handoff).

M7 is complete as design/governance (`docs/governance/agnostic-dry-run-design-and-evidence.md`). M7.1 defined the dry-run evidence model, comparison method, non-persistence rules, and failure model — all design-only, no implementation. M7.1 is approved. This handoff records M7 completion only; it does not authorize M8.

**M8 is the earliest proposed minimal runtime implementation phase, gated behind explicit owner authorization.** M7 approval does not automatically authorize M8 implementation. M8 must not begin until the owner explicitly authorizes code-producing work outside `docs/governance/`.

Until M8 is authorized, the next session continues as design/governance only. Do NOT create runtime code, `.adf/` directories, registry, CLI, or adapters. Do NOT invoke builders. Do NOT activate candidate or primary mode.

M8 candidate scope, not authorized by this handoff:
- Implement the minimal runtime as a Python module in `src/agentic_development_framework/`.
- Implement the invocation contract from M6.1 Section 3.3.
- Implement the artifact store layout from M6.1 Section 4.
- Implement the dry-run evidence contract from M7.1.
- Implement schema validation integration.
- Implement `framework_state` update proposal generation.
- Implement the failure model from M6.1 Section 9.
- Write runtime-specific tests (separate from builder tests).
- No autonomous execution, no agent invocation, no git, no mode activation.

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
- Do not begin M8 implementation without explicit owner authorization.

## Recommended Order After M5

- M6.1 — Define minimal builder invocation/runtime strategy (design/governance only, no implementation). **COMPLETE.**
- M7 — Agnostic dry-run design and evidence (design/governance only). **COMPLETE.**
- M8 — Minimal runtime implementation (earliest code phase after M7). **Requires explicit owner authorization.**
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
- M6.1 complete (commit `ab023d6`). M7.1 complete (docs/governance/agnostic-dry-run-design-and-evidence.md, pending commit). Next phase: M8 (minimal runtime implementation, requires explicit owner authorization).

## First Prompt For Next Session

```text
Read coordinator-contract.md and docs/governance/extraction-handoff.md. M7 is complete as design/governance (docs/governance/agnostic-dry-run-design-and-evidence.md). M8 is the next proposed phase (minimal runtime implementation) but requires explicit owner authorization before any code-producing work begins. If the owner has not authorized M8, continue as design/governance only. Do NOT create runtime code, .adf/ directories, registry, CLI, or adapters. Do NOT invoke builders. Do NOT activate candidate or primary mode. Do NOT claim production, candidate, primary, stable, autonomous, or canonical readiness.
```

## Risks

- Losing context and restarting wrong phase.
- Prematurely creating runtime without owner authorization (M8 gated).
- Copying FBA/Odoo coupling into runtime design.
- Accidentally activating candidate or primary.
- Overengineering the runtime/invocation layer.
- Modifying builders, tests, or schemas during design/governance phases.
- Push remaining pending too long without review/commit.
- Skipping M8 authorization gate and implementing runtime without owner approval.

## Usage

Read this document at the start of any new session until the extraction reaches candidate planning. It is a strict operational handoff, not an activation document, and it does not authorize new commitments outside the roadmap.
