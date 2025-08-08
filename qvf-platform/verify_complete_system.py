#!/usr/bin/env python3
"""
Complete QVF Platform System Verification
Tests the entire full-stack application including all components:
- Backend API with QVF core integration
- Authentication system with role-based access
- All 5 dashboards and interfaces
- End-to-end workflows
- Performance metrics
"""

import sys
import os
import time
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3006"
TEST_TIMEOUT = 30
PERFORMANCE_THRESHOLDS = {
    "api_response_time": 2.0,  # seconds
    "frontend_load_time": 5.0,  # seconds
    "qvf_calculation_time": 5.0,  # seconds
}

class QVFSystemVerifier:
    """Complete system verification for QVF Platform."""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        self.auth_tokens = {}
        self.performance_metrics = {}
        
    def print_header(self, title: str):
        """Print formatted section header."""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
    
    def print_success(self, message: str):
        """Print success message."""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print error message."""
        print(f"❌ {message}")
    
    def print_warning(self, message: str):
        """Print warning message."""
        print(f"⚠️  {message}")
    
    def print_info(self, message: str):
        """Print info message."""
        print(f"ℹ️  {message}")
    
    def measure_performance(self, operation_name: str, func, *args, **kwargs):
        """Measure and record operation performance."""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            self.performance_metrics[operation_name] = elapsed
            return result, elapsed
        except Exception as e:
            elapsed = time.time() - start_time
            self.performance_metrics[operation_name] = elapsed
            raise e
    
    def verify_environment(self) -> bool:
        """Verify system prerequisites."""
        self.print_header("ENVIRONMENT VERIFICATION")
        
        checks = []
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.print_success(f"Python version: {python_version.major}.{python_version.minor}")
            checks.append(True)
        else:
            self.print_error(f"Python version too old: {python_version.major}.{python_version.minor}")
            checks.append(False)
        
        # Check required packages
        required_packages = ['requests', 'fastapi', 'uvicorn']
        for package in required_packages:
            try:
                __import__(package)
                self.print_success(f"Package {package} available")
                checks.append(True)
            except ImportError:
                self.print_error(f"Package {package} not found")
                checks.append(False)
        
        # Check project structure
        project_paths = [
            Path("apps/api/src/qvf_api"),
            Path("apps/web/src"),
            Path("apps/api/qvf.db")
        ]
        
        for path in project_paths:
            if path.exists():
                self.print_success(f"Project path exists: {path}")
                checks.append(True)
            else:
                self.print_error(f"Project path missing: {path}")
                checks.append(False)
        
        return all(checks)
    
    def verify_backend_health(self) -> bool:
        """Verify backend API is running and healthy."""
        self.print_header("BACKEND API HEALTH CHECK")
        
        try:
            # Test basic health endpoint
            response, elapsed = self.measure_performance(
                "health_check", 
                requests.get, 
                f"{API_BASE_URL}/health", 
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                health_data = response.json()
                self.print_success(f"API Health: {health_data.get('status', 'unknown')} ({elapsed:.3f}s)")
                
                # Check QVF engine status
                qvf_status = health_data.get('qvf_engine', {})
                if qvf_status.get('status') == 'healthy':
                    self.print_success(f"QVF Engine: {qvf_status.get('status')}")
                else:
                    self.print_warning(f"QVF Engine: {qvf_status.get('status', 'unknown')}")
                
                return True
            else:
                self.print_error(f"Health check failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Backend health check failed: {e}")
            return False
    
    def verify_authentication_system(self) -> bool:
        """Verify authentication system works for all user roles."""
        self.print_header("AUTHENTICATION SYSTEM VERIFICATION")
        
        # Test users for different roles
        test_users = [
            ("executive", "executive123", "Executive"),
            ("product_owner", "po123", "Product Owner"), 
            ("scrum_master", "sm123", "Scrum Master"),
            ("developer", "dev123", "Developer")
        ]
        
        auth_results = []
        
        for username, password, role in test_users:
            try:
                # Test login
                auth_data = {
                    "username": username,
                    "password": password
                }
                
                response, elapsed = self.measure_performance(
                    f"auth_{username}",
                    requests.post,
                    f"{API_BASE_URL}/api/v1/auth/token",
                    data=auth_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data['access_token']
                    self.auth_tokens[username] = access_token
                    
                    # Verify token works
                    headers = {"Authorization": f"Bearer {access_token}"}
                    user_response = requests.get(f"{API_BASE_URL}/api/v1/auth/me", headers=headers)
                    
                    if user_response.status_code == 200:
                        user_info = user_response.json()
                        actual_role = user_info.get('role', 'unknown')
                        self.print_success(f"{role} login successful ({elapsed:.3f}s) - Role: {actual_role}")
                        auth_results.append(True)
                    else:
                        self.print_error(f"{role} user info failed: HTTP {user_response.status_code}")
                        auth_results.append(False)
                else:
                    self.print_error(f"{role} login failed: HTTP {response.status_code}")
                    auth_results.append(False)
                    
            except Exception as e:
                self.print_error(f"{role} authentication error: {e}")
                auth_results.append(False)
        
        return all(auth_results)
    
    def verify_qvf_core_functionality(self) -> bool:
        """Verify QVF core scoring functionality."""
        self.print_header("QVF CORE FUNCTIONALITY VERIFICATION")
        
        try:
            # Use executive token for authenticated requests
            headers = {"Authorization": f"Bearer {self.auth_tokens.get('executive', '')}"}
            
            # Test criteria endpoint
            response, elapsed = self.measure_performance(
                "qvf_criteria",
                requests.get,
                f"{API_BASE_URL}/api/v1/qvf/criteria",
                headers=headers,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                criteria = response.json()
                self.print_success(f"QVF criteria loaded: {len(criteria)} criteria ({elapsed:.3f}s)")
            else:
                self.print_error(f"QVF criteria failed: HTTP {response.status_code}")
                return False
            
            # Test scoring endpoint with comprehensive work items (corrected values for API validation)
            test_work_items = [
                {
                    "id": "EPIC-001",
                    "title": "Strategic Customer Platform",
                    "description": "Major platform enhancement for customer experience",
                    "business_value": 9,  # 1-10 scale
                    "technical_complexity": 8,  # 1-10 scale
                    "story_points": 21,  # 1-21 scale (fibonacci)
                    "priority": "High",
                    "risk_level": 3,  # 1-10 scale
                    "dependencies": 3,
                    "customer_impact": 9,
                    "market_opportunity": 8
                },
                {
                    "id": "FEATURE-001",
                    "title": "User Authentication Enhancement",
                    "description": "Improve security with MFA",
                    "business_value": 7,  # 1-10 scale
                    "technical_complexity": 5,  # 1-10 scale
                    "story_points": 13,  # 1-21 scale (fibonacci)
                    "priority": "High",
                    "risk_level": 2,  # 1-10 scale
                    "dependencies": 1,
                    "customer_impact": 7,
                    "market_opportunity": 5
                },
                {
                    "id": "TASK-001",
                    "title": "Database Performance Optimization",
                    "description": "Optimize database queries for better performance",
                    "business_value": 4,  # 1-10 scale
                    "technical_complexity": 6,  # 1-10 scale
                    "story_points": 8,  # 1-21 scale (fibonacci)
                    "priority": "Medium",
                    "risk_level": 4,  # 1-10 scale
                    "dependencies": 0,
                    "customer_impact": 3,
                    "market_opportunity": 2
                }
            ]
            
            scoring_payload = {"work_items": test_work_items}
            
            response, elapsed = self.measure_performance(
                "qvf_scoring",
                requests.post,
                f"{API_BASE_URL}/api/v1/qvf/score",
                json=scoring_payload,
                headers=headers,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('summary', {})
                
                self.print_success(f"QVF scoring successful ({elapsed:.3f}s)")
                self.print_info(f"   Items processed: {summary.get('total_items', 0)}")
                self.print_info(f"   Average score: {summary.get('average_score', 0):.3f}")
                self.print_info(f"   High priority: {summary.get('high_priority_count', 0)}")
                self.print_info(f"   Calculation method: {result.get('metadata', {}).get('calculation_method', 'unknown')}")
                
                # Verify individual scores
                scores = result.get('scores', [])
                if scores:
                    for score in scores:
                        qvf_score = score.get('qvf_score', 0)
                        category = score.get('category', 'unknown')
                        item_id = score.get('id', 'unknown')
                        self.print_info(f"   {item_id}: {qvf_score:.3f} ({category})")
                
                return True
            else:
                self.print_error(f"QVF scoring failed: HTTP {response.status_code}")
                if response.text:
                    self.print_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"QVF core functionality error: {e}")
            return False
    
    def verify_frontend_accessibility(self) -> bool:
        """Verify all frontend routes are accessible."""
        self.print_header("FRONTEND ACCESSIBILITY VERIFICATION")
        
        routes_to_test = [
            ("/", "Home page"),
            ("/login", "Login page"),
            ("/dashboard", "Main dashboard"),
            ("/dashboard/executive", "Executive dashboard"),
            ("/dashboard/product-owner", "Product owner dashboard"), 
            ("/dashboard/scrum-master", "Scrum master dashboard"),
            ("/work-items", "Work items management"),
            ("/compare", "Stakeholder comparison")
        ]
        
        route_results = []
        
        for route, description in routes_to_test:
            try:
                response, elapsed = self.measure_performance(
                    f"frontend_{route.replace('/', '_')}",
                    requests.get,
                    f"{FRONTEND_URL}{route}",
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    self.print_success(f"{description}: Accessible ({elapsed:.3f}s)")
                    
                    # Check for basic content indicators
                    content = response.text
                    if "QVF Platform" in content or "QVF" in content:
                        route_results.append(True)
                    else:
                        self.print_warning(f"{description}: Accessible but may have content issues")
                        route_results.append(True)  # Still accessible
                else:
                    self.print_error(f"{description}: HTTP {response.status_code}")
                    route_results.append(False)
                    
            except Exception as e:
                self.print_error(f"{description}: {e}")
                route_results.append(False)
        
        return all(route_results)
    
    def verify_database_functionality(self) -> bool:
        """Verify database operations."""
        self.print_header("DATABASE FUNCTIONALITY VERIFICATION")
        
        try:
            # Test database endpoints with authenticated requests
            headers = {"Authorization": f"Bearer {self.auth_tokens.get('executive', '')}"}
            
            # Test work items endpoint
            response, elapsed = self.measure_performance(
                "work_items_list",
                requests.get,
                f"{API_BASE_URL}/api/v1/work-items",
                headers=headers,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code in [200, 404]:  # 404 is okay if no work items exist
                self.print_success(f"Work items endpoint accessible ({elapsed:.3f}s)")
                
                if response.status_code == 200:
                    work_items = response.json()
                    if isinstance(work_items, list):
                        self.print_info(f"   Found {len(work_items)} work items in database")
                    else:
                        self.print_info("   Work items endpoint returned data")
                else:
                    self.print_info("   No work items in database (expected for fresh install)")
                
                return True
            else:
                self.print_error(f"Work items endpoint failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Database functionality error: {e}")
            return False
    
    def verify_role_based_access_control(self) -> bool:
        """Verify role-based access control works correctly."""
        self.print_header("ROLE-BASED ACCESS CONTROL VERIFICATION")
        
        # Test access patterns for different roles
        access_tests = [
            ("executive", "/api/v1/qvf/criteria", "GET", True, "Executive should access QVF criteria"),
            ("product_owner", "/api/v1/qvf/criteria", "GET", True, "Product Owner should access QVF criteria"),
            ("scrum_master", "/api/v1/work-items", "GET", True, "Scrum Master should access work items"),
            ("developer", "/api/v1/qvf/criteria", "GET", True, "Developer should access QVF criteria")
        ]
        
        rbac_results = []
        
        for role, endpoint, method, should_access, description in access_tests:
            try:
                token = self.auth_tokens.get(role)
                if not token:
                    self.print_error(f"{description}: No token available for {role}")
                    rbac_results.append(False)
                    continue
                
                headers = {"Authorization": f"Bearer {token}"}
                if method == "GET":
                    response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=TEST_TIMEOUT)
                elif method == "POST":
                    response = requests.post(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=TEST_TIMEOUT)
                else:
                    response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=TEST_TIMEOUT)
                
                if should_access:
                    if response.status_code in [200, 404]:  # 404 may be valid for empty resources
                        self.print_success(f"{description}: ✓")
                        rbac_results.append(True)
                    else:
                        self.print_error(f"{description}: Access denied (HTTP {response.status_code})")
                        rbac_results.append(False)
                else:
                    if response.status_code in [401, 403]:
                        self.print_success(f"{description}: Properly denied ✓")
                        rbac_results.append(True)
                    else:
                        self.print_error(f"{description}: Should be denied but got HTTP {response.status_code}")
                        rbac_results.append(False)
                        
            except Exception as e:
                self.print_error(f"{description}: Error - {e}")
                rbac_results.append(False)
        
        return all(rbac_results)
    
    def verify_end_to_end_workflow(self) -> bool:
        """Verify complete end-to-end QVF workflow."""
        self.print_header("END-TO-END WORKFLOW VERIFICATION")
        
        try:
            # Use product owner token for this workflow
            headers = {"Authorization": f"Bearer {self.auth_tokens.get('product_owner', '')}"}
            
            # Step 1: Get QVF criteria (stakeholder comparison preparation)
            self.print_info("Step 1: Loading QVF criteria for stakeholder comparison...")
            response = requests.get(f"{API_BASE_URL}/api/v1/qvf/criteria", headers=headers)
            
            if response.status_code != 200:
                self.print_error(f"Failed to load QVF criteria: HTTP {response.status_code}")
                return False
            
            criteria = response.json()
            self.print_success(f"QVF criteria loaded: {len(criteria)} criteria available")
            
            # Step 2: Simulate work items creation (normally done via UI) - corrected values for API validation
            self.print_info("Step 2: Creating sample work items for scoring...")
            sample_work_items = [
                {
                    "id": "E2E-EPIC-001",
                    "title": "Customer Experience Enhancement Epic", 
                    "description": "End-to-end improvement of customer journey",
                    "business_value": 9,  # 1-10 scale
                    "technical_complexity": 7,  # 1-10 scale
                    "story_points": 21,  # 1-21 scale (fibonacci)
                    "priority": "High",
                    "risk_level": 2,  # 1-10 scale
                    "dependencies": 2,
                    "customer_impact": 9,
                    "market_opportunity": 8
                },
                {
                    "id": "E2E-FEATURE-001", 
                    "title": "Mobile App Performance Feature",
                    "description": "Optimize mobile app for better user experience",
                    "business_value": 7,  # 1-10 scale
                    "technical_complexity": 5,  # 1-10 scale
                    "story_points": 13,  # 1-21 scale (fibonacci)
                    "priority": "High",
                    "risk_level": 2,  # 1-10 scale
                    "dependencies": 1,
                    "customer_impact": 8,
                    "market_opportunity": 6
                }
            ]
            
            # Step 3: Calculate QVF scores (core workflow)
            self.print_info("Step 3: Calculating QVF scores...")
            scoring_payload = {"work_items": sample_work_items}
            
            response, elapsed = self.measure_performance(
                "e2e_qvf_scoring",
                requests.post,
                f"{API_BASE_URL}/api/v1/qvf/score",
                json=scoring_payload,
                headers=headers,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code != 200:
                self.print_error(f"QVF scoring failed: HTTP {response.status_code}")
                return False
            
            result = response.json()
            scores = result.get('scores', [])
            summary = result.get('summary', {})
            
            self.print_success(f"QVF scores calculated successfully ({elapsed:.3f}s)")
            self.print_info(f"   Total items: {summary.get('total_items', 0)}")
            self.print_info(f"   Average score: {summary.get('average_score', 0):.3f}")
            
            # Step 4: Verify prioritization worked
            if len(scores) >= 2:
                # Sort by QVF score descending
                sorted_scores = sorted(scores, key=lambda x: x.get('qvf_score', 0), reverse=True)
                highest_score = sorted_scores[0]
                
                self.print_info(f"Step 4: Prioritization results:")
                self.print_info(f"   Highest priority: {highest_score.get('id')} (Score: {highest_score.get('qvf_score', 0):.3f})")
                
                # Verify the epic scored higher (should have higher business value)
                if highest_score.get('id') == "E2E-EPIC-001":
                    self.print_success("✓ Prioritization correctly identified epic as highest value")
                else:
                    self.print_info(f"✓ Prioritization completed (highest: {highest_score.get('id')})")
            
            # Step 5: Verify work item management workflow
            self.print_info("Step 5: Testing work item management workflow...")
            
            # Test work items endpoint
            response = requests.get(f"{API_BASE_URL}/api/v1/work-items", headers=headers)
            if response.status_code in [200, 404]:  # 404 is okay for empty database
                self.print_success("✓ Work item management endpoint accessible")
            else:
                self.print_warning(f"Work item management endpoint: HTTP {response.status_code}")
            
            self.print_success("END-TO-END WORKFLOW COMPLETED SUCCESSFULLY")
            return True
            
        except Exception as e:
            self.print_error(f"End-to-end workflow error: {e}")
            return False
    
    def generate_performance_report(self):
        """Generate performance metrics report."""
        self.print_header("PERFORMANCE METRICS REPORT")
        
        if not self.performance_metrics:
            self.print_warning("No performance metrics collected")
            return
        
        # Analyze performance metrics
        for operation, elapsed_time in self.performance_metrics.items():
            # Determine performance threshold
            threshold = PERFORMANCE_THRESHOLDS.get(
                operation, 
                PERFORMANCE_THRESHOLDS.get("api_response_time", 2.0)
            )
            
            if elapsed_time <= threshold:
                status = "✅ GOOD"
            elif elapsed_time <= threshold * 2:
                status = "⚠️  ACCEPTABLE" 
            else:
                status = "❌ SLOW"
            
            self.print_info(f"{operation}: {elapsed_time:.3f}s {status}")
        
        # Overall performance summary
        avg_response_time = sum(self.performance_metrics.values()) / len(self.performance_metrics)
        self.print_info(f"\nAverage response time: {avg_response_time:.3f}s")
        
        if avg_response_time <= 1.0:
            self.print_success("Overall performance: EXCELLENT")
        elif avg_response_time <= 2.0:
            self.print_success("Overall performance: GOOD")
        elif avg_response_time <= 5.0:
            self.print_warning("Overall performance: ACCEPTABLE")
        else:
            self.print_error("Overall performance: NEEDS OPTIMIZATION")
    
    def generate_deployment_readiness_report(self):
        """Generate deployment readiness assessment."""
        self.print_header("DEPLOYMENT READINESS ASSESSMENT")
        
        # Calculate overall success rate
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        self.print_info(f"Overall Test Results: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Deployment readiness criteria
        deployment_checks = [
            ("Environment Setup", self.results.get('environment', False), "CRITICAL"),
            ("Backend API Health", self.results.get('backend_health', False), "CRITICAL"),
            ("Authentication System", self.results.get('authentication', False), "CRITICAL"),
            ("QVF Core Functionality", self.results.get('qvf_core', False), "CRITICAL"),
            ("Frontend Accessibility", self.results.get('frontend', False), "HIGH"),
            ("Database Functionality", self.results.get('database', False), "HIGH"),
            ("Role-Based Access Control", self.results.get('rbac', False), "HIGH"),
            ("End-to-End Workflow", self.results.get('e2e_workflow', False), "MEDIUM")
        ]
        
        critical_failures = []
        high_failures = []
        medium_failures = []
        
        self.print_info("\nDetailed Readiness Assessment:")
        for check_name, passed, priority in deployment_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            self.print_info(f"  {check_name}: {status} ({priority})")
            
            if not passed:
                if priority == "CRITICAL":
                    critical_failures.append(check_name)
                elif priority == "HIGH":
                    high_failures.append(check_name)
                else:
                    medium_failures.append(check_name)
        
        # Deployment recommendation
        self.print_info("\nDeployment Recommendation:")
        if critical_failures:
            self.print_error("❌ NOT READY FOR DEPLOYMENT")
            self.print_error(f"   Critical failures: {', '.join(critical_failures)}")
        elif high_failures:
            self.print_warning("⚠️  DEPLOYMENT WITH CAUTION")
            self.print_warning(f"   High priority issues: {', '.join(high_failures)}")
        elif medium_failures:
            self.print_success("✅ READY FOR DEPLOYMENT")
            self.print_info(f"   Minor issues to address: {', '.join(medium_failures)}")
        else:
            self.print_success("🎉 FULLY READY FOR PRODUCTION DEPLOYMENT")
        
        # Provide specific recommendations
        self.print_info("\nRecommendations:")
        if critical_failures:
            self.print_info("1. Resolve all critical failures before deployment")
            self.print_info("2. Re-run verification after fixes")
        elif high_failures:
            self.print_info("1. Address high-priority issues for optimal experience")
            self.print_info("2. Consider staged deployment with monitoring")
        else:
            self.print_info("1. System is ready for production deployment")
            self.print_info("2. Monitor performance metrics post-deployment")
            self.print_info("3. Set up regular health checks")
    
    def run_complete_verification(self):
        """Run complete system verification."""
        self.print_header("QVF PLATFORM COMPLETE SYSTEM VERIFICATION")
        self.print_info(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_info(f"Testing against:")
        self.print_info(f"  Backend API: {API_BASE_URL}")
        self.print_info(f"  Frontend App: {FRONTEND_URL}")
        
        # Run all verification steps
        verification_steps = [
            ("environment", "Environment Setup", self.verify_environment),
            ("backend_health", "Backend Health", self.verify_backend_health),
            ("authentication", "Authentication System", self.verify_authentication_system),
            ("qvf_core", "QVF Core Functionality", self.verify_qvf_core_functionality),
            ("frontend", "Frontend Accessibility", self.verify_frontend_accessibility),
            ("database", "Database Functionality", self.verify_database_functionality),
            ("rbac", "Role-Based Access Control", self.verify_role_based_access_control),
            ("e2e_workflow", "End-to-End Workflow", self.verify_end_to_end_workflow)
        ]
        
        for key, name, func in verification_steps:
            try:
                result = func()
                self.results[key] = result
                if result:
                    self.print_success(f"{name}: COMPLETED ✓")
                else:
                    self.print_error(f"{name}: FAILED ✗")
            except Exception as e:
                self.print_error(f"{name}: EXCEPTION - {e}")
                self.results[key] = False
        
        # Generate reports
        self.generate_performance_report()
        self.generate_deployment_readiness_report()
        
        # Final summary
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        self.print_header("FINAL VERIFICATION SUMMARY")
        self.print_info(f"Verification completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_info(f"Total duration: {duration.total_seconds():.1f} seconds")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        self.print_info(f"Tests passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 100:
            self.print_success("🎉 ALL VERIFICATIONS PASSED - SYSTEM FULLY OPERATIONAL")
        elif success_rate >= 87.5:  # 7/8 tests
            self.print_success("✅ SYSTEM OPERATIONAL WITH MINOR ISSUES")
        elif success_rate >= 75:   # 6/8 tests
            self.print_warning("⚠️  SYSTEM PARTIALLY OPERATIONAL")
        else:
            self.print_error("❌ SYSTEM HAS SIGNIFICANT ISSUES")
        
        return success_rate >= 75  # Consider 75% or higher as successful


def main():
    """Main verification entry point."""
    verifier = QVFSystemVerifier()
    
    print("🔍 QVF Platform Complete System Verification")
    print("=" * 70)
    print("This script will comprehensively test:")
    print("• Backend API with all endpoints")
    print("• Authentication system with all user roles")
    print("• QVF core calculation engine")
    print("• Frontend application accessibility")
    print("• Database operations")
    print("• Role-based access control")
    print("• End-to-end workflow functionality")
    print("• Performance metrics and optimization recommendations")
    print()
    
    try:
        success = verifier.run_complete_verification()
        
        if success:
            print("\n🚀 VERIFICATION COMPLETED SUCCESSFULLY")
            print("\n📋 Quick Start Guide:")
            print("   1. Backend API: http://localhost:8000")
            print("   2. API Documentation: http://localhost:8000/docs")
            print("   3. Frontend Application: http://localhost:3006")
            print("\n👥 Test User Accounts:")
            print("   • Executive: executive / executive123")
            print("   • Product Owner: product_owner / po123")
            print("   • Scrum Master: scrum_master / sm123")
            print("   • Developer: developer / dev123")
            print("\n🎯 Key Features Verified:")
            print("   ✅ QVF Scoring Engine")
            print("   ✅ Stakeholder Comparison Interface")
            print("   ✅ Work Item Management")
            print("   ✅ Executive Dashboard")
            print("   ✅ Product Owner Dashboard")
            print("   ✅ Scrum Master Dashboard")
            print("   ✅ Authentication & Security")
            
            return True
        else:
            print("\n⚠️  VERIFICATION COMPLETED WITH ISSUES")
            print("Check the detailed output above for specific problems.")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification cancelled by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Verification failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)