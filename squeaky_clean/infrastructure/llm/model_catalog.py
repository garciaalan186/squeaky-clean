"""ModelId: the single source of truth for concrete Claude model identifiers.

A model version string is an infrastructure detail (a vendor identifier), so it
lives HERE, once. The router, pricing table, and any adapter reference these
constants — never a bare literal — so a version bump is a one-line change and
cannot drift across layers. Inner (domain/application) layers never name a
concrete model: they route by ``ModelTier`` and let the infrastructure boundary
resolve it (see ModelRouter).

To bump a tier's model, change the VALUE of the semantic constant below; every
call site follows automatically.
"""

from typing import Final


class ModelId:
    """Concrete model identifiers, grouped by role in the current lineup."""

    # --- Current production models (bump these values on a release) ---
    OPUS: Final = "claude-opus-4-8"
    SONNET: Final = "claude-sonnet-5"
    HAIKU: Final = "claude-haiku-4-5-20251001"

    # --- Retained only so ModelPricing can price historical run manifests ---
    HAIKU_4_5_ALIAS: Final = "claude-haiku-4-5"
    SONNET_4_6: Final = "claude-sonnet-4-6"
    SONNET_4_5: Final = "claude-sonnet-4-5"
    OPUS_4_7: Final = "claude-opus-4-7"
    OPUS_4_6: Final = "claude-opus-4-6"
