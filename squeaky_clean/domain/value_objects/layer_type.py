"""LayerType enum: the four Clean Architecture layers."""

from enum import Enum


class LayerType(Enum):
    """Enumerates the Clean Architecture layers a module may belong to."""

    DOMAIN = "domain"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    INTERFACE = "interface"
