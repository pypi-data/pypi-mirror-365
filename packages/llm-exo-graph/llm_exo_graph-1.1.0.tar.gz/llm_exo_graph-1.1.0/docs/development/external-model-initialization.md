# External Model Initialization Pattern

## Overview

The Knowledge Graph Engine v2.2.0 introduces a new initialization pattern where **embedder and cross-encoder models are initialized externally** and passed as parameters. This provides better control, resource management, and eliminates internal fallbacks.

## Motivation

### Previous Issues
- **Hidden Dependencies**: Models were initialized internally with fallbacks
- **Resource Duplication**: Multiple instances of the same model could be created
- **Poor Error Handling**: Fallbacks masked initialization failures
- **Limited Control**: No way to configure model parameters externally

### New Benefits
- **Explicit Dependencies**: All required models must be provided
- **Resource Efficiency**: Single model instances shared across components
- **Clear Error Handling**: Initialization failures are immediately visible
- **Full Control**: External configuration of all model parameters

## Updated API

### VectorStore Changes

**Before (v2.1.0):**
```python
# Old: model_name parameter with internal initialization
vector_store = VectorStore(
    model_name="all-MiniLM-L6-v2",
    neo4j_config=config
)
```

**After (v2.2.0):**
```python
# New: mandatory embedder parameter
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer('all-MiniLM-L6-v2')
vector_store = VectorStore(
    embedder=embedder,
    neo4j_config=config
)
```

### ClassifierDetector Changes

**Before (v2.1.0):**
```python
# Old: internal cross-encoder initialization
detector = ClassifierDetector(
    classifier_map, 
    embedder=embedder,
    use_cross_encoder=True,
    use_hybrid=True
)
```

**After (v2.2.0):**
```python
# New: external cross-encoder initialization
from sentence_transformers import SentenceTransformer, CrossEncoder

embedder = SentenceTransformer('all-MiniLM-L6-v2')
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Hybrid approach (recommended)
detector = ClassifierDetector(
    classifier_map, 
    embedder=embedder,
    cross_encoder=cross_encoder,
    use_hybrid=True
)

# Bi-encoder only
detector = ClassifierDetector(
    classifier_map, 
    embedder=embedder
)
```

## Migration Guide

### Step 1: Update VectorStore Initialization

```python
# Old code:
vector_store = VectorStore(model_name="all-MiniLM-L6-v2")

# New code:
from sentence_transformers import SentenceTransformer
embedder = SentenceTransformer('all-MiniLM-L6-v2')
vector_store = VectorStore(embedder=embedder)
```

### Step 2: Update ClassifierDetector Initialization

```python
# Old code:
detector = ClassifierDetector(classifier_map, embedder, use_cross_encoder=True)

# New code:
from sentence_transformers import CrossEncoder
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
detector = ClassifierDetector(classifier_map, embedder, cross_encoder=cross_encoder)
```

### Step 3: Update Test and Example Files

All test files and examples need to be updated to use external model initialization. See the updated test files for reference patterns.

## Best Practices

### Model Sharing

Share model instances across components to save memory:

```python
# Initialize models once
embedder = SentenceTransformer('all-MiniLM-L6-v2')
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Share across components
vector_store = VectorStore(embedder=embedder)
detector = ClassifierDetector(classifier_map, embedder, cross_encoder=cross_encoder)
```

### Error Handling

Handle model initialization failures explicitly:

```python
try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    logger.error(f"Failed to initialize embedder: {e}")
    raise

try:
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
except Exception as e:
    logger.warning(f"Cross-encoder unavailable: {e}")
    cross_encoder = None

# Use bi-encoder only if cross-encoder fails
detector = ClassifierDetector(classifier_map, embedder, cross_encoder=cross_encoder)
```

### Configuration Options

Configure models externally for different use cases:

```python
# Fast, lightweight setup
embedder = SentenceTransformer('all-MiniLM-L6-v2')
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-2-v2')  # Smaller model

# High accuracy setup
embedder = SentenceTransformer('all-mpnet-base-v2')
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')  # Larger model

# Production setup with caching
embedder = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/opt/models')
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', cache_folder='/opt/models')
```

## Initialization Patterns

### Basic Pattern

```python
from sentence_transformers import SentenceTransformer, CrossEncoder
from exo_graph.models.classifier_map import ClassifierMap
from exo_graph.utils.graph_standardizer import GraphStandardizer
from exo_graph.storage.vector_store import VectorStore

# Initialize models
embedder = SentenceTransformer('all-MiniLM-L6-v2')
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Initialize components
vector_store = VectorStore(embedder=embedder, neo4j_config=config)
detector = GraphStandardizer(classifier_map, embedder, cross_encoder=cross_encoder)
```

### Production Pattern with Error Handling

```python
import logging
from sentence_transformers import SentenceTransformer, CrossEncoder

logger = logging.getLogger(__name__)

def initialize_models():
    """Initialize models with proper error handling."""
    # Initialize embedder (mandatory)
    try:
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedder initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize embedder: {e}")
        raise
    
    # Initialize cross-encoder (optional)
    try:
        cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
        logger.info("Cross-encoder initialized successfully")
    except Exception as e:
        logger.warning(f"Cross-encoder initialization failed: {e}")
        cross_encoder = None
    
    return embedder, cross_encoder

def initialize_kg_components(embedder, cross_encoder, classifier_map, neo4j_config):
    """Initialize KG components with models."""
    vector_store = VectorStore(embedder=embedder, neo4j_config=neo4j_config)
    
    # Use hybrid if cross-encoder available, otherwise bi-encoder only
    detector = ClassifierDetector(
        classifier_map, 
        embedder, 
        cross_encoder=cross_encoder,
        use_hybrid=cross_encoder is not None
    )
    
    return vector_store, detector
```

### Testing Pattern

```python
import pytest
from sentence_transformers import SentenceTransformer, CrossEncoder

@pytest.fixture
def embedder():
    """Shared embedder fixture for tests."""
    return SentenceTransformer('all-MiniLM-L6-v2')

@pytest.fixture
def cross_encoder():
    """Shared cross-encoder fixture for tests."""
    try:
        return CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    except Exception:
        return None

def test_classifier_detector(classifier_map, embedder, cross_encoder):
    """Test classifier detector with external models."""
    detector = ClassifierDetector(classifier_map, embedder, cross_encoder=cross_encoder)
    assert detector.get_similarity_method() in ["hybrid (bi-encoder top-10 + cross-encoder)", "bi-encoder"]
```

## Breaking Changes

### VectorStore

- **Removed**: `model_name` parameter
- **Required**: `embedder` parameter (mandatory)
- **Removed**: Internal embedder fallback in `search()` method

### ClassifierDetector

- **Removed**: `use_cross_encoder` parameter
- **Required**: `embedder` parameter (mandatory)
- **Added**: `cross_encoder` parameter (optional)
- **Changed**: `use_hybrid` requires both embedder and cross_encoder
- **Removed**: Internal cross-encoder initialization
- **Removed**: All embedder availability checks

### Error Handling

- **Added**: Explicit `ValueError` for missing embedder
- **Removed**: Silent fallbacks to word-based matching
- **Changed**: Immediate failure on missing required models

## Performance Impact

### Memory Usage
- **Reduced**: Eliminates duplicate model instances
- **Controlled**: Explicit model lifecycle management
- **Optimized**: Single models shared across components

### Initialization Time
- **Faster**: No redundant model loading
- **Predictable**: No hidden model downloads
- **Controlled**: Explicit model caching configuration

### Runtime Performance
- **Unchanged**: Same classification performance
- **Improved**: No runtime model checks
- **Reliable**: No fallback overhead

## Compatibility

### Backward Compatibility
- **Breaking**: This is a breaking change requiring code updates
- **Migration**: All existing code must be updated to new pattern
- **Timeline**: Required for v2.2.0+

### Future Compatibility
- **Stable**: New pattern will be maintained long-term
- **Extensible**: Easy to add new model types
- **Flexible**: Supports different model configurations

## Conclusion

The external model initialization pattern provides:
- **Better Control**: Explicit model management
- **Resource Efficiency**: Shared model instances
- **Clear Errors**: No hidden fallbacks
- **Production Ready**: Proper error handling and configuration

This change improves the overall architecture and makes the system more suitable for production deployments.