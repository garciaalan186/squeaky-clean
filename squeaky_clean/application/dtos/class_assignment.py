"""ClassAssignment DTO: one ClassSpec routed to an ICP plus file paths."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


@dataclass(frozen=True)
class ClassAssignment:
    """Immutable record bundling a ClassSpec with its ICP + output paths.

    `icp_spec_name` is the markdown spec name (without .md) that
    LoadAgentSpec resolves (e.g., ``ValueObjectICP``). `file_path` is the
    production file the ICP will emit (e.g., ``src/calculator/operand.py``)
    and `test_file_path` is the sibling pytest file. `module` carries the
    focal ModuleSpec so the formatter can expose intra-module sibling
    interfaces. `architecture` is the OPTIONAL full ArchitectureSpec so
    the formatter can resolve cross-module exported sibling classes.
    `tech_spec` is the OPTIONAL Tier T TechSpec injected by the H1
    bridge when the ICP is a Tier C infrastructure adapter agent.
    """

    class_spec: ClassSpec
    module: ModuleSpec
    toolkit: LanguageToolkit
    icp_spec_name: str
    file_path: str
    test_file_path: str
    architecture: ArchitectureSpec | None = None
    tech_spec: TechSpec | None = None
