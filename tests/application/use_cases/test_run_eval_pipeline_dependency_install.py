"""Pipeline integration test: dependency installer wired between integrate + tests."""

from dataclasses import replace
from pathlib import Path

from eval.problems.p0_calculator import P0
from squeaky_clean.application.dtos.install_result import InstallResult
from squeaky_clean.application.use_cases.run_eval_pipeline import RunEvalPipeline
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from tests.application.use_cases.run_eval_stub_deps import build_stub_deps


class _StubInstaller(DependencyInstaller):
    """Reports failure; counts how many times install() was called."""

    def __init__(self, succeeded: bool) -> None:
        self.calls: int = 0
        self._succeeded = succeeded

    def install(self, project_dir: Path) -> InstallResult:
        del project_dir
        self.calls += 1
        return InstallResult(self._succeeded, 7, "stubbed")


def test_failed_install_sets_metric_and_test_runner_still_runs(
    tmp_path: Path,
) -> None:
    deps = build_stub_deps()
    stub = _StubInstaller(succeeded=False)
    deps = replace(deps, dependency_installer=stub)
    pipeline = RunEvalPipeline(deps)
    bundle = pipeline.run(P0, tmp_path)
    assert stub.calls == 1
    assert bundle.metrics.dependency_install_failed is True
    deps.test_runner.run.assert_called_once()  # type: ignore[attr-defined]


def test_succeeded_install_keeps_metric_false(tmp_path: Path) -> None:
    deps = build_stub_deps()
    stub = _StubInstaller(succeeded=True)
    deps = replace(deps, dependency_installer=stub)
    pipeline = RunEvalPipeline(deps)
    bundle = pipeline.run(P0, tmp_path)
    assert stub.calls == 1
    assert bundle.metrics.dependency_install_failed is False


def test_no_installer_keeps_metric_false(tmp_path: Path) -> None:
    deps = build_stub_deps()  # dependency_installer is None
    pipeline = RunEvalPipeline(deps)
    bundle = pipeline.run(P0, tmp_path)
    assert bundle.metrics.dependency_install_failed is False
