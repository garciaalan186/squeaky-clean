"""MapConcernToSecurityICP: resolve a concern category to a Security ICP spec."""

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit

_CATEGORY_MAP: dict[str, str] = {
    "input_validation": "InputValidationSecurityICP",
    "boundary": "BoundarySecurityICP",
    "error_handling": "ErrorSafetySecurityICP",
    "injection": "InjectionSecurityICP",
    "access_control": "AccessControlSecurityICP",
    "data_exposure": "AccessControlSecurityICP",
}

_FALLBACK: str = "AccessControlSecurityICP"


class MapConcernToSecurityICP:
    """Maps a security concern category to a Security ICP spec path."""

    def map(self, category: str, toolkit: LanguageToolkit) -> str:
        """Return ``<lang>/security/<ICPName>`` for the given category."""
        icp_name = _CATEGORY_MAP.get(category, _FALLBACK)
        return f"{toolkit.icp_library}/security/{icp_name}"
