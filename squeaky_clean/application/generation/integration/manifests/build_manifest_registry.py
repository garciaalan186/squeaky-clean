"""Registry: artifactId -> groupId, plus the Spring-technology set."""

from __future__ import annotations

_GROUP_IDS: dict[str, str] = {
    "spring-boot-starter-web": "org.springframework.boot",
    "spring-boot-starter": "org.springframework.boot",
    "spring-boot-starter-data-jdbc": "org.springframework.boot",
    "spring-boot-starter-data-mongodb": "org.springframework.boot",
    "spring-boot-starter-data-redis": "org.springframework.boot",
    "spring-boot-starter-data-elasticsearch": "org.springframework.boot",
    "spring-boot-starter-websocket": "org.springframework.boot",
    "spring-kafka": "org.springframework.kafka",
    "spring-web": "org.springframework",
    "spring-cloud-starter-config": "org.springframework.cloud",
    "spring-cloud-stream-binder-kafka-streams": "org.springframework.cloud",
    "jackson-databind": "com.fasterxml.jackson.core",
    "jdbi3-core": "org.jdbi",
    "lettuce-core": "io.lettuce",
    "okhttp": "com.squareup.okhttp3",
    "grpc-netty-shaded": "io.grpc",
    "grpc-okhttp": "io.grpc",
    "grpc-server-spring-boot-starter": "net.devh",
    "jakarta.websocket-api": "jakarta.websocket",
    "logback-classic": "ch.qos.logback",
    "log4j-core": "org.apache.logging.log4j",
    "elasticsearch-java": "co.elastic.clients",
    "kafka-streams": "org.apache.kafka",
    "aws-sdk-java-v2": "software.amazon.awssdk",
}

_SPRING_TECHNOLOGIES: frozenset[str] = frozenset({
    "spring_boot", "spring_kafka", "spring_data_jdbc",
    "spring_data_mongodb", "spring_data_redis",
    "spring_data_elasticsearch", "spring_websocket",
    "spring_rest_client", "spring_cloud_config",
    "spring_cloud_stream", "grpc_spring_boot",
})


def lookup_group_id(artifact_id: str) -> str | None:
    """Return the registered groupId for ``artifact_id`` or None."""
    return _GROUP_IDS.get(artifact_id)


def is_spring_tech(tech: str) -> bool:
    """Return True iff ``tech`` is a Spring-managed technology."""
    return tech in _SPRING_TECHNOLOGIES
