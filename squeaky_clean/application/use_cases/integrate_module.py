"""IntegrateModule: materialize a ModuleImplementation + TestArchitecture on disk."""

from squeaky_clean.application.dtos.integration_request import IntegrationRequest
from squeaky_clean.application.dtos.integration_result import IntegrationResult
from squeaky_clean.application.use_cases.integration_file_writer import IntegrationFileWriter
from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem


class IntegrateModule:
    """Writes all generated source + test files under the requested output dir."""

    def __init__(
        self,
        fs: ProjectFileSystem,
        bootstrap: IntegrationBootstrap,
    ) -> None:
        self._fs: ProjectFileSystem = fs
        self._writer: IntegrationFileWriter = IntegrationFileWriter(fs)
        self._bootstrap: IntegrationBootstrap = bootstrap

    def execute(self, request: IntegrationRequest) -> IntegrationResult:
        """Write every ImplementedClass + TestSkeleton and return the result.

        Delegates language-specific project skeleton writes (``conftest.py``,
        ``package.json``, etc.) to the injected IntegrationBootstrap.
        Then writes each class, each test skeleton, and any security
        test skeletons and returns an IntegrationResult with sorted paths.
        """
        output_dir = request.output_dir
        self._bootstrap.bootstrap(output_dir)
        src_paths = tuple(
            self._writer.write_class(impl, output_dir)
            for impl in request.implementation.implemented_classes
        )
        test_skeletons = list(request.test_architecture.test_skeletons)
        if request.security_test_architecture is not None:
            test_skeletons.extend(
                request.security_test_architecture.test_skeletons
            )
        test_paths = tuple(
            self._writer.write_test(sk, output_dir) for sk in test_skeletons
        )
        return IntegrationResult(
            output_dir=output_dir,
            files_written=tuple(sorted(src_paths)),
            test_files_written=tuple(sorted(test_paths)),
        )
