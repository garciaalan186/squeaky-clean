"""Integration tests: pipeline retries / aborts on constraint #22 violations."""

from dataclasses import replace
from pathlib import Path

import pytest

from squeaky_clean.application.dtos.infrastructure_choice import InfrastructureChoice
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.http_conventions_error import (
    HttpConventionsError,
)
from squeaky_clean.application.use_cases.run_eval_pipeline import RunEvalPipeline
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from tests.application.use_cases.run_eval_stub_deps import build_stub_deps


def _http_problem() -> ProblemSpec:
    return ProblemSpec(
        id="P_HTTP", tier=0, slug="http", description="d",
        required_bounded_contexts=["w"], acceptance_criteria=["a"],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=["Adapter"], target_language=TargetLanguage.JAVA,
        infrastructure_choices=(
            InfrastructureChoice(category="rest_server_handler",
                                 technology="spring_boot",
                                 version_pin="2.7"),
        ),
    )


def _arch_with_headers(headers_type: str) -> ArchitectureSpec:
    cls = ClassSpec(
        name="Ctrl", pattern="Adapter", implements=None,
        methods=(f"handle(headers: {headers_type}): int",),
        depends=(), concretes=(),
    )
    mod = ModuleSpec(
        name="Calculator", layer=LayerType.INFRASTRUCTURE, exports=(),
        depends=(), classes=(cls,), invariants=(),
    )
    return ArchitectureSpec(modules=(mod,), graph=ArchitectureGraph(edges={}))


def test_pipeline_aborts_on_persistent_violations(tmp_path: Path) -> None:
    deps = build_stub_deps()
    bad = _arch_with_headers("String[]")
    calls = {"n": 0}

    def _design(_p: ProblemSpec, prior_violations: tuple[str, ...] = ()
                ) -> ArchitectureSpec:
        calls["n"] += 1
        return bad

    deps.design_architecture.execute = _design  # type: ignore[assignment,method-assign]
    pipeline = RunEvalPipeline(replace(deps))
    with pytest.raises(HttpConventionsError) as ei:
        pipeline.run(_http_problem(), tmp_path)
    assert ei.value.violations
    assert calls["n"] == 2
    assert (tmp_path / "HTTP_CONVENTION_VIOLATIONS.txt").exists()


def test_pipeline_proceeds_after_one_retry(tmp_path: Path) -> None:
    deps = build_stub_deps()
    bad = _arch_with_headers("String[]")
    good = _arch_with_headers("Map<String, String>")
    state = {"n": 0}

    def _design(_p: ProblemSpec, prior_violations: tuple[str, ...] = ()
                ) -> ArchitectureSpec:
        state["n"] += 1
        return bad if state["n"] == 1 else good

    deps.design_architecture.execute = _design  # type: ignore[assignment,method-assign]
    deps.design_architecture.last_raw_notation = (  # type: ignore[misc]
        "MODULE Calculator\nLAYER Infrastructure\nCLASSES {}\n"
    )
    pipeline = RunEvalPipeline(replace(deps))
    bundle = pipeline.run(_http_problem(), tmp_path)
    assert bundle.metrics.architect_retries == 1
    assert bundle.metrics.http_convention_violations == 0
    assert state["n"] == 2
