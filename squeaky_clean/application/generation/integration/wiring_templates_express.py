"""wiring_templates_express: JavaScript (Express) composition-root renderer."""

from __future__ import annotations


def render_express_main(tech_specs: dict[str, object]) -> str:
    """Emit a JavaScript composition root ``index.js`` for JS TechSpec runtimes.

    Picks the runtime from inbound categories present in ``tech_specs``:
    rest_server_handler -> Express ``app.listen``; message_queue_consumer
    -> ``setInterval`` poll skeleton; otherwise an empty server skeleton.
    """
    rest = "rest_server_handler" in tech_specs
    consumer = "message_queue_consumer" in tech_specs
    head = "// Auto-generated composition root (WiringGenerator).\n"
    if rest:
        return (head
                + "const express = require('express');\n"
                + "const app = express();\n"
                + "app.use(express.json());\n"
                + "const port = process.env.SERVICE_PORT || 8000;\n"
                + "app.post('/', (req, res) => res.status(200).json({}));\n"
                + "app.listen(port, () => console.log(`listening on ${port}`));\n")
    if consumer:
        return (head
                + "console.log('consumer started');\n"
                + "setInterval(() => {}, 1000);\n")
    return (head + "console.log('service ready');\n"
            + "setInterval(() => {}, 1000);\n")
