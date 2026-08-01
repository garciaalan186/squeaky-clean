"""wiring_templates_java: Spring Boot composition-root renderer."""

from __future__ import annotations


def render_spring_boot_main() -> str:
    """Emit a Spring Boot composition root.

    Spring's component scanning + @Bean configuration handles the wiring
    of @RestController / @KafkaListener / etc. — so the Java composition
    root is the @SpringBootApplication bootstrap class plus a few @Bean
    factories for non-Spring-managed adapters (e.g. blob stores).

    The body is intentionally minimal: a real project gains @Bean methods
    for outbound adapters (BlobStore, KafkaTemplate, etc.) but those are
    auto-configured by Spring Boot starter modules in the common path.
    """
    return (
        "// App: Spring Boot composition root (auto-wires @RestController / @KafkaListener).\n"
        "package com.example;\n"
        "\n"
        "import org.springframework.boot.SpringApplication;\n"
        "import org.springframework.boot.autoconfigure.SpringBootApplication;\n"
        "import org.springframework.kafka.annotation.EnableKafka;\n"
        "\n"
        "@SpringBootApplication\n"
        "@EnableKafka\n"
        "public class App {\n"
        "    public static void main(String[] args) {\n"
        "        SpringApplication.run(App.class, args);\n"
        "    }\n"
        "}\n"
    )
