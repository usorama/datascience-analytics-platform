# DataScience Platform - NLP Enhancement Module

## Overview

The NLP Enhancement module provides production-ready natural language processing capabilities for the DataScience Platform, including advanced semantic understanding, domain-specific model selection, historical risk prediction, and efficient vector-based similarity search.

## Key Features

### 🚀 Production-Ready Semantic Embeddings
- Real transformer models with GPU support
- Advanced caching with TTL and LRU eviction
- Batch processing for optimal performance
- Graceful fallback to mock implementations

### 🎯 Domain-Specific Model Selection
- Automatic domain detection (Financial, Legal, Security, Technical, etc.)
- Intelligent model routing based on content analysis
- Support for specialized models (FinBERT, LegalBERT, SecBERT)
- Confidence scoring for model selections

### 🔮 Historical Risk Prediction
- ML-based risk prediction using historical project data
- Multiple risk types (Schedule, Budget, Quality, Technical Debt)
- Feature engineering from text and metadata
- Actionable recommendations and similar case analysis

### 🔍 Vector-Based Similarity Search
- FAISS-powered efficient similarity search
- Metadata filtering and hybrid search capabilities
- Multiple distance metrics (cosine, euclidean, inner product)
- Scalable to millions of vectors

### 📝 Advanced Text Processing
- Comprehensive text preprocessing pipeline
- Multi-language support with NLTK and spaCy
- Keyword extraction and sentence segmentation
- Configurable cleaning and normalization

### 📊 Model Management & Monitoring
- Comprehensive model lifecycle management
- Performance monitoring and system resource tracking
- Advanced caching strategies
- Statistics and usage analytics

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NLP Enhancement Module                    │
├─────────────────────────────────────────────────────────────┤
│                        Core Layer                            │
├─────────────────┬───────────────┬──────────────────────────┤
│   SemanticEmbedder  │  TextProcessor  │  ModelManager     │
│   • Real transformers │  • Preprocessing │  • Lifecycle mgmt │
│   • GPU support     │  • Multi-language │  • Monitoring    │
│   • Advanced cache  │  • Keywords      │  • Statistics    │
├─────────────────┴───────────────┴──────────────────────────┤
│                      Domain Layer                           │
├─────────────────────┬───────────────────────────────────────┤
│   DomainModelSelector │     HistoricalRiskPredictor         │
│   • Auto detection   │     • ML-based prediction           │
│   • Specialist models│     • Feature engineering          │
│   • Confidence scores│     • Actionable insights          │
├─────────────────────┴───────────────────────────────────────┤
│                    Infrastructure Layer                      │
├─────────────────────┬───────────────────────────────────────┤
│      VectorStore    │           Utilities                   │
│      • FAISS index  │           • Caching                   │
│      • Metadata     │           • Monitoring                │
│      • Hybrid search│           • Error handling            │
└─────────────────────┴───────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
# Install enhanced NLP dependencies
pip install -r requirements-nlp.txt

# Optional: Download spaCy language model
python -m spacy download en_core_web_sm
```

### Basic Usage

```python
from datascience_platform.nlp import SemanticEmbedder, DomainModelSelector

# Initialize embedder with caching
embedder = SemanticEmbedder(
    model_name="sentence-transformers/all-mpnet-base-v2",
    use_cache=True
)

# Generate embeddings
text = "Financial risk assessment for quarterly planning"
embedding = embedder.embed_text(text)
print(f"Embedding shape: {embedding.shape}")

# Domain-specific model selection
selector = DomainModelSelector()
domain, confidence = selector.detect_domain(text)
print(f"Detected domain: {domain.value} (confidence: {confidence:.3f})")
```

### Advanced Features

```python
from datascience_platform.nlp import (
    HistoricalRiskPredictor, 
    VectorStore, 
    TextProcessor,
    ModelManager
)

# Risk prediction
predictor = HistoricalRiskPredictor()
predictions = predictor.predict_risk(
    title="Implement payment gateway",
    description="Complex integration requiring security review...",
    team_size=5,
    priority="high"
)

for pred in predictions:
    print(f"{pred.risk_type.value}: {pred.probability:.3f}")

# Vector similarity search
store = VectorStore(dimension=768)
store.add_vector("doc1", embedding, {"category": "financial"})

similar = store.search(query_embedding, k=5)
for doc_id, similarity, metadata in similar:
    print(f"{doc_id}: {similarity:.3f}")

# Model management with monitoring
manager = ModelManager(enable_monitoring=True)
manager.register_model("embedder", embedder)

with manager.time_inference("embedder"):
    results = embedder.embed_texts(["text1", "text2"])
```

## Module Structure

```
src/datascience_platform/nlp/
├── __init__.py                 # Main module exports
├── core/                       # Core NLP functionality
│   ├── __init__.py
│   └── embedder.py            # Enhanced semantic embedder
├── domain/                     # Domain-specific models
│   ├── __init__.py
│   └── model_selector.py      # Domain model selection
├── risk/                       # Risk prediction
│   ├── __init__.py
│   └── predictor.py           # Historical risk predictor
├── vector_store/              # Vector operations
│   ├── __init__.py
│   └── faiss_store.py         # FAISS-based vector store
├── utils/                      # Utilities
│   ├── __init__.py
│   ├── text_processing.py     # Text preprocessing
│   └── model_utils.py         # Model management
└── tests/                      # Comprehensive tests
    ├── __init__.py
    ├── test_integration.py     # Integration tests
    └── test_embedder.py        # Unit tests
```

## Configuration

### Environment Variables

```bash
# Optional: Specify cache directories
export DS_PLATFORM_CACHE_DIR="/path/to/cache"
export DS_PLATFORM_MODEL_DIR="/path/to/models"

# Optional: GPU configuration
export CUDA_VISIBLE_DEVICES="0,1"

# Optional: Model-specific settings
export TRANSFORMERS_CACHE="/path/to/transformers/cache"
```

### Configuration Files

Create `nlp_config.yaml` in your project:

```yaml
embedder:
  model_name: "sentence-transformers/all-mpnet-base-v2"
  use_cache: true
  device: "auto"  # auto, cpu, cuda
  batch_size: 32

domain_selector:
  auto_download: false
  confidence_threshold: 0.3

risk_predictor:
  model_types: ["random_forest", "xgboost"]
  cross_validation: true
  validation_split: 0.2

vector_store:
  index_type: "flat"  # flat, ivf, hnsw
  metric_type: "cosine"
  dimension: 768
```

## Performance Optimization

### GPU Acceleration

```python
# Enable GPU support
embedder = SemanticEmbedder(
    model_name="sentence-transformers/all-mpnet-base-v2",
    device="cuda"  # Uses GPU if available
)

# For production with multiple GPUs
import torch
if torch.cuda.device_count() > 1:
    embedder.model = torch.nn.DataParallel(embedder.model)
```

### Batch Processing

```python
# Process multiple texts efficiently
texts = ["text1", "text2", "text3", ...]
embeddings = embedder.embed_texts(
    texts, 
    batch_size=64  # Adjust based on memory
)
```

### Caching Strategy

```python
# Configure advanced caching
from datascience_platform.nlp.utils import ModelCache

cache = ModelCache(
    max_cache_size_gb=4.0,  # 4GB cache limit
    ttl_hours=168,          # 1 week TTL
    compress_disk=True      # Compress cached items
)

embedder = SemanticEmbedder(cache_dir="/fast/ssd/cache")
```

## Examples and Demos

### Running the Demo

```bash
# Run comprehensive demo
python examples/nlp_enhancement_demo.py

# The demo will:
# 1. Download models (if not cached)
# 2. Process sample work items
# 3. Demonstrate all features
# 4. Show performance statistics
```

### Integration Example

See `examples/nlp_enhancement_demo.py` for a complete end-to-end example showing:

- Semantic embedding generation
- Domain-specific model selection  
- Risk prediction and recommendations
- Vector similarity search
- Text processing pipeline
- Model management and monitoring

## Testing

### Running Tests

```bash
# Run all NLP tests
pytest src/datascience_platform/nlp/tests/ -v

# Run with coverage
pytest src/datascience_platform/nlp/tests/ --cov=datascience_platform.nlp

# Run integration tests only
pytest src/datascience_platform/nlp/tests/test_integration.py -v

# Run performance benchmarks
pytest src/datascience_platform/nlp/tests/ --benchmark-only
```

## Troubleshooting

### Common Issues

#### Model Download Failures
```python
# Solution: Use offline mode or specify local models
embedder = SemanticEmbedder(
    model_name="/path/to/local/model",
    use_cache=True
)
```

#### Memory Issues
```python
# Solution: Reduce batch size and enable memory cleanup
embedder = SemanticEmbedder(batch_size=16)
embedder.clear_cache(older_than_hours=24)
```

#### GPU Out of Memory
```python
# Solution: Use CPU or smaller models
embedder = SemanticEmbedder(
    model_name="sentence-transformers/all-MiniLM-L6-v2",  # Smaller model
    device="cpu"
)
```

## Migration Guide

### From Legacy Implementation

If migrating from the existing semantic module:

```python
# Old way
from datascience_platform.ado.semantic import SemanticEmbedder
embedder = SemanticEmbedder()

# New way (backward compatible)
from datascience_platform.ado.semantic import SemanticEmbedder
embedder = SemanticEmbedder(use_domain_selection=True)

# Or use enhanced module directly
from datascience_platform.nlp import SemanticEmbedder
embedder = SemanticEmbedder()
```

---

*This module represents a significant enhancement to the DataScience Platform's NLP capabilities, providing production-ready, scalable, and maintainable natural language processing features.*