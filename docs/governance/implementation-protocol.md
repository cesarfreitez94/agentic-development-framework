# Implementation Protocol

## Purpose

This protocol defines the mandatory implementation, delegation, review, and git discipline for ADF framework work.
It adapts the bootstrap governance rules to an agnostic framework repository and does not create agents, schemas, runtime, or adapters.

## Current Mode

- ADF is in shadow/current bootstrap.
- `coordinator-contract.md` is the coordination authority.
- Candidate mode is not active.
- Primary mode is not active.
- `controlled_inspect` and `controlled_commit` are not active.
- Git remains manual unless a future phase explicitly promotes a gated git capability.

## Mandatory Flow

For any new phase:

1. Do not implement production changes directly unless the active phase explicitly allows it.
2. Design first.
3. Review the design.
4. Detect conflicts with schemas, contracts, runtime boundaries, repository policy, and allowed files.
5. Adjust before implementation.

## Delegation Packet

Every implementation or delegated task must define:

- Objective.
- Scope.
- Exact prompt or task instruction.
- Explicit allowed files.
- Explicit forbidden files.
- Expected output.
- Acceptance criteria.
- Stop conditions.
- Review requirements.
- Git instructions, if applicable.

A task without these fields is not executable.

## Implementation Rules

- Use a bounded prompt.
- Touch only explicit allowed files.
- Treat forbidden files as stop conditions.
- Do not touch runtime behavior unless the phase specifically allows it.
- Do not touch agents, commands, schemas, adapters, generators, templates, or runtime surfaces unless the phase specifically allows them.
- Do not expand scope because a change seems useful.
- Declare `CAPABILITY_GAP` when the required capability does not exist.
- Block or escalate out-of-context work instead of improvising.

## Post-Implementation Report

After implementation, report:

- Files created or modified.
- Commands executed.
- Tests executed, or why tests were not run.
- Result.
- Risks.
- Doubts or blockers.
- Diff or status evidence when files changed.

## Review Rules

- No approval without evidence.
- No approval without a diff when files changed.
- Review status, diff stat, relevant full diff, test evidence or justified test exception, scope compliance, and remaining risks.
- Use `APPROVE` only for compliant work.
- Use `REQUEST_CHANGES` when the issue is recoverable inside scope.
- Use `REJECT` or `BLOCK` when the work violates scope, touches forbidden files, hides evidence, or creates unacceptable risk.
- The reviewer does not correct implementation directly unless separately assigned as an implementer.

## Git Rules

- In shadow/current bootstrap, humans execute git operations.
- Do not use `git add .`.
- Stage only intended files or hunks.
- Run `git status` before git actions.
- Inspect `git diff --stat` and the relevant full diff before staging.
- After staging, inspect `git diff --cached` before committing.
- Verify contamination: no forbidden files, unrelated files, unreviewed untracked files, or mixed features are included.
- Commit only after review approval and only when the active phase explicitly requires or allows a commit.
- Push, PR, merge, tag, and release actions require milestone gates and owner/coordinator approval.
- Permanent manual git cannot be claimed as production-ready.

## Sequencing Rule

- Do not advance to the next phase without reviewing the previous change.
- If a commit was approved and created, review the resulting status before continuing.
- If there is no commit in the current phase, document the pending worktree state before continuing.

## Priority Rule

When deciding between valid approaches, prefer:

1. Simplicity.
2. Automation only where it is justified by the target operating model.
3. Agents only when a single-responsibility agent is necessary.
4. Runtime changes only after explicit approval and gates.

## Utility Rule

If a utility, schema, adapter, runtime component, or agent seems unnecessary, question it before implementing it.

## Promotion Rule

- Candidate promotion requires owner/coordinator approval.
- Primary promotion requires owner/coordinator approval.
- `controlled_inspect` requires a separate approved gate.
- `controlled_commit` requires a separate approved gate.
- No document in `docs/governance/` activates promotion by itself.

## Definition Of Done

A phase is done only when design is reviewed, implementation stays within allowed files, tests pass or an exception is justified, diff evidence is reviewed, git state is explicit, and risks are documented.
