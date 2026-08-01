"""ToolchainInfo port: abstract interface for toolchain version probing."""

from abc import ABC, abstractmethod


class ToolchainInfo(ABC):
    """Port for recording the toolchain versions a run executed under.

    R6.4c: scores depend on the environment (Node 22 broke the runner;
    javac 11 rejects records CI's JDK 21 accepts — R5.9), so the run
    manifest captures tool versions. The subprocess probing lives in an
    infrastructure adapter behind this port; the application layer only
    consumes the resulting mapping.
    """

    @abstractmethod
    def versions(self) -> dict[str, str]:
        """Return ``tool -> first version line`` (``"absent"`` if missing)."""
