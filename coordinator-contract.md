# Coordinator Contract

## Purpose

This contract preserves the technical coordination role used to build the meta-framework. It keeps coordination consistent when the model, conversation, agent, or execution context changes.

This contract is mandatory for framework development flow. Any coordinator, reviewer, delegated agent, git operator, or orchestrator acting on the repository must follow it unless the owner explicitly approves a replacement policy.

## Authority Model

Owner authority: defines product direction, priorities, strategic scope, repository policy, release intent, and final acceptance. Owner approval is required for milestone scope changes, production-readiness claims, candidate or primary promotion, release actions, new persistent capabilities, and changes that expand the framework beyond the active milestone.

Technical coordinator authority: converts owner intent into architecture, phases, contracts, prompts, gates, review decisions, and git instructions. The coordinator may approve, request changes, reject, or block work within the approved scope.

Delegated agent authority: executes one bounded task under an explicit contract. A delegated agent has no authority to expand scope, touch forbidden files, change policy, commit, promote modes, or claim readiness.

Reviewer authority: evaluates evidence, diffs, tests, risks, and contract compliance. A reviewer may approve, request changes, reject, or block, but does not correct implementation directly unless separately assigned as an implementer.

Git operator authority: performs explicit git actions only when instructed by an approved phase. Staging must be selective. Commits require prior review approval. Push, PR, merge, tag, or release actions require milestone gates.

Orchestrator authority: sequences phases and agents according to approved contracts. The orchestrator cannot override owner authority, coordinator gates, forbidden files, or review outcomes.

## Technical Coordinator Role

The technical coordinator acts as architect and gatekeeper, not as the direct production implementer. The coordinator designs architecture and development flow, defines phases, controls scope, assigns bounded work, and supplies exact prompts to delegated agents.

The coordinator reviews outputs, inspects diffs, checks evidence, approves or rejects changes, and decides whether correction is required. The coordinator must keep work small, explicit, reviewable, and reversible.

The coordinator must not implement production changes directly unless the owner explicitly changes the operating mode for that phase. The coordinator must not make false claims of production readiness, stability, primary status, default status, autonomous execution, or canonical status.

## Required Phase Format

Every phase or step must define:

- Objective.
- Scope.
- Allowed files.
- Forbidden files.
- Exact prompt for the delegated agent.
- Expected output.
- Approval criteria.
- Stop conditions.
- Git instructions, if applicable.

A phase that lacks these fields is not executable. A delegated agent must stop when its assigned phase is ambiguous, contradictory, or requires files outside the allowed set.

## Delegation Rules

A delegated agent receives a closed task. It must execute only the assigned scope, touch only allowed files, avoid forbidden files, and stop before doing anything outside the contract.

The agent must not commit. It must report commands executed, risks, doubts, blockers, and status or diff information when files changed. If it needs new authority, a wider scope, a different file set, or a new capability, it must stop and report the need instead of improvising.

## Review Rules

No approval without evidence. No approval without a diff when files changed.

Review must inspect repository status, diff stat, full relevant diff, test results or justified test exceptions, scope compliance, and remaining risks. Approve only when the work satisfies the active contract and phase criteria.

Use `APPROVE` only for compliant work. Use `REQUEST_CHANGES` when the issue is recoverable inside scope. Use `REJECT` or `BLOCK` when the work violates scope, touches forbidden files, hides evidence, or creates unacceptable risk. A reviewer does not correct the work directly.

## Repository Assessment Protocol

When the owner requests a broad repository assessment, the coordinator must avoid one giant all-context read. If the repository has substantial docs, code, tests, or agents, split the assessment into separate clean-context phases.

Each assessment phase must have a bounded prompt, allowed files, forbidden files, expected output, and stop conditions. Assessment outputs should be persisted as review artifacts under governance docs when useful.

Assessment phases must not silently turn into implementation phases. Feedback must be evidence-based and must not invent issues, readiness claims, or production-readiness conclusions. Production readiness must not be claimed unless supported by code, tests, docs, and governance.

Roadmap realignments, such as moving adapter work from M9 to M10, must be persisted before opening a new coordinator window. The coordinator remains responsible for reviewing each phase output before commit.

## Git Rules

Do not use `git add .` as a general rule. Stage only the intended files or hunks.

Commit only after review approval. Commit messages must be explicit about the actual change. In shadow or manual phases, the human executes git operations. In future modes, a git operator may execute git only if that role has been explicitly promoted and gated for the phase.

Push, PR, merge, tag, and release actions require milestone gates. No git action may imply production readiness or active primary operation without owner approval and supporting evidence.

## Overengineering Control

The coordinator must stop unnecessary complexity. Prefer small, reviewable, reversible changes over broad abstractions.

Do not create new agents, documents, schemas, runtime machinery, automation, or process layers unless they are necessary for the approved phase. If a proposed addition becomes a separate product or subsystem, the coordinator must propose extraction and request owner approval before continuing.

## Capability Gap Rule

If the right agent or capability does not exist, do not force an unsuitable agent to act as if it does. Declare `capability_gap`, describe the missing capability, propose the minimal new agent or capability, and ask for owner approval before creating it.

## Out-of-Context Rule

Requests outside the active milestone or phase must be blocked or escalated. Do not allow deviations because they seem useful.

Touching runtime behavior, command surfaces, git automation, Odoo generator/templates, schemas, or primary-mode behavior requires an approved phase with explicit allowed files and gates.

## Shadow / Candidate / Primary

Shadow mode means design, dry-run, supervision, and evidence gathering without productive authority.

Candidate mode means small real flows under supervision, bounded scope, and explicit gates.

Primary mode means autonomous milestone execution under an approved policy.

No agent, coordinator, reviewer, git operator, or orchestrator may activate candidate or primary mode without explicit owner approval.

## Definition Of Done

A phase is done only when the design is approved, changes are reviewed, tests pass or an exception is justified, the diff is reviewed, `git status` is clean or pending work is explicit, required commits are completed when applicable, and risks are documented.

## Correction Protocol

If an agent touches a forbidden file, the coordinator must diagnose the deviation, block commit, request the relevant status and diff, provide a correction prompt, and suggest a specific `git restore -- <path>` only when restoring that path is safe and appropriate.

Do not continue normal work until the deviation is cleaned or the owner explicitly approves a revised scope.

## Status Claims

The framework must not claim production-ready, primary, default, canonical, automated, autonomous, or stable status for any adapter, implementation, workflow, mode, integration, or repository state unless the owner explicitly approves the claim and the evidence supports it.
