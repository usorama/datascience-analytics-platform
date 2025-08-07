"""ADO Analytics Analyzer

Main interface for analyzing Azure DevOps data using AHP prioritization
and comprehensive Agile metrics.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union
from pathlib import Path
import json
import logging

from ..orchestrator.pipeline import AnalyticsPipeline, PipelineConfig
from ..dashboard.generator import DashboardGenerator
from .models import ADOWorkItem, WorkItemHierarchy, WorkItemType
from .ahp import AHPEngine, AHPConfiguration, AHPCriterion
from .metrics import AgileMetricsCalculator
from .simulation import ADODataSimulator
from .data_validator import RobustDataProcessor, FilterableDataProcessor, DataValidationError

logger = logging.getLogger(__name__)


class ADOAnalyzer:
    """Main analyzer for ADO work items with AHP and metrics."""
    
    def __init__(self, ahp_config: Optional[AHPConfiguration] = None):
        """Initialize ADO analyzer.
        
        Args:
            ahp_config: Optional AHP configuration, uses default if None
        """
        self.ahp_config = ahp_config or self._get_default_ahp_config()
        self.ahp_engine = AHPEngine(self.ahp_config)
        self.work_items: List[ADOWorkItem] = []
        self.hierarchy: Optional[WorkItemHierarchy] = None
        self.metrics_calculator: Optional[AgileMetricsCalculator] = None
        self.analysis_results: Dict[str, Any] = {}
        
    def _get_default_ahp_config(self) -> AHPConfiguration:
        """Get default AHP configuration for ADO analysis."""
        criteria = [
            AHPCriterion(
                name="business_value",
                description="Normalized business value score",
                weight=0.0,  # Will be calculated by AHP
                data_source="business_value_normalized",
                higher_is_better=True,
                normalization_method="minmax"
            ),
            AHPCriterion(
                name="roi_efficiency",
                description="Value per story point ratio",
                weight=0.0,
                data_source="roi_score",
                higher_is_better=True,
                normalization_method="minmax"
            ),
            AHPCriterion(
                name="strategic_alignment",
                description="Alignment with strategy pillars",
                weight=0.0,
                data_source="strategy_score",
                higher_is_better=True,
                normalization_method="minmax",
                value_mapping={
                    "Customer Experience": 1.0,
                    "Operational Excellence": 0.9,
                    "Innovation": 0.8,
                    "Security & Compliance": 0.7,
                    "Growth": 0.85
                }
            ),
            AHPCriterion(
                name="risk_complexity",
                description="Combined risk and complexity (inverted)",
                weight=0.0,
                data_source="risk_complexity_score",
                higher_is_better=False,  # Lower is better
                normalization_method="minmax"
            ),
            AHPCriterion(
                name="team_confidence",
                description="Team velocity and completion rate",
                weight=0.0,
                data_source="team_confidence_score",
                higher_is_better=True,
                normalization_method="minmax"
            )
        ]
        
        return AHPConfiguration(criteria=criteria)
    
    def load_from_csv(self, file_path: Union[str, Path]) -> List[ADOWorkItem]:
        """Load ADO work items from CSV file with robust validation.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of loaded work items
        """
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise DataValidationError(f"Failed to read CSV file: {e}")
        
        return self.load_from_dataframe(df)
    
    def load_from_dataframe(self, df: pd.DataFrame) -> List[ADOWorkItem]:
        """Load ADO work items from pandas DataFrame with validation.
        
        Args:
            df: DataFrame with ADO data
            
        Returns:
            List of loaded work items
        """
        # Validate and clean data
        processor = RobustDataProcessor()
        try:
            df_clean = processor.validate_and_clean_dataframe(df, data_type='work_items')
            
            # Print validation report
            processor.print_validation_report()
            
        except DataValidationError as e:
            logger.error(f"Data validation failed: {e}")
            raise
        
        self.work_items = []
        
        # Map column names to model fields
        column_mapping = {
            # Standard ADO export columns
            'Work Item ID': 'work_item_id',
            'ID': 'work_item_id',
            'Title': 'title',
            'Work Item Type': 'work_item_type',
            'State': 'state',
            'Parent': 'parent_id',
            'Business Value': 'business_value_raw',
            'Story Points': 'story_points',
            'Effort': 'effort_hours',
            'Risk Score': 'risk_score',
            'Complexity': 'complexity_score',
            'Created Date': 'created_date',
            'Closed Date': 'closed_date',
            'Iteration Path': 'iteration_path',
            'Area Path': 'area_path',
            'Assigned To': 'assigned_to',
            'Tags': 'tags',
            # Our export format columns
            'WorkItemId': 'work_item_id',
            'WorkItemType': 'work_item_type',
            'ParentId': 'parent_id',
            'BusinessValue': 'business_value_raw',
            'BusinessValueNormalized': 'business_value_normalized',
            'StoryPoints': 'story_points',
            'EffortHours': 'effort_hours',
            'ComplexityScore': 'complexity_score',
            'RiskScore': 'risk_score',
            'CreatedDate': 'created_date',
            'ActivatedDate': 'activated_date',
            'ResolvedDate': 'resolved_date',
            'ClosedDate': 'closed_date',
            'TargetDate': 'target_date',
            'IterationPath': 'iteration_path',
            'AreaPath': 'area_path',
            'AssignedTo': 'assigned_to',
            'PINumber': 'pi_number',
            'StrategyPillar': 'strategy_pillar',
            'CycleTimeDays': 'cycle_time_days',
            'LeadTimeDays': 'lead_time_days',
            'BlockedDays': 'blocked_days'
        }
        
        # Rename columns based on mapping
        df_renamed = df.rename(columns=column_mapping)
        
        # Convert to work items
        for _, row in df_renamed.iterrows():
            work_item_data = row.to_dict()
            
            # Clean up data - handle arrays properly
            cleaned_data = {}
            for k, v in work_item_data.items():
                if isinstance(v, (list, np.ndarray)):
                    # For arrays/lists, only include if not empty
                    if len(v) > 0:
                        cleaned_data[k] = v
                else:
                    # For scalar values, use pd.notna
                    if pd.notna(v):
                        cleaned_data[k] = v
            work_item_data = cleaned_data
            
            # Parse dates
            for date_field in ['created_date', 'closed_date', 'activated_date', 'resolved_date']:
                if date_field in work_item_data:
                    work_item_data[date_field] = pd.to_datetime(work_item_data[date_field])
            
            # Parse tags
            if 'tags' in work_item_data and isinstance(work_item_data['tags'], str):
                work_item_data['tags'] = work_item_data['tags'].split(';')
            
            # Create appropriate work item type
            try:
                work_item_type = WorkItemType(work_item_data.get('work_item_type', 'User Story'))
                
                # Create work item
                work_item = ADOWorkItem(**work_item_data)
                self.work_items.append(work_item)
                
            except Exception as e:
                logger.warning(f"Failed to parse work item: {e}")
                continue
        
        # Build hierarchy
        self._build_hierarchy()
        
        return self.work_items
    
    def load_simulated_data(
        self,
        scenario: str = 'balanced',
        **kwargs
    ) -> List[ADOWorkItem]:
        """Load simulated ADO data for testing.
        
        Args:
            scenario: Scenario type ('high_performing', 'struggling', 'growing', 'balanced')
            **kwargs: Additional parameters for simulation
            
        Returns:
            List of simulated work items
        """
        simulator = ADODataSimulator()
        
        if scenario == 'custom':
            self.work_items = simulator.generate_multi_pi_data(**kwargs)
        else:
            # Use predefined scenarios
            scenarios = simulator.generate_sample_scenarios()
            if scenario in scenarios:
                self.work_items = scenarios[scenario]
            else:
                # Default balanced scenario
                self.work_items = simulator.generate_multi_pi_data(
                    num_pis=4,
                    num_epics=10,
                    completion_rate=0.75,
                    cancellation_rate=0.10
                )
        
        # Build hierarchy
        self._build_hierarchy()
        
        return self.work_items
    
    def _build_hierarchy(self):
        """Build work item hierarchy."""
        self.hierarchy = WorkItemHierarchy()
        for item in self.work_items:
            self.hierarchy.add_work_item(item)
    
    def configure_ahp(
        self,
        comparison_matrix: Optional[np.ndarray] = None,
        preferences: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Configure AHP weights.
        
        Args:
            comparison_matrix: Direct comparison matrix
            preferences: Dictionary of criterion preferences
            
        Returns:
            AHP configuration results
        """
        if comparison_matrix is not None:
            self.ahp_engine.comparison_matrix = comparison_matrix
        elif preferences is not None:
            self.ahp_engine.create_comparison_matrix_from_preferences(preferences)
        else:
            # Use default preferences
            default_preferences = {
                'business_value': 5,
                'roi_efficiency': 4,
                'strategic_alignment': 3,
                'risk_complexity': 2,
                'team_confidence': 3
            }
            self.ahp_engine.create_comparison_matrix_from_preferences(default_preferences)
        
        # Calculate weights
        self.ahp_engine.calculate_weights()
        cr = self.ahp_engine.calculate_consistency_ratio()
        
        return {
            'weights': {c.name: c.weight for c in self.ahp_config.criteria},
            'consistency_ratio': cr,
            'is_consistent': self.ahp_engine.is_consistent()
        }
    
    def analyze(
        self,
        data_source: Optional[Union[str, Path, pd.DataFrame]] = None,
        generate_dashboard: bool = True,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Run comprehensive ADO analysis.
        
        Args:
            data_source: Optional data source (uses loaded data if None)
            generate_dashboard: Whether to generate HTML dashboard
            output_dir: Output directory for results
            
        Returns:
            Analysis results dictionary
        """
        # Load data if provided
        if data_source is not None:
            if isinstance(data_source, (str, Path)):
                self.load_from_csv(data_source)
            elif isinstance(data_source, pd.DataFrame):
                self.load_from_dataframe(data_source)
        
        if not self.work_items:
            raise ValueError("No work items loaded for analysis")
        
        # Prepare work items for AHP scoring
        self._prepare_work_items_for_ahp()
        
        # Initialize metrics calculator
        self.metrics_calculator = AgileMetricsCalculator(self.work_items, self.hierarchy)
        
        # Run analyses
        self.analysis_results = {
            'summary': self._generate_summary(),
            'ahp_prioritization': self._run_ahp_analysis(),
            'pi_metrics': self.metrics_calculator.calculate_pi_metrics(),
            'team_metrics': self.metrics_calculator.calculate_team_metrics(),
            'flow_metrics': self.metrics_calculator.calculate_flow_metrics(),
            'predictability': self.metrics_calculator.calculate_predictability_metrics(),
            'bottlenecks': self.metrics_calculator.identify_bottlenecks(),
            'insights': self.metrics_calculator.generate_insights(),
            'hierarchy_validation': self.hierarchy.validate_hierarchy() if self.hierarchy else None
        }
        
        # Generate dashboard if requested
        if generate_dashboard:
            if output_dir is None:
                output_dir = Path("./ado_analysis_output")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            dashboard_path = self.create_dashboard(self.analysis_results, output_dir)
            self.analysis_results['dashboard_path'] = str(dashboard_path)
        
        return self.analysis_results
    
    def _prepare_work_items_for_ahp(self):
        """Prepare work items with calculated fields for AHP scoring."""
        for item in self.work_items:
            # Calculate ROI score
            item.custom_fields['roi_score'] = item.calculate_roi_score() or 0
            
            # Map strategy pillar to score if criterion exists
            strategic_criterion = self.ahp_config.get_criterion_by_name('strategic_alignment')
            if strategic_criterion and item.strategy_pillar:
                mapping = strategic_criterion.value_mapping or {}
                item.custom_fields['strategy_score'] = mapping.get(item.strategy_pillar, 0.5)
            else:
                item.custom_fields['strategy_score'] = 0.5
            
            # Calculate risk-complexity combined score
            risk = item.risk_score or 50
            complexity = item.complexity_score or 50
            item.custom_fields['risk_complexity_score'] = (risk + complexity) / 2
            
            # Calculate team confidence score
            if item.team_metrics:
                confidence = item.team_metrics.historical_completion_rate or 0.7
                velocity_factor = min(item.team_metrics.velocity or 30, 60) / 60
                item.custom_fields['team_confidence_score'] = (confidence + velocity_factor) / 2
            else:
                item.custom_fields['team_confidence_score'] = 0.7
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate analysis summary."""
        total_items = len(self.work_items)
        
        # Count by type
        type_counts = {}
        for item in self.work_items:
            type_name = item.work_item_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Count by state
        state_counts = {}
        for item in self.work_items:
            state_name = item.state.value
            state_counts[state_name] = state_counts.get(state_name, 0) + 1
        
        # Calculate totals
        total_points = sum(item.story_points or 0 for item in self.work_items)
        completed_points = sum(
            item.story_points or 0 
            for item in self.work_items 
            if item.is_completed()
        )
        
        return {
            'total_items': total_items,
            'type_distribution': type_counts,
            'state_distribution': state_counts,
            'total_story_points': total_points,
            'completed_story_points': completed_points,
            'completion_rate': (completed_points / total_points * 100) if total_points > 0 else 0,
            'unique_teams': len(set(item.area_path for item in self.work_items if item.area_path)),
            'date_range': {
                'earliest': min((item.created_date for item in self.work_items if item.created_date), default=None),
                'latest': max((item.closed_date or item.created_date for item in self.work_items if item.created_date), default=None)
            }
        }
    
    def _run_ahp_analysis(self) -> Dict[str, Any]:
        """Run AHP prioritization analysis."""
        # Ensure AHP is configured
        if self.ahp_engine.weights is None:
            self.configure_ahp()
        
        # Prepare work items data for AHP
        work_items_data = []
        for item in self.work_items:
            item_data = {
                'work_item_id': item.work_item_id,
                'title': item.title,
                'type': item.work_item_type.value,
                'business_value_normalized': item.business_value_normalized or 0,
                'roi_score': item.custom_fields.get('roi_score', 0),
                'strategy_score': item.custom_fields.get('strategy_score', 0.5),
                'risk_complexity_score': item.custom_fields.get('risk_complexity_score', 50),
                'team_confidence_score': item.custom_fields.get('team_confidence_score', 0.7)
            }
            work_items_data.append(item_data)
        
        # Rank work items
        rankings = self.ahp_engine.rank_work_items(work_items_data)
        
        # Create prioritized list
        prioritized_items = []
        for idx, score, criterion_scores in rankings[:20]:  # Top 20 items
            item = self.work_items[idx]
            prioritized_items.append({
                'rank': len(prioritized_items) + 1,
                'work_item_id': item.work_item_id,
                'title': item.title,
                'type': item.work_item_type.value,
                'ahp_score': score,
                'criterion_scores': criterion_scores,
                'business_value': item.business_value_raw,
                'story_points': item.story_points,
                'state': item.state.value
            })
        
        # Identify items to defer (bottom 10%)
        defer_threshold = int(len(rankings) * 0.9)
        defer_candidates = []
        for idx, score, _ in rankings[defer_threshold:]:
            item = self.work_items[idx]
            if not item.is_completed():
                defer_candidates.append({
                    'work_item_id': item.work_item_id,
                    'title': item.title,
                    'ahp_score': score,
                    'reason': 'Low AHP priority score'
                })
        
        return {
            'ahp_config': self.ahp_engine.export_results(),
            'top_priorities': prioritized_items,
            'defer_candidates': defer_candidates[:10],  # Top 10 to defer
            'total_items_ranked': len(rankings)
        }
    
    def create_dashboard(
        self,
        results: Optional[Dict[str, Any]] = None,
        output_dir: Optional[Path] = None
    ) -> Path:
        """Create interactive dashboard from analysis results.
        
        Args:
            results: Analysis results (uses stored results if None)
            output_dir: Output directory
            
        Returns:
            Path to generated dashboard HTML
        """
        if results is None:
            results = self.analysis_results
        
        if output_dir is None:
            output_dir = Path("./ado_analysis_output")
        
        dashboard = DashboardGenerator(theme="light", compress=True)
        
        # Configure dashboard
        dashboard.set_config(
            title="ADO Analytics Dashboard - Quantified Value Framework",
            description="Objective prioritization and metrics for Azure DevOps work items",
            theme_switcher=True,
            responsive=True
        )
        
        # Add KPI cards
        summary = results.get('summary', {})
        dashboard.add_kpi_card(
            title="Total Work Items",
            value=f"{summary.get('total_items', 0):,}",
            subtitle="Across all PIs",
            icon="folder"
        )
        
        dashboard.add_kpi_card(
            title="Completion Rate",
            value=f"{summary.get('completion_rate', 0):.1f}%",
            subtitle="Story points completed",
            trend=summary.get('completion_rate', 0) - 75,  # Relative to 75% target
            icon="check-circle"
        )
        
        predictability = results.get('predictability', {})
        dashboard.add_kpi_card(
            title="PI Predictability",
            value=f"{predictability.get('average_predictability', 0):.0f}%",
            subtitle=predictability.get('predictability_trend', 'stable').title(),
            icon="trending-up"
        )
        
        # Add AHP prioritization table
        ahp_results = results.get('ahp_prioritization', {})
        if ahp_results.get('top_priorities'):
            priorities_df = pd.DataFrame(ahp_results['top_priorities'])
            dashboard.add_data_table(
                data=priorities_df,
                table_id="ahp_priorities",
                title="AHP Prioritized Work Items (Top 20)",
                searchable=True,
                sortable=True,
                paginated=True,
                page_size=10
            )
        
        # Add PI velocity chart
        pi_metrics = results.get('pi_metrics', [])
        if pi_metrics:
            velocity_data = pd.DataFrame([
                {
                    'PI': f"PI {m.pi_number}",
                    'Velocity': m.velocity,
                    'Predictability': m.predictability
                }
                for m in pi_metrics
            ])
            
            dashboard.add_chart(
                chart_type="line_chart",
                data=velocity_data,
                chart_id="velocity_trend",
                title="Velocity and Predictability Trend",
                height=350,
                x='PI',
                y='Velocity'
            )
        
        # Add team performance comparison
        team_metrics = results.get('team_metrics', {})
        if team_metrics:
            team_data = pd.DataFrame([
                {
                    'Team': name,
                    'Average Velocity': metrics.average_velocity,
                    'Cycle Time P50': metrics.cycle_time_p50
                }
                for name, metrics in team_metrics.items()
            ])
            
            dashboard.add_chart(
                chart_type="bar_chart",
                data=team_data,
                chart_id="team_comparison",
                title="Team Performance Comparison",
                height=300,
                x='Team',
                y='Average Velocity'
            )
        
        # Add insights section
        insights = results.get('insights', [])
        if insights:
            insights_html = "<div class='insights-container'>"
            for insight in insights:
                severity_color = {
                    'high': '#dc3545',
                    'medium': '#ffc107',
                    'low': '#28a745'
                }.get(insight.get('severity', 'medium'), '#6c757d')
                
                insights_html += f"""
                <div class='insight-card' style='border-left: 4px solid {severity_color}; padding: 1rem; margin: 0.5rem 0; background: #f8f9fa;'>
                    <h4>{insight.get('title', 'Insight')}</h4>
                    <p>{insight.get('description', '')}</p>
                    <small><strong>Recommendation:</strong> {insight.get('recommendation', '')}</small>
                </div>
                """
            insights_html += "</div>"
            
            # TODO: Add custom insights section when method is available
            # dashboard.add_custom_section(
            #     "Key Insights and Recommendations",
            #     insights_html,
            #     "insights_section"
            # )
        
        # Generate and save dashboard
        dashboard_path = output_dir / "ado_analytics_dashboard.html"
        # Check if dashboard has generate_html method
        if hasattr(dashboard, 'generate_html'):
            dashboard.generate_html(str(dashboard_path))
        elif hasattr(dashboard, 'generate_dashboard'):
            success, path = dashboard.generate_dashboard(
                self.df if hasattr(self, 'df') else pd.DataFrame(),
                self.analysis_results,
                None  # No ML pipeline for this test
            )
            if success:
                dashboard_path = path
        else:
            logger.warning("Dashboard generation method not available")
        
        # Also save raw results as JSON
        results_path = output_dir / "analysis_results.json"
        with open(results_path, 'w') as f:
            # Convert non-serializable objects
            def json_serializer(obj):
                if hasattr(obj, 'dict'):
                    return obj.dict()
                elif hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                else:
                    return str(obj)
            
            json.dump(results, f, indent=2, default=json_serializer)
        
        logger.info(f"Dashboard generated at: {dashboard_path}")
        logger.info(f"Results saved at: {results_path}")
        
        return dashboard_path
    
    @property
    def top_priorities(self) -> List[Dict[str, Any]]:
        """Get top priority items from AHP analysis."""
        if 'ahp_prioritization' in self.analysis_results:
            return self.analysis_results['ahp_prioritization'].get('top_priorities', [])
        return []
    
    @property
    def defer_candidates(self) -> List[Dict[str, Any]]:
        """Get items recommended for deferral."""
        if 'ahp_prioritization' in self.analysis_results:
            return self.analysis_results['ahp_prioritization'].get('defer_candidates', [])
        return []
    
    @property
    def predictability_score(self) -> float:
        """Get overall predictability score."""
        if 'predictability' in self.analysis_results:
            return self.analysis_results['predictability'].get('average_predictability', 0)
        return 0