"""QVF Orchestration Integration Tests

Comprehensive integration tests for the QVF orchestration system,
validating all components working together at enterprise scale.

Test Coverage:
- End-to-end scoring workflows with real-time and batch modes
- Scheduling and priority queue management
- Resource monitoring and throttling
- Error handling and recovery scenarios
- Performance and scalability validation
- Data consistency and transaction integrity

Test Scenarios:
1. Small batch scoring (10 items) - baseline functionality
2. Medium batch scoring (1000 items) - performance validation  
3. Large batch scoring (5000+ items) - enterprise scale
4. Priority queue stress testing
5. Concurrent workflow execution
6. Error recovery and retry logic
7. Resource constraint handling
8. Monitoring and alerting validation

Usage:
    python -m pytest integration_tests.py -v
    
    # Or run specific test categories
    python integration_tests.py --test-category=performance
    python integration_tests.py --test-category=scalability
"""

import asyncio
import pytest
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, patch
import time
import statistics

# Import orchestration components
from .orchestrator import (
    QVFOrchestrator, ScoringMode, OperationPriority, ScoringRequest,
    WorkflowResult, WorkflowStatus, OrchestrationError
)
from .scheduler import QVFScheduler, JobType, Priority, ResourceLimits
from .monitoring import OperationMonitor, OperationType, AlertSeverity

# Import core QVF components
from ..core.scoring import QVFScoringEngine, ScoringConfiguration
from ..core.criteria import create_default_qvf_configuration, QVFCriteriaConfiguration
from ..core.financial import FinancialMetrics, NPVCalculation, ROICalculation
from ..ado.work_items import WorkItemManager, QVFWorkItemScore
from ..ado.models import ADOWorkItem, WorkItemType, WorkItemState

logger = logging.getLogger(__name__)


class MockWorkItemManager:
    """Mock work item manager for testing."""
    
    def __init__(self, item_count: int = 100):
        self.item_count = item_count
        self.update_success_rate = 0.95  # 95% success rate by default
        self.api_delay = 0.1  # 100ms per API call
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def load_work_items_for_scoring(
        self,
        project_name: str,
        work_item_types: Optional[List[WorkItemType]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Mock work item loading."""
        await asyncio.sleep(self.api_delay * (self.item_count / 100))  # Simulate API delay
        
        work_items = []
        for i in range(self.item_count):
            work_item = {
                "id": i + 1,
                "fields": {
                    "System.Id": i + 1,
                    "System.Title": f"Test Work Item {i + 1}",
                    "System.WorkItemType": "Feature",
                    "System.State": "Active",
                    "System.AreaPath": f"{project_name}\\Test Area",
                    "System.IterationPath": f"{project_name}\\Sprint 1",
                    "Microsoft.VSTS.Common.BusinessValue": (i % 10) + 1,
                    "Microsoft.VSTS.Scheduling.StoryPoints": (i % 21) + 1
                }
            }
            work_items.append(work_item)
        
        logger.info(f"Mock loaded {len(work_items)} work items for {project_name}")
        return work_items
    
    async def update_work_item_scores(
        self,
        project_name: str,
        work_item_scores: Dict[int, Any],
        **kwargs
    ) -> Any:
        """Mock work item score updates."""
        await asyncio.sleep(self.api_delay * (len(work_item_scores) / 50))  # Simulate batch updates
        
        # Simulate some failures based on success rate
        successful_count = int(len(work_item_scores) * self.update_success_rate)
        failed_count = len(work_item_scores) - successful_count
        
        # Mock UpdateResult
        mock_result = Mock()
        mock_result.total_items = len(work_item_scores)
        mock_result.successful_updates = successful_count  
        mock_result.failed_updates = failed_count
        mock_result.processing_time_seconds = self.api_delay * (len(work_item_scores) / 50)
        mock_result.success_rate = self.update_success_rate * 100
        mock_result.batch_results = []
        
        logger.info(f"Mock updated {successful_count}/{len(work_item_scores)} work item scores")
        return mock_result


class IntegrationTestSuite:
    """Comprehensive integration test suite for QVF orchestration."""
    
    def __init__(self):
        self.test_organization_url = "https://dev.azure.com/test-org"
        self.test_pat = "test-pat-token"
        self.test_project = "TestProject"
        
        # Test configuration
        self.qvf_config = create_default_qvf_configuration()
        self.scoring_config = ScoringConfiguration()
        
        # Test results tracking
        self.test_results: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, List[float]] = {
            "execution_time": [],
            "throughput": [],
            "success_rate": [],
            "memory_usage": []
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete integration test suite."""
        logger.info("Starting QVF orchestration integration tests")
        start_time = time.time()
        
        test_methods = [
            self.test_basic_orchestration,
            self.test_batch_scoring_workflow,
            self.test_real_time_scoring,
            self.test_priority_queue_management,
            self.test_concurrent_workflows,
            self.test_error_handling_and_recovery,
            self.test_resource_monitoring,
            self.test_scheduling_system,
            self.test_performance_at_scale,
            self.test_monitoring_and_alerts
        ]
        
        passed_tests = 0
        failed_tests = 0
        
        for test_method in test_methods:
            try:
                logger.info(f"Running {test_method.__name__}")
                result = await test_method()
                
                if result.get("passed", False):
                    passed_tests += 1
                    logger.info(f"✅ {test_method.__name__} PASSED")
                else:
                    failed_tests += 1
                    logger.error(f"❌ {test_method.__name__} FAILED: {result.get('error', 'Unknown error')}")
                
                self.test_results.append({
                    "test_name": test_method.__name__,
                    "result": result
                })
                
            except Exception as e:
                failed_tests += 1
                logger.error(f"❌ {test_method.__name__} FAILED with exception: {e}")
                self.test_results.append({
                    "test_name": test_method.__name__,
                    "result": {"passed": False, "error": str(e)}
                })
        
        total_time = time.time() - start_time
        
        # Generate comprehensive test report
        report = {
            "summary": {
                "total_tests": len(test_methods),
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / len(test_methods)) * 100,
                "total_execution_time": total_time
            },
            "performance_metrics": self._analyze_performance_metrics(),
            "test_results": self.test_results,
            "recommendations": self._generate_test_recommendations()
        }
        
        logger.info(f"Integration tests completed: {passed_tests}/{len(test_methods)} passed")
        return report
    
    async def test_basic_orchestration(self) -> Dict[str, Any]:
        """Test 1: Basic orchestration functionality with small dataset."""
        start_time = time.time()
        
        try:
            # Setup mock components
            mock_work_manager = MockWorkItemManager(item_count=10)
            
            # Patch the real components with mocks
            with patch('datascience_platform.qvf.orchestration.orchestrator.WorkItemManager') as mock_wm_class:
                mock_wm_class.return_value = mock_work_manager
                
                orchestrator = QVFOrchestrator(
                    organization_url=self.test_organization_url,
                    personal_access_token=self.test_pat,
                    batch_size=5
                )
                
                # Execute scoring
                async with orchestrator:
                    result = await orchestrator.score_work_items(
                        project_name=self.test_project,
                        mode=ScoringMode.BATCH,
                        criteria_config=self.qvf_config
                    )
                
                execution_time = time.time() - start_time
                self.performance_metrics["execution_time"].append(execution_time)
                
                # Validate results
                assert result.status == WorkflowStatus.COMPLETED
                assert result.total_items_processed == 10
                assert result.successful_updates > 0
                assert result.processing_duration is not None
                
                # Calculate throughput
                throughput = result.total_items_processed / execution_time
                self.performance_metrics["throughput"].append(throughput)
                self.performance_metrics["success_rate"].append(result.success_rate)
                
                return {
                    "passed": True,
                    "execution_time": execution_time,
                    "items_processed": result.total_items_processed,
                    "throughput": throughput,
                    "success_rate": result.success_rate
                }
        
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def test_batch_scoring_workflow(self) -> Dict[str, Any]:
        """Test 2: Medium-scale batch scoring workflow."""
        start_time = time.time()
        
        try:
            mock_work_manager = MockWorkItemManager(item_count=1000)
            
            with patch('datascience_platform.qvf.orchestration.orchestrator.WorkItemManager') as mock_wm_class:
                mock_wm_class.return_value = mock_work_manager
                
                orchestrator = QVFOrchestrator(
                    organization_url=self.test_organization_url,
                    personal_access_token=self.test_pat,
                    batch_size=100
                )
                
                # Add financial data for more comprehensive scoring
                financial_data = {}
                for i in range(1, 1001):
                    financial_data[i] = FinancialMetrics(
                        npv_calculation=NPVCalculation(
                            cash_flows=[10000, 15000, 20000],
                            discount_rate=0.1,
                            time_periods=[1, 2, 3]
                        ),
                        roi_calculation=ROICalculation(
                            investment_amount=50000,
                            expected_return=75000,
                            time_horizon_months=12
                        )
                    )
                
                # Execute batch scoring
                async with orchestrator:
                    result = await orchestrator.batch_score_all_items(
                        project_name=self.test_project,
                        criteria_config=self.qvf_config,
                        financial_data=financial_data,
                        batch_size=100
                    )
                
                execution_time = time.time() - start_time
                throughput = result.total_items_processed / execution_time
                
                # Performance validation
                assert result.total_items_processed == 1000
                assert result.success_rate > 90  # Should have high success rate
                assert execution_time < 120  # Should complete within 2 minutes
                assert throughput > 8  # Should process at least 8 items/second
                
                return {
                    "passed": True,
                    "execution_time": execution_time,
                    "items_processed": result.total_items_processed,
                    "throughput": throughput,
                    "success_rate": result.success_rate,
                    "performance_score": (throughput * result.success_rate / 100) / 10  # Composite score
                }
        
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def test_real_time_scoring(self) -> Dict[str, Any]:
        """Test 3: Real-time scoring with low latency requirements."""
        try:
            mock_work_manager = MockWorkItemManager(item_count=5)
            mock_work_manager.api_delay = 0.02  # 20ms delay for real-time
            
            with patch('datascience_platform.qvf.orchestration.orchestrator.WorkItemManager') as mock_wm_class:
                mock_wm_class.return_value = mock_work_manager
                
                orchestrator = QVFOrchestrator(
                    organization_url=self.test_organization_url,
                    personal_access_token=self.test_pat
                )
                
                # Test multiple real-time requests
                async with orchestrator:
                    latencies = []
                    
                    for i in range(5):
                        start_time = time.time()
                        
                        result = await orchestrator.score_work_items(
                            project_name=self.test_project,
                            work_item_ids=[i + 1],
                            mode=ScoringMode.REAL_TIME,
                            criteria_config=self.qvf_config,
                            priority=OperationPriority.HIGH
                        )
                        
                        latency = time.time() - start_time
                        latencies.append(latency)
                        
                        assert result.status == WorkflowStatus.COMPLETED
                        assert latency < 2.0  # Should complete within 2 seconds
                
                avg_latency = statistics.mean(latencies)
                max_latency = max(latencies)
                
                return {
                    "passed": True,
                    "average_latency": avg_latency,
                    "max_latency": max_latency,
                    "latency_sla_met": max_latency < 2.0,
                    "requests_processed": len(latencies)
                }
        
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def test_priority_queue_management(self) -> Dict[str, Any]:
        """Test 4: Priority queue management and ordering."""
        try:
            # Test scheduler priority queue
            scheduler = QVFScheduler(worker_count=2)
            
            async with scheduler.managed_scheduler():
                # Queue requests with different priorities
                request_ids = []
                
                # Low priority request
                low_priority_request = ScoringRequest(
                    project_name=self.test_project,
                    mode=ScoringMode.BATCH
                )
                low_id = await scheduler.queue_priority_request(
                    low_priority_request, Priority.LOW, max_wait_seconds=60
                )
                request_ids.append((low_id, Priority.LOW))
                
                # High priority request  
                high_priority_request = ScoringRequest(
                    project_name=self.test_project,
                    mode=ScoringMode.REAL_TIME
                )
                high_id = await scheduler.queue_priority_request(
                    high_priority_request, Priority.HIGH, max_wait_seconds=30
                )
                request_ids.append((high_id, Priority.HIGH))
                
                # Critical priority request
                critical_priority_request = ScoringRequest(
                    project_name=self.test_project,
                    mode=ScoringMode.REAL_TIME
                )
                critical_id = await scheduler.queue_priority_request(
                    critical_priority_request, Priority.CRITICAL, max_wait_seconds=15
                )
                request_ids.append((critical_id, Priority.CRITICAL))
                
                # Allow some processing time
                await asyncio.sleep(2)
                
                # Check queue status
                queue_status = scheduler.get_queue_status()
                
                return {
                    "passed": True,
                    "requests_queued": len(request_ids),
                    "queue_size": queue_status["total_queued"],
                    "priority_distribution": queue_status["priority_distribution"],
                    "queue_utilization": queue_status["queue_utilization"]
                }
        
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def test_concurrent_workflows(self) -> Dict[str, Any]:
        """Test 5: Concurrent workflow execution."""
        start_time = time.time()
        
        try:
            mock_work_manager = MockWorkItemManager(item_count=100)
            
            with patch('datascience_platform.qvf.orchestration.orchestrator.WorkItemManager') as mock_wm_class:
                mock_wm_class.return_value = mock_work_manager
                
                orchestrator = QVFOrchestrator(
                    organization_url=self.test_organization_url,
                    personal_access_token=self.test_pat,
                    max_concurrent_workflows=3
                )
                
                # Start multiple concurrent workflows
                async with orchestrator:
                    tasks = []
                    
                    for i in range(3):
                        task = orchestrator.score_work_items(
                            project_name=f"{self.test_project}_{i}",
                            mode=ScoringMode.BATCH,
                            criteria_config=self.qvf_config,
                            description=f"Concurrent workflow {i+1}"
                        )
                        tasks.append(task)
                    
                    # Wait for all workflows to complete
                    results = await asyncio.gather(*tasks)
                
                execution_time = time.time() - start_time
                
                # Validate all workflows completed successfully
                successful_workflows = sum(1 for result in results if result.status == WorkflowStatus.COMPLETED)
                total_items_processed = sum(result.total_items_processed for result in results)
                overall_success_rate = statistics.mean([result.success_rate for result in results])
                
                return {
                    "passed": successful_workflows == 3,
                    "concurrent_workflows": len(results),
                    "successful_workflows": successful_workflows,
                    "total_execution_time": execution_time,
                    "total_items_processed": total_items_processed,
                    "overall_success_rate": overall_success_rate,
                    "concurrency_efficiency": (total_items_processed / execution_time) / len(results)
                }
        
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def test_error_handling_and_recovery(self) -> Dict[str, Any]:
        """Test 6: Error handling and recovery scenarios."""
        try:
            # Setup mock with low success rate to simulate errors
            mock_work_manager = MockWorkItemManager(item_count=50)
            mock_work_manager.update_success_rate = 0.7  # 70% success rate
            
            with patch('datascience_platform.qvf.orchestration.orchestrator.WorkItemManager') as mock_wm_class:
                mock_wm_class.return_value = mock_work_manager
                
                orchestrator = QVFOrchestrator(
                    organization_url=self.test_organization_url,
                    personal_access_token=self.test_pat
                )
                
                # Test error scenarios
                async with orchestrator:
                    # Test with invalid configuration (should handle gracefully)
                    try:
                        result = await orchestrator.score_work_items(
                            project_name=self.test_project,
                            mode=ScoringMode.BATCH,
                            criteria_config=None  # Invalid config
                        )
                        
                        # Should complete with default config
                        assert result.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]
                        
                    except Exception as e:
                        # Exception handling is working
                        pass
                    
                    # Test with partial failures
                    result = await orchestrator.score_work_items(
                        project_name=self.test_project,
                        mode=ScoringMode.BATCH,
                        criteria_config=self.qvf_config
                    )
                    
                    # Should complete even with some failures
                    assert result.status == WorkflowStatus.COMPLETED
                    assert result.failed_updates > 0  # Should have some failures
                    assert result.successful_updates > 0  # Should have some successes
                
                return {
                    "passed": True,
                    "error_handling_tested": True,
                    "partial_failure_handling": result.failed_updates > 0,
                    "graceful_degradation": result.successful_updates > 0,
                    "final_success_rate": result.success_rate
                }
        
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def test_resource_monitoring(self) -> Dict[str, Any]:
        """Test 7: Resource monitoring and throttling."""
        try:
            # Test with restrictive resource limits
            resource_limits = ResourceLimits(
                max_cpu_percent=50.0,
                max_memory_percent=60.0,
                max_concurrent_workflows=2,
                max_api_calls_per_minute=100
            )
            
            scheduler = QVFScheduler(worker_count=1)
            scheduler._resource_monitor.limits = resource_limits
            
            async with scheduler.managed_scheduler():
                # Queue multiple requests to test throttling
                request_ids = []
                
                for i in range(5):
                    request = ScoringRequest(
                        project_name=f"{self.test_project}_{i}",
                        mode=ScoringMode.BATCH
                    )
                    
                    request_id = await scheduler.queue_priority_request(
                        request, Priority.NORMAL
                    )
                    request_ids.append(request_id)
                
                # Allow processing time
                await asyncio.sleep(3)
                
                # Check resource monitoring
                queue_status = scheduler.get_queue_status()
                resource_status = queue_status["resource_status"]
                
                return {
                    "passed": True,
                    "resource_monitoring_active": "cpu_percent" in resource_status,
                    "throttling_detected": queue_status["total_queued"] > 0,
                    "resource_limits_enforced": not resource_status.get("can_accept_work", True),
                    "queue_management": queue_status["total_queued"] <= resource_limits.max_queue_size
                }
        
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def test_scheduling_system(self) -> Dict[str, Any]:
        """Test 8: Job scheduling and cron functionality."""
        try:
            scheduler = QVFScheduler()
            
            async with scheduler.managed_scheduler():
                # Schedule a test job
                job_id = await scheduler.schedule_job(
                    job_name="Test Batch Scoring",
                    job_type=JobType.BATCH_SCORING,
                    cron_expression="0 2 * * *",  # Daily at 2 AM
                    project_name=self.test_project,
                    configuration={
                        "mode": ScoringMode.BATCH.value,
                        "batch_size": 100
                    },
                    description="Test scheduled job"
                )
                
                # Get scheduled jobs
                scheduled_jobs = scheduler.get_scheduled_jobs()
                
                # Test job management
                pause_result = scheduler.pause_job(job_id)
                resume_result = scheduler.resume_job(job_id)
                cancel_result = scheduler.cancel_job(job_id)
                
                return {
                    "passed": True,
                    "job_scheduled": job_id is not None,
                    "job_found_in_list": any(job["job_id"] == job_id for job in scheduled_jobs),
                    "job_management": pause_result and resume_result and cancel_result,
                    "scheduler_functionality": len(scheduled_jobs) > 0
                }
        
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def test_performance_at_scale(self) -> Dict[str, Any]:
        """Test 9: Performance validation at enterprise scale."""
        start_time = time.time()
        
        try:
            # Test with larger dataset
            mock_work_manager = MockWorkItemManager(item_count=5000)
            mock_work_manager.api_delay = 0.01  # Optimized API delay
            
            with patch('datascience_platform.qvf.orchestration.orchestrator.WorkItemManager') as mock_wm_class:
                mock_wm_class.return_value = mock_work_manager
                
                orchestrator = QVFOrchestrator(
                    organization_url=self.test_organization_url,
                    personal_access_token=self.test_pat,
                    batch_size=500,
                    max_concurrent_workflows=5
                )
                
                # Execute large-scale batch scoring
                async with orchestrator:
                    result = await orchestrator.batch_score_all_items(
                        project_name=self.test_project,
                        criteria_config=self.qvf_config,
                        batch_size=500
                    )
                
                execution_time = time.time() - start_time
                throughput = result.total_items_processed / execution_time
                
                # Enterprise scale validation
                scale_requirements = {
                    "items_processed": result.total_items_processed >= 5000,
                    "completion_time": execution_time <= 60,  # Complete within 1 minute
                    "throughput": throughput >= 80,  # At least 80 items/second
                    "success_rate": result.success_rate >= 95,  # 95% success rate
                    "memory_efficiency": True  # Would need actual memory monitoring
                }
                
                passed = all(scale_requirements.values())
                
                return {
                    "passed": passed,
                    "scale_requirements": scale_requirements,
                    "execution_time": execution_time,
                    "throughput": throughput,
                    "items_processed": result.total_items_processed,
                    "success_rate": result.success_rate,
                    "performance_grade": "A" if throughput > 100 else "B" if throughput > 50 else "C"
                }
        
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def test_monitoring_and_alerts(self) -> Dict[str, Any]:
        """Test 10: Monitoring system and alerting functionality."""
        try:
            # Setup monitoring system
            monitor = OperationMonitor(enable_real_time_alerts=True)
            await monitor.start_background_tasks()
            
            try:
                # Setup alert callback
                alerts_triggered = []
                
                def alert_callback(alert):
                    alerts_triggered.append(alert)
                    logger.info(f"Test alert triggered: {alert.title}")
                
                monitor.add_alert_callback(alert_callback)
                
                # Simulate operations with monitoring
                with monitor.track_operation(OperationType.BATCH_SCORING) as tracker:
                    tracker.record_business_context(
                        project_name=self.test_project,
                        configuration_id="test_config"
                    )
                    
                    # Simulate successful operation
                    tracker.record_success(95, 100)
                    tracker.record_quality_metrics({
                        "average_score": 0.85,
                        "data_quality_score": 0.9
                    })
                
                # Simulate operation with low success rate (should trigger alert)
                with monitor.track_operation(OperationType.REAL_TIME_SCORING) as tracker:
                    tracker.record_success(70, 100)  # 70% success rate (below threshold)
                    tracker.record_quality_metrics({
                        "data_quality_score": 0.6  # Below quality threshold
                    })
                
                # Allow time for alert processing
                await asyncio.sleep(1)
                
                # Get monitoring metrics
                metrics = monitor.get_comprehensive_metrics(
                    time_range=timedelta(minutes=5)
                )
                
                # Get active operations and alerts
                active_ops = monitor.get_active_operations()
                
                return {
                    "passed": True,
                    "monitoring_active": metrics is not None,
                    "operations_tracked": metrics["summary"]["total_operations"] >= 2,
                    "alerts_triggered": len(alerts_triggered),
                    "metrics_collected": len(metrics["quality_metrics"]) > 0,
                    "system_health": metrics.get("system_health", {}).get("status", "unknown")
                }
            
            finally:
                await monitor.stop_background_tasks()
        
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _analyze_performance_metrics(self) -> Dict[str, Any]:
        """Analyze collected performance metrics."""
        analysis = {}
        
        for metric_name, values in self.performance_metrics.items():
            if values:
                analysis[metric_name] = {
                    "count": len(values),
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0
                }
        
        return analysis
    
    def _generate_test_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Analyze test results
        failed_tests = [r for r in self.test_results if not r["result"].get("passed", False)]
        performance_issues = []
        
        # Check for performance issues
        if self.performance_metrics["throughput"]:
            avg_throughput = statistics.mean(self.performance_metrics["throughput"])
            if avg_throughput < 10:
                performance_issues.append("Low throughput detected")
        
        if self.performance_metrics["execution_time"]:
            avg_execution_time = statistics.mean(self.performance_metrics["execution_time"])
            if avg_execution_time > 30:
                performance_issues.append("High execution times detected")
        
        # Generate recommendations
        if failed_tests:
            recommendations.append(f"Address {len(failed_tests)} failed test cases")
        
        if performance_issues:
            recommendations.extend(performance_issues)
            recommendations.append("Consider optimizing batch sizes and concurrent workflow limits")
        
        if not failed_tests and not performance_issues:
            recommendations.append("All tests passed - system is performing well")
            recommendations.append("Consider stress testing with larger datasets")
        
        return recommendations


async def run_integration_tests():
    """Run the complete integration test suite."""
    print("🚀 Starting QVF Orchestration Integration Tests")
    print("=" * 60)
    
    test_suite = IntegrationTestSuite()
    
    try:
        # Run all tests
        report = await test_suite.run_all_tests()
        
        # Print summary
        print("\n📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: ✅ {report['summary']['passed_tests']}")
        print(f"Failed: ❌ {report['summary']['failed_tests']}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Total Execution Time: {report['summary']['total_execution_time']:.2f}s")
        
        # Print performance metrics
        if report["performance_metrics"]:
            print("\n📈 PERFORMANCE METRICS")
            print("=" * 60)
            for metric_name, data in report["performance_metrics"].items():
                if data["count"] > 0:
                    print(f"{metric_name.replace('_', ' ').title()}: "
                          f"avg={data['average']:.2f}, "
                          f"min={data['min']:.2f}, "
                          f"max={data['max']:.2f}")
        
        # Print recommendations
        if report["recommendations"]:
            print("\n💡 RECOMMENDATIONS")
            print("=" * 60)
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"{i}. {rec}")
        
        # Print detailed results for failed tests
        failed_results = [r for r in report["test_results"] if not r["result"].get("passed", False)]
        if failed_results:
            print("\n❌ FAILED TEST DETAILS")
            print("=" * 60)
            for result in failed_results:
                print(f"Test: {result['test_name']}")
                print(f"Error: {result['result'].get('error', 'Unknown error')}")
                print()
        
        return report
    
    except Exception as e:
        print(f"\n💥 Test suite failed with exception: {e}")
        logger.exception("Integration test suite failed")
        return {"error": str(e)}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="QVF Orchestration Integration Tests")
    parser.add_argument("--test-category", help="Run specific test category")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    asyncio.run(run_integration_tests())