"""P10 Report Builder: exercises Builder + AbstractFactory + Prototype (R5.6)."""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P10: ProblemSpec = ProblemSpec(
    id="P10",
    tier=10,
    slug="report_builder",
    description=(
        "A report generator. Reports are assembled step by step from a title "
        "and text sections by a builder. Report elements (headings, "
        "paragraphs) are created through interchangeable element factories — "
        "an HTML family and a Markdown family — so a report renders in either "
        "format without changing its content. A stored template report can be "
        "cloned and customized without modifying the template."
    ),
    required_bounded_contexts=["reporting"],
    acceptance_criteria=[
        "Given a report builder, When title 'Q1' is set and sections 'intro' and 'summary' are added and build is called, Then the report has title 'Q1' and 2 sections",
        "Given a report builder with no title set, When build is called, Then an error is raised",
        "Given the HTML element factory, When a heading for 'Intro' is created and rendered, Then the result is '<h1>Intro</h1>'",
        "Given the Markdown element factory, When a heading for 'Intro' is created and rendered, Then the result is '# Intro'",
        "Given the HTML element factory, When a paragraph for 'hello' is created and rendered, Then the result is '<p>hello</p>'",
        "Given a template report with title 'Template' and 1 section, When it is cloned and the clone's title is changed to 'March', Then the clone has title 'March' and the template still has title 'Template'",
        "Given a template report with 1 section, When a section is added to a clone of it, Then the template still has 1 section",
    ],
    expected_module_count=(1, 3),
    expected_class_count=(6, 18),
    required_patterns=[
        "Builder", "AbstractFactory", "Prototype", "SimpleClass",
    ],
    target_language=TargetLanguage.PYTHON,
    # R5.6 golden: N=3, run 472 (2026-07-30). HONESTLY UNSTABLE — 1.00/0.00/
    # 0.00 across seeds; the creational family flakes end-to-end. This IS the
    # baseline; improvements must beat it, not a lucky N=1.
    golden_metrics=GoldenMetrics(
        replicates=3,
        tests_pass_mean=0.3333, tests_pass_stddev=0.5774,
        functional_pass_mean=0.3333, functional_pass_stddev=0.5774,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.0501, cost_usd_stddev=0.0434,
        model_routing=(
            "architect=claude-sonnet-5",
            "fixer=claude-sonnet-5",
            "icp=claude-haiku-4-5-20251001",
            "manager=claude-sonnet-5",
        ),
        calibrated_run="meta-evaluation_472_20260730-211547",
    ),
)
