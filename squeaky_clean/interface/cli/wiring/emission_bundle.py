"""EmissionBundle: per-language emission collaborators built by EmissionWiring."""

from dataclasses import dataclass

from squeaky_clean.application.generation.emission.orchestrate_module import OrchestrateModule
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.interface.cli.language_adapter_bundle import LanguageAdapterBundle


@dataclass(frozen=True)
class EmissionBundle:
    """Toolkit + language adapters + module orchestrator for one problem."""

    toolkit: LanguageToolkit
    adapters: LanguageAdapterBundle
    orchestrate_module: OrchestrateModule
