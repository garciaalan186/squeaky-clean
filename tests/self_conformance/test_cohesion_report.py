"""Tests for the advisory cohesion report (R6.11a) — shape only, never gated."""

from tests.self_conformance.cohesion_report import intra_package_import_ratios


def test_report_is_well_formed_and_advisory() -> None:
    ratios = intra_package_import_ratios()
    assert ratios, "no multi-module packages found — scan is broken"
    for pkg, (intra, internal, ratio) in ratios.items():
        assert pkg.startswith("squeaky_clean")
        assert 0 <= intra <= internal
        assert 0.0 <= ratio <= 1.0


def test_known_cohesive_package_scores_above_zero() -> None:
    ratios = intra_package_import_ratios()
    notation = ratios.get(
        "squeaky_clean/application/generation/notation",
    )
    assert notation is not None
    assert notation[2] > 0.0, "the notation parser fleet imports itself"
