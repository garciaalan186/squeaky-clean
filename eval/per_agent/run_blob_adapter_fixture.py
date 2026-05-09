"""H2 driver: score one BlobStorageAdapterICP fixture via live Haiku call."""

# mypy: ignore-errors
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
from squeaky_clean.infrastructure.config.env_loader import EnvLoader  # noqa: E402

EnvLoader(ROOT.parent / ".env").load()

from eval.per_agent.blob_storage_adapter_icp_metric import (  # noqa: E402
    BlobAdapterSpec,
    score_blob_storage_output,
)
from squeaky_clean.application.use_cases.tech_spec_block_formatter import (  # noqa: E402
    TechSpecBlockFormatter,
)
from squeaky_clean.domain.interfaces.llm_request import LLMRequest  # noqa: E402
from squeaky_clean.infrastructure.llm.anthropic_sdk_gateway import (  # noqa: E402
    AnthropicSDKGateway,
)
from squeaky_clean.infrastructure.techspec.tech_spec_builder import TechSpecBuilder  # noqa: E402

FIX_DIR = ROOT / "eval" / "per_agent" / "fixtures" / "blob_storage_adapter_icp"
SPEC_DIR = ROOT / "eval" / "tech_specs"
ICP_DIR = ROOT / "src" / "interface" / "agent_specs" / "icps" / "python" / "infrastructure"
MODEL = "claude-haiku-4-5-20251001"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture")
    args = parser.parse_args()
    fix = json.loads((FIX_DIR / args.fixture).read_text())
    ts = json.loads((SPEC_DIR / fix["tech_spec_path"]).read_text())
    tech = TechSpecBuilder().build(ts)
    sys_p = (ICP_DIR / "BlobStorageAdapterICP.md").read_text()
    usr_p = _user_prompt(fix, tech)
    gw = AnthropicSDKGateway(MODEL)
    resp = gw.complete(LLMRequest(
        model=MODEL, system_prompt=sys_p, user_prompt=usr_p,
        temperature=0.0, tier="icp",
    ))
    spec = BlobAdapterSpec(
        name=fix["name"],
        methods=[m.split("(")[0] for m in fix["methods"]],
        port_dotted=fix["sibling_interfaces"].split("file=")[1].split(")")[0],
        port_class=fix["depends"][0],
        primary_imports=fix["expected_imports"],
        error_types=fix["expected_error_types"],
    )
    score = score_blob_storage_output(spec, resp.content)
    print(f"\n=== {args.fixture} ===")
    for k, v in score.items():
        print(f"  {k}: {v}")
    print(f"\ncost: ${resp.cost_usd:.4f}")
    print("\n--- generated code ---")
    print(resp.content)
    return 0 if score["total"] >= 0.80 else 1


def _user_prompt(fix: dict, tech) -> str:
    block = TechSpecBlockFormatter().format(tech)
    return (
        f"CLASS_NAME {fix['name']}\nPATTERN Adapter\n"
        f"IMPLEMENTS {fix['depends'][0]}\n"
        f"FIELDS []\nMETHODS [{', '.join(fix['methods'])}]\n"
        f"DEPENDS [{', '.join(fix['depends'])}]\n"
        f"FILE_PATH {fix['target_file']}\n"
        f"{fix['sibling_interfaces']}\n"
        f"{block}"
    )


if __name__ == "__main__":
    sys.exit(main())
