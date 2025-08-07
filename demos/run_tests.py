#!/usr/bin/env python3
"""Comprehensive test runner for the DataScience Analytics Platform.

This script orchestrates the complete test suite including:
- Unit tests
- Integration tests  
- Performance tests
- Coverage reporting
- Test result analysis
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import webbrowser
from dataclasses import dataclass


@dataclass
class TestResult:
    """Test execution result."""
    success: bool
    exit_code: int
    duration: float
    output: str
    coverage_percent: Optional[float] = None


class TestRunner:
    """Comprehensive test runner with coverage and reporting."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize test runner.
        
        Args:
            project_root: Project root directory. Auto-detected if None.
        """
        self.project_root = project_root or Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        self.src_dir = self.project_root / "src"
        self.reports_dir = self.project_root / "test_reports"
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(exist_ok=True)
        
        # Test suite configuration
        self.test_suites = {
            'unit': {
                'path': 'tests/unit',
                'markers': '-m "unit"',
                'timeout': 300,  # 5 minutes
                'description': 'Fast unit tests for individual components'
            },
            'integration': {
                'path': 'tests/integration',
                'markers': '-m "integration"',
                'timeout': 600,  # 10 minutes
                'description': 'Integration tests for component interactions'
            },
            'performance': {
                'path': 'tests/performance',
                'markers': '-m "performance"',
                'timeout': 1800,  # 30 minutes
                'description': 'Performance and benchmark tests'
            },
            'all': {
                'path': 'tests',
                'markers': '',
                'timeout': 2400,  # 40 minutes
                'description': 'Complete test suite'
            }
        }
    
    def run_pytest(self, 
                   test_path: str = "tests", 
                   markers: str = "",
                   coverage: bool = True,
                   verbose: bool = True,
                   timeout: int = 300,
                   extra_args: List[str] = None) -> TestResult:
        """Run pytest with specified configuration.
        
        Args:
            test_path: Path to test directory or file
            markers: Pytest markers to filter tests
            coverage: Enable coverage reporting
            verbose: Enable verbose output
            timeout: Test timeout in seconds
            extra_args: Additional pytest arguments
            
        Returns:
            TestResult with execution details
        """
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test path
        cmd.append(test_path)
        
        # Add markers
        if markers:
            cmd.extend(markers.split())
        
        # Coverage configuration
        if coverage:
            cmd.extend([
                "--cov=src/datascience_platform",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-report=json:coverage.json",
                f"--cov-fail-under=80"
            ])
        
        # Verbosity and formatting
        if verbose:
            cmd.extend(["-v", "--tb=short"])
        else:
            cmd.extend(["-q"])
        
        # Additional pytest options
        cmd.extend([
            "--strict-markers",
            "--disable-warnings",
            "--durations=10",  # Show 10 slowest tests
            f"--timeout={timeout}"
        ])
        
        # Add extra arguments
        if extra_args:
            cmd.extend(extra_args)
        
        print(f"Running: {' '.join(cmd)}")
        print("-" * 80)
        
        # Execute tests
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout + 60  # Buffer for cleanup
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            # Extract coverage percentage if available
            coverage_percent = None
            if coverage and success:
                coverage_percent = self._extract_coverage_percent(result.stdout)
            
            return TestResult(
                success=success,
                exit_code=result.returncode,
                duration=duration,
                output=result.stdout + result.stderr,
                coverage_percent=coverage_percent
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestResult(
                success=False,
                exit_code=-1,
                duration=duration,
                output=f"Tests timed out after {timeout} seconds"
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                success=False,
                exit_code=-2,
                duration=duration,
                output=f"Test execution failed: {str(e)}"
            )
    
    def _extract_coverage_percent(self, output: str) -> Optional[float]:
        """Extract coverage percentage from pytest output."""
        lines = output.split('\n')
        for line in lines:
            if 'TOTAL' in line and '%' in line:
                # Look for pattern like "TOTAL    1234    567    46%"
                parts = line.split()
                for part in parts:
                    if part.endswith('%'):
                        try:
                            return float(part[:-1])
                        except ValueError:
                            continue
        return None
    
    def run_test_suite(self, suite_name: str = "all", **kwargs) -> TestResult:
        """Run a specific test suite.
        
        Args:
            suite_name: Name of test suite to run
            **kwargs: Additional arguments passed to run_pytest
            
        Returns:
            TestResult with execution details
        """
        if suite_name not in self.test_suites:
            raise ValueError(f"Unknown test suite: {suite_name}. Available: {list(self.test_suites.keys())}")
        
        suite_config = self.test_suites[suite_name]
        
        print(f"\n{'='*80}")
        print(f"Running {suite_name.upper()} Test Suite")
        print(f"Description: {suite_config['description']}")
        print(f"Path: {suite_config['path']}")
        print(f"{'='*80}")
        
        # Merge suite config with provided kwargs
        run_kwargs = {
            'test_path': suite_config['path'],
            'markers': suite_config['markers'],
            'timeout': suite_config['timeout'],
            **kwargs
        }
        
        return self.run_pytest(**run_kwargs)
    
    def run_quick_tests(self) -> TestResult:
        """Run quick tests for development feedback."""
        print("\n" + "="*80)
        print("QUICK TEST RUN - Unit Tests Only")
        print("="*80)
        
        return self.run_test_suite(
            'unit',
            coverage=False,
            verbose=False,
            extra_args=['--maxfail=5']  # Stop after 5 failures
        )
    
    def run_full_suite(self) -> Dict[str, TestResult]:
        """Run the complete test suite with detailed reporting.
        
        Returns:
            Dictionary mapping suite names to their results
        """
        results = {}
        
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST SUITE EXECUTION")
        print("="*80)
        
        # Run test suites in order
        suite_order = ['unit', 'integration']  # Skip performance by default for speed
        
        for suite_name in suite_order:
            print(f"\n🧪 Starting {suite_name} tests...")
            
            try:
                result = self.run_test_suite(suite_name, coverage=(suite_name == 'unit'))
                results[suite_name] = result
                
                if result.success:
                    print(f"✅ {suite_name} tests PASSED ({result.duration:.1f}s)")
                    if result.coverage_percent:
                        print(f"📊 Coverage: {result.coverage_percent:.1f}%")
                else:
                    print(f"❌ {suite_name} tests FAILED ({result.duration:.1f}s)")
                    print(f"Exit code: {result.exit_code}")
                    
                    # Optionally continue or stop on failure
                    if suite_name == 'unit':
                        print("⚠️  Unit tests failed - continuing with integration tests")
                    
            except Exception as e:
                print(f"💥 {suite_name} test execution error: {str(e)}")
                results[suite_name] = TestResult(
                    success=False,
                    exit_code=-3,
                    duration=0,
                    output=str(e)
                )
        
        return results
    
    def generate_report(self, results: Dict[str, TestResult]) -> Path:
        """Generate comprehensive test report.
        
        Args:
            results: Dictionary of test results
            
        Returns:
            Path to generated report file
        """
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'project_root': str(self.project_root),
            'python_version': sys.version,
            'results': {}
        }
        
        total_duration = 0
        all_passed = True
        
        for suite_name, result in results.items():
            report_data['results'][suite_name] = {
                'success': result.success,
                'exit_code': result.exit_code,
                'duration': result.duration,
                'coverage_percent': result.coverage_percent,
                'output_lines': len(result.output.split('\n'))
            }
            
            total_duration += result.duration
            if not result.success:
                all_passed = False
        
        report_data['summary'] = {
            'all_passed': all_passed,
            'total_duration': total_duration,
            'suites_run': len(results),
            'average_coverage': self._calculate_average_coverage(results)
        }
        
        # Save JSON report
        json_report_path = self.reports_dir / f"test_report_{int(time.time())}.json"
        with open(json_report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Generate HTML report
        html_report_path = self._generate_html_report(report_data)
        
        return html_report_path
    
    def _calculate_average_coverage(self, results: Dict[str, TestResult]) -> Optional[float]:
        """Calculate average coverage across test suites."""
        coverage_values = [r.coverage_percent for r in results.values() if r.coverage_percent is not None]
        return sum(coverage_values) / len(coverage_values) if coverage_values else None
    
    def _generate_html_report(self, report_data: Dict) -> Path:
        """Generate HTML test report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>DataScience Platform Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .suite {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ background-color: #d4edda; border-color: #c3e6cb; }}
        .failure {{ background-color: #f8d7da; border-color: #f5c6cb; }}
        .metric {{ display: inline-block; margin: 10px 15px 10px 0; }}
        .coverage {{ font-weight: bold; color: #007bff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 DataScience Analytics Platform - Test Report</h1>
        <p><strong>Generated:</strong> {report_data['timestamp']}</p>
        <p><strong>Python:</strong> {report_data['python_version'].split()[0]}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <div class="metric">
            <strong>Status:</strong> 
            {'✅ ALL PASSED' if report_data['summary']['all_passed'] else '❌ SOME FAILED'}
        </div>
        <div class="metric">
            <strong>Total Duration:</strong> {report_data['summary']['total_duration']:.1f}s
        </div>
        <div class="metric">
            <strong>Suites Run:</strong> {report_data['summary']['suites_run']}
        </div>
        {f'<div class="metric coverage">Coverage: {report_data["summary"]["average_coverage"]:.1f}%</div>' 
         if report_data['summary']['average_coverage'] else ''}
    </div>
    
    <h2>🔍 Test Suite Details</h2>
"""
        
        for suite_name, result in report_data['results'].items():
            status_class = 'success' if result['success'] else 'failure'
            status_icon = '✅' if result['success'] else '❌'
            
            html_content += f"""
    <div class="suite {status_class}">
        <h3>{status_icon} {suite_name.title()} Tests</h3>
        <div class="metric"><strong>Status:</strong> {'PASSED' if result['success'] else 'FAILED'}</div>
        <div class="metric"><strong>Duration:</strong> {result['duration']:.1f}s</div>
        <div class="metric"><strong>Exit Code:</strong> {result['exit_code']}</div>
        {f'<div class="metric coverage">Coverage: {result["coverage_percent"]:.1f}%</div>' 
         if result['coverage_percent'] else ''}
    </div>
"""
        
        html_content += """
    <div class="summary">
        <h2>📁 Report Files</h2>
        <ul>
            <li><a href="htmlcov/index.html">Coverage Report</a> (if available)</li>
            <li><a href="coverage.json">Coverage JSON</a> (if available)</li>
        </ul>
    </div>
</body>
</html>
"""
        
        html_report_path = self.reports_dir / "test_report.html"
        with open(html_report_path, 'w') as f:
            f.write(html_content)
        
        return html_report_path
    
    def check_environment(self) -> List[str]:
        """Check test environment and return any issues."""
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append(f"Python 3.8+ required, found {sys.version}")
        
        # Check required directories
        if not self.test_dir.exists():
            issues.append(f"Test directory not found: {self.test_dir}")
        
        if not self.src_dir.exists():
            issues.append(f"Source directory not found: {self.src_dir}")
        
        # Check pytest installation
        try:
            import pytest
            if hasattr(pytest, '__version__'):
                print(f"✅ pytest {pytest.__version__} available")
        except ImportError:
            issues.append("pytest not installed")
        
        # Check coverage plugin
        try:
            import pytest_cov
            print("✅ pytest-cov available")
        except ImportError:
            issues.append("pytest-cov not installed (coverage reporting disabled)")
        
        return issues


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for DataScience Analytics Platform"
    )
    
    parser.add_argument(
        'suite',
        nargs='?',
        default='all',
        choices=['unit', 'integration', 'performance', 'all', 'quick'],
        help='Test suite to run (default: all)'
    )
    
    parser.add_argument(
        '--no-coverage',
        action='store_true',
        help='Disable coverage reporting'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        help='Test timeout in seconds'
    )
    
    parser.add_argument(
        '--open-report',
        action='store_true',
        help='Open HTML report in browser after completion'
    )
    
    parser.add_argument(
        '--check-env',
        action='store_true',
        help='Check test environment and exit'
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner()
    
    # Check environment if requested
    if args.check_env:
        print("🔍 Checking test environment...")
        issues = runner.check_environment()
        
        if issues:
            print("\n❌ Environment issues found:")
            for issue in issues:
                print(f"  • {issue}")
            return 1
        else:
            print("\n✅ Test environment looks good!")
            return 0
    
    # Run environment check
    print("🔍 Checking test environment...")
    issues = runner.check_environment()
    if issues:
        print("\n⚠️  Environment issues (continuing anyway):")
        for issue in issues:
            print(f"  • {issue}")
    
    print("\n🚀 Starting test execution...")
    
    # Execute tests based on suite selection
    if args.suite == 'quick':
        result = runner.run_quick_tests()
        results = {'quick': result}
    elif args.suite == 'all':
        results = runner.run_full_suite()
    else:
        # Run specific suite
        kwargs = {}
        if args.timeout:
            kwargs['timeout'] = args.timeout
        if args.no_coverage:
            kwargs['coverage'] = False
        if args.verbose:
            kwargs['verbose'] = True
        
        result = runner.run_test_suite(args.suite, **kwargs)
        results = {args.suite: result}
    
    # Generate report
    print("\n📄 Generating test report...")
    report_path = runner.generate_report(results)
    print(f"Report saved to: {report_path}")
    
    # Open report in browser if requested
    if args.open_report and report_path.exists():
        try:
            webbrowser.open(f"file://{report_path.absolute()}")
            print("🌐 Report opened in browser")
        except Exception as e:
            print(f"Could not open browser: {e}")
    
    # Print final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    total_duration = sum(r.duration for r in results.values())
    all_passed = all(r.success for r in results.values())
    
    for suite_name, result in results.items():
        status = "✅ PASSED" if result.success else "❌ FAILED"
        coverage_info = f" (Coverage: {result.coverage_percent:.1f}%)" if result.coverage_percent else ""
        print(f"{suite_name.upper()}: {status} in {result.duration:.1f}s{coverage_info}")
    
    print(f"\nTotal execution time: {total_duration:.1f}s")
    print(f"Overall result: {'✅ SUCCESS' if all_passed else '❌ FAILURE'}")
    
    # Exit with appropriate code
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())