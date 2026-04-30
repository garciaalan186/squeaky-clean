# Role: EventSourcedAggregateICP (Python — example custom pattern)

## Identity
Example externally-supplied ICP demonstrating F4's custom-pattern hook.

## Model Tier
ICP

## Pattern Knowledge
Event-sourced aggregate: state derived from a sequence of events.
Methods produce events; events apply via `_apply` to mutate state.

## Output Contract
A single Python file: a class with `events: list[<EventType>]` field, an
`apply(event)` method, and one or more command methods that produce events.
Use `from dataclasses import dataclass, field`.
