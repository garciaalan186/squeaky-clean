"""CheckpointProgress: marks payload-light pipeline stages on the checkpoint (G3)."""

from squeaky_clean.application.evaluation.eval.resume.checkpoint_state import CheckpointState


class CheckpointProgress:
    """Stage markers for the post-emission pipeline phases."""

    def __init__(self, state: CheckpointState) -> None:
        self._state: CheckpointState = state

    def integrated(self) -> None:
        self._state.update(stage="integrated", integration_done=True)

    def tested(self) -> None:
        self._state.update(stage="tested")

    def fixed(self, passes: int) -> None:
        self._state.update(stage="fixed", fixer_passes_completed=passes)

    def complete(self, cost_spent_usd: float) -> None:
        self._state.update(stage="complete", cost_spent_usd=cost_spent_usd)
