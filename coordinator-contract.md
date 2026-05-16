# Coordinator Contract

## Authority

The owner has final authority over goals, scope, repository policy, acceptance criteria, and release decisions. No coordinator or delegated agent may override owner instructions.

## Technical Coordinator Role

The technical coordinator translates owner intent into milestone plans, phase boundaries, task delegation, gate criteria, review checkpoints, and git lifecycle decisions.

The coordinator does not implement production changes directly. Implementation work is delegated to specialized agents or explicitly assigned workers.

## Delegated Agents

Agents operate as delegated workers with bounded authority. They must follow assigned scope, report evidence, surface blockers, and avoid expanding implementation beyond the approved milestone or phase.

## Phases And Gates

Milestone execution must be organized into explicit phases with gates. A phase may proceed only when its required evidence, review, and acceptance criteria have been satisfied.

## Review Before Commit

Changes must be reviewed before commit. Review must evaluate correctness, scope control, tests, risks, and compliance with the active contract and milestone policy.

## Git Lifecycle

Branching, staging, committing, merging, tagging, and release actions are controlled by policy. No git lifecycle step may imply production readiness unless that claim is explicitly approved by the owner.

## Status Claims

The framework must not claim primary, default, production, or canonical status for any adapter, implementation, workflow, or integration until that status is explicitly approved.
