# Schema Validation System

## Overview

The Schema Validation System is a **non-invasive** validation layer that helps prevent schema-related issues in the memory processing pipeline. It validates data at multiple levels without modifying any existing committed code.

## Key Features

 **Non-Invasive**: No modification of existing working code
 **Comprehensive**: Validates AI outputs, model conversions, and database compatibility
 **Multi-Level**: Pydantic validation + custom schema validation
 **Database-Aware**: Checks Qdrant and Kuzu compatibility
 **Early Detection**: Catches issues before they cause runtime errors

## Architecture

```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ AI Output │ │ Pydantic │ │ Database │
│ Validation │ -> │ Model │ -> │ Compatibility │
│ │ │ Validation │ │ Validation │
└─────────────────┘ └─────────────────┘ └─────────────────┘
 │ │ │
 v v v
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ • Schema match │ │ • Required │ │ • Vector dims │
│ • Required │ │ fields │ │ • SQL safety │
│ • field types │ │ • Type safety │ │ • JSON compat │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Components

### 1. SchemaValidator
Core validator that checks:
- AI outputs against JSON schemas
- Model field types and requirements
- Database compatibility (Qdrant/Kuzu)
- Relationship schema safety

### 2. PipelineValidator
End-to-end pipeline validation:
- Complete flow validation
- Cross-component consistency
- Memory creation workflows

### 3. StandaloneValidator
Easy-to-use interface:
- Quick validation methods
- Convenience functions
- Non-invasive integration

## Usage Examples

### Quick Memory Validation

```python
from memory_system.validation import create_validator

validator = create_validator()

# Quick check of a Memory object
memory = Memory(content="Test", vector=[0.1] * 768)
is_valid = validator.quick_validate_memory(memory)
```

### AI Output Validation

```python
# Validate AI-generated content analysis
ai_output = {
 "content_type": "text",
 "main_themes": ["technology"],
 "key_insights": ["AI is important"],
 "actionable_items": ["Learn more"]
}

report = validator.validate_ai_outputs(
 content_analysis_output=ai_output,
 memory_extraction_output={"memories": ["test"], "summary": "test"}
)

if not report.pipeline_valid:
 print(f"Found {report.error_count} errors")
```

### Complete Flow Validation

```python
# Validate entire memory processing flow
report = validator.validate_complete_flow(
 original_content="Input text",
 ai_content_analysis=ai_analysis_output,
 ai_memory_extraction=ai_extraction_output,
 final_memories=memory_objects
)

validator.print_report(report)
```

## Validation Levels

### 1. Pydantic Validation (First Line)
- Automatic field validation
- Type checking
- Required field enforcement
- Custom validators (e.g., non-empty content)

### 2. Schema Validation (Second Line)
- AI output schema compliance
- JSON schema validation
- Field type consistency
- Array structure validation

### 3. Database Compatibility (Third Line)
- Vector dimension validation (768 for Google embeddings)
- Qdrant payload JSON compatibility
- Kuzu node property types
- Relationship schema safety

### 4. Cross-Component Validation (Fourth Line)
- Memory count consistency
- Content preservation
- End-to-end flow integrity

## Common Validation Checks

### Memory Objects
- Content not empty
- Vector has 768 dimensions (Google embeddings)
- Vector contains only numbers
- All fields JSON serializable

### AI Outputs
- Required fields present
- Field types match schema
- Array items have correct types
- No missing critical data

### Relationships
- Relationship type is SQL-safe (no spaces/special chars)
- Property types match Kuzu expectations
- Confidence is numeric (0.0-1.0)
- Boolean fields are actual booleans

## Integration Patterns

### 1. Development Validation
```python
# During development - validate everything
if __name__ == "__main__":
 validator = create_validator()
 # ... validate your data
```

### 2. Selective Validation
```python
# Only validate critical paths
if memory.vector is None:
 is_valid = validator.quick_validate_memory(memory)
 if not is_valid:
 # Handle invalid memory
```

### 3. Pre-Storage Validation
```python
# Before storing in databases
def store_memories(memories):
 report = validator.validate_memory_objects(memories)
 if not report.pipeline_valid:
 raise ValueError(f"Invalid memories: {report.error_count} errors")

 # Proceed with storage
```

## Benefits

### For Development
- 🐛 **Early Bug Detection**: Catch schema issues during development
- **Clear Error Messages**: Understand exactly what's wrong
- **Comprehensive Reports**: See all issues at once

### For Production
- 🛡 **Data Integrity**: Ensure all data meets requirements
- **Performance**: Avoid runtime failures from bad data
- 📈 **Reliability**: Consistent data quality

### For Maintenance
- **Non-Invasive**: No changes to existing code
- 📝 **Documentation**: Clear validation requirements
- **Targeted**: Focus validation where needed

## Example Demo

Run the validation demo to see it in action:

```bash
cd /path/to/project
python examples/simple_validation_demo.py
```

This demonstrates:
- Memory object validation
- AI output validation
- Database compatibility checks
- Vector dimension validation

## Error Types

### ValidationLevel.ERROR
- Missing required fields
- Wrong data types
- Invalid vector dimensions
- Non-JSON serializable data

### ValidationLevel.WARNING
- Suboptimal but valid data
- Performance concerns
- Potential compatibility issues

### ValidationLevel.CRITICAL
- System-breaking issues
- Complete validation failures

## Best Practices

1. **Use Early**: Validate as soon as data is created
2. **Be Selective**: Don't over-validate in performance-critical paths
3. **Handle Gracefully**: Use validation results to improve data quality
4. **Monitor**: Track validation failures to improve AI outputs
5. **Document**: Share validation requirements with the team

## Files Structure

```
src/memory_system/validation/
├── __init__.py # Main exports
├── schema_validator.py # Core schema validation
├── pipeline_validator.py # Pipeline validation
└── standalone_validator.py # Easy-to-use interface

tests/
└── test_validation.py # Comprehensive tests

examples/
├── simple_validation_demo.py # Simple demo
└── validation_demo.py # Detailed demo
```

## Future Enhancements

- [ ] Custom validation rules
- [ ] Performance optimization
- [ ] More database types
- [ ] Automated fixing suggestions
- [ ] Integration with logging systems
