"""Tests for the TechSpecResolution union alias (R6.8)."""

from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_fetch_failed import TechSpecFetchFailed
from squeaky_clean.domain.value_objects.tech_spec_operation import TechSpecOperation
from squeaky_clean.domain.value_objects.tech_spec_poisoned import TechSpecPoisoned
from squeaky_clean.domain.value_objects.tech_spec_resolution import TechSpecResolution


def _spec() -> TechSpec:
    op = TechSpecOperation(name="get", signature="get(key: str): str",
                           sdk_call="client.get", error_types=("RedisError",),
                           idempotency="idempotent")
    return TechSpec(schema_version="v1", category="kv_cache", technology="redis",
                    version_pin="5.0", language="python",
                    install={"manager": "pip", "package": "redis==5.0"},
                    imports={}, client_construction={}, primary_operations=(op,),
                    auth={})


def test_union_members_are_the_three_variants() -> None:
    # TechSpec itself is the success variant; no Resolved wrapper exists.
    variants: tuple[TechSpecResolution, ...] = (
        _spec(), TechSpecFetchFailed("down"), TechSpecPoisoned("markers"),
    )
    kinds = [type(v).__name__ for v in variants]
    assert kinds == ["TechSpec", "TechSpecFetchFailed", "TechSpecPoisoned"]


def test_isinstance_narrowing_distinguishes_success_from_failure() -> None:
    outcomes: list[TechSpecResolution] = [_spec(), TechSpecFetchFailed("x")]
    specs = [o for o in outcomes if isinstance(o, TechSpec)]
    failures = [o for o in outcomes if not isinstance(o, TechSpec)]
    assert len(specs) == 1 and len(failures) == 1
    assert failures[0].reason == "x"
