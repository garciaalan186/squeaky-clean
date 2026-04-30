"""P5 OAuth2 Authorization Server: realistic security-sensitive multi-module app."""

from squeaky_clean.application.dtos.data_classification import DataClassification
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P5: ProblemSpec = ProblemSpec(
    id="P5",
    tier=4,
    slug="oauth2_server",
    description=(
        "Minimal OAuth2 authorization server supporting client registration, "
        "authorization-code grants, access-token issuance, and refresh-token "
        "rotation. Three bounded contexts: Clients (client registration + "
        "credentials), Grants (authorization codes + redirect validation), "
        "Tokens (access + refresh issuance + revocation)."
    ),
    required_bounded_contexts=["Clients", "Grants", "Tokens"],
    acceptance_criteria=[
        "Given a client_name 'app1' and redirect_uri 'https://app1/cb', When register_client is called, Then result is a Client",
        "Given a client 'c1' and redirect_uri 'https://app1/cb', When issue_code is called, Then result is an AuthorizationCode",
        "Given a client 'c1' and a wrong redirect_uri 'https://evil', When issue_code is called, Then an error is raised",
        "Given a valid AuthorizationCode, When exchange_code is called, Then result is an AccessToken",
        "Given an AuthorizationCode that was already exchanged, When exchange_code is called, Then an error is raised",
        "Given a valid RefreshToken, When refresh is called, Then result is a new AccessToken",
        "Given a revoked RefreshToken, When refresh is called, Then an error is raised",
    ],
    expected_module_count=(3, 4),
    expected_class_count=(15, 30),
    required_patterns=[
        "Entity", "ValueObject", "Repository", "UseCase",
    ],
    target_language=TargetLanguage.PYTHON,
    domain_conventions=(
        "single_use_authorization_code",
        "refresh_token_rotation",
        "redirect_uri_strict_match",
        "unique_by_natural_key",
    ),
    data_classification=(
        DataClassification(field_ref="Client.client_secret", sensitivity="credential"),
        DataClassification(field_ref="AccessToken.value", sensitivity="session_token"),
        DataClassification(field_ref="RefreshToken.value", sensitivity="session_token"),
        DataClassification(field_ref="AuthorizationCode.value", sensitivity="session_token"),
    ),
)
