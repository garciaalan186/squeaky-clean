# Contributing to Squeaky Clean

Thanks for considering a contribution. Squeaky Clean is open-source under Apache 2.0 and welcomes outside PRs.

## Ground rules

- **The framework eats its own dog food.** Every Hard Rule it enforces on generated code (one class per file, ≤5 public methods, ≤80 lines, layered import discipline, no `Any` types in mypy --strict) applies to its own source. The self-conformance gate adds three framework-only rules on top. No f-string-driven reflection — `setattr` / `getattr` called with a dynamically built attribute name is banned everywhere in the framework, reported under the `ReflectionBan` key prefix. `FsPortBypass` bans a raw `Path.write_text` / `write_bytes` anywhere under `application/generation/**` or `application/evaluation/**`: generated-project artifacts go through the `ProjectFileSystem` port, framework-internal ones through `atomic_write_text`, so an interrupted run can never leave a half-written file behind. (`mkdir` / `exists` / `open` are deliberately out of scope — the rule is about writes.) `ImpureConstruction` bans constructing an I/O-touching class — `JSONLogger`, `LocalFileSystem`, `ClaudeCLIGateway`, `AnthropicSDKGateway`, `CachingLLMGateway`, `ContentAddressedCache`, `LoadAgentSpec` — anywhere under `application/**`: those arrive by injection from the composition root (`squeaky_clean/interface/cli/dependency_builder.py`). Both live in `tests/self_conformance/di_conformance_rules.py` and are wired into `conformance_scan.py`.
- **New modules go in a component, not a type bucket.** `squeaky_clean/application/` is three cohesive components: `generation/` (the product pipeline), `evaluation/` (the eval harness), and `shared/` (what both build on). The permitted edges are `generation → shared` and `evaluation → {generation, shared}`; `generation` never imports `evaluation`, because the product must not depend on its own harness. Data-carrying types live beside the code that uses them. `ComponentDependencyRule` and `PackageCohesionRule` — no package over 20 direct modules, no type-named catch-alls (`use_cases/`, `dtos/`, `helpers/`, `utils/`, `misc/`, `common/`) — enforce this in the self-conformance gate.
- **Impure collaborators are injected, never constructed.** Anything touching the filesystem, the network or the environment is built once in the composition root and passed inward. In practice that means `LoadAgentSpec` and `ProjectFileSystem` are required constructor arguments on the classes that need them rather than optional ones defaulting to `None`, and every shell-out sits behind a port implemented in `squeaky_clean/infrastructure/` — the application layer is subprocess-free. A new use case that wants to read a spec, write a file or run a command takes the collaborator as an argument and lets `dependency_builder.py` supply it.
- **Errors surface; they never degrade a run silently.** An `except` block either recovers, logs a structured run-log event carrying the reason, or raises — it never returns `None` and calls the problem handled. `tests/self_conformance/test_no_silent_swallow.py` enforces that mechanically, banning `return None`, a bare `return` and a bare `pass` inside an `except` across `squeaky_clean/infrastructure/techspec/`, `squeaky_clean/application/generation/techspec/` and `squeaky_clean/application/generation/integration/manifests/`. It is a plain unit test local to those directories rather than a conformance-scan rule. `None` stays a legal return value in those modules, but only on a path meaning "not applicable / clean miss".
- **Determinism over cleverness.** New code paths add to either pure-function math (preferred) or LLM calls (cost-bearing). LLM calls require explicit per-tier accounting + the prompt-cache layer.
- **Tests are non-negotiable.** Every new use case + DTO + adapter ships with unit tests. On every push to `main` and every pull request, CI runs ruff + mypy --strict + the drift guards and self-conformance ratchet + the full unit suite + the $0 eval replay gate; live LLM tests stay opt-in behind the `integration` marker.
- **Say what you measured.** A metric that wasn't measured is reported as `n/a` / `null`, never as `0.00`. Accepting a fix, declaring a regression or updating a golden baseline takes N ≥ 3 replicates (`--replicates 3`); a single run is exploratory and the report labels it as such. Tests that shell out to a real toolchain skip rather than fail when it is absent, so a green suite means what it says.

## Getting set up

Python 3.10+ is the baseline. A **JDK** is required for Java compilation and the micro-eval `javac` gate, and **Node.js** for the TypeScript/JavaScript toolchain; CI pins Temurin JDK 21 and Node.js 20 so those gates don't float with the runner image. The generated Java itself is JDK-neutral — plain `public final class` with explicit private final fields, a constructor and getters, never `record`, `sealed` or `var` — so it compiles on any JDK ≥ 11 even though the gate runs on 21. Tests that shell out to the real `node` binary skip rather than fail on a machine without it, so the suite stays honest about what it actually measured — but a PR touching a Java or TypeScript emitter should be validated on a machine that has both.

```bash
# Clone
git clone https://github.com/garciaalan186/squeaky-clean.git
cd squeaky-clean

# Install + dev deps
pip install -e ".[dev]"

# Run the test suite
pytest tests/ -q

# Type-check
mypy --strict squeaky_clean tests

# Linter
ruff check squeaky_clean tests

# Compile-verify the pattern emitters (pattern x language, real LLM calls)
squeaky --micro-evals

# Same, narrowed to the fixtures whose names start with these prefixes
squeaky --micro-evals --micro-patterns strategy,visitor

# Replay the CI eval gate locally ($0, no API key)
SQUEAKY_CACHE_DIR=tests/ci_replay_cache squeaky --problem P0 --replay-only
```

## The $0 replay gate

CI runs a full end-to-end eval on every push and pull request without spending a cent. It replays benchmark problem P0 against the small cache bundle committed at `tests/ci_replay_cache/`, with `SQUEAKY_CACHE_DIR` pointed at that bundle and the CLI invoked with `--problem P0 --replay-only`. Everything except the LLM calls runs for real — spec parsing, model routing, pattern emission, integration, the generated project's pytest suite, and scoring — so the gate catches what unit tests structurally cannot: it stops at the LLM seam, and this does not.

`--replay-only` serves every LLM call from the content-addressed response cache. A prompt that is not in the cache does not fall through to the API; the run fails with a `ReplayCacheMissError` carrying the model, the cache-key prefix and the head of the prompt, so the drifted prompt is identifiable from the failure alone. Run it locally with the command above before you push — it is the cheapest way to confirm your change did not move a prompt.

**Editing an agent spec or any prompt will turn this gate red until the committed bundle is refreshed.** That is the gate working: a changed spec produces a changed prompt, a changed prompt is a different cache key, and a different cache key is a miss. Two failure shapes, two meanings:

| Symptom | Means |
|---|---|
| `ReplayCacheMissError` | A prompt or agent spec drifted. Refresh `tests/ci_replay_cache/` in the same PR. |
| The gate runs but the score changes | A harness regression — routing, emission, integration, or scoring moved. Investigate before refreshing anything. |

A replay miss during a sweep aborts the whole sweep rather than being scored as one problem's failure: it is an infrastructure signal, not a benchmark result, and must never be reported as a green sweep.

## What good PRs look like

| | |
|---|---|
| **Scope** | One thing per PR. A new Tier C emitter is one PR; tightening a validator is another. |
| **Tests** | New tests covering the change. Existing tests still pass. |
| **mypy + ruff** | Clean. No `# type: ignore` without explanation. |
| **Documentation** | Update docs/ if user-facing behavior changes. Update CHANGELOG.md. |
| **Spec changes** | Changing an agent spec or a prompt changes its cache key, so the $0 replay gate goes red until you refresh `tests/ci_replay_cache/` in the same PR. If you modify an emitter spec, link to a per-agent eval fixture (under `eval/per_agent/fixtures/`) demonstrating the change improves something measurable, and quote the affected `--micro-evals` cells before and after — that is the cheapest evidence the emitter still produces compiling code, and `--micro-patterns <prefix>` restricts that run to the fixtures you touched instead of the full matrix. An emitter spec can be authored either as one complete file per language under `emitters/<language>/<category>/`, or once as a cross-language template under `emitters/_shared/<category>/` composed with the per-language profiles at `emitters/_shared/profiles/<language>.md`. All 23 creational, structural and behavioral patterns are authored as shared templates; the remaining 11 DDD/Clean patterns each have their four per-language files, 44 in all. For one of those shared-template patterns, a language-specific fix belongs in that language's profile block, while a change to the shared template lands in all four languages at once and has to be validated across them, and the drift guards — for example the Java §Notation `float` → `double` type-fidelity rule — are asserted once per pattern against the composed template + profile, parameterized over every shared-template pattern, rather than against four file copies. If you add or rename a pattern spec, add the matching golden-Squib routing fixture under `eval/squib_fixtures/` — edit the pattern table in `scripts/gen_squib_fixtures.py` and re-run it to regenerate the 28 routing fixtures plus `manifest.json` — so `tests/eval/test_golden_squib_routing.py` covers it in all four languages, resolving the routed spec the way production does (a shared template plus that language's profile, or a per-language spec file), and `--micro-evals` compile-checks it in Python, Java and TypeScript. The seven `*_depends_shape.squib` peer-shape fixtures in that directory are hand-maintained: the generator neither produces nor reproduces them, and `manifest.json` does not list them, so edit them directly. |

## High-leverage contribution areas

- **Tier C TechSpec snapshots.** The bundled catalog covers the top 2-3 technologies per category. Adding more (e.g. Cassandra under document_db, Pulsar under message_queue) is mostly mechanical.
- **Per-language code-emit tightening.** When tests_pass for a given language is below 0.50, look at `eval/per_agent/REPORT.md` + the failing pytest output. The Failures section of `micro_eval_report.md` is the faster loop for compile-level defects: it names the failing `pattern/language` cell, the error count and a compiler-output excerpt. Tightening the language's emitter spec — its profile block for a creational, structural or behavioral pattern, its per-language file for any of the 11 DDD/Clean patterns — is often a one-line change, and `--micro-patterns` re-runs just that pattern's cells.
- **MCDA scoring entries.** `eval/mcda_scores/<category>.json` files have ~3 candidates each. PRs welcome to add Cloud Run / Cloud Functions / Vercel / etc. with realistic 1-5 scores per criterion.
- **Convention registry.** `squeaky_clean/application/generation/notation/convention_to_invariant.py` has ~9 entries. Common social/e-commerce/auth/IoT/healthcare conventions are good additions.

## What we won't merge

- **Hardcoded local paths.** Use `Path(__file__).resolve().parents[N]` or `Path.cwd()` defaults.
- **Heuristics that re-introduce domain inference.** "If the ProblemSpec mentions Twitter, assume timeline includes self" is exactly what we refuse to do.
- **Provider-specific changes that break the gateway port.** `LLMGateway` is multi-provider-ready by design.
- **Code that relies on the meta-evaluation harness output.** The framework runs against any directory; harness outputs are observational, not load-bearing.

## RFCs

Significant design changes (anything that touches the Squib grammar, the agent hierarchy, or the validators) start with a GitHub issue describing the proposal. If maintainers agree it warrants a written design, the RFC lands as a markdown file under `docs/` (modeled on `docs/infrastructure_layer_design.md`).

The 12 open design questions in `docs/infrastructure_layer_design.md` §10 are the seed material for early RFCs.

## Code of Conduct

See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Be civil; assume good intent.

## License

By contributing, you agree your contribution is licensed under Apache 2.0 (matching the project). No CLA required.

## Questions?

- Open a Discussion on GitHub.
- Tag maintainers in PRs.
