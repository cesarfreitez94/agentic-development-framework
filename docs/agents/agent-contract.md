# ADF Agent Contract

## Purpose

This contract defines the minimum standard for creating new agents in the Agentic Development Framework (ADF).
It exists to support future autonomous milestone execution without introducing improvised agents, superagents, or agents with mixed responsibilities.

Every new ADF agent must be contract-driven, narrowly scoped, reviewable, and compatible with the current shadow/current bootstrap path.
This document does not create, activate, or promote any agent.

## Current Mode

- ADF currently operates in shadow/current bootstrap.
- `coordinator-contract.md` remains the authority for coordination, delegation, gates, promotion, and readiness claims.
- Candidate mode is not active.
- Primary mode is not active.
- `controlled_inspect` and `controlled_commit` are not active.
- New ADF agents must be safe in shadow/current mode and must not assume runtime authority, git authority, or production authority.
- Each agent contract must remain compatible with a future explicit promotion to candidate or primary, if owner/coordinator approval and gates allow it.

## Required Frontmatter

Every future ADF subagent definition must start from this base frontmatter:

```yaml
---
description: ...
mode: subagent
hidden: true
permission:
  read: allow
  glob: allow
  grep: allow
  edit: deny
  bash: deny
---
```

`edit` and `bash` may only change in a future phase with explicit promotion.
Any exception requires gates, justification, and owner/coordinator approval.

The frontmatter is a template constraint for future agent definitions, not an active agent creation.

## Required Agent Sections

Every new ADF agent contract must include, at minimum:

- Identity and purpose.
- Single responsibility.
- Operating principles.
- Allowed inputs.
- Expected outputs.
- Possible decisions.
- Allowed files.
- Forbidden files.
- What it must never do.
- Relationship with `coordinator-contract.md`.
- Relationship with other ADF agents, if any exist.
- Relationship with `current_mode`.
- Operating procedure.
- Acceptance criteria.
- Stop conditions.

## Responsibility Rules

- An ADF agent must have exactly one responsibility.
- It must not act as orchestrator unless it is the orchestrator.
- It must not implement unless it is an explicitly authorized implementer.
- It must not review unless it is the reviewer.
- It must not operate git unless it is the git operator.
- It must not select context unless it is the context broker.
- It must not produce `task_packet` unless it is the packetizer.
- It must not plan unless it is the planner.
- It must not define policy unless it is the policy agent.
- It must not decide roadmap or product direction unless that authority is explicitly delegated by the owner.

## Decision Vocabulary

Recommended decision vocabularies:

- `APPROVE` / `ADJUST` / `BLOCK`
- `APPROVE` / `CLARIFY` / `BLOCK`
- `APPROVE` / `REQUEST_CHANGES` / `REJECT`
- `ROUTE` / `CLARIFY` / `HOLD` / `BLOCK` / `CAPABILITY_GAP` / `PROMOTION_REQUIRED`
- `APPROVE_GIT_ACTION` / `HOLD` / `BLOCK` / `PROMOTION_REQUIRED`

Any new decision term must be justified in the agent contract.
The `CAPABILITY_GAP` decision covers the same condition described as `capability_gap` in the coordination policy.

## Contract Alignment

When applicable, every new agent must declare how it relates to:

- `intent`
- `roadmap_slice`
- `policy_constraints`
- `plan`
- `task_packet`
- `context_bundle`
- `review_report`
- `git_operation`

The agent must state whether each contract is an input, output, dependency, validation target, or out of scope.

## Automation Readiness

- New agents are born shadow-safe.
- Agents must be designed for future automation when their role is expected to become automated.
- Do not design permanent manual helpers when the final role should be automated.
- Declare `current_mode` and the expected future candidate or primary mode when applicable.
- Use `PROMOTION_REQUIRED` when a requested capability belongs to a future phase.
- Do not claim production readiness while required git lifecycle control remains permanently manual.

## Capability Gap Rule

If a task does not fit an existing approved ADF agent or capability:

- Do not force the task into the closest agent.
- Declare `CAPABILITY_GAP`.
- Define the minimum responsibility needed.
- Propose a candidate agent name that follows the approved ADF naming policy, if such a policy exists.
- Request owner/coordinator approval before creating the agent or expanding capability.

## Out-of-Context Rule

Agents must block or escalate requests outside their context, including:

- Touching repository runtime behavior without an approved phase.
- Touching command surfaces without an approved phase.
- Touching adapters, generators, templates, or adapter runtimes without an approved phase.
- Touching schemas without an approved phase.
- Activating candidate or primary mode without promotion.
- Operating git without gates.
- Mixing unrelated milestones or features.
- Changing `coordinator-contract.md` without explicit owner/coordinator approval.

## Git and Production Readiness Rule

- ADF is not production-ready if git remains permanently manual.
- A future git operator must reach at least `controlled_commit` capability for commits per feature before production readiness can be claimed.
- `controlled_inspect` and `controlled_commit` are not activated by this contract.
- Push and PR operations require milestone gates.

## New Agent Creation Checklist

- Approved ADF naming policy or explicit owner/coordinator naming approval.
- Clear purpose.
- Single responsibility.
- Correct frontmatter.
- Read-only by default.
- Future permissions documented, if applicable.
- Clear inputs and outputs.
- Clear decisions.
- Allowed and forbidden files documented.
- Relationship with existing contracts documented.
- Relationship with other agents documented, if any exist.
- Gates and stop conditions documented.
- Production or candidate implications documented, if applicable.
- Does not invade the coordinator, reviewer, implementer, or git operator roles.

## Anti-patterns

Forbidden patterns:

- Superagent that does everything.
- Agent that both implements and reviews.
- Agent that performs both git operations and review.
- Agent that reads the whole repository by default.
- Agent that activates candidate or primary mode.
- Agent that creates commits without gates.
- Agent that modifies adapters, generators, schemas, runtime behavior, or commands outside an approved phase.

## Usage

Consult this document before creating any new ADF agent.
If a proposed agent cannot satisfy this contract, stop and request owner/coordinator clarification or approval before implementation.
