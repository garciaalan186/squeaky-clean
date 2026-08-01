"""Tests for RefactorPlan: the triage decision over analyzed violations."""

import dataclasses

import pytest

from squeaky_clean.application.generation.recovery.refactor.refactor_plan import RefactorPlan


def test_plan_holds_fix_and_ignore_violation_ids_as_tuples() -> None:
    plan = RefactorPlan(fix=("coupling:User", "cycle:Orders"), ignore=("god_class:App",))
    assert plan.fix == ("coupling:User", "cycle:Orders")
    assert plan.ignore == ("god_class:App",)


def test_plans_compare_by_value_and_replace_moves_a_category() -> None:
    plan = RefactorPlan(fix=("coupling:User",), ignore=())
    assert plan == RefactorPlan(fix=("coupling:User",), ignore=())
    triaged = dataclasses.replace(plan, fix=(), ignore=("coupling:User",))
    assert triaged.ignore == ("coupling:User",)
    assert plan.fix == ("coupling:User",)


def test_plan_is_frozen() -> None:
    plan = RefactorPlan(fix=(), ignore=())
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(plan, "fix", ("x:Y",))  # noqa: B010
