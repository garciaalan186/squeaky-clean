"""Tests for RefactorPlanSerializer: stable refactor_plan.json rendering."""

import json

from squeaky_clean.application.generation.recovery.refactor.refactor_plan import RefactorPlan
from squeaky_clean.application.generation.recovery.refactor.refactor_plan_serializer import (
    RefactorPlanSerializer,
)


def test_serialized_plan_round_trips_through_json() -> None:
    plan = RefactorPlan(fix=("coupling:User", "cycle:Orders"), ignore=("god_class:App",))
    text = RefactorPlanSerializer().serialize(plan)
    assert json.loads(text) == {
        "fix": ["coupling:User", "cycle:Orders"],
        "ignore": ["god_class:App"],
    }


def test_output_is_indented_and_diff_friendly() -> None:
    text = RefactorPlanSerializer().serialize(RefactorPlan(fix=("a:B",), ignore=()))
    assert text == '{\n  "fix": [\n    "a:B"\n  ],\n  "ignore": []\n}'


def test_same_plan_always_serializes_identically() -> None:
    plan = RefactorPlan(fix=("a:B",), ignore=("c:D",))
    assert RefactorPlanSerializer().serialize(plan) == RefactorPlanSerializer().serialize(plan)


def test_empty_plan_serializes_to_empty_lists() -> None:
    text = RefactorPlanSerializer().serialize(RefactorPlan(fix=(), ignore=()))
    assert json.loads(text) == {"fix": [], "ignore": []}
