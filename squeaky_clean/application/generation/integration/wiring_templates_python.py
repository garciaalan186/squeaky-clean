"""wiring_templates_python: Python main.py renderers (Flask / Kafka / gRPC)."""

from __future__ import annotations


def _entry_header() -> str:
    return ('if __name__ == "__main__":\n'
            "    HOST = os.environ.get(\"SERVICE_HOST\", \"127.0.0.1\")\n"
            "    PORT = int(os.environ.get(\"SERVICE_PORT\", \"8000\"))\n")


def render_flask(handler_var: str, use_case_var: str) -> str:
    """Emit a Flask app block routing POST / to the inbound handler."""
    return (
        "from flask import Flask, request, jsonify\n"
        "app = Flask(__name__)\n\n"
        "def _route() -> object:\n"
        "    payload = request.get_json(silent=True) or {}\n"
        f"    result = {handler_var}.handle(payload)\n"
        "    return jsonify(result)\n\n"
        "app.add_url_rule(\"/\", \"root\", _route, methods=[\"POST\"])\n\n"
        + _entry_header()
        + "    app.run(host=HOST, port=PORT)\n"
    )


def render_kafka_consumer_loop(consumer_var: str, use_case_var: str) -> str:
    """Emit a polling consume loop with KeyboardInterrupt-graceful shutdown."""
    return (
        _entry_header()
        + "    try:\n"
        "        while True:\n"
        f"            msg = {consumer_var}.poll_one(1.0)\n"
        "            if msg is None:\n"
        "                continue\n"
        f"            {use_case_var}.execute(msg)\n"
        "    except KeyboardInterrupt:\n"
        "        pass\n"
    )


def render_grpc_server(handler_var: str) -> str:
    """Emit a minimal grpc.server bootstrap that delegates to the handler."""
    return (
        "import grpc\n"
        "from concurrent import futures\n\n"
        + _entry_header()
        + "    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))\n"
        f"    server.add_insecure_port(f\"{{HOST}}:{{PORT}}\")\n"
        f"    {handler_var}.serve(server)\n"
        "    server.start()\n"
        "    server.wait_for_termination()\n"
    )


def render_default() -> str:
    """Emit a no-runtime skeleton so the file is still executable Python."""
    return (
        'if __name__ == "__main__":\n'
        "    # TODO: no inbound entry point detected by WiringGenerator.\n"
        "    pass\n"
    )


def render_runtime(
    rest_var: str | None,
    kafka_var: str | None,
    grpc_var: str | None,
    use_case_var: str,
) -> str:
    """Pick the right runtime block based on which inbound adapter exists."""
    if rest_var is not None:
        return render_flask(rest_var, use_case_var)
    if kafka_var is not None:
        return render_kafka_consumer_loop(kafka_var, use_case_var)
    if grpc_var is not None:
        return render_grpc_server(grpc_var)
    return render_default()
