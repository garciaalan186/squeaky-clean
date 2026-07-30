"""MCDACriterion: enumerated MCDA criterion names (design §3.2)."""

from typing import Literal, get_args

MCDACriterion = Literal[
    "ops",
    "cost",
    "cold",
    "thru",
    "eco",
    "reg",
    "lic",
    "team",
]

ALL_MCDA_CRITERIA: tuple[str, ...] = tuple(get_args(MCDACriterion))
