"""LanguageAdapterRegistry: the ONE per-language dispatch table (R6.7).

Every per-language constructor lives here — test runners, granularity
rules, integration bootstraps, class parsers, dependency installers and
(optional) ahead-of-time compilers. The selector / compiler-factory /
test-runner-factory modules are thin views over this table.

Go/Rust stay registered: R6.10 archived their EMITTER SPEC fleets (see
ACTIVE_EMITTER_LANGUAGES in map_pattern_to_emitter), not their toolchain
adapters — a recovered/replayed Go or Rust run must still dispatch.

The entries themselves live in ``language_adapters/`` (scripted vs
compiled targets); ``LanguageAdapterEntry`` is re-exported here so the
thin-view modules keep a single import point.
"""

from __future__ import annotations

from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.interface.cli.language_adapters.compiled_language_entries import (
    compiled_entries,
)
from squeaky_clean.interface.cli.language_adapters.language_adapter_entry import (
    LanguageAdapterEntry as LanguageAdapterEntry,
)
from squeaky_clean.interface.cli.language_adapters.scripted_language_entries import (
    scripted_entries,
)

REGISTRY: dict[TargetLanguage, LanguageAdapterEntry] = {
    **scripted_entries(),
    **compiled_entries(),
}
