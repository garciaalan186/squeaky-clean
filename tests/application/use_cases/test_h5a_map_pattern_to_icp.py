"""H5a routing tests for MapPatternToEmitter and infrastructure_category_inference.

Adds coverage for relational_db, document_db, message_queue_producer,
message_queue_consumer, and stream_processor categories.
"""

from squeaky_clean.application.generation.emission.map_pattern_to_emitter import MapPatternToEmitter
from squeaky_clean.application.generation.techspec.infrastructure_category_inference import (
    infer_category,
)
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_PY = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)


def test_relational_db_routes_when_save_find_by_id_present() -> None:
    icp = MapPatternToEmitter().map_with_layer(
        "Repository", _PY, LayerType.INFRASTRUCTURE,
        ("save", "find_by_id"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/RelationalDBRepositoryEmitter"


def test_document_db_routes_when_upsert_present() -> None:
    icp = MapPatternToEmitter().map_with_layer(
        "Repository", _PY, LayerType.INFRASTRUCTURE,
        ("upsert", "find_by_id"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/DocumentDBRepositoryEmitter"


def test_mq_producer_routes_when_publish_present() -> None:
    icp = MapPatternToEmitter().map_with_layer(
        "Gateway", _PY, LayerType.INFRASTRUCTURE,
        ("publish", "flush"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/MessageQueueProducerEmitter"


def test_mq_consumer_routes_when_consume_present() -> None:
    icp = MapPatternToEmitter().map_with_layer(
        "Gateway", _PY, LayerType.INFRASTRUCTURE,
        ("consume", "close"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/MessageQueueConsumerEmitter"


def test_mq_consumer_routes_when_poll_one_present() -> None:
    icp = MapPatternToEmitter().map_with_layer(
        "Gateway", _PY, LayerType.INFRASTRUCTURE,
        ("poll_one", "commit"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/MessageQueueConsumerEmitter"


def test_stream_processor_routes_when_process_aggregate_present() -> None:
    icp = MapPatternToEmitter().map_with_layer(
        "Gateway", _PY, LayerType.INFRASTRUCTURE,
        ("process", "aggregate"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/StreamProcessorEmitter"


def test_h5a_categories_fall_back_when_manual() -> None:
    icp = MapPatternToEmitter().map_with_layer(
        "Repository", _PY, LayerType.INFRASTRUCTURE,
        ("save", "find_by_id"),
        infrastructure_mode="manual",
    )
    assert icp == "python/ddd_clean/RepositoryEmitter"


def test_blob_storage_still_wins_over_rdb_for_blob_methods() -> None:
    """Order-sensitivity: blob verbs are preferred to generic save/find."""
    icp = MapPatternToEmitter().map_with_layer(
        "Repository", _PY, LayerType.INFRASTRUCTURE,
        ("put_blob", "get_blob", "save"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/BlobStorageAdapterEmitter"


def test_infer_category_returns_none_for_unknown_methods() -> None:
    assert infer_category(("frobnicate", "wibble")) is None


def test_infer_category_consume_beats_relational_db_save() -> None:
    """A class with both consume and save should prefer mq_consumer."""
    assert infer_category(("consume", "save")) == "message_queue_consumer"
