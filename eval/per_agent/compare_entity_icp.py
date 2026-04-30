"""Compare hand-written EntityICP vs optimized DSPy module (milestone D1).

For each held-out fixture, invokes (a) the hand-written EntityICP.md spec
through AnthropicSDKGateway and (b) the saved optimized DSPy module.
Scores both with `score_entity_output` and prints a comparison table.
"""

# mypy: ignore-errors
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

from squeaky_clean.infrastructure.config.env_loader import EnvLoader

ROOT = Path(__file__).resolve().parents[2]
EnvLoader(ROOT.parent / ".env").load()


from eval.per_agent.entity_icp_metric import (  # noqa: E402
    EntitySpec,
    score_entity_output,
)
from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec  # noqa: E402
from squeaky_clean.domain.interfaces.llm_request import LLMRequest  # noqa: E402
from squeaky_clean.infrastructure.dspy.entity_icp_dspy import (  # noqa: E402
    EntityICPModule,
    configure_lm,
)
from squeaky_clean.infrastructure.llm.anthropic_sdk_gateway import (  # noqa: E402
    AnthropicSDKGateway,
)

FIX_DIR = ROOT / "eval" / "per_agent" / "fixtures" / "entity_icp"
OPT_PATH = ROOT / "eval" / "per_agent" / "optimized" / "entity_icp_v1.json"
REPORT_PATH = ROOT / "eval" / "per_agent" / "REPORT.md"
HAIKU = "claude-haiku-4-5-20251001"


def _serialize(j: dict) -> str:
    return (
        f"CLASS {j['name']}\nPATTERN Entity\n"
        f"FIELDS [{', '.join(j['fields'])}]\n"
        f"METHODS [{', '.join(j['methods'])}]\n"
        f"DEPENDS [{', '.join(j['depends'])}]\n"
        f"CONCRETES [{', '.join(j['concretes'])}]\n"
        f"INVARIANTS [{', '.join(repr(s) for s in j['invariants'])}]\n"
        f"FILE_PATH {j['target_file']}\n"
        f"{j['sibling_interfaces']}"
    )


def _handwritten(gw: AnthropicSDKGateway, sys_prompt: str, j: dict) -> tuple[str, float]:
    req = LLMRequest(
        model=HAIKU,
        system_prompt=sys_prompt,
        user_prompt=_serialize(j),
        temperature=0.0,
    )
    resp = gw.complete(req)
    return resp.content, resp.cost_usd


def _dspy_call(module: EntityICPModule, j: dict) -> str:
    pred = module(
        class_spec=_serialize({**j, "sibling_interfaces": ""}),
        sibling_interfaces=j["sibling_interfaces"],
        target_file=j["target_file"],
    )
    return getattr(pred, "code", "") or ""


def main() -> int:
    configure_lm()
    gw = AnthropicSDKGateway()
    sys_prompt = LoadAgentSpec().load("python/ddd_clean/EntityICP")

    module = EntityICPModule()
    if OPT_PATH.exists():
        try:
            module.load(str(OPT_PATH))
            print(f"loaded optimized module from {OPT_PATH}")
        except Exception as exc:  # noqa: BLE001
            print(f"could not load {OPT_PATH}: {exc}; using uncompiled module")
    else:
        print(f"WARNING: {OPT_PATH} missing — comparing baseline DSPy")

    _HOLDOUT_STEMS = frozenset({
        "01_money_amount",
        "03_account_balance",
        "04_order_lifecycle",
        "08_invoice_total",
    })
    holdout = sorted(p for p in FIX_DIR.glob("*.json") if p.stem in _HOLDOUT_STEMS)
    print(f"comparing {len(holdout)} held-out fixtures: {[p.stem for p in holdout]}\n")

    rows: list[tuple[str, float, float, float]] = []
    hand_scores: list[float] = []
    dspy_scores: list[float] = []
    cost = 0.0
    t0 = time.monotonic()

    for path in holdout:
        j = json.loads(path.read_text())
        spec = EntitySpec(name=j["name"], fields=j["fields"], methods=j["methods"])
        hw_text, hw_cost = _handwritten(gw, sys_prompt, j)
        cost += hw_cost
        hw_score = score_entity_output(spec, hw_text, j["sibling_interfaces"])["total"]
        ds_text = _dspy_call(module, j)
        ds_score = score_entity_output(spec, ds_text, j["sibling_interfaces"])["total"]
        rows.append((j["name"], float(hw_score), float(ds_score),
                     float(ds_score) - float(hw_score)))
        hand_scores.append(float(hw_score))
        dspy_scores.append(float(ds_score))

    print(f"{'fixture':<22} {'hand':>6} {'dspy':>6} {'delta':>6}")
    print("-" * 44)
    for name, h, d, dlt in rows:
        print(f"{name:<22} {h:>6.3f} {d:>6.3f} {dlt:>+6.3f}")
    hm = statistics.mean(hand_scores)
    hs = statistics.stdev(hand_scores) if len(hand_scores) > 1 else 0.0
    dm = statistics.mean(dspy_scores)
    ds_ = statistics.stdev(dspy_scores) if len(dspy_scores) > 1 else 0.0
    print(f"\nhand-written: {hm:.3f} ± {hs:.3f}")
    print(f"dspy:         {dm:.3f} ± {ds_:.3f}")
    pooled = ((hs ** 2 + ds_ ** 2) / 2) ** 0.5 if (hs or ds_) else 0.0
    sigma_units = ((dm - hm) / pooled) if pooled > 0 else 0.0
    decision = (
        "PASS" if sigma_units >= 2.0
        else "FAIL" if sigma_units <= -2.0
        else "INCONCLUSIVE"
    )
    print(f"sigma_units (DSPy - hand) = {sigma_units:+.2f}  decision={decision}")
    elapsed = time.monotonic() - t0
    print(f"hand-written API spend on this comparison: ${cost:.4f}  elapsed={elapsed:.1f}s")

    REPORT_PATH.write_text(
        "# EntityICP D1 Comparison\n\n"
        f"- Held-out fixtures: {len(holdout)}\n"
        f"- Hand-written: {hm:.3f} ± {hs:.3f}\n"
        f"- DSPy (optimized): {dm:.3f} ± {ds_:.3f}\n"
        f"- sigma_units (DSPy − hand): {sigma_units:+.2f}\n"
        f"- Decision: {decision}\n"
        f"- Comparison API spend: ${cost:.4f}\n\n"
        "| fixture | hand | dspy | delta |\n|---|---|---|---|\n"
        + "\n".join(f"| {n} | {h:.3f} | {d:.3f} | {dl:+.3f} |"
                    for n, h, d, dl in rows)
        + "\n",
    )
    print(f"wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
