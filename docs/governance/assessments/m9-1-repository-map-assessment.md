# M9.1 Repository Map Assessment

## Scope Statement

This is a shallow repository mapping assessment only. It is not an implementation review, not a production-readiness approval, not an FBA integration-readiness approval, and not adapter work.

The assessment intentionally avoids deep reads of source, test, schema, agent, runtime, builder, packaging, or adapter-related files. It maps visible repository structure, file groups, apparent responsibilities, and boundaries for later M9 subphases.

## Evidence Commands

Commands executed before assessment work:

- `git branch --show-current`
  - Output: `main`.
- `git status --short`
  - Output: clean before starting.
- `git log --oneline -5`
  - Output:

```text
d620175 Realign roadmap for repository assessment
b2b18fb Update extraction handoff after M8.1 completion
7d6608f Implement minimal ADF runtime invocation
3b811a5 Define agnostic dry-run design and evidence
c300802 Update extraction handoff after M6.1 completion
```

Source-of-truth files read in full:

- `coordinator-contract.md`
- `docs/governance/extraction-handoff.md`

Shallow map commands executed:

- `find . -maxdepth 2 -type d -not -path './.git*' | sort`
  - Relevant output: top-level groups include `agents/`, `docs/`, `schemas/`, `src/`, and `tests/`; local cache directories are also visible.
- `find . -maxdepth 2 -type f -not -path './.git/*' -not -path './.pytest_cache/*' | sort`
  - Relevant output: top-level tracked-facing files include `coordinator-contract.md`, `.gitignore`, `pyproject.toml`, `README.md`, and test files under `tests/`.
- `find docs -maxdepth 3 -type f | sort`
  - Relevant output: governance and agent documentation files are present under `docs/agents/` and `docs/governance/`.
- `find agents -maxdepth 3 -type f | sort`
  - Relevant output: 9 OpenCode agent markdown files are present under `agents/opencode/`.
- `find schemas -maxdepth 3 -type f | sort`
  - Relevant output: 13 meta schema JSON files are present under `schemas/meta/`.
- `find src -maxdepth 4 -type f | sort`
  - Relevant output: Python package files are present under `src/agentic_development_framework/`, including builder modules and runtime modules; local `__pycache__` files are visible but were not assessed as source.
- `find tests -maxdepth 2 -type f | sort`
  - Relevant output: builder, schema/package, and runtime test filenames are present; local `__pycache__` files are visible but were not assessed as tests.
- `mkdir -p docs/governance/assessments`
  - Relevant output: no terminal output; created the assessment artifact directory required for this file.

## Source-of-Truth Alignment

`coordinator-contract.md` establishes these applicable constraints for M9.1:

- Delegated agents execute bounded tasks only and must not expand scope, touch forbidden files, commit, promote modes, or claim readiness.
- Broad repository assessment must avoid one giant all-context read and should be split into clean-context phases.
- Assessment phases must not turn into implementation phases.
- Feedback must be evidence-based and must not invent issues, readiness claims, or production-readiness conclusions.
- Production readiness requires owner approval and supporting evidence across code, tests, docs, and governance.
- Git actions beyond inspection require explicit authorization; commits are not allowed here.
- Candidate and primary modes may not be activated without explicit owner approval.

`docs/governance/extraction-handoff.md` establishes these applicable constraints for M9.1:

- Current mode is bootstrap/shadow; candidate mode, primary mode, controlled inspect, and controlled commit are not active.
- M9 is repository assessment and ADF readiness review, documentation/governance only unless separately authorized.
- M9.1 is repository map assessment and must be run as a separate bounded subphase.
- M10 is FBA adapter boundary and adapter notes; M10 is not authorized by the handoff.
- M9 must not implement runtime features, create adapters, create CLI, activate candidate or primary mode, add git execution, add agent invocation, mutate `framework_state`, or create `.adf/` artifact store unless separately authorized.
- ADF is not claimed production-ready and is not claimed ready for FBA integration.

## Repository Map

### Governance / Docs

Visible governance and documentation assets:

- `coordinator-contract.md`
- `README.md`
- `docs/agents/agent-contract.md`
- `docs/governance/agnostic-dry-run-design-and-evidence.md`
- `docs/governance/builder-runtime-extraction-strategy.md`
- `docs/governance/candidate-mode-plan.md`
- `docs/governance/extraction-handoff.md`
- `docs/governance/implementation-protocol.md`
- `docs/governance/m5-remaining-schema-audit.md`
- `docs/governance/minimal-builder-invocation-runtime-strategy.md`
- `docs/governance/assessments/m9-1-repository-map-assessment.md`

Visible responsibilities from filenames and handoff evidence:

- Coordination contract and operating policy.
- Extraction handoff and milestone continuity.
- Builder/runtime strategy documentation.
- Dry-run design and evidence guidance.
- Candidate-mode planning documentation, without activation.
- Agent contract documentation.
- M5 schema audit record.

### Agent Contracts / OpenCode Agents

Visible agent contract and OpenCode agent assets:

- `docs/agents/agent-contract.md`
- `agents/opencode/context-broker.md`
- `agents/opencode/git-operator.md`
- `agents/opencode/intake.md`
- `agents/opencode/orchestrator.md`
- `agents/opencode/packetizer.md`
- `agents/opencode/planner.md`
- `agents/opencode/policy.md`
- `agents/opencode/reviewer.md`
- `agents/opencode/roadmap.md`

Visible responsibilities from filenames and handoff evidence:

- Intake, roadmap, policy, planning, packetization, context brokerage, review, orchestration, and gated git operation roles.
- Handoff states 9/9 OpenCode agents were migrated in M4.

### Schemas

Visible schema assets under `schemas/meta/`:

- `context_bundle.schema.json`
- `decisions.schema.json`
- `framework_state.schema.json`
- `git_operation.schema.json`
- `implementation_report.schema.json`
- `intent.schema.json`
- `plan.schema.json`
- `policy_constraints.schema.json`
- `review_report.schema.json`
- `roadmap_slice.schema.json`
- `schema_catalog.schema.json`
- `task_packet.schema.json`
- `test_report.schema.json`

Visible responsibilities from filenames and handoff evidence:

- 13 project-agnostic meta-framework schema contracts.
- Handoff states schemas were added in M3 and all 13 programmatic builders correspond to these schema contracts.

### Builders

Visible builder module assets under `src/agentic_development_framework/builders/`:

- `__init__.py`
- `context_bundle.py`
- `decisions.py`
- `framework_state.py`
- `git_operation.py`
- `implementation_report.py`
- `intent.py`
- `plan.py`
- `policy_constraints.py`
- `review_report.py`
- `roadmap_slice.py`
- `schema_catalog.py`
- `task_packet.py`
- `test_report.py`

Visible responsibilities from filenames and handoff evidence:

- 13 programmatic builders for meta-framework artifacts.
- Handoff states M5 completed all 13 builders and corresponding tests.

### Runtime

Visible runtime module assets under `src/agentic_development_framework/runtime/`:

- `__init__.py`
- `invocation.py`

Visible responsibilities from filenames and handoff evidence:

- Minimal runtime invocation entry point exposed as `invoke_builder`.
- Static builder invocation, schema validation, structured evidence, dry-run evidence, optional explicit persistence, and `framework_state` proposal/preview behavior are described in the handoff.
- Runtime is described by the handoff as non-autonomous, not a CLI, not a registry, not an adapter, not git execution, and not agent invocation.

### Tests

Visible test assets under `tests/`:

- `test_build_context_bundle.py`
- `test_build_decisions.py`
- `test_build_framework_state.py`
- `test_build_git_operation.py`
- `test_build_implementation_report.py`
- `test_build_intent.py`
- `test_build_plan.py`
- `test_build_policy_constraints.py`
- `test_build_review_report.py`
- `test_build_roadmap_slice.py`
- `test_build_schema_catalog.py`
- `test_build_task_packet.py`
- `test_build_test_report.py`
- `test_meta_schemas.py`
- `test_package_import.py`
- `test_runtime_dry_run.py`
- `test_runtime_invocation.py`

Visible responsibilities from filenames and handoff evidence:

- Builder tests for 13 builder modules.
- Meta schema/package tests.
- Runtime invocation and dry-run tests.

Tests were not executed during M9.1 because this subphase is documentation/governance repository mapping only.

### Packaging / Config

Visible packaging/config assets from shallow top-level map:

- `.gitignore`
- `pyproject.toml`
- `README.md`

Visible responsibilities from filenames only:

- Python package configuration appears centralized in `pyproject.toml`.
- Repository ignore policy appears centralized in `.gitignore`.
- Public repository overview appears to be `README.md`, which was not read or modified in this phase.

### Missing / Not-Created Assets Explicitly Visible From The Handoff

The handoff explicitly identifies these as not created, not active, incomplete, or not authorized:

- No adapters created; adapter work is moved to M10 and not authorized.
- No builder registry created.
- No builder CLI created.
- No `.adf/` artifact store created.
- No `metadata.json` inventory created.
- No persistent dry-run artifact store created.
- No git execution capability added.
- No agent invocation capability added.
- No direct `framework_state` mutation.
- Candidate mode is not active.
- Primary mode is not active.
- `controlled_inspect` is not implemented.
- `controlled_commit` is not implemented.
- Repository assessment artifacts had not been created before M9.1; this file is the first M9.1 assessment artifact.

## Assessment Boundaries For Later M9 Subphases

Recommended split for later M9 review, preserving clean contexts and avoiding a giant all-context read:

- M9.2 — Governance and milestone consistency assessment.
  - Read governance docs and milestone records in focused detail.
  - Compare `coordinator-contract.md`, `docs/governance/extraction-handoff.md`, roadmap statements, and governance docs for consistency.
  - Avoid source/runtime/schema/test/agent implementation review except as referenced evidence.
- M9.3 — Code/runtime/schema assessment.
  - Read source builder modules, runtime modules, and schemas in bounded groups.
  - Check implementation and schema alignment without reading tests and agent docs deeply in the same context.
  - Preserve prohibitions on adapters, CLI, registry, `.adf/` store creation, git execution, agent invocation, and mode activation.
- M9.4 — Tests/agents/documentation assessment.
  - Review test coverage files, OpenCode agent files, and user-facing docs in bounded slices.
  - Avoid making implementation changes while assessing tests or agents.
  - Keep README update decisions for M9.5 unless separately authorized.
- M9.5 — Consolidated repository assessment plus controlled documentation update.
  - Synthesize M9.1 through M9.4 artifacts.
  - Only then consider controlled README/handoff updates if explicitly authorized by that subphase.
  - Do not authorize adapter, CLI, registry, `.adf/`, git execution, agent invocation, or mode promotion by consolidation alone.

## Non-Readiness Statement

M9.1 does not certify production readiness.

M9.1 does not certify FBA integration readiness.

M9.1 does not authorize adapters, CLI, registry, `.adf` store, git execution, agent invocation, or candidate/primary mode.

## Risks / Gaps Observed From Map Only

- The repository contains substantial governance, agent, schema, builder, runtime, and test surfaces; later M9 phases should remain split to avoid context pollution and accidental implementation review sprawl.
- Local cache artifacts are visible in shallow maps under `src/**/__pycache__/`, `tests/__pycache__/`, and `.pytest_cache/`; these are not assessed as source/test assets and should not be confused with repository deliverables.
- The handoff contains historical HEAD/origin baseline references around M8.3, while the current git log shows `d620175 Realign roadmap for repository assessment` as latest; M9.2 should treat this as a governance consistency item to verify, not as an implementation issue.
- Missing assets listed in the handoff, including adapters, CLI, registry, `.adf/` store, and mode activation, remain explicit non-assets and should not be created during assessment phases.

## Coordinator Review Checklist

- [ ] Scope respected.
- [ ] Only allowed file changed.
- [ ] No source/test/schema/agent changes.
- [ ] No README update.
- [ ] No adapter/runtime/CLI/registry work.
- [ ] No readiness claims.
- [ ] Git status reviewed.
- [ ] Diff reviewed.
