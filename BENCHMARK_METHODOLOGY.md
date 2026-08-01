# Benchmark Methodology — Complexity-Normalized Agent Performance

Status: methodology proposal. Last updated 2026-07-30.

## 1. Problem statement

Comparing agent runs across heterogeneous problems (P0 Calculator vs Twitter clone vs Kafka event producer) on token usage, cost, wall-clock, or velocity in **absolute terms is misleading** — a 100-line Calculator and a 100-line Kafka adapter are nominally equal but the latter requires far more architectural decisions. We want a denominator that captures **architectural complexity** (decisions made), not **textual size** (chars produced).

This document defines an Architectural Complexity Score (**ACS**) and the normalization metrics that derive from it. Sections 2–6 define the trust rules that govern every number produced under it: how many samples a claim needs, what a run is judged against, which figures are calibrated, how emission is verified below the level of a full benchmark problem, and how a number is attributed to the part of the pipeline that earned it.

## 2. Replication and claims policy

One run is a sample, not a measurement. **Accepting a fix, declaring a regression, or updating a baseline requires N ≥ 3 replicates (`--replicates 3`).** Below that threshold a run is exploratory and may not be cited as evidence for any of those three claims.

The policy is enforced in the output rather than left to discipline. `replicate_summary.md` carries an explicit note whenever N is below 3, and a single-sample sweep labels itself exploratory in its own `SUMMARY.md`.

`--replicates N` (N > 1) together with one or more problem ids routes to the replicated path, running one full pipeline per seed with `seed = replicate index`. Every other flag — cost cap, security tests, cache configuration, fixer passes, infrastructure mode — is carried into each replicate unchanged; only the seed varies. Several problems can be replicated in a single invocation.

Each replicated run writes both artifacts into the **first replicate's run directory**, so the summary sits with the runs it summarizes:

| Artifact | Contents |
|---|---|
| `replicate_summary.json` | `problem_id`, `replicates`, `tests_pass_mean` / `tests_pass_stddev`, `functional_pass_mean` / `functional_pass_stddev`, `security_pass_mean` / `security_pass_stddev`, `cost_usd_mean` / `cost_usd_stddev`, `wall_clock_ms_mean` / `wall_clock_ms_stddev`, `cache_hit_ratio`, `reports` (the per-replicate report paths), and `failures` (one string per failed replicate) |
| `replicate_summary.md` | mean/σ table over `tests_pass`, functional, security, cost USD and wall-clock ms, plus the cache hit ratio — the below-threshold note when N < 3, and a line naming how many replicates failed and were excluded from the statistics |

A failing replicate does not abort the calibration. The failure is recorded as `"replicate <N>: <ErrorType>: <message>"` and excluded from the aggregated statistics, and the surviving replicates still produce a summary — so one flaky seed costs a sample rather than the whole run. Two infrastructure signals are the deliberate exceptions and still abort everything: `BudgetExceededError` (the cost cap) and `ReplayCacheMissError` (a replay-only cache miss). When no replicate produces a result there is nothing to aggregate, and the run raises `ReplicateCalibrationError` — a `RuntimeError` subclass naming the problem id and every failure.

### 2.1 Unmeasured is never zero

A metric that was not measured is never reported as `0.0`, because `0.0` is also a real, meaningful score:

- In `metrics.json` and the sweep JSON, `test_outcome.security_tests_pass` serializes as JSON `null` when `test_outcome.security_test_count == 0`; `test_outcome.tests_pass` and `test_outcome.functional_tests_pass` serialize as `null` when `test_outcome.test_status` is "not measured" with zero tests collected.
- In Markdown tables the security column renders `n/a` rather than `0.00`.
- A genuine 0% — tests ran and all of them failed — still reports `0.00`, so a reader can tell "insecure" from "security tests not enabled".
- Architecture violations render as `<n> ⚠` when non-zero.
- Summary tables carry a legend: pass rate / functional covers functional acceptance criteria only; security means the generated security tests, `n/a` = not measured, enabled with `--security-tests`.

### 2.2 Prompt cache key

The cache key is the sha256 of the model, the prompts and the replicate id. Temperature and seed are deliberately excluded: neither is sent to the API, so including them would only fragment the cache. Replicates are therefore cache-isolated from one another — replicate 2 never reads replicate 1's entries — while re-running the same replicate is memoized.

A failed call is never written to the cache. A response that timed out, and a response whose content is empty or whitespace-only, are both skipped on store — a cached failure would otherwise be replayed as an empty result on every later run of that prompt, including cached and `--replay-only` runs. Those calls are retried live instead.

`SQUEAKY_CACHE_DIR` overrides the cache directory. The default is unchanged: `meta-evaluation-results/cache/` next to the framework checkout.

### 2.3 Replay — reproducing a run for $0

`--replay-only` modifies a normal run (`--problem P0 --replay-only`) so that every LLM call is served from that cache. It is not a top-level command and it does not stub the pipeline: spec parsing, model routing, pattern emission, integration, the generated project's test suite and scoring all run for real, and the resulting score is produced the same way any other run's is. Only the model responses come off disk, so the run costs $0 and needs no API key.

A prompt that is not in the cache never falls through to the live API. The run fails with `ReplayCacheMissError`, whose message carries the model, the cache-key prefix and the head of the prompt — enough to identify which prompt drifted. Replay therefore reproduces a number only for the exact prompts it was recorded against: change an agent spec and the replay stops rather than silently measuring something else. Inside a sweep the miss aborts the whole sweep instead of being recorded as one problem's failure, because it is an infrastructure signal — prompt drift or a stale bundle — and not a benchmark result.

This is what makes a full end-to-end eval affordable as a per-push gate: CI replays P0 from a cache bundle committed at `tests/ci_replay_cache/`, with `SQUEAKY_CACHE_DIR` pointed at the bundle. Prompt drift surfaces as a cache miss; a harness regression — routing, emission, integration or scoring moving — surfaces as a changed score. Replayed figures are reproductions of recorded runs, not fresh samples, and do not count toward the N ≥ 3 replication threshold in §2.

### 2.4 Report schema

`eval_report.json` (per problem) and `metrics.json` (per sweep) carry `"schema_version": 2`. The metrics are grouped into seven nested objects rather than written as flat siblings:

| Group | Carries |
|---|---|
| `test_outcome` | `tests_pass`, `test_status`, `tests_collected`, `functional_test_count`, `functional_tests_pass`, `security_test_count`, `security_tests_pass` |
| `cost` | `estimated_cost_usd`, `total_tokens_input`, `total_tokens_output`, and the per-tier `architect_*` / `test_architect_*` / `icp_*` / `security_architect_*` token, cost and duration fields |
| `velocity` | `artifact_token_estimate`, `artifact_to_output_ratio`, `icp_artifact_to_output_ratio`, `output_token_velocity`, `artifact_token_velocity`, `architect_velocity`, `test_architect_velocity`, `icp_velocity`, `icp_throughput_velocity` |
| `structure` | `avg_file_line_count`, `max_file_line_count`, `max_methods_per_class`, `max_args_per_method`, `classes_per_module`, `orphan_files`, and every `acs_*` field |
| `reliability` | `agent_retries`, `agent_hangs`, `hallucinations`, `llm_timeouts`, `architect_retries`, `compile_errors`, `classes_fixed`, `fixer_input_tokens`, `fixer_output_tokens`, `fixer_cost_usd`, `fixer_duration_ms` |
| `notation` | `notation_novelty`, `spec_conformance_violations`, `test_obligation_gaps`, `cross_module_dependency_violations`, `http_convention_violations`, `dependency_injection_violations`, `test_criteria_filtered`, `composer_validation_failures`, `composer_manager_fallback_calls`, `infrastructure_choices_explicit`, `infrastructure_choices_derived`, `infrastructure_icp_count`, `mcda_runs`, `dependency_install_failed` |
| `security_scan` | `secret_leaks_detected`, `sast_high_findings`, `sast_medium_findings`, `sast_failed` |

`architecture_violations`, `total_wall_clock_ms`, `parallelism_limit`, `peak_parallelism`, `cache_by_tier`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `cache_hit_count`, `cache_miss_count`, `cache_savings_usd`, `replicate_id`, `runs` and `budget_exceeded` stay at the top level, unnested.

Historical runs remain comparable. Reports written under the earlier flat, unversioned schema are still read as they were, and the metrics-history aggregator and the `scripts/comparison/` and `scripts/comparison_v2/` benchmark scripts flatten nested payloads back to the historical leaf names — so a run recorded before the schema change and one recorded after yield identical keys, and a series plotted across them is continuous.

## 3. Golden baselines and the regression gate

Every sweep judges each problem's result against that problem's stored golden baseline and writes one verdict per problem into the sweep summary under `## Regression Gate (vs routing-stamped goldens)`. Each verdict is also emitted as a `regression_gate` log event.

| Verdict | Meaning | Gates? |
|---|---|:---:|
| `<pid>: no golden (uncalibrated)` | The problem has no baseline. | No |
| `<pid>: not comparable (routing changed since calibration)` | The current tier → model routing differs from the calibration routing. That is a model change, not a tool regression. | No |
| `<pid>: OK (tests <current> vs golden <mean>±<sigma>)` | Within tolerance of the baseline. | No |
| `<pid>: REGRESSION <metric> <current> vs <mean>±<sigma> (drop <n>σ)` | A drop of 2 sigma or more below the baseline mean. | Yes |

When any metric trips, `regressions.json` is written into the run directory.

A baseline attaches to a problem spec as the optional field `golden_metrics: GoldenMetrics | None`; `None` means uncalibrated, and an uncalibrated problem never gates. `GoldenMetrics` is a frozen value object:

| Field | Carries |
|---|---|
| `replicates` | N behind the baseline |
| `tests_pass_mean` / `tests_pass_stddev` | overall pass rate |
| `functional_pass_mean` / `functional_pass_stddev` | functional acceptance criteria |
| `security_pass_mean` / `security_pass_stddev` | generated security tests |
| `cost_usd_mean` / `cost_usd_stddev` | run cost |
| `model_routing` | tuple of `"<tier>=<model>"` entries for architect / manager / icp / fixer — what the calibration ran under |
| `calibrated_run` | the run directory name the calibration produced |

Wall-clock and cache fields are not calibrated and do not gate: both are dominated by machine and cache state rather than by the framework.

## 4. Published calibrated baselines

N = 3 replicates, seeds 0–2, dated 2026-07-30, calibrated under routing `architect=claude-sonnet-5`, `manager=claude-sonnet-5`, `fixer=claude-sonnet-5`, `icp=claude-haiku-4-5-20251001`.

| Problem | tests pass | functional | security | cost USD | calibration stamp |
|---|---:|---:|---:|---:|---|
| P0 Calculator | 1.00 ± 0.00 | 1.00 ± 0.00 | n/a | $0.0187 ± 0.0113 | `meta-evaluation_457_20260730-164556` |
| P1 Todo Manager | 1.00 ± 0.00 | 1.00 ± 0.00 | n/a | $0.1335 ± 0.0195 | `meta-evaluation_482_20260730-225636` |
| P2 E-Commerce Cart | 1.00 ± 0.00 | 1.00 ± 0.00 | n/a | $0.0482 ± 0.0436 | `meta-evaluation_454_20260730-163813` |
| P3 Chat Application | 0.73 ± 0.31 | 0.73 ± 0.31 | n/a | $0.0921 ± 0.0230 | `meta-evaluation_485_20260730-230028` |
| P4 Twitter Clone | 0.67 ± 0.21 | 0.67 ± 0.21 | n/a | $0.4449 ± 0.0440 | `meta-evaluation_488_20260730-230409` |
| P5 OAuth2 Server | 0.57 ± 0.38 | 0.57 ± 0.38 | n/a | $0.4087 ± 0.0595 | `meta-evaluation_491_20260730-231701` |
| P6 Stock Monitor | 0.83 ± 0.29 | 0.83 ± 0.29 | n/a | $0.0617 ± 0.0337 | `meta-evaluation_494_20260730-232833` |
| P7 Order Lifecycle | 0.33 ± 0.17 | 0.33 ± 0.17 | n/a | $0.1056 ± 0.0062 | `meta-evaluation_497_20260730-233117` |
| P8 Text Editor | 0.83 ± 0.29 | 0.83 ± 0.29 | n/a | $0.0715 ± 0.0165 | `meta-evaluation_500_20260730-233535` |
| P9 Drawing Canvas | 1.00 ± 0.00 | 1.00 ± 0.00 | n/a | $0.0360 ± 0.0050 | `meta-evaluation_503_20260730-233818` |
| P10 Report Builder | 0.33 ± 0.58 | 0.33 ± 0.58 | n/a | $0.0501 ± 0.0434 | `meta-evaluation_472_20260730-211547` |
| P11 Notification Middleware | 0.78 ± 0.38 | 0.78 ± 0.38 | n/a | $0.1326 ± 0.0934 | `meta-evaluation_477_20260730-220845` |

P0's three replicates ran under run 457; P2's under runs 454–456. Security is `n/a` across the table — security tests were not enabled for any of the calibration runs, so no baseline's security mean is a measured 0%.

Every canonical problem carries a baseline, so none of them reports `no golden (uncalibrated)`. That verdict still applies to any problem without one — a user-authored spec whose `golden_metrics` is left `None` — and such a problem never gates until it is calibrated at N ≥ 3 under a recorded routing.

The suite is published as measured, not as a scoreboard. P0, P1, P2 and P9 are clean at 1.00 ± 0.00. P7 at 0.33 ± 0.17 is the weakest recorded baseline in the suite. P10's is unstable: its three seeds scored 1.00 / 0.00 / 0.00 — the creational family flakes end to end rather than failing consistently — which is what puts the mean at 0.33 and the σ at 0.58, wide enough that little will gate against it. P5 at 0.57 ± 0.38, P3 at 0.73 ± 0.31 and P11 at 0.78 ± 0.38 are wide spreads rather than clean passes. All of them are recorded anyway: an improvement has to beat the measured distribution, not a lucky N = 1.

P11's recalibration ran 3 of 3 replicates with zero architect failures, after the architect's emission budget was raised — the Sonnet architect's adaptive thinking shares the output-token budget with the Squib text, and on a multi-pattern brief like P11 the thinking alone consumed the gateway's 4096-token default, so the Squib text truncated mid-structure (unbalanced braces) or never started. A probe measured 4466 tokens needed to reach a clean `end_turn`; `DesignArchitecture` now requests 16384 on the architect call, and because the knob is capacity rather than spend, the headroom bills nothing unless it is used.

Because the baselines are routing-stamped, bumping a tier's model does not silently turn into a regression report: the gate returns `not comparable` until the problem is recalibrated under the new routing.

## 5. Micro-evals — the middle measurement tier

`--micro-evals` runs a pattern × language micro-eval matrix. It sits between unit tests, which stop at the LLM seam, and full benchmark problems: a handful of LLM calls plus one compiler invocation verifies that a pattern's emitters produce **compiling** code in a language.

For every squib fixture in `eval/squib_fixtures/` (`*.squib`), the command emits that fixture module's classes through the real model routing and the real pattern emitters, then compiles the result — once per target language (Python, Java, TypeScript). All sibling classes of the fixture module are emitted together, so cross-class contracts (`implements` / `extends`) are exercised, not just single-file syntax.

The corpus is the golden-Squib routing fixtures listed in `manifest.json` plus the hand-authored `*_depends_shape.squib` peer-shape fixtures, one per polymorphic pattern family. The matrix globs the whole directory, so it runs over a wider set than the routing test covers.

Each fixture is self-contained: every type its focal class references — parameter, return and field types, and the entries of `concretes:` — is declared as a sibling and emitted with it, so a cell's compile never depends on a type the module never declared. The siblings declare real capabilities rather than placeholder stubs: a payment port declares `charge(amount: Money): Result` with its adapter as a concrete, a `Money` sibling declares `zero()` / `add(other)` / `isNegative()`, view models declare their fields and invariants, and a Composite's component declares the real `size()` / `add(child)` signatures — so a cell exercises genuine cross-class contracts.

Each cell is isolated. A failure or an exception in one cell fails only that cell, and a language with no compiler or implementer registered fails the cell loudly rather than being silently skipped.

`--micro-patterns <prefix>[,<prefix>...]` narrows the corpus to the fixtures whose filename stem starts with one of the comma-separated prefixes. It modifies `--micro-evals` rather than being a command of its own, and its default — empty — runs every fixture. The match is on the stem, so `--micro-patterns state` takes `state.squib` and `state_depends_shape.squib` together, and `squeaky --micro-evals --micro-patterns strategy,visitor` measures those pattern families without paying for the whole fixture × language matrix.

### 5.1 Compile gates

| Language | Gate |
|---|---|
| Python | No ahead-of-time compile step exists, so the gate parses every `.py` file. This still catches truncated emissions, stray prose and malformed definitions. |
| Java | The JDK's `javac` directly against every `.java` file in the cell — no Maven and no `pom.xml`, an order of magnitude faster than `mvn`. 60-second timeout; class output under `_out/`. |
| TypeScript | The TypeScript compiler, with `tsconfig.json` (ES2022, nodenext modules, strict, noEmit, esModuleInterop, skipLibCheck, `include: ["src/**/*.ts"]`) and `package.json` (`{"type": "module"}`) scaffolded into each cell, mirroring what the integration bootstrap generates for full runs. |

Java micro-eval cells promote the ICP tier to the manager model, because the small model misses Java contracts often enough to matter — mirroring the per-problem recipe.

### 5.2 Output

Cells are written under `<run-dir>/micro-evals/<pattern>-<language>/`, and `micro_eval_report.md` plus `micro_eval_report.json` are written to the run directory.

The Markdown report is a pattern × language pass matrix — `✅` / `❌` with the compile-error count, and `—` where a cell has no adapter — with header counts of cells / passed / failed / total cost, and a Failures section listing `pattern/language`, the error count and a compiler-output excerpt.

The command prints its one-line result and exits:

```
[squeaky] micro-evals: <passed>/<total> cells passed, $<cost> — <report path>
```

`--micro-evals` is one of the accepted top-level commands: the CLI requires exactly one of `--problem`, `--problems`, `--sweep`, `--problem-file`, `--recover-from`, `--triage`, `--refactor`, `--squib-file`, `--rebuild-dashboard`, `--micro-evals`, or `--resume`.

## 6. Ablation controls — isolating the pattern vocabulary

A benchmark number says how well the pipeline did; on its own it does not say which part of the pipeline earned it. `--architect-mode {patterned,free}` isolates one part: the GoF/DDD pattern vocabulary itself.

| Mode | RequirementCompiler behavior |
|---|---|
| `patterned` (default) | Every class is annotated with the GoF/DDD pattern it plays, and routes to that pattern's dedicated emitter. |
| `free` | Every class is annotated `SimpleClass`, and routes to the escape-hatch emitter. |

Everything else is held fixed. The module decomposition, the layer assignment, the class granularity and the invariants come out exactly as they do under `patterned`; only the pattern annotation is replaced. The two arms therefore differ in one variable, which is what makes the difference between them attributable to that variable.

Run the same problem in both modes at N ≥ 3 (§2) and compare `tests_pass`, functional pass rate, architecture violations and cost. The delta is the measured contribution of the pattern vocabulary. `free` is a control arm, not a degraded mode meant for production runs — it exists so that the value of the vocabulary is a measurement rather than an assumption.

## 7. Recent benchmark numbers (event-pipeline)

Single samples (N = 1) — exploratory under §2. They orient; they do not establish.

| Run | tests_pass | Cost | In tokens | Out tokens | Wall ms | Artifact tok/s |
|---|---:|---:|---:|---:|---:|---:|
| Producer Python | 0.39 | $0.32 | 78,185 | 21,134 | 14,903 | 855 |
| Persister Python | 0.27 | $0.40 | 98,695 | 26,517 | 14,011 | 1,162 |
| Producer Java | 0.00 | $0.28 | 56,670 | 18,421 | 38,038 | 313 |
| Persister Java | 0.00 | $0.41 | 84,678 | 27,567 | 30,067 | 570 |

**Cross-run consistency**: ~$0.35/run, 80–100k input tokens, 20–27k output tokens. Java wall-clock is ~2× Python because Java emitters are wordier (more boilerplate per class). **Artifact-token velocity** (output tokens per wall-second) is the closest existing throughput metric — already exposed as `EvalMetrics.velocity.artifact_token_velocity`.

These numbers are not directly comparable: Java is doing more *work* per token than Python because Java needs more verbosity to express the same architectural decision. Without a complexity denominator, comparisons mislead.

## 8. Why simpler alternatives fail

- **Class count alone**: misses that a Repository with 1 method is harder than an Entity with 3 fields.
- **LoC alone**: incentivizes verbosity; rewards Java over Python for the same architecture.
- **Token count alone**: includes prompt tokens which are framework-determined, not problem-determined.
- **McCabe alone**: captures control flow but misses architectural breadth (modules, contracts).
- **Halstead alone**: captures vocabulary/operators but misses topology (cross-module deps).

The composite below captures architectural breadth, codegen complexity, and constraint complexity independently — so a problem can score high on one dimension without inflating the others.

## 9. Architectural Complexity Score (ACS) — composite metric

Three independent dimensions, weighted, normalized to 1.0 at P0 Calculator.

### 9.1 Dimension S — Structural complexity (~50% weight)

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

### 9.2 Dimension G — Codegen complexity (~30% weight)

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

McCabe + Halstead are well-validated information-theoretic metrics for source complexity. They normalize across languages because `ast` modules exist for Python and `tree-sitter` works for Java/JS/TS.

The `E` term (external SDK surface) is what specifically captures the "Kafka adapter is harder than Calculator" intuition: Calculator imports zero SDK symbols; the Kafka producer imports `Producer`, `KafkaException`, `KafkaError`, `Message`, `KafkaTemplate`, etc. Each external symbol is a real architectural decision the model had to ground.

**Cross-language normalization**: McCabe and Halstead values are absolute and language-agnostic (a `for` loop adds 1 to McCabe regardless of whether it's Python, Java, or TypeScript). The `β₂` weight on AST node count is small (0.001) because Java tends to produce 2–3× more nodes than Python for equivalent logic — heavy weighting would unfairly penalize verbose languages.

### 9.3 Dimension P — Constraint complexity (~20% weight)

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

### 9.4 Composite

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

## 10. Estimated baseline ACS values

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

The pattern-focused problems are deliberately small — 1–3 modules, 4–20 classes, 5–8 acceptance criteria each — and exist to test whether the architect *selects* the right pattern, not to stress architectural breadth. P6 `stock_monitor` (Observer), P7 `order_lifecycle` (State), P8 `text_editor` (Command + Memento) and P9 `drawing_canvas` (Composite + Visitor) cover the behavioral family; P10 `report_builder` (Builder + AbstractFactory + Prototype) covers the creational family and P11 `notification_middleware` (ChainOfResponsibility + Decorator + Adapter + Facade) the structural family. None of them has ACS figures yet; they enter the table after the calibration pass in §13.

## 11. Normalization metrics

Once ACS is computed, derived metrics give fair cross-problem comparisons:

| Metric | Formula | What it measures |
|---|---|---|
| **ACS-cost** | `estimated_cost_usd / ACS` | $ per unit of architectural complexity |
| **ACS-velocity** | `ACS / (total_wall_clock_ms / 1000)` | architectural-complexity-units produced per wall-second |
| **ACS-tests-pass** | `tests_pass / ACS` | normalized pass rate (penalizes "easy benchmarks pass") |
| **ACS-tokens** | `(cost.total_tokens_input + cost.total_tokens_output) / ACS` | tokens per complexity unit |

### 11.1 Worked example

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

**Interpretation**: the framework is ~40% cheaper *per unit of complexity* on hard problems than on easy ones — consistent with cache reuse across more emitters amortizing fixed overhead. ACS-velocity is ~4× higher on hard problems for the same reason. Without ACS normalization, raw `cost_usd` makes Calculator look "cheaper" when it's actually less efficient per architectural decision.

Both inputs are single samples, so the ratio is directional: promoting it to a claim requires the N ≥ 3 replication of §2.

## 12. Implementation

Add `squeaky_clean/application/evaluation/eval/metrics/architectural_complexity_scorer.py` (~80 lines). Pure function:

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

`ComplexityScore` DTO at `squeaky_clean/application/evaluation/eval/metrics/complexity_score.py`:

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

### 12.1 Component computation

- **S**: walk `arch.modules` and `arch.graph.edges`. Pure function; no codegen needed.
- **G**: requires the integrated source directory. Per-language AST visitor:
  - Python: `ast.parse` + walk for control-flow nodes (`If`, `For`, `While`, `BoolOp`, `Try`, `With`, etc.) for McCabe.
  - Java/JS/TS: stdlib regex-based McCabe approximation OR `tree-sitter` (a small additional dep — defer that decision).
  - `H` is McCabe sum, `N` is total AST node count, `V` is `len(set(all_identifiers))`, `E` is `len(set(non_stdlib_imports))`.
  - Skip if `source_dir is None` (lets ACS run pre-codegen).
- **P**: walk `problem` directly.

### 12.2 EvalMetrics extension

The ACS fields live on the `structure` group of `EvalMetrics` — `StructureStats` at `squeaky_clean/application/evaluation/eval/metrics/model/structure_stats.py`, reached as `metrics.structure.acs_composite` and serialized under `structure` in `eval_report.json`:

```python
acs_structural: float = 0.0
acs_codegen: float = 0.0
acs_constraint: float = 0.0
acs_composite: float = 0.0
acs_normalized: float = 1.0
acs_cost_per_unit: float = 0.0     # $/ACS
acs_velocity: float = 0.0          # ACS/sec
```

### 12.3 SUMMARY.md integration

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

### 12.4 Dashboard integration

The existing `HtmlDashboardWriter` (G4) plots metrics per run over time. Add `structure.acs_normalized`, `structure.acs_cost_per_unit`, `structure.acs_velocity` to the plotted series — gives drift detection on the framework's per-complexity efficiency, not just absolute spend.

## 13. Calibration procedure

1. Implement the scorer.
2. Run the canonical ProblemSpecs (P0–P11) once each on Python with `--deterministic`. Compute raw ACS for each.
3. Compute `ACS_baseline = ACS(P0 Calculator)`. The normalization is applied uniformly.
4. Inspect: do the relative numbers match intuition? P3 Chat should be ~10–15× P0; Twitter should be ~12–18× P0; Calculator/2 (a hypothetical P-0.5) would be < 1.0.
5. If a problem's ACS feels off, adjust α / β / γ weights and re-baseline.
6. Once weights are stable, freeze them in code with a `# Calibrated 2026-04-XX` comment. Re-baseline only when adding a new problem class that the existing dimensions don't cover (e.g. a new "stream-processing complexity" dimension if Apache Flink-style topologies become common).

ACS calibration is deterministic and pre-codegen, so a single `--deterministic` pass per problem suffices. It is distinct from the golden-baseline calibration of §3–§4, which measures stochastic run outcomes and therefore requires N ≥ 3.

## 14. Why this beats simpler alternatives — restated

| Alternative | Failure mode |
|---|---|
| Class count | Misses method density per class; Repository(1) ≠ Entity(3) |
| LoC | Verbosity bias — Java looks "harder" than Python for same architecture |
| Token count | Prompt tokens are framework-determined, not problem-determined |
| McCabe alone | Misses architectural breadth (modules, contracts) |
| Halstead alone | Misses topology (cross-module deps, exports) |
| External-SDK-count alone | Misses constraint complexity (acceptance criteria, contracts) |

The composite combines all three independently. A problem can score high on Constraint (many acceptance criteria) without inflating Structural (still one module). Calculator with 100 invented acceptance criteria would score high on P but low on S — appropriately distinguished from Twitter clone with 13 criteria across 9 modules.

## 15. Limitations and open questions

- **Q**: Are the default weights right? **A**: Defaults are an educated guess; calibration §13 tunes them. Treat the framework's behavior over the next 50 runs as evidence; revise once.
- **Q**: Does `E` (external SDK surface) double-count what `IC` (infrastructure_choices) already captures? **A**: Partially. `IC` counts categories chosen; `E` counts distinct *symbols* imported. A category like Kafka may import 5 symbols (Producer, Consumer, KafkaException, ...) — `E` captures this granularity. Slight redundancy is acceptable for cross-language stability.
- **Q**: How does ACS handle multi-language distributed systems (event-pipeline = producer-Java + persister-Python)? **A**: Each service computes its own ACS. The system-level score is the sum (or geometric mean for "balanced complexity" semantics). Decide once SystemSpec (Milestone I) lands.
- **Q**: Does the per-language tree-sitter dep pull a heavy native dependency into the framework? **A**: Yes — defer the tree-sitter decision. v1 of the scorer can compute G only for Python (using stdlib `ast`) and skip G for other languages (return 0). This makes ACS slightly under-scored for non-Python runs but is good enough to start.
- **Q**: How does ACS compare across model tiers (Architect vs ICP)? **A**: ACS is per-run. Per-tier `cost_usd` is already broken out on `EvalMetrics.cost`. Future extension: `ACS-cost-per-tier` to see whether the architect spends disproportionately on harder problems vs ICPs.
- **Q**: Should ACS-normalized metrics gate? **A**: Not yet. The regression gate (§3) runs on the calibrated raw metrics — `tests_pass`, functional, security, cost — because those have routing-stamped baselines at N ≥ 3. ACS-normalized series are plotted for drift, not gated, until they carry baselines of their own.

## 16. Roadmap placement

This is small enough to land as a Milestone K10 line item or roll into the open-source launch metrics dashboard work. ~80 lines + AST visitor per language = ~300 lines total + tests. Could ship before launch as a credibility-builder ("we publish complexity-normalized cost numbers").

## 17. References

- Cyclomatic complexity (McCabe 1976): https://www.literateprogramming.com/mccabe.pdf
- Halstead software metrics (Halstead 1977): standard textbook coverage; see *Software Engineering Metrics and Models* (Conte, Dunsmore, Shen).
- Tree-sitter for cross-language AST: https://tree-sitter.github.io/
