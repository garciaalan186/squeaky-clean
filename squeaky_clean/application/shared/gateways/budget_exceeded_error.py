"""BudgetExceededError: raised when a spend would exceed the run's cost cap."""


class BudgetExceededError(RuntimeError):
    """Raised when recording or projecting a spend would exceed the cap."""
