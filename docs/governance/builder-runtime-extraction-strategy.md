# ADF Builder/Runtime Extraction Strategy (M5)

## Purpose

M5 defines the extraction strategy for ADF programmatic builders and the minimal runtime boundary. This is a design/governance phase only. No implementation, no builder migration, no runtime creation.

The strategy exists so that future M5.x phases can implement builders one by one with clear contracts, audit trails, and zero FBA-coupling risk.

## Why Direct FBA Builder Copying Is Forbidden

The ADF repository was extracted from `factory-build-agent` (FBA) to create a project-agnostic meta-framework. The FBA repository contains:

- Odoo-specific semantics (generators, templates, adapter logic)
- V2 meta-workflow migration utilities that assume FBA directory layout
- Project-coupled assumptions about issue tracking, milestone naming, and task identification
- Builder implementations interleaved with FBA runtime behavior

Directly copying builders from FBA into ADF would:

1. Import FBA/Odoo coupling into ADF core — violating the agnostic mandate.
2. Bypass the contract-driven design that the schemas/meta contracts define.
3. Create hidden dependencies on FBA directory paths, environment assumptions, and operational patterns not present in ADF.
4. Undermine the reviewability and auditability of each builder.
5. Risk builders that produce artifacts for FBA's pipeline, not ADF's agentic pipeline.

Every builder must be derived from ADF's own schema contracts, not from FBA's source code.

## Core ADF Builder Definition

An ADF builder is a **pure, deterministic, project-agnostic artifact constructor** with these properties:

| Property | Rule |
|----------|------|
| **Input** | Explicit typed input contract (a dictionary/object matching the corresponding schema or a subset thereof) |
| **Output** | A single well-formed schema-compliant artifact (JSON/dict, written to an explicit output path) |
| **Determinism** | Same inputs → same outputs every time; no randomness, no external calls, no ambient state |
| **Project-agnostic** | No knowledge of project structure, repository layout, issue tracker, git, or specific tech stack |
| **No side effects** | Does not mutate filesystem beyond its assigned output path; does not execute git, tests, or commands |
| **No runtime decisions** | Does not decide scope, priority, acceptance, routing, or authorization |
| **No autonomous execution** | Is invoked explicitly; never runs itself or chains to other builders |
| **Idempotent** | Producing the same artifact ID twice with identical inputs yields identical output |
| **Schema-validated** | Output must validate against the corresponding schema/meta contract before being accepted |

A builder is a **transformation function**, not an agent, not an orchestrator, and not a runtime.

## Component Definitions

### Builder

> A deterministic function or callable that transforms typed input into a schema-valid output artifact.

Builders are the *production layer* of the pipeline. They exist to make the agentic pipeline executable and reproducible. Each builder corresponds to exactly one meta schema contract.

### Validator

> A function that checks whether an artifact conforms to its schema contract and returns a pass/fail result with structured findings.

Validators consume the schemas in `schemas/meta/` and apply json-schema validation plus any additional contract-specific invariants (e.g., `plan_id` references a real `PLAN-*` artifact, `intent_id` references a real `INTENT-*` artifact).

### Runtime

> A not-yet-created execution layer that sequences builders, manages artifact state, handles input/output file I/O, and provides the bridge between agentic coordination and deterministic artifact production.

Runtime is explicitly out of scope for M5. It is defined here as a boundary only. See section 11.

### Adapter

> A project-specific or domain-specific layer that translates between ADF artifacts and a concrete project's environment.

Adapters handle non-agnostic concerns: Odoo generators, specific issue tracker formats, project directory conventions, legacy migration utilities. Adapters belong to downstream projects (like FBA), not to ADF core.

### Orchestrator

> The agent (`adf-orchestrator.md`) that coordinates the agentic pipeline: routing, gates, delegation, and flow control.

The orchestrator produces decisions and delegation packets. It does not produce schema artifacts (those come from agents or builders).

### Delegated Agent

> A single-responsibility agent in `agents/opencode/` that performs one pipeline step (intake, roadmap, policy, planner, packetizer, context-broker, reviewer, git-operator).

Agents produce structured outputs (intents, plans, task packets, etc.) through LLM reasoning. Builders produce the *same schema artifacts* through deterministic programmatic execution. Agents and builders are complementary, not redundant.

## Builder Extraction Principles

1. **Schema-first**: Every builder must be derived from an existing `schemas/meta/*.schema.json` contract. No builder may be created without a corresponding schema.
2. **One builder, one contract**: Each builder produces exactly one artifact type. No multi-contract builders.
3. **No FBA source reference**: Builder design must reference only ADF schemas, agent contracts, and governance documents, never FBA source files.
4. **Pure input/output**: Every builder receives an explicit input dict and returns an explicit output dict. No hidden state, no ambient file reads, no environment variables.
5. **Output path assignment by caller**: The caller (future runtime or orchestrator) decides the output path. The builder writes only to the assigned path.
6. **Schema validation before acceptance**: Every builder output must validate against its corresponding schema contract before being treated as complete.
7. **No agent responsibility**: A builder does not replace the corresponding agent. The agent produces reasoned, contextual outputs; the builder produces deterministic, reproducible outputs. They serve different operating modes (agentic vs. programmatic).
8. **Incremental extraction**: Extract one builder at a time per a future M5.x phase. Review each independently. No bulk migration.
9. **Test-first**: Each builder extraction must include schema validation tests before the builder is accepted.

## Required Builder Contract Shape

Every ADF builder must conform to this Python callable contract:

```python
from typing import Dict, Any, Optional

def build_<artifact_name>(inputs: Dict[str, Any], output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Build a <artifact_name> artifact from typed inputs.

    Args:
        inputs: Typed dict matching the builder's expected input contract.
                Must include all required fields for artifact generation.
        output_path: Optional filesystem path. If provided, writes the artifact
                     as JSON to this path. Caller controls the path.

    Returns:
        Dict representing the complete schema-valid artifact.

    Raises:
        ValueError: If inputs are invalid or missing required fields.
        SchemaValidationError: If the produced artifact fails schema validation.

    Contract:
        - Deterministic: same inputs → same outputs.
        - Project-agnostic: no filesystem reads beyond schema references.
        - No side effects beyond assigned output_path.
        - Idempotent by artifact_id.
    """
```

All builders share these invariants:

| Requirement | Mandatory |
|-------------|-----------|
| Type-hinted inputs and return | Yes |
| TypedDict or dataclass input model (preferred) | Yes |
| JSON Schema validation of output | Yes |
| Unique artifact ID generation | Yes |
| Explicit error on invalid input | Yes |
| No filesystem reads (except schema for validation) | Yes |
| No network calls | Yes |
| No environment variable reads | Yes |
| No stdout/stderr output (logging only via a passed logger) | Yes |

## How Builders Consume Schemas/Meta Contracts

Each builder must form a closed loop with its schema:

```
schema/meta/<artifact>.schema.json  ──defines──►  artifact shape
                                                         │
                                          ┌──────────────┘
                                          ▼
                                    builder inputs
                                          │
                                    builder logic
                                          │
                                          ▼
                                    output dict
                                          │
                              ┌───────────┘
                              ▼
                    schema validation
                    (jsonschema draft-07)
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                  valid       invalid
                    │           │
                    ▼           ▼
               accept       SchemaValidationError
```

Builders must:

1. Reference schemas by their `$id` or relative path within `schemas/meta/`.
2. Use the exact `required` fields, `pattern` constraints, `enum` values, and `additionalProperties` rules from the schema.
3. Never extend or override the schema — if the schema is insufficient, the schema must be updated first via its own approved phase.
4. Validate output using Python `jsonschema` against the corresponding `.schema.json` file.
5. Include the written artifact path in a validation report.

## What Belongs In ADF Core vs Adapter Layer

### ADF Core (allowed for M5.x builder extraction)

| Component | Belongs in core? | Rationale |
|-----------|-----------------|-----------|
| Schema contracts (`schemas/meta/`) | Yes | Project-agnostic contract definitions |
| Agent contracts (`agents/opencode/`) | Yes | Agentic pipeline definitions |
| Governance documents | Yes | Framework operational rules |
| Builders for meta contracts | Yes | Pure artifact constructors |
| Schema validators | Yes | Contract enforcement |
| Future runtime (minimal) | Yes, but not in M5 | Controlled execution layer |
| Tests for builders and schemas | Yes | Validation and evidence |

### Adapter Layer (explicitly NOT core, not extracted in M5/M5.x)

| Component | Belongs in core? | Rationale |
|-----------|-----------------|-----------|
| FBA-specific utilities | No | Project-coupled |
| Odoo generators/templates | No | Domain-specific |
| `meta_workflow_migration.py` | No | FBA directory layout assumptions |
| Issue tracker integration | No | External service coupling |
| CI/CD integration | No | Environment-specific |
| Project-specific agent prompts | No | Not agnostic |
| Any file referencing `factory-build-agent` | No | Violates extraction goal |

## What Must Remain Outside M5

These items are explicitly excluded from the M5 strategy scope and must not be designed, implemented, or prepared during M5:

- Python builder implementation
- Runtime implementation
- Adapter implementation
- Controlled inspect mode
- Controlled commit mode
- Candidate mode activation
- Primary mode activation
- Any modification to `agents/`, `schemas/`, `tests/`, `src/`, `README.md`, `pyproject.toml`, or `coordinator-contract.md`
- Git operations beyond reading status
- Any file creation outside `docs/governance/`

## Candidate Future Builder List (Planned Future Phases Only)

This is a planning inventory, not an implementation commitment. Every builder below requires its own M5.x sub-phase with design, review, implementation, and testing.

### Pipeline Contract Builders (one per meta schema)

| Builder | Schema | Inputs | Output | Phase |
|---------|--------|--------|--------|-------|
| `build_intent` | `intent.schema.json` | user message, source, scope, constraints, outputs | `INTENT-*` artifact | M5.1 |
| `build_policy_constraints` | `policy_constraints.schema.json` | intent, policy refs, allowed/blocked ops, checks | `POLICY-*` artifact | M5.2 |
| `build_roadmap_slice` | `roadmap_slice.schema.json` | intent, milestone info, policy refs | `RSLICE-*` artifact | M5.3 |
| `build_plan` | `plan.schema.json` | intent, roadmap slice, tasks list, constraints | `PLAN-*` artifact | M5.4 |
| `build_task_packet` | `task_packet.schema.json` | plan, task info, allowed/forbidden files, ops | `TPACKET-*` artifact | M5.5 |
| `build_context_bundle` | `context_bundle.schema.json` | task packet, context items, policy refs | `CTX-*` artifact | M5.6 |
| `build_implementation_report` | `implementation_report.schema.json` | task packet, changed files, status, artifacts | `IMPL-*` artifact | M5.7 |
| `build_test_report` | `test_report.schema.json` | impl report, test runs, failures, coverage | `TEST-*` artifact | M5.8 |
| `build_review_report` | `review_report.schema.json` | impl report, test report, findings, recommendation | `REV-*` artifact | M5.9 |
| `build_git_operation` | `git_operation.schema.json` | review report, branch, operation type, policy checks | `GIT-*` artifact | M5.10 |
| `build_decisions` | `decisions.schema.json` | question, options, decision type, required by | `DEC-*` artifact | M5.11 |

### Pipeline Coordination Contract Builders

| Builder | Schema | Purpose | Phase |
|---------|--------|---------|-------|
| `build_framework_state` | `framework_state.schema.json` | Construct persistent state artifact | M5.12 |
| `build_schema_catalog` | `schema_catalog.schema.json` | Construct catalog of active contracts | M5.13 |

### No Additional Builders

No builders beyond the 13 meta-schema contracts are planned. If a future need arises for a builder without a corresponding schema in `schemas/meta/`, the schema must be designed, reviewed, and approved first.

## Runtime Boundary

The ADF runtime is a future execution layer that does not exist yet. This section defines what it *may* do in the future and what it must *not* do yet, to prevent scope creep.

### What Future Runtime May Do (post-M5, post-builder extraction)

- Accept an explicit builder invocation with typed inputs
- Assign an output path for the artifact
- Invoke the builder with its contract
- Validate the output against the schema
- Store the artifact in a well-known location (e.g., `.adf/artifacts/`)
- Update `framework_state` with the new artifact reference
- Return the artifact ID and path to the caller
- Sequence multiple builder invocations according to a plan

### What Runtime Must Not Do Yet (blocked until explicit owner approval)

- Sequence builders autonomously (this is the orchestrator's role)
- Make decisions about scope, routing, or acceptance
- Execute git operations
- Invoke agents
- Modify repository files outside `.adf/`
- Touch schemas, agents, tests, docs, or source code
- Operate without explicit invocation
- Replace the agentic pipeline
- Activate candidate or primary mode

### Runtime Boundary Statement

> Runtime is a **builder executor and artifact store**, not an agent, not an orchestrator, and not a decision-maker. It is the bridge that makes agentic coordination produce deterministic, auditable artifacts. It must never absorb the responsibilities of agents, the orchestrator, or the coordinator.

## Migration Readiness Checklist For Each Future Builder

Before extracting any builder in a future M5.x phase, these conditions must be true:

| # | Condition | Gate |
|---|-----------|------|
| 1 | Corresponding schema in `schemas/meta/` is stable (version 2.0, no open changes) | Schema review |
| 2 | Corresponding agent in `agents/opencode/` exists and its contract references the schema | Agent audit |
| 3 | Input contract for the builder is fully derived from the schema's `required` + `properties` fields | Contract audit |
| 4 | Output artifact ID format matches the schema's `pattern` constraint | Schema compliance |
| 5 | No FBA source files were consulted during design | Extraction purity check |
| 6 | No Odoo, adapter, or project-specific terms appear in builder logic or tests | Contamination grep |
| 7 | Schema validation test exists and passes | Test evidence |
| 8 | Builder output matches what the corresponding agent would produce for the same input (semantic equivalence, not byte equality) | Contractual equivalence check |
| 9 | No `edit` or `bash` permissions escalated in any agent because of the builder | Permission audit |
| 10 | `framework_state` schema can accommodate the new artifact type | State schema check |

## Review Gates For Future M5.x Phases

Each M5.x sub-phase must pass these gates:

| Gate | Criteria |
|------|----------|
| **G1: Schema Stability** | The relevant schema has not changed in the last 2 commits. No open schema changes for the artifact type. |
| **G2: Contract Purity** | Builder design references only ADF schemas, agent contracts, and governance docs. Zero FBA references. |
| **G3: Implementation Scope** | Implementation touches only the builder file and its test file. No other files. If a `framework_state.schema.json` change is required, the phase must stop; a separate schema-governance phase must be approved first. |
| **G4: Test Evidence** | Schema validation test passes. Determinism test passes (same input × 3 = same output). Error handling test passes. |
| **G5: Agent Compatibility** | The corresponding agent's "Capacidad No Disponible" section lists the builder as a dependency gap. The builder fills that gap without replacing the agent. |
| **G6: No Capability Activation** | Builder extraction does not activate candidate mode, primary mode, controlled_inspect, controlled_commit, or any runtime capability. |
| **G7: Diff Review** | Diff is small, single-purpose, and reviewed. No forbidden files touched. |

## Stop Conditions

Stop the M5.x phase immediately if any of these occur:

1. A builder design references FBA source code, directory paths, or FBA-specific concepts.
2. A builder implementation would require modifying agents, schemas, or governance documents outside the approved scope.
3. A builder's contract shape diverges from the schema it claims to implement.
4. Scope creep: a builder starts incorporating runtime logic, adapter behavior, git operations, or autonomous decisions.
5. Two or more unrelated builders are being implemented in the same phase (violates one-at-a-time extraction).
6. Any file outside `allowed_files` for the phase is modified.
7. A builder attempts to import or depend on another builder not yet extracted.
8. Tests cannot be written without access to FBA test fixtures, mocks, or FBA-specific test data.
9. The builder introduces new dependencies not already in `pyproject.toml` without prior approval.

## Risks and Anti-Overengineering Rules

### Risks

| Risk | Mitigation |
|------|------------|
| Copying FBA builder logic unconsciously | Every builder phase must include a contamination grep against FBA terms |
| Builders absorbing agent responsibilities | Each builder must stay pure (input → artifact). No decisions. |
| Runtime creeping into builder extraction | Runtime boundary is explicitly in section 11; any runtime-like logic blocks the phase |
| Builders being designed for only one pipeline mode | Builders must work for both agentic and programmatic pipelines |
| Overengineering the builder contract | The contract is a Python callable with typed dict → typed dict. No frameworks, no DI, no plugins |
| Premature builder chaining | Builders must be invocable independently. No implicit sequencing |
| Schema instability | If a schema changes after a builder is extracted, the builder must be updated in a separate corrective phase |

### Anti-Overengineering Rules

1. **No builder base class**: Each builder is a plain function. No `AbstractBuilder`, no inheritance hierarchy, no metaclasses.
2. **No dependency injection**: Builders receive explicit inputs. No DI container, no service locator.
3. **No plugin system**: The 13 planned builders are exhaustive. No plugin architecture, no dynamic builder registry.
4. **No event system**: No publish/subscribe, no hooks, no lifecycle events.
5. **No configuration files**: Builder behavior is fully specified by its input contract. No YAML/TOML/JSON config for builders.
6. **No middleware**: No pipeline middleware, no interceptor chain, no decorator stack for cross-cutting concerns.
7. **No async by default**: Builders are synchronous. Async is not needed for deterministic artifact construction.
8. **No CLI**: Builders are Python callables. A future CLI wrapping them is an adapter concern, not a core concern.
9. **No web API**: Builders are library code. No HTTP endpoints, no RPC, no server.
10. **No caching layer**: Builders are deterministic. If caching is needed, it belongs in the runtime layer, not in builders.

## Proposed Next Phases After M5

| Phase | Description | Prerequisite |
|-------|-------------|-------------|
| **M5.1** | Design and implement `build_intent` | M5 approved + schema stable |
| **M5.2** | Design and implement `build_policy_constraints` | M5.1 complete |
| **M5.3** | Design and implement `build_roadmap_slice` | M5.2 complete |
| **M5.4** | Design and implement `build_plan` | M5.3 complete |
| **M5.5** | Design and implement `build_task_packet` | M5.4 complete |
| **M5.6** | Design and implement `build_context_bundle` | M5.5 complete |
| **M5.7** | Design and implement `build_implementation_report` | M5.6 complete |
| **M5.8** | Design and implement `build_test_report` | M5.7 complete |
| **M5.9** | Design and implement `build_review_report` | M5.8 complete |
| **M5.10** | Design and implement `build_git_operation` | M5.9 complete |
| **M5.11** | Design and implement `build_decisions` | M5.10 complete |
| **M5.12** | Design and implement `build_framework_state` | M5.11 complete |
| **M5.13** | Design and implement `build_schema_catalog` | M5.12 complete |
| **M6** | Builder tests and schema validation hardening | All M5.x phases complete |
| **M7** | Agnostic dry-run with builder pipeline | M6 complete |
| **M8** | Minimal runtime design and implementation | M7 complete |
| **M9** | FBA adapter notes (adapter layer, not core) | M8 complete |

Each M5.x phase must be a self-contained design → implement → test → review cycle, producing exactly one builder. No phase may produce more than one builder. Phases must be sequential (each builder may depend on the previous builder's artifact as input).

## Definitions And Reference

- **FBA**: `factory-build-agent`, the original project from which ADF was extracted.
- **Meta-framework**: The ADF project itself — a framework for agentic development workflows.
- **Schema contract**: A JSON Schema file in `schemas/meta/` that defines the shape of an ADF artifact.
- **Artifact**: A JSON document conforming to a schema contract, identified by a unique ID.
- **Pipeline**: The sequence of contract transformations from intent to git operation.
- **Agentic pipeline**: The pipeline as executed by ADF agents (LLM reasoning).
- **Programmatic pipeline**: The pipeline as executed by builders and runtime (deterministic).
- **Extraction**: The process of deriving a clean, agnostic builder from schema contracts without copying FBA source code.

## Approval and Activation

This document is a design artifact for M5. It does not activate candidate mode, primary mode, any builder, any runtime, or any git capability. It requires coordinator review and owner approval before any M5.x implementation phase begins.

Approval criteria:
- All 16 sections are complete and internally consistent.
- Builder contract shape is implementable without contradicting agent contracts.
- Runtime boundary is explicit and does not pre-authorize execution.
- Anti-overengineering rules are enforceable.
- Stop conditions are testable.
- No forbidden files are touched.
