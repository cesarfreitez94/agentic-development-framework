# M9.5A Production Readiness Gap Assessment

## Scope Statement

This is a production-readiness gap assessment only. It estimates missing evidence and remaining work before ADF could be considered production-ready under different operating models.

This is not implementation, not remediation, not a production-readiness certification, not an FBA integration certification, and not adapter work. This assessment does not authorize source, test, schema, runtime, builder, agent, packaging, README, extraction handoff, or existing governance-document changes.

## Evidence Commands

Commands executed before assessment work:

- `git branch --show-current`
  - Output: `main`.
- `git status --short`
  - Output: clean before starting.
- `git log --oneline -8`
  - Output:

```text
e469672 Add M9.4 tests agents documentation assessment
ad1969a Add M9.3 code runtime schema assessment
05045df Add M9.2 governance consistency assessment
ef97b4a Add M9.1 repository map assessment
d620175 Realign roadmap for repository assessment
b2b18fb Update extraction handoff after M8.1 completion
7d6608f Implement minimal ADF runtime invocation
3b811a5 Define agnostic dry-run design and evidence
```

Inventory commands executed:

- `find schemas/meta -maxdepth 1 -type f | sort`
  - Relevant output: 13 meta schema files listed under `schemas/meta/`.
- `find src/agentic_development_framework/builders -maxdepth 1 -type f | sort`
  - Relevant output: 13 builder modules plus `__init__.py` listed.
- `find src/agentic_development_framework/runtime -maxdepth 1 -type f | sort`
  - Relevant output: `__init__.py` and `invocation.py` listed.
- `find tests -maxdepth 1 -type f | sort`
  - Relevant output: 17 top-level test files listed, including 13 builder test files, schema/package tests, runtime invocation tests, and dry-run tests.
- `find agents/opencode -maxdepth 1 -type f | sort`
  - Relevant output: 9 OpenCode agent files listed.
- `find docs/governance/assessments -maxdepth 1 -type f | sort`
  - Relevant output: M9.1, M9.2, M9.3, and M9.4 assessment artifacts listed before this M9.5A artifact was created.

Tests were not run. M9.5A is assessment/governance/documentation only, and running tests could create or update runtime/cache artifacts outside the single allowed output file. This assessment relies on M9.1-M9.4 evidence and prior documented test evidence.

## Source Documents Reviewed

Source of truth:

- `coordinator-contract.md`
- `docs/governance/extraction-handoff.md`

Prior M9 evidence:

- `docs/governance/assessments/m9-1-repository-map-assessment.md`
- `docs/governance/assessments/m9-2-governance-milestone-consistency-assessment.md`
- `docs/governance/assessments/m9-3-code-runtime-schema-assessment.md`
- `docs/governance/assessments/m9-4-tests-agents-documentation-assessment.md`

Documentation support:

- `README.md`
- `docs/agents/agent-contract.md`
- `docs/governance/agnostic-dry-run-design-and-evidence.md`
- `docs/governance/builder-runtime-extraction-strategy.md`
- `docs/governance/candidate-mode-plan.md`
- `docs/governance/implementation-protocol.md`
- `docs/governance/m5-remaining-schema-audit.md`
- `docs/governance/minimal-builder-invocation-runtime-strategy.md`

Inventory only:

- `schemas/meta/` via `find schemas/meta -maxdepth 1 -type f | sort`
- `src/agentic_development_framework/builders/` via `find src/agentic_development_framework/builders -maxdepth 1 -type f | sort`
- `src/agentic_development_framework/runtime/` via `find src/agentic_development_framework/runtime -maxdepth 1 -type f | sort`
- `tests/` via `find tests -maxdepth 1 -type f | sort`
- `agents/opencode/` via `find agents/opencode -maxdepth 1 -type f | sort`
- `docs/governance/assessments/` via `find docs/governance/assessments -maxdepth 1 -type f | sort`

## Current Evidence Baseline

M9.1 established a shallow repository map. It found governance docs, 9 OpenCode agents, 13 meta schemas, 13 builder modules, minimal runtime files, 17 top-level test files, packaging/config files, and explicitly missing or unauthorized assets including adapters, CLI, registry, `.adf/` artifact store, git execution, agent invocation, candidate mode, primary mode, `controlled_inspect`, and `controlled_commit`.

M9.2 established governance and milestone consistency. It found the current M9/M10 boundary is that M9 is repository assessment and readiness review while adapter work moved to M10. It also identified stale handoff and older roadmap language, including older references to M9 as adapter notes and pre-M9.1 current-state language.

M9.3 established code/runtime/schema alignment from bounded review. It found 13 Draft-07 schema contracts, 13 matching builders, a static runtime mapping for all 13 builders, schema validation, in-memory dry-run evidence, optional explicit persistence, and `framework_state` proposal/preview behavior. It also found gaps in runtime write failure handling, conflict detection terminology, runtime all-builder invocation coverage, and semantic comparison depth.

M9.4 established tests/agents/documentation alignment. It found 17 test files, 9 read-only OpenCode agent contracts, broad builder test coverage, runtime/dry-run side-effect tests, stale README content, historical governance language requiring time-context markers, no fresh test run in M9.4, minimal schema inventory/import tests, and future automation gates remaining inactive.

## Readiness Model

Passive/library-style framework readiness means ADF can be treated as a production-ready Python package or library surface for deterministic schema artifact construction and explicit runtime builder invocation. This requires package/import surface confidence, current user-facing documentation, repeatable verification, release/installation evidence, and sufficiently tested runtime behavior. It does not require autonomous git execution, agent invocation, candidate mode, primary mode, or FBA adapters.

Autonomous/agentic operational readiness means ADF can safely operate supervised or autonomous agentic development flows with operational authority. This requires mode governance, controlled inspection, controlled commit capability, agent invocation boundaries, gates, audit evidence, rollback/fallback policy, owner approval, and evidence that the system can coordinate real work without violating scope. This is a higher readiness level than passive/library readiness.

FBA integration readiness means ADF has an explicitly authorized project-specific integration boundary for Factory Build Agent and enough translation, adapter, test, and governance evidence to connect ADF artifacts to FBA-specific workflows. This requires a separate M10-style boundary decision and must not be conflated with either passive library readiness or autonomous operational readiness.

These are distinct readiness levels. Evidence for one level does not certify another.

## Current Strengths

- Governance structure: `coordinator-contract.md`, implementation protocol, candidate-mode plan, and handoff define bounded delegation, authority, stop conditions, git discipline, readiness-claim restrictions, and mode-promotion gates.
- OpenCode agent contracts: M9.4 found 9 OpenCode agent files with read-only contracts, single-responsibility role boundaries, `edit: deny`, `bash: deny`, and explicit prohibitions on unauthorized git, mode activation, implementation, and readiness claims.
- Schema inventory: M9.1 and M9.3 found 13 meta schemas, with M9.3 observing Draft-07 declarations, strict top-level `additionalProperties: false`, contract metadata, and distinct artifact ID patterns.
- Builder inventory: M9.1 and M9.3 found 13 builders corresponding to the 13 schema contracts, with M9.3 observing deterministic callable behavior, schema validation, and explicit output-path writing only.
- Minimal runtime invocation: M9.3 found `invoke_builder` exposes explicit caller-selected builder invocation, static mapping for all 13 builders, validation evidence, dry-run evidence, optional explicit persistence, path boundary checks, and `framework_state` proposals/previews only.
- Tests: M9.4 found 17 top-level test files, including 13 builder test files, schema/package tests, runtime invocation tests, and dry-run tests. Prior handoff evidence records 227 tests passing after M8.1.
- Shadow/bootstrap safety boundaries: current governance consistently keeps candidate mode, primary mode, `controlled_inspect`, `controlled_commit`, git execution, agent invocation, direct `framework_state` mutation, CLI, registry, adapters, and `.adf/` artifact store inactive or unauthorized.

## Production-Readiness Gap Matrix

| Area | Evidence from M9.1-M9.4 | Gap | Severity | Required action type | Suggested phase |
|------|--------------------------|-----|----------|----------------------|-----------------|
| Documentation freshness | M9.4 found `README.md` still describes only an initial package shell while agents, schemas, builders, tests, and runtime now exist. | User-facing docs are stale and can mislead users about actual assets and non-readiness boundaries. | high | docs | M9.5B |
| Extraction handoff freshness | M9.2 and M9.4 found handoff language still says M9.1 is proposed next and assessment artifacts are not created yet. | Operational handoff can restart future sessions at the wrong phase or obscure current M9 evidence. | high | docs | M9.5B |
| Schema inventory testing | M9.4 found schema tests check JSON/`$schema` and forbidden strings; M9.3 inspection established deeper schema characteristics. | Tests do not visibly assert complete schema inventory or Draft-07 metaschema validity. | medium | tests | M12 |
| Package/import surface testing | M9.4 found `test_package_import.py` covers import and `__version__` only. | Exported builder/runtime surface completeness and install/import modes are minimally tested. | medium | tests | M12 |
| Runtime all-builder invocation coverage | M9.3 and M9.4 found runtime tests primarily exercise `invoke_builder` through `build_intent`; builders are tested directly. | All 13 runtime mappings are not visibly invoked end-to-end through the runtime entry point. | high | tests | M11 or M12 |
| Runtime write failure handling | M9.3 found post-validation directory creation and file writes are not visibly converted into structured runtime failure evidence. | Explicit persistence may surface raw I/O failures rather than the structured failure model described by M6.1. | high | implementation | M11 |
| `framework_state` artifacts vs `artifact_refs` conflict detection | M9.3 found runtime conflict detection checks `artifact_refs`, while current schema and builder use `artifacts`. | Duplicate/conflict detection may miss schema-shaped `framework_state` artifacts unless terminology is clarified or behavior is changed. | high | implementation / owner decision | M11 |
| Dry-run semantic comparison depth | M9.3 found comparison appears shallow top-level dictionary comparison; M9.4 found dry-run tests do not prove full M7.1 semantic dimensions. | Current evidence does not support claims of deep semantic equivalence. | medium | implementation / docs / tests | M11 or M12 |
| Optional persistence vs `.adf` artifact store boundary | M9.2-M9.4 repeatedly distinguish M8.1 optional explicit persistence from the unimplemented `.adf/` store. | Documentation and future users may conflate optional output persistence with production artifact-store readiness. | high | docs / owner decision / future phase | M9.5B or M11 |
| Packaging/release/installation evidence | M9.1 mapped `pyproject.toml`; M9.4 found only minimal import/version test evidence. | No M9 evidence of build artifacts, install-from-wheel/sdist checks, published release process, dependency pin/release policy, or supported Python matrix. | high | tests / docs / owner decision | M12 |
| CI or repeatable verification evidence | Prior handoff records 227 tests passed after M8.1; M9.3 and M9.4 did not run tests. | Current M9.5A does not establish fresh repeatable CI/pass evidence or cache-safe verification process. | high | tests / owner decision | M12 |
| Mode governance | Governance docs consistently keep shadow/bootstrap active and candidate/primary inactive. | Promotion gates exist as plans, but no activation evidence, dry-run gate completion, controlled inspection, or owner approval exists. | blocker | owner decision / future phase | Later candidate gate phase |
| Git execution boundary | M9.1-M9.4 and governance docs prohibit git execution; agent contract says production readiness requires at least `controlled_commit`. | ADF cannot be considered autonomous production-ready while git remains manual and `controlled_commit` inactive. | blocker | implementation / owner decision / future phase | Later controlled git phase |
| Agent invocation boundary | M9.3 found runtime does not invoke agents; M9.4 found agents are read-only contracts. | No operational agent invocation path, audit trail, permission model, or invocation tests exist. | blocker | implementation / owner decision / future phase | Later agent invocation phase |
| Candidate/primary mode readiness | Candidate-mode plan exists; M9.2 and M9.4 confirm candidate and primary are inactive. | Required candidate dry-runs, negative cases, rollback, owner approval, and promotion evidence are incomplete or absent. | blocker | owner decision / future phase | Later candidate/primary gate phase |
| FBA adapter/integration boundary | M9.2 and M9.4 confirm M10 adapter boundary is deferred and not authorized; M9.5A did not inspect FBA. | No authorized adapter boundary decision, translation layer, integration contract, adapter tests, or FBA-specific evidence exists. | blocker | owner decision / docs / tests / implementation | M10 candidate/proposed |

## Passive/Library-Style Production Readiness Estimate

ADF has meaningful passive/library foundations: 13 schema contracts, 13 deterministic builders, tests for builders, import/version testing, and a minimal explicit runtime invocation surface. However, M9.1-M9.4 evidence is not sufficient to claim passive/library production readiness.

Must fix before readiness:

- Refresh user-facing documentation so README and current handoff status do not misrepresent repository contents or readiness boundaries.
- Establish repeatable verification evidence, preferably CI or a documented cache-safe local verification path.
- Expand package/import surface tests beyond basic import and version so exported builders and runtime entry points are covered.
- Add runtime tests or evidence that all 13 supported builders can be invoked end-to-end through `invoke_builder`.
- Resolve or document the `framework_state.artifacts` versus `state_update_proposal.add_artifact_refs` conflict-detection boundary.
- Ensure explicit persistence write failures produce structured failure evidence or formally document the limitation.

Should fix before readiness:

- Add schema inventory and metaschema validity tests so the schema set is enforced by tests, not only inspection.
- Clarify optional explicit persistence versus the still-unimplemented `.adf/` artifact store and `metadata.json` inventory.
- Clarify dry-run comparison depth so the framework does not overclaim semantic equivalence.
- Add installation/build/release evidence for package consumers, including wheel/sdist or editable-install behavior as appropriate.

Optional hardening:

- Add broader negative tests for path, persistence, invalid builder return, and state proposal edge cases.
- Add documentation examples for passive library usage that preserve non-autonomous boundaries.
- Add maintenance policy notes for schema versioning and compatibility once release intent exists.

## Autonomous/Agentic Operational Readiness Estimate

ADF is not evidenced as autonomous or operationally production-ready. Current evidence shows strong safety governance and read-only agent contracts, but operational authority remains deliberately inactive.

Before autonomous/agentic operational readiness could be considered, ADF would need at minimum:

- `controlled_inspect`: exact read-only git command allowlist, audit trail, failure fallback, permission model, tests or dry-runs, and owner approval.
- `controlled_commit`: selective staging gates, reviewed diff requirements, commit-message policy, rollback policy, no-mixed-feature enforcement, hook/failure handling, tests or supervised trials, and owner approval.
- Agent invocation: an explicit invocation boundary for OpenCode/LLM agents, audit evidence, input/output contracts, permission constraints, failure behavior, and tests or supervised evidence.
- Git execution: explicit separation between artifact construction and real git operations, with gates proving no unauthorized `git add`, commit, push, PR, or branch actions occur.
- Candidate/primary mode: completed required dry-runs and negative cases from the candidate-mode plan, reviewed gates, clean worktree policy, owner approval, and separate activation phase.
- Gates and evidence: reviewer approvals, task packets, context bundles, test evidence or justified exceptions, status/diff review, rollback/fallback policy, and audit logs.

Current governance supports a path toward operational readiness, but M9.5A does not certify that path and does not activate any mode.

## FBA Integration Readiness Estimate

ADF is not evidenced as ready for FBA integration. M9.1-M9.4 consistently treat FBA adapter work as deferred to M10 or later, and this assessment did not inspect FBA or any external source.

Before FBA integration readiness could be considered, ADF would need at minimum:

- M10 adapter boundary notes that define what belongs in ADF core versus a project-specific FBA adapter.
- An explicit adapter authorization decision from the owner/coordinator before any adapter implementation begins.
- A rule that no adapter implementation occurs before authorization, including no translation layer, CLI, registry, `.adf/` store, FBA source inspection, or FBA-specific behavior by implication.
- A translation layer or project-specific contract that maps ADF artifacts to FBA-specific concepts without importing FBA/Odoo coupling into ADF core.
- Integration tests or evidence that exercise the translation boundary, adapter failure behavior, contamination controls, and non-core ownership of project-specific semantics.

M10 should remain candidate/proposed only unless separately authorized by the owner.

## Recommended Remediation Roadmap

This roadmap recommends staged post-M9 work only. It does not authorize execution.

- M9.5B controlled documentation update: update README and extraction handoff only if explicitly authorized, recording current assets, M9.1-M9.5A status, stale-roadmap supersession, and non-readiness boundaries.
- Possible M11 technical hardening: address runtime write failure handling, `framework_state` conflict detection, runtime mapping synchronization, dry-run comparison depth, and optional persistence boundary only under a code-authorized phase.
- Possible M12 test/release hardening: add schema inventory/metaschema tests, package/import surface tests, all-builder runtime invocation tests, installation/build/release verification, and CI or repeatable local verification evidence.
- Possible M10 adapter boundary decision: define FBA adapter boundary notes and decide whether adapter implementation is authorized later. Keep M10 as candidate/proposed unless separately authorized by the owner.
- Later candidate/primary mode gates if desired: separately design and approve `controlled_inspect`, `controlled_commit`, agent invocation, audit logging, rollback/fallback, supervised dry-runs, and owner-approved mode activation.

## Non-Readiness Statement

M9.5A does not certify production readiness.

M9.5A does not certify FBA integration readiness.

M9.5A does not authorize adapters, CLI, registry, `.adf` store, git execution, agent invocation, source/test/schema/agent/runtime changes, README changes, handoff changes, or candidate/primary mode.

M9.5A does not authorize remediation, refactoring, new tests, source changes, package changes, existing governance-document edits, adapter implementation, FBA source inspection, direct `framework_state` mutation, or any operational mode activation.

## Coordinator Review Checklist

- [ ] scope respected
- [ ] only allowed file changed
- [ ] no README update
- [ ] no extraction handoff update
- [ ] no existing governance docs edited
- [ ] no source/test/schema/agent/runtime/builder changes
- [ ] no implementation
- [ ] no adapter/CLI/registry work
- [ ] no .adf store
- [ ] no git execution
- [ ] no agent invocation
- [ ] no readiness certification
- [ ] no mode activation
- [ ] git status reviewed
- [ ] diff reviewed
