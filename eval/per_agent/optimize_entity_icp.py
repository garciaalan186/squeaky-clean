"""Compile EntityICPModule with MIPROv2 / BootstrapFewShot (milestone D1)."""

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

import dspy  # noqa: E402

from eval.per_agent.entity_icp_metric import (  # noqa: E402
    EntitySpec,
    score_entity_output,
)
from squeaky_clean.infrastructure.dspy.entity_icp_dspy import (  # noqa: E402
    EntityICPModule,
    configure_lm,
)

FIX_DIR = ROOT / "eval" / "per_agent" / "fixtures" / "entity_icp"
OUT_DIR = ROOT / "eval" / "per_agent" / "optimized"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _serialize_spec(j: dict[str, object]) -> str:
    return (
        f"CLASS {j['name']}\nPATTERN Entity\n"
        f"FIELDS [{', '.join(j['fields'])}]\n"
        f"METHODS [{', '.join(j['methods'])}]\n"
        f"DEPENDS [{', '.join(j['depends'])}]\n"
        f"CONCRETES [{', '.join(j['concretes'])}]\n"
        f"INVARIANTS [{', '.join(repr(s) for s in j['invariants'])}]\n"
        f"FILE_PATH {j['target_file']}"
    )


def _load_examples() -> list[tuple[dict, dspy.Example]]:
    examples: list[tuple[dict, dspy.Example]] = []
    for path in sorted(FIX_DIR.glob("*.json")):
        j = json.loads(path.read_text())
        ex = dspy.Example(
            class_spec=_serialize_spec(j),
            sibling_interfaces=j["sibling_interfaces"],
            target_file=j["target_file"],
            _meta=j,
        ).with_inputs("class_spec", "sibling_interfaces", "target_file")
        examples.append((j, ex))
    return examples


def metric_fn(example, pred, trace=None) -> float:  # noqa: ANN001
    meta = example._meta
    spec = EntitySpec(
        name=meta["name"], fields=meta["fields"], methods=meta["methods"],
    )
    code = getattr(pred, "code", "") or ""
    return float(score_entity_output(spec, code, meta["sibling_interfaces"])["total"])


def _eval_module(module: EntityICPModule, examples) -> list[float]:
    scores: list[float] = []
    for _, ex in examples:
        try:
            pred = module(
                class_spec=ex.class_spec,
                sibling_interfaces=ex.sibling_interfaces,
                target_file=ex.target_file,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  [{ex._meta['name']}] EXC: {exc}", flush=True)
            scores.append(0.0)
            continue
        s = metric_fn(ex, pred)
        scores.append(s)
        print(f"  [{ex._meta['name']}] score={s:.3f}", flush=True)
    return scores


def main() -> int:
    configure_lm()
    all_ex = _load_examples()
    # _load_examples returns list[tuple[dict, Example]] keyed by spec dict;
    # match holdout by the spec name encoded into the fixture filename.
    name_to_holdout = {
        "Money": True,         # 01: construction invariant
        "Account": True,       # 03: methods (mutating)
        "Order": True,         # 04: lifecycle invariant + 3 methods
        "Invoice": True,       # 08: methods + default field values
    }
    train = [ex for j, ex in all_ex if j["name"] not in name_to_holdout]
    test = [ex for j, ex in all_ex if j["name"] in name_to_holdout]
    test_full = [(j, ex) for j, ex in all_ex if j["name"] in name_to_holdout]
    print(f"loaded {len(all_ex)} fixtures: {len(train)} train / {len(test)} holdout")
    print(f"  holdout: {[j['name'] for j, _ in test_full]}")
    t0 = time.monotonic()

    # Baseline
    print("\n== BASELINE (uncompiled) ==", flush=True)
    base = EntityICPModule()
    base_scores = _eval_module(base, test_full)

    # Compile
    method = "BootstrapFewShot"
    print(f"\n== COMPILING with {method} ==", flush=True)
    try:
        from dspy.teleprompt import BootstrapFewShot
        teleprompter = BootstrapFewShot(
            metric=metric_fn, max_bootstrapped_demos=2,
            max_labeled_demos=0, max_rounds=1,
        )
        compiled = teleprompter.compile(EntityICPModule(), trainset=train)
    except Exception as exc:  # noqa: BLE001
        print(f"compile failed: {exc}", flush=True)
        return 2

    # Save
    save_path = OUT_DIR / "entity_icp_v1.json"
    try:
        compiled.save(str(save_path))
    except Exception as exc:  # noqa: BLE001
        print(f"save failed (continuing): {exc}", flush=True)

    print("\n== OPTIMIZED on held-out ==", flush=True)
    opt_scores = _eval_module(compiled, test_full)

    elapsed = time.monotonic() - t0
    bm = statistics.mean(base_scores) if base_scores else 0.0
    bs = statistics.stdev(base_scores) if len(base_scores) > 1 else 0.0
    om = statistics.mean(opt_scores) if opt_scores else 0.0
    os_ = statistics.stdev(opt_scores) if len(opt_scores) > 1 else 0.0
    print(f"\nbaseline:  mean={bm:.3f} ± {bs:.3f}  (n={len(base_scores)})")
    print(f"optimized: mean={om:.3f} ± {os_:.3f}  (n={len(opt_scores)})")
    print(f"method: {method}  elapsed: {elapsed:.1f}s")

    summary = {
        "method": method, "elapsed_s": elapsed,
        "baseline_scores": base_scores, "optimized_scores": opt_scores,
        "baseline_mean": bm, "baseline_stdev": bs,
        "optimized_mean": om, "optimized_stdev": os_,
        "save_path": str(save_path),
    }
    (OUT_DIR / "entity_icp_v1_summary.json").write_text(
        json.dumps(summary, indent=2),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
