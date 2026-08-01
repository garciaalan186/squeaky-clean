"""Tests for the Spring Boot composition-root template."""

from squeaky_clean.application.generation.integration.wiring_templates_java import (
    render_spring_boot_main,
)


def test_spring_boot_root_bootstraps_the_application() -> None:
    code = render_spring_boot_main()
    assert "@SpringBootApplication" in code
    assert "@EnableKafka" in code
    assert "SpringApplication.run(App.class, args);" in code
    assert code.startswith("// App: Spring Boot composition root")
