"""Tests for MCDAScorer (H3) — reproduces design §3.2 worked example."""

import pytest

from squeaky_clean.application.dtos.mcda_weights import MCDAWeights
from squeaky_clean.application.use_cases.mcda_registry import MCDARegistryEntry
from squeaky_clean.application.use_cases.mcda_scorer import MCDAScorer

_WEIGHTS = MCDAWeights().as_dict()


def _entry(tech: str, scores: dict[str, int], stab: str = "ga") -> MCDARegistryEntry:
    return MCDARegistryEntry(
        technology=tech, version_pin=f"{tech}==1.0",
        stability=stab, scores=scores,
    )


def _msg_queue_candidates() -> tuple[MCDARegistryEntry, ...]:
    """Design §3.2 worked example: 5 messaging candidates."""
    return (
        _entry("kafka",    {"ops": 2, "cost": 3, "cold": 4, "thru": 5,
                            "eco": 5, "reg": 5, "lic": 5, "team": 4}),
        _entry("rabbitmq", {"ops": 3, "cost": 4, "cold": 5, "thru": 3,
                            "eco": 5, "reg": 5, "lic": 5, "team": 2}),
        _entry("sqs",      {"ops": 5, "cost": 4, "cold": 3, "thru": 4,
                            "eco": 4, "reg": 5, "lic": 5, "team": 3}),
        _entry("kinesis",  {"ops": 4, "cost": 3, "cold": 3, "thru": 5,
                            "eco": 4, "reg": 4, "lic": 5, "team": 3}),
        _entry("nats",     {"ops": 3, "cost": 4, "cold": 5, "thru": 4,
                            "eco": 3, "reg": 5, "lic": 5, "team": 1}),
    )


def test_worked_example_reproduces_design_section_3_2() -> None:
    table = MCDAScorer().score(
        "message_queue_consumer", _msg_queue_candidates(), _WEIGHTS, (),
    )
    by_tech = {r.technology: r.weighted_score for r in table.candidates}
    assert by_tech["sqs"] == pytest.approx(4.05)
    assert by_tech["kafka"] == pytest.approx(3.75)
    assert by_tech["kinesis"] == pytest.approx(3.75)
    assert by_tech["rabbitmq"] == pytest.approx(3.65)
    assert by_tech["nats"] == pytest.approx(3.45)
    assert table.winner().technology == "sqs"


def test_tie_breaker_alphabetical_when_no_prefs_or_stability_diff() -> None:
    table = MCDAScorer().score(
        "message_queue_consumer", _msg_queue_candidates(), _WEIGHTS, (),
    )
    runners_up = [r.technology for r in table.candidates
                  if r.weighted_score == pytest.approx(3.75)]
    # kafka < kinesis alphabetically
    assert runners_up == ["kafka", "kinesis"]


def test_problem_overrides_take_precedence_on_ties() -> None:
    table = MCDAScorer().score(
        "message_queue_consumer", _msg_queue_candidates(), _WEIGHTS,
        ("kinesis", "kafka"),
    )
    runners_up = [r.technology for r in table.candidates
                  if r.weighted_score == pytest.approx(3.75)]
    # kinesis listed first in prefs → wins the tie
    assert runners_up == ["kinesis", "kafka"]


def test_scorer_is_deterministic() -> None:
    s = MCDAScorer()
    a = s.score("c", _msg_queue_candidates(), _WEIGHTS, ())
    b = s.score("c", _msg_queue_candidates(), _WEIGHTS, ())
    assert a.candidates == b.candidates
    assert a.weights == b.weights
