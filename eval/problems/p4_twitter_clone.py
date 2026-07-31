"""P4 Twitter Clone: multi-module web app with auth, posts, timeline."""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P4: ProblemSpec = ProblemSpec(
    id="P4",
    tier=4,
    slug="twitter_clone",
    description=(
        "Twitter-style social application supporting user signup, password "
        "login, posting tweets, following other users, and viewing a timeline "
        "of tweets from followed users. Built as multiple bounded contexts: "
        "Auth (users + credentials + sessions), Posts (tweets + authoring), "
        "and Timeline (follow graph + feed retrieval)."
    ),
    required_bounded_contexts=["Auth", "Posts", "Timeline"],
    acceptance_criteria=[
        "Given a username 'alice' and password 'pw1', When sign_up is called, Then result is a User",
        "Given an existing user 'alice' with password 'pw1', When login is called with username 'alice' and password 'pw1', Then result is a Session",
        "Given a user 'alice' and password 'wrong', When login is called, Then an error is raised",
        "Given a user 'alice' and content 'hello', When post_tweet is called, Then result is a Tweet",
        "Given an empty content, When post_tweet is called, Then an error is raised",
        "Given user 'alice' follows 'bob' and bob has 1 tweet, When get_timeline is called for alice, Then the result length is 1",
        "Given user 'alice' has not followed anyone, When get_timeline is called for alice, Then the result length is 0",
    ],
    expected_module_count=(3, 4),
    expected_class_count=(12, 25),
    required_patterns=[
        "Entity", "ValueObject", "Repository", "UseCase",
    ],
    target_language=TargetLanguage.PYTHON,
    # R5.2 golden: N=3, meta-evaluation_488 (2026-07-30), zero replicate failures.
    golden_metrics=GoldenMetrics(
        replicates=3,
        tests_pass_mean=0.6667, tests_pass_stddev=0.2082,
        functional_pass_mean=0.6667, functional_pass_stddev=0.2082,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.4449, cost_usd_stddev=0.0440,
        model_routing=(
        "architect=claude-sonnet-5",
        "fixer=claude-sonnet-5",
        "icp=claude-haiku-4-5-20251001",
        "manager=claude-sonnet-5",
    ),
        calibrated_run="meta-evaluation_488_20260730-230409",
    ),
)
