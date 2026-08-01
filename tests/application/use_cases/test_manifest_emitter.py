"""Tests for ManifestEmitter: language-routed dependency manifest emission."""

import dataclasses
from pathlib import Path

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.manifest_emitter import ManifestEmitter
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.interfaces.run_logger import RunLogger
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_operation import TechSpecOperation
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import _impl


class _FakeRunLogger(RunLogger):
    """Captures every emitted (kind, fields) event for assertions."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    def event(self, kind: str, **fields: object) -> None:
        self.events.append((kind, dict(fields)))


def _pip_spec() -> TechSpec:
    op = TechSpecOperation(name="get", signature="get(key: str): str",
                           sdk_call="client.get", error_types=("RedisError",),
                           idempotency="idempotent")
    return TechSpec(schema_version="v1", category="kv_cache", technology="redis",
                    version_pin="5.0", language="python",
                    install={"manager": "pip", "package": "redis==5.0"},
                    imports={}, client_construction={}, primary_operations=(op,),
                    auth={})


def _ctx(tmp_path: Path, tech_specs: dict[str, TechSpec]) -> PipelineContext:
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    arch = ArchitectureSpec(modules=(_impl().module,),
                            graph=ArchitectureGraph(edges={}))
    ctx = PipelineContext(
        problem=P0, output_dir=out,
        emitter=CheckpointEmitter("P0", out),
        lifecycle=LifecycleTimestampLog(out),
    )
    return dataclasses.replace(ctx, arch=arch, tech_specs=tech_specs)


def test_no_tech_specs_emits_no_manifest_events(tmp_path: Path) -> None:
    logger = _FakeRunLogger()
    ctx = _ctx(tmp_path, {})
    ManifestEmitter(logger, LocalFileSystem()).emit(ctx)
    assert logger.events == []
    assert not (ctx.output_dir / "requirements.txt").exists()


def test_python_pip_spec_emits_requirements_event_on_success(tmp_path: Path) -> None:
    logger = _FakeRunLogger()
    ctx = _ctx(tmp_path, {"kv_cache": _pip_spec()})
    ManifestEmitter(logger, LocalFileSystem()).emit(ctx)
    kinds = [kind for kind, _ in logger.events]
    assert kinds == ["requirements_txt_emitted"]
    requirements = ctx.output_dir / "requirements.txt"
    assert requirements.read_text() == "redis==5.0\n"
    # Non-python manifests stay unwritten for a python target.
    assert not (ctx.output_dir / "go.mod").exists()
    assert not (ctx.output_dir / "Cargo.toml").exists()
    assert not (ctx.output_dir / "package.json").exists()


class _FailingFs(LocalFileSystem):
    def write(self, path: Path, content: str) -> None:
        raise OSError("disk full")


def test_manifest_write_error_is_caught_and_logged(tmp_path: Path) -> None:
    """R6.8: a generator's ManifestWriteError becomes a logged failure event."""
    logger = _FakeRunLogger()
    ctx = _ctx(tmp_path, {"kv_cache": _pip_spec()})
    ManifestEmitter(logger, _FailingFs()).emit(ctx)
    kinds = [kind for kind, _ in logger.events]
    assert kinds == ["manifest_emit_failed"]
    assert "disk full" in str(logger.events[0][1]["error"])
