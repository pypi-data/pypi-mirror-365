"""
JSON schema definitions for AI service
Universal schemas for any type of content processing
"""

# JSON schemas for various data structures used in the memory system

SCHEMAS = {
    "text_analysis": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "topics": {"type": "array", "items": {"type": "string"}},
            "key_concepts": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["title", "summary", "topics"],
    },
    "memory_extraction": {
        "type": "object",
        "properties": {
            "memories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of salient memory facts extracted from conversation",
            },
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "extraction_context": {"type": "string"},
        },
        "required": ["memories"],
    },
    "entity_relationship_extraction": {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                        },
                        "importance": {
                            "type": "string",
                            "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                        },
                        "context": {"type": "string"},
                    },
                    "required": ["name", "type", "description", "confidence"],
                },
            },
            "relationships": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "type": {"type": "string"},
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                        },
                        "strength": {
                            "type": "string",
                            "enum": ["WEAK", "MODERATE", "STRONG", "ESSENTIAL"],
                        },
                        "context": {"type": "string"},
                    },
                    "required": ["source", "target", "type", "confidence"],
                },
            },
        },
        "required": ["entities", "relationships"],
    },
    "content_analysis": {
        "type": "object",
        "properties": {
            "content_type": {"type": "string"},
            "main_themes": {"type": "array", "items": {"type": "string"}},
            "key_insights": {"type": "array", "items": {"type": "string"}},
            "actionable_items": {"type": "array", "items": {"type": "string"}},
            "metadata": {
                "type": "object",
                "properties": {
                    "complexity": {
                        "type": "string",
                        "enum": ["SIMPLE", "MODERATE", "COMPLEX", "EXPERT"],
                    },
                    "domain": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"],
                    },
                },
            },
        },
        "required": ["content_type", "main_themes"],
    },
}
