"""Memory system data models."""

from .api import (
    CreateMemoryFromMessagePairRequest,
    CreateMemoryRequest,
    MemoryStatsResponse,
    ProcessingResponse,
    SearchRequest,
    SearchResponse,
)
from .core import (
    Entity,
    ImportanceLevel,
    Memory,
    MemoryType,
    ProcessingResult,
    Relationship,
    RelationshipStrength,
    RelationshipType,
    SearchResult,
)
from .extraction import (
    ContentAnalysis,
    EntityRelationshipExtraction,
    MemoryExtraction,
    TextAnalysis,
)

__all__ = [
    # Core models
    "MemoryType",
    "Memory",
    "Entity",
    "Relationship",
    "SearchResult",
    "ProcessingResult",
    # Enums
    "ImportanceLevel",
    "RelationshipStrength",
    "RelationshipType",
    # API models
    "CreateMemoryRequest",
    "CreateMemoryFromMessagePairRequest",
    "ProcessingResponse",
    "SearchRequest",
    "SearchResponse",
    "MemoryStatsResponse",
    # Extraction models
    "TextAnalysis",
    "MemoryExtraction",
    "EntityRelationshipExtraction",
    "ContentAnalysis",
]
