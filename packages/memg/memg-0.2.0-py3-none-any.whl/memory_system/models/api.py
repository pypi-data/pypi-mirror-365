"""API request and response models"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .core import MemoryType, SearchResult


class CreateMemoryRequest(BaseModel):
    """Simplified request model for creating memories (document or note)"""

    content: str = Field(..., description="Memory content")
    memory_type: Optional[MemoryType] = Field(
        None, description="Type of memory (auto-detected if not provided)"
    )
    title: Optional[str] = Field(None, description="Optional title")
    source: str = Field("user", description="Source of memory")
    tags: List[str] = Field(default_factory=list, description="Optional tags")
    confidence: float = Field(0.8, ge=0.0, le=1.0, description="Storage confidence")


class ProcessingResponse(BaseModel):
    """Response for memory processing operations"""

    success: bool = Field(..., description="Whether operation succeeded")
    memory_id: str = Field(..., description="ID of created/updated memory")
    final_type: MemoryType = Field(
        ..., description="Final memory type after AI processing"
    )
    ai_verified: bool = Field(..., description="Whether AI verified the type")
    summary_generated: bool = Field(
        default=False, description="Whether AI summary was generated"
    )
    processing_time_ms: float = Field(
        default=0.0, description="Processing time in milliseconds"
    )

    # Optional details
    type_changed: bool = Field(
        default=False, description="Whether type was auto-corrected"
    )
    original_type: Optional[MemoryType] = Field(
        None, description="Original type if changed"
    )
    word_count: int = Field(default=0, description="Content word count")


class SearchRequest(BaseModel):
    """Request model for searching memories"""

    query: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum results to return")
    memory_types: List[MemoryType] = Field(
        default_factory=lambda: [MemoryType.DOCUMENT, MemoryType.NOTE],
        description="Types to search",
    )
    include_invalid: bool = Field(
        False, description="Include superseded/invalid memories"
    )
    score_threshold: float = Field(
        0.3, ge=0.0, le=1.0, description="Minimum similarity score"
    )
    tags: List[str] = Field(default_factory=list, description="Filter by tags")


class SearchResponse(BaseModel):
    """Response model for search results"""

    query: str = Field(..., description="Original search query")
    total_results: int = Field(0, description="Total number of results found")
    documents_count: int = Field(0, description="Number of document results")
    notes_count: int = Field(0, description="Number of note results")
    search_time_ms: float = Field(
        default=0.0, description="Search time in milliseconds"
    )
    results: List[SearchResult] = Field(
        default_factory=list, description="Search results"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class MemoryStatsResponse(BaseModel):
    """System statistics response"""

    total_memories: int = Field(0, description="Total memories stored")
    documents_count: int = Field(0, description="Number of documents")
    notes_count: int = Field(0, description="Number of notes")
    valid_memories: int = Field(0, description="Number of valid memories")
    superseded_memories: int = Field(0, description="Number of superseded memories")
    avg_document_words: float = Field(0.0, description="Average document word count")
    avg_note_words: float = Field(0.0, description="Average note word count")

    # Storage stats
    vector_dimension: int = Field(768, description="Vector embedding dimension")
    total_storage_mb: float = Field(0.0, description="Approximate storage usage in MB")


# Legacy support - simplified versions of complex requests
class CreateMemoryFromMessagePairRequest(BaseModel):
    """Legacy support - converts to CreateMemoryRequest with conversation type"""

    current_message: str = Field(..., description="Current message content")
    previous_message: Optional[str] = Field(
        None, description="Previous message content"
    )
    speaker: Optional[str] = Field(None, description="Current message speaker")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")
    source: str = Field("conversation", description="Memory source")
    tags: List[str] = Field(default_factory=list)

    def to_create_request(self) -> CreateMemoryRequest:
        """Convert to standard CreateMemoryRequest"""
        # Combine messages into single content
        content_parts = []
        if self.previous_message:
            content_parts.append(f"Previous: {self.previous_message}")
        content_parts.append(f"Current: {self.current_message}")

        content = "\n".join(content_parts)

        return CreateMemoryRequest(
            content=content,
            memory_type=MemoryType.CONVERSATION,
            source=self.source,
            tags=(
                self.tags + [f"conversation:{self.conversation_id}"]
                if self.conversation_id
                else self.tags
            ),
        )
