"""Metric entity: a single named numeric measurement."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Metric:
    """One named numeric measurement recorded during an eval run."""

    name: str
    value: float
