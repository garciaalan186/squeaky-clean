# Benchmark Methodology — Complexity-Normalized Agent Performance

Status: methodology proposal. Last updated 2026-04-28.

## 1. Problem statement

Comparing agent runs across heterogeneous problems (P0 Calculator vs Twitter clone vs Kafka event producer) on token usage, cost, wall-clock, or velocity in **absolute terms is misleading** — a 100-line Calculator and a 100-line Kafka adapter are nominally equal but the latter requires far more architectural decisions. We want a denominator that captures **architectural complexity** (decisions made), not **textual size** (chars produced).

This document defines an Architectural Complexity Score (**ACS**) and the normalization metrics that derive from it.

## 2. Recent benchmark numbers (event-pipeline)

| Run | tests_pass | Cost | In tokens | Out tokens | Wall ms | Artifact tok/s |
|---|---:|---:|---:|---:|---:|---:|
| Producer Python | 0.39 | $0.32 | 78,185 | 21,134 | 14,903 | 855 |
| Persister Python | 0.27 | $0.40 | 98,695 | 26,517 | 14,011 | 1,162 |
| Producer Java | 0.00 | $0.28 | 56,670 | 18,421 | 38,038 | 313 |
| Persister Java | 0.00 | $0.41 | 84,678 | 27,567 | 30,067 | 570 |

**Cross-run consistency**: ~$0.35/run, 80–100k input tokens, 20–27k output tokens. Java wall-clock is ~2× Python because Java ICPs are wordier (more boilerplate per class). **Artifact-token velocity** (output tokens per wall-second) is the closest existing throughput metric — already exposed on `EvalMetrics`.

These numbers are not directly comparable: Java is doing more *work* per token than Python because Java needs more verbosity to express the same architectural decision. Without a complexity denominator, comparisons mislead.

## 3. Why simpler alternatives fail

- **Class count alone**: misses that a Repository with 1 method is harder than an Entity with 3 fields.
- **LoC alone**: incentivizes verbosity; rewards Java over Python for the same architecture.
- **Token count alone**: includes prompt tokens which are framework-determined, not problem-determined.
- **McCabe alone**: captures control flow but misses architectural breadth (modules, contracts).
- **Halstead alone**: captures vocabulary/operators but misses topology (cross-module deps).

The composite below captures architectural breadth, codegen complexity, and constraint complexity independently — so a problem can score high on one dimension without inflating the others.

## 4. Architectural Complexity Score (ACS) — composite metric

Three independent dimensions, weighted, normalized to 1.0 at P0 Calculator.

### 4.1 Dimension S — Structural complexity (~50% weight)

Pre-codegen, derived from `ArchitectureSpec`:

```
S = α₁·M + α₂·C + α₃·D + α₄·X + α₅·I

where
  M = module count
  C = class count
  D = dep edges in the architecture graph (intra-module + cross-module)
  X = cross-module exports (sum of EXPORTS list lengths)
  I = invariant count (across all modules + classes)

defaults:
  α = [1.0, 0.5, 0.3, 0.4, 0.2]
```

Captures architectural breadth: how many bounded contexts, how many classes per context, how tightly they couple.

**Rationale**: a single-module 5-class Calculator scores ~5; a 9-module 22-class Twitter scores ~25. The α weights treat modules and exports more heavily than classes alone because crossing a bounded-context boundary is the harder architectural decision.

### 4.2 Dimension G — Codegen complexity (~30% weight)

Post-codegen, derived from parsing each generated source file's AST:

```
G = β₁·H + β₂·N + β₃·V + β₄·E

where
  H = total cyclomatic complexity (sum of McCabe scores across all functions)
  N = total node count in all ASTs (a Halstead-like volume proxy)
  V = total vocabulary count (distinct identifiers — Halstead operand count)
  E = external SDK API surface used (count of distinct symbols imported from non-stdlib)

defaults:
  β = [0.4, 0.001, 0.05, 0.5]
```

McCabe + Halstead are well-validated information-theoretic metrics for source complexity. They normalize across languages because `ast` modules exist for Python and `tree-sitter` works for Java/Go/Rust/JS/TS.

The `E` term (external SDK surface) is what specifically captures the "Kafka adapter is harder than Calculator" intuition: Calculator imports zero SDK symbols; the Kafka producer imports `Producer`, `KafkaException`, `KafkaError`, `Message`, `KafkaTemplate`, etc. Each external symbol is a real architectural decision the model had to ground.

**Cross-language normalization**: McCabe and Halstead values are absolute and language-agnostic (a `for` loop adds 1 to McCabe regardless of whether it's Python, Java, or Rust). The `β₂` weight on AST node count is small (0.001) because Java tends to produce 2–3× more nodes than Python for equivalent logic — heavy weighting would unfairly penalize verbose languages.

### 4.3 Dimension P — Constraint complexity (~20% weight)

Pre-codegen, derived from `ProblemSpec`:

```
P = γ₁·A + γ₂·CC + γ₃·DC + γ₄·IC

where
  A  = acceptance criteria count
  CC = cross-service contracts (produces + consumes)
  DC = data classifications declared
  IC = infrastructure_choices count

defaults:
  γ = [1.0, 2.0, 1.0, 1.5]
```

Captures problem-level constraints the architect must satisfy. CC and IC carry higher weight because cross-service contracts and explicit infrastructure choices each impose hard constraints the architect cannot relax.

### 4.4 Composite

```
ACS = w_S · S + w_G · G + w_P · P

defaults:
  w_S = 0.5
  w_G = 0.3
  w_P = 0.2

normalize:
  ACS_normalized = ACS / ACS_baseline   where ACS_baseline = ACS(P0 Calculator)
```

P0 Calculator → 1.0 by construction. All other problems score relative to that baseline.

## 5. Estimated baseline ACS values

From existing data (rough — exact values populate after a one-pass calibration run on the canonical problem set):

| Problem | Modules | Classes | Acceptance criteria | External SDK symbols | ACS (rough) |
|---|---:|---:|---:|---:|---:|
| P0 Calculator | 1 | 5 | 4 | 0 | **1.0** (baseline) |
| P1 Todo Manager | 2 | 12 | 6 | ~3 | ~3.5 |
| P2 E-commerce Cart | 4 | 28 | 9 | ~5 | ~7.5 |
| P3 Chat App | 8 | 60 | 12 | ~8 | ~14 |
| P5 OAuth2 Server | 4 | 22 | 7 | ~6 | ~9 |
| Twitter clone | 9 | 22 | 13 | ~4 | ~16 |
| Event-pipeline producer | 4 | 8 | 5 | ~7 (Kafka + Express) | ~11 |
| Event-pipeline persister | 4 | 8 | 5 | ~7 (Kafka + blob) | ~11 |

## 6. Normalization metrics

Once ACS is computed, derived metrics give fair cross-problem comparisons:

| Metric | Formula | What it measures |
|---|---|---|
| **ACS-cost** | `estimated_cost_usd / ACS` | $ per unit of architectural complexity |
| **ACS-velocity** | `ACS / (total_wall_clock_ms / 1000)` | architectural-complexity-units produced per wall-second |
| **ACS-tests-pass** | `tests_pass / ACS` | normalized pass rate (penalizes "easy benchmarks pass") |
| **ACS-tokens** | `(total_tokens_input + total_tokens_output) / ACS` | tokens per complexity unit |

### 6.1 Worked example

Recent event-pipeline producer (Python): ACS ≈ 11.

```
ACS-cost     = $0.32 / 11 = $0.029 per ACS-unit
ACS-velocity = 11 / 14.9s = 0.74 ACS-units/wall-second
ACS-tokens   = 99,319 / 11 = 9,029 tokens/ACS-unit
```

Calculator P0: ACS = 1.0.

```
ACS-cost     = $0.05 / 1.0 = $0.05 per ACS-unit
ACS-velocity = 1.0 / 6s = 0.17 ACS-units/wall-second
ACS-tokens   = ~12k / 1.0 = 12,000 tokens/ACS-unit
```

**Interpretation**: the framework is ~40% cheaper *per unit of complexity* on hard problems than on easy ones — consistent with cache reuse across more ICPs amortizing fixed overhead. ACS-velocity is ~4× higher on hard problems for the same reason. Without ACS normalization, raw `cost_usd` makes Calculator look "cheaper" when it's actually less efficient per architectural decision.

## 7. Implementation

Add `src/application/use_cases/architectural_complexity_scorer.py` (~80 lines). Pure function:

```python
class ArchitecturalComplexityScorer:
    def score(
        self,
        problem: ProblemSpec,
        arch: ArchitectureSpec,
        source_dir: Path | None = None,
    ) -> ComplexityScore:
        """Return ACS components + composite."""
```

`ComplexityScore` DTO at `src/application/dtos/complexity_score.py`:

```python
@dataclass(frozen=True)
class ComplexityScore:
    structural: float           # S dimension
    codegen: float              # G dimension; 0.0 if source_dir is None
    constraint: float           # P dimension
    composite: float            # ACS
    normalized: float           # ACS / ACS_baseline
    components: dict[str, float] # M, C, D, X, I, H, N, V, E, A, CC, DC, IC
```

### 7.1 Component computation

- **S**: walk `arch.modules` and `arch.graph.edges`. Pure function; no codegen needed.
- **G**: requires the integrated source directory. Per-language AST visitor:
  - Python: `ast.parse` + walk for control-flow nodes (`If`, `For`, `While`, `BoolOp`, `Try`, `With`, etc.) for McCabe.
  - Java/Go/Rust/JS/TS: stdlib regex-based McCabe approximation OR `tree-sitter` (a small additional dep — defer that decision).
  - `H` is McCabe sum, `N` is total AST node count, `V` is `len(set(all_identifiers))`, `E` is `len(set(non_stdlib_imports))`.
  - Skip if `source_dir is None` (lets ACS run pre-codegen).
- **P**: walk `problem` directly.

### 7.2 EvalMetrics extension

Add four fields:

```python
acs_structural: float = 0.0
acs_codegen: float = 0.0
acs_constraint: float = 0.0
acs_composite: float = 0.0
acs_normalized: float = 1.0
acs_cost_per_unit: float = 0.0     # $/ACS
acs_velocity: float = 0.0          # ACS/sec
```

### 7.3 SUMMARY.md integration

`SummaryWriter` gains an "Architectural Complexity" section:

```markdown
## Architectural Complexity (ACS)

| Dimension | Value | Weight | Contribution |
|---|---:|---:|---:|
| Structural | 12.4 | 0.5 | 6.20 |
| Codegen    | 8.7  | 0.3 | 2.61 |
| Constraint | 7.5  | 0.2 | 1.50 |
| **Composite (ACS)** | | | **10.31** |
| **ACS-normalized (vs P0)** | | | **10.31** |

| Normalized metric | Value |
|---|---:|
| Cost per ACS-unit | $0.031 |
| Velocity (ACS/s)  | 0.69 |
| Tokens per ACS    | 9,640 |
```

### 7.4 Dashboard integration

The existing `HtmlDashboardWriter` (G4) plots metrics per run over time. Add `acs_normalized`, `acs_cost_per_unit`, `acs_velocity` to the plotted series — gives drift detection on the framework's per-complexity efficiency, not just absolute spend.

## 8. Calibration procedure

1. Implement the scorer.
2. Run all 6 canonical ProblemSpecs (P0–P5) once each on Python with `--deterministic`. Compute raw ACS for each.
3. Compute `ACS_baseline = ACS(P0 Calculator)`. The normalization is applied uniformly.
4. Inspect: do the relative numbers match intuition? P3 Chat should be ~10–15× P0; Twitter should be ~12–18× P0; Calculator/2 (a hypothetical P-0.5) would be < 1.0.
5. If a problem's ACS feels off, adjust α / β / γ weights and re-baseline.
6. Once weights are stable, freeze them in code with a `# Calibrated 2026-04-XX` comment. Re-baseline only when adding a new problem class that the existing dimensions don't cover (e.g. a new "stream-processing complexity" dimension if Apache Flink-style topologies become common).

## 9. Why this beats simpler alternatives — restated

| Alternative | Failure mode |
|---|---|
| Class count | Misses method density per class; Repository(1) ≠ Entity(3) |
| LoC | Verbosity bias — Java looks "harder" than Python for same architecture |
| Token count | Prompt tokens are framework-determined, not problem-determined |
| McCabe alone | Misses architectural breadth (modules, contracts) |
| Halstead alone | Misses topology (cross-module deps, exports) |
| External-SDK-count alone | Misses constraint complexity (acceptance criteria, contracts) |

The composite combines all three independently. A problem can score high on Constraint (many acceptance criteria) without inflating Structural (still one module). Calculator with 100 invented acceptance criteria would score high on P but low on S — appropriately distinguished from Twitter clone with 13 criteria across 9 modules.

## 10. Limitations and open questions

- **Q**: Are the default weights right? **A**: Defaults are an educated guess; calibration §8 tunes them. Treat the framework's behavior over the next 50 runs as evidence; revise once.
- **Q**: Does `E` (external SDK surface) double-count what `IC` (infrastructure_choices) already captures? **A**: Partially. `IC` counts categories chosen; `E` counts distinct *symbols* imported. A category like Kafka may import 5 symbols (Producer, Consumer, KafkaException, ...) — `E` captures this granularity. Slight redundancy is acceptable for cross-language stability.
- **Q**: How does ACS handle multi-language distributed systems (event-pipeline = producer-Java + persister-Python)? **A**: Each service computes its own ACS. The system-level score is the sum (or geometric mean for "balanced complexity" semantics). Decide once SystemSpec (Milestone I) lands.
- **Q**: Does the per-language tree-sitter dep pull a heavy native dependency into the framework? **A**: Yes — defer the tree-sitter decision. v1 of the scorer can compute G only for Python (using stdlib `ast`) and skip G for other languages (return 0). This makes ACS slightly under-scored for non-Python runs but is good enough to start.
- **Q**: How does ACS compare across model tiers (Architect vs ICP)? **A**: ACS is per-run. Per-tier `cost_usd` is already broken out on `EvalMetrics`. Future extension: `ACS-cost-per-tier` to see whether the architect spends disproportionately on harder problems vs ICPs.

## 11. Roadmap placement

This is small enough to land as a Milestone K10 line item or roll into the open-source launch metrics dashboard work. ~80 lines + AST visitor per language = ~300 lines total + tests. Could ship before launch as a credibility-builder ("we publish complexity-normalized cost numbers").

## 12. References

- Cyclomatic complexity (McCabe 1976): https://www.literateprogramming.com/mccabe.pdf
- Halstead software metrics (Halstead 1977): standard textbook coverage; see *Software Engineering Metrics and Models* (Conte, Dunsmore, Shen).
- Tree-sitter for cross-language AST: https://tree-sitter.github.io/
