# ADF Candidate Mode Plan

## Purpose

This document defines the plan to promote the Agentic Development Framework (ADF) from shadow/current bootstrap toward candidate mode.
It does not activate candidate mode.

Candidate mode is an intermediate step toward primary operation and autonomous milestone execution.
Its purpose is to test supervised end-to-end coordination before ADF is allowed to operate with production-level automation.

## Current Status

- ADF is currently in shadow/current bootstrap.
- `coordinator-contract.md` remains the coordination authority.
- Git is still manual in the current phase.
- Candidate mode is not active.
- Primary mode is not active.
- `controlled_inspect` is not active.
- `controlled_commit` is not active.
- This plan does not create agents, schemas, runtime, adapters, or commands.

## Definitions

### Shadow / Current Bootstrap

- Authority: owner/coordinator authority remains the only operating authority under `coordinator-contract.md`.
- Permissions: proposed or future agents are read-only unless explicitly allowed by a reviewed phase.
- Git: ADF may recommend actions only; humans execute all git operations unless a future git mode is explicitly promoted.
- Runtime: existing repository behavior and command surfaces remain unchanged.
- Human role: owner/coordinator interprets outputs and decides whether to act.
- Allowed risk: low. No autonomous execution, no mode promotion, and no repository writes by future agents.

### Candidate Mode

- Authority: owner/coordinator authority remains active; ADF may coordinate supervised real flows only through approved contracts and gates.
- Permissions: ADF may operate only through approved gates, contracts, task packets, context bundles, and explicit allowed files.
- Git: ADF may advance from recommendation to `controlled_inspect` if that mode is formally promoted, but cannot commit until `controlled_commit` is separately approved.
- Runtime: current runtime and command surfaces remain active; candidate mode does not replace primary command or execution authority.
- Human role: owner/coordinator approves scope, gates, exceptions, and promotions.
- Allowed risk: limited and reversible. Small real tasks are allowed only under review gates and rollback policy.

### Primary Mode

- Authority: ADF becomes the operating authority for approved framework development flows.
- Permissions: ADF can coordinate milestone-level execution within owner-approved policy and gates.
- Git: ADF may operate commits, milestone branches, and PRs according to promoted git modes and rollback rules.
- Runtime: any runtime or command activation must be explicit in a separate approved phase.
- Human role: owner/coordinator governs policy, approvals, exceptions, and release decisions.
- Allowed risk: managed production risk with reviewer gates, git gates, observability, rollback, and fallback.

## Candidate Mode Definition

Candidate means:

- ADF coordinates complete flows under supervision.
- ADF still does not replace owner/coordinator authority.
- ADF may operate small, real, reversible tasks under gates.
- ADF may delegate implementation to an authorized external implementer.
- ADF may use git `controlled_inspect` only if that mode is formally promoted.
- ADF cannot make automatic commits until `controlled_commit` is separately approved.

## Candidate Entry Criteria

- Base ADF agent contract exists.
- Required future ADF agents exist and have been audited.
- Contracts have been hardened against mixed responsibility and out-of-scope behavior.
- Controlled dry-run has been completed.
- Pending negative dry-runs are completed before activation.
- External implementer contract is defined.
- `controlled_inspect` is defined.
- Audit trail is defined.
- `CAPABILITY_GAP` behavior is tested.
- Out-of-context `BLOCK` behavior is tested.
- Reviewer failure cases are tested.
- Rollback policy is defined.
- Owner/coordinator approval is recorded for promotion.

## Candidate Allowed Capabilities

If candidate mode is explicitly promoted, candidate may allow ADF to:

- Coordinate complete supervised flows.
- Produce contractual artifacts.
- Delegate implementation to an authorized external implementer.
- Execute small real tasks under gates.
- Use `controlled_inspect` if formally enabled.
- Prepare git plans without automatic commit.
- Route work to reviewer and git operator roles.

## Candidate Forbidden Capabilities

Candidate mode must not allow ADF to:

- Replace owner/coordinator authority.
- Activate primary mode.
- Modify command surfaces without an approved phase.
- Modify runtime behavior without an approved phase.
- Make automatic commits without `controlled_commit`.
- Push or open PRs automatically.
- Touch adapters, generators, templates, or adapter runtimes without a specific phase.
- Modify schemas or utilities without `task_packet`, `context_bundle`, reviewer, and gates.
- Mix unrelated features.
- Use `git add .`.
- Skip reviewer.

## Git Promotion Path

The following git modes are promotion levels, not active capabilities created by this document.

### shadow_recommend_only

- Purpose: let ADF recommend git actions without executing them.
- Permissions: read repository status only through human-provided output or approved read-only inspection.
- Commands permitted: none executed by ADF.
- Gates: human review of recommendations.
- Risks: outdated status, incomplete diff context, manual transcription errors.
- Expected output: git plan, files to stage, proposed commit message, risks, and stop conditions.

### controlled_inspect

- Purpose: allow a future ADF git operator to inspect repository state without changing it.
- Permissions: execute exact allowlisted read-only git commands only.
- Commands permitted: `git status --short`, `git status --branch --short`, `git diff --stat`, `git diff -- <path>`, `git diff --cached --stat`, `git diff --cached -- <path>`, `git log --oneline -n 10`, `git branch --show-current`.
- Gates: exact command allowlist, audit trail, no shell expansion beyond approved command, fallback to `HOLD` on failure.
- Risks: misinterpreting diffs, exposing unrelated worktree changes, inspection output being mistaken for approval to stage.
- Expected output: inspection report, contamination warnings, branch validation, and recommended next action.

### controlled_stage

- Purpose: allow selective staging of reviewed allowed files.
- Permissions: stage only exact files approved by task packet and reviewer.
- Commands permitted: `git add -- <explicit-file>` for approved files only, plus controlled inspect commands.
- Gates: reviewer approval, allowed files check, no forbidden files, no unreviewed untracked files, no `git add .`.
- Risks: staging unrelated changes in an approved file, missing generated artifacts, stale reviewer output.
- Expected output: staged file list and `git diff --cached` summary for review.

### controlled_commit

- Purpose: allow a future ADF git operator to create commits for one reviewed feature at a time.
- Permissions: commit staged approved changes with an approved Conventional Commit message.
- Commands permitted: controlled inspect commands, approved selective `git add -- <explicit-file>`, `git diff --cached`, `git commit -m "<approved-message>"`.
- Gates: reviewer `APPROVE`, tests passed or exception approved, correct branch, no mixed features, rollback documented.
- Risks: commit includes user changes, commit message references wrong issue, hooks modify files, rollback plan is incomplete.
- Expected output: commit hash, final status, included files, tests, and rollback note.

### milestone_branch_operator

- Purpose: allow ADF to manage milestone branch flow after feature-level git is reliable.
- Permissions: create or validate milestone branches and coordinate feature merges only under milestone policy.
- Commands permitted: controlled git commands explicitly approved for branch operation.
- Gates: milestone issue exists if required by policy, branch naming policy, clean worktree, reviewed roadmap scope, no direct main commit.
- Risks: branch divergence, mixing milestone scope, accidental work on main.
- Expected output: branch status, milestone scope confirmation, and next feature branch recommendation.

### pr_operator

- Purpose: allow ADF to prepare and open PRs after milestone gates are satisfied.
- Permissions: push and PR operations only after owner-approved PR policy and all gates pass.
- Commands permitted: approved `git push -u` and `gh pr create` commands for the current approved branch.
- Gates: tests passed, reviewer approved, changelog/roadmap requirements met when applicable, user validation for milestone-to-main PRs.
- Risks: premature PR, missing manual validation, leaking unrelated changes, incorrect base branch.
- Expected output: PR URL, PR summary, test evidence, remaining risks.

## Gates Before controlled_inspect

- Exact read-only git command allowlist must be defined.
- No generic shell access.
- No write commands.
- Audit trail must record command, purpose, output summary, decision, and timestamp.
- Any command failure, unexpected branch, or ambiguous output must fall back to `HOLD`.
- Inspection outputs do not authorize staging or commit by themselves.

## Gates Before controlled_commit

- Reviewer decision is `APPROVE`.
- Tests passed, or a documented exception is explicitly approved.
- `task_packet` is present.
- `context_bundle` is present.
- `allowed_files_only` is satisfied.
- No forbidden files are modified.
- No unreviewed untracked files are present.
- Commit message is approved.
- Current branch is the correct milestone or feature branch.
- No mixed features are present.
- `git diff --cached` has been reviewed.
- Rollback is documented.

## External Implementer Contract Summary

The authorized external implementer:

- Receives `task_packet`.
- Receives `context_bundle`.
- Works only within closed `allowed_files`.
- Treats `forbidden_files` as explicit stop conditions.
- Does not commit.
- Does not push.
- Does not open PRs.
- Does not expand scope.
- Returns modified files, implementation summary, tests run, risks, and status or diff when applicable.
- Stops if the task requires touching files outside scope.

## Required Candidate Dry-runs

- Real single-file task.
- `REQUEST_CHANGES` case.
- `REJECT` case.
- Out-of-context `BLOCK` case.
- `CAPABILITY_GAP` case.
- Git operator `HOLD` case.
- Git operator `PROMOTION_REQUIRED` case.
- Unexpected untracked file case.
- Forbidden file modified case.
- Incomplete `task_packet` `ADJUST` case.

## Candidate Risks

- Excessive bureaucracy.
- Unstructured contracts.
- Permanently manual git.
- Lack of validation tooling.
- Poorly defined external implementer.
- Missing audit log.
- Premature bash promotion.
- Scope creep into runtime, commands, adapters, or generators.
- Orchestrator becoming a superagent.
- Reviewer becoming an implementer.

## Minimal Roadmap To Candidate

- Create base governance documents.
- Define external implementer contract.
- Define `controlled_inspect` design.
- Complete real single-file supervised dry-run.
- Complete negative/failure dry-runs.
- Complete candidate gate review.
- Decide candidate activation only if gates pass.

## Candidate Activation Rule

- Candidate is not activated by this document.
- Candidate requires explicit owner/coordinator approval.
- Candidate requires clean worktree and reviewed gates.
- Candidate must be activated in a separate phase.

## Production Readiness Rule

- ADF is not production-ready while git remains permanently manual.
- Production readiness requires at least `controlled_commit` for commits per feature.
- Primary requires milestone-level automation, reviewer gates, git gates, rollback/fallback, and owner-approved policy.

## Usage

Consult this document before promoting any ADF agent or flow to candidate.
Use it as a reusable plan for checking scope, gates, git permissions, external implementation rules, and activation conditions.

The final objective is real milestone autonomy with controlled risk, not permanent manual assistance.
