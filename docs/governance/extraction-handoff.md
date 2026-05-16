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
- M5 — Define ADF builder/runtime extraction strategy: design document produced, no implementation, no builder migration, no runtime created.

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

- `docs/governance/builder-runtime-extraction-strategy.md` created with all 16 required sections.
- Strategy defines: builder definition, contract shape, schema consumption, core vs adapter boundary, candidate builder list (13 builders across M5.1–M5.13), runtime boundary, migration checklist, review gates, stop conditions, risks, anti-overengineering rules, and next phases.
- No implementation, no builder migration, no runtime created.
- No FBA builder copying.
- No forbidden files touched.
- Pending coordinator review and owner approval before M5.1.
- Coordinator review: requested changes before approval.

### M5 Commit

- (pending review approval — no commit created yet)

## Current Commits

Recent relevant commits:

- `58faf54` M4.4 migrate ADF git operator opencode agent
- `14b6370` M4.3 migrate context review ADF opencode agents
- `4c38940` M4.2 migrate control planning ADF opencode agents
- `87c919f` M4.1 migrate foundational ADF opencode agents
- `3d2cfda` Add agnostic meta schemas
- `c287c74` Add ADF governance documents
- `f224656` Strengthen coordinator contract

## Current Assets In ADF

- `coordinator-contract.md`
- `docs/agents/agent-contract.md`
- `docs/governance/candidate-mode-plan.md`
- `docs/governance/implementation-protocol.md`
- `docs/governance/builder-runtime-extraction-strategy.md`
- `schemas/meta/*.schema.json`
- `tests/test_meta_schemas.py`
- `tests/test_package_import.py`
- `agents/opencode/orchestrator.md`
- `agents/opencode/intake.md`
- `agents/opencode/roadmap.md`
- `agents/opencode/policy.md`
- `agents/opencode/planner.md`
- `agents/opencode/packetizer.md`
- `agents/opencode/context-broker.md`
- `agents/opencode/reviewer.md`
- `agents/opencode/git-operator.md`

## Not Yet Migrated

- Python builders/utilities are not migrated yet.
- Builders must not be copied directly from FBA without a clean extraction strategy (strategy now defined in M5).
- Builder extraction strategy is complete; individual builder extraction begins at M5.1.
- Runtime is not created.
- Adapters are not created.
- Candidate mode is not active.
- `controlled_inspect` is not implemented.
- `controlled_commit` is not implemented.

## Next Phase

M5.1 — Design and implement `build_intent`, the first ADF programmatic builder.

M5.1 is the first implementation phase after M5 strategy approval. It must:

- Design `build_intent` from `schemas/meta/intent.schema.json`.
- Implement the builder as a pure, deterministic Python callable.
- Include schema validation tests.
- Follow the builder contract shape defined in `docs/governance/builder-runtime-extraction-strategy.md`.
- Pass all M5.x review gates (G1–G7).
- Touch only allowed files (builder file, test file, possibly `src/adf/` structure).
- Not reference FBA source code.
- Not create runtime or adapters.
- Not activate candidate or primary mode.

## Explicit Do Not Do Yet

- Do not migrate Python builders before agents.
- Do not migrate `meta_workflow_migration.py` yet.
- Do not create runtime.
- Do not create adapters.
- Do not activate candidate.
- Do not activate primary.
- Do not implement `controlled_inspect`.
- Do not implement `controlled_commit`.
- Do not continue V2 development inside `factory-build-agent`.
- Do not copy FBA/Odoo-specific semantics into ADF core.

## Recommended Order After M5.1

- M5.2 — Design and implement `build_policy_constraints`.
- M5.3 — Design and implement `build_roadmap_slice`.
- M5.4 — Design and implement `build_plan`.
- M5.5 — Design and implement `build_task_packet`.
- M5.6 — Design and implement `build_context_bundle`.
- M5.7 — Design and implement `build_implementation_report`.
- M5.8 — Design and implement `build_test_report`.
- M5.9 — Design and implement `build_review_report`.
- M5.10 — Design and implement `build_git_operation`.
- M5.11 — Design and implement `build_decisions`.
- M5.12 — Design and implement `build_framework_state`.
- M5.13 — Design and implement `build_schema_catalog`.
- M6 — Builder tests and schema validation hardening.
- M7 — Agnostic dry-run.
- M8 — Minimal runtime design and implementation.
- M9 — FBA adapter notes.

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

## Definition Of Done For M5.1

- `build_intent` Python callable implemented in `src/adf/builders/`.
- Schema validation test passes against `schemas/meta/intent.schema.json`.
- Determinism test passes (same input × 3 = same output).
- Error handling test passes (invalid input → `ValueError`, invalid output → `SchemaValidationError`).
- No FBA source references in builder code or tests.
- No forbidden files touched.
- `pyproject.toml` updated only if new test dependencies are needed (requires prior approval).
- Coordinator review approved.
- Working tree clean or pending work explicit.

## First Prompt For Next Session

```text
Read coordinator-contract.md and docs/governance/extraction-handoff.md. Continue from M5.1 — Design and implement build_intent, the first ADF programmatic builder. Follow docs/governance/builder-runtime-extraction-strategy.md for contract shape, review gates, and stop conditions. Do not reference FBA source code. Do not create runtime or adapters. Do not activate candidate or primary mode.
```

## Risks

- Losing context and restarting wrong phase.
- Migrating utilities before agents.
- Copying FBA/Odoo coupling into ADF core.
- Accidentally activating candidate.
- Creating broad agents or superagents.
- Overengineering before M5 design is approved.

## Usage

Read this document at the start of any new session until the extraction reaches candidate planning. It is a strict operational handoff, not an activation document, and it does not authorize new commitments outside the roadmap.
