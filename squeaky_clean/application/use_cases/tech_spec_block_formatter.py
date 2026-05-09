"""TechSpecBlockFormatter: render a TechSpec into the TECH_SPEC prompt block."""

from typing import cast

from squeaky_clean.application.dtos.tech_spec import TechSpec


class TechSpecBlockFormatter:
    """Render a TechSpec as the TECH_SPEC block injected into Tier C prompts."""

    def format(self, spec: TechSpec) -> str:
        """Return the multi-line TECH_SPEC block for inclusion in user prompt."""
        types = cast(list[object], spec.imports.get("types") or [])
        primary = str(spec.imports.get("primary") or "")
        construction_code = str(spec.client_construction.get("code") or "")
        deps = cast(
            list[object], spec.client_construction.get("dependencies") or []
        )
        auth_method = str(spec.auth.get("method") or "none")
        env_vars = cast(list[object], spec.auth.get("env_vars") or [])
        lines: list[str] = [
            "TECH_SPEC",
            f"  category: {spec.category}",
            f"  technology: {spec.technology}",
            f"  version_pin: {spec.version_pin}",
            f"  language: {spec.language}",
            f"  install: {spec.install.get('manager','')}: {spec.install.get('package','')}",
            "  imports:",
            f"    primary: {primary}",
            f"    types: [{', '.join(str(t) for t in types)}]",
            "  client_construction:",
            f"    code: {construction_code}",
            f"    dependencies: [{', '.join(str(d) for d in deps)}]",
            "  primary_operations:",
        ]
        for op in spec.primary_operations:
            lines.append(f"    - name: {op.name}")
            lines.append(f"      signature: {op.signature}")
            lines.append(f"      sdk_call: {op.sdk_call}")
            lines.append(f"      error_types: [{', '.join(op.error_types)}]")
            lines.append(f"      idempotency: {op.idempotency}")
            lines.append(f"      retry_policy: {op.retry_policy}")
        lines.append("  auth:")
        lines.append(f"    method: {auth_method}")
        lines.append(
            f"    env_vars: [{', '.join(str(v) for v in env_vars)}]"
        )
        if spec.code_style_notes:
            lines.append("  code_style_notes:")
            for note in spec.code_style_notes:
                lines.append(f"    - {note}")
        return "\n".join(lines)
