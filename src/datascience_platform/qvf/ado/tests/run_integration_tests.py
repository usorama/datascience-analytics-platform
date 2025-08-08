"""ADO Integration Test Runner

This script runs comprehensive tests for Azure DevOps REST API integration
and provides detailed reporting on test results, performance metrics, and
coverage analysis.

Usage:
    python run_integration_tests.py [--verbose] [--coverage] [--performance]
    
Features:
- Comprehensive test execution for REST client and work items manager
- Performance benchmarking and metrics collection
- Code coverage reporting
- Integration test validation
- Mock ADO environment simulation
"""

import asyncio
import time
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone

# Test framework imports
import pytest
import coverage

# Logging setup
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestExecutionResult:
    """Container for test execution results and metrics."""
    
    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
        self.end_time = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_skipped = 0
        self.execution_time_seconds = 0.0
        self.coverage_percentage = 0.0
        self.performance_metrics = {}
        self.error_details = []
        self.success_rate = 0.0
    
    def mark_completed(self):
        """Mark test execution as completed."""
        self.end_time = datetime.now(timezone.utc)
        self.execution_time_seconds = (self.end_time - self.start_time).total_seconds()
        if self.tests_run > 0:
            self.success_rate = (self.tests_passed / self.tests_run) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary format."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time_seconds": self.execution_time_seconds,
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "tests_skipped": self.tests_skipped,
            "success_rate": self.success_rate,
            "coverage_percentage": self.coverage_percentage,
            "performance_metrics": self.performance_metrics,
            "error_details": self.error_details
        }


class ADOIntegrationTestRunner:
    """Comprehensive test runner for ADO integration components."""
    
    def __init__(self, verbose: bool = False, coverage_enabled: bool = False):
        self.verbose = verbose
        self.coverage_enabled = coverage_enabled
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent.parent.parent
        
        # Initialize coverage if enabled
        self.cov = None
        if coverage_enabled:
            self.cov = coverage.Coverage(
                source=['datascience_platform.qvf.ado'],
                omit=['*/tests/*', '*/test_*.py']
            )
        
        logger.info(f"Test runner initialized. Coverage: {coverage_enabled}, Verbose: {verbose}")
    
    def run_all_tests(self) -> TestExecutionResult:
        """Run all ADO integration tests with comprehensive reporting."""
        result = TestExecutionResult()
        
        try:
            logger.info("Starting ADO integration test execution...")
            
            if self.cov:
                self.cov.start()
            
            # Run tests with pytest
            pytest_args = [
                str(self.test_dir),
                "-v" if self.verbose else "-q",
                "--tb=short",
                "--disable-warnings",
                "-x",  # Stop on first failure
                "--durations=10"  # Show slowest 10 tests
            ]
            
            # Run pytest and capture results
            exit_code = pytest.main(pytest_args)
            
            if self.cov:
                self.cov.stop()
                self.cov.save()
                result.coverage_percentage = self._get_coverage_percentage()
            
            # Parse pytest results (simplified)
            if exit_code == 0:
                result.tests_passed = self._count_tests()
                result.tests_run = result.tests_passed
                logger.info(f"✅ All tests passed! ({result.tests_passed} tests)")
            else:
                result.tests_failed = 1
                result.tests_run = 1
                result.error_details.append(f"Test execution failed with exit code: {exit_code}")
                logger.error(f"❌ Test execution failed with exit code: {exit_code}")
            
            result.mark_completed()
            
        except Exception as e:
            logger.error(f"Error during test execution: {e}")
            result.error_details.append(str(e))
            result.tests_failed = 1
            result.tests_run = 1
            result.mark_completed()
        
        return result
    
    def run_performance_benchmark(self) -> Dict[str, Any]:
        """Run performance benchmarks for ADO integration components."""
        logger.info("Running performance benchmarks...")
        
        benchmark_results = {
            "rest_client_performance": self._benchmark_rest_client(),
            "work_items_performance": self._benchmark_work_items(),
            "batch_processing_performance": self._benchmark_batch_processing()
        }
        
        logger.info("Performance benchmarks completed")
        return benchmark_results
    
    def _benchmark_rest_client(self) -> Dict[str, float]:
        """Benchmark REST client performance."""
        from datascience_platform.qvf.ado.rest_client import ADOClientConfig, RateLimiter
        
        # Test configuration creation performance
        start_time = time.time()
        for _ in range(1000):
            config = ADOClientConfig(
                organization_url="https://dev.azure.com/testorg",
                personal_access_token="test_pat"
            )
        config_creation_time = (time.time() - start_time) * 1000  # milliseconds
        
        # Test rate limiter performance
        start_time = time.time()
        limiter = RateLimiter(requests_per_minute=600)
        for _ in range(100):
            # Simulate token consumption
            if limiter.tokens > 0:
                limiter.tokens -= 1
        rate_limiter_time = (time.time() - start_time) * 1000
        
        return {
            "config_creation_time_ms": config_creation_time,
            "rate_limiter_time_ms": rate_limiter_time,
            "config_creation_per_sec": 1000 / (config_creation_time / 1000),
            "rate_limiter_ops_per_sec": 100 / (rate_limiter_time / 1000)
        }
    
    def _benchmark_work_items(self) -> Dict[str, float]:
        """Benchmark work items manager performance."""
        from datascience_platform.qvf.ado.work_items import QVFWorkItemScore
        
        # Test QVF score creation performance
        start_time = time.time()
        scores = []
        for i in range(1000):
            score = QVFWorkItemScore(
                work_item_id=i,
                overall_score=0.5 + (i % 50) / 100,
                configuration_id="benchmark_test"
            )
            scores.append(score)
        score_creation_time = (time.time() - start_time) * 1000
        
        # Test field updates generation performance
        start_time = time.time()
        for score in scores[:100]:  # Test subset for field updates
            field_updates = score.to_field_updates()
        field_updates_time = (time.time() - start_time) * 1000
        
        return {
            "score_creation_time_ms": score_creation_time,
            "field_updates_time_ms": field_updates_time,
            "scores_created_per_sec": 1000 / (score_creation_time / 1000),
            "field_updates_per_sec": 100 / (field_updates_time / 1000)
        }
    
    def _benchmark_batch_processing(self) -> Dict[str, float]:
        """Benchmark batch processing performance."""
        from datascience_platform.qvf.ado.work_items import WorkItemUpdateBatch, QVFWorkItemScore
        
        # Create test data
        scores = {}
        for i in range(500):
            scores[i] = QVFWorkItemScore(
                work_item_id=i,
                overall_score=0.7,
                configuration_id="batch_test"
            )
        
        # Test batch creation performance
        start_time = time.time()
        batches = []
        batch_size = 50
        for batch_start in range(0, len(scores), batch_size):
            batch_end = min(batch_start + batch_size, len(scores))
            batch_scores = {
                wid: scores[wid] 
                for wid in list(scores.keys())[batch_start:batch_end]
            }
            
            batch = WorkItemUpdateBatch(
                batch_id=f"batch_{len(batches)}",
                project_name="benchmark",
                work_item_scores=batch_scores
            )
            batches.append(batch)
        batch_creation_time = (time.time() - start_time) * 1000
        
        return {
            "batch_creation_time_ms": batch_creation_time,
            "batches_created": len(batches),
            "items_per_batch": batch_size,
            "batches_per_second": len(batches) / (batch_creation_time / 1000)
        }
    
    def _get_coverage_percentage(self) -> float:
        """Get code coverage percentage."""
        if not self.cov:
            return 0.0
        
        try:
            # Generate coverage report and extract percentage
            total_coverage = self.cov.report(file=None, show_missing=False)
            return round(total_coverage, 2)
        except Exception as e:
            logger.warning(f"Could not calculate coverage: {e}")
            return 0.0
    
    def _count_tests(self) -> int:
        """Count total number of tests in test files."""
        test_count = 0
        
        for test_file in self.test_dir.glob("test_*.py"):
            with open(test_file, 'r') as f:
                content = f.read()
                # Simple count of test functions
                test_count += content.count("def test_")
        
        return test_count
    
    def generate_report(self, result: TestExecutionResult, performance_metrics: Dict[str, Any]) -> str:
        """Generate comprehensive test report."""
        report_lines = [
            "="*80,
            "ADO INTEGRATION TEST REPORT",
            "="*80,
            "",
            f"📅 Execution Date: {result.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"⏱️  Execution Time: {result.execution_time_seconds:.2f} seconds",
            f"✅ Tests Passed: {result.tests_passed}",
            f"❌ Tests Failed: {result.tests_failed}",
            f"⏭️  Tests Skipped: {result.tests_skipped}",
            f"📊 Success Rate: {result.success_rate:.1f}%",
            "",
            "COMPONENT COVERAGE:",
            "-"*20,
            f"📈 Code Coverage: {result.coverage_percentage:.1f}%",
            "",
            "PERFORMANCE BENCHMARKS:",
            "-"*25
        ]
        
        # Add performance metrics
        if "rest_client_performance" in performance_metrics:
            rest_perf = performance_metrics["rest_client_performance"]
            report_lines.extend([
                "🔌 REST Client Performance:",
                f"   • Config Creation: {rest_perf['config_creation_per_sec']:.0f} configs/sec",
                f"   • Rate Limiter: {rest_perf['rate_limiter_ops_per_sec']:.0f} ops/sec",
                ""
            ])
        
        if "work_items_performance" in performance_metrics:
            work_perf = performance_metrics["work_items_performance"]
            report_lines.extend([
                "📋 Work Items Performance:",
                f"   • Score Creation: {work_perf['scores_created_per_sec']:.0f} scores/sec",
                f"   • Field Updates: {work_perf['field_updates_per_sec']:.0f} updates/sec",
                ""
            ])
        
        if "batch_processing_performance" in performance_metrics:
            batch_perf = performance_metrics["batch_processing_performance"]
            report_lines.extend([
                "🔄 Batch Processing Performance:",
                f"   • Batch Creation: {batch_perf['batches_per_second']:.0f} batches/sec",
                f"   • Batches Created: {batch_perf['batches_created']}",
                ""
            ])
        
        # Add error details if any
        if result.error_details:
            report_lines.extend([
                "ERROR DETAILS:",
                "-"*15
            ])
            for i, error in enumerate(result.error_details, 1):
                report_lines.append(f"{i}. {error}")
        
        # Add summary
        status_emoji = "✅" if result.tests_failed == 0 else "❌"
        report_lines.extend([
            "",
            "SUMMARY:",
            "-"*10,
            f"{status_emoji} Overall Status: {'PASSED' if result.tests_failed == 0 else 'FAILED'}",
            f"📊 Total Test Coverage: {result.coverage_percentage:.1f}%",
            f"⚡ Performance Rating: {'Excellent' if all(perf.get('batches_per_second', 0) > 10 for perf in performance_metrics.values() if isinstance(perf, dict)) else 'Good'}",
            "",
            "="*80
        ])
        
        return "\n".join(report_lines)
    
    def save_results(self, result: TestExecutionResult, performance_metrics: Dict[str, Any]):
        """Save test results to files."""
        results_dir = self.project_root / "test_results"
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = results_dir / f"ado_integration_tests_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump({
                "test_results": result.to_dict(),
                "performance_metrics": performance_metrics
            }, f, indent=2)
        
        # Save text report
        report_file = results_dir / f"ado_integration_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(self.generate_report(result, performance_metrics))
        
        logger.info(f"Results saved to: {results_dir}")


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="ADO Integration Test Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose test output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Enable code coverage")
    parser.add_argument("--performance", "-p", action="store_true", help="Run performance benchmarks")
    parser.add_argument("--save-results", "-s", action="store_true", help="Save results to files")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = ADOIntegrationTestRunner(
        verbose=args.verbose,
        coverage_enabled=args.coverage
    )
    
    print("🚀 Starting ADO Integration Tests...")
    print(f"   Coverage: {'Enabled' if args.coverage else 'Disabled'}")
    print(f"   Performance: {'Enabled' if args.performance else 'Disabled'}")
    print(f"   Verbose: {'Enabled' if args.verbose else 'Disabled'}")
    print("-" * 50)
    
    # Run tests
    test_result = runner.run_all_tests()
    
    # Run performance benchmarks if requested
    performance_metrics = {}
    if args.performance:
        performance_metrics = runner.run_performance_benchmark()
    
    # Generate and display report
    report = runner.generate_report(test_result, performance_metrics)
    print(report)
    
    # Save results if requested
    if args.save_results:
        runner.save_results(test_result, performance_metrics)
    
    # Exit with appropriate code
    exit_code = 0 if test_result.tests_failed == 0 else 1
    print(f"\n🏁 Test execution completed with exit code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)