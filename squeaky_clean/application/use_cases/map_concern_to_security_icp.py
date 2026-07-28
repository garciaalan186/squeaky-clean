"""MapConcernToSecurityEmitter: resolve a concern category to a Security ICP spec."""

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit

_CATEGORY_MAP: dict[str, str] = {
    "input_validation": "InputValidationSecurityEmitter",
    "boundary": "BoundarySecurityEmitter",
    "error_handling": "ErrorSafetySecurityEmitter",
    "injection": "InjectionSecurityEmitter",
    "access_control": "AccessControlSecurityEmitter",
    "data_exposure": "AccessControlSecurityEmitter",
}

_FALLBACK: str = "AccessControlSecurityEmitter"


class MapConcernToSecurityEmitter:
    """Maps a security concern category to a Security ICP spec path."""

    def map(self, category: str, toolkit: LanguageToolkit) -> str:
        """Return ``<lang>/security/<ICPName>`` for the given category."""
        icp_name = _CATEGORY_MAP.get(category, _FALLBACK)
        return f"{toolkit.icp_library}/security/{icp_name}"
