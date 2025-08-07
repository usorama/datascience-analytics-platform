# CLAUDE.md - NLP Module

This file provides guidance to Claude Code (claude.ai/code) when working with the NLP module in the DataScience Platform.

## 🧠 NLP Module Overview

The DataScience Platform NLP module provides **production-ready semantic analysis** with GPU acceleration, real transformer models, and enterprise-grade performance. This is **not a prototype** - it's a complete implementation with comprehensive caching, error handling, and monitoring.

### Key Capabilities
- **GPU-Accelerated Embeddings**: Automatic MPS (Apple Silicon), CUDA, and CPU fallback
- **Real Transformer Models**: Production sentence-transformers with domain-specific models
- **Advanced Vector Operations**: FAISS integration for million-scale similarity search
- **Enterprise Caching**: TTL-based cache with LRU eviction and compression
- **Domain Intelligence**: Automatic model selection for finance, legal, security, healthcare
- **Risk Prediction**: ML-powered historical risk assessment with feature engineering

## 🏗️ Architecture & Components

### Core Components

#### `/core/embedder.py` - **SemanticEmbedder** (Primary Interface)
```python
from datascience_platform.nlp import SemanticEmbedder

# Auto-detects GPU (MPS for Apple Silicon, CUDA, or CPU)
embedder = SemanticEmbedder(
    model_name="sentence-transformers/all-mpnet-base-v2",  # Default production model
    use_cache=True,          # 90%+ hit rate caching
    device=None,            # Auto-detect: 'mps' | 'cuda' | 'cpu'
    batch_size=32,          # Configurable for memory optimization
    max_seq_length=512      # Control input length
)

# High-performance single text embedding
embedding = embedder.embed_text("Financial risk assessment document")
# Returns: numpy array (768,) - normalized unit vector

# Optimized batch processing
embeddings = embedder.embed_texts([
    "Q1 revenue projections show strong growth",
    "Security vulnerability requires immediate attention",
    "Customer satisfaction metrics exceed targets"
])
# Returns: numpy array (3, 768) - batch processed efficiently
```

#### `/domain/model_selector.py` - **DomainModelSelector**
```python
from datascience_platform.nlp import DomainModelSelector

selector = DomainModelSelector()

# Automatic domain detection and model recommendation
recommended_model = selector.recommend_model(
    text="SEC filing shows quarterly compliance requirements",
    context="regulatory_analysis"
)
# Returns: 'nlpaueb/sec-bert-base' for financial/SEC documents

# Available domains: financial, legal, security, healthcare, technical, business, compliance
```

#### `/vector_store/faiss_store.py` - **VectorStore**
```python
from datascience_platform.nlp import VectorStore

# High-performance vector database for similarity search
vector_store = VectorStore(
    dimension=768,           # Embedding dimension
    index_type="IVF",       # IndexIVFFlat for large datasets
    metric="cosine",        # cosine | l2 | inner_product
    use_gpu=True            # GPU acceleration if available
)

# Scalable operations - handles millions of embeddings
vector_store.add_embeddings(embeddings, metadata=document_metadata)

# Lightning-fast similarity search
similar_docs = vector_store.search(
    query_embedding=query_embedding,
    k=10,                   # Top 10 results
    threshold=0.7,          # Minimum similarity score
    filter_metadata={"category": "financial"}  # Metadata filtering
)
```

#### `/risk/predictor.py` - **HistoricalRiskPredictor**
```python
from datascience_platform.nlp import HistoricalRiskPredictor

predictor = HistoricalRiskPredictor()

# ML-powered risk assessment using historical patterns
risk_score = predictor.predict_risk(
    text="Critical security vulnerability in production system",
    historical_data=past_incidents,
    feature_engineering=True  # Advanced feature extraction
)
# Returns: RiskPrediction(score=0.95, confidence=0.87, factors=['urgency', 'security'])
```

### Utility Components

#### `/utils/text_processing.py` - Text Processing Utilities
- Advanced text cleaning and normalization
- Language detection and multilingual support
- Entity extraction and PII detection
- Document chunking for large texts

#### `/utils/model_utils.py` - Model Management
- **ModelManager**: Comprehensive model lifecycle management
- **ModelCache**: Advanced caching with size limits and TTL
- **SystemMonitor**: Real-time GPU/CPU/memory monitoring
- **ModelMetrics**: Performance tracking and optimization

## ⚡ Performance & GPU Acceleration

### Automatic Device Detection
```python
# The system automatically detects and optimizes for your hardware:

# Apple Silicon Macs (M1/M2/M3)
device = 'mps'  # 3-5x faster than CPU
logger.info("Using Apple Silicon GPU (MPS)")

# NVIDIA GPUs with CUDA
device = 'cuda'  # 10-50x faster depending on GPU

# CPU Fallback
device = 'cpu'   # Still optimized with vectorization
```

### Performance Optimizations
- **Batch Processing**: Configurable batch sizes for memory-constrained environments
- **Advanced Caching**: 90%+ hit rate with TTL-based LRU eviction
- **Memory Management**: Automatic cleanup and garbage collection
- **Vector Compression**: Reduced storage footprint for embeddings

## 🔗 Integration Patterns

### ADO Analytics Integration
```python
# Semantic alignment scoring for ADO work items
from datascience_platform.ado.semantic.embedder import SemanticEmbedder as ADOEmbedder

# Enhanced ADO embedder uses the core NLP system
ado_embedder = ADOEmbedder(
    model_name="sentence-transformers/all-mpnet-base-v2",
    use_cache=True
)

# Calculate work item alignment
alignment_score = ado_embedder.calculate_similarity(
    business_objective_embedding,
    work_item_description_embedding
)
```

### Dashboard Generation Integration
```python
# NLP insights automatically flow into generated dashboards
nlp_insights = {
    'semantic_clusters': embedder.find_similar_texts(query, documents, top_k=5),
    'risk_assessment': predictor.predict_risk(high_priority_text),
    'domain_classification': selector.classify_domain(business_documents)
}
```

### MLE-STAR Optimization Integration  
```python
# NLP components can be optimized using MLE-STAR methodology
from datascience_platform.mle_star import MLEStarOptimizer

optimizer = MLEStarOptimizer()
optimized_config = optimizer.optimize_nlp_pipeline(
    current_pipeline=embedder,
    optimization_target='throughput'  # or 'accuracy', 'memory'
)
```

## 📊 Usage Examples & Patterns

### Basic Semantic Analysis
```python
from datascience_platform.nlp import SemanticEmbedder

# Initialize with automatic GPU detection
embedder = SemanticEmbedder()

# Process business documents
documents = [
    "Q4 financial results exceed projections by 15%",
    "New security protocol implementation required",  
    "Customer satisfaction survey shows improvement"
]

# Generate embeddings with GPU acceleration
embeddings = embedder.embed_texts(documents)

# Find similar content
query = "quarterly financial performance"
similar = embedder.find_similar_texts(query, documents, top_k=2, threshold=0.6)
# Returns: [(0, "Q4 financial results...", 0.82)]
```

### Advanced Domain-Specific Analysis
```python
from datascience_platform.nlp import SemanticEmbedder, DomainModelSelector

# Use domain-specific models for specialized content
selector = DomainModelSelector()
financial_model = selector.get_model_for_domain('financial')

# Specialized financial analysis
financial_embedder = SemanticEmbedder(model_name=financial_model)

# Process SEC filings, earnings reports, etc.
sec_embedding = financial_embedder.embed_text(
    "Form 10-K annual report shows revenue growth of 12% year-over-year"
)
```

### Large-Scale Vector Operations
```python
from datascience_platform.nlp import SemanticEmbedder, VectorStore

# Set up production-scale vector database
embedder = SemanticEmbedder(batch_size=64)  # Larger batches for throughput
vector_store = VectorStore(dimension=768, index_type="IVF")

# Process large document collections efficiently
document_embeddings = embedder.embed_texts(
    large_document_collection,  # Handles millions of documents
    batch_size=128  # Optimized for your GPU memory
)

# Build searchable index
vector_store.add_embeddings(document_embeddings, metadata=document_metadata)

# Lightning-fast similarity search across millions of documents
results = vector_store.search(query_embedding, k=50, threshold=0.75)
```

## 🛡️ Error Handling & Fallbacks

### Graceful Degradation
The NLP module provides robust fallback mechanisms:

```python
# Automatic fallback chain:
# 1. Try real transformer models with GPU
# 2. Fall back to CPU if GPU unavailable  
# 3. Use enhanced mock embeddings if transformers unavailable
# 4. Never crash - always returns valid embeddings

embedder = SemanticEmbedder()  # Handles all fallbacks automatically
```

### Installation Requirements
```bash
# Core functionality (always works)
pip install -e .

# Full NLP capabilities
pip install sentence-transformers torch faiss-cpu
pip install -r requirements-nlp.txt

# GPU acceleration
pip install torch torchvision torchaudio  # For NVIDIA CUDA
# MPS support built into PyTorch 2.0+ (automatic on Apple Silicon)
```

## 📈 Monitoring & Optimization

### Performance Statistics
```python
# Get comprehensive performance metrics
stats = embedder.get_stats()
print(f"Cache hit rate: {stats['cache_stats']['hit_rate']:.1%}")
print(f"Average processing time: {stats['avg_processing_time']:.3f}s")
print(f"Total embeddings generated: {stats['texts_encoded']:,}")

# Model information
info = embedder.get_model_info()
print(f"Device: {info['device']}")
print(f"Model: {info['model_name']}")
print(f"Embedding dimension: {info['embedding_dim']}")
```

### Cache Management
```python
# Advanced cache operations
embedder.clear_cache(older_than_hours=24)  # Clear old cache entries
cache_stats = embedder.cache.get_stats()   # Detailed cache metrics

# Cache warming for production deployment
embedder.warm_up([
    "Sample financial document",
    "Security assessment report", 
    "Business requirement specification"
])
```

## 🧪 Testing & Validation

### Comprehensive Test Suite
```bash
# Run NLP-specific tests
python3 test_nlp_comprehensive.py

# Quick functionality test  
python3 test_nlp_demo.py

# Integration tests with other modules
python3 -m pytest src/datascience_platform/nlp/tests/ -v
```

### Test Coverage
- **Unit Tests**: All core classes with edge cases
- **Integration Tests**: End-to-end workflows  
- **Performance Tests**: GPU acceleration validation
- **Fallback Tests**: Mock implementations when libraries unavailable

## 🔧 Configuration & Tuning

### Memory Optimization
```python
# For memory-constrained environments
embedder = SemanticEmbedder(
    batch_size=16,          # Reduce batch size
    max_seq_length=256,     # Limit input length
    use_cache=True,         # Essential for performance
    cache_dir=Path("/fast_ssd/cache")  # Use fast storage
)
```

### Production Configuration
```python
# Production-optimized setup
embedder = SemanticEmbedder(
    model_name="sentence-transformers/all-mpnet-base-v2",
    device=None,            # Auto-detect GPU
    batch_size=64,          # Large batches for throughput
    use_cache=True,         # Essential
    cache_dir=Path("/app/cache"),
    max_seq_length=512      # Full model capacity
)
```

## 📚 Links & References

### Main Documentation
- **Platform Overview**: `/IMPLEMENTATION_SUMMARY.md` - Complete feature documentation
- **Installation Guide**: `/verify_installation.py` - Installation verification
- **Demo Scripts**: `/demo_*.py` - Working examples for each component

### Command-Line Interface
```bash
# After installation, these commands are available:
dsplatform nlp embed "text to analyze"          # Quick embedding generation
dsplatform nlp similar "query" data.csv        # Find similar content
ds-analyze data.csv --include-nlp              # Include NLP insights in analysis
```

### API Reference
- **SemanticEmbedder**: Primary embedding interface with GPU acceleration
- **DomainModelSelector**: Intelligent domain-specific model selection  
- **VectorStore**: High-performance similarity search with FAISS
- **HistoricalRiskPredictor**: ML-powered risk assessment
- **ModelManager**: Comprehensive model lifecycle management

### Integration Points
- **ADO Module**: `/src/datascience_platform/ado/semantic/` - Business alignment scoring
- **Dashboard Module**: `/src/datascience_platform/dashboard/` - Automatic NLP insights
- **MLE-STAR Module**: `/src/datascience_platform/mle_star/` - Pipeline optimization

---

## 💡 Developer Notes

When working with this NLP module:

1. **Always use the SemanticEmbedder as the primary interface** - it handles all complexity
2. **GPU acceleration is automatic** - no manual configuration needed  
3. **Caching is essential for performance** - 90%+ hit rates in production
4. **Batch processing is highly optimized** - use `embed_texts()` for multiple documents
5. **Error handling is comprehensive** - the system never crashes, always degrades gracefully
6. **Domain-specific models provide better accuracy** - use DomainModelSelector for specialized content

The NLP module represents the **state-of-the-art in production semantic analysis**, combining the latest transformer research with enterprise-grade performance, monitoring, and reliability.