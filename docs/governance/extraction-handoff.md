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
- Builders must not be copied directly from FBA without a clean extraction strategy.
- Runtime is not created.
- Adapters are not created.
- Candidate mode is not active.
- `controlled_inspect` is not implemented.
- `controlled_commit` is not implemented.

## Next Phase

M5 — Define ADF builder/runtime extraction strategy.

M5 is design/governance only. No implementation, no builder migration, no runtime creation.

Builders must not be copied directly from FBA without a clean extraction strategy.

M5 must decide:

- Which builders truly belong in ADF.
- Which builders are conceptual vs necessary.
- Which schemas/contracts govern each builder.
- What minimal runtime is required.
- What remains out of scope to avoid copying FBA/Odoo semantics.
- How the agentic pipeline connects to future real execution.

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

## Recommended Order After M5

- M6 — Implement approved builders one by one.
- M7 — Builder tests and schema validation.
- M8 — Agnostic dry-run.
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

## Definition Of Done For M5

- Design document produced (design/architectural decision document).
- Builder inventory decided (which are in ADF, which deferred, which out of scope).
- Schema/contract map per builder.
- Minimal runtime boundary defined.
- Out-of-scope boundaries documented (no FBA/Odoo semantics).
- Agentic pipeline → real execution connection sketched.
- No implementation, no code migration, no runtime created.

## First Prompt For Next Session

```text
Read coordinator-contract.md and docs/governance/extraction-handoff.md. Continue from M5 — Define ADF builder/runtime extraction strategy. M5 is design/governance only. Do not migrate builders, do not create runtime. Do not copy builders directly from FBA without a clean extraction strategy.
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
