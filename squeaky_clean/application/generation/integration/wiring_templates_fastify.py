"""wiring_templates_fastify: TypeScript (Fastify/Express) composition-root renderer."""

from __future__ import annotations


def render_fastify_main(tech_specs: dict[str, object]) -> str:
    """Emit a TypeScript composition root ``src/index.ts`` for TS TechSpecs.

    Picks the runtime from the resolved ``rest_server_handler`` technology
    so the wiring's HTTP framework matches the generated handler + the
    ``package.json`` dependency (an ``express`` handler must not be wired
    with Fastify). Values map ``rest_server_handler -> <technology>``;
    ``message_queue_consumer`` -> ``setInterval`` poll skeleton; otherwise
    an empty server skeleton. Falls back to Fastify when the technology is
    unspecified (preserves the historical default).
    """
    consumer = "message_queue_consumer" in tech_specs
    head = "// Auto-generated composition root (WiringGenerator).\n"
    if "rest_server_handler" in tech_specs:
        rest_tech = str(tech_specs["rest_server_handler"])
        if "express" in rest_tech:
            return (head
                    + "import express from 'express';\n\n"
                    + "const app = express();\n"
                    + "app.use(express.json());\n"
                    + "const port = Number(process.env.SERVICE_PORT ?? 8000);\n"
                    + "app.post('/', (_req, res) => { res.status(200).json({}); });\n"
                    + "app.listen(port, () => console.log(`listening on ${port}`));\n")
        return (head
                + "import Fastify from 'fastify';\n\n"
                + "const app = Fastify({ logger: true });\n"
                + "const port = Number(process.env.SERVICE_PORT ?? 8000);\n"
                + "app.post('/', async () => ({}));\n"
                + "app.listen({ port, host: '0.0.0.0' });\n")
    if consumer:
        return (head
                + "console.log('consumer started');\n"
                + "setInterval((): void => undefined, 1000);\n")
    return (head + "console.log('service ready');\n"
            + "setInterval((): void => undefined, 1000);\n")
