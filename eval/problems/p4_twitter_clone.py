"""P4 Twitter Clone: multi-module web app with auth, posts, timeline."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
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
)
