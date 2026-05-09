"""D2 ablation: compare hand-written EntityICP vs minimal-ablation prompt.

Runs both prompts against 3 frozen ClassSpec fixtures (live API, Haiku),
scores the emitted code with ICPScorer, reports mean structural-pass and
sigma. The hand-written prompt should beat the ablation by >=2sigma to
satisfy the Roadmap's D2 gate.
"""

from __future__ import annotations

import statistics
from pathlib import Path

from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec
from squeaky_clean.eval.agent_scorers.prompt_optimizer import (
    OptimizationFixture,
    PromptOptimizer,
    make_fixture,
)
from squeaky_clean.infrastructure.config.env_loader import EnvLoader
from squeaky_clean.infrastructure.llm.anthropic_sdk_gateway import AnthropicSDKGateway

_HAIKU = "claude-haiku-4-5-20251001"

_ABLATION_PROMPT = (
    "Emit one Python class. Use @dataclass. Implement methods. "
    "No prose. One ```python fenced block."
)


def _fixtures() -> list[OptimizationFixture]:
    return [
        make_fixture(
            name="todo_entity",
            user_prompt=(
                "CLASS Todo\nFIELDS [id: str, title: str, is_pending: bool]\n"
                "METHODS [mark_complete(): None]\n"
                "INVARIANTS []\n"
                "SIBLING_INTERFACES []\n"
            ),
            expected_class="Todo",
        ),
        make_fixture(
            name="user_entity",
            user_prompt=(
                "CLASS User\nFIELDS [id: str, name: str, email: str]\n"
                "METHODS [change_email(new: str): None]\n"
                "INVARIANTS [\"email must be non-empty\"]\n"
                "SIBLING_INTERFACES []\n"
            ),
            expected_class="User",
        ),
        make_fixture(
            name="account_entity",
            user_prompt=(
                "CLASS Account\nFIELDS [id: str, balance: float]\n"
                "METHODS [deposit(amount: float): None, withdraw(amount: float): None]\n"
                "INVARIANTS [\"balance must be >= 0\"]\n"
                "SIBLING_INTERFACES []\n"
            ),
            expected_class="Account",
        ),
    ]


def main() -> None:
    for candidate in (Path.cwd() / ".env",
                      Path(__file__).resolve().parents[2] / ".env"):
        if candidate.is_file():
            EnvLoader(candidate).load()
            break
    gw = AnthropicSDKGateway()
    opt = PromptOptimizer(gw, _HAIKU)
    fxs = _fixtures()
    handwritten = LoadAgentSpec().load("python/ddd_clean/EntityICP")
    a = opt.evaluate("handwritten", handwritten, fxs)
    b = opt.evaluate("ablation", _ABLATION_PROMPT, fxs)
    print(f"handwritten mean={a.mean_score:.2f} passed={a.fixtures_passed}/{a.fixtures_total}")
    print(f"ablation    mean={b.mean_score:.2f} passed={b.fixtures_passed}/{b.fixtures_total}")
    delta = a.mean_score - b.mean_score
    n = max(a.fixtures_total, 1)
    sigma_a = statistics.stdev([1.0] * a.fixtures_passed + [0.0] * (n - a.fixtures_passed)) if n > 1 else 0.0
    print(f"delta={delta:+.2f}  sample_sigma_handwritten={sigma_a:.2f}")
    if sigma_a > 0:
        print(f"sigma_units={delta / sigma_a:+.2f}")


if __name__ == "__main__":
    main()
