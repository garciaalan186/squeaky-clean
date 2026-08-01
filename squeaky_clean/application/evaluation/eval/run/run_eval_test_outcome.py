"""RunEvalTestOutcome: derive the TestOutcome block from pipeline test runs."""

from squeaky_clean.application.evaluation.eval.metrics.metrics_inputs import MetricsInputs
from squeaky_clean.application.evaluation.eval.metrics.model.test_outcome import TestOutcome


class RunEvalTestOutcome:
    """Splits functional vs security results into one TestOutcome."""

    def build(self, inputs: MetricsInputs) -> TestOutcome:
        """TestOutcome for one run; headline = functional acceptance."""
        pr = inputs.test_run_result
        total = pr.passed + pr.failed + pr.errors
        tests_pass = (pr.passed / total) if total > 0 else 0.0
        fr = inputs.functional_test_run_result
        if fr is None:
            return TestOutcome(
                tests_pass=tests_pass,
                test_status=self._test_status(pr.passed, pr.failed, pr.errors),
                tests_collected=total,
                functional_tests_pass=tests_pass,
                functional_test_count=total,
                security_test_count=inputs.security_test_count,
            )
        func_total = fr.passed + fr.failed + fr.errors
        func_pass = (fr.passed / func_total) if func_total > 0 else 0.0
        sec_total = total - func_total
        sec_pass = (
            ((pr.passed - fr.passed) / sec_total) if sec_total > 0 else 0.0
        )
        # Headline reflects functional acceptance (the documented meaning
        # of tests_pass), not the security-diluted blend; the numerous
        # auto-generated security tests are reported via security_tests_pass.
        return TestOutcome(
            tests_pass=func_pass,
            test_status=self._test_status(fr.passed, fr.failed, fr.errors),
            tests_collected=func_total,
            functional_tests_pass=func_pass,
            functional_test_count=func_total,
            security_test_count=inputs.security_test_count,
            security_tests_pass=sec_pass,
        )

    @staticmethod
    def _test_status(passed: int, failed: int, errors: int) -> str:
        """Classify a test run so a real 0% is not confused with "no run".

        ``not_measured`` = nothing collected (toolchain absent);
        ``build_failed`` = only errors, no test executed to pass/fail
        (compile/collection failure); ``ok`` = tests actually ran.
        """
        if passed + failed + errors == 0:
            return "not_measured"
        if passed == 0 and failed == 0 and errors > 0:
            return "build_failed"
        return "ok"
