"""TechSpecTarget: the (category, technology, version_pin) a TechSpec is for."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TechSpecTarget:
    """Identifies the technology choice a draft TechSpec describes.

    The triple always travels together (resolver lookups, doc fetch
    attempts, draft extraction), so it is bundled as one value object.
    """

    category: str
    technology: str
    version_pin: str
