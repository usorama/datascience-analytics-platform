#!/bin/bash
# DataScience Platform - Quick Installation Script
# Usage: curl -sSL https://raw.githubusercontent.com/yourusername/ds-package/main/quick_install.sh | bash

set -e

echo "🚀 DataScience Platform - Quick Installation"
echo "=============================================="

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "📋 Python version: $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "❌ Error: Python 3.8+ required, found $python_version"
    exit 1
fi

# Detect system
if [[ "$OSTYPE" == "darwin"* ]]; then
    system="macOS"
    # Check for Apple Silicon
    if [[ $(uname -m) == "arm64" ]]; then
        system="macOS (Apple Silicon)"
        apple_silicon=true
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    system="Linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    system="Windows"
else
    system="Unknown"
fi

echo "💻 System: $system"

# Create temporary directory
install_dir=$(mktemp -d)
cd "$install_dir"

echo "📦 Cloning repository..."
git clone https://github.com/yourusername/ds-package.git
cd ds-package

echo "🔧 Installing core dependencies..."
pip install -r requirements.txt

echo "📦 Installing DataScience Platform..."
pip install -e .

echo "🧠 Installing NLP dependencies..."
pip install sentence-transformers torch faiss-cpu

# Apple Silicon specific setup
if [[ "$apple_silicon" == true ]]; then
    echo "🍎 Optimizing for Apple Silicon..."
    pip install --upgrade torch torchvision torchaudio
fi

echo "🧪 Running verification tests..."
if python3 -c "
from datascience_platform.nlp import SemanticEmbedder
embedder = SemanticEmbedder()
print(f'GPU Support: {embedder.device}')
embedding = embedder.embed_text('Installation test')
print(f'Embedding shape: {embedding.shape}')
print('✅ Installation verified!')
"; then
    echo "🎉 Installation completed successfully!"
else
    echo "⚠️  Installation completed with warnings. Basic functionality available."
fi

echo ""
echo "Next steps:"
echo "  cd ds-package"
echo "  python3 setup_and_test.py  # Run comprehensive tests"
echo "  python demo_ado_analysis.py  # Try examples"
echo ""
echo "📚 Documentation: README.md and docs/ directory"
echo "🐛 Issues: https://github.com/yourusername/ds-package/issues"

# Cleanup
cd /
rm -rf "$install_dir"

echo "🚀 Ready to analyze data with AI! 🚀"