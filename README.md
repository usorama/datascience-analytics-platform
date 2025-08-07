# DataScience Platform

A **production-ready** comprehensive ML-powered analytics platform with advanced NLP capabilities, automatic dashboard generation, and strategic alignment scoring for enterprise use.

## ✨ Key Features

- **🧠 Advanced NLP/NLU**: Real transformer embeddings with domain-specific models (FinBERT, SecBERT, LegalBERT)
- **⚡ GPU Acceleration**: Apple Silicon (M1/M2/M3) MPS support with automatic fallback
- **🔍 ML Optimization**: MLE-STAR implementation for systematic pipeline improvement
- **📊 Auto-Dashboard Generation**: TypeScript/React dashboards from ML outputs
- **🎯 Strategic Alignment**: QVF framework with AHP for objective prioritization
- **🔮 Risk Assessment**: ML-based risk prediction using historical data
- **📈 ADO Analytics**: 20+ Agile metrics with semantic alignment scoring
- **🗄️ Vector Database**: FAISS integration for scalable similarity search

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (check with `python --version` or `python3 --version`)
- **Git** installed on your system
- **Internet connection** for downloading dependencies

### Installation Options

#### Option 1: Clone and Install (Recommended for Development)
```bash
# Clone the repository
git clone https://github.com/yourusername/ds-package.git
cd ds-package

# Optional: Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies and the package in development mode
pip install -r requirements.txt
pip install -e .

# Install NLP dependencies (optional but recommended for full features)
pip install sentence-transformers torch faiss-cpu

# For Apple Silicon Macs - verify MPS support
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available() if hasattr(torch.backends, \"mps\") else False}')"

# Run comprehensive verification
python3 setup_and_test.py
```

#### Option 2: Install Pre-built Package (Production Use)
```bash
# Clone repository to get the pre-built wheel
git clone https://github.com/yourusername/ds-package.git
cd ds-package

# Install the pre-built wheel (faster, no compilation)
pip install dist/datascience_platform-2.0.0-py3-none-any.whl

# Or install with all optional features
pip install "dist/datascience_platform-2.0.0-py3-none-any.whl[full]"
```

#### Option 3: Direct Installation from Git (One Command)
```bash
# Install directly from GitHub repository
pip install git+https://github.com/yourusername/ds-package.git

# Or with all features
pip install "git+https://github.com/yourusername/ds-package.git[full]"
```

#### Option 4: PyPI Installation (Future Release)
```bash
# Basic installation (when published to PyPI)
pip install datascience-platform

# With GPU support (including Apple Silicon)
pip install datascience-platform[gpu]

# Full installation with all features
pip install datascience-platform[full]
```

### Verification

After installation, verify everything is working:

```python
# Test basic functionality
from datascience_platform.nlp import SemanticEmbedder
from datascience_platform.ado import ADOAnalyzer
from datascience_platform.dashboard.generative import DashboardGenerator

# Check GPU support (should show 'mps' on Apple Silicon, 'cuda' on NVIDIA, or 'cpu')
embedder = SemanticEmbedder()
print(f"Using device: {embedder.device}")

# Test embedding generation
embedding = embedder.embed_text("Test semantic understanding")
print(f"Embedding shape: {embedding.shape}")  # Should show (768,)

# Test ADO analysis
analyzer = ADOAnalyzer()
print("ADO analyzer ready")

print("✅ Installation verified successfully!")
```

### Usage

```python
from datascience_platform import DataAnalyzer, DashboardGenerator
from datascience_platform.nlp import SemanticEmbedder

# Analyze your data
analyzer = DataAnalyzer()
results = analyzer.analyze("your_data.csv")

# Generate dashboard
dashboard = DashboardGenerator()
dashboard.create(results, output_dir="my_dashboard")

# Use NLP features with automatic GPU detection
embedder = SemanticEmbedder()  # Automatically uses GPU if available
embedding = embedder.embed_text("Your business text here")

# Semantic similarity
text1 = "Financial risk assessment for quarterly planning"
text2 = "Q4 financial risk analysis and forecasting"
similarity = embedder.calculate_similarity(
    embedder.embed_text(text1),
    embedder.embed_text(text2)
)
print(f"Similarity: {similarity:.3f}")
```

### Command Line Interface

After installation, you can use these CLI commands:

```bash
# Main CLI interface
./dsplatform --help                    # Show all available commands
./dsplatform data read data.csv        # Read and analyze data
./dsplatform data validate data.csv    # Validate data quality

# Quick analysis commands
./ds-analyze data.csv                  # Quick data analysis
./ds-dashboard data.csv                # Generate interactive dashboard

# Test the installation
python3 verify_installation.py         # Comprehensive installation test
```

### Demo and Examples

Explore the platform with included examples:

```bash
# Run demonstration scripts
python demos/demo_ado_analysis.py           # ADO analytics
python demos/demo_semantic_ado.py           # Semantic alignment
python demos/demo_mle_star.py               # ML optimization
python demos/demo_dashboard.py              # Dashboard generation
python demos/demo_explainable_scoring.py   # Explainable AI scoring

# Comprehensive examples in examples/ directory
python examples/nlp_enhancement_demo.py     # NLP capabilities demo
```

## 🏗️ Architecture Overview

### Core Components

1. **🧠 NLP Enhancement**: State-of-the-art transformer models with domain-specific variants
2. **⚙️ MLE-STAR Optimization**: Systematic ML pipeline improvement with ablation studies
3. **🎯 Strategic Alignment**: Multi-dimensional scoring with evidence tracking and QVF framework
4. **🔮 Risk Prediction**: Historical learning for project risk assessment using ML models
5. **📊 Dashboard Generation**: Automatic TypeScript/React dashboards with interactive components
6. **📈 ADO Analytics**: Comprehensive Agile metrics with semantic understanding
7. **🗄️ Vector Operations**: FAISS-powered similarity search and clustering

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Operating System**: macOS, Linux, or Windows
- **RAM**: 4GB minimum, 8GB recommended (16GB+ for large datasets)
- **Storage**: 2GB free space for full installation
- **Internet**: Required for model downloads on first use

### GPU Support (Optional but Recommended for Performance)
- **Apple Silicon**: M1/M2/M3/M4 Macs with MPS support (3-5x faster)
- **NVIDIA**: CUDA 11.0+ compatible GPUs
- **AMD**: ROCm support (experimental)
- **Automatic Fallback**: CPU-only mode if no GPU available

### Dependencies
**Core dependencies** (installed automatically):
- pandas >= 1.5.0
- numpy >= 1.21.0
- scikit-learn >= 1.0.0
- pydantic >= 2.0.0

**NLP/ML dependencies** (optional but recommended):
- sentence-transformers >= 2.2.0
- torch >= 2.0.0
- faiss-cpu >= 1.7.4
- transformers >= 4.30.0

## 🏭 Production Deployment

### Docker Deployment (Recommended)
```bash
# Build production image
docker build -t datascience-platform:latest .

# Run with GPU support (NVIDIA)
docker run --gpus all -p 8080:8080 datascience-platform:latest

# Run on Apple Silicon
docker run -p 8080:8080 datascience-platform:latest
```

### Cloud Deployment

#### AWS ECS/Fargate
```bash
# Use provided CloudFormation template
aws cloudformation create-stack --stack-name ds-platform \
  --template-body file://deploy/aws/ecs-stack.yaml
```

#### Azure Container Instances
```bash
# Deploy to Azure
az container create --resource-group myResourceGroup \
  --name ds-platform --image datascience-platform:latest
```

#### Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy ds-platform --image datascience-platform:latest \
  --platform managed --region us-central1
```

### Environment Configuration

**Production Environment Variables:**
```bash
# Performance settings
export DS_PLATFORM_BATCH_SIZE=64          # Increase for better throughput
export DS_PLATFORM_CACHE_SIZE=10000       # Larger cache for production
export DS_PLATFORM_GPU_MEMORY_LIMIT=8192  # GPU memory limit (MB)

# Storage settings
export DS_PLATFORM_DATA_DIR="/data"       # Data storage directory
export DS_PLATFORM_CACHE_DIR="/cache"     # Cache storage directory
export DS_PLATFORM_LOG_LEVEL="INFO"       # Production logging level

# Security settings
export DS_PLATFORM_API_KEY="your-api-key" # API authentication
export DS_PLATFORM_CORS_ORIGINS="https://yourdomain.com"
```

### Performance Tuning

**For High-Volume Processing:**
```python
# Configure for production workloads
from datascience_platform import DataAnalyzer

analyzer = DataAnalyzer(
    batch_size=128,              # Larger batches
    max_workers=8,               # Parallel processing
    cache_size=50000,            # Larger cache
    gpu_memory_fraction=0.8      # Use more GPU memory
)
```

### Monitoring and Logging

**Health Checks:**
```bash
# Built-in health check endpoint
curl http://localhost:8080/health

# Detailed system status
curl http://localhost:8080/status
```

**Logging Configuration:**
```python
import logging
from datascience_platform.utils import setup_production_logging

# Production-ready logging
setup_production_logging(
    level=logging.INFO,
    format="json",              # Structured logging
    output="/var/log/ds-platform.log"
)
```

## 🔧 Troubleshooting

### Common Installation Issues

#### Import Errors
```bash
# If you get import errors, ensure all dependencies are installed
pip install -r requirements.txt
pip install sentence-transformers torch faiss-cpu transformers

# Verify installation
python3 verify_installation.py
```

#### Apple Silicon GPU Not Detected
```bash
# Ensure you have the latest PyTorch with MPS support
pip install --upgrade torch torchvision torchaudio

# Verify MPS availability
python -c "import torch; print('MPS Available:', hasattr(torch.backends, 'mps') and torch.backends.mps.is_available())"
```

#### FAISS Installation Issues
```bash
# Try CPU-only FAISS first
pip install faiss-cpu

# If that fails, use conda
conda install -c conda-forge faiss-cpu

# For NVIDIA GPUs with CUDA support
pip install faiss-gpu  # Requires CUDA 11.0+
```

#### Memory Issues During Processing
```python
# Reduce batch size to handle memory constraints
from datascience_platform.nlp import SemanticEmbedder
embedder = SemanticEmbedder(batch_size=16)  # Default is 32

# For very large datasets, use streaming processing
analyzer = DataAnalyzer(streaming=True, chunk_size=1000)
```

#### GPU Memory Issues
```bash
# Set GPU memory limits
export DS_PLATFORM_GPU_MEMORY_LIMIT=4096  # Limit to 4GB

# Or configure in Python
import os
os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'  # For Apple Silicon
```

### System-Specific Issues

#### Linux Systems
```bash
# Install system dependencies for some ML libraries
sudo apt-get update
sudo apt-get install build-essential python3-dev

# For GPU support on Linux
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Windows Systems
```bash
# Use Visual C++ Build Tools if compilation fails
# Install Microsoft Visual C++ 14.0 or greater

# For GPU support on Windows
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Getting Help

1. **Run Diagnostics**: `python3 setup_and_test.py` - Comprehensive system test
2. **Check Logs**: Enable debug logging with `export LOG_LEVEL=DEBUG`
3. **Verify Installation**: Use `python3 verify_installation.py`
4. **GitHub Issues**: Check repository issues for known problems
5. **Community**: Join discussions and get support

## 📚 Additional Documentation

- **[Project Structure](PROJECT_STRUCTURE.md)** - Detailed codebase organization
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Complete feature documentation
- **[CLAUDE.md](CLAUDE.md)** - Development guidelines for Claude Code

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and code of conduct in the repository.

## 📄 License

MIT License - see LICENSE file for details.

---

**DataScience Platform** - Production-ready ML analytics for the enterprise.  
*Built with ❤️ for data scientists and business analysts.*
