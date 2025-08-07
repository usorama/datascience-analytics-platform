# DataScience Platform - Examples & Demos Guide

This guide provides comprehensive instructions for running all demonstration scripts and examples in the DataScience Platform. Each demo showcases different aspects of the platform's ML, NLP, and analytics capabilities.

## 📁 Directory Structure

```
examples/
├── CLAUDE.md                    # This guide
└── nlp_enhancement_demo.py     # NLP capabilities demonstration

demos/
├── demo_ado_analysis.py        # ADO analytics & metrics
├── demo_semantic_ado.py        # Semantic alignment scoring
├── demo_mle_star.py            # ML pipeline optimization
├── demo_generative_dashboard.py # Dashboard generation
├── demo_complete_system.py     # Full system integration
├── demo_intelligent_qa.py      # Q&A system
├── demo_relationship_extraction.py # Entity relationships
├── demo_explainable_scoring.py # Explainable AI
└── [additional demo files...]

docs/examples/
├── example_sales_analysis.py   # Sales data analysis
├── example_customer_segmentation.py # Customer analytics
├── example_time_series_forecast.py # Time series ML
└── README.md                   # Docs examples guide
```

## 🚀 Quick Start Setup

### Prerequisites
```bash
# Core installation
pip install -r requirements.txt
pip install -e .

# For NLP/GPU features
pip install -r requirements-nlp.txt

# Verify installation
python3 verify_installation.py
```

### GPU Acceleration (Recommended)
- **Apple Silicon**: Automatic MPS acceleration (3-5x faster)
- **NVIDIA**: CUDA support with fallback to CPU
- **CPU**: Automatic fallback with optimizations

## 📊 Demo Categories

### 1. ADO Analytics & Agile Metrics

#### `demos/demo_ado_analysis.py`
**Demonstrates**: Comprehensive Agile/PI planning analytics with 20+ metrics

**Key Features**:
- Velocity tracking and cycle time analysis
- PI confidence scoring and burndown analysis
- Quantified Value Framework (QVF) with AHP
- Work item prioritization and risk assessment

**Run Command**:
```bash
python3 demos/demo_ado_analysis.py
```

**Expected Output**:
- Agile metrics dashboard
- PI planning insights
- Work item prioritization scores
- Performance trend analysis

**Prerequisites**: None (generates synthetic data)

#### `demos/demo_semantic_ado.py`
**Demonstrates**: Strategic alignment scoring with semantic analysis

**Key Features**:
- Multi-dimensional alignment scoring
- Evidence-based decision making
- Semantic similarity analysis
- Strategic objective mapping

**Run Command**:
```bash
python3 demos/demo_semantic_ado.py
```

**Expected Output**:
- Alignment scores with evidence
- Strategic mapping results
- Semantic similarity matrices
- Decision support insights

**Prerequisites**: NLP dependencies (`pip install -r requirements-nlp.txt`)

#### `demos/demo_integrated_semantic_ado.py`
**Demonstrates**: Complete ADO workflow with semantic enhancements

**Key Features**:
- Full ADO-to-semantic pipeline
- Real-time scoring updates
- Interactive alignment dashboard
- Comprehensive reporting

**Run Command**:
```bash
python3 demos/demo_integrated_semantic_ado.py
```

### 2. NLP & Semantic Analysis

#### `examples/nlp_enhancement_demo.py`
**Demonstrates**: Advanced NLP capabilities with transformer models

**Key Features**:
- Real transformer embeddings (sentence-transformers)
- Domain-specific models (FinBERT, SecBERT, LegalBERT)
- GPU acceleration (MPS/CUDA)
- Vector similarity search with FAISS
- Historical risk prediction

**Run Command**:
```bash
python3 examples/nlp_enhancement_demo.py
```

**Expected Output**:
- GPU acceleration status
- Domain model selection results
- Vector similarity search results
- Risk prediction analysis
- Performance benchmarks

**Prerequisites**: 
- NLP dependencies (`pip install -r requirements-nlp.txt`)
- 4GB+ RAM recommended for transformer models

#### `demos/demo_intelligent_qa.py`
**Demonstrates**: Intelligent Q&A system with contextual understanding

**Key Features**:
- Natural language query processing
- Context-aware responses
- Multi-domain knowledge integration
- Confidence scoring

**Run Command**:
```bash
python3 demos/demo_intelligent_qa.py
```

#### `demos/demo_relationship_extraction.py`
**Demonstrates**: Entity relationship extraction from text

**Key Features**:
- Named entity recognition
- Relationship mapping
- Knowledge graph construction
- Semantic clustering

**Run Command**:
```bash
python3 demos/demo_relationship_extraction.py
```

### 3. ML Pipeline Optimization (MLE-STAR)

#### `demos/demo_mle_star.py`
**Demonstrates**: ML pipeline optimization using ablation studies

**Key Features**:
- Automatic pipeline component detection
- Systematic ablation studies
- Performance improvement recommendations
- Component impact analysis
- Two-loop refinement methodology

**Run Command**:
```bash
python3 demos/demo_mle_star.py
```

**Expected Output**:
- Pipeline component analysis
- Ablation study results
- Optimization recommendations
- Performance improvements
- Component impact scores

**Prerequisites**: scikit-learn, numpy, pandas

#### Test Files for MLE-STAR:
- `demos/test_mle_star_quick.py` - Quick validation tests
- `demos/test_ml_modules.py` - Module-specific tests

### 4. Dashboard Generation

#### `demos/demo_generative_dashboard.py`
**Demonstrates**: Automatic TypeScript/React dashboard generation

**Key Features**:
- ML optimization pipeline
- Convergence validation
- TypeScript/React code generation
- Three-tab dashboard architecture
- Interactive visualizations

**Run Command**:
```bash
python3 demos/demo_generative_dashboard.py
```

**Expected Output**:
- `generated_dashboard/` directory with complete React app
- TypeScript component files
- Interactive charts and visualizations
- Responsive design implementation

**Prerequisites**: ML pipeline data or will generate synthetic data

**Generated Files**:
```
generated_dashboard/
├── src/
│   ├── components/
│   │   ├── Analytics.tsx
│   │   ├── MLOutputs.tsx
│   │   └── Decisions.tsx
│   ├── types/
│   │   └── index.ts
│   └── App.tsx
├── package.json
└── tailwind.config.js
```

#### `demos/demo_dashboard.py`
**Demonstrates**: Basic dashboard functionality

**Key Features**:
- Data visualization basics
- Chart generation
- Layout management

**Run Command**:
```bash
python3 demos/demo_dashboard.py
```

### 5. Business Case Examples

#### `docs/examples/example_sales_analysis.py`
**Demonstrates**: Complete sales data analysis workflow

**Key Features**:
- Sales transaction processing
- KPI calculation and analysis
- Regional performance comparison
- Customer segment analysis
- Seasonal trend identification

**Run Command**:
```bash
cd docs/examples
python3 example_sales_analysis.py
```

**Expected Output**:
- `sales_data.parquet` - Cleaned sales data
- `sales_analysis.json` - Analysis results
- Console insights and recommendations

#### `docs/examples/example_customer_segmentation.py`
**Demonstrates**: Advanced customer analytics

**Key Features**:
- RFM (Recency, Frequency, Monetary) analysis
- Customer Lifetime Value calculation
- Behavioral segmentation
- Marketing recommendations

**Run Command**:
```bash
cd docs/examples
python3 example_customer_segmentation.py
```

#### `docs/examples/example_time_series_forecast.py`
**Demonstrates**: Time series forecasting with ML

**Key Features**:
- Time series data processing
- Seasonal decomposition
- Multiple forecasting models
- Performance evaluation

**Run Command**:
```bash
cd docs/examples
python3 example_time_series_forecast.py
```

### 6. Integration & System Tests

#### `demos/demo_complete_system.py`
**Demonstrates**: Full system integration across all components

**Key Features**:
- End-to-end pipeline execution
- Multi-component interaction
- Performance validation
- Comprehensive reporting

**Run Command**:
```bash
python3 demos/demo_complete_system.py
```

**Expected Output**:
- Complete system validation
- Performance metrics across components
- Integration test results
- Full dashboard generation

#### `demos/demo_simple.py`
**Demonstrates**: Basic platform functionality for quick validation

**Run Command**:
```bash
python3 demos/demo_simple.py
```

### 7. Explainable AI & Interpretability

#### `demos/demo_explainable_scoring.py`
**Demonstrates**: Explainable AI with transparency in decision making

**Key Features**:
- SHAP value calculations
- Feature importance analysis
- Decision explanation
- Transparency reporting

**Run Command**:
```bash
python3 demos/demo_explainable_scoring.py
```

**Expected Output**:
- Feature importance scores
- Decision explanations
- SHAP visualizations
- Transparency reports

## 🛠 Command Line Tools

After installation, these CLI tools are available globally:

```bash
# Main CLI interface
dsplatform --help

# Quick data analysis
ds-analyze data.csv

# Dashboard generation
ds-dashboard data.csv

# Direct CLI usage
./dsplatform data read data.csv
./dsplatform data validate data.csv
```

## 📋 Testing & Validation

### Comprehensive Test Suite
```bash
# Run all tests with coverage
python3 run_tests.py --coverage

# Component-specific tests
python3 test_nlp_comprehensive.py    # NLP system tests
python3 test_mle_star_quick.py       # ML optimization tests
python3 demos/test_ado_quick.py      # ADO analytics tests
python3 demos/test_dashboard.py      # Dashboard generation tests
```

### Quick Validation
```bash
# System verification
python3 verify_installation.py

# Setup and test
python3 setup_and_test.py
```

## 🔧 Configuration & Customization

### Environment Variables
```bash
export DS_PLATFORM_GPU_DEVICE="mps"    # Force specific GPU
export DS_PLATFORM_CACHE_SIZE="1000"   # Cache size limit
export DS_PLATFORM_BATCH_SIZE="32"     # Processing batch size
```

### Model Configuration
- **NLP Models**: Automatic selection based on domain
- **GPU Acceleration**: Auto-detection with fallback
- **Cache Settings**: Configurable TTL and size limits
- **Batch Processing**: Adjustable for memory constraints

## 📊 Expected Performance

### NLP Processing
- **GPU (MPS/CUDA)**: 3-5x faster than CPU
- **Batch Processing**: 32-item batches (configurable)
- **Cache Hit Rate**: 90%+ with warm cache
- **Memory Usage**: 2-4GB for transformer models

### ML Pipeline
- **Optimization Speed**: 10-50x faster ablation studies
- **Component Analysis**: Real-time feedback
- **Model Training**: Parallel execution where possible

### Dashboard Generation
- **Generation Time**: 30-120 seconds for complete React app
- **Component Count**: 15+ interactive components
- **Bundle Size**: Optimized for production deployment

## 🐛 Troubleshooting

### Common Issues

#### NLP Import Errors
```bash
# Install NLP dependencies
pip install -r requirements-nlp.txt
pip install sentence-transformers torch faiss-cpu
```

#### GPU Not Detected
```bash
# Check GPU availability
python3 -c "import torch; print(torch.backends.mps.is_available())"  # macOS
python3 -c "import torch; print(torch.cuda.is_available())"          # NVIDIA
```

#### Memory Issues
```bash
# Reduce batch size
export DS_PLATFORM_BATCH_SIZE="16"

# Use CPU mode
export DS_PLATFORM_GPU_DEVICE="cpu"
```

#### Dashboard Generation Fails
- Ensure sufficient disk space (>1GB)
- Check write permissions in current directory
- Verify all ML pipeline components are working

### Getting Help

1. **Check Installation**: `python3 verify_installation.py`
2. **Run Basic Test**: `python3 demos/demo_simple.py`
3. **Check Dependencies**: `pip list | grep -E "(torch|transformers|sentence)"`
4. **System Info**: Platform auto-detects GPU and provides detailed logging

## 🔗 Related Documentation

- **Main Documentation**: `/IMPLEMENTATION_SUMMARY.md` - Complete feature overview
- **Installation Guide**: `/INSTALL_FROM_GIT.md` - Setup instructions
- **Components Guide**: `/docs/components-ado-semantic.md` - ADO semantic analysis
- **NLP Enhancement**: `/docs/nlp-enhancement-plan.md` - NLP system details

## 💡 Best Practices

### Running Demos
1. **Start Simple**: Begin with `demo_simple.py` for basic validation
2. **Check Prerequisites**: Install NLP dependencies for advanced features
3. **Monitor Resources**: GPU demos require significant memory
4. **Sequential Testing**: Run component tests before integration demos

### Development Workflow
1. **Use Virtual Environment**: Isolate dependencies
2. **Check GPU Support**: Verify acceleration is working
3. **Validate Outputs**: Check generated files and console output
4. **Performance Monitoring**: Watch memory usage during large demos

### Production Deployment
1. **Resource Planning**: Account for transformer model sizes
2. **Caching Strategy**: Configure appropriate cache sizes
3. **GPU Utilization**: Leverage acceleration for production workloads
4. **Monitoring**: Set up logging and performance monitoring

This guide provides everything needed to explore the DataScience Platform's capabilities through practical demonstrations. Each demo is designed to showcase specific features while providing real-world applicability.