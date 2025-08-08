#!/usr/bin/env python3
"""Startup script for QVF Platform API with proper path configuration."""

import sys
import os
from pathlib import Path

def setup_python_path():
    """Setup Python path to include both API source and project root."""
    script_dir = Path(__file__).parent
    api_src_path = script_dir / "apps" / "api" / "src"
    project_root = script_dir.parent
    
    # Add paths to Python path
    sys.path.insert(0, str(api_src_path))
    sys.path.insert(0, str(project_root))
    
    # Set environment variable for subprocess
    current_path = os.environ.get("PYTHONPATH", "")
    new_paths = [str(api_src_path), str(project_root)]
    if current_path:
        new_paths.append(current_path)
    os.environ["PYTHONPATH"] = os.pathsep.join(new_paths)
    
    return api_src_path

def main():
    """Main startup function."""
    print("🚀 Starting QVF Platform API...")
    
    # Setup paths
    api_src_path = setup_python_path()
    
    # Test import
    try:
        from qvf_api.main import app
        from qvf_api.services.qvf_service import qvf_service
        
        health = qvf_service.get_health_status()
        print(f"✅ QVF Service Status: {health['status']}")
        print(f"   QVF Core Available: {health.get('qvf_core', False)}")
        print(f"   AI Features: {health.get('ai_features', False)}")
        
    except Exception as e:
        print(f"❌ Failed to import API: {e}")
        return 1
    
    # Start server
    print("\n🌐 Starting FastAPI server at http://localhost:8000")
    print("📚 API Documentation available at http://localhost:8000/docs")
    print("❤️  Health check available at http://localhost:8000/health")
    print("🔧 QVF endpoints at http://localhost:8000/api/v1/qvf/")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        import uvicorn
        uvicorn.run(
            "qvf_api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 QVF Platform API stopped")
        return 0
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())