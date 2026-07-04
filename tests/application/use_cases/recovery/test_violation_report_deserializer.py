"""Tests for ViolationReportDeserializer (round-trips the serializer)."""

from squeaky_clean.application.dtos.recovery.architectural_violation import (
    ArchitecturalViolation,
)
from squeaky_clean.application.dtos.recovery.violation_report import ViolationReport
from squeaky_clean.application.use_cases.recovery.violation_report_deserializer import (
    ViolationReportDeserializer,
)
from squeaky_clean.application.use_cases.recovery.violation_report_serializer import (
    ViolationReportSerializer,
)

_REPORT = ViolationReport((
    ArchitecturalViolation("framework-coupling", "app.Page", "inherits X", "split"),
    ArchitecturalViolation("granularity", "God", "6 methods", "decompose"),
))


def test_serialize_then_deserialize_is_identity() -> None:
    text = ViolationReportSerializer().serialize(_REPORT)
    assert ViolationReportDeserializer().deserialize(text).violations == _REPORT.violations


def test_empty_report_round_trips() -> None:
    text = ViolationReportSerializer().serialize(ViolationReport(()))
    assert ViolationReportDeserializer().deserialize(text).violations == ()
