# Contributing to Squeaky Clean

Thanks for considering a contribution. Squeaky Clean is open-source under Apache 2.0 and welcomes outside PRs.

## Ground rules

- **The framework eats its own dog food.** Every Hard Rule it enforces on generated code (one class per file, ≤3 public methods, ≤80 lines, layered import discipline, no `Any` types in mypy --strict) applies to its own source.
- **Determinism over cleverness.** New code paths add to either pure-function math (preferred) or LLM calls (cost-bearing). LLM calls require explicit per-tier accounting + the prompt-cache layer.
- **Tests are non-negotiable.** Every new use case + DTO + adapter ships with unit tests. CI runs mypy --strict + ruff + the full test suite + secret scan.

## Getting set up

```bash
# Clone
git clone https://github.com/your-org/squeaky-clean.git
cd squeaky-clean

# Install + dev deps
pip install -e ".[dev]"

# Run the test suite
pytest tests/ -q

# Type-check
mypy --strict src tests

# Linter
ruff check src tests
```

## What good PRs look like

| | |
|---|---|
| **Scope** | One thing per PR. A new Tier C ICP is one PR; tightening a validator is another. |
| **Tests** | New tests covering the change. Existing tests still pass. |
| **mypy + ruff** | Clean. No `# type: ignore` without explanation. |
| **Documentation** | Update docs/ if user-facing behavior changes. Update CHANGELOG.md. |
| **Spec changes** | If you modify an ICP spec, link to a per-agent eval fixture (under `eval/per_agent/fixtures/`) demonstrating the change improves something measurable. |

## High-leverage contribution areas

- **Tier C TechSpec snapshots.** The bundled catalog covers the top 2-3 technologies per category. Adding more (e.g. Cassandra under document_db, Pulsar under message_queue) is mostly mechanical.
- **Per-language code-emit tightening.** When tests_pass for a given language is below 0.50, look at `eval/per_agent/REPORT.md` + the failing pytest output. Tightening the language's ICP spec is often a one-line change.
- **MCDA scoring entries.** `eval/mcda_scores/<category>.json` files have ~3 candidates each. PRs welcome to add Cloud Run / Cloud Functions / Vercel / etc. with realistic 1-5 scores per criterion.
- **Convention registry.** `src/application/use_cases/convention_to_invariant.py` has ~9 entries. Common social/e-commerce/auth/IoT/healthcare conventions are good additions.

## What we won't merge

- **Hardcoded local paths.** Use `Path(__file__).resolve().parents[N]` or `Path.cwd()` defaults.
- **Heuristics that re-introduce domain inference.** "If the ProblemSpec mentions Twitter, assume timeline includes self" is exactly what we refuse to do.
- **Provider-specific changes that break the gateway port.** `LLMGateway` is multi-provider-ready by design.
- **Code that relies on the meta-evaluation harness output.** The framework runs against any directory; harness outputs are observational, not load-bearing.

## RFCs

Significant design changes (anything that touches §Notation grammar, the agent hierarchy, or the validators) start as RFCs in `docs/rfcs/`. Open an issue first and link to your RFC PR.

The 12 open design questions in `docs/infrastructure_layer_design.md` §10 are the seed material for early RFCs.

## Code of Conduct

See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Be civil; assume good intent.

## License

By contributing, you agree your contribution is licensed under Apache 2.0 (matching the project). No CLA required.

## Questions?

- Open a Discussion on GitHub.
- Tag maintainers in PRs.
