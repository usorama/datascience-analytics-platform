# DataScience Platform - Detailed Reference

This document contains detailed technical information moved from CLAUDE.md for performance optimization.
Reference this file when you need comprehensive implementation details.

## Complete Project Structure (125 Python files)

### Core Module Details

#### ADO Analytics Module (`src/datascience_platform/ado/`)
- **Files**: 10 total including semantic subsystem
- **Key Components**:
  - analyzer.py: Main ADO metrics analyzer
  - semantic/alignment.py: QVF alignment scoring engine
  - semantic/embedder.py: GPU-accelerated embeddings
  - ahp.py: Analytic Hierarchy Process implementation
  - metrics.py: 25+ Agile metrics calculations
  - simulation.py: Monte Carlo simulations

#### NLP Engine (`src/datascience_platform/nlp/`)
- **Multi-backend Support**: MPS (Apple Silicon), CUDA (NVIDIA), CPU fallback
- **Domain Models**: FinBERT, SecBERT, LegalBERT, BioBERT
- **Vector Store**: FAISS indexing for millions of embeddings
- **Caching**: LRU with TTL management, 90%+ hit rate

#### Dashboard Generator (`src/datascience_platform/dashboard/`)
- **Output**: TypeScript/React with Next.js compatibility
- **Charts**: 15+ interactive types (Plotly, Chart.js, D3.js)
- **Templates**: 5 production-ready HTML templates
- **Features**: SSR support, accessibility (WCAG 2.1), responsive design

#### MLE-STAR Optimizer (`src/datascience_platform/mle_star/`)
- **Optimization**: Two-loop refinement with convergence detection
- **Ablation**: Systematic component analysis
- **Persistence**: Model versioning and repository management
- **Compatibility**: scikit-learn pipeline format

## Installation Variants

### Docker Deployment
```bash
docker build -t ds-platform:production .
docker run --gpus all -v $(pwd)/data:/app/data ds-platform:production
```

### Package Building
```bash
python3 -m build
pip install dist/datascience_platform-2.0.0-py3-none-any.whl[full]
```

## Advanced Configuration

### Production Environment Variables
```bash
export DS_PLATFORM_ENV=production
export DS_PLATFORM_GPU_ENABLED=true
export DS_PLATFORM_CACHE_SIZE=50000
export DS_PLATFORM_LOG_LEVEL=INFO
export DS_PLATFORM_METRICS_ENABLED=true
```

### Configuration YAML Structure
```yaml
database:
  connection_pool_size: 20
  query_timeout: 30
ml:
  gpu_memory_fraction: 0.8
  batch_size: 64
  model_cache_size: 10
nlp:
  model_parallel: true
  precision: "mixed"
  max_sequence_length: 512
dashboard:
  ssr_enabled: true
  cdn_optimization: true
  accessibility_compliance: "WCAG2.1"
```

## Performance Specifications

### Hardware Acceleration
- **Apple Silicon MPS**: 3-5x performance improvement
- **NVIDIA CUDA**: Memory-optimized GPU processing
- **CPU Optimization**: Multi-core with OpenMP/MKL

### Scalability Metrics
- **Embeddings**: Handle 10M+ vectors with FAISS
- **Batch Processing**: Dynamic size adjustment (8-512)
- **Memory Management**: Automatic garbage collection
- **Cache Performance**: Sub-millisecond retrieval

## API Endpoints

### REST API (FastAPI)
- POST `/api/v1/analyze/ado` - ADO analysis
- POST `/api/v1/nlp/embed` - Text embedding
- POST `/api/v1/ml/optimize` - Pipeline optimization
- GET `/api/v1/dashboard/{id}` - Dashboard retrieval
- POST `/api/v1/etl/validate` - Data validation

## Exception Hierarchy
```python
DataSciencePlatformError (base)
├── ValidationError (data validation)
├── ProcessingError (pipeline errors)
├── ResourceError (hardware/memory)
├── ConfigurationError (config issues)
└── IntegrationError (external services)
```

## Dependency Details

### Core Dependencies
- pandas >= 1.5.0
- numpy >= 1.21.0
- scikit-learn >= 1.0.0
- pydantic >= 2.0.0
- fastapi >= 0.100.0

### NLP/GPU Dependencies
- sentence-transformers >= 2.2.0
- torch >= 2.0.0
- faiss-cpu >= 1.7.4 (or faiss-gpu)
- transformers >= 4.30.0

### Dashboard Dependencies
- plotly >= 5.0.0
- streamlit >= 1.25.0
- jinja2 >= 3.0.0

## QVF Implementation Details

### Module Structure
```
qvf/
├── core/
│   ├── criteria.py (QVF criteria config)
│   ├── scoring.py (Enhanced AHP)
│   └── financial.py (NPV/COPQ calcs)
├── ado/
│   ├── custom_fields.py
│   ├── rest_client.py
│   └── work_items.py
├── ai/
│   ├── ollama_manager.py
│   ├── fallback.py
│   └── semantic.py
└── safe_agent/
    ├── core/ (agent orchestration)
    ├── llm/ (Ollama integration)
    ├── learning/ (RL engine)
    └── storage/ (ChromaDB, SQLite)
```

### SAFe Agent Components
- **Ollama**: Local LLM execution
- **ChromaDB**: Semantic memory storage
- **SQLite**: Conversation persistence
- **RL Engine**: Adaptive coaching
- **Elicitation**: Stakeholder preference extraction

## Testing Suites

### Unit Tests
```bash
pytest tests/unit/ -v --cov=src/datascience_platform
```

### Integration Tests
```bash
pytest tests/integration/ --integration
```

### Performance Tests
```bash
python3 scripts/performance_benchmark.py --full
```

### Component Tests
- `test_nlp_comprehensive.py` - NLP system validation
- `test_mle_star_quick.py` - ML pipeline testing
- `test_ado_metrics.py` - ADO calculations
- `test_dashboard_generation.py` - Dashboard creation

## Production Monitoring

### Logging Configuration
```python
from datascience_platform.logging import setup_production_logging

setup_production_logging(
    level=logging.INFO,
    format="structured",
    handlers=["file", "console", "syslog"],
    rotation="daily",
    retention_days=30
)
```

### Performance Tracking
```python
from datascience_platform.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()
with monitor.track_operation("operation_name"):
    # Your code here
    pass
metrics = monitor.get_performance_report()
```

## Security & Compliance

### Data Privacy
- GDPR/CCPA compliant handling
- PII detection and masking
- Encrypted storage (AES-256)
- Secure deletion protocols

### Access Control
- Role-based permissions (RBAC)
- API key management
- OAuth2/JWT authentication
- Rate limiting and throttling

### Audit & Compliance
- Comprehensive operation logging
- Change tracking and versioning
- Compliance report generation
- Automated security scanning

## Development Velocity Metrics

### With Claude Code Assistance
- 1 story point = 10 minutes
- 6-day sprint = 40-50 story points
- POC development = 1-2 sprints
- Production feature = 2-4 sprints

### Traditional Development
- 1 story point = 2-4 hours
- 2-week sprint = 20-30 story points
- POC development = 2-4 weeks
- Production feature = 1-3 months

## Migration Guides

### From v1.x to v2.0
1. Update import paths (datascience_platform namespace)
2. Migrate configuration to YAML format
3. Update API endpoints to v1 prefix
4. Review breaking changes in CHANGELOG.md

## Troubleshooting

### Common Issues
- **GPU not detected**: Check CUDA/MPS installation
- **Memory errors**: Reduce batch size in config
- **Import errors**: Verify all dependencies installed
- **Performance issues**: Enable caching, check GPU usage

### Debug Mode
```bash
export DS_PLATFORM_DEBUG=true
export DS_PLATFORM_PROFILE=true
```

## Contributing Guidelines

### Code Standards
- Type hints required for all functions
- Docstrings in NumPy format
- Unit tests for new features
- Performance benchmarks for critical paths

### PR Requirements
- All tests passing
- Code coverage > 90%
- Documentation updated
- Performance impact assessed

---

This reference document contains all detailed technical information from the original CLAUDE.md.
Keep the main CLAUDE.md lean and refer to this document when comprehensive details are needed.