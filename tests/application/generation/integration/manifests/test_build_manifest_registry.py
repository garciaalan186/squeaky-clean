"""Tests for build_manifest_registry: groupId lookups + Spring-tech set."""

from squeaky_clean.application.generation.integration.manifests.build_manifest_registry import (
    is_spring_tech,
    lookup_group_id,
)


def test_lookup_group_id_returns_registered_group() -> None:
    assert lookup_group_id("spring-kafka") == "org.springframework.kafka"
    assert lookup_group_id("okhttp") == "com.squareup.okhttp3"


def test_lookup_group_id_returns_none_for_unregistered_artifact() -> None:
    assert lookup_group_id("no-such-artifact") is None


def test_is_spring_tech_accepts_spring_managed_technologies() -> None:
    assert is_spring_tech("spring_boot")
    assert is_spring_tech("grpc_spring_boot")


def test_is_spring_tech_rejects_non_spring_technologies() -> None:
    assert not is_spring_tech("kafka_streams")
    assert not is_spring_tech("")
