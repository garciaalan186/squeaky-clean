"""wiring_templates_go: Go composition-root main.go renderer."""

from __future__ import annotations


def render_go_main(tech_specs: dict[str, object]) -> str:
    """Emit a Go composition root ``main.go`` for Go TechSpec runtimes.

    Picks the runtime from inbound categories present in ``tech_specs``:
    rest_server_handler -> http.ListenAndServe; message_queue_consumer ->
    signal-based shutdown loop; otherwise a sleep skeleton.
    """
    rest = "rest_server_handler" in tech_specs
    consumer = "message_queue_consumer" in tech_specs
    head = ("// Auto-generated composition root (WiringGenerator).\n"
            "package main\n\nimport (\n\t\"log\"\n\t\"net/http\"\n"
            "\t\"os\"\n\t\"os/signal\"\n\t\"syscall\"\n\t\"time\"\n)\n\n")
    if rest:
        body = ("func main() {\n\taddr := os.Getenv(\"SERVICE_ADDR\")\n"
                "\tif addr == \"\" { addr = \":8080\" }\n"
                "\tlog.Printf(\"listening on %s\", addr)\n"
                "\tif err := http.ListenAndServe(addr, nil); err != nil "
                "{ log.Fatal(err) }\n}\n")
    elif consumer:
        body = ("func main() {\n\tsigs := make(chan os.Signal, 1)\n"
                "\tsignal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)\n"
                "\tlog.Println(\"consumer started\")\n"
                "\tfor {\n\t\tselect {\n\t\tcase <-sigs:\n"
                "\t\t\tlog.Println(\"shutting down\"); return\n"
                "\t\tdefault: time.Sleep(100 * time.Millisecond)\n"
                "\t\t}\n\t}\n}\n")
    else:
        body = ("func main() {\n\tlog.Println(\"service ready\")\n"
                "\tfor { time.Sleep(time.Second) }\n}\n")
    return head + body
