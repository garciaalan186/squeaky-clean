# Agentic Architecture Recovery

Squeaky Clean generates Clean-Architecture projects from a `ProblemSpec`.
**Architecture Recovery is the inverse path**: point the framework at an
existing brownfield project, and it ingests the code, recovers a faithful
`Squib`, analyzes it for Clean-Architecture violations, lets you triage which
to fix, applies the fixes, and re-enters the standard generation pipeline.

Messy legacy code in → a freshly generated Clean-Architecture project out, with
human checkpoints in the middle.

## The pipeline

Five separated, independently re-runnable phases. Each persists an artifact, so
you can stop, edit, and resume — nothing is a black box.

| Phase | CLI | Input → Artifact | LLM? |
|---|---|---|---|
| **Recover** | `--recover-from` | project → `recovered.squib` + `violations.json` | no |
| **Analyze** | (part of `--recover-from`) | artifact → categorized `violations.json` | no |
| **Triage** | `--triage` | `violations.json` → `refactor_plan.json` | no |
| **Refactor** | `--refactor` | Squib + plan → `refactored.squib` | no (v1) |
| **Regenerate** | `--squib-file` | signed-off Squib → code | yes |

**Recovery is faithful.** The recovered Squib is a true photograph of the
original — coupling, cycles, and god-classes included. All opinion about what is
*wrong* lives in the separate Analyze phase, and all *fixing* lives in the
opt-in Refactor phase. This keeps the recovered artifact verifiable against the
source and re-analyzable later with better rules.

## Worked example

```bash
# 1. RECOVER + ANALYZE — ingest a project, emit a reviewable Squib + violations
squeaky --recover-from ./legacy-app --language python \
        --recover-out out/recovered.squib \
        --criteria testability,evolvability,simplicity,performance,migration_safety,delivery_speed
# → out/recovered.squib
# → out/recovered.squib.violations.json   (categorized findings)
# → out/recovered.squib.violations.md     (human-readable review)

# 2. TRIAGE — opt-out review; every category is addressed by default
squeaky --triage out/recovered.squib.violations.json
# prompts per category: "address all N framework-coupling violation(s)? [Y/n]"
# → out/refactor_plan.json

# 3. REFACTOR — apply the accepted transforms
squeaky --refactor out/recovered.squib --plan out/refactor_plan.json \
        --refactor-out out/refactored.squib
# → out/refactored.squib   (coupled classes split into Entity + Repository + Adapter)

# 4. REGENERATE — feed the signed-off Squib back into generation
squeaky --squib-file out/refactored.squib --legacy-tests ./legacy-app/tests
```

You can also edit `recovered.squib` by hand at step 1 and skip straight to
`--squib-file` — the review gate reports any parse error with line context and
waits for a corrected version.

## Supported languages

`--language {python,javascript,typescript,java}`. Everything after ingest is
language-neutral (layers, patterns, decomposition, analysis, refactoring all
operate on the language-agnostic `ClassCatalog`/`ArchitectureSpec`), so only the
*extractor* is language-specific.

| Language | Backend | Fidelity |
|---|---|---|
| Python | real `ast` walk | high — bases, methods, fields, imports, decorators |
| Java | regex (package-keyed FQNs) | medium — imports resolve to real edges via `package` |
| JavaScript / TypeScript | regex (path-keyed FQNs) | medium — relative imports rarely resolve, so a sparser graph |

Go and Rust are not yet supported for recovery and raise a clear error. The
regex extractors are approximate by design (method-arg rendering is rough,
multiple-classes-per-file uses proximity slicing); they produce a solid
*reviewable* artifact, not a perfect parse. A tree-sitter/AST backend per
language is the planned fidelity upgrade.

Ingest excludes test and vendored code across languages (`test_*.py`,
`*.test.ts`, `*.spec.ts`, `*Test.java`, `tests/`, `node_modules/`, `.venv/`,
`target/`, `__tests__/`, …) so the recovered architecture reflects production
code only.

## Analyze — violation categories

Each category points one of the framework's own generated-code rules *inward* at
the recovered artifact. Findings are structured
`{ category, target, detail, suggestion }` with a stable `category:target` id.

- **framework-coupling** — a domain class inheriting a *foreign* base (an ORM
  model, Active Record). Detected generically: a base that resolves to neither a
  sibling class nor the language *standard library* (bounded allowlist), so no
  per-framework knowledge is needed. Per Clean Architecture, this class is a
  Dependency-Rule violation, not an Entity.
- **dependency-rule** — a class importing a sibling in a strictly *outer* layer.
- **cyclic-dependency** — module-level dependency cycles.
- **granularity** — a class exceeding the ≤5-public-method bound.
- **decorative-class** — a class with no methods and no invariants.

## Architectural MCDA — preserve vs split

Whether a framework-coupled class should be **preserved** (kept as an
Active-Record boundary object) or **split** (into a pure Entity + Repository port
+ Adapter) is a genuine trade-off with no universal answer. You supply an
importance ranking of shared criteria via `--criteria` (most-important first):

`testability, simplicity, performance, evolvability, migration_safety, delivery_speed`

Rank → weights via **rank-order centroid**. Options are scored by weighted sum,
with **hard invariants (Dependency Rule, SOLID, acyclicity) as non-negotiable
gates** — never bought back by a high weighted score — and near-ties flagged for
human review. Purity-first priorities recommend *split*; speed/risk-first
priorities recommend *preserve*.

## Refactor — what the transform does

For each framework-coupling violation you kept, the class is split 1→N:

```
Page (extends models.Model)   ──►   Page          -> Entity      (Domain)
                                     PageRepository-> Repository  (Domain port)
                                     PageAdapter   -> Adapter     (PageInfra, Infrastructure)
```

The Entity keeps the original members, the Repository port carries conventional
`save`/`find_by_id`, and the Adapter (in a companion `<Module>Infra`
Infrastructure module) implements the port — exports and cross-module
dependencies wired so the result validates and can regenerate.

**This is a skeleton, not a finished refactor.** The Entity keeps *all* original
members; which are business rules vs persistence concerns is not yet resolved —
that member classification is the planned agentic follow-up (the first LLM step
in this pipeline). Only the framework-coupling category has a transform today;
cycles/granularity/decorative are detected and triageable but not yet
auto-transformed.

## Is the CLI interactive?

Mostly no — it's a flag-driven batch CLI. The one interactive step is `--triage`,
which prompts a `[Y/n]` per violation *category* (default yes; closed stdin ⇒
yes). Everything else is determined by flags upfront, and every phase is
persistable and re-runnable from its artifact.

## Design background

- [`recovery_refactoring_pipeline.md`](recovery_refactoring_pipeline.md) — the
  Recover → Analyze → Triage → Refactor design, faithful-recovery principle, and
  the sharding approach for large projects.
- [`architecture_recovery_refactoring_and_mcda.md`](architecture_recovery_refactoring_and_mcda.md)
  — why the coupling detector is generic (no framework registry) and how the
  architectural MCDA works, grounded in Clean Architecture's "the database is a
  detail."

## See also

- [`architecture.md`](architecture.md) — the forward generation pipeline
- [`squib.md`](squib.md) — the grammar the recovered artifact is written in
- [`roadmap.md`](roadmap.md) — Milestones L / M / N
