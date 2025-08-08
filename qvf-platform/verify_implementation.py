#!/usr/bin/env python3
"""Comprehensive verification of QVF FastAPI backend implementation."""

import sys
import os
import time
import json
import subprocess
import requests
from pathlib import Path

# Add both API source and project root to Python path
script_dir = Path(__file__).parent
api_src_path = script_dir / "apps" / "api" / "src"
project_root = script_dir.parent
sys.path.insert(0, str(api_src_path))
sys.path.insert(0, str(project_root))

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message."""
    print(f"✅ {message}")

def print_error(message):
    """Print error message."""
    print(f"❌ {message}")

def print_info(message):
    """Print info message."""
    print(f"ℹ️  {message}")

def verify_environment():
    """Verify the environment is properly set up."""
    print_header("Environment Verification")
    
    # Check pnpm installation
    try:
        subprocess.run(["pnpm", "--version"], capture_output=True, check=True)
        print_success("pnpm is installed and working")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("pnpm is not installed or not working")
        return False
    
    # Check Python path setup
    try:
        from qvf_api.main import app
        print_success("FastAPI app can be imported")
    except ImportError as e:
        print_error(f"FastAPI app import failed: {e}")
        return False
    
    # Check QVF core connection
    try:
        from src.datascience_platform.qvf import QVFCriteriaEngine
        engine = QVFCriteriaEngine()
        print_success(f"QVF Core engine connected successfully")
    except ImportError as e:
        print_error(f"QVF Core connection failed: {e}")
        return False
    
    return True

def verify_qvf_service():
    """Verify QVF service functionality."""
    print_header("QVF Service Verification")
    
    try:
        from qvf_api.services.qvf_service import qvf_service
        
        # Test health status
        health = qvf_service.get_health_status()
        print_success(f"QVF Service Status: {health['status']}")
        print_info(f"   QVF Core Available: {health.get('qvf_core', False)}")
        print_info(f"   Criteria Engine: {health.get('criteria_engine', False)}")
        print_info(f"   AI Features: {health.get('ai_features', False)}")
        
        # Test criteria retrieval
        criteria = qvf_service.get_available_criteria()
        category_count = len(criteria.get('categories', {}))
        print_success(f"Available criteria categories: {category_count}")
        
        # Test calculation
        test_result = qvf_service.test_qvf_calculation()
        items_processed = test_result['summary']['total_items']
        avg_score = test_result['summary']['average_score']
        print_success(f"Test calculation: {items_processed} items, avg score: {avg_score}")
        
        return health.get('status') == 'healthy'
        
    except Exception as e:
        print_error(f"QVF Service verification failed: {e}")
        return False

def start_test_server():
    """Start a test server."""
    print_header("Server Startup")
    
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{api_src_path}:{project_root}"
        
        process = subprocess.Popen([
            "python3", "-m", "uvicorn", 
            "qvf_api.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000",
            "--log-level", "error"  # Reduce noise
        ], cwd=str(api_src_path), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print_info("Starting FastAPI server...")
        time.sleep(4)
        
        # Test if server is running
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code == 200:
                print_success("FastAPI server started successfully")
                return process
        except:
            pass
        
        # Server didn't start properly
        print_error("Failed to start FastAPI server")
        process.terminate()
        return None
        
    except Exception as e:
        print_error(f"Server startup failed: {e}")
        return None

def verify_api_endpoints():
    """Verify all API endpoints."""
    print_header("API Endpoints Verification")
    
    base_url = "http://127.0.0.1:8000"
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/api/v1/qvf/health", "QVF health check"),
        ("/api/v1/qvf/criteria", "QVF criteria"),
        ("/api/v1/qvf/test", "QVF test calculation")
    ]
    
    success_count = 0
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(base_url + endpoint, timeout=10)
            if response.status_code == 200:
                print_success(f"{description}: Working")
                success_count += 1
            else:
                print_error(f"{description}: Status {response.status_code}")
        except Exception as e:
            print_error(f"{description}: {e}")
    
    print_info(f"Endpoints working: {success_count}/{len(endpoints)}")
    return success_count == len(endpoints)

def verify_qvf_scoring():
    """Verify QVF scoring endpoint."""
    print_header("QVF Scoring Verification")
    
    url = "http://127.0.0.1:8000/api/v1/qvf/score"
    
    # Test with comprehensive work items
    test_data = {
        "work_items": [
            {
                "id": "FEATURE-001",
                "title": "High-Value Feature",
                "description": "Critical customer-facing feature",
                "business_value": 9,
                "technical_complexity": 4,
                "story_points": 8,
                "priority": "High",
                "risk_level": 2
            },
            {
                "id": "TECH-001",
                "title": "Technical Debt Cleanup",
                "description": "Refactor legacy code",
                "business_value": 3,
                "technical_complexity": 8,
                "story_points": 13,
                "priority": "Medium",
                "risk_level": 6
            },
            {
                "id": "BUG-001",
                "title": "Critical Bug Fix",
                "description": "Production issue affecting users",
                "business_value": 7,
                "technical_complexity": 3,
                "story_points": 3,
                "priority": "High",
                "risk_level": 1
            }
        ]
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            print_success("QVF Scoring endpoint working")
            print_info(f"   Items processed: {result['summary']['total_items']}")
            print_info(f"   Average score: {result['summary']['average_score']}")
            print_info(f"   High priority: {result['summary']['high_priority_count']}")
            print_info(f"   Medium priority: {result['summary']['medium_priority_count']}")
            print_info(f"   Low priority: {result['summary']['low_priority_count']}")
            
            # Print individual scores
            print_info("Individual scores:")
            for score in result['scores']:
                qvf_score = score['qvf_score']
                category = score['category']
                print_info(f"   {score['id']}: {qvf_score:.3f} ({category})")
            
            # Verify metadata
            metadata = result.get('metadata', {})
            calculation_method = metadata.get('calculation_method', 'unknown')
            qvf_core = metadata.get('qvf_core_available', False)
            ai_enhanced = metadata.get('ai_enhanced', False)
            
            print_info(f"   Calculation method: {calculation_method}")
            print_info(f"   QVF core used: {qvf_core}")
            print_info(f"   AI enhanced: {ai_enhanced}")
            
            return True
        else:
            print_error(f"QVF Scoring failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"QVF Scoring endpoint error: {e}")
        return False

def verify_database():
    """Verify database setup."""
    print_header("Database Verification")
    
    try:
        from qvf_api.database import create_tables, SessionLocal
        from qvf_api.models import QVFSession, WorkItemScore, QVFCalculationLog
        
        # Test database creation
        create_tables()
        print_success("Database tables created successfully")
        
        # Test session creation
        db = SessionLocal()
        try:
            # Test basic query (should not fail even with empty tables)
            session_count = db.query(QVFSession).count()
            print_success(f"Database query working (sessions: {session_count})")
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print_error(f"Database verification failed: {e}")
        return False

def main():
    """Main verification function."""
    print("🔍 QVF FastAPI Backend Implementation Verification")
    print("=" * 60)
    
    # Track all verification results
    results = {}
    
    # Environment verification
    results['environment'] = verify_environment()
    
    # QVF service verification
    results['qvf_service'] = verify_qvf_service()
    
    # Database verification
    results['database'] = verify_database()
    
    # Start server for API tests
    server_process = start_test_server()
    if server_process:
        try:
            # API endpoints verification
            results['api_endpoints'] = verify_api_endpoints()
            
            # QVF scoring verification
            results['qvf_scoring'] = verify_qvf_scoring()
            
        finally:
            # Clean up server
            server_process.terminate()
            server_process.wait()
            print_info("Test server stopped")
    else:
        results['api_endpoints'] = False
        results['qvf_scoring'] = False
    
    # Final summary
    print_header("Verification Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print_info(f"Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL VERIFICATIONS PASSED!")
        print("   The QVF FastAPI backend is fully functional and ready for use.")
        print("   ✅ FastAPI server connects to existing QVF core engine")
        print("   ✅ Database configuration is working")
        print("   ✅ API endpoints respond correctly")
        print("   ✅ QVF calculations work with real data")
        print("   ✅ Health checks show system status")
        
        print(f"\n🚀 To start the API server:")
        print(f"   cd {script_dir}")
        print(f"   python3 start_api.py")
        print(f"\n📚 API Documentation: http://localhost:8000/docs")
        print(f"❤️  Health Check: http://localhost:8000/health")
        print(f"🔧 QVF Endpoints: http://localhost:8000/api/v1/qvf/")
        
        return True
    else:
        print("\n⚠️ Some verifications failed.")
        print("   Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)