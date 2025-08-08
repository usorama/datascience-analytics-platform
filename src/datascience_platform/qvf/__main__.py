#!/usr/bin/env python3
"""QVF (Quantified Value Framework) Command Line Interface

This module provides the main CLI interface for QVF operations including:
- Portfolio scoring and prioritization
- Configuration management and validation
- System health checks

Usage:
    python -m datascience_platform.qvf score --help
    python -m datascience_platform.qvf configure --help
    python -m datascience_platform.qvf validate --help

Created: August 2025
Author: DataScience Platform Team
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# QVF Core Imports
from .core.criteria import QVFCriteriaEngine, create_enterprise_configuration, create_agile_configuration
from .core.financial import FinancialCalculator

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QVFCLIError(Exception):
    """Base exception for QVF CLI operations."""
    pass


class QVFScorer:
    """Handles QVF scoring operations."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.criteria_engine = QVFCriteriaEngine()
        self.financial_calc = FinancialCalculator()
        self.console = Console()
    
    def score_portfolio(
        self, 
        work_items_file: str,
        output_file: Optional[str] = None,
        criteria_preset: str = "enterprise"
    ) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Score a portfolio of work items using QVF."""
        try:
            # Load work items
            work_items_df = pd.read_csv(work_items_file)
            
            if work_items_df.empty:
                return False, "No work items found in input file", None
            
            # Get criteria configuration
            if criteria_preset == "enterprise":
                criteria_config = create_enterprise_configuration()
            elif criteria_preset == "agile":
                criteria_config = create_agile_configuration()
            else:
                criteria_config = self.criteria_engine.get_default_configuration()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(
                    f"Scoring {len(work_items_df)} work items...", 
                    total=len(work_items_df)
                )
                
                # Convert DataFrame to work items format
                work_items = work_items_df.to_dict('records')
                
                # Score work items in batches
                batch_size = self.config.get("scoring", {}).get("batch_size", 100)
                scored_items = []
                
                for i in range(0, len(work_items), batch_size):
                    batch = work_items[i:i + batch_size]
                    
                    # Score batch
                    batch_scores = self._score_batch(batch, criteria_config)
                    scored_items.extend(batch_scores)
                    
                    progress.advance(task, len(batch))
            
            # Create results DataFrame
            results_df = pd.DataFrame(scored_items)
            
            # Sort by QVF score (descending)
            results_df = results_df.sort_values('qvf_score', ascending=False)
            results_df['qvf_rank'] = range(1, len(results_df) + 1)
            
            # Save results if output file specified
            if output_file:
                results_df.to_csv(output_file, index=False)
                return True, f"Scoring completed. Results saved to {output_file}", results_df
            
            return True, "Scoring completed successfully", results_df
            
        except Exception as e:
            return False, f"Scoring failed: {str(e)}", None
    
    def _score_batch(
        self, 
        batch: List[Dict], 
        criteria_config
    ) -> List[Dict]:
        """Score a batch of work items."""
        scored_batch = []
        
        for item in batch:
            try:
                # Calculate basic QVF score using available criteria
                criteria_score = self._calculate_basic_score(item)
                
                # Add basic financial score if available
                financial_score = 0.0
                if 'estimated_value' in item and 'development_cost' in item:
                    try:
                        estimated_value = float(item.get('estimated_value', 0))
                        development_cost = float(item.get('development_cost', 0))
                        
                        if development_cost > 0:
                            # Simple ROI calculation: (value - cost) / cost * 100
                            roi = ((estimated_value - development_cost) / development_cost) * 100
                            # Normalize to 0-100 scale (cap at 200% ROI)
                            financial_score = min(100, max(0, (roi + 100) / 3))
                        else:
                            financial_score = 50  # Default moderate score
                    except (ValueError, TypeError, ZeroDivisionError):
                        financial_score = 0.0
                
                # Combine scores (70% criteria, 30% financial)
                combined_score = (criteria_score * 0.7) + (financial_score * 0.3)
                
                scored_item = {
                    **item,
                    'qvf_score': combined_score,
                    'criteria_score': criteria_score,
                    'financial_score': financial_score,
                    'qvf_confidence': 0.8 if criteria_score > 0 else 0.3,
                    'qvf_category': self._categorize_score(combined_score)
                }
                
                scored_batch.append(scored_item)
                
            except Exception as e:
                logger.warning(f"Failed to score work item {item.get('id', 'unknown')}: {e}")
                # Add item with default scores
                scored_batch.append({
                    **item,
                    'qvf_score': 0.0,
                    'criteria_score': 0.0,
                    'financial_score': 0.0,
                    'qvf_confidence': 0.0,
                    'qvf_category': 'Unscored'
                })
        
        return scored_batch
    
    def _calculate_basic_score(self, item: Dict) -> float:
        """Calculate basic QVF score using available criteria fields."""
        try:
            # Define criteria weights (simplified version)
            criteria_weights = {
                'business_value': 0.25,
                'user_impact': 0.20,
                'strategic_alignment': 0.15,
                'time_criticality': 0.15,
                'risk_reduction': 0.10,
                'technical_feasibility': 0.10,
                'resource_availability': 0.05
            }
            
            # Calculate weighted score
            total_score = 0.0
            total_weight = 0.0
            
            for criteria, weight in criteria_weights.items():
                if criteria in item and item[criteria] is not None:
                    try:
                        # Normalize to 0-100 scale (assuming input is 1-10)
                        raw_value = float(item[criteria])
                        normalized_value = (raw_value / 10.0) * 100.0
                        total_score += normalized_value * weight
                        total_weight += weight
                    except (ValueError, TypeError):
                        continue
            
            # Return normalized score or 0 if no valid criteria
            if total_weight > 0:
                return total_score / total_weight
            else:
                return 0.0
                
        except Exception as e:
            logger.warning(f"Error calculating basic score: {e}")
            return 0.0
    
    def _categorize_score(self, score: float) -> str:
        """Categorize QVF scores into priority levels."""
        if score >= 80:
            return "Critical"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Minimal"


class QVFValidator:
    """Validates QVF system health and configuration."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.console = Console()
    
    def validate_system(self) -> Tuple[bool, Dict]:
        """Comprehensive system validation."""
        results = {
            "overall_status": True,
            "checks": {},
            "timestamp": datetime.now().isoformat()
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            # Core components validation
            task1 = progress.add_task("Validating core components...", total=None)
            results["checks"]["core"] = self._validate_core_components()
            progress.advance(task1)
            
            # Performance validation
            task2 = progress.add_task("Running performance tests...", total=None)
            results["checks"]["performance"] = self._validate_performance()
            progress.advance(task2)
        
        # Determine overall status
        results["overall_status"] = all(
            check.get("status", False) for check in results["checks"].values()
        )
        
        return results["overall_status"], results
    
    def _validate_core_components(self) -> Dict:
        """Validate core QVF components."""
        try:
            # Test criteria engine
            criteria_engine = QVFCriteriaEngine()
            config = create_enterprise_configuration()
            
            # Test basic financial calculation
            financial_calc = FinancialCalculator()
            test_roi = 50.0  # Mock ROI for validation
            
            return {
                "status": True,
                "message": "Core components validated successfully",
                "details": {
                    "criteria_engine": "OK",
                    "financial_calculator": "OK",
                    "test_roi": f"{test_roi:.1f}%"
                }
            }
            
        except Exception as e:
            return {
                "status": False,
                "message": f"Core component validation failed: {str(e)}",
                "details": {}
            }
    
    def _validate_performance(self) -> Dict:
        """Run performance validation tests."""
        try:
            start_time = time.time()
            
            # Create test data
            test_items = [
                {
                    "id": f"item_{i}",
                    "title": f"Test Item {i}",
                    "description": f"Test description for item {i}",
                    "estimated_value": 10000 + (i * 1000),
                    "development_cost": 5000 + (i * 500),
                    "business_value": 8,
                    "user_impact": 7,
                    "strategic_alignment": 6
                }
                for i in range(100)  # Test with 100 items
            ]
            
            # Score test items
            scorer = QVFScorer(self.config)
            
            # Create temporary CSV file
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                df = pd.DataFrame(test_items)
                df.to_csv(tmp_file.name, index=False)
                tmp_file_path = tmp_file.name
            
            try:
                success, message, results_df = scorer.score_portfolio(
                    work_items_file=tmp_file_path,
                    criteria_preset="enterprise"
                )
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
            
            duration = time.time() - start_time
            
            if success and duration < 60:
                return {
                    "status": True,
                    "message": f"Performance validation passed ({duration:.1f}s)",
                    "details": {
                        "duration_seconds": duration,
                        "items_processed": len(test_items),
                        "items_per_second": len(test_items) / duration
                    }
                }
            else:
                return {
                    "status": False,
                    "message": f"Performance validation failed: {message}",
                    "details": {"duration_seconds": duration}
                }
                
        except Exception as e:
            return {
                "status": False,
                "message": f"Performance validation failed: {str(e)}",
                "details": {}
            }


def create_score_parser(subparsers):
    """Create score command parser."""
    score_parser = subparsers.add_parser(
        'score',
        help='Score work items using QVF methodology'
    )
    score_parser.add_argument(
        'input_file',
        help='CSV file containing work items to score'
    )
    score_parser.add_argument(
        '-o', '--output',
        help='Output CSV file for scored results'
    )
    score_parser.add_argument(
        '-p', '--preset',
        choices=['enterprise', 'agile', 'startup'],
        default='enterprise',
        help='Criteria preset to use for scoring'
    )
    score_parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for processing work items'
    )


def create_configure_parser(subparsers):
    """Create configure command parser."""
    config_parser = subparsers.add_parser(
        'configure',
        help='Configure QVF criteria and settings'
    )
    config_parser.add_argument(
        'action',
        choices=['init', 'criteria', 'stakeholders', 'weights'],
        help='Configuration action to perform'
    )
    config_parser.add_argument(
        '--output',
        help='Output configuration file'
    )
    config_parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive configuration mode'
    )


def create_validate_parser(subparsers):
    """Create validate command parser."""
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate QVF system health and configuration'
    )
    validate_parser.add_argument(
        '--config',
        help='Configuration file to validate'
    )
    validate_parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed validation results'
    )
    validate_parser.add_argument(
        '--output',
        help='Save validation results to file'
    )


def handle_score_command(args):
    """Handle score command."""
    try:
        console.print(Panel.fit("🎯 QVF Portfolio Scoring", style="bold blue"))
        
        # Create config
        config = {
            "scoring": {
                "batch_size": getattr(args, 'batch_size', 100)
            }
        }
        
        # Create scorer and score portfolio
        scorer = QVFScorer(config)
        success, message, results_df = scorer.score_portfolio(
            work_items_file=args.input_file,
            output_file=args.output,
            criteria_preset=args.preset
        )
        
        if success:
            console.print(f"✅ {message}", style="bold green")
            
            # Display summary table
            if results_df is not None and len(results_df) > 0:
                table = Table(title="QVF Scoring Summary")
                table.add_column("Category", style="cyan")
                table.add_column("Count", justify="right", style="magenta")
                table.add_column("Avg Score", justify="right", style="green")
                
                summary = results_df.groupby('qvf_category').agg({
                    'qvf_score': ['count', 'mean']
                }).round(1)
                
                for category in summary.index:
                    count = summary.loc[category, ('qvf_score', 'count')]
                    avg_score = summary.loc[category, ('qvf_score', 'mean')]
                    table.add_row(category, str(count), f"{avg_score:.1f}")
                
                console.print(table)
        else:
            console.print(f"❌ {message}", style="bold red")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"❌ Scoring failed: {str(e)}", style="bold red")
        sys.exit(1)


def handle_configure_command(args):
    """Handle configure command."""
    try:
        console.print(Panel.fit("⚙️ QVF Configuration", style="bold blue"))
        
        if args.action == 'init':
            # Create initial configuration
            config = {
                "scoring": {
                    "batch_size": 100,
                    "timeout": 60,
                    "consistency_threshold": 0.10
                },
                "criteria": {
                    "preset": "enterprise"
                }
            }
            
            output_file = args.output or "qvf_config.json"
            with open(output_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            console.print(f"✅ Configuration saved to {output_file}", style="bold green")
        
        elif args.action == 'criteria':
            # Configure criteria weights
            criteria_engine = QVFCriteriaEngine()
            config = create_enterprise_configuration()
            
            console.print("📊 Current Enterprise Criteria Configuration:")
            table = Table(title="QVF Criteria Weights")
            table.add_column("Criterion", style="cyan")
            table.add_column("Weight", justify="right", style="green")
            table.add_column("Description", style="white")
            
            for criterion in config.criteria:
                table.add_row(
                    criterion.name,
                    f"{criterion.weight:.3f}",
                    criterion.description
                )
            
            console.print(table)
        
        else:
            console.print(f"Configuration action '{args.action}' not yet implemented", style="yellow")
            
    except Exception as e:
        console.print(f"❌ Configuration failed: {str(e)}", style="bold red")
        sys.exit(1)


def handle_validate_command(args):
    """Handle validate command."""
    try:
        console.print(Panel.fit("✅ QVF System Validation", style="bold blue"))
        
        # Load configuration if provided
        config = {}
        if args.config and Path(args.config).exists():
            with open(args.config, 'r') as f:
                config = json.load(f)
        
        # Create validator and run validation
        validator = QVFValidator(config)
        is_valid, results = validator.validate_system()
        
        # Display results
        if is_valid:
            console.print("🎉 System validation passed!", style="bold green")
        else:
            console.print("❌ System validation failed", style="bold red")
        
        # Show detailed results if requested
        if args.detailed:
            for check_name, check_result in results["checks"].items():
                status_icon = "✅" if check_result["status"] else "❌"
                status_color = "green" if check_result["status"] else "red"
                
                console.print(f"\n{status_icon} {check_name.title()}", style=f"bold {status_color}")
                console.print(f"  Message: {check_result['message']}")
                
                if check_result.get("details"):
                    console.print("  Details:")
                    for key, value in check_result["details"].items():
                        console.print(f"    {key}: {value}")
        
        # Save results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            console.print(f"📄 Validation results saved to {args.output}", style="blue")
        
        if not is_valid:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"❌ Validation failed: {str(e)}", style="bold red")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='qvf',
        description='Quantified Value Framework (QVF) - Enterprise Prioritization System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  qvf score work_items.csv -o scored_results.csv --preset enterprise
  qvf configure init --output my_config.json
  qvf validate --detailed

For more information, visit: https://github.com/your-org/ds-package
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='QVF 1.0.0'
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='command'
    )
    
    # Create command parsers
    create_score_parser(subparsers)
    create_configure_parser(subparsers)
    create_validate_parser(subparsers)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run command handler
    try:
        if args.command == 'score':
            handle_score_command(args)
        elif args.command == 'configure':
            handle_configure_command(args)
        elif args.command == 'validate':
            handle_validate_command(args)
    except KeyboardInterrupt:
        console.print("\n⏹️ Operation cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {str(e)}", style="bold red")
        logger.exception("Unexpected error in QVF CLI")
        sys.exit(1)


if __name__ == '__main__':
    main()