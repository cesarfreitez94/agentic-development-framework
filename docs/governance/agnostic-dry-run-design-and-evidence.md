# Agnostic Dry-Run Design and Evidence (M7.1)

## 1. Purpose

This document defines the **design-only, governance-only** plan for a future agnostic dry-run capability within ADF. M7 is a design phase: no runtime exists and no runtime is implemented here. The term "dry-run" throughout this document means **simulated or planned execution evidence**, not productive execution, not artifact persistence, and not autonomous pipeline operation.

The dry-run defined here is a non-persistent, caller-driven validation flow. It exists so that M8 (minimal runtime implementation) has a clear, minimal evidence contract to implement against.

## 2. Baseline

- **M5 is fully complete.** All 13 programmatic builders extracted, tested (215 tests passing), and reviewed.
- **M6.1 is complete.** The minimal builder invocation/runtime strategy is defined in `docs/governance/minimal-builder-invocation-runtime-strategy.md` (commit `ab023d6`).
- **Current mode remains shadow/bootstrap.** No production, candidate, or primary operation.
- **Candidate and primary modes remain inactive.** No mode activation has occurred or is authorized.
- **`controlled_inspect` and `controlled_commit` remain unimplemented.** They are not prerequisites for M7.
- **No runtime, no CLI, no adapters, no registry, no artifact store exist.**
- **All 13 builders are pure, deterministic Python callables** in `src/agentic_development_framework/builders/`, each conforming to the contract shape in `docs/governance/builder-runtime-extraction-strategy.md`.
- **This document does not alter any of the above.**

## 3. Dry-Run Definition

A **dry-run** is a **future/conceptual** non-persistent, caller-driven validation flow that, when implemented, would invoke a builder in a simulated execution context, collect structured evidence about what the invocation produced and whether it is valid, and return that evidence to the caller — without writing any canonical artifact to disk and without mutating any persistent framework state.

A dry-run **would** invoke builders only in a future runtime design; **M7 only designs the behavior** and does not invoke any builder. The dry-run contract:

- **Must not write canonical artifacts** to `.adf/artifacts/` or any persistent artifact store.
- **Must not mutate `framework_state`** in any persistent form.
- **Must not execute git** operations (no `git add`, `git commit`, `git push`, `git diff`, or `git status` writes).
- **Must not invoke agents** (no LLM agent invocation, no reasoning delegation).
- **Must not decide acceptance.** Dry-run produces evidence; acceptance remains a reviewer/orchestrator gate.
- **Must not activate candidate mode, primary mode, or any autonomous execution mode.**

A dry-run is a **read-evaluate-return** pattern: invoke the builder with explicit inputs, validate the output, compare if a target exists, produce structured evidence, return — and leave no persistent trace outside the evidence returned to the caller.

## 4. Future Dry-Run Invocation Model

The following is a **conceptual input shape** for a future dry-run invocation. It is not implemented in M7 and no code exists for it.

```
DryRunRequest (conceptual):
  builder_name: str               # e.g., "build_plan"
  explicit_inputs: Dict[str, Any] # typed dict matching the builder's input contract
  expected_schema: Optional[str]  # schema path or reference, e.g. "schemas/meta/plan.schema.json"
  prior_artifact_refs: Optional[Dict[str, str]]  # artifact ID -> expected type, for context
  comparison_target: Optional[Dict[str, Any]]    # agent-produced artifact to compare against
  dry_run_context: Optional[Dict[str, Any]]      # caller-supplied context (phase, milestone, etc.)
```

All fields are explicit. No ambient repository scanning, no environment variable fallback, no hidden state resolution.

Key design constraints for the future invocation:

- **`builder_name`** selects the builder callable. The runtime does not auto-select, discover, or infer which builder to invoke.
- **`explicit_inputs`** are passed directly to the builder. The runtime does not synthesize, infer, or complete missing fields.
- **`expected_schema`** names the schema contract used for validation. If omitted, the runtime may derive it from the builder's known output type, but must not guess.
- **`prior_artifact_refs`** provide context for the caller's reference resolution. The dry-run does not resolve these references itself — it may record them as context in evidence.
- **`comparison_target`** is an optional agent-produced artifact for semantic comparison (see Section 7). When absent, no comparison is performed.
- **`dry_run_context`** is caller-supplied metadata (milestone, phase, invocation ID, reviewer, etc.) carried into evidence. The runtime does not interpret or act on it.

## 5. Dry-Run Evidence Model

A future dry-run invocation must return a structured **DryRunEvidence** result. Evidence is for review, not for acceptance.

### 5.1 Evidence Fields

```
DryRunEvidence (conceptual):
  builder_name: str
  input_summary: Dict[str, Any]       # summary of inputs (may redact sensitive fields)
  produced_artifact: Optional[Dict]   # the artifact dict produced by the builder (in-memory, not persisted)
  artifact_preview: Optional[str]     # truncated or summarized preview for human review
  schema_validation:                  # validation outcome block
    schema_ref: str                   # schema path or URI validated against
    outcome: "pass" | "fail"
    findings: List[Dict]              # structured findings (field, issue, severity)
  deterministic_check:                # deterministic check result
    performed: bool
    result: Optional["identical" | "different"]
  comparison: Optional[Dict]          # comparison result if comparison_target was provided
    outcome: str                      # one of the mismatch categories in Section 7
    details: List[Dict]               # field-level comparison details
  state_update_proposal_preview: Optional[Dict]  # what the update proposal would look like (preview only)
  no_write_confirmation: bool         # always true for dry-run; confirms nothing was written
  no_git_confirmation: bool           # always true for dry-run; confirms no git operations
  timestamp: str                      # ISO 8601 timestamp of the dry-run
```

### 5.2 Evidence Constraints

- **`produced_artifact`** is the full dict returned by the builder. It exists only in memory and is returned to the caller. It is never written to `.adf/artifacts/` or any file.
- **`schema_validation`** uses the existing `schemas/meta/*.schema.json` contracts (Draft-07 `jsonschema`). Validation evidence is structured: each finding includes the field path, the issue description, and a severity indicator (error, warning).
- **`deterministic_check`** may be performed by invoking the same builder twice with identical inputs and comparing byte-level output. This is optional and diagnostic.
- **`comparison`** is present only when `comparison_target` is supplied. It uses semantic equivalence (Section 7).
- **`state_update_proposal_preview`** is what the runtime *would* propose as a `framework_state` update, but it is a preview only. It is never applied. It exists so the reviewer can assess whether the produced artifact is compatible with the current state trajectory.
- **`no_write_confirmation`** and **`no_git_confirmation`** are always `true` for dry-run. They are explicit assertions that no side effects occurred.

### 5.3 Evidence Display

Dry-run evidence may be displayed (printed to stdout, returned as structured data to the caller) but must not be written as a persistent file. If future diagnostic or quarantine persistence is needed (e.g., saving a dry-run evidence record for audit), it must be separately approved as a diagnostic/quarantine behavior — it is not part of the dry-run contract defined here.

## 6. Non-Persistence Rules

The dry-run is defined by what it does **not** persist. These rules are absolute:

1. **No canonical artifact writes.** Dry-run must not write to `.adf/artifacts/intent/`, `.adf/artifacts/plan/`, or any type-group directory.
2. **No `.adf/artifacts/` writes.** No artifact file of any kind is created under `.adf/`.
3. **No `metadata.json` writes.** No inventory/index is updated or created.
4. **No `framework_state` writes.** No persistent state mutation occurs. The `state_update_proposal_preview` is in-memory only.
5. **No validation report files written.** Validation evidence is returned in memory, not saved as `.validation.json` or similar.
6. **Dry-run evidence may be displayed or returned to the caller in memory only.** If a future implementation extends this to write evidence to a quarantine or diagnostic store, that extension requires separate approval.

If a future implementation needs to persist dry-run evidence:
- The destination must be outside `.adf/artifacts/` canonical paths.
- The file must be clearly marked as diagnostic/quarantine, not canonical.
- The behavior must be opt-in, not default.
- The owner must approve the persistence surface.

## 7. Agent-produced vs Builder-produced Comparison

When an agent-produced artifact is provided as `comparison_target`, the dry-run compares it to the builder-produced artifact using **semantic equivalence, not byte equality**.

### 7.1 Comparison Principles

- Byte-level comparison is rejected: JSON serialization order, whitespace, and formatting differences are irrelevant.
- Field order differences are not meaningful.
- The comparison compares **meaning**, **structure**, and **constraint satisfaction**, not serialization fidelity.

### 7.2 Semantic Dimensions Compared

| Dimension | Description |
|-----------|-------------|
| Required fields | Are all schema-required fields present in both artifacts with comparable values? |
| Artifact IDs and patterns | Do IDs conform to the expected pattern? Are referenced IDs present in both? |
| References (prior artifact refs) | Do both artifacts reference the same prior artifacts by ID? |
| Task/order meaning | If the artifact contains task lists, sequences, or ordering: is the functional meaning preserved? |
| Policy constraints | If the artifact encodes constraints, rules, or conditions: are they semantically equivalent? |
| Lifecycle and gate semantics | Do phase designations, gate conditions, and status values convey the same intent? |
| Risk and decision preservation | Are risk assessments, blocking conditions, and decision rationales preserved? |

### 7.3 Mismatch Categories

| Category | Meaning |
|----------|---------|
| `equivalent` | Both artifacts convey the same semantic content. No meaningful difference. |
| `equivalent_with_format_differences` | Same semantics, but differ in field ordering, whitespace, key ordering, or serialization format. |
| `partial_equivalence` | Core meaning aligns, but some fields differ in a way that does not change pipeline intent. Differences are documented. |
| `schema_valid_but_semantically_different` | Both pass schema validation but convey different meaning (different phase, different scope, different constraints). |
| `schema_invalid` | One or both artifacts fail schema validation. Schema compliance failure precedes semantic comparison. |
| `unsafe_or_out_of_scope` | The artifact contains fields, values, or semantics outside the expected schema or safety boundary. |

### 7.4 Comparison Governance

- Comparison informs review only. It does **not** automatically approve, reject, or substitute artifacts.
- A `partial_equivalence` or `schema_valid_but_semantically_different` result must be escalated to the reviewer/orchestrator.
- Comparison is **never** used to silently select the builder output over agent output or vice versa.
- The orchestrator owns the decision about which artifact (if any) is accepted.

## 8. Pipeline Dry-Run Scenario

The following is an **illustrative conceptual pipeline sequence** showing how dry-run could validate a full artifact chain in a future phase. It is not an autonomous runtime plan, not a production workflow, and not a commitment to implement this exact sequence in M8.

### 8.1 Illustrative Sequence

```
1. intent           → build_intent(inputs)              → INTENT artifact preview
2. policy_constraints → build_policy_constraints(inputs)  → POLICY artifact preview
3. roadmap_slice    → build_roadmap_slice(inputs)        → RSLICE artifact preview
4. plan             → build_plan(inputs)                 → PLAN artifact preview
5. task_packet      → build_task_packet(inputs)          → TPACKET artifact preview
6. context_bundle   → build_context_bundle(inputs)       → CTX artifact preview
7. implementation_report → build_implementation_report(inputs) → IMPL artifact preview
8. test_report      → build_test_report(inputs)          → TEST artifact preview
9. review_report    → build_review_report(inputs)        → REV artifact preview
10. git_operation   → build_git_operation(inputs)        → GIT artifact preview
11. decisions       → build_decisions(inputs)            → DEC artifact preview
12. framework_state → build_framework_state(inputs)      → STATE artifact preview
13. schema_catalog  → build_schema_catalog(inputs)       → CATALOG artifact preview
```

### 8.2 Sequencing Governance

- The sequence above is **illustrative**, not prescriptive. The orchestrator owns pipeline sequencing.
- In a future dry-run, the caller invokes each builder explicitly. The runtime executes only the builders the caller selects, one at a time.
- There is no implicit chaining, no automatic progression to the next builder, and no autonomous pipeline execution.
- Cross-builder references (e.g., `plan` requiring an `intent_id`) are resolved by the caller before each invocation. The dry-run does not walk the dependency graph.
- The dry-run may be invoked for a single builder or a sequence. The sequence is always caller-directed.

### 8.3 What the Pipeline Scenario Is Intended to Validate in a Future Dry-Run

- Whether all 13 builders can be invoked in a logical order with compatible input/output shapes.
- Whether each builder's output passes schema validation.
- Whether the artifact chain is internally consistent (IDs reference valid prior artifacts).
- Whether builder outputs can be compared to agent outputs at any point in the chain.
- Whether dry-run evidence accumulates without persistence.

## 9. Failure Evidence

A future dry-run must **fail closed**: every failure produces structured evidence and stops. No silent continuation, no partial success treated as complete.

### 9.1 Failure Categories and Evidence

| Failure Condition | Evidence Produced | Behavior |
|-------------------|-------------------|----------|
| Missing required input | `DryRunFailure`, error_type=`MissingInputError`, missing fields listed | Stop. No builder invoked. |
| Invalid input type | `DryRunFailure`, error_type=`TypeError`, field and expected/actual types recorded | Stop. No builder invoked. |
| Builder exception | `DryRunFailure`, error_type=`BuilderError`, exception class and message recorded | Stop. No artifact produced. |
| Builder returns non-dict | `DryRunFailure`, error_type=`InvalidReturnType`, actual return type recorded | Stop. No artifact. |
| Schema validation failure | `DryRunFailure`, error_type=`SchemaValidationError`, findings list with field-level issues | Stop. Invalid artifact captured in evidence only (not written). |
| Semantic comparison failure | `DryRunFailure`, error_type=`ComparisonFailure`, mismatch category and field-level details | Stop. Both artifacts captured in evidence. |
| Unsafe scope detected | `DryRunFailure`, error_type=`UnsafeScopeError`, offending fields/values listed | Stop immediately. |
| Forbidden persistence attempt | `DryRunFailure`, error_type=`PersistenceViolationError`, attempted path recorded | Stop immediately. |
| Unknown builder name | `DryRunFailure`, error_type=`BuilderNotFoundError`, requested builder name recorded | Stop. |
| Comparison target fails schema validation independently | `DryRunFailure`, error_type=`ComparisonTargetInvalidError`, target findings recorded | Stop. No comparison performed. |

### 9.2 Failure Response Shape (Conceptual)

```
DryRunFailure (conceptual):
  success: false
  error_type: str                    # one of the categories above
  builder_name: str
  input_summary: Dict
  validation_outcome: Optional[str]  # "fail" if schema validation was reached
  findings: List[Dict]
  comparison_outcome: Optional[str]  # if comparison was attempted
  unsafe_fields: Optional[List[str]]
  attempted_path: Optional[str]      # if persistence was attempted
  timestamp: str
```

### 9.3 Failure Governance

- No failure is silent. Every failure returns structured evidence.
- No partial artifact is treated as valid.
- No state update proposal is produced for a failed dry-run.
- Failures are evidence for the reviewer/orchestrator to act on, not automatic blockers for the overall milestone.

## 10. Review Gates for M8

Before M8 (minimal runtime implementation) can begin, M7 must prove the following design properties:

| Gate | Description |
|------|-------------|
| Dry-run evidence model is clear | All evidence fields (Section 5) are well-defined, non-ambiguous, and implementable. |
| Comparison model is reviewable | The semantic comparison framework (Section 7) defines mismatch categories that a human reviewer can understand and act on. |
| Non-persistence boundaries are explicit | Every rule in Section 6 is unambiguous: what cannot be written, under what conditions. |
| Runtime remains non-autonomous | Nowhere in this document does the dry-run acquire decision-making authority. |
| No mode activation is implied | No section suggests that dry-run enables candidate, primary, or autonomous operation. |
| No registry, CLI, or adapter is required for M8 | M8 can implement the dry-run contract without creating a builder registry, CLI, or adapter layer. |
| Owner must explicitly authorize code-producing M8 | M7 approval does not automatically authorize M8 implementation. A separate, explicit owner authorization is required before any file outside `docs/governance/` is created or modified for M8. |

### 10.1 M8 Gate Checklist

- [x] Dry-run evidence model defined (Section 5)
- [x] Comparison model defined (Section 7)
- [x] Non-persistence rules explicit (Section 6)
- [x] Failure model defined (Section 9)
- [x] Pipeline scenario illustrative only (Section 8)
- [x] No runtime implementation in M7
- [x] No forbidden files touched
- [x] Owner authorization for M8 is a separate gate

## 11. Non-Goals

The following are **explicitly excluded** from M7 scope and must not be produced, designed, or claimed during M7:

- **No runtime implementation.** No Python modules, no invocation code, no artifact store code.
- **No builder registry.** No dynamic discovery, no plugin loading, no classpath scanning.
- **No CLI.** No argparse, no click, no shell wrappers.
- **No adapters.** No FBA adapter, no Odoo adapter, no project-specific translation layer.
- **No git execution.** No `git add`, `git commit`, `git push`, `git status` automation.
- **No agent invocation.** No LLM agent invocation, no reasoning delegation.
- **No candidate mode.** Candidate mode remains inactive and is not designed here.
- **No primary mode.** Primary mode remains inactive and is not activated, designed, or authorized.
- **No `controlled_inspect`.** Remains unimplemented and is not a prerequisite.
- **No `controlled_commit`.** Remains unimplemented and is not a prerequisite.
- **No FBA/Odoo semantics.** No project-specific coupling in the dry-run design.
- **No production readiness claims.** M7 does not assert any operational readiness.
- **No autonomous milestone execution in M7.** The dry-run is caller-driven only.
- **No persistent dry-run artifact store.** No `.adf/dry-runs/` directory, no dry-run log files.

## 12. Approval Criteria

This document is approved when:

1. **Internal consistency.** All 13 sections agree on dry-run's role, boundaries, and constraints. No internal contradictions.
2. **No forbidden files touched.** Only `docs/governance/agnostic-dry-run-design-and-evidence.md` exists as a new file. No builders, schemas, agents, tests, source code, or configuration files are modified.
3. **No implementation.** The document is a design/governance artifact. It contains no code, no module paths, no import statements, no implementation instructions.
4. **Runtime boundary preserved.** The dry-run is consistently described as caller-driven, non-persistent, evidence-producing — never as autonomous, decision-making, or production.
5. **Dry-run evidence is sufficient for M8 planning.** A future M8 implementer can read this document and understand what evidence a dry-run must produce, what it must not persist, and how comparison works.
6. **Comparison method is semantic and review-oriented.** The comparison framework (Section 7) defines mismatch categories that support human review, not automated substitution.
7. **No candidate, primary, or readiness claims.** The document does not claim the framework is ready for any operational mode.
8. **Git status only shows the new M7 document.** No other files are staged or modified.

## 13. Stop Conditions

Stop this phase immediately and do not commit if:

- Any forbidden file must be touched to complete the design.
- Implementation seems necessary to define the design (e.g., a runtime function signature is needed).
- Runtime files (Python modules, `.adf/` directories, configuration files) are needed.
- Schema changes are needed to support the dry-run evidence model.
- Builder inspection or modification is needed (e.g., reading builder source to document behavior).
- FBA source inspection seems necessary to define comparison semantics.
- Candidate or primary activation is implied by any section.
- The document proposes persistent dry-run artifact storage beyond in-memory evidence.
- The document assigns decision-making authority to the dry-run or runtime.

---

*M7.1 — Design only. No implementation. No code. No runtime. No persistence. No mode activation.*
