# Minimal Builder Invocation / Runtime Strategy (M6.1)

## 1. Purpose

This document defines the **design-only, governance-only** strategy for a future minimal runtime that invokes ADF builders, stores artifacts, updates `framework_state`, and preserves the boundary between the orchestrator, agents, builders, and the runtime.

This is a **design phase** (M6.1). No runtime is created, no code is written, and no files outside this document are touched. The strategy exists so that future phases (M7, M8) have a clear, minimal contract to implement against — not so that implementation begins now.

## 2. Current Baseline

- **M5 is fully complete.** All 13 programmatic builders are extracted, tested (215 tests passing), and reviewed.
- Every builder is a pure, deterministic, project-agnostic artifact constructor conforming to the contract shape defined in `docs/governance/builder-runtime-extraction-strategy.md`.
- No runtime exists.
- No adapters exist.
- No builder registry, CLI, or invocation layer exists.
- Candidate mode is **not active**.
- Primary mode is **not active**.
- `controlled_inspect` and `controlled_commit` are **not implemented**.
- The framework operates in shadow/bootstrap mode only.

All 13 builders are importable Python callables in `src/agentic_development_framework/builders/`, each producing one schema artifact per invocation.

## 3. Minimal Invocation Model

The future runtime must implement a **single, explicit, caller-driven** invocation path. Nothing is implicit, ambient, or autonomous.

### 3.1 Invocation Flow

```
explicit caller request
  → builder selection (by caller, not by runtime)
  → typed input assembly (by caller, not by runtime)
  → output path assignment (by caller or by runtime under caller direction)
  → builder invocation (runtime invokes the builder callable)
  → builder returns artifact dict
  → schema validation (runtime validates against the corresponding schema/meta contract)
  → artifact written to assigned path (runtime performs the I/O)
  → artifact stored in artifact store (runtime records the artifact)
  → framework_state update proposal produced (runtime does NOT apply the update)
  → result returned to caller (artifact ID, path, validation outcome, state update proposal)
```

### 3.2 What the Runtime Must Not Decide

The runtime is a **builder executor and artifact store**, not a decision-maker. It must never decide:

- Which builder to invoke
- What scope or priority an invocation has
- Whether an artifact should be accepted (validation produces evidence; acceptance is the orchestrator's gate)
- What the next step in the pipeline should be
- Whether to execute git operations
- Whether to invoke agents
- Whether to activate candidate or primary mode

The runtime executes what it is told to execute, produces evidence, and returns. It has no autonomy.

### 3.3 Minimal Invocation Contract (Future)

```python
# Conceptual contract only — not implemented in M6.1
def invoke_builder(
    builder_name: str,
    inputs: Dict[str, Any],
    output_path: Optional[str] = None,
    *,
    validate: bool = True,
    store: bool = True,
) -> InvocationResult:
    ...
```

All parameters are explicit. There is no configuration file, no environment variable fallback, no ambient repository scanning.

## 4. Artifact Store Layout

The artifact store is a **design proposal** for where future runtime stores builder outputs. It must not be created during M6.1.

### 4.1 Root Location

```
.adf/
  artifacts/          # root of the artifact store
    metadata.json     # inventory/index of stored artifacts (explicit, not hidden state)
```

### 4.2 Per-Artifact-Type Grouping

Artifacts are grouped by their type prefix for discoverability:

```
.adf/artifacts/
  intent/             # INTENT-* artifacts
  policy/             # POLICY-* artifacts
  roadmap/            # RSLICE-* artifacts
  plan/               # PLAN-* artifacts
  task_packet/        # TPACKET-* artifacts
  context/            # CTX-* artifacts
  implementation/     # IMPL-* artifacts
  test/               # TEST-* artifacts
  review/             # REV-* artifacts
  git/                # GIT-* artifacts
  decisions/          # DEC-* artifacts
  state/              # framework_state snapshots
  catalog/            # schema_catalog snapshots
  validation/         # validation reports (one per artifact invocation)
```

### 4.3 Naming Convention

Each artifact file is named by its unique artifact ID:

```
{ARTIFACT_PREFIX}-{timestamp_or_sequence}.json
```

Examples:
- `INTENT-20260516-001.json`
- `PLAN-20260516-002.json`
- `REV-20260516-003.json`

The exact ID format is defined by each schema's `pattern` constraint on the `artifact_id` field. The runtime does not invent IDs; it uses the ID produced by the builder.

### 4.4 Validation Report Strategy

Each builder invocation that passes through the runtime produces a validation report stored alongside or near the artifact. Two options are proposed (final choice deferred to M8 implementation):

**Option A (co-located):**
```
.adf/artifacts/intent/INTENT-20260516-001.json
.adf/artifacts/intent/INTENT-20260516-001.validation.json
```

**Option B (separate tree):**
```
.adf/artifacts/intent/INTENT-20260516-001.json
.adf/artifacts/validation/INTENT-20260516-001.validation.json
```

Either option must record: artifact ID, artifact path, schema validated against, validation outcome (pass/fail), validation findings list, timestamp, and builder name.

### 4.5 Metadata Strategy

`.adf/artifacts/metadata.json` is a registry of stored artifacts, not a runtime database. It records:
- Artifact ID
- Artifact type
- File path relative to `.adf/artifacts/`
- Validation outcome
- Timestamp
- Builder name

The metadata file is **written explicitly** by the runtime on each store operation. It is not a live index, not a database, and not a source of truth for routing decisions. Its purpose is discoverability and auditability.

### 4.6 What the Artifact Store Must Not Do

- Must not be used as ambient state by builders
- Must not be read by builders (builders receive explicit inputs)
- Must not auto-index or auto-discover artifacts for pipeline routing
- Must not serve as a configuration store
- Must not be a database, cache, or event source

## 5. Input Wiring Strategy

### 5.1 Explicit Input Passing

Every builder invocation must receive its inputs through an **explicit `inputs` dict** passed by the caller. The runtime does not synthesize, infer, or complete inputs. If a required field is missing, the builder raises `ValueError` — the runtime surfaces this as an invocation failure and does not attempt to fill gaps.

### 5.2 Resolving Prior Artifact References

Many builders require references to prior artifacts (e.g., `build_plan` needs an `intent_id` referencing a prior `INTENT-*` artifact, or a `roadmap_slice_id` referencing a prior `RSLICE-*` artifact). In a future runtime, these references are resolved by the **caller** (orchestrator), not by the runtime.

The runtime **may** provide a helper that reads a prior artifact from `.adf/artifacts/` by artifact ID and returns it to the caller — but this helper:
- Is opt-in, never implicit
- Returns the artifact dict, not a resolved reference
- Does not chain builders automatically
- The caller remains responsible for assembling the input dict

```
# Conceptual — not implemented in M6.1
# The orchestrator (caller) resolves references before invoking:
prior_intent = runtime.read_artifact("INTENT-20260516-001")  # explicit read
inputs = {
    "intent": prior_intent,
    "roadmap_slice_id": "RSLICE-20260516-001",
    ...
}
result = runtime.invoke_builder("build_plan", inputs)
```

### 5.3 Forbidden Input Sources

The runtime must never wire inputs from:
- Environment variables
- Repository filesystem scanning (e.g., detecting what branch, what directory)
- Git log, git status, or git diff
- Hidden state files outside `.adf/`
- Previous invocation side effects not stored in the artifact store
- Configuration files (YAML, TOML, JSON configs outside `.adf/`)
- Default values that the builder does not define

Input is **what the caller provides**, nothing more, nothing less.

### 5.4 Cross-Builder References

Builders may accept artifact IDs as string fields (e.g., `intent_id`, `plan_id`). The runtime validates that these IDs conform to the schema's `pattern` for that artifact type. The runtime does not resolve the reference into a full artifact during builder invocation — the builder itself handles that if it needs the referenced artifact's fields, in which case the caller must pass the full referenced artifact's dict as part of the inputs.

This keeps the runtime simple: it passes dicts, validates IDs against patterns, and does not perform graph resolution or dependency walking.

## 6. framework_state Update Strategy

### 6.1 Design Principle: Safest Minimal Approach

The runtime must **not** directly mutate `framework_state`. Instead, the runtime produces an **update proposal** — a delta that describes what would change. The orchestrator (or a future state manager) reviews the proposal and applies it if accepted.

Rationale:
- Direct mutation by a stateless executor is dangerous: it can overwrite decisions it did not make.
- A proposal can be reviewed, merged, or rejected by the component that owns state authority.
- This preserves the boundary: runtime executes, orchestrator decides.

### 6.2 Update Proposal Shape (Conceptual)

The `state_update_proposal` fields below (e.g., `set_current_phase`, `update_statuses`) are present in the result **only when the caller/orchestrator explicitly supplies them as invocation context**. The runtime does not infer, derive, or originate phase or status values from builder output, sequence position, or any other source.

```
InvocationResult:
  artifact_id: "PLAN-20260516-001"
  artifact_path: ".adf/artifacts/plan/PLAN-20260516-001.json"
  artifact_type: "plan"
  validation: { outcome: "pass", findings: [...] }
  state_update_proposal:
    add_artifact_refs:
      - type: "plan"
        id: "PLAN-20260516-001"
        path: ".adf/artifacts/plan/PLAN-20260516-001.json"
    set_current_phase: "M5.5"        # proposed, not applied
    update_statuses:
      M5.4: "complete"
      M5.5: "in_progress"
    pending_decisions: null           # runtime never proposes decisions
```

### 6.3 What the Runtime Proposes vs What It Must Not Propose

| Field | Runtime May Propose | Runtime Must Not Propose |
|-------|--------------------|--------------------------|
| `artifact_refs` additions | Yes (recording what was produced) | Must not remove or alter existing refs |
| `current_phase` | No — may only be included when explicitly supplied by the caller/orchestrator as invocation context | Must not infer, decide, or derive phase transitions from builder output or any other source |
| `statuses` | No — may only be included when explicitly supplied by the caller/orchestrator as invocation context | Must not infer or derive status transitions from builder output or sequence position |
| `pending_decisions` | **Never** | Decisions belong to the orchestrator |
| `mode` (shadow/candidate/primary) | **Never** | Mode promotion requires owner approval |
| `gates` | **Never** | Gates are coordinator/orchestrator authority |
| Git state | **Never** | Runtime does not touch git |

### 6.4 State Update Conflict

If a state update proposal would conflict with the current `framework_state` (e.g., referencing an artifact ID that already exists, or setting `current_phase` to a value incompatible with the current state), the runtime must:
1. Detect the conflict before producing the proposal.
2. Mark the proposal as `conflicted: true` with a description of the conflict.
3. Return the conflicted proposal to the caller.
4. Not silently overwrite or merge.

The caller (orchestrator) resolves the conflict.

### 6.5 No Schema Modification

This document does not propose or authorize any changes to `framework_state.schema.json`. The update proposal strategy is designed to work within the existing schema contract. If the existing schema proves insufficient, a separate schema-governance phase must be approved.

## 7. Orchestrator vs Runtime Boundary

### 7.1 Responsibilities Table

| Concern | Orchestrator (`agents/opencode/orchestrator.md`) | Runtime (future) |
|---------|--------------------------------------------------|-------------------|
| Pipeline flow and sequencing | **Owns** | Does not decide |
| Delegation to agents | **Owns** | Does not invoke agents |
| Gate decisions (approve/block/reject) | **Owns** | Provides validation evidence only |
| Scope and priority decisions | **Owns** | Does not decide |
| Acceptance of artifacts | **Owns** (reviewer agent or coordinator) | Provides validation pass/fail |
| Git operations | Delegates to git-operator agent | Never executes git |
| Mode activation (candidate/primary) | Requires owner approval | Never activates |
| Builder invocation | **Delegates** to runtime | **Executes** |
| Schema validation | May use runtime's validation output | **Performs** validation |
| Artifact storage | May direct runtime where to store | **Performs** I/O |
| framework_state updates | **Reviews and applies** proposals | Produces update proposals |
| Coordination decisions | **Owns** | Provides evidence |

### 7.2 Boundary Statement

> The runtime is a **builder executor and artifact store**. It is a tool used by the orchestrator, agents, and coordinator — not a peer, not a replacement, and not an autonomous subsystem. It must never absorb the responsibilities of agents (reasoning), the orchestrator (flow control), the reviewer (acceptance), the git-operator (version control), or the coordinator (architecture decisions).

### 7.3 What Builders Do vs What Agents Do

| | Builder | Agent |
|---|---------|-------|
| Type | Deterministic Python callable | LLM-prompted reasoning agent |
| Input | Typed dict matching schema contract | Natural language + structured context |
| Output | Single schema artifact (dict) | Structured but contextual output |
| Determinism | Same inputs → same outputs every time | May vary; reasoned, not deterministic |
| Role | Reproducible artifact production | Contextual reasoning and decision support |
| Invocation | Explicit, by runtime | Explicit, by orchestrator |

Builders and agents are **complementary**, not redundant. A builder can produce the same artifact shape as an agent would reason about, but it does so deterministically and without reasoning. This enables auditable, reproducible pipelines without replacing agentic judgment.

## 8. Validation and Evidence Strategy

### 8.1 Required Validation Before Artifact Acceptance

Before any artifact is accepted into the artifact store, the runtime must perform these validations:

1. **Schema validation** — The artifact must pass validation against its corresponding `schemas/meta/*.schema.json` contract. This uses `jsonschema` (Draft-07). The result is a pass/fail with structured findings.

2. **Deterministic checks** — The runtime may (optionally, in diagnostic/dry-run mode) invoke the same builder twice with identical inputs and verify the outputs are byte-identical. This confirms builder determinism at invocation time.

3. **Artifact path evidence** — The runtime must record the exact output path, the artifact ID, the builder name, and the timestamp. This evidence is included in the validation report.

4. **State update evidence** — If the runtime produces a `framework_state` update proposal, the proposal must include the validation outcome as evidence supporting the proposal. A proposal without validation evidence is invalid.

### 8.2 Validation Report Shape (Conceptual)

```json
{
  "artifact_id": "PLAN-20260516-001",
  "artifact_path": ".adf/artifacts/plan/PLAN-20260516-001.json",
  "builder": "build_plan",
  "schema": "schemas/meta/plan.schema.json",
  "validated_at": "2026-05-16T12:00:00Z",
  "validation_outcome": "pass",
  "findings": [],
  "determinism_check": "not_performed",
  "state_update_proposal_compatible": true
}
```

### 8.3 Evidence, Not Acceptance

Validation produces **evidence**. It does not _accept_ the artifact. Acceptance is a gate decision made by the reviewer agent, orchestrator, or coordinator. The runtime provides evidence so that the acceptance decision is informed, not so that it is automated.

### 8.4 No Tests in M6.1

This document does not create or authorize the creation of tests. Tests for validation and evidence strategies will be designed in M7 (agnostic dry-run) and implemented in M8 (minimal runtime).

## 9. Failure Model

The runtime must **fail closed**: every failure produces structured evidence and stops the invocation. No silent continuation, no partial writes treated as success, no fallback to default behavior.

### 9.1 Invalid Input Failure

| Condition | Behavior |
|-----------|----------|
| Missing required field in inputs | Builder raises `ValueError`. Runtime catches, produces `InvocationFailure` with reason and the builder name. No artifact written. |
| Input field type mismatch | Builder raises `TypeError` or `ValueError`. Runtime surfaces the error. |
| Unknown builder name | Runtime raises `BuilderNotFoundError`. No artifact written. |

### 9.2 Builder Failure

| Condition | Behavior |
|-----------|----------|
| Builder raises an exception | Runtime catches, produces `InvocationFailure` with exception details. No artifact written. No partial state update. |
| Builder returns output that is not a dict | Runtime validates return type. Produces `InvocationFailure` with mismatch description. |

### 9.3 Schema Validation Failure

| Condition | Behavior |
|-----------|----------|
| Artifact fails schema validation | Runtime does **not** store the artifact as an accepted/canonical artifact in the artifact store. The invalid artifact may be captured as **failure evidence or quarantine output only** (e.g., in a `.adf/artifacts/validation/` or `.adf/quarantine/` location, never under the canonical type-group directory). The runtime produces a `validation_outcome: "fail"` with findings list. The invocation result is marked `accepted: false`. No state update proposal is produced (invalid artifacts must not trigger state transitions). |

### 9.4 Write Failure

| Condition | Behavior |
|-----------|----------|
| Output path is not writable | Runtime raises `WriteError`. No artifact written. No state update. |
| Disk full or I/O error | Runtime raises `WriteError`. No artifact written. No state update. |
| Output path is outside `.adf/` | Runtime refuses. Raises `PathNotAllowedError`. No artifact written. |

### 9.5 State Update Conflict

| Condition | Behavior |
|-----------|----------|
| Proposed artifact ID already exists in `framework_state.artifact_refs` | Runtime marks proposal as `conflicted: true` with conflict description. Returns conflicted proposal to caller. Does not write state. |
| Proposed `current_phase` is incompatible with current state | Same as above. |
| Proposal references an artifact type not in `artifact_refs` schema | Runtime marks as invalid proposal. |

### 9.6 Failure Response Shape (Conceptual)

```json
{
  "success": false,
  "error_type": "SchemaValidationError",
  "builder": "build_plan",
  "artifact_path": ".adf/artifacts/plan/PLAN-20260516-001.json",
  "validation_outcome": "fail",
  "findings": [
    { "field": "tasks", "issue": "Array is empty but minItems is 1" }
  ],
  "state_update_proposal": null
}
```

All failures return structured evidence. No failure is silent.

## 10. Non-Goals / Explicitly Out of Scope

The following are **explicitly excluded** from this design and from any M6 phase:

- Runtime implementation (code, files, modules, packages)
- Builder registry (dynamic discovery, plugin loading, or classpath scanning)
- CLI for builder invocation (argparse, click, or shell wrappers)
- Adapter layer (FBA, Odoo, project-specific)
- Git execution (the runtime never runs `git`)
- Agent invocation (the runtime never invokes LLM agents)
- Candidate mode activation
- Primary mode activation
- `controlled_inspect` or `controlled_commit` implementation
- FBA/Odoo semantics in any form
- Plugin systems, dependency injection, middleware, or event buses
- Web API, HTTP endpoints, or RPC
- Async runtime, asyncio, or background execution
- Caching layer or memoization infrastructure
- Scheduler, daemon, or autonomous/background execution
- Any file modification outside `docs/governance/minimal-builder-invocation-runtime-strategy.md`
- Builder modification, test modification, schema modification, or agent modification
- Production, candidate, or primary readiness claims

## 11. Future Phase Decomposition

After M6.1, the following phases are proposed. Each is **design-first and gated** — no implementation is authorized by this document.

### M7 — Agnostic Dry-Run Design and Evidence

**Type:** Design/governance only.

**Scope:**
- Design a dry-run mode for the runtime that invokes builders without writing artifacts to disk.
- Define evidence collection: what traces, diffs, and validation reports a dry-run produces.
- Design the comparison method between agent-produced outputs and builder-produced outputs (semantic equivalence, not byte equality).
- Define how dry-run results inform future implementation decisions.
- No runtime implementation.

**Gate:** Coordinator review and approval of this document (M6.1).

### M8 — Minimal Runtime Implementation

**Type:** Implementation (first code-producing phase after M6/M7).

**Scope:**
- Implement the minimal runtime as a Python module in `src/agentic_development_framework/`.
- Implement the invocation contract from section 3.3.
- Implement the artifact store layout from section 4.
- Implement schema validation integration.
- Implement `framework_state` update proposal generation.
- Implement the failure model from section 9.
- Write runtime-specific tests (separate from builder tests).
- No autonomous execution, no agent invocation, no git, no mode activation.

**Gate:** M7 approved. Owner authorization to write code outside `docs/governance/`.

### M9 — Adapter Notes

**Type:** Design only.

**Scope:**
- Document how a downstream project (e.g., FBA) would implement an adapter that translates between ADF artifacts and its project-specific environment.
- Define adapter contract boundary: what belongs in the adapter vs what stays in ADF core.
- No adapter implementation.
- No FBA source inspection.

**Gate:** M8 complete. Owner approval for adapter design.

### Future Phase Gates (General)

No future phase may begin without:
1. The preceding phase being complete and approved.
2. Owner authorization for any code-producing phase.
3. A clean `git status` before starting.
4. Explicit allowed/forbidden file lists.
5. All anti-overengineering rules still in effect.

## 12. Approval Criteria

This document is approved when:

1. **Internal consistency** — All 12 sections agree on the runtime's role, boundaries, and constraints. No internal contradictions.
2. **No forbidden scope introduced** — No implementation, no registry, no CLI, no adapters, no git, no agent invocation, no mode activation, no FBA/Odoo semantics, no automation.
3. **Runtime boundary remains minimal** — The runtime is consistently described as a builder executor and artifact store, never as a decision-maker, orchestrator replacement, or autonomous system.
4. **No files outside allowed_files are touched** — Only `docs/governance/minimal-builder-invocation-runtime-strategy.md` is created. No builders, schemas, agents, tests, source code, or configuration files are modified.
5. **No production/candidate/primary readiness claimed** — The document is a design artifact for governance, not an activation document. It does not claim the framework is ready for any operational mode.

### Stop Conditions

Stop this phase immediately and do not commit if:
- Any forbidden file is touched.
- The document proposes implementation instead of design.
- The document introduces autonomous execution, hidden state, or implicit behavior.
- The document expands runtime authority beyond builder execution and artifact storage.
- The document claims production, candidate, or primary readiness.

---

*M6.1 — Design only. No implementation. No code. No registry. No CLI. No runtime.*
