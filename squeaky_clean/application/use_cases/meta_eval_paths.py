"""MetaEvalPaths: computes per-run directory layout under a run root."""

from datetime import datetime
from pathlib import Path


class MetaEvalPaths:
    """Allocates a new meta-evaluation run directory with per-problem subdirs."""

    _PREFIX = "meta-evaluation_"

    def __init__(self, run_root: Path) -> None:
        self._run_root: Path = run_root
        self._run_dir: Path | None = None

    def allocate(self) -> Path:
        """Create and return a fresh `meta-evaluation_{NNN}_{timestamp}/` dir."""
        self._run_root.mkdir(parents=True, exist_ok=True)
        next_index = self._next_index()
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        name = f"{self._PREFIX}{next_index:03d}_{timestamp}"
        run_dir = self._run_root / name
        run_dir.mkdir(parents=True, exist_ok=False)
        self._run_dir = run_dir
        return run_dir

    def adopt(self, existing_run_dir: Path) -> None:
        """Reuse an already-allocated run directory (for sweep sharing)."""
        if not existing_run_dir.is_dir():
            raise FileNotFoundError(f"run dir does not exist: {existing_run_dir}")
        self._run_dir = existing_run_dir

    def problem_set_dir(self, index: int, slug: str) -> Path:
        """Return the path `problem-set-{index}-{slug}-code/` inside the run.

        ``slug`` should already encode the target language for sweep
        mode so multiple language variants of one problem don't share
        a directory and clobber each other's files in parallel.
        """
        if self._run_dir is None:
            raise RuntimeError("allocate() must be called before problem_set_dir()")
        path = self._run_dir / f"problem-set-{index}-{slug}-code"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _next_index(self) -> int:
        existing: list[int] = []
        for child in self._run_root.iterdir():
            if not child.is_dir() or not child.name.startswith(self._PREFIX):
                continue
            parts = child.name[len(self._PREFIX):].split("_", 1)
            if parts and parts[0].isdigit():
                existing.append(int(parts[0]))
        return (max(existing) + 1) if existing else 1
