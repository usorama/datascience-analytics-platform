# CLAUDE.md - Scripts Directory

This directory contains essential utility and automation scripts for the DataScience Platform, focused on production deployment, installation verification, and CI/CD integration.

## Script Overview

### Core Scripts

| Script | Purpose | Environment | Dependencies |
|--------|---------|-------------|--------------|
| `quick_install.sh` | One-line production installation | Production/Development | Git, Python 3.8+, pip |
| `setup_and_test.py` | Comprehensive system validation | Development/CI | All platform dependencies |
| `verify_installation.py` | Post-install verification | Production/Staging | Core platform modules |

## Detailed Script Documentation

### 🚀 quick_install.sh - One-Line Installation

**Purpose**: Automated production-ready installation with system detection and GPU optimization.

**Usage**:
```bash
# Remote installation (production deployment)
curl -sSL https://raw.githubusercontent.com/yourusername/ds-package/main/scripts/quick_install.sh | bash

# Local execution
./scripts/quick_install.sh
```

**Features**:
- **System Detection**: Automatically detects macOS, Linux, Windows
- **Apple Silicon Optimization**: Special MPS GPU acceleration setup for M1/M2/M3 chips
- **Python Validation**: Ensures Python 3.8+ compatibility
- **Progressive Installation**: Core → Platform → NLP → GPU optimization
- **Verification**: Built-in semantic embedder test
- **Cleanup**: Automatic temporary directory removal

**Production Considerations**:
- **Network Requirements**: Requires internet access for Git clone and pip installs
- **System Requirements**: 2GB+ available disk space, Python 3.8+
- **Security**: Uses HTTPS for all downloads, validates Python version
- **Fallback**: Continues with warnings if NLP components fail

**Exit Codes**:
- `0`: Successful installation with full verification
- `1`: Python version incompatible
- `2`: Git clone failed (check network/permissions)

---

### 🧪 setup_and_test.py - Comprehensive System Validation

**Purpose**: Full-stack testing and validation for development environments and CI/CD pipelines.

**Usage**:
```bash
# Full system test and setup
python3 scripts/setup_and_test.py

# Automated mode (for CI)
python3 scripts/setup_and_test.py --ci-mode
```

**Test Modules**:

1. **System Check**: Platform detection, Python version, GPU capabilities
2. **GPU Support Update**: Apple Silicon MPS optimization
3. **Vector Database**: FAISS setup and persistence testing
4. **Comprehensive Testing**: 
   - ADO analytics with synthetic data
   - Semantic scoring (multi-dimensional)
   - ML pipeline optimization (MLE-STAR)
   - Dashboard generation (TypeScript/React)
5. **Package Creation**: Production-ready setup.py, pyproject.toml, MANIFEST.in
6. **Distribution Build**: Wheel and source distribution creation

**CI/CD Integration**:
```yaml
# GitHub Actions example
- name: Run comprehensive tests
  run: |
    python3 scripts/setup_and_test.py
    if [ $? -eq 0 ]; then
      echo "✅ All tests passed"
    else
      echo "❌ Tests failed"
      exit 1
    fi
```

**Performance Benchmarks**:
- **Vector DB**: 100 vectors added/searched in <1s
- **Embeddings**: Single text <0.1s, batch of 3 <0.3s
- **Dashboard**: Complete generation <5s
- **Memory**: Peak usage <2GB during full test suite

---

### ✅ verify_installation.py - Installation Verification

**Purpose**: Production deployment verification with detailed diagnostics and fallback detection.

**Usage**:
```bash
# Standard verification
python3 scripts/verify_installation.py

# Exit code for automation
python3 scripts/verify_installation.py && echo "Installation verified"
```

**Verification Tests**:

1. **Python Compatibility**: Version 3.8+ validation
2. **Core Module Imports**: All critical platform components
3. **GPU Detection**: CUDA/MPS/CPU device identification
4. **Embedding Generation**: Performance and accuracy testing
5. **ADO Functionality**: Basic analyzer and simulator validation
6. **Optional Features**: sentence-transformers, torch, faiss, sklearn

**Output Examples**:
```
🔍 Checking Python version...
✅ Python 3.11.5 - Compatible

🔍 Testing GPU support...
✅ Apple Silicon GPU (MPS) detected and active! 🚀

🔍 Testing embedding generation...
✅ Single embedding: Shape (768,), Time: 0.045s
✅ Batch embeddings: Shape (3, 768), Time: 0.128s
```

**Production Deployment Checklist**:
- ✅ All core tests pass (100% required)
- ✅ GPU acceleration available (optional but recommended)
- ✅ Embedding generation <0.1s (performance baseline)
- ✅ Optional features ≥70% available (for full functionality)

**Exit Codes**:
- `0`: Installation verified, ready for production
- `1`: Critical failures, requires troubleshooting

## Integration Patterns

### Docker Integration

```dockerfile
FROM python:3.11-slim

# Copy and run installation
COPY scripts/quick_install.sh /tmp/
RUN chmod +x /tmp/quick_install.sh && /tmp/quick_install.sh

# Verify installation
COPY scripts/verify_installation.py /tmp/
RUN python3 /tmp/verify_installation.py

WORKDIR /app
```

### CI/CD Pipeline Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy DataScience Platform

on:
  push:
    branches: [main]

jobs:
  test-and-deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Run comprehensive setup
      run: python3 scripts/setup_and_test.py
    
    - name: Verify installation
      run: python3 scripts/verify_installation.py
    
    - name: Build distribution
      run: python3 -m build
    
    - name: Upload to PyPI
      if: github.ref == 'refs/heads/main'
      run: python3 -m twine upload dist/*
```

## Dependencies and Prerequisites

### System Requirements

**Minimum**:
- Python 3.8+
- 2GB RAM
- 1GB disk space
- Internet connection (for installation)

**Recommended**:
- Python 3.11+
- 8GB RAM (for full ML features)
- 5GB disk space
- GPU support (CUDA 11.0+ or Apple Silicon)

### Python Dependencies

**Core** (always required):
```
pandas>=1.5.0
numpy>=1.21.0
scikit-learn>=1.0.0
pydantic>=2.0.0
```

**NLP/GPU** (auto-installed by scripts):
```
sentence-transformers>=2.2.0
torch>=2.0.0
faiss-cpu>=1.7.4
transformers>=4.30.0
```

**Development** (for setup_and_test.py):
```
pytest>=7.0.0
build>=0.8.0
setuptools>=60.0.0
```

## Troubleshooting Guide

### Common Issues

**1. Installation Fails on Apple Silicon**
```bash
# Solution: Update Xcode Command Line Tools
xcode-select --install

# Verify fix
python3 scripts/verify_installation.py
```

**2. GPU Not Detected**
```bash
# Check PyTorch installation
python3 -c "import torch; print(f'MPS: {torch.backends.mps.is_available()}')"

# Reinstall with GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**3. Memory Issues During Testing**
```bash
# Reduce batch sizes in setup_and_test.py
export PYTHONHASHSEED=0
ulimit -v 4000000  # Limit to 4GB
python3 scripts/setup_and_test.py
```

**4. Import Errors**
```bash
# Verify Python path
python3 -c "import sys; print('\\n'.join(sys.path))"

# Reinstall in development mode
pip install -e .
```

### Performance Optimization

**For Production Deployments**:
1. **Pre-compile Models**: Run verify_installation.py once to cache transformers
2. **Vector DB Warmup**: Initialize FAISS with expected data size
3. **Memory Management**: Set appropriate batch sizes for your system
4. **GPU Memory**: Monitor MPS/CUDA memory usage for concurrent operations

**For CI/CD Pipelines**:
1. **Cache Dependencies**: Cache pip and transformer downloads
2. **Parallel Testing**: Run verification tests in parallel where possible
3. **Resource Limits**: Set appropriate memory/CPU limits
4. **Artifact Storage**: Save built wheels for deployment

## Production Deployment Workflow

### Standard Deployment
```bash
# 1. Fresh installation
curl -sSL https://raw.githubusercontent.com/yourusername/ds-package/main/scripts/quick_install.sh | bash

# 2. Verification
python3 scripts/verify_installation.py

# 3. Performance baseline
python3 -c "
from datascience_platform.nlp import SemanticEmbedder
import time
embedder = SemanticEmbedder()
start = time.time()
embedding = embedder.embed_text('Production test')
print(f'Embedding time: {time.time() - start:.3f}s')
print(f'Device: {embedder.device}')
"
```

### High-Availability Deployment
```bash
# 1. Multi-environment setup
./scripts/quick_install.sh
python3 scripts/setup_and_test.py

# 2. Load balancer health check endpoint
python3 -c "
from datascience_platform.nlp import SemanticEmbedder
try:
    embedder = SemanticEmbedder()
    embedding = embedder.embed_text('health check')
    print('HEALTHY')
except:
    print('UNHEALTHY')
    exit(1)
"
```

## Links to Main Documentation

- **[Main README](../README.md)**: Platform overview and quick start
- **[Implementation Summary](../IMPLEMENTATION_SUMMARY.md)**: Complete feature documentation
- **[API Documentation](../docs/)**: Detailed API references
- **[Examples](../examples/)**: Usage examples and tutorials
- **[Project Structure](../PROJECT_STRUCTURE.md)**: Codebase organization

## Automation and Monitoring

### Health Check Integration
```python
#!/usr/bin/env python3
# health_check.py
import subprocess
import sys

def health_check():
    result = subprocess.run([
        sys.executable, 'scripts/verify_installation.py'
    ], capture_output=True, text=True)
    
    return result.returncode == 0

if __name__ == "__main__":
    sys.exit(0 if health_check() else 1)
```

### Monitoring Integration
The scripts provide structured output suitable for monitoring systems:
- **Prometheus**: Exit codes and timing metrics
- **DataDog**: Performance and error logging
- **CloudWatch**: System health and utilization
- **Grafana**: Dashboard visualization of test results

These scripts form the foundation of reliable DataScience Platform deployments, providing comprehensive validation, optimization, and monitoring capabilities for production environments.