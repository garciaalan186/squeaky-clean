"""Tests for TechSpecStage: no-op guards + explicit-choice resolution."""

import dataclasses
from pathlib import Path
from typing import cast
from unittest.mock import Mock

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.evaluation.eval.run.stages.tech_spec_stage import TechSpecStage
from squeaky_clean.application.generation.architecture.orchestrate_architecture import (
    OrchestrateArchitecture,
)
from squeaky_clean.application.generation.emission.orchestrate_module import OrchestrateModule
from squeaky_clean.application.generation.techspec.infrastructure_choice import (
    InfrastructureChoice,
)
from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.interfaces.tech_spec_resolver import TechSpecResolver
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_operation import TechSpecOperation
from squeaky_clean.domain.value_objects.tech_spec_target import TechSpecTarget
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import _impl, build_stub_deps


def _redis_spec() -> TechSpec:
    op = TechSpecOperation(name="get", signature="get(key: str): str",
                           sdk_call="client.get", error_types=("RedisError",),
                           idempotency="idempotent")
    return TechSpec(schema_version="v1", category="kv_cache", technology="redis",
                    version_pin="5.0", language="python",
                    install={"manager": "pip", "package": "redis==5.0"},
                    imports={}, client_construction={}, primary_operations=(op,),
                    auth={})


class _StubResolver(TechSpecResolver):
    """Returns the canned redis TechSpec for any triple."""

    def resolve(self, target: TechSpecTarget) -> TechSpec:
        return _redis_spec()


def _ctx(tmp_path: Path, problem: ProblemSpec) -> PipelineContext:
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    arch = ArchitectureSpec(modules=(_impl().module,),
                            graph=ArchitectureGraph(edges={}))
    ctx = PipelineContext(
        problem=problem, output_dir=out,
        emitter=CheckpointEmitter(problem.id, out),
        lifecycle=LifecycleTimestampLog(out),
    )
    return dataclasses.replace(ctx, arch=arch)


def _orchestrator() -> OrchestrateArchitecture:
    return OrchestrateArchitecture(cast(OrchestrateModule, Mock(spec=OrchestrateModule)))


def test_noop_when_infrastructure_mode_is_not_auto(tmp_path: Path) -> None:
    deps = build_stub_deps()  # infrastructure_mode defaults to "manual"
    ctx = _ctx(tmp_path, P0)
    out = TechSpecStage(deps, _orchestrator()).run(ctx)
    assert out is ctx


def test_noop_in_auto_mode_without_a_resolver(tmp_path: Path) -> None:
    deps = dataclasses.replace(
        build_stub_deps(), run_config=RunConfig(infrastructure_mode="auto"))
    ctx = _ctx(tmp_path, P0)
    out = TechSpecStage(deps, _orchestrator()).run(ctx)
    assert out is ctx


def test_explicit_choice_resolves_and_registers_spec(tmp_path: Path) -> None:
    deps = dataclasses.replace(
        build_stub_deps(),
        run_config=RunConfig(infrastructure_mode="auto"),
        tech_spec_resolver=_StubResolver())
    problem = dataclasses.replace(
        P0, infrastructure_choices=(
            InfrastructureChoice("kv_cache", "redis", "5.0"),))
    single = Mock(spec=OrchestrateModule)
    stage = TechSpecStage(
        deps, OrchestrateArchitecture(cast(OrchestrateModule, single)))
    out = stage.run(_ctx(tmp_path, problem))
    assert set(out.tech_specs) == {"kv_cache"}
    assert out.tech_specs["kv_cache"].technology == "redis"
    single.register_tech_spec.assert_called_once_with(out.tech_specs["kv_cache"])
    assert out.counters.infra_explicit == 1
    assert out.counters.infra_derived == 0
    assert out.counters.mcda_runs == 0
