"""Agile Metrics Calculator

This module calculates comprehensive Agile metrics for ADO work items,
including velocity, cycle time, lead time, and predictability scoring.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict
import logging
from dataclasses import dataclass

from .models import ADOWorkItem, WorkItemHierarchy, WorkItemState, WorkItemType

logger = logging.getLogger(__name__)


@dataclass
class PIMetrics:
    """Metrics for a Program Increment."""
    pi_number: int
    start_date: datetime
    end_date: datetime
    planned_story_points: float
    completed_story_points: float
    cancelled_story_points: float
    deferred_story_points: float
    velocity: float
    predictability: float
    completion_rate: float
    cancellation_rate: float
    team_metrics: Dict[str, Dict[str, float]]


@dataclass
class TeamMetrics:
    """Metrics for a specific team."""
    team_name: str
    velocity_trend: List[float]
    average_velocity: float
    velocity_stability: float  # Standard deviation / mean
    cycle_time_p50: float
    cycle_time_p90: float
    lead_time_p50: float
    lead_time_p90: float
    throughput: float  # Items completed per PI
    wip_limit_violations: int
    blocked_time_percentage: float


@dataclass
class FlowMetrics:
    """Flow metrics for work items."""
    cycle_time_distribution: Dict[str, float]
    lead_time_distribution: Dict[str, float]
    flow_efficiency: float
    wait_time_percentage: float
    touch_time_percentage: float
    blocked_time_percentage: float
    rework_percentage: float


class AgileMetricsCalculator:
    """Calculate Agile metrics for ADO work items."""
    
    def __init__(self, work_items: List[ADOWorkItem], hierarchy: Optional[WorkItemHierarchy] = None):
        """Initialize calculator with work items.
        
        Args:
            work_items: List of ADO work items
            hierarchy: Optional work item hierarchy
        """
        self.work_items = work_items
        self.hierarchy = hierarchy or self._build_hierarchy(work_items)
        self.metrics_cache = {}
        
    def _build_hierarchy(self, work_items: List[ADOWorkItem]) -> WorkItemHierarchy:
        """Build hierarchy from work items list."""
        hierarchy = WorkItemHierarchy()
        for item in work_items:
            hierarchy.add_work_item(item)
        return hierarchy
    
    def calculate_pi_metrics(
        self, 
        pi_duration_weeks: int = 10,
        start_date: Optional[datetime] = None
    ) -> List[PIMetrics]:
        """Calculate metrics by Program Increment.
        
        Args:
            pi_duration_weeks: Duration of each PI in weeks
            start_date: Start date for PI calculation
            
        Returns:
            List of PI metrics
        """
        # Group work items by PI
        pi_groups = self._group_by_pi(pi_duration_weeks, start_date)
        pi_metrics_list = []
        
        for pi_num, (pi_start, pi_end, items) in pi_groups.items():
            # Calculate planned vs actual
            planned_points = sum(
                item.story_points or 0 
                for item in items 
                if item.created_date and item.created_date <= pi_start
            )
            
            completed_points = sum(
                item.story_points or 0 
                for item in items 
                if item.is_completed()
            )
            
            cancelled_points = sum(
                item.story_points or 0 
                for item in items 
                if item.state == WorkItemState.CANCELLED
            )
            
            deferred_points = sum(
                item.story_points or 0 
                for item in items 
                if item.state == WorkItemState.DEFERRED
            )
            
            # Calculate rates
            total_points = planned_points if planned_points > 0 else 1
            velocity = completed_points
            predictability = (completed_points / planned_points * 100) if planned_points > 0 else 0
            completion_rate = (completed_points / total_points * 100)
            cancellation_rate = (cancelled_points / total_points * 100)
            
            # Calculate team-specific metrics
            team_metrics = self._calculate_team_metrics_for_pi(items)
            
            pi_metrics = PIMetrics(
                pi_number=pi_num,
                start_date=pi_start,
                end_date=pi_end,
                planned_story_points=planned_points,
                completed_story_points=completed_points,
                cancelled_story_points=cancelled_points,
                deferred_story_points=deferred_points,
                velocity=velocity,
                predictability=predictability,
                completion_rate=completion_rate,
                cancellation_rate=cancellation_rate,
                team_metrics=team_metrics
            )
            
            pi_metrics_list.append(pi_metrics)
        
        return pi_metrics_list
    
    def _group_by_pi(
        self, 
        pi_duration_weeks: int,
        start_date: Optional[datetime] = None
    ) -> Dict[int, Tuple[datetime, datetime, List[ADOWorkItem]]]:
        """Group work items by PI number."""
        # Find earliest date if not provided
        if not start_date:
            dates = [item.created_date for item in self.work_items if item.created_date]
            start_date = min(dates) if dates else datetime.now()
        
        pi_groups = defaultdict(lambda: (None, None, []))
        pi_duration = timedelta(weeks=pi_duration_weeks)
        
        for item in self.work_items:
            # Determine PI based on target date or created date
            reference_date = item.target_date or item.created_date
            if not reference_date:
                continue
            
            # Calculate PI number
            time_since_start = reference_date - start_date
            pi_number = int(time_since_start.days / (pi_duration_weeks * 7)) + 1
            
            # Calculate PI boundaries
            pi_start = start_date + (pi_number - 1) * pi_duration
            pi_end = pi_start + pi_duration
            
            # Add to group
            if pi_groups[pi_number][0] is None:
                pi_groups[pi_number] = (pi_start, pi_end, [item])
            else:
                pi_groups[pi_number][2].append(item)
        
        return dict(pi_groups)
    
    def _calculate_team_metrics_for_pi(
        self, 
        items: List[ADOWorkItem]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate team-specific metrics for a PI."""
        team_groups = defaultdict(list)
        
        # Group by team
        for item in items:
            team = item.area_path or "Unassigned"
            team_groups[team].append(item)
        
        team_metrics = {}
        for team, team_items in team_groups.items():
            completed_points = sum(
                item.story_points or 0 
                for item in team_items 
                if item.is_completed()
            )
            
            cycle_times = [
                item.cycle_time_days 
                for item in team_items 
                if item.cycle_time_days is not None
            ]
            
            team_metrics[team] = {
                'velocity': completed_points,
                'throughput': len([i for i in team_items if i.is_completed()]),
                'cycle_time_avg': np.mean(cycle_times) if cycle_times else 0,
                'items_count': len(team_items)
            }
        
        return team_metrics
    
    def calculate_team_metrics(self) -> Dict[str, TeamMetrics]:
        """Calculate comprehensive metrics by team."""
        team_groups = defaultdict(list)
        
        # Group by team
        for item in self.work_items:
            team = item.area_path or "Unassigned"
            team_groups[team].append(item)
        
        team_metrics_dict = {}
        
        for team, items in team_groups.items():
            # Calculate velocity trend by PI
            pi_metrics = self.calculate_pi_metrics()
            velocity_trend = [
                pi.team_metrics.get(team, {}).get('velocity', 0)
                for pi in pi_metrics
            ]
            
            avg_velocity = np.mean(velocity_trend) if velocity_trend else 0
            velocity_stability = (
                np.std(velocity_trend) / avg_velocity 
                if avg_velocity > 0 else 0
            )
            
            # Calculate cycle and lead times
            cycle_times = [
                item.cycle_time_days 
                for item in items 
                if item.cycle_time_days is not None
            ]
            lead_times = [
                item.lead_time_days 
                for item in items 
                if item.lead_time_days is not None
            ]
            
            # Calculate flow metrics
            blocked_time = sum(
                item.blocked_days or 0 
                for item in items
            )
            total_time = sum(
                item.cycle_time_days or 0 
                for item in items
            )
            blocked_percentage = (
                (blocked_time / total_time * 100) 
                if total_time > 0 else 0
            )
            
            metrics = TeamMetrics(
                team_name=team,
                velocity_trend=velocity_trend,
                average_velocity=avg_velocity,
                velocity_stability=velocity_stability,
                cycle_time_p50=np.percentile(cycle_times, 50) if cycle_times else 0,
                cycle_time_p90=np.percentile(cycle_times, 90) if cycle_times else 0,
                lead_time_p50=np.percentile(lead_times, 50) if lead_times else 0,
                lead_time_p90=np.percentile(lead_times, 90) if lead_times else 0,
                throughput=len([i for i in items if i.is_completed()]) / len(pi_metrics) if pi_metrics else 0,
                wip_limit_violations=0,  # Would need WIP limits to calculate
                blocked_time_percentage=blocked_percentage
            )
            
            team_metrics_dict[team] = metrics
        
        return team_metrics_dict
    
    def calculate_flow_metrics(
        self, 
        work_item_types: Optional[List[WorkItemType]] = None
    ) -> FlowMetrics:
        """Calculate flow metrics for work items.
        
        Args:
            work_item_types: Optional filter by work item types
            
        Returns:
            Flow metrics
        """
        # Filter items if needed
        items = self.work_items
        if work_item_types:
            items = [i for i in items if i.work_item_type in work_item_types]
        
        # Calculate cycle time distribution
        cycle_times = [
            item.cycle_time_days 
            for item in items 
            if item.cycle_time_days is not None
        ]
        
        cycle_time_dist = {
            'p25': np.percentile(cycle_times, 25) if cycle_times else 0,
            'p50': np.percentile(cycle_times, 50) if cycle_times else 0,
            'p75': np.percentile(cycle_times, 75) if cycle_times else 0,
            'p90': np.percentile(cycle_times, 90) if cycle_times else 0,
            'p95': np.percentile(cycle_times, 95) if cycle_times else 0,
            'mean': np.mean(cycle_times) if cycle_times else 0,
            'std': np.std(cycle_times) if cycle_times else 0
        }
        
        # Calculate lead time distribution
        lead_times = [
            item.lead_time_days 
            for item in items 
            if item.lead_time_days is not None
        ]
        
        lead_time_dist = {
            'p25': np.percentile(lead_times, 25) if lead_times else 0,
            'p50': np.percentile(lead_times, 50) if lead_times else 0,
            'p75': np.percentile(lead_times, 75) if lead_times else 0,
            'p90': np.percentile(lead_times, 90) if lead_times else 0,
            'p95': np.percentile(lead_times, 95) if lead_times else 0,
            'mean': np.mean(lead_times) if lead_times else 0,
            'std': np.std(lead_times) if lead_times else 0
        }
        
        # Calculate flow efficiency
        total_cycle_time = sum(cycle_times)
        total_lead_time = sum(lead_times)
        flow_efficiency = (
            (total_cycle_time / total_lead_time * 100) 
            if total_lead_time > 0 else 0
        )
        
        # Calculate wait vs touch time
        wait_time = total_lead_time - total_cycle_time if total_lead_time > total_cycle_time else 0
        wait_percentage = (wait_time / total_lead_time * 100) if total_lead_time > 0 else 0
        touch_percentage = 100 - wait_percentage
        
        # Calculate blocked time percentage
        blocked_time = sum(item.blocked_days or 0 for item in items)
        blocked_percentage = (
            (blocked_time / total_cycle_time * 100) 
            if total_cycle_time > 0 else 0
        )
        
        # Calculate rework (items that went from closed back to active)
        # This is simplified - would need state history for accurate calculation
        rework_items = len([
            item for item in items 
            if item.state == WorkItemState.ACTIVE and item.closed_date
        ])
        rework_percentage = (
            (rework_items / len(items) * 100) 
            if items else 0
        )
        
        return FlowMetrics(
            cycle_time_distribution=cycle_time_dist,
            lead_time_distribution=lead_time_dist,
            flow_efficiency=flow_efficiency,
            wait_time_percentage=wait_percentage,
            touch_time_percentage=touch_percentage,
            blocked_time_percentage=blocked_percentage,
            rework_percentage=rework_percentage
        )
    
    def calculate_predictability_metrics(self) -> Dict[str, Any]:
        """Calculate predictability metrics across PIs."""
        pi_metrics = self.calculate_pi_metrics()
        
        if not pi_metrics:
            return {}
        
        # Extract velocity and predictability trends
        velocities = [pi.velocity for pi in pi_metrics]
        predictabilities = [pi.predictability for pi in pi_metrics]
        completion_rates = [pi.completion_rate for pi in pi_metrics]
        
        # Calculate trends
        velocity_trend = self._calculate_trend(velocities)
        predictability_trend = self._calculate_trend(predictabilities)
        
        # Calculate stability metrics
        velocity_cv = (
            np.std(velocities) / np.mean(velocities) 
            if np.mean(velocities) > 0 else 0
        )
        
        # Monte Carlo simulation for future PI
        monte_carlo_forecast = self._monte_carlo_velocity_forecast(velocities)
        
        return {
            'average_velocity': np.mean(velocities),
            'velocity_trend': velocity_trend,
            'velocity_stability': 1 - velocity_cv,  # Higher is more stable
            'average_predictability': np.mean(predictabilities),
            'predictability_trend': predictability_trend,
            'average_completion_rate': np.mean(completion_rates),
            'monte_carlo_forecast': monte_carlo_forecast,
            'confidence_intervals': {
                'velocity_p10': np.percentile(velocities, 10),
                'velocity_p50': np.percentile(velocities, 50),
                'velocity_p90': np.percentile(velocities, 90)
            }
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear regression
        x = np.arange(len(values))
        coefficients = np.polyfit(x, values, 1)
        slope = coefficients[0]
        
        # Determine trend based on slope relative to mean
        mean_value = np.mean(values)
        if mean_value == 0:
            return "stable"
        
        relative_slope = slope / mean_value
        
        if relative_slope > 0.1:
            return "increasing"
        elif relative_slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _monte_carlo_velocity_forecast(
        self, 
        historical_velocities: List[float],
        simulations: int = 1000
    ) -> Dict[str, float]:
        """Forecast next PI velocity using Monte Carlo simulation."""
        if not historical_velocities:
            return {}
        
        # Generate simulations based on historical distribution
        mean_velocity = np.mean(historical_velocities)
        std_velocity = np.std(historical_velocities)
        
        if std_velocity == 0:
            # No variation, return deterministic forecast
            return {
                'p10': mean_velocity,
                'p50': mean_velocity,
                'p90': mean_velocity,
                'mean': mean_velocity
            }
        
        # Run simulations
        simulated_velocities = np.random.normal(
            mean_velocity, 
            std_velocity, 
            simulations
        )
        
        # Ensure non-negative
        simulated_velocities = np.maximum(simulated_velocities, 0)
        
        return {
            'p10': np.percentile(simulated_velocities, 10),
            'p50': np.percentile(simulated_velocities, 50),
            'p90': np.percentile(simulated_velocities, 90),
            'mean': np.mean(simulated_velocities),
            'std': np.std(simulated_velocities)
        }
    
    def identify_bottlenecks(self) -> Dict[str, Any]:
        """Identify process bottlenecks and improvement opportunities."""
        bottlenecks = {
            'state_transitions': {},
            'blocked_items': [],
            'long_cycle_time': [],
            'team_imbalances': {},
            'work_type_issues': {}
        }
        
        # Analyze state transitions
        state_counts = defaultdict(int)
        for item in self.work_items:
            state_counts[item.state] += 1
        
        total_items = len(self.work_items)
        for state, count in state_counts.items():
            percentage = (count / total_items * 100) if total_items > 0 else 0
            if percentage > 20 and state not in [WorkItemState.CLOSED, WorkItemState.NEW]:
                bottlenecks['state_transitions'][state] = {
                    'count': count,
                    'percentage': percentage,
                    'severity': 'high' if percentage > 30 else 'medium'
                }
        
        # Find blocked items
        blocked_threshold = 5  # days
        for item in self.work_items:
            if item.blocked_days and item.blocked_days > blocked_threshold:
                bottlenecks['blocked_items'].append({
                    'work_item_id': item.work_item_id,
                    'title': item.title,
                    'blocked_days': item.blocked_days,
                    'team': item.area_path
                })
        
        # Find items with long cycle times
        cycle_times = [
            item.cycle_time_days 
            for item in self.work_items 
            if item.cycle_time_days is not None
        ]
        if cycle_times:
            p90_cycle_time = np.percentile(cycle_times, 90)
            for item in self.work_items:
                if item.cycle_time_days and item.cycle_time_days > p90_cycle_time:
                    bottlenecks['long_cycle_time'].append({
                        'work_item_id': item.work_item_id,
                        'title': item.title,
                        'cycle_time_days': item.cycle_time_days,
                        'type': item.work_item_type.value
                    })
        
        # Analyze team imbalances
        team_metrics = self.calculate_team_metrics()
        avg_velocity = np.mean([tm.average_velocity for tm in team_metrics.values()])
        
        for team_name, metrics in team_metrics.items():
            velocity_ratio = metrics.average_velocity / avg_velocity if avg_velocity > 0 else 1
            
            if velocity_ratio < 0.5 or velocity_ratio > 2.0:
                bottlenecks['team_imbalances'][team_name] = {
                    'velocity_ratio': velocity_ratio,
                    'average_velocity': metrics.average_velocity,
                    'issue': 'underutilized' if velocity_ratio < 0.5 else 'overloaded'
                }
        
        # Analyze work type distribution issues
        type_counts = defaultdict(int)
        type_cycle_times = defaultdict(list)
        
        for item in self.work_items:
            type_counts[item.work_item_type] += 1
            if item.cycle_time_days:
                type_cycle_times[item.work_item_type].append(item.cycle_time_days)
        
        for work_type, cycle_times in type_cycle_times.items():
            if cycle_times:
                avg_cycle_time = np.mean(cycle_times)
                if work_type == WorkItemType.USER_STORY and avg_cycle_time > 10:
                    bottlenecks['work_type_issues'][work_type.value] = {
                        'average_cycle_time': avg_cycle_time,
                        'count': type_counts[work_type],
                        'issue': 'stories_too_large'
                    }
        
        return bottlenecks
    
    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate actionable insights from metrics."""
        insights = []
        
        # Analyze predictability
        predictability = self.calculate_predictability_metrics()
        if predictability.get('average_predictability', 0) < 80:
            insights.append({
                'type': 'predictability',
                'severity': 'high',
                'title': 'Low PI Predictability',
                'description': f"Average predictability is {predictability.get('average_predictability', 0):.1f}%, below target of 80%",
                'recommendation': 'Review estimation practices and reduce scope volatility'
            })
        
        # Analyze bottlenecks
        bottlenecks = self.identify_bottlenecks()
        if bottlenecks['blocked_items']:
            insights.append({
                'type': 'bottleneck',
                'severity': 'high',
                'title': f"{len(bottlenecks['blocked_items'])} Items Blocked",
                'description': f"Items blocked for more than 5 days affecting delivery",
                'recommendation': 'Escalate blockers and improve dependency management'
            })
        
        # Analyze team performance
        team_metrics = self.calculate_team_metrics()
        for team_name, metrics in team_metrics.items():
            if metrics.velocity_stability > 0.3:  # High variability
                insights.append({
                    'type': 'team_performance',
                    'severity': 'medium',
                    'title': f"{team_name} Velocity Unstable",
                    'description': f"Velocity varies by {metrics.velocity_stability*100:.0f}% between PIs",
                    'recommendation': 'Stabilize team composition and improve estimation'
                })
        
        # Analyze flow efficiency
        flow_metrics = self.calculate_flow_metrics()
        if flow_metrics.flow_efficiency < 15:
            insights.append({
                'type': 'flow_efficiency',
                'severity': 'high',
                'title': 'Poor Flow Efficiency',
                'description': f"Only {flow_metrics.flow_efficiency:.1f}% of time is value-adding",
                'recommendation': 'Reduce wait times and improve work item flow'
            })
        
        return insights
    
    def export_metrics_summary(self) -> Dict[str, Any]:
        """Export comprehensive metrics summary."""
        return {
            'summary': {
                'total_work_items': len(self.work_items),
                'completed_items': len([i for i in self.work_items if i.is_completed()]),
                'active_items': len([i for i in self.work_items if i.is_active()]),
                'cancelled_items': len([i for i in self.work_items if i.is_cancelled()])
            },
            'pi_metrics': [
                {
                    'pi_number': pi.pi_number,
                    'velocity': pi.velocity,
                    'predictability': pi.predictability,
                    'completion_rate': pi.completion_rate
                }
                for pi in self.calculate_pi_metrics()
            ],
            'team_performance': {
                team: {
                    'average_velocity': metrics.average_velocity,
                    'velocity_stability': metrics.velocity_stability,
                    'cycle_time_p50': metrics.cycle_time_p50,
                    'throughput': metrics.throughput
                }
                for team, metrics in self.calculate_team_metrics().items()
            },
            'flow_metrics': {
                'flow_efficiency': self.calculate_flow_metrics().flow_efficiency,
                'cycle_time_p50': self.calculate_flow_metrics().cycle_time_distribution['p50'],
                'lead_time_p50': self.calculate_flow_metrics().lead_time_distribution['p50']
            },
            'predictability': self.calculate_predictability_metrics(),
            'insights': self.generate_insights()
        }