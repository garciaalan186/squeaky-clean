"""Compare hand-written EntityICP vs optimized DSPy module (milestone D1).

RETIRED (R6.10 speculative-surface triage): the DSPy wrapper this script
drove (`squeaky_clean/infrastructure/dspy/entity_icp_dspy.py`) was deleted
from the production tree — it had eval-only callers and the `dspy-ai`
extra was never installed in CI. Recover both from git history:

    git log --diff-filter=D -- squeaky_clean/infrastructure/dspy/
"""

from __future__ import annotations

raise SystemExit(
    "compare_entity_icp.py is retired (R6.10): the dspy subtree was removed "
    "from squeaky_clean/. See this file's docstring for the git-history "
    "recovery command."
)
