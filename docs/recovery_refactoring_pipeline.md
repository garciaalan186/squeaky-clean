# Recovery Refactoring Pipeline: Recover → Analyze → Triage → Refactor

> **Status: implemented.** This is the design record; for CLI usage see the
> user guide, [`architecture_recovery.md`](architecture_recovery.md).

Design note for roadmap **Milestone N**. Supersedes the "recovery emits the
fix" framing: recovery stays *faithful*, and cleanup is a separate, optional,
violation-driven downstream. Milestones L and M compose into this pipeline
rather than standing alone.

## Principle: recovery observes, it does not opine

The recovered artifact must be a **true photograph of the original** — coupling,
cycles, god-classes and all. A faithful artifact is verifiable against the
source, re-analyzable later with better rules, and honest about what exists.
Any opinion about what's *wrong* or how to *fix* it belongs to a later phase.

## The four phases and their artifacts

| Phase | Input → Artifact | LLM? |
|---|---|---|
| **Recover** | brownfield → `RecoveryArtifact` (catalog + layers + faithful Squib) | no |
| **Analyze** | `RecoveryArtifact` → `ViolationReport` (categorized, persisted `violations.json`) | no |
| **Triage** | `ViolationReport` → `RefactorPlan` (interactive; fix-by-default, uncheck to ignore) | no |
| **Refactor** | artifact + plan → `refactored.squib` (transforms applied only to accepted violations) | some |
| **Regenerate** | signed-off Squib → code | yes (existing `--squib-file`) |

Each phase persists its artifact and is independently re-runnable. Recovery is
faithful; refactoring is opt-in and traceable to a specific accepted violation.

## Analyze — violation categories

Every category points an existing generated-code rule *inward* at the recovered
architecture. Each finding is a structured `ArchitecturalViolation
{ category, target, detail, suggestion, violation_id }`:

- **framework-coupling** — domain class inherits a foreign base (Milestone L's
  `FrameworkCouplingDetector`).
- **dependency-rule** — a class imports a sibling in a strictly *outer* layer
  (Domain→App/Infra/Interface, App→Infra/Interface, Infra→Interface).
- **cyclic-dependency** — module-level cycles (`ArchitectureGraph`).
- **granularity** — a class exceeding the ≤5-public-method bound.
- **decorative-class** — a class with no methods and no invariants (rule 13).

Analyzers implement a common `ViolationAnalyzer` port so the set is extensible;
`ViolationAnalysis` runs them all and returns a `ViolationReport` grouped by
category. Fully deterministic — no LLM.

## Triage — opt-out interactive review

The reviewer sees violations grouped by category, **all checked by default**
(bias toward cleanliness), and unchecks the ones to leave alone. The result is
a persisted `RefactorPlan` — per-violation `fix | ignore` plus an optional
reason — an auditable architectural-debt decision record that can be diffed and
re-run. **Milestone M (MCDA)** governs *strategy* here: the user's criteria
ranking decides, e.g., framework-coupling → *preserve* vs *split*, and can order
which categories are worth addressing.

## Refactor — transforms scoped to accepted violations

Each accepted violation maps to a transform on the faithful artifact:
framework-coupling → the 1→N Entity + Repository + Adapter split; cyclic →
dependency-inversion break; granularity → class split. The semantically hard
judgement (which members are business vs persistence) lands here, on a small
reviewed set — and is where the agentic layer belongs (an LLM classifies
members; the human gate is the backstop). Output is `refactored.squib`, fed to
the existing regeneration path.

## Sharding for large projects

The parser assembles *before* it parses, so sharding needs no grammar change:

- **Squib** — a directory of `*.squib` (one per module / bounded context) + a
  manifest, concatenated then handed to the existing single-string parser; the
  emitter gains a sharded mode. On Wagtail the single Squib was 500 KB —
  unreviewable; sharded by module it is tractable and VCS-diffable.
- **ViolationReport / RecoveryArtifact** — shard by category or module so the
  triage step is navigable.

Sharding is **threshold-driven, not mandatory** (single file under ~40 modules;
shard above). The driver is human-review ergonomics and diff-ability, not
parser capability.
