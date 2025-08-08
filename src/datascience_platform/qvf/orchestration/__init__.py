"""QVF Orchestration Module

Provides enterprise-grade orchestration capabilities for QVF scoring and work item updates,
including batch processing, scheduling, monitoring, and data consistency management.

Key Components:
- QVFOrchestrator: Main orchestration engine
- ScoringWorkflow: Workflow management for scoring operations
- BatchProcessor: High-performance batch processing
- ScoreUpdateScheduler: Scheduling and queue management
- OperationMonitor: Monitoring and reporting system

Usage:
    from datascience_platform.qvf.orchestration import QVFOrchestrator, ScoringMode
    
    orchestrator = QVFOrchestrator(
        organization_url="https://dev.azure.com/yourorg",
        personal_access_token="your_pat",
        batch_size=100
    )
    
    # Real-time scoring
    result = await orchestrator.score_work_items(
        project_name="MyProject",
        work_item_ids=[1234, 5678],
        mode=ScoringMode.REAL_TIME
    )
    
    # Batch scoring with scheduling
    job_id = await orchestrator.schedule_batch_scoring(
        project_name="MyProject",
        criteria_config=qvf_config,
        schedule="0 2 * * *"  # Daily at 2 AM
    )
"""

from .orchestrator import (
    QVFOrchestrator,
    ScoringMode,
    ScoringWorkflow,
    BatchProcessor,
    WorkflowResult,
    OrchestrationError
)

__all__ = [
    "QVFOrchestrator",
    "ScoringMode", 
    "ScoringWorkflow",
    "BatchProcessor",
    "WorkflowResult",
    "OrchestrationError"
]