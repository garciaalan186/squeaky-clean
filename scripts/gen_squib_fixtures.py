"""Generate golden-Squib fixtures — one per benchmark-uncovered pattern.

Each fixture is a minimal but realistic §Notation (Squib) whose focal class
demands a specific GoF/DDD pattern, so the pipeline's pattern->ICP routing can
be validated deterministically (and each fixture is runnable via --squib-file).
Writes eval/squib_fixtures/*.squib + manifest.json.
"""

from __future__ import annotations

import json
from pathlib import Path

_OUT = Path(__file__).resolve().parents[1] / "eval" / "squib_fixtures"

# pattern -> (category, module, layer, focal_class, class_block_lines)
# class_block_lines: the body of the focal class (methods/fields/concretes/...).
_F: dict[str, tuple[str, str, str, str, list[str]]] = {
    # ---- Creational ----
    "AbstractFactory": ("creational", "Theming", "Domain", "WidgetFactory", [
        "methods: [create_button(): Button, create_checkbox(): Checkbox]",
        "concretes: [DarkWidgetFactory, LightWidgetFactory]"]),
    "Builder": ("creational", "Reporting", "Application", "ReportBuilder", [
        "methods: [with_title(title: str): ReportBuilder, build(): Report]"]),
    "FactoryMethod": ("creational", "Documents", "Application", "DocumentCreator", [
        "methods: [create_document(): Document]",
        "concretes: [PdfCreator, HtmlCreator]"]),
    "Singleton": ("creational", "Configuration", "Infrastructure", "AppConfig", [
        "fields: [values: str]", "methods: [get(key: str): str]"]),
    "Prototype": ("creational", "Shapes", "Domain", "Shape", [
        "fields: [color: str]", "methods: [clone(): Shape]"]),
    # ---- Structural ----
    "Adapter": ("structural", "Payments", "Infrastructure", "StripeAdapter", [
        "implements: PaymentPort",
        "methods: [charge(amount: Money): Result]", "depends: [StripeSdk]"]),
    "Bridge": ("structural", "Rendering", "Domain", "Shape", [
        "methods: [draw(): void]", "depends: [Renderer]"]),
    "Composite": ("structural", "Filesystem", "Domain", "Directory", [
        "fields: [children: Node]",
        "methods: [size(): int, add(child: Node): void]"]),
    "Decorator": ("structural", "Streams", "Domain", "CompressingStream", [
        "implements: DataStream",
        "methods: [write(data: str): void]", "depends: [DataStream]"]),
    "Facade": ("structural", "Ordering", "Application", "OrderFacade", [
        "methods: [place_order(command: OrderCommand): Result]",
        "depends: [Inventory, Billing]"]),
    "Flyweight": ("structural", "Text", "Domain", "Glyph", [
        "fields: [symbol: str]", "methods: [render(position: int): void]"]),
    "Proxy": ("structural", "Images", "Domain", "ImageProxy", [
        "implements: Image",
        "methods: [display(): void]", "depends: [RealImage]"]),
    # ---- Behavioral ----
    "ChainOfResponsibility": ("behavioral", "Support", "Domain", "TicketHandler", [
        "methods: [handle(ticket: Ticket): Result]",
        "concretes: [Tier1Handler, Tier2Handler]"]),
    "Command": ("behavioral", "Editor", "Application", "EditCommand", [
        "methods: [execute(): void]",
        "concretes: [InsertCommand, DeleteCommand]"]),
    "Interpreter": ("behavioral", "Expressions", "Domain", "Expression", [
        "methods: [interpret(context: Context): int]",
        "concretes: [NumberExpr, AddExpr]"]),
    "Iterator": ("behavioral", "History", "Domain", "HistoryIterator", [
        "fields: [items: Event]",
        "methods: [next(): Event, has_next(): bool]"]),
    "Mediator": ("behavioral", "ChatRoom", "Application", "ChatMediator", [
        "methods: [notify(sender: str, event: str): void]", "depends: [Member]"]),
    "Memento": ("behavioral", "TextEditor", "Domain", "EditorMemento", [
        "fields: [content: str]", "methods: [content(): str]"]),
    "Observer": ("behavioral", "Notifications", "Domain", "EventObserver", [
        "methods: [update(event: Event): void]",
        "concretes: [EmailObserver, SmsObserver]"]),
    "State": ("behavioral", "OrderLifecycle", "Domain", "OrderState", [
        "methods: [next(order: Order): OrderState]",
        "concretes: [PendingState, ShippedState]"]),
    "TemplateMethod": ("behavioral", "Imports", "Application", "DataImporter", [
        "methods: [import_records(raw: str): Record]",
        "concretes: [CsvImporter, JsonImporter]"]),
    "Visitor": ("behavioral", "Ast", "Domain", "NodeVisitor", [
        "methods: [visit_number(node: NumberNode): int, "
        "visit_add(node: AddNode): int]",
        "concretes: [EvalVisitor]"]),
    # ---- DDD / Clean ----
    "Aggregate": ("ddd_clean", "Orders", "Domain", "Order", [
        "fields: [id: str, lines: OrderLine]",
        "methods: [add_line(line: OrderLine): void, total(): Money]",
        'invariants: ["order total must be non-negative"]']),
    "DomainEvent": ("ddd_clean", "OrderEvents", "Domain", "OrderPlaced", [
        "fields: [order_id: str, occurred_on: str]"]),
    "Specification": ("ddd_clean", "Catalog", "Domain", "InStockSpec", [
        "methods: [is_satisfied_by(product: Product): bool]"]),
    "Gateway": ("ddd_clean", "PaymentPort", "Domain", "PaymentGateway", [
        "methods: [charge(amount: Money): Result]"]),
    "Presenter": ("ddd_clean", "OrderView", "Interface", "OrderPresenter", [
        "methods: [present(order: Order): OrderViewModel]"]),
    "DTOMapper": ("ddd_clean", "UserApi", "Application", "UserMapper", [
        "methods: [to_dto(user: User): UserDto, to_domain(dto: UserDto): User]"]),
}


def _render(pattern: str, module: str, layer: str, focal: str,
            body: list[str]) -> str:
    inner = "\n".join(f"    {line}" for line in body)
    return (
        f"MODULE {module}\n"
        f"LAYER {layer}\n"
        f"EXPORTS [{focal}]\n"
        f"DEPENDS []\n"
        f"CLASSES {{\n"
        f"  {focal} -> {pattern} {{\n"
        f"{inner}\n"
        f"  }}\n"
        f"}}\n"
    )


def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict[str, str]] = {}
    for pattern, (category, module, layer, focal, body) in sorted(_F.items()):
        stem = "".join(f"_{c.lower()}" if c.isupper() else c
                       for c in pattern).lstrip("_")
        fname = f"{stem}.squib"
        (_OUT / fname).write_text(_render(pattern, module, layer, focal, body))
        manifest[pattern] = {
            "file": fname, "focal": focal, "category": category,
        }
    (_OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {len(manifest)} fixtures + manifest.json to {_OUT}")


if __name__ == "__main__":
    main()
