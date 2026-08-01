"""pattern_category_table: GoF + DDD/Clean pattern -> emitter category."""

# Full GoF + DDD/Clean catalog → category directory under emitters/<lang>/.
# Every PatternName in domain.value_objects.pattern_name has a dedicated ICP
# spec in every ACTIVE emitter language (see ACTIVE_EMITTER_LANGUAGES in
# map_pattern_to_emitter); test_pattern_emitter_resolution enforces that
# invariant on disk. SimpleClassEmitter is the ONLY fallback and is reserved
# for genuinely unrecognized pattern names — it is never a silent stand-in
# for a catalog pattern that lacks a spec.
PATTERN_CATEGORY: dict[str, str] = {
    # Creational
    "AbstractFactory": "creational",
    "Builder": "creational",
    "FactoryMethod": "creational",
    "Singleton": "creational",
    "Prototype": "creational",
    # Structural
    "Adapter": "structural",
    "Bridge": "structural",
    "Composite": "structural",
    "Decorator": "structural",
    "Facade": "structural",
    "Flyweight": "structural",
    "Proxy": "structural",
    # Behavioral
    "ChainOfResponsibility": "behavioral",
    "Command": "behavioral",
    "Interpreter": "behavioral",
    "Iterator": "behavioral",
    "Mediator": "behavioral",
    "Memento": "behavioral",
    "Observer": "behavioral",
    "State": "behavioral",
    "Strategy": "behavioral",
    "TemplateMethod": "behavioral",
    "Visitor": "behavioral",
    # DDD / Clean
    "Entity": "ddd_clean",
    "ValueObject": "ddd_clean",
    "Aggregate": "ddd_clean",
    "DomainEvent": "ddd_clean",
    "Specification": "ddd_clean",
    "Repository": "ddd_clean",
    "Gateway": "ddd_clean",
    "Presenter": "ddd_clean",
    "UseCase": "ddd_clean",
    "DTOMapper": "ddd_clean",
    "SimpleClass": "ddd_clean",
}

FALLBACK_NAME: str = "SimpleClassEmitter"
FALLBACK_CATEGORY: str = "ddd_clean"
