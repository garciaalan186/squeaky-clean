"""GenerateSecurityTests: dispatch parallel Security ICPs for each concern."""

from squeaky_clean.application.generation.security.security_dispatch_context import (
    SecurityDispatchContext,
)
from squeaky_clean.application.generation.security.security_icp_dispatcher import (
    SecurityICPDispatcher,
)
from squeaky_clean.application.generation.security.security_test_context import SecurityTestContext
from squeaky_clean.application.generation.testgen.generate_test_architecture_deps import (
    GenerateTestArchitectureDeps,
)
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.shared.gateways.recording_gateway import RecordingGateway


class GenerateSecurityTests:
    """Use case: produce a TestArchitecture of security tests via parallel ICPs."""

    def __init__(self, deps: GenerateTestArchitectureDeps) -> None:
        self._deps: GenerateTestArchitectureDeps = deps
        recording_gw = RecordingGateway(deps.gateway, deps.recorder)
        self._dispatcher: SecurityICPDispatcher = SecurityICPDispatcher(
            gateway=recording_gw, router=deps.router,
            run_config=deps.run_config,
        )

    def execute(self, context: SecurityTestContext) -> TestArchitecture:
        """Dispatch Security ICPs in parallel and return TestArchitecture."""
        dispatch_ctx = SecurityDispatchContext(
            review=context.review,
            module=context.module,
            toolkit=self._deps.toolkit,
            architecture=context.architecture,
        )
        return self._dispatcher.dispatch(dispatch_ctx)
