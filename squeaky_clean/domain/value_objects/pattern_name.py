"""PatternName: literal type listing every recognized GoF/DDD pattern."""

from typing import Literal, get_args

PatternName = Literal[
    "AbstractFactory",
    "Builder",
    "FactoryMethod",
    "Singleton",
    "Prototype",
    "Adapter",
    "Bridge",
    "Composite",
    "Decorator",
    "Facade",
    "Flyweight",
    "Proxy",
    "ChainOfResponsibility",
    "Command",
    "Interpreter",
    "Iterator",
    "Mediator",
    "Memento",
    "Observer",
    "State",
    "Strategy",
    "TemplateMethod",
    "Visitor",
    "Entity",
    "ValueObject",
    "Aggregate",
    "DomainEvent",
    "Specification",
    "Repository",
    "Gateway",
    "Presenter",
    "UseCase",
    "DTOMapper",
    "SimpleClass",
]

ALL_PATTERNS: frozenset[PatternName] = frozenset(get_args(PatternName))
