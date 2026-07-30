"""ModuleAssignment DTO: which module each class lands in, and its layer."""

from dataclasses import dataclass

from squeaky_clean.domain.value_objects.layer_type import LayerType


@dataclass(frozen=True)
class ModuleAssignment:
    """Result of grouping catalogued classes into modules.

    `module_of` maps every class FQN to the name of the module it belongs
    to. `layer_of` maps every module name to its Clean-Architecture layer
    (a domain SCC seeds a DOMAIN module; an orphan non-domain class keeps
    its own layer). Both are derived deterministically from the catalog.
    """

    module_of: dict[str, str]
    layer_of: dict[str, LayerType]
