# M9.4 Tests Agents Documentation Assessment

## Scope Statement

This is a tests/agents/documentation assessment only. It is not implementation, not remediation, not readiness approval, and not adapter work.

M9.4 reviews visible tests, OpenCode agent files, the agent contract, README, governance documents, and prior M9 assessment evidence at an assessment level only. It does not modify tests, agents, README, source, schemas, runtime, builders, package configuration, existing governance documents, or any adapter-related file.

This assessment does not authorize fixes, refactors, new tests, source changes, schema changes, agent changes, README updates, existing governance updates, adapters, CLI, registry, `.adf/` artifact store, git execution, agent invocation, `framework_state` mutation, candidate mode, or primary mode.

## Evidence Commands

Commands executed before assessment work:

- `git branch --show-current`
  - Output: `main`.
- `git status --short`
  - Output: clean before starting.
- `git log --oneline -5`
  - Output:

```text
ad1969a Add M9.3 code runtime schema assessment
05045df Add M9.2 governance consistency assessment
ef97b4a Add M9.1 repository map assessment
d620175 Realign roadmap for repository assessment
b2b18fb Update extraction handoff after M8.1 completion
```

Bounded inventory commands executed:

- `find tests -maxdepth 1 -type f | sort`
  - Relevant output: 17 top-level test files were listed, including 13 `test_build_*.py` files, `test_meta_schemas.py`, `test_package_import.py`, `test_runtime_dry_run.py`, and `test_runtime_invocation.py`.
- `find agents/opencode -maxdepth 1 -type f | sort`
  - Relevant output: 9 OpenCode agent files were listed under `agents/opencode/`.
- `find docs -maxdepth 3 -type f | sort`
  - Relevant output: `docs/agents/agent-contract.md`, governance documents, and M9.1 through M9.3 assessment artifacts were listed.

Tests were not run during M9.4. Running `python -m pytest` can create or update pytest cache and bytecode/cache artifacts unless extra cache-disabling controls are used, and this phase authorizes only the M9.4 assessment artifact to be written. This assessment therefore relies on read-only inspection of the allowed test files and prior documented test evidence from M8.1/M9.3.

## Source Documents Reviewed

Source of truth:

- `coordinator-contract.md`
- `docs/governance/extraction-handoff.md`

Prior M9 evidence:

- `docs/governance/assessments/m9-1-repository-map-assessment.md`
- `docs/governance/assessments/m9-2-governance-milestone-consistency-assessment.md`
- `docs/governance/assessments/m9-3-code-runtime-schema-assessment.md`

Documentation:

- `README.md`
- `docs/agents/agent-contract.md`
- `docs/governance/agnostic-dry-run-design-and-evidence.md`
- `docs/governance/builder-runtime-extraction-strategy.md`
- `docs/governance/candidate-mode-plan.md`
- `docs/governance/implementation-protocol.md`
- `docs/governance/m5-remaining-schema-audit.md`
- `docs/governance/minimal-builder-invocation-runtime-strategy.md`

OpenCode agents:

- `agents/opencode/context-broker.md`
- `agents/opencode/git-operator.md`
- `agents/opencode/intake.md`
- `agents/opencode/orchestrator.md`
- `agents/opencode/packetizer.md`
- `agents/opencode/planner.md`
- `agents/opencode/policy.md`
- `agents/opencode/reviewer.md`
- `agents/opencode/roadmap.md`

Tests:

- `tests/test_build_context_bundle.py`
- `tests/test_build_decisions.py`
- `tests/test_build_framework_state.py`
- `tests/test_build_git_operation.py`
- `tests/test_build_implementation_report.py`
- `tests/test_build_intent.py`
- `tests/test_build_plan.py`
- `tests/test_build_policy_constraints.py`
- `tests/test_build_review_report.py`
- `tests/test_build_roadmap_slice.py`
- `tests/test_build_schema_catalog.py`
- `tests/test_build_task_packet.py`
- `tests/test_build_test_report.py`
- `tests/test_meta_schemas.py`
- `tests/test_package_import.py`
- `tests/test_runtime_dry_run.py`
- `tests/test_runtime_invocation.py`

## Test Suite Assessment

Schema tests:

- `tests/test_meta_schemas.py` checks that schema files under `schemas/meta/` are JSON documents containing `$schema`.
- `tests/test_meta_schemas.py` checks schemas for listed adapter/FBA-specific references including `factory-build-agent`, `src/fba`, `.factory/framework-state.json`, `fba-agent-observer`, `opencode.ai/fba`, `FBA`, `Odoo`, and `odoo`.
- Visible strength: the schema tests provide a simple contamination guard against project-specific references in schema files.
- Visible gap: the schema tests do not visibly validate every schema against the JSON Schema Draft-07 metaschema or assert the full expected schema inventory. M9.3 documents stronger schema characteristics from read-only inspection, including 13 Draft-07 contracts, top-level `additionalProperties: false`, and `contract_version` `2.0`.

Package/import tests:

- `tests/test_package_import.py` imports `agentic_development_framework` and asserts `__version__ == "0.1.0"`.
- Visible strength: basic package importability is covered.
- Visible gap: package testing is minimal and does not cover exported builder/runtime surface completeness beyond import and version.

Builder tests:

- The visible suite includes 13 builder test files corresponding to the 13 builder modules and schema contracts mapped in M9.3.
- Across the visible builder tests, common coverage includes schema-valid output, deterministic output, missing required inputs, explicit `output_path` writes using `tmp_path`, invalid field types or patterns, duplicate detection, enum/status constraints, conditional rule failures, and forced schema-validation failure via mocked `jsonschema.validate`.
- Visible strength: builder tests are contract-heavy and cover many negative cases for each builder artifact type.
- Visible strength: builder tests use temporary output paths for write checks instead of persistent repository paths.
- Visible gap: the builder tests validate individual builders but do not by themselves prove a full end-to-end 13-artifact pipeline or cross-builder semantic equivalence. M9.3 also records that runtime invocation coverage does not visibly invoke all 13 mapped builders end-to-end through `invoke_builder`.

Runtime invocation tests:

- `tests/test_runtime_invocation.py` covers successful explicit `build_intent` invocation, unknown builder structured failure, validation pass evidence, invalid input structured failure, invalid artifact non-storage, path boundary refusal, `framework_state` non-mutation/proposal preview behavior, and a watched-file no-modification check for one builder, one schema, and one agent file.
- Visible strength: runtime tests directly target the non-autonomous invocation boundary and side-effect constraints described by M8.1 and M9.3.
- Visible gap: runtime tests visibly exercise `invoke_builder` primarily through `build_intent`; they do not visibly assert that all 13 `_SUPPORTED_BUILDERS` entries are invocable end-to-end or synchronized with the schema/builder inventory.

Dry-run tests:

- `tests/test_runtime_dry_run.py` covers dry-run evidence, no artifact-root/output creation, no-write and no-git confirmations, explicit deterministic check evidence, and an `equivalent` comparison category.
- Visible strength: dry-run tests support the M7/M8 boundary that dry-run evidence is returned in memory without persistence or git execution.
- Visible gap: dry-run comparison coverage is minimal and aligns with M9.3's finding that current comparison appears shallow relative to the richer M7.1 semantic-comparison design language.

Test execution result:

- Tests were not run in M9.4 for the cache/artifact reason stated in Evidence Commands.
- Prior documented evidence in `docs/governance/extraction-handoff.md` records 227 tests passed after M8.1, and M9.3 relied on read-only inspection plus prior documented passing-test evidence.

## OpenCode Agent Assessment

The visible OpenCode agent set contains 9 files:

- `adf-intake`: interprets initial requests into a minimal `intent`; explicitly does not plan, review, implement, select context, or operate git.
- `adf-roadmap`: produces a minimal `roadmap_slice`; explicitly does not modify roadmap, implement, plan in detail, packetize, review, or select context.
- `adf-policy`: derives explicit operational constraints; applies default deny; explicitly does not plan, packetize, implement, review, select context, operate git, or activate modes.
- `adf-planner`: turns authorized objectives into small packetizable plans; explicitly does not create final task packets, implement, review, select context, or operate git.
- `adf-packetizer`: converts authorized plans or work units into proposed `task_packet` contracts; explicitly does not implement, review, select detailed context, or run tests.
- `adf-context-broker`: proposes minimal `context_bundle` from a `task_packet`; explicitly avoids broad repository exploration and does not implement, review, orchestrate, or execute commands.
- `adf-reviewer`: reviews an already implemented output/diff against task packet, context bundle, tests, and constraints; explicitly does not correct files, run tests, or operate git.
- `adf-git-operator`: evaluates git lifecycle eligibility in `shadow_recommend_only`; explicitly does not execute git in current mode and treats controlled git modes as future gaps.
- `adf-orchestrator`: routes, delegates, and evaluates gates; explicitly does not implement, edit, run bash, commit, activate primary, or replace owner/coordinator authority.

Assessment against `docs/agents/agent-contract.md` and coordinator boundaries:

- Bounded scope: aligned. Each agent states a single responsibility and lists expected outputs, allowed inputs, prohibited responsibilities, and stop/adjust/block behavior.
- No autonomous commits without authorization: aligned. All reviewed agents have `edit: deny` and `bash: deny`; `adf-git-operator` states that in `shadow_recommend_only` it cannot execute git and that `APPROVE_GIT_ACTION` does not execute or enable automation.
- No unauthorized mode promotion: aligned. Agents consistently state that candidate, primary, `controlled_inspect`, and `controlled_commit` are not active or must not be activated by the agent.
- No readiness claims: aligned. `adf-orchestrator` says no agent should declare readiness without evidence and owner approval; `adf-git-operator` frames controlled git modes as future capability gaps; the agent contract warns against production-readiness claims while git remains permanently manual.
- No adapter/FBA implementation during M9: aligned at the visible contract level. Agents prohibit unauthorized adapters, generators, templates, runtime surfaces, and out-of-context work. Some agent contracts retain historical `.factory` references as unavailable session-note inputs or gaps, but do not authorize reading FBA source or implementing adapters.
- Clean handoff expectations: broadly aligned. Agents specify required output sections, recommendations, missing-information handling, and downstream relationships.

Agent risks or ambiguities observed:

- The active agent files are Spanish-language contracts while several governance/source-of-truth documents are English. This is not a functional contradiction, but it may increase reviewer burden for future controlled updates.
- `agents/opencode/context-broker.md` retains `.factory/meta/session_notes/...` references as unavailable gaps. This is bounded in the file, but should remain clearly historical/non-active to avoid future confusion.
- `docs/governance/extraction-handoff.md` records a known non-blocking M4 polish gap: `context-broker.md` lacks reciprocal "Relacion Con" sections for upstream/downstream documentation consistency. This remains a documentation polish item only.

No agent files were modified.

## Documentation Assessment

Current source-of-truth docs:

- `coordinator-contract.md` is current for authority, bounded delegation, repository assessment protocol, git rules, mode promotion, and status/readiness claims.
- `docs/governance/extraction-handoff.md` is the operational handoff and contains the current M9/M10 boundary: M9 is repository assessment/readiness review, M10 is FBA adapter boundary/notes, and M9 must not implement runtime features, adapters, CLI, registry, `.adf/` store, git execution, agent invocation, `framework_state` mutation, or mode activation.
- M9.1, M9.2, and M9.3 are current prior evidence for repository map, governance consistency, and code/runtime/schema findings.
- `docs/agents/agent-contract.md` is current for future agent contract expectations and explicitly does not create, activate, or promote agents.
- `docs/governance/implementation-protocol.md` and `docs/governance/candidate-mode-plan.md` remain aligned on shadow/current bootstrap, manual git unless promoted, and inactive candidate/primary modes.

Historical docs with superseded roadmap language:

- `docs/governance/builder-runtime-extraction-strategy.md` was created for M5 and still lists proposed next phases ending with M9 as FBA adapter notes. M8.3 and M9 evidence supersede this by defining M9 as repository assessment and moving adapter work to M10.
- `docs/governance/minimal-builder-invocation-runtime-strategy.md` was created for M6.1 and still describes runtime as future/no runtime exists and lists M9 as adapter notes. M8.1 implemented minimal runtime invocation, while M8.3 moved adapter notes to M10.
- `docs/governance/agnostic-dry-run-design-and-evidence.md` was created for M7.1 and correctly states design-only/future dry-run in its historical context. M8.1 later implemented in-memory dry-run evidence inside `invoke_builder`, so current docs should treat M7.1 as historical design input rather than current status.
- `docs/governance/m5-remaining-schema-audit.md` is historical M5 evidence and includes FBA schema comparison performed during that earlier phase. It should not be read as authorization for M9.4 to inspect FBA.

Docs that may need M9.5 controlled updates:

- `README.md` is visibly stale. It says the repository contains only the initial package shell and coordination contract and that agents, schemas, runtime components, utilities, and integrations will be introduced later. Current M9 evidence shows agents, schemas, builders, tests, and minimal runtime invocation already exist.
- `docs/governance/extraction-handoff.md` contains useful current M9 boundaries but also historical language noted by M9.2: M9.1 is proposed next, repository assessment artifacts are not created yet, and older HEAD/origin baselines are historical.
- Older M5/M6/M7 roadmap or status wording may need explicit supersession markers so future sessions do not treat historical adapter-M9 language or pre-runtime status as current.

No documentation files other than this M9.4 assessment artifact were modified.

## Cross-Assessment Consistency

Compared with M9.1 repository map:

- Confirmed: 9 OpenCode agent files are present under `agents/opencode/`.
- Confirmed: 17 top-level test files are present under `tests/`, matching builder, schema/package, runtime invocation, and dry-run categories.
- Confirmed: documentation groups under `docs/agents/` and `docs/governance/` are present.
- Confirmed: missing/unauthorized assets from the handoff remain out of scope for this assessment: adapters, CLI, registry, `.adf/` store, git execution capability, agent invocation capability, candidate mode, and primary mode.

Compared with M9.2 governance consistency:

- Confirmed: M9 remains governance/documentation assessment work, not implementation.
- Confirmed: older roadmap language still creates M9/M10 ambiguity unless treated as historical and superseded by M8.3.
- Confirmed: README is a likely M9.5 controlled-update candidate because it is stale against current repository contents.
- Confirmed: candidate/primary and controlled git modes remain inactive.

Compared with M9.3 code/runtime/schema assessment:

- Confirmed: visible tests cover the 13 builders directly and runtime invocation/dry-run behavior separately.
- Confirmed: runtime tests focus `invoke_builder` primarily on `build_intent`, while direct builder tests cover all builders. This supports M9.3's gap that all 13 runtime mappings are not visibly exercised end-to-end through runtime tests.
- Confirmed: dry-run comparison tests use M7 category names, but visible test coverage is minimal and does not prove deep semantic comparison.
- Confirmed: optional explicit persistence tests exist, but no `.adf/` artifact store or metadata inventory is authorized or assessed as ready.

Tensions or unresolved items:

- README status is inconsistent with current repository assets and should not be relied on as current source-of-truth.
- Historical governance docs are useful audit records but need time-context markers to avoid stale roadmap interpretation.
- Agent contracts are aligned with read-only/shadow safety, but future activation would require explicit owner/coordinator authorization, tests, gates, and possibly controlled updates to agent documentation.

## Alignment Findings

Aligned:

- Initial branch was `main` and status was clean before M9.4 work began.
- The visible test inventory matches the M9.1/M9.3 categories: schema/package tests, 13 builder tests, runtime invocation tests, and dry-run tests.
- The visible builder tests are broad contract tests with schema validation, determinism, invalid inputs, explicit output-path writes, and negative cases.
- Runtime/dry-run tests support core non-autonomous boundaries: explicit builder selection, structured failures, no invalid artifact storage, path boundary checks, no direct `framework_state` mutation, no writes in dry-run, and no-git confirmation.
- All 9 OpenCode agent files have read-only frontmatter with `edit: deny` and `bash: deny`.
- OpenCode agent contracts are single-responsibility and prohibit implementation, unauthorized git, mode activation, readiness claims, and out-of-scope work.
- Coordinator contract, handoff, agent contract, implementation protocol, and candidate-mode plan align that candidate/primary modes are inactive and require explicit approval.

Stale or ambiguous:

- `README.md` is stale because it still describes only an initial package shell and says agents, schemas, runtime components, utilities, and integrations will be introduced later.
- Older M5/M6 governance docs still mention M9 as adapter notes, superseded by M8.3/M9 evidence that moved adapter work to M10.
- M6.1/M7.1 docs describe runtime/dry-run as future design in their historical phase context; M8.1 later implemented minimal runtime invocation and in-memory dry-run evidence.
- The handoff includes historical statements that were true before M9.1/M9.2/M9.3 but are stale after those committed assessment artifacts.
- `.factory` references in `context-broker.md` are explicitly marked unavailable, but remain historical/cross-repo-looking references that future maintainers should not treat as M9 authorization.

Risks/gaps:

- Tests were not run in M9.4, so this assessment does not provide fresh test execution evidence.
- Schema tests are minimal contamination and `$schema` checks; they do not visibly assert the complete schema inventory or Draft-07 metaschema validity.
- Package import testing is minimal.
- Runtime invocation tests visibly focus on `build_intent`; all 13 builders are tested directly but not all are visibly invoked through runtime.
- Dry-run comparison tests do not prove the full semantic comparison dimensions described in M7.1.
- README drift can mislead future users about actual current assets and status.

Explicitly out of scope for M9.4:

- Running remediation, adding tests, editing test files, editing agent files, editing README, editing source/runtime/builders/schemas, editing existing governance docs, updating package config, or creating new operational capabilities.
- Creating adapters, CLI, registry, `.adf/` artifact store, git execution, agent invocation, `framework_state` mutation, candidate mode, primary mode, or FBA integration behavior.
- Inspecting FBA or any external repository.

## Required Corrections or Documentation Updates For Later Phases

Safe documentation clarifications for M9.5:

- Update README to reflect current assets after M9.1-M9.4 consolidation, if M9.5 explicitly authorizes README changes.
- Update or qualify extraction handoff status language to record completed M9.1-M9.4 artifacts after coordinator review, if true at M9.5 time.
- Add explicit supersession notes to older M5/M6 roadmap sections that refer to M9 adapter notes, clarifying that M8.3 moved adapter work to M10.
- Clarify M7.1 and M6.1 as historical design inputs where M8.1 later implemented a minimal subset.
- Clarify that optional explicit runtime persistence is not the full `.adf/` artifact store or metadata inventory.

Test/agent/doc changes requiring explicit owner authorization:

- Add tests that assert complete schema inventory and schema metaschema validity.
- Add tests that verify runtime mapping synchronization with all 13 builders and schemas.
- Add runtime tests that invoke all 13 builder mappings end-to-end through `invoke_builder`.
- Add or revise agent documentation for reciprocal relationship sections, including the known `context-broker.md` polish gap.
- Translate, normalize, or otherwise reorganize agent contracts for consistency.

Implementation items requiring explicit owner authorization:

- Any runtime change for write failure handling, conflict detection, comparison behavior, or mapping synchronization noted by M9.3.
- Any source, builder, schema, runtime, packaging, config, or test modification.
- Any new command surface, operational workflow, controlled git mode, agent invocation capability, artifact store, or `framework_state` mutation path.

Items deferred to M10 or later:

- FBA adapter boundary notes.
- Any adapter implementation.
- Any downstream FBA integration behavior.
- Any project-specific translation layer, Odoo behavior, or FBA source inspection.

## Non-Readiness Statement

M9.4 does not certify production readiness.

M9.4 does not certify FBA integration readiness.

M9.4 does not authorize adapters, CLI, registry, `.adf` store, git execution, agent invocation, source/test/schema/agent/doc changes, or candidate/primary mode.

M9.4 also does not authorize README updates, existing governance document edits, runtime/builder/schema/test remediation, `framework_state` mutation, or adapter-related work.

## Risks / Gaps Observed From Tests Agents Documentation Review Only

- No fresh test run was performed in M9.4, so current pass/fail state is not re-established by this phase.
- Visible schema tests provide only basic JSON/`$schema` and forbidden-string checks; deeper schema contract assertions remain documented by M9.3 inspection rather than test execution in this phase.
- Visible runtime tests do not exercise every supported builder through the runtime entry point.
- Visible dry-run comparison tests cover category presence but not full M7.1 semantic-comparison depth.
- README is stale relative to the present repository contents.
- Historical M5/M6/M7 governance language can be misread as current if not interpreted in phase context.
- Agent contracts are read-only/shadow aligned, but future automation would need separate authorization, gates, and review before any permission or mode change.
- `context-broker.md` retains known documentation polish gap and historical unavailable `.factory` references; these are not active authorization but may need future clarification.

## Coordinator Review Checklist

- [ ] scope respected
- [ ] only allowed file changed
- [ ] no README update
- [ ] no source/test/schema/agent/runtime/builder changes
- [ ] no existing governance docs edited
- [ ] no implementation
- [ ] no adapter/CLI/registry work
- [ ] no .adf store
- [ ] no git execution
- [ ] no agent invocation
- [ ] no readiness claims
- [ ] no mode activation
- [ ] git status reviewed
- [ ] diff reviewed
