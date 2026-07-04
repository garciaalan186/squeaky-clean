# Architecture-Aware Recovery Refactoring + Architectural MCDA

Design note for roadmap Milestones **L** and **M**. Both stem from one
observation surfaced while benchmarking Agentic Architecture Recovery on a
real Django CMS (Wagtail): recovering messy code *toward* Clean Architecture
is a **refactoring**, not a **relabeling**.

## Motivating problem

The recovery pipeline classified ~1,970 Wagtail classes as `ValueObject` and
only 2 as `Entity`, despite ~290 Django `models.Model` subclasses. The naive
fix — teach the fingerprinter that `models.Model` means Entity — is wrong on
two counts:

1. **It doesn't scale.** Django, SQLAlchemy, Pydantic, Peewee, then JPA,
   GORM, ActiveRecord… a framework registry per language, maintained forever.
2. **It's not even correct per Clean Architecture.** Robert C. Martin: *the
   database is a detail*; an ORM maps rows to **data structures**, not objects;
   a class welded to `models.Model` is coupled to the outermost ring and
   therefore **cannot** be a domain Entity. It's an Active-Record data
   structure at the boundary. The clean form is a **1→N split**: a pure Entity
   (business rules, no framework), a Repository/Gateway **port**, and an
   outer-ring **Adapter** that maps rows ↔ Entity.

So the class *is* the smell. The fix is generic and principled, not a lookup
table.

## Milestone L — framework-coupling detector → RefactorProposal

**Signal (framework-agnostic).** A class the layer-assigner placed in the
DOMAIN layer that inherits a **foreign base** — one that resolves to neither
(a) a sibling class in the recovered catalog nor (b) the language's *standard
library* allowlist (`object`, `ABC`, `Enum`, `Exception`, `Protocol`,
`NamedTuple`, …). The allowlist enumerates the **standard library** (small,
stable, per-language), never frameworks (unbounded). Inheriting a foreign base
in the domain layer is itself the Dependency-Rule violation Clean Architecture
cares about — no framework needs to be named to see it.

**Output.** Instead of a single `PatternName`, the class yields a
`RefactorProposal { fqn, foreign_base, entity, repository, adapter, reason }`
recommending the 1→N split. Proposals are rendered as a human-readable sidecar
(`<squib>.refactors.md`) at the review gate; the human decides whether to
apply them. (Auto-expanding the decomposer from 1→N specs is a later step; v1
advises, the human acts.)

## Milestone M — architectural trade-off MCDA

*Preserve the Active-Record class* vs *split into Entity+Repository+Adapter* is
a genuine trade-off with no universal answer: a prototype optimizes delivery
speed and low migration risk; a system being hardened optimizes testability and
evolvability. The decision should be driven by **stated priorities**, not a
hardcoded preference.

**Criteria (generic, benefit-framed, higher = better):** testability,
simplicity, performance, evolvability, migration-safety, delivery-speed.

**Weights.** The user provides an *ordering* (most→least important). Rank →
weights via **rank-order centroid** (ROC): `w_i = (1/n)·Σ_{k=i..n} 1/k`,
normalized to sum 1 — more separation than rank-sum, a standard MCDA method.

**Scoring.** Each option carries per-criterion scores (1–5). Weighted sum
ranks them (reusing the existing `MCDAScorer` philosophy). Two guardrails:

1. **Hard invariants are gates, not criteria.** The Dependency Rule, SOLID,
   and acyclicity are non-negotiable: an option that violates one is marked
   *infeasible* and excluded **before** scoring. A weighted score can never buy
   back a violation (avoids the compensatory-aggregation failure of weighted
   sums).
2. **Sensitivity is surfaced.** When the top two options are within a small
   margin, the outcome is flagged *close* and shown at the human review gate
   rather than silently committed.

**Wiring.** The criteria ranking is captured once at onboarding (or per
squib-generation run) and threaded through both the greenfield decomposition
and the recovery refactor decisions. For each `RefactorProposal`, a
`RefactorDecider` scores *preserve* vs *split* under the user's weighting and
recommends the winner (flagging close calls).

## Why this answers the scaling objection

Nothing here indexes a framework. Milestone L allowlists the *standard
library*; Milestone M encodes *generic architectural trade-off profiles*. The
long tail of framework-specific judgement lives where it belongs — in the LLM
tie-break (which already knows every framework from training, cached and
bounded) and ultimately the human review gate.
