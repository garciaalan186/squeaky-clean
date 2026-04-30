"""ModelTier enum: agent tiers mapped to model sizes by the router."""

from enum import Enum


class ModelTier(Enum):
    """The three agent tiers used by the Squeaky Clean pipeline."""

    ARCHITECT = "architect"
    MANAGER = "manager"
    ICP = "icp"
    FIXER = "fixer"
