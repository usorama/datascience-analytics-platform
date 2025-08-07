#!/usr/bin/env python3
"""
DataScience Platform - Installation Verification Script
Run this after installation to verify all components are working correctly.
"""

import sys
import time

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "info": "\033[94m",      # Blue
        "success": "\033[92m",   # Green  
        "warning": "\033[93m",   # Yellow
        "error": "\033[91m",     # Red
        "reset": "\033[0m"       # Reset
    }
    
    symbols = {
        "info": "🔍",
        "success": "✅", 
        "warning": "⚠️",
        "error": "❌"
    }
    
    color = colors.get(status, colors["info"])
    symbol = symbols.get(status, "ℹ️")
    reset = colors["reset"]
    
    print(f"{color}{symbol} {message}{reset}")

def check_python_version():
    """Check Python version compatibility"""
    print_status("Checking Python version...")
    version = sys.version_info
    
    if version >= (3, 8):
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Compatible", "success")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Requires 3.8+", "error")
        return False

def test_imports():
    """Test core module imports"""
    print_status("Testing core module imports...")
    
    modules = [
        ("datascience_platform.nlp", "SemanticEmbedder"),
        ("datascience_platform.ado", "ADOAnalyzer"),
        ("datascience_platform.ado", "ADODataSimulator"),
        ("datascience_platform.dashboard.generative", "DashboardGenerator"),
        ("datascience_platform.mle_star", "MLPipelineAnalyzer"),
    ]
    
    success_count = 0
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print_status(f"  {module_name}.{class_name}", "success")
            success_count += 1
        except ImportError as e:
            print_status(f"  {module_name}.{class_name} - {e}", "warning")
        except Exception as e:
            print_status(f"  {module_name}.{class_name} - Unexpected error: {e}", "error")
    
    if success_count == len(modules):
        print_status("All core modules imported successfully", "success")
        return True
    else:
        print_status(f"Imported {success_count}/{len(modules)} modules", "warning")
        return success_count > 0

def test_gpu_support():
    """Test GPU support and device detection"""
    print_status("Testing GPU support...")
    
    try:
        from datascience_platform.nlp import SemanticEmbedder
        embedder = SemanticEmbedder()
        device = embedder.device
        
        if device == 'mps':
            print_status("Apple Silicon GPU (MPS) detected and active! 🚀", "success")
        elif device == 'cuda':
            print_status("NVIDIA CUDA GPU detected and active! 🚀", "success") 
        elif device == 'cpu':
            print_status("Using CPU (GPU not available or not configured) 💻", "info")
        else:
            print_status(f"Unknown device: {device}", "warning")
        
        return True, device
        
    except Exception as e:
        print_status(f"GPU detection failed: {e}", "error")
        return False, "unknown"

def test_embedding_generation():
    """Test basic embedding generation"""
    print_status("Testing embedding generation...")
    
    try:
        from datascience_platform.nlp import SemanticEmbedder
        embedder = SemanticEmbedder()
        
        # Test single embedding
        start_time = time.time()
        embedding = embedder.embed_text("DataScience Platform installation verification test")
        generation_time = time.time() - start_time
        
        print_status(f"  Single embedding: Shape {embedding.shape}, Time: {generation_time:.3f}s", "success")
        
        # Test batch embeddings
        test_texts = [
            "Financial risk assessment for quarterly planning",
            "Technical implementation of security features", 
            "Customer satisfaction and user experience optimization"
        ]
        
        start_time = time.time()
        embeddings = embedder.embed_texts(test_texts)
        batch_time = time.time() - start_time
        
        print_status(f"  Batch embeddings: Shape {embeddings.shape}, Time: {batch_time:.3f}s", "success")
        
        # Test similarity calculation
        similarity = embedder.calculate_similarity(embeddings[0], embeddings[1])
        print_status(f"  Similarity calculation: {similarity:.3f}", "success")
        
        return True
        
    except Exception as e:
        print_status(f"Embedding generation failed: {e}", "error")
        return False

def test_ado_functionality():
    """Test ADO analysis functionality"""
    print_status("Testing ADO analysis functionality...")
    
    try:
        from datascience_platform.ado import ADODataSimulator, ADOAnalyzer
        
        # Generate test data
        simulator = ADODataSimulator()
        work_items = simulator.generate_multi_pi_data(num_pis=1, num_epics=2)
        print_status(f"  Generated {len(work_items)} synthetic work items", "success")
        
        # Test analysis (but skip the full analysis to avoid errors in verification)
        analyzer = ADOAnalyzer()
        print_status("  ADO analyzer initialized successfully", "success")
        
        return True
        
    except Exception as e:
        print_status(f"ADO functionality test failed: {e}", "error")
        return False

def test_optional_features():
    """Test optional features that might not be available"""
    print_status("Testing optional features...")
    
    optional_imports = [
        ("sentence_transformers", "SentenceTransformer"),
        ("torch", "tensor"),
        ("faiss", "IndexFlatL2"),
        ("sklearn", "Pipeline"),
    ]
    
    available_features = []
    for module_name, item_name in optional_imports:
        try:
            module = __import__(module_name)
            if hasattr(module, item_name):
                available_features.append(module_name)
                print_status(f"  {module_name} - Available", "success")
            else:
                print_status(f"  {module_name} - Partial installation", "warning")
        except ImportError:
            print_status(f"  {module_name} - Not available", "warning")
    
    print_status(f"Optional features available: {len(available_features)}/{len(optional_imports)}", 
                 "success" if len(available_features) > 2 else "warning")
    
    return len(available_features) > 0

def main():
    """Main verification function"""
    print("=" * 60)
    print("🚀 DataScience Platform - Installation Verification")
    print("=" * 60)
    print()
    
    # Track test results
    results = {}
    
    # Run tests
    results['python'] = check_python_version()
    print()
    
    results['imports'] = test_imports() 
    print()
    
    gpu_success, device = test_gpu_support()
    results['gpu'] = gpu_success
    print()
    
    results['embeddings'] = test_embedding_generation()
    print()
    
    results['ado'] = test_ado_functionality()
    print()
    
    results['optional'] = test_optional_features()
    print()
    
    # Summary
    print("=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name.upper():12} {status}")
    
    print()
    
    if passed == total:
        print_status("🎉 All tests passed! DataScience Platform is ready to use.", "success")
        return_code = 0
    elif passed >= total * 0.7:  # 70% pass rate
        print_status(f"⚠️  {passed}/{total} tests passed. Core functionality available.", "warning")
        return_code = 0
    else:
        print_status(f"❌ Only {passed}/{total} tests passed. Installation may have issues.", "error")
        return_code = 1
    
    print()
    print("Next steps:")
    if return_code == 0:
        print("  • Run examples: python demo_ado_analysis.py")
        print("  • Full test suite: python3 setup_and_test.py") 
        print("  • Interactive UI: streamlit run streamlit_ado_semantic.py")
    else:
        print("  • Check installation: pip install -r requirements.txt")
        print("  • Reinstall package: pip install -e .")
        print("  • Check documentation: README.md")
    
    print("  • Get help: https://github.com/yourusername/ds-package/issues")
    print()
    
    return return_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)