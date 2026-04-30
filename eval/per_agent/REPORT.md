# EntityICP D1+D2 Comparison

## D1 (initial split, alphabetical 6/4 — fixtures 07-10 in holdout)

- Hand-written: 1.000 ± 0.000
- DSPy (optimized): 1.000 ± 0.000
- Decision: INCONCLUSIVE — holdout fixtures (Appointment, Invoice, PaymentMethod, Subscription) had no construction invariants, no methods, no lifecycle invariants. Both approaches saturated the metric on trivial entities.

## D2 (rotated split, discriminating fixtures in holdout)

- Held-out fixtures: 4 (Money, Account, Order, Invoice — each carries one of: construction invariant / mutating methods / lifecycle invariant + methods / methods + defaults)
- Hand-written: 1.000 ± 0.000
- DSPy (optimized): 1.000 ± 0.000
- sigma_units (DSPy − hand): +0.00
- Decision: INCONCLUSIVE
- Comparison API spend: $0.0109

| fixture | hand | dspy | delta |
|---|---|---|---|
| Money | 1.000 | 1.000 | +0.000 |
| Account | 1.000 | 1.000 | +0.000 |
| Order | 1.000 | 1.000 | +0.000 |
| Invoice | 1.000 | 1.000 | +0.000 |

## Verdict on D3 / DSPy scale-up: **STOP**

Both splits saturate the 7-component metric on Haiku 4.5. With the metric as defined, DSPy cannot demonstrate ≥2σ improvement because the hand-written spec already achieves the metric ceiling. Two options to recover signal — neither is a free lunch:

1. **Tighten the metric** — add components today's hand-written EntityICP can't trivially pass (specific docstring style, exception-message wording, internal structure beyond AST + mypy). Requires first committing to an opinionated style.
2. **Weaken the model** — re-run with Haiku 3.5 or a smaller non-Anthropic model. Surfaces differences but only because the baseline degrades, not because DSPy improves; arguably misleading.

Neither option moves the framework forward. **D3 (scale DSPy to all 34 patterns) does not pass the gate.** Maintain hand-written ICP specs as authoritative; keep DSPy modules as experimental scaffolding that can be revisited when the metric becomes more demanding (e.g. when D1 fixture set is extended into harder-to-saturate territory under future Milestone H per-agent eval work).

**Cost of this finding:** ~$0.02 across both phases. Cheap, honest, decisive.
