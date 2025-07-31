"""
Memory Retrieval - Search and retrieve memories using semantic search.
"""

import logging
import os
from datetime import datetime, timezone
from typing import List, Optional

from ..models import Memory, SearchResult
from ..qdrant.interface import QdrantInterface
from ..utils.embeddings import GenAIEmbedder

logger = logging.getLogger(__name__)


class MemoryRetriever:
    """
    Memory retrieval system using semantic search.

    Provides search capabilities across stored memories using:
    - Semantic similarity search via Qdrant
    - Category and tag filtering
    - Confidence-based ranking
    """

    def __init__(
        self,
        qdrant_interface: Optional[QdrantInterface] = None,
        embedder: Optional[GenAIEmbedder] = None,
    ):
        """
        Initialize the Memory Retriever.

        Args:
            qdrant_interface: Qdrant interface for vector search
            embedder: Embedding generator for query vectors
        """
        self.qdrant = qdrant_interface or QdrantInterface()
        self.embedder = embedder or GenAIEmbedder()

        logger.info("MemoryRetriever initialized")

    async def search_memories(
        self,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.7,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """
        Search for memories using semantic similarity.

        Args:
            query: Search query text
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0.0 to 1.0)
            category: Filter by category (optional)
            tags: Filter by tags (optional)

        Returns:
            List of SearchResult objects with memories and scores
        """
        try:
            logger.info(f"Searching memories for: '{query}'")

            # Generate query embedding
            query_vector = self.embedder.get_embedding(query)
            logger.debug(f"Generated query embedding: {len(query_vector)} dimensions")

            # Prepare filters
            filters = {}
            if category:
                filters["category"] = category
            if tags:
                filters["tags"] = tags  # Qdrant will handle array filtering

            # Search in Qdrant (simplified - filters not yet implemented in interface)
            search_results = self.qdrant.search_points(
                vector=query_vector,
                limit=limit,
            )

            logger.debug(f"Qdrant returned {len(search_results)} results")

            # Convert to SearchResult objects and filter by score
            results = []
            for result in search_results:
                if result.get("score", 0.0) < score_threshold:
                    continue

                # Extract memory data from payload
                payload = result.get("payload", {})

                # Skip invalid memories if temporal reasoning is enabled
                if self._should_filter_invalid_memories() and not payload.get(
                    "is_valid", True
                ):
                    logger.debug(
                        f"Filtering out invalid memory: {payload.get('content', '')[:50]}..."
                    )
                    continue

                # Reconstruct Memory object with all fields
                from ..models.core import MemoryType

                # Parse memory_type enum
                memory_type_str = payload.get("memory_type", "note")
                try:
                    memory_type = MemoryType(memory_type_str)
                except ValueError:
                    memory_type = MemoryType.NOTE  # Default fallback

                memory = Memory(
                    id=result.get("id"),  # ID is in the result, not payload
                    content=payload.get("content"),
                    memory_type=memory_type,
                    summary=payload.get("summary"),
                    ai_verified_type=payload.get("ai_verified_type", False),
                    title=payload.get("title"),
                    source=payload.get("source"),
                    tags=payload.get("tags", []),
                    confidence=payload.get("confidence", 0.8),
                    vector=None,  # Don't need full vector for display
                    is_valid=payload.get("is_valid", True),
                    created_at=datetime.fromisoformat(
                        payload.get(
                            "created_at", datetime.now(timezone.utc).isoformat()
                        )
                    ),
                    expires_at=(
                        datetime.fromisoformat(payload["expires_at"])
                        if payload.get("expires_at")
                        else None
                    ),
                    supersedes=payload.get("supersedes"),
                    superseded_by=payload.get("superseded_by"),
                )

                # Create search result
                search_result = SearchResult(
                    memory=memory,
                    score=result.get("score", 0.0),
                    source="qdrant",
                    metadata={"rank": len(results) + 1},
                )

                results.append(search_result)
                logger.debug(
                    f"Found memory: {memory.title or memory.content[:50]}... (score: {search_result.score:.3f})"
                )

            # Sort by score (highest first) and add relevance metadata
            results.sort(key=lambda x: x.score, reverse=True)

            # Add relevance categories to metadata
            for i, result in enumerate(results):
                result.metadata["rank"] = i + 1
                result.metadata["relevance_tier"] = self._get_relevance_tier(
                    result.score
                )

            logger.info(f"Retrieved {len(results)} memories for query: '{query}'")
            return results

        except Exception as e:
            raise RuntimeError(
                f"CRITICAL: Memory search failed - database connection or query error: {str(e)}"
            ) from e

    async def get_memory_by_id(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: Unique memory identifier

        Returns:
            Memory object if found, None otherwise
        """
        # Note: get_point method not implemented in current Qdrant interface
        # This would require implementing get_point in QdrantInterface
        logger.warning(
            "get_memory_by_id not yet implemented - requires Qdrant interface enhancement"
        )
        return None

    async def get_memories_by_category(
        self, category: str, limit: int = 20
    ) -> List[Memory]:
        """
        Get all memories in a specific category.

        Args:
            category: Category to filter by
            limit: Maximum number of memories to return

        Returns:
            List of Memory objects in the category
        """
        # Note: filter_points method not implemented in current Qdrant interface
        # For now, we'll do a broad search and filter results
        logger.warning(
            "get_memories_by_category using basic search - filters not yet implemented"
        )

        # Do a general search with a neutral query
        search_results = await self.search_memories(
            query=f"category {category}",
            limit=limit,
            score_threshold=0.0,  # Lower threshold for category search
        )

        # Filter results by category manually
        filtered_memories = [
            result.memory
            for result in search_results
            if result.memory.category == category
        ]

        return filtered_memories

    async def get_stats(self) -> dict:
        """
        Get memory database statistics.

        Returns:
            Dictionary with memory statistics
        """
        try:
            stats = self.qdrant.get_stats()
            return {
                "total_memories": stats.get("points", 0),
                "vector_size": stats.get(
                    "vector_size", int(os.getenv("EMBEDDING_DIMENSION_LEN", "768"))
                ),
                "status": "healthy" if stats else "error",
            }
        except Exception as e:
            raise RuntimeError(
                f"CRITICAL: Failed to get memory stats - database connection error: {str(e)}"
            ) from e

    def _should_filter_invalid_memories(self) -> bool:
        """
        Check if invalid memories should be filtered from search results.

        Returns:
            True if temporal reasoning is enabled and invalid memories should be filtered
        """
        try:
            from ..config import get_config

            config = get_config()
            return config.mem0.enable_temporal_reasoning
        except Exception:
            # Default to filtering invalid memories if config fails
            return True

    def _get_relevance_tier(self, score: float) -> str:
        """
        Categorize relevance score into tiers.

        Args:
            score: Similarity score (0.0 to 1.0)

        Returns:
            Relevance tier string
        """
        if score >= 0.9:
            return "highly_relevant"
        elif score >= 0.7:
            return "relevant"
        elif score >= 0.5:
            return "moderately_relevant"
        elif score >= 0.3:
            return "low_relevance"
        else:
            return "minimal_relevance"
