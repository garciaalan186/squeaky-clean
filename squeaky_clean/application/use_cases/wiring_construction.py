"""wiring_construction: per-class construction-line emitters."""

from __future__ import annotations

from typing import cast

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.use_cases.snake_case_converter import SnakeCaseConverter
from squeaky_clean.application.use_cases.wiring_walker import (
    category_for,
    env_args_for,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec

_SNAKE: SnakeCaseConverter = SnakeCaseConverter()


def _ctor_args_inbound(
    cls: ClassSpec, spec: TechSpec | None, symbol_vars: dict[str, str],
) -> str:
    """Build ctor args for an inbound adapter: deps first, then env_vars."""
    parts: list[str] = [symbol_vars[d] for d in cls.depends
                        if d in symbol_vars]
    if spec is None:
        return ", ".join(parts) if parts else env_args_for(spec)
    deps_raw = cast(list[str],
                    spec.client_construction.get("dependencies") or [])
    for d in deps_raw:
        if d == "use_case":
            continue
        parts.append(f'os.environ.get("{d.upper()}", "")')
    return ", ".join(parts) if parts else '""'


def emit_outbound(
    cls: ClassSpec, tech_specs: dict[str, TechSpec],
    symbol_vars: dict[str, str],
) -> str:
    """Append outbound adapter ctor call (env-only deps) and update symbols."""
    var = _SNAKE.convert(cls.name)
    symbol_vars[cls.name] = var
    spec = tech_specs.get(category_for(cls))
    return f"{var} = {cls.name}({env_args_for(spec)})"


def emit_use_case(
    cls: ClassSpec, symbol_vars: dict[str, str],
) -> str:
    """Append use_case ctor call wired to outbound adapters."""
    var = _SNAKE.convert(cls.name)
    symbol_vars[cls.name] = var
    deps = [symbol_vars[d] for d in cls.depends if d in symbol_vars]
    return f"{var} = {cls.name}({', '.join(deps)})"


def emit_inbound(
    cls: ClassSpec, tech_specs: dict[str, TechSpec],
    symbol_vars: dict[str, str],
) -> str:
    """Append inbound adapter ctor call (deps + env vars)."""
    var = _SNAKE.convert(cls.name)
    symbol_vars[cls.name] = var
    spec = tech_specs.get(category_for(cls))
    args = _ctor_args_inbound(cls, spec, symbol_vars)
    return f"{var} = {cls.name}({args})"
