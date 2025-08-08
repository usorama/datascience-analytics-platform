#!/usr/bin/env python3
"""QVF Deployment Test Script

This script tests the complete QVF deployment package including:
- CLI functionality
- Scoring operations  
- Configuration management
- System validation
- File I/O operations

Usage:
    python3 examples/test_qvf_deployment.py

Created: August 2025
Author: DataScience Platform Team
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd


def run_command(cmd, description):
    """Run a command and return result."""
    print(f"🧪 Testing: {description}")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True, result.stdout
        else:
            print(f"   ❌ Failed: {result.stderr}")
            return False, result.stderr
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, str(e)


def test_qvf_cli_help():
    """Test QVF CLI help functionality."""
    return run_command(
        ["python3", "-m", "src.datascience_platform.qvf", "--help"],
        "QVF CLI Help Command"
    )


def test_qvf_validation():
    """Test QVF system validation."""
    return run_command(
        ["python3", "-m", "src.datascience_platform.qvf", "validate"],
        "QVF System Validation"
    )


def test_qvf_configuration():
    """Test QVF configuration generation."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        config_path = tmp_file.name
    
    try:
        success, output = run_command(
            ["python3", "-m", "src.datascience_platform.qvf", "configure", "init", "--output", config_path],
            "QVF Configuration Generation"
        )
        
        if success and os.path.exists(config_path):
            # Verify configuration file contents
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            expected_sections = ["scoring", "criteria"]
            if all(section in config for section in expected_sections):
                print(f"   ✅ Configuration file contains expected sections")
                return True, output
            else:
                print(f"   ❌ Configuration file missing expected sections")
                return False, "Missing configuration sections"
        else:
            return success, output
            
    finally:
        # Cleanup
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_qvf_scoring():
    """Test QVF scoring functionality."""
    # Use the existing sample data file
    sample_file = Path(__file__).parent / "qvf_sample_workitems.csv"
    
    if not sample_file.exists():
        return False, "Sample work items file not found"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
        output_path = tmp_file.name
    
    try:
        success, output = run_command([
            "python3", "-m", "src.datascience_platform.qvf", "score",
            str(sample_file),
            "-o", output_path,
            "--preset", "enterprise"
        ], "QVF Portfolio Scoring")
        
        if success and os.path.exists(output_path):
            # Verify output file contents
            try:
                results_df = pd.read_csv(output_path)
                
                # Check for required output columns
                required_columns = ['qvf_score', 'qvf_rank', 'qvf_category']
                if all(col in results_df.columns for col in required_columns):
                    print(f"   ✅ Scored {len(results_df)} work items successfully")
                    print(f"   ✅ Output contains all required columns")
                    
                    # Check ranking is correct
                    if results_df['qvf_rank'].tolist() == list(range(1, len(results_df) + 1)):
                        print(f"   ✅ Work items properly ranked")
                        return True, output
                    else:
                        print(f"   ❌ Work item ranking is incorrect")
                        return False, "Incorrect ranking"
                else:
                    print(f"   ❌ Output missing required columns")
                    return False, "Missing required columns in output"
                    
            except Exception as e:
                print(f"   ❌ Error reading output file: {str(e)}")
                return False, str(e)
        else:
            return success, output
            
    finally:
        # Cleanup
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_deployment_scripts():
    """Test deployment scripts exist and are executable."""
    scripts = [
        "scripts/deploy_qvf.py",
        "scripts/verify_qvf_deployment.py"
    ]
    
    project_root = Path(__file__).parent.parent
    all_exist = True
    
    for script_path in scripts:
        full_path = project_root / script_path
        if full_path.exists() and os.access(full_path, os.X_OK):
            print(f"   ✅ {script_path} exists and is executable")
        else:
            print(f"   ❌ {script_path} missing or not executable")
            all_exist = False
    
    return all_exist, "Deployment scripts check"


def test_package_imports():
    """Test QVF package imports."""
    try:
        # Test core imports
        from src.datascience_platform.qvf.core.criteria import QVFCriteriaEngine, create_enterprise_configuration
        from src.datascience_platform.qvf.core.financial import FinancialCalculator
        
        # Test instantiation
        criteria_engine = QVFCriteriaEngine()
        financial_calc = FinancialCalculator()
        config = create_enterprise_configuration()
        
        if criteria_engine and financial_calc and config:
            print("   ✅ QVF core modules import and instantiate successfully")
            return True, "Import test successful"
        else:
            print("   ❌ Failed to instantiate QVF components")
            return False, "Instantiation failed"
            
    except ImportError as e:
        print(f"   ❌ Import error: {str(e)}")
        return False, str(e)
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False, str(e)


def test_configuration_files():
    """Test configuration files exist and are valid."""
    config_files = [
        "config/qvf_production.json",
        "config/qvf_development.json"
    ]
    
    project_root = Path(__file__).parent.parent
    all_valid = True
    
    for config_file in config_files:
        full_path = project_root / config_file
        
        if full_path.exists():
            try:
                with open(full_path, 'r') as f:
                    config = json.load(f)
                
                # Check required sections
                if "ado" in config and "scoring" in config:
                    print(f"   ✅ {config_file} exists and is valid JSON")
                else:
                    print(f"   ❌ {config_file} missing required sections")
                    all_valid = False
                    
            except json.JSONDecodeError:
                print(f"   ❌ {config_file} contains invalid JSON")
                all_valid = False
        else:
            print(f"   ❌ {config_file} does not exist")
            all_valid = False
    
    return all_valid, "Configuration files check"


def main():
    """Main test execution."""
    print("🚀 QVF Deployment Package Test Suite")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_package_imports),
        ("QVF CLI Help", test_qvf_cli_help),
        ("QVF System Validation", test_qvf_validation),
        ("QVF Configuration", test_qvf_configuration),
        ("QVF Scoring", test_qvf_scoring),
        ("Deployment Scripts", test_deployment_scripts),
        ("Configuration Files", test_configuration_files),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            success, message = test_func()
            results.append((test_name, success, message))
            
            if success:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Test failed with exception: {str(e)}")
            results.append((test_name, False, str(e)))
            failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 QVF Test Summary")
    print("=" * 50)
    
    for test_name, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not success:
            print(f"         {message}")
    
    print(f"\n📈 Results: {passed} passed, {failed} failed, {passed + failed} total")
    
    if failed == 0:
        print("\n🎉 All QVF deployment tests passed successfully!")
        print("🚀 QVF system is ready for deployment.")
        return 0
    else:
        print(f"\n💥 {failed} test(s) failed. Please review and fix issues before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())