# Unified Schema - One Source of Truth

## The Vision

After clean slate cleanup, we have **ONE unified schema** across the entire system:
- **Models define the schema** (Pydantic models are the source of truth)
- **No backward compatibility** adjustments or hacks
- **Strict validation** at every layer
- **Databases match models** exactly

## 📋 Single Schema Definition

### Core Models (Source of Truth)

```python
# This IS the schema - everything else derives from this
class Memory(BaseModel):
 id: str = Field(default_factory=lambda: str(uuid4()))
 content: str # Required, non-empty
 title: Optional[str] = None
 source: Optional[str] = None
 created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
 confidence: float = Field(0.8, ge=0.0, le=1.0)
 is_valid: bool = Field(True)
 vector: Optional[List[float]] = None # MUST be 768 dimensions
 category: Optional[str] = None
 tags: List[str] = Field(default_factory=list)

class Entity(BaseModel):
 id: str = Field(default_factory=lambda: str(uuid4()))
 name: str # Required
 entity_type: str # Required
 description: Optional[str] = None
 importance: ImportanceLevel = ImportanceLevel.MEDIUM
 confidence: float = Field(0.8, ge=0.0, le=1.0)
 created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Relationship(BaseModel):
 source_id: str # Required
 target_id: str # Required
 relationship_type: RelationshipType # MUST be UPPERCASE_UNDERSCORE
 confidence: float = Field(0.8, ge=0.0, le=1.0)
 is_valid: bool = Field(True)
 created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

## 🗄 Database Schema Alignment

### Qdrant Schema (Derived from Memory model)
```python
# Vector collection configuration
collection_config = {
 "vectors": VectorParams(size=768, distance=Distance.COSINE), # From Memory.vector
 "payload_schema": {
 "id": "keyword", # From Memory.id
 "content": "text", # From Memory.content
 "title": "keyword", # From Memory.title
 "source": "keyword", # From Memory.source
 "created_at": "datetime", # From Memory.created_at
 "confidence": "float", # From Memory.confidence
 "category": "keyword", # From Memory.category
 "tags": "keyword", # From Memory.tags
 "is_valid": "bool" # From Memory.is_valid
 }
}
```

### Kuzu Schema (Derived from all models)
```sql
-- Memory nodes (from Memory model)
CREATE NODE TABLE Memory(
 id STRING, -- Memory.id
 content STRING, -- Memory.content (required)
 title STRING, -- Memory.title (optional, defaults to "")
 source STRING, -- Memory.source (optional, defaults to "")
 created_at STRING, -- Memory.created_at (ISO format)
 confidence DOUBLE, -- Memory.confidence (0.0-1.0)
 is_valid BOOLEAN, -- Memory.is_valid
 PRIMARY KEY(id)
);

-- Entity nodes (from Entity model)
CREATE NODE TABLE Entity(
 id STRING, -- Entity.id
 name STRING, -- Entity.name (required)
 entity_type STRING, -- Entity.entity_type (required)
 description STRING, -- Entity.description (optional, defaults to "")
 importance STRING, -- Entity.importance (enum as string)
 confidence DOUBLE, -- Entity.confidence (0.0-1.0)
 created_at STRING, -- Entity.created_at (ISO format)
 PRIMARY KEY(id)
);

-- Relationships (from Relationship model)
-- Table names are relationship_type values (UPPERCASE_UNDERSCORE)
CREATE REL TABLE {relationship_type}(
 FROM Memory TO Memory, -- From Relationship.source_id/target_id
 confidence DOUBLE, -- Relationship.confidence
 is_valid BOOLEAN, -- Relationship.is_valid
 created_at STRING -- Relationship.created_at
);
```

## 🔄 Schema Flow (No Adjustments)

```
Pydantic Models (Source of Truth)
 ↓
 Validation
 ↓
 Qdrant Storage ← No transformation, direct mapping
 ↓
 Kuzu Storage ← No transformation, direct mapping
 ↓
 Retrieval ← No transformation, direct reconstruction
```

### Example: Memory Processing Flow
```python
# 1. Create Memory from validated data (source of truth)
memory = Memory(
 content="Docker is a containerization platform",
 vector=[0.1] * 768, # Exactly 768 dimensions
 title="Docker Overview",
 category="technology"
)

# 2. Validate against schema (no adjustments)
validator.quick_validate_memory(memory) # Pass/fail, no fixing

# 3. Store in Qdrant (direct mapping)
qdrant_payload = memory.to_qdrant_payload() # Direct conversion, no adjustments
qdrant.add_point(memory.id, memory.vector, qdrant_payload)

# 4. Store in Kuzu (direct mapping)
kuzu_props = memory.to_kuzu_node() # Direct conversion, no adjustments
kuzu.add_node("Memory", kuzu_props)

# 5. Retrieve (direct reconstruction)
retrieved_memory = Memory(**qdrant_payload, vector=vector) # Exact reconstruction
```

## 🚫 What We NO LONGER Do

### Backward Compatibility (REMOVED)
```python
# OLD WAY - Complex adjustments
def add_relationship(rel_type, props):
 # Try different sanitization approaches
 rel_type = rel_type.replace(" ", "_").replace("-", "_")

 # Dynamic type detection and conversion
 for k, v in props.items():
 if isinstance(v, str) and k == "confidence":
 props[k] = float(v) # Convert string to float
 elif k == "is_valid" and isinstance(v, str):
 props[k] = v.lower() == "true" # Convert string to bool

 # Try-catch for schema conflicts
 try:
 create_table_with_guessed_schema()
 except:
 try_different_schema()
```

### Unified Approach (NEW WAY)
```python
# NEW WAY - Direct from model
def add_relationship(relationship: Relationship):
 # Relationship model IS the schema
 # No conversion, no adjustment, no guessing

 # Validate at model level (strict)
 # relationship_type MUST be RelationshipType enum (UPPERCASE_UNDERSCORE)
 # confidence MUST be float 0.0-1.0
 # is_valid MUST be boolean

 # Direct storage (no schema conflicts possible)
 kuzu_props = relationship.to_kuzu_props() # Exact mapping
 kuzu.add_relationship(
 relationship.source_id,
 relationship.target_id,
 relationship.relationship_type,
 kuzu_props
 )
```

## Benefits of Unified Schema

### 1. Single Source of Truth
- **Pydantic models** define everything
- **Database schemas** derive from models
- **Validation rules** come from models
- **API contracts** match models exactly

### 2. Zero Schema Drift
- Models change → Everything changes automatically
- No manual database migrations
- No schema synchronization issues
- No version conflicts

### 3. Predictable Behavior
- If model validation passes → Database storage succeeds
- If model validation fails → Clear error message
- No surprises, no edge cases
- Fail fast, fail clearly

### 4. Simplified Development
- Write model once → Works everywhere
- Add field to model → Available in all layers
- Change validation → Applies system-wide
- Test model → Test entire schema

## Strict Validation Rules

### Memory Schema Rules
```python
# These are enforced at ALL levels
- content: MUST be non-empty string
- vector: MUST be exactly 768 floats OR None
- confidence: MUST be float between 0.0 and 1.0
- is_valid: MUST be boolean
- created_at: MUST be timezone-aware datetime
```

### Relationship Schema Rules
```python
# These are enforced at ALL levels
- relationship_type: MUST be RelationshipType enum (UPPERCASE_UNDERSCORE)
- source_id: MUST be non-empty string
- target_id: MUST be non-empty string
- confidence: MUST be float between 0.0 and 1.0
- is_valid: MUST be boolean
```

### Entity Schema Rules
```python
# These are enforced at ALL levels
- name: MUST be non-empty string
- entity_type: MUST be non-empty string
- importance: MUST be ImportanceLevel enum
- confidence: MUST be float between 0.0 and 1.0
```

## Implementation Strategy

### Phase 1: Clean Slate (Ready Now)
```bash
python scripts/clean_slate_cleanup.py --nuke
```
- Deletes all existing data
- Implements unified schema
- Removes backward compatibility

### Phase 2: Unified Operations (Immediate)
- All operations use Pydantic models directly
- No conversion layers or adjustments
- Strict validation at entry points
- Direct database mapping

### Phase 3: Future Development (Ongoing)
- Add new fields to models → Automatically available everywhere
- Change validation rules → Applied system-wide
- Modify relationships → Schema updates automatically

## 💡 Example Usage

### Clean Memory Creation
```python
# Define memory (this IS the schema)
memory = Memory(
 content="Kubernetes orchestrates Docker containers",
 vector=embedder.embed("Kubernetes orchestrates Docker containers"), # Always 768
 title="K8s Overview",
 category="container-orchestration",
 tags=["kubernetes", "docker", "orchestration"]
)

# Validate (pass/fail, no adjustments)
if not validator.quick_validate_memory(memory):
 raise ValueError("Invalid memory - fix the data")

# Store (direct mapping, no conversion)
await processor.store_memory(memory)
```

### Clean Relationship Creation
```python
# Define relationship (this IS the schema)
relationship = Relationship(
 source_id="k8s_entity_id",
 target_id="docker_entity_id",
 relationship_type=RelationshipType.WORKS_WITH, # Enum ensures format
 confidence=0.9,
 is_valid=True
)

# Store (direct mapping, RelationshipType ensures WORKS_WITH table)
kuzu.add_relationship(
 relationship.source_id,
 relationship.target_id,
 relationship.relationship_type.value, # "WORKS_WITH"
 relationship.to_kuzu_props()
)
```

## The Result

**One schema. No adjustments. No surprises. Just clean, predictable code that works.**

The models ARE the schema. Everything else just follows. 
