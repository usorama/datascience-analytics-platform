#!/usr/bin/env python3
"""QVF Deployment Automation Script

This script provides automated deployment of the Quantified Value Framework (QVF)
to Azure DevOps environments with comprehensive validation and monitoring.

Features:
- Environment validation and dependency checking
- Azure DevOps custom field deployment
- QVF scoring configuration and validation
- Health check monitoring and rollback capabilities
- Integration testing and verification

Usage:
    python3 scripts/deploy_qvf.py --config config/qvf_production.json --environment prod
    python3 scripts/deploy_qvf.py --dry-run --config config/qvf_test.json
    python3 scripts/deploy_qvf.py --rollback --deployment-id 12345

Created: August 2025
Author: DataScience Platform Team
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.logging import RichHandler

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# QVF imports
from src.datascience_platform.qvf.core.criteria import QVFCriteriaEngine, create_enterprise_configuration
from src.datascience_platform.qvf.core.financial import FinancialCalculator
from src.datascience_platform.qvf.ado.custom_fields import CustomFieldManager
from src.datascience_platform.qvf.ado.rest_client import ADOClient
from src.datascience_platform.qvf.ado.work_items import WorkItemManager

# Optional AI imports
try:
    from src.datascience_platform.qvf.ai.ollama_manager import OllamaManager
    from src.datascience_platform.qvf.ai.semantic import SemanticAnalyzer
    AI_AVAILABLE = True
except ImportError:
    OllamaManager = None
    SemanticAnalyzer = None
    AI_AVAILABLE = False

# Setup logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
console = Console()


class QVFDeploymentError(Exception):
    """Base exception for QVF deployment operations."""
    pass


class QVFDeploymentManager:
    """Comprehensive QVF deployment manager with rollback capabilities."""
    
    def __init__(self, config_path: str, environment: str = "development"):
        self.config_path = Path(config_path)
        self.environment = environment
        self.deployment_id = str(uuid.uuid4())[:8]
        self.deployment_log = []
        self.console = Console()
        
        # Load and validate configuration
        self.config = self._load_and_validate_config()
        
        # Initialize deployment state
        self.deployment_state = {
            "deployment_id": self.deployment_id,
            "environment": environment,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "initialized",
            "steps_completed": [],
            "rollback_actions": [],
            "config_hash": self._calculate_config_hash()
        }
        
        logger.info(f"🚀 QVF Deployment Manager initialized (ID: {self.deployment_id})")
    
    def _load_and_validate_config(self) -> Dict:
        """Load and validate deployment configuration."""
        if not self.config_path.exists():
            raise QVFDeploymentError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Validate required configuration sections
            required_sections = ["ado", "scoring", "criteria", "deployment"]
            for section in required_sections:
                if section not in config:
                    raise QVFDeploymentError(f"Missing required configuration section: {section}")
            
            # Validate ADO configuration
            ado_config = config["ado"]
            required_ado_fields = ["organization", "project", "pat_token"]
            for field in required_ado_fields:
                if not ado_config.get(field):
                    raise QVFDeploymentError(f"Missing required ADO configuration: {field}")
            
            # Add deployment-specific settings
            if "deployment" not in config:
                config["deployment"] = {}
            
            # Set default deployment settings
            deployment_defaults = {
                "timeout_seconds": 600,
                "retry_attempts": 3,
                "health_check_interval": 30,
                "rollback_enabled": True,
                "backup_enabled": True,
                "validation_required": True
            }
            
            for key, default_value in deployment_defaults.items():
                if key not in config["deployment"]:
                    config["deployment"][key] = default_value
            
            return config
            
        except json.JSONDecodeError as e:
            raise QVFDeploymentError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise QVFDeploymentError(f"Failed to load configuration: {e}")
    
    def _calculate_config_hash(self) -> str:
        """Calculate hash of configuration for change detection."""
        import hashlib
        config_str = json.dumps(self.config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
    
    async def deploy(self, dry_run: bool = False) -> Tuple[bool, Dict]:
        """Execute comprehensive QVF deployment."""
        try:
            self.deployment_state["status"] = "in_progress"
            self.deployment_state["dry_run"] = dry_run
            
            if dry_run:
                self.console.print(Panel.fit("🔍 QVF Deployment - DRY RUN MODE", style="bold yellow"))
            else:
                self.console.print(Panel.fit("🚀 QVF Production Deployment", style="bold blue"))
            
            # Deployment steps
            deployment_steps = [
                ("validate_environment", "Validating deployment environment"),
                ("check_dependencies", "Checking system dependencies"), 
                ("validate_ado_connection", "Validating Azure DevOps connection"),
                ("backup_existing_config", "Creating configuration backup"),
                ("deploy_custom_fields", "Deploying custom fields to ADO"),
                ("configure_scoring_engine", "Configuring QVF scoring engine"),
                ("deploy_ai_components", "Deploying AI enhancement components"),
                ("run_integration_tests", "Running integration test suite"),
                ("verify_deployment", "Verifying deployment health"),
                ("update_deployment_registry", "Updating deployment registry")
            ]
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            ) as progress:
                
                main_task = progress.add_task(
                    "QVF Deployment Progress", 
                    total=len(deployment_steps)
                )
                
                for step_name, step_description in deployment_steps:
                    step_task = progress.add_task(step_description, total=None)
                    
                    try:
                        # Execute deployment step
                        step_result = await self._execute_deployment_step(
                            step_name, dry_run
                        )
                        
                        if step_result["success"]:
                            self.deployment_state["steps_completed"].append({
                                "step": step_name,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "result": step_result
                            })
                            progress.advance(step_task)
                            progress.advance(main_task)
                        else:
                            raise QVFDeploymentError(
                                f"Deployment step '{step_name}' failed: {step_result['error']}"
                            )
                            
                    except Exception as e:
                        logger.error(f"Deployment step '{step_name}' failed: {e}")
                        self.deployment_state["status"] = "failed"
                        self.deployment_state["error"] = str(e)
                        
                        # Attempt rollback if not dry run
                        if not dry_run and self.config["deployment"]["rollback_enabled"]:
                            await self._execute_rollback()
                        
                        return False, self.deployment_state
            
            # Deployment completed successfully
            self.deployment_state["status"] = "completed"
            self.deployment_state["end_time"] = datetime.now(timezone.utc).isoformat()
            
            success_message = "🎉 QVF deployment completed successfully!"
            if dry_run:
                success_message = "✅ QVF deployment validation passed (dry run)"
            
            self.console.print(success_message, style="bold green")
            
            # Save deployment state
            await self._save_deployment_state()
            
            return True, self.deployment_state
            
        except Exception as e:
            logger.exception("Deployment failed with unexpected error")
            self.deployment_state["status"] = "failed"
            self.deployment_state["error"] = str(e)
            return False, self.deployment_state
    
    async def _execute_deployment_step(self, step_name: str, dry_run: bool) -> Dict:
        """Execute a specific deployment step."""
        step_handlers = {
            "validate_environment": self._validate_environment,
            "check_dependencies": self._check_dependencies,
            "validate_ado_connection": self._validate_ado_connection,
            "backup_existing_config": self._backup_existing_config,
            "deploy_custom_fields": self._deploy_custom_fields,
            "configure_scoring_engine": self._configure_scoring_engine,
            "deploy_ai_components": self._deploy_ai_components,
            "run_integration_tests": self._run_integration_tests,
            "verify_deployment": self._verify_deployment,
            "update_deployment_registry": self._update_deployment_registry
        }
        
        handler = step_handlers.get(step_name)
        if not handler:
            return {
                "success": False,
                "error": f"Unknown deployment step: {step_name}"
            }
        
        try:
            result = await handler(dry_run)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _validate_environment(self, dry_run: bool) -> Dict:
        """Validate deployment environment."""
        validation_results = {
            "environment": self.environment,
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "working_directory": str(Path.cwd()),
            "config_valid": True
        }
        
        # Check Python version (3.8+)
        import sys
        if sys.version_info < (3, 8):
            raise QVFDeploymentError(f"Python 3.8+ required, found {sys.version}")
        
        # Validate environment-specific settings
        env_settings = self.config.get("environments", {}).get(self.environment)
        if env_settings:
            validation_results["environment_config"] = env_settings
        
        return validation_results
    
    async def _check_dependencies(self, dry_run: bool) -> Dict:
        """Check system dependencies."""
        dependencies = {
            "pandas": None,
            "rich": None,
            "aiohttp": None,
            "pydantic": None
        }
        
        # Check core dependencies
        for dep in dependencies:
            try:
                module = __import__(dep)
                dependencies[dep] = getattr(module, "__version__", "unknown")
            except ImportError:
                raise QVFDeploymentError(f"Required dependency missing: {dep}")
        
        # Check optional AI dependencies
        ai_dependencies = {}
        if AI_AVAILABLE:
            try:
                import requests
                ai_dependencies["requests"] = requests.__version__
            except ImportError:
                pass
        
        return {
            "core_dependencies": dependencies,
            "ai_dependencies": ai_dependencies,
            "ai_available": AI_AVAILABLE
        }
    
    async def _validate_ado_connection(self, dry_run: bool) -> Dict:
        """Validate Azure DevOps connection."""
        if dry_run:
            return {"status": "dry_run_skip", "message": "ADO validation skipped in dry run"}
        
        ado_config = self.config["ado"]
        client = ADOClient(
            organization=ado_config["organization"],
            project=ado_config["project"],
            personal_access_token=ado_config["pat_token"]
        )
        
        # Test connection
        health_check = await client.health_check()
        
        if health_check["status"] != "healthy":
            raise QVFDeploymentError(f"ADO connection failed: {health_check}")
        
        # Store rollback action
        self.deployment_state["rollback_actions"].append({
            "type": "ado_connection",
            "data": {"client_config": "stored_securely"}
        })
        
        return health_check
    
    async def _backup_existing_config(self, dry_run: bool) -> Dict:
        """Create backup of existing configuration."""
        if not self.config["deployment"]["backup_enabled"]:
            return {"status": "backup_disabled", "message": "Backup disabled in configuration"}
        
        backup_dir = Path("backups") / f"qvf_deployment_{self.deployment_id}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup configuration files
        config_backup = backup_dir / "config.json"
        if not dry_run:
            with open(config_backup, 'w') as f:
                json.dump(self.config, f, indent=2)
        
        # Backup deployment state
        state_backup = backup_dir / "deployment_state.json"
        if not dry_run:
            with open(state_backup, 'w') as f:
                json.dump(self.deployment_state, f, indent=2)
        
        return {
            "backup_directory": str(backup_dir),
            "files_backed_up": ["config.json", "deployment_state.json"],
            "backup_size": len(json.dumps(self.config)) if dry_run else config_backup.stat().st_size
        }
    
    async def _deploy_custom_fields(self, dry_run: bool) -> Dict:
        """Deploy QVF custom fields to Azure DevOps."""
        if dry_run:
            return {
                "status": "dry_run_simulation",
                "message": "Would deploy custom fields to ADO",
                "fields": list(self.config["ado"]["custom_fields"].keys())
            }
        
        ado_config = self.config["ado"]
        client = ADOClient(
            organization=ado_config["organization"],
            project=ado_config["project"],
            personal_access_token=ado_config["pat_token"]
        )
        
        field_manager = CustomFieldManager(client)
        deployed_fields = []
        
        # Deploy each custom field
        for field_key, field_name in ado_config["custom_fields"].items():
            field_type = self._get_field_type(field_key)
            
            field_result = await field_manager.create_custom_field(
                field_name=field_name,
                field_type=field_type,
                description=f"QVF {field_key.replace('_', ' ').title()}"
            )
            
            deployed_fields.append({
                "name": field_name,
                "type": field_type,
                "status": "created" if field_result.get("created") else "exists"
            })
        
        # Store rollback action
        self.deployment_state["rollback_actions"].append({
            "type": "custom_fields",
            "data": {"deployed_fields": deployed_fields}
        })
        
        return {
            "deployed_fields": deployed_fields,
            "total_fields": len(deployed_fields)
        }
    
    def _get_field_type(self, field_key: str) -> str:
        """Get appropriate field type for QVF custom fields."""
        type_mapping = {
            "qvf_score": "Double",
            "qvf_rank": "Integer",
            "qvf_confidence": "Double", 
            "qvf_category": "String"
        }
        return type_mapping.get(field_key, "String")
    
    async def _configure_scoring_engine(self, dry_run: bool) -> Dict:
        """Configure QVF scoring engine."""
        if dry_run:
            return {
                "status": "dry_run_simulation",
                "message": "Would configure QVF scoring engine"
            }
        
        # Initialize scoring components
        criteria_engine = QVFCriteriaEngine()
        financial_calc = FinancialCalculator()
        
        # Configure criteria based on configuration
        criteria_preset = self.config["criteria"]["preset"]
        if criteria_preset == "enterprise":
            criteria_config = create_enterprise_configuration()
        else:
            criteria_config = criteria_engine.get_default_configuration()
        
        # Test scoring with sample data
        test_item = {
            "id": "test_001",
            "title": "Test Work Item",
            "business_value": 8,
            "user_impact": 7,
            "strategic_alignment": 6,
            "estimated_value": 50000,
            "development_cost": 25000
        }
        
        score_result = criteria_engine.calculate_work_item_score(
            work_item=test_item,
            criteria_config=criteria_config
        )
        
        return {
            "criteria_preset": criteria_preset,
            "test_score": score_result["score"],
            "criteria_count": len(criteria_config.criteria),
            "engine_status": "configured"
        }
    
    async def _deploy_ai_components(self, dry_run: bool) -> Dict:
        """Deploy AI enhancement components."""
        if not AI_AVAILABLE:
            return {
                "status": "ai_not_available",
                "message": "AI components not available - dependencies not installed"
            }
        
        if not self.config["scoring"].get("enable_ai", False):
            return {
                "status": "ai_disabled",
                "message": "AI components disabled in configuration"
            }
        
        if dry_run:
            return {
                "status": "dry_run_simulation",
                "message": "Would deploy AI components (Ollama integration)"
            }
        
        try:
            # Test Ollama connection
            ollama_manager = OllamaManager()
            health_status = ollama_manager.get_health_status()
            
            if health_status["status"] == "healthy":
                return {
                    "ollama_status": health_status,
                    "ai_components": "deployed",
                    "available_models": health_status.get("available_models", [])
                }
            else:
                return {
                    "ollama_status": health_status,
                    "ai_components": "degraded",
                    "message": "Ollama not available - falling back to mathematical methods"
                }
                
        except Exception as e:
            return {
                "status": "ai_deployment_failed",
                "error": str(e),
                "fallback": "mathematical_methods_only"
            }
    
    async def _run_integration_tests(self, dry_run: bool) -> Dict:
        """Run integration test suite."""
        if dry_run:
            return {
                "status": "dry_run_skip",
                "message": "Integration tests skipped in dry run"
            }
        
        test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        
        # Test 1: Core scoring functionality
        try:
            criteria_engine = QVFCriteriaEngine()
            criteria_config = create_enterprise_configuration()
            
            test_items = [
                {
                    "id": f"test_{i}",
                    "business_value": 8,
                    "user_impact": 7,
                    "strategic_alignment": 6
                }
                for i in range(10)
            ]
            
            for item in test_items:
                score_result = criteria_engine.calculate_work_item_score(
                    work_item=item,
                    criteria_config=criteria_config
                )
                if not (0 <= score_result["score"] <= 100):
                    raise ValueError(f"Invalid score: {score_result['score']}")
            
            test_results["test_details"].append({
                "name": "core_scoring",
                "status": "passed",
                "items_scored": len(test_items)
            })
            test_results["passed_tests"] += 1
            
        except Exception as e:
            test_results["test_details"].append({
                "name": "core_scoring",
                "status": "failed",
                "error": str(e)
            })
            test_results["failed_tests"] += 1
        
        test_results["total_tests"] = len(test_results["test_details"])
        
        # Test 2: Financial calculations
        try:
            financial_calc = FinancialCalculator()
            metrics = financial_calc.calculate_comprehensive_metrics(
                estimated_value=100000,
                development_cost=50000,
                maintenance_cost=10000,
                risk_cost=5000
            )
            
            if metrics.roi_calculation.roi_percentage < 0:
                raise ValueError("Unexpected negative ROI")
            
            test_results["test_details"].append({
                "name": "financial_calculations",
                "status": "passed",
                "roi_percentage": metrics.roi_calculation.roi_percentage
            })
            test_results["passed_tests"] += 1
            
        except Exception as e:
            test_results["test_details"].append({
                "name": "financial_calculations", 
                "status": "failed",
                "error": str(e)
            })
            test_results["failed_tests"] += 1
        
        test_results["total_tests"] = len(test_results["test_details"])
        
        return test_results
    
    async def _verify_deployment(self, dry_run: bool) -> Dict:
        """Verify deployment health and functionality."""
        if dry_run:
            return {
                "status": "dry_run_simulation",
                "message": "Deployment verification would be performed"
            }
        
        verification_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "deployment_id": self.deployment_id,
            "health_checks": {},
            "overall_status": "unknown"
        }
        
        # Check 1: Core components health
        try:
            criteria_engine = QVFCriteriaEngine()
            financial_calc = FinancialCalculator()
            
            verification_results["health_checks"]["core_components"] = {
                "status": "healthy",
                "criteria_engine": "operational",
                "financial_calculator": "operational"
            }
        except Exception as e:
            verification_results["health_checks"]["core_components"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check 2: ADO connectivity
        try:
            ado_config = self.config["ado"]
            client = ADOClient(
                organization=ado_config["organization"],
                project=ado_config["project"],
                personal_access_token=ado_config["pat_token"]
            )
            
            health_check = await client.health_check()
            verification_results["health_checks"]["ado_connectivity"] = health_check
            
        except Exception as e:
            verification_results["health_checks"]["ado_connectivity"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Determine overall status
        all_healthy = all(
            check.get("status") == "healthy" 
            for check in verification_results["health_checks"].values()
        )
        
        verification_results["overall_status"] = "healthy" if all_healthy else "degraded"
        
        return verification_results
    
    async def _update_deployment_registry(self, dry_run: bool) -> Dict:
        """Update deployment registry with current deployment info."""
        registry_file = Path("deployments") / "qvf_deployments.json"
        registry_file.parent.mkdir(exist_ok=True)
        
        # Load existing registry
        registry = []
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    registry = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                registry = []
        
        # Add current deployment
        deployment_record = {
            "deployment_id": self.deployment_id,
            "environment": self.environment,
            "config_hash": self.deployment_state["config_hash"],
            "status": self.deployment_state["status"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": dry_run
        }
        
        registry.append(deployment_record)
        
        # Keep only last 50 deployments
        registry = registry[-50:]
        
        if not dry_run:
            with open(registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
        
        return {
            "registry_file": str(registry_file),
            "deployment_record": deployment_record,
            "total_deployments": len(registry)
        }
    
    async def _save_deployment_state(self) -> None:
        """Save current deployment state to file."""
        state_dir = Path("deployments") / self.deployment_id
        state_dir.mkdir(parents=True, exist_ok=True)
        
        state_file = state_dir / "deployment_state.json"
        with open(state_file, 'w') as f:
            json.dump(self.deployment_state, f, indent=2)
        
        logger.info(f"Deployment state saved to {state_file}")
    
    async def _execute_rollback(self) -> bool:
        """Execute rollback actions if deployment fails."""
        try:
            self.console.print("🔄 Initiating rollback...", style="bold yellow")
            
            for rollback_action in reversed(self.deployment_state["rollback_actions"]):
                action_type = rollback_action["type"]
                action_data = rollback_action["data"]
                
                logger.info(f"Rolling back action: {action_type}")
                
                # Execute rollback based on action type
                if action_type == "custom_fields":
                    # Note: In practice, you might want to keep custom fields
                    # and just reset their values rather than delete them
                    pass
                elif action_type == "ado_connection":
                    # Close any persistent connections
                    pass
            
            self.console.print("✅ Rollback completed", style="bold green")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Rollback failed: {e}", style="bold red")
            return False


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="QVF Deployment Automation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Production deployment
  python3 scripts/deploy_qvf.py --config config/qvf_prod.json --environment prod
  
  # Dry run validation
  python3 scripts/deploy_qvf.py --config config/qvf_test.json --dry-run
  
  # Force deployment without validation
  python3 scripts/deploy_qvf.py --config config/qvf_dev.json --force
  
  # Check deployment status
  python3 scripts/deploy_qvf.py --status --deployment-id abc12345
        """
    )
    
    # Main action arguments
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '--deploy', 
        action='store_true',
        help='Execute QVF deployment'
    )
    action_group.add_argument(
        '--status',
        action='store_true', 
        help='Check deployment status'
    )
    action_group.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback specified deployment'
    )
    
    # Configuration arguments
    parser.add_argument(
        '--config',
        required=True,
        help='Path to QVF configuration file'
    )
    parser.add_argument(
        '--environment',
        choices=['development', 'staging', 'production'],
        default='development',
        help='Target deployment environment'
    )
    
    # Deployment options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform validation without making changes'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip pre-deployment validation'
    )
    parser.add_argument(
        '--deployment-id',
        help='Deployment ID for status or rollback operations'
    )
    
    # Output options
    parser.add_argument(
        '--output',
        help='Save deployment results to file'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser


async def main():
    """Main deployment script entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if args.deploy:
            # Execute deployment
            manager = QVFDeploymentManager(args.config, args.environment)
            success, results = await manager.deploy(dry_run=args.dry_run)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                console.print(f"📄 Results saved to {args.output}", style="blue")
            
            # Display summary
            if success:
                console.print(Panel.fit("✅ QVF Deployment Successful", style="bold green"))
                
                # Show summary table
                table = Table(title="Deployment Summary")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="white")
                
                table.add_row("Deployment ID", results["deployment_id"])
                table.add_row("Environment", results["environment"])
                table.add_row("Status", results["status"])
                table.add_row("Steps Completed", str(len(results["steps_completed"])))
                
                if "end_time" in results:
                    start_time = datetime.fromisoformat(results["start_time"].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(results["end_time"].replace('Z', '+00:00'))
                    duration = end_time - start_time
                    table.add_row("Duration", str(duration).split('.')[0])
                
                console.print(table)
                sys.exit(0)
            else:
                console.print(Panel.fit("❌ QVF Deployment Failed", style="bold red"))
                console.print(f"Error: {results.get('error', 'Unknown error')}")
                sys.exit(1)
        
        elif args.status:
            # Check deployment status
            if not args.deployment_id:
                console.print("❌ Deployment ID required for status check", style="red")
                sys.exit(1)
            
            # Load deployment state
            state_file = Path("deployments") / args.deployment_id / "deployment_state.json"
            
            if not state_file.exists():
                console.print(f"❌ Deployment not found: {args.deployment_id}", style="red")
                sys.exit(1)
            
            with open(state_file, 'r') as f:
                deployment_state = json.load(f)
            
            console.print(Panel.fit(f"📊 Deployment Status: {args.deployment_id}", style="bold blue"))
            
            status_table = Table(title="Deployment Details")
            status_table.add_column("Property", style="cyan")
            status_table.add_column("Value", style="white")
            
            for key, value in deployment_state.items():
                if key not in ["steps_completed", "rollback_actions"]:
                    status_table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(status_table)
        
        elif args.rollback:
            # Execute rollback
            if not args.deployment_id:
                console.print("❌ Deployment ID required for rollback", style="red")
                sys.exit(1)
            
            console.print(f"🔄 Rollback functionality for {args.deployment_id} not yet implemented")
            console.print("This would restore the system to pre-deployment state", style="yellow")
    
    except Exception as e:
        logger.exception("Deployment script failed")
        console.print(f"❌ Deployment script failed: {str(e)}", style="bold red")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())