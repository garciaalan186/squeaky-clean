"""ViolationReportRenderer: render a ViolationReport as review markdown."""

from squeaky_clean.application.dtos.recovery.violation_report import ViolationReport


class ViolationReportRenderer:
    """Renders a ViolationReport grouped by category for human review.

    An empty report says so explicitly, so a clean architecture is
    distinguishable from a skipped analysis. Categories are sorted for
    stable output; each violation shows its target, the specifics, and the
    suggested fix.
    """

    def render(self, report: ViolationReport) -> str:
        """Return grouped markdown describing the violations."""
        if not report.violations:
            return "# Architecture violations\n\nNone found.\n"
        grouped = report.by_category()
        lines = [f"# Architecture violations ({len(report.violations)})", ""]
        for category in sorted(grouped):
            items = grouped[category]
            lines.append(f"## {category} ({len(items)})")
            lines.extend(
                f"- `{v.target}` — {v.detail}. _{v.suggestion}_" for v in items
            )
            lines.append("")
        return "\n".join(lines) + "\n"
