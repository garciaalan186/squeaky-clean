"""wiring_templates: stable lookup facade over the per-language renderers.

Split per language (R6.11): the renderer bodies live in
``wiring_templates_{python,go,rust,express,fastify,java}.py``; this module
re-exports every public renderer so importers keep one flat namespace.
"""

from __future__ import annotations

from squeaky_clean.application.generation.integration.wiring_templates_express import (
    render_express_main as render_express_main,
)
from squeaky_clean.application.generation.integration.wiring_templates_fastify import (
    render_fastify_main as render_fastify_main,
)
from squeaky_clean.application.generation.integration.wiring_templates_go import (
    render_go_main as render_go_main,
)
from squeaky_clean.application.generation.integration.wiring_templates_java import (
    render_spring_boot_main as render_spring_boot_main,
)
from squeaky_clean.application.generation.integration.wiring_templates_python import (
    render_default as render_default,
)
from squeaky_clean.application.generation.integration.wiring_templates_python import (
    render_flask as render_flask,
)
from squeaky_clean.application.generation.integration.wiring_templates_python import (
    render_grpc_server as render_grpc_server,
)
from squeaky_clean.application.generation.integration.wiring_templates_python import (
    render_kafka_consumer_loop as render_kafka_consumer_loop,
)
from squeaky_clean.application.generation.integration.wiring_templates_python import (
    render_runtime as render_runtime,
)
from squeaky_clean.application.generation.integration.wiring_templates_rust import (
    render_rust_main as render_rust_main,
)
