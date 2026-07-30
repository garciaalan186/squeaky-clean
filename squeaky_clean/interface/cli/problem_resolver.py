"""ProblemResolver: look up a ProblemSpec by its id string."""

from eval.problems.p0_calculator import P0
from eval.problems.p0_calculator_go import P0GO
from eval.problems.p0_calculator_java import P0JAVA
from eval.problems.p0_calculator_js import P0JS
from eval.problems.p0_calculator_rust import P0RUST
from eval.problems.p0_calculator_ts import P0TS
from eval.problems.p1_todo_manager import P1
from eval.problems.p1_todo_manager_java import P1JAVA
from eval.problems.p1_todo_manager_js import P1JS
from eval.problems.p1_todo_manager_ts import P1TS
from eval.problems.p2_ecommerce_cart import P2
from eval.problems.p2_ecommerce_cart_java import P2JAVA
from eval.problems.p2_ecommerce_cart_js import P2JS
from eval.problems.p2_ecommerce_cart_ts import P2TS
from eval.problems.p3_chat_app import P3
from eval.problems.p3_chat_app_java import P3JAVA
from eval.problems.p3_chat_app_js import P3JS
from eval.problems.p3_chat_app_ts import P3TS
from eval.problems.p4_twitter_clone import P4
from eval.problems.p5_oauth2_server import P5
from eval.problems.p6_stock_monitor import P6
from eval.problems.p7_order_lifecycle import P7
from eval.problems.p8_text_editor import P8
from eval.problems.p9_drawing_canvas import P9
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec

_REGISTRY: dict[str, ProblemSpec] = {
    "P0": P0, "P0JS": P0JS, "P0TS": P0TS, "P0JAVA": P0JAVA,
    "P0GO": P0GO, "P0RUST": P0RUST,
    "P1": P1, "P1JS": P1JS, "P1TS": P1TS, "P1JAVA": P1JAVA,
    "P2": P2, "P2JS": P2JS, "P2TS": P2TS, "P2JAVA": P2JAVA,
    "P3": P3, "P3JS": P3JS, "P3TS": P3TS, "P3JAVA": P3JAVA,
    "P4": P4, "P5": P5,
    # Pattern-rich problems — each demands a structurally distinct pattern the
    # P0–P5 suite never exercises (Observer, State, Command+Memento,
    # Composite+Visitor). These measure whether the architect *chooses* the
    # right pattern end-to-end, complementing the golden-Squib routing test.
    "P6": P6, "P7": P7, "P8": P8, "P9": P9,
}


class ProblemResolver:
    """Resolves a problem id string to the corresponding ProblemSpec."""

    def resolve(self, problem_id: str) -> ProblemSpec:
        """Return the ProblemSpec registered under ``problem_id``."""
        if problem_id not in _REGISTRY:
            raise KeyError(f"unknown problem id: {problem_id}")
        return _REGISTRY[problem_id]
