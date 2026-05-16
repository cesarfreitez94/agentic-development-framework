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

## Current Commits

Recent relevant commits:

- `3d2cfda` Add agnostic meta schemas
- `c287c74` Add ADF governance documents
- `f224656` Strengthen coordinator contract
- `532fb2b` Bootstrap agentic development framework

## Current Assets In ADF

- `coordinator-contract.md`
- `docs/agents/agent-contract.md`
- `docs/governance/candidate-mode-plan.md`
- `docs/governance/implementation-protocol.md`
- `schemas/meta/*.schema.json`
- `tests/test_meta_schemas.py`
- `tests/test_package_import.py`

## Not Yet Migrated

- ADF/OpenCode agents are not migrated yet.
- Python builders/utilities are not migrated yet.
- Runtime is not created.
- Adapters are not created.
- Candidate mode is not active.
- `controlled_inspect` is not implemented.
- `controlled_commit` is not implemented.

## Next Phase

M4 — Migrate ADF OpenCode agents.

Source routes:

- `/home/cafl/projects/factory-build-agent/.opencode/agents/framework-v2-orchestrator.md`
- `/home/cafl/projects/factory-build-agent/.opencode/agents/framework-v2-intake.md`
- `/home/cafl/projects/factory-build-agent/.opencode/agents/framework-v2-roadmap.md`
- `/home/cafl/projects/factory-build-agent/.opencode/agents/framework-v2-policy.md`
- `/home/cafl/projects/factory-build-agent/.opencode/agents/framework-v2-planner.md`
- `/home/cafl/projects/factory-build-agent/.opencode/agents/framework-v2-packetizer.md`
- `/home/cafl/projects/factory-build-agent/.opencode/agents/framework-v2-context-broker.md`
- `/home/cafl/projects/factory-build-agent/.opencode/agents/framework-v2-reviewer.md`
- `/home/cafl/projects/factory-build-agent/.opencode/agents/framework-v2-git-operator.md`

Destination routes:

- `agents/opencode/orchestrator.md`
- `agents/opencode/intake.md`
- `agents/opencode/roadmap.md`
- `agents/opencode/policy.md`
- `agents/opencode/planner.md`
- `agents/opencode/packetizer.md`
- `agents/opencode/context-broker.md`
- `agents/opencode/reviewer.md`
- `agents/opencode/git-operator.md`

## Required Adaptation For M4

- `framework-v2-*` must become ADF agents.
- FBA must be replaced with ADF or generic project wording.
- V1 FBA authority must be replaced with current bootstrap / existing project authority.
- Odoo generator/templates/runtime must be generalized to adapters/generators/templates/runtime.
- `.factory/meta/session_notes` must be replaced with `docs/governance` and `docs/agents`.
- `src/fba` must be replaced with `src/agentic_development_framework` when applicable.
- Candidate/primary/`controlled_inspect`/`controlled_commit` must remain inactive.
- Do not change permissions to edit/bash allow.

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

## Recommended Order After M4

- M5 — Migrate Python builders/utilities one by one.
- M5.1 — `intent_builder`.
- M5.2 — `policy_constraints`.
- M5.3 — `plan_builder`.
- M5.4 — `task_packet_builder`.
- M5.5 — `context_broker`.
- M5.6 — `roadmap_slice_builder`.
- M6 — Builder tests and schema validation.
- M7 — Agnostic dry-run.
- M8 — FBA adapter notes.

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

## Definition Of Done For M4

- 9 agents migrated to `agents/opencode`.
- Agents are ADF/generic, not FBA core.
- No candidate/primary activation.
- No bash/edit permission expansion.
- Tests still pass.
- grep for FBA/Odoo coupling reviewed.
- Commit created only after review.

## First Prompt For Next Session

```text
Read coordinator-contract.md and docs/governance/extraction-handoff.md. Continue from M4 — Migrate ADF OpenCode agents. Do not migrate builders yet.
```

## Risks

- Losing context and restarting wrong phase.
- Migrating utilities before agents.
- Copying FBA/Odoo coupling into ADF core.
- Accidentally activating candidate.
- Creating broad agents or superagents.
- Overengineering before M4.

## Usage

Read this document at the start of any new session until the extraction reaches candidate planning. It is a strict operational handoff, not an activation document, and it does not authorize new commitments outside the roadmap.
