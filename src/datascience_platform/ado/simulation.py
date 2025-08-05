"""ADO Data Simulation Engine

This module generates realistic Azure DevOps work item data for testing
and demonstration purposes without requiring real data.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from faker import Faker
import numpy as np
import pandas as pd

from .models import (
    ADOWorkItem, Epic, PIO, Feature, UserStory,
    WorkItemState, WorkItemType, WorkItemHierarchy, TeamMetrics
)

fake = Faker()


class ADODataSimulator:
    """Generate realistic ADO work item hierarchies and data."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize simulator with optional seed for reproducibility.
        
        Args:
            seed: Random seed for reproducible data generation
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            Faker.seed(seed)
        
        self.fake = Faker()
        
        # Configuration for realistic distributions
        self.team_names = [
            "Platform Team", "Mobile Team", "Data Team", 
            "Frontend Team", "Backend Team", "DevOps Team",
            "Quality Team", "Architecture Team"
        ]
        
        self.strategy_pillars = [
            "Customer Experience", "Operational Excellence",
            "Innovation", "Security & Compliance", "Growth"
        ]
        
        self.feature_categories = [
            "User Management", "Analytics", "Integration",
            "Performance", "Security", "UI/UX", "API",
            "Infrastructure", "Data Processing", "Mobile"
        ]
        
        self.story_templates = [
            "As a {user}, I want to {action} so that {benefit}",
            "Enable {feature} for {user_type} users",
            "Implement {component} to support {capability}",
            "Optimize {process} to improve {metric}",
            "Add {functionality} to {module}",
            "Fix {issue} in {component}",
            "Refactor {module} for better {quality}"
        ]
        
        self.work_item_counter = 1000  # Starting ID
    
    def generate_multi_pi_data(
        self,
        num_pis: int = 4,
        num_epics: int = 10,
        features_per_epic: Tuple[int, int] = (2, 5),
        stories_per_feature: Tuple[int, int] = (3, 8),
        pi_duration_weeks: int = 10,
        completion_rate: float = 0.75,
        cancellation_rate: float = 0.10,
        start_date: Optional[datetime] = None
    ) -> List[ADOWorkItem]:
        """Generate work items across multiple PIs.
        
        Args:
            num_pis: Number of PIs to generate
            num_epics: Total number of epics
            features_per_epic: Range of features per epic
            stories_per_feature: Range of stories per feature
            pi_duration_weeks: Duration of each PI
            completion_rate: Percentage of items completed
            cancellation_rate: Percentage of items cancelled
            start_date: Start date for generation
            
        Returns:
            List of all generated work items
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(weeks=pi_duration_weeks * num_pis)
        
        all_items = []
        hierarchy = WorkItemHierarchy()
        
        # Distribute epics across PIs
        epics_per_pi = max(1, num_epics // num_pis)
        
        for pi_num in range(1, num_pis + 1):
            pi_start = start_date + timedelta(weeks=(pi_num - 1) * pi_duration_weeks)
            pi_end = pi_start + timedelta(weeks=pi_duration_weeks)
            
            # Generate epics for this PI
            num_epics_this_pi = epics_per_pi if pi_num < num_pis else num_epics - (epics_per_pi * (num_pis - 1))
            
            for epic_idx in range(num_epics_this_pi):
                # Create epic
                epic = self._generate_epic(pi_num, pi_start, pi_end)
                all_items.append(epic)
                hierarchy.add_work_item(epic)
                
                # Generate PIOs for epic
                num_pios = random.randint(1, 3)
                for pio_idx in range(num_pios):
                    pio = self._generate_pio(epic, pi_num, pi_start, pi_end)
                    all_items.append(pio)
                    hierarchy.add_work_item(pio)
                    
                    # Some features under PIO
                    num_features_pio = random.randint(1, 2)
                    for _ in range(num_features_pio):
                        feature = self._generate_feature(pio, pi_num, pi_start, pi_end)
                        all_items.append(feature)
                        hierarchy.add_work_item(feature)
                        
                        # Generate stories
                        num_stories = random.randint(*stories_per_feature)
                        for _ in range(num_stories):
                            story = self._generate_user_story(feature, pi_num, pi_start, pi_end)
                            all_items.append(story)
                            hierarchy.add_work_item(story)
                
                # Generate features directly under epic
                num_features = random.randint(*features_per_epic)
                for feat_idx in range(num_features):
                    feature = self._generate_feature(epic, pi_num, pi_start, pi_end)
                    all_items.append(feature)
                    hierarchy.add_work_item(feature)
                    
                    # Generate stories for feature
                    num_stories = random.randint(*stories_per_feature)
                    for story_idx in range(num_stories):
                        story = self._generate_user_story(feature, pi_num, pi_start, pi_end)
                        all_items.append(story)
                        hierarchy.add_work_item(story)
        
        # Apply completion and cancellation rates
        self._apply_realistic_states(all_items, completion_rate, cancellation_rate, start_date)
        
        # Calculate rollup metrics
        self._calculate_rollup_metrics(all_items, hierarchy)
        
        return all_items
    
    def _generate_epic(
        self, 
        pi_num: int, 
        pi_start: datetime, 
        pi_end: datetime
    ) -> Epic:
        """Generate a realistic epic."""
        epic_id = self._get_next_id()
        
        category = random.choice(self.feature_categories)
        pillar = random.choice(self.strategy_pillars)
        
        epic = Epic(
            work_item_id=epic_id,
            title=f"[PI{pi_num}] {category} Enhancement Initiative",
            state=WorkItemState.ACTIVE,
            business_value_raw=random.randint(50, 100),
            complexity_score=random.randint(60, 95),
            risk_score=random.randint(20, 80),
            created_date=pi_start - timedelta(days=random.randint(14, 30)),
            target_date=pi_end,
            pi_number=pi_num,
            strategy_pillar=pillar,
            area_path=random.choice(self.team_names[:3]),  # Epics owned by senior teams
            assigned_to=self.fake.name(),
            business_case=f"Improve {category.lower()} capabilities to support {pillar}",
            success_criteria=f"Achieve 20% improvement in {category.lower()} metrics",
            target_market_size=random.randint(10000, 1000000),
            revenue_impact=random.randint(100000, 5000000),
            tags=[pillar, category, f"PI{pi_num}"]
        )
        
        # Normalize business value
        epic.business_value_normalized = epic.business_value_raw / 100.0
        
        return epic
    
    def _generate_pio(
        self, 
        parent: ADOWorkItem,
        pi_num: int, 
        pi_start: datetime, 
        pi_end: datetime
    ) -> PIO:
        """Generate a Program Increment Objective."""
        pio_id = self._get_next_id()
        
        confidence = random.randint(60, 95)
        is_stretch = confidence < 70
        
        pio = PIO(
            work_item_id=pio_id,
            parent_id=parent.work_item_id,
            title=f"PIO: {parent.title.replace('[PI' + str(pi_num) + '] ', '')} - Q{random.randint(1,4)} Objective",
            state=WorkItemState.ACTIVE,
            business_value_raw=parent.business_value_raw * random.uniform(0.2, 0.4),
            complexity_score=random.randint(40, 80),
            risk_score=parent.risk_score * random.uniform(0.8, 1.2),
            created_date=parent.created_date + timedelta(days=random.randint(1, 7)),
            target_date=pi_end - timedelta(days=random.randint(0, 14)),
            pi_number=pi_num,
            strategy_pillar=parent.strategy_pillar,
            area_path=parent.area_path,
            assigned_to=parent.assigned_to,
            pi_confidence=confidence,
            stretch_goal=is_stretch,
            committed=not is_stretch,
            tags=parent.tags + ["PIO", f"Confidence-{confidence}"]
        )
        
        pio.business_value_normalized = pio.business_value_raw / 100.0
        
        return pio
    
    def _generate_feature(
        self,
        parent: ADOWorkItem,
        pi_num: int,
        pi_start: datetime,
        pi_end: datetime
    ) -> Feature:
        """Generate a realistic feature."""
        feature_id = self._get_next_id()
        
        category = random.choice(self.feature_categories)
        enabler_types = ["Technical", "Infrastructure", "Architecture", "Exploration", None]
        enabler_type = random.choice(enabler_types)
        
        feature = Feature(
            work_item_id=feature_id,
            parent_id=parent.work_item_id,
            title=f"{category} - {self.fake.bs().title()}",
            state=WorkItemState.NEW,
            business_value_raw=parent.business_value_raw * random.uniform(0.1, 0.3),
            story_points=random.randint(8, 40),
            complexity_score=random.randint(30, 70),
            risk_score=random.randint(10, 60),
            created_date=parent.created_date + timedelta(days=random.randint(5, 15)),
            target_date=pi_end - timedelta(days=random.randint(7, 21)),
            pi_number=pi_num,
            strategy_pillar=parent.strategy_pillar,
            area_path=random.choice(self.team_names),
            assigned_to=self.fake.name(),
            mvp_scope=f"Core {category.lower()} functionality with basic {self.fake.word()} support",
            enabler_type=enabler_type,
            architectural_impact="Low" if enabler_type is None else "High",
            feature_flag=f"feature_{category.lower()}_{feature_id}" if random.random() > 0.5 else None,
            tags=parent.tags + [category, "Feature"]
        )
        
        feature.business_value_normalized = feature.business_value_raw / 100.0
        
        return feature
    
    def _generate_user_story(
        self,
        parent: Feature,
        pi_num: int,
        pi_start: datetime,
        pi_end: datetime
    ) -> UserStory:
        """Generate a realistic user story."""
        story_id = self._get_next_id()
        
        # Generate story from template
        template = random.choice(self.story_templates)
        user_types = ["user", "admin", "developer", "customer", "analyst", "manager"]
        actions = ["access", "create", "update", "view", "export", "configure", "manage"]
        benefits = ["efficiency", "visibility", "control", "automation", "insights", "compliance"]
        
        if "{user}" in template:
            title = template.format(
                user=random.choice(user_types),
                action=self.fake.word() + " " + random.choice(actions),
                benefit="improve " + random.choice(benefits)
            )
        else:
            # Use faker to fill in placeholders
            title = template
            replacements = {
                "{feature}": self.fake.word(),
                "{user_type}": random.choice(user_types),
                "{component}": self.fake.word(),
                "{capability}": self.fake.bs(),
                "{process}": self.fake.word() + " process",
                "{metric}": random.choice(["performance", "accuracy", "speed", "quality"]),
                "{functionality}": self.fake.word() + " feature",
                "{module}": parent.title.split()[0],
                "{issue}": self.fake.word() + " error",
                "{quality}": random.choice(["performance", "maintainability", "scalability"])
            }
            for placeholder, value in replacements.items():
                title = title.replace(placeholder, value)
        
        story = UserStory(
            work_item_id=story_id,
            parent_id=parent.work_item_id,
            title=title,
            state=WorkItemState.NEW,
            business_value_raw=parent.business_value_raw * random.uniform(0.05, 0.2),
            story_points=random.choice([1, 2, 3, 5, 8, 13]),
            complexity_score=random.randint(10, 50),
            risk_score=random.randint(5, 40),
            created_date=parent.created_date + timedelta(days=random.randint(3, 10)),
            target_date=parent.target_date - timedelta(days=random.randint(0, 7)),
            iteration_path=f"PI{pi_num}/Sprint{random.randint(1, 5)}",
            pi_number=pi_num,
            strategy_pillar=parent.strategy_pillar,
            area_path=parent.area_path,
            assigned_to=self.fake.name() if random.random() > 0.2 else None,
            acceptance_criteria=self._generate_acceptance_criteria(),
            story_type="User Story" if "As a" in title else "Technical Story",
            test_cases_count=random.randint(2, 10),
            test_automation_percentage=random.randint(0, 100),
            tags=parent.tags + ["Story", f"Sprint{random.randint(1, 5)}"]
        )
        
        story.business_value_normalized = story.business_value_raw / 100.0
        
        # Add team metrics
        story.team_metrics = TeamMetrics(
            team_name=story.area_path,
            velocity=random.randint(20, 60),
            capacity=random.randint(30, 70),
            historical_completion_rate=random.uniform(0.6, 0.95)
        )
        
        return story
    
    def _generate_acceptance_criteria(self) -> str:
        """Generate realistic acceptance criteria."""
        criteria = [
            "Given: User is authenticated\nWhen: Action is performed\nThen: Expected result occurs",
            "- Functionality works as specified\n- Unit tests pass\n- Code review completed",
            "- Feature is accessible to target users\n- Performance meets SLA\n- Security scan passes",
            "- API returns correct response\n- Error handling implemented\n- Documentation updated"
        ]
        return random.choice(criteria)
    
    def _apply_realistic_states(
        self,
        items: List[ADOWorkItem],
        completion_rate: float,
        cancellation_rate: float,
        start_date: datetime
    ):
        """Apply realistic state transitions to work items."""
        now = datetime.now()
        
        for item in items:
            # Skip if item is in future
            if item.created_date > now:
                continue
            
            # Determine final state based on rates
            rand = random.random()
            
            if rand < completion_rate:
                # Complete the item
                item.state = WorkItemState.CLOSED
                
                # Set state transition dates
                days_to_activate = random.randint(1, 7)
                days_to_resolve = random.randint(
                    5 if isinstance(item, UserStory) else 20,
                    20 if isinstance(item, UserStory) else 60
                )
                days_to_close = random.randint(1, 3)
                
                item.activated_date = item.created_date + timedelta(days=days_to_activate)
                item.resolved_date = item.activated_date + timedelta(days=days_to_resolve)
                item.closed_date = item.resolved_date + timedelta(days=days_to_close)
                
                # Ensure dates don't exceed current date
                if item.closed_date > now:
                    item.state = WorkItemState.ACTIVE
                    item.resolved_date = None
                    item.closed_date = None
                
                # Calculate metrics
                if item.activated_date and item.resolved_date:
                    item.cycle_time_days = (item.resolved_date - item.activated_date).days
                if item.created_date and item.resolved_date:
                    item.lead_time_days = (item.resolved_date - item.created_date).days
                
                # Add some blocked time
                if random.random() < 0.3:  # 30% chance of being blocked
                    item.blocked_days = random.randint(1, 5)
                    
            elif rand < completion_rate + cancellation_rate:
                # Cancel the item
                item.state = random.choice([
                    WorkItemState.CANCELLED,
                    WorkItemState.DEFERRED
                ])
                
                # Set cancellation date
                days_to_cancel = random.randint(10, 30)
                cancel_date = item.created_date + timedelta(days=days_to_cancel)
                if cancel_date <= now:
                    item.closed_date = cancel_date
                    
            else:
                # Item is still active
                if (now - item.created_date).days > 7:
                    item.state = WorkItemState.ACTIVE
                    item.activated_date = item.created_date + timedelta(days=random.randint(1, 7))
                else:
                    item.state = WorkItemState.NEW
    
    def _calculate_rollup_metrics(
        self,
        items: List[ADOWorkItem],
        hierarchy: WorkItemHierarchy
    ):
        """Calculate roll-up metrics for parent items."""
        # Calculate from bottom up (stories -> features -> epics)
        for item in items:
            if isinstance(item, (Epic, PIO, Feature)):
                rollup = hierarchy.calculate_rollup_metrics(item.work_item_id)
                
                # Only Epic has these fields
                if isinstance(item, Epic):
                    item.total_story_points = rollup['total_story_points']
                    item.completion_percentage = rollup['completion_percentage']
                
                # All parent types can have updated risk/complexity
                if rollup['average_risk_score'] is not None:
                    item.risk_score = rollup['average_risk_score']
                if rollup['average_complexity_score'] is not None:
                    item.complexity_score = rollup['average_complexity_score']
    
    def _get_next_id(self) -> int:
        """Get next work item ID."""
        self.work_item_counter += 1
        return self.work_item_counter
    
    def generate_sample_scenarios(self) -> Dict[str, List[ADOWorkItem]]:
        """Generate various sample scenarios for testing."""
        scenarios = {}
        
        # Scenario 1: High performing team
        Faker.seed(42)
        scenarios['high_performing'] = self.generate_multi_pi_data(
            num_pis=4,
            num_epics=8,
            completion_rate=0.90,
            cancellation_rate=0.05
        )
        
        # Scenario 2: Struggling team
        Faker.seed(43)
        scenarios['struggling'] = self.generate_multi_pi_data(
            num_pis=4,
            num_epics=12,
            completion_rate=0.55,
            cancellation_rate=0.25
        )
        
        # Scenario 3: Growing team
        Faker.seed(44)
        scenarios['growing'] = self.generate_multi_pi_data(
            num_pis=6,
            num_epics=15,
            completion_rate=0.70,
            cancellation_rate=0.15
        )
        
        return scenarios
    
    def export_to_csv_format(
        self,
        items: List[ADOWorkItem],
        include_metrics: bool = True
    ) -> pd.DataFrame:
        """Export work items to CSV-compatible format.
        
        Args:
            items: List of work items to export
            include_metrics: Whether to include calculated metrics
            
        Returns:
            DataFrame ready for CSV export
        """
        import pandas as pd
        
        data = []
        for item in items:
            row = {
                'WorkItemId': item.work_item_id,
                'Title': item.title,
                'WorkItemType': item.work_item_type.value,
                'State': item.state.value,
                'ParentId': item.parent_id,
                'BusinessValue': item.business_value_raw,
                'BusinessValueNormalized': item.business_value_normalized,
                'StoryPoints': item.story_points,
                'EffortHours': item.effort_hours,
                'ComplexityScore': item.complexity_score,
                'RiskScore': item.risk_score,
                'CreatedDate': item.created_date,
                'ActivatedDate': item.activated_date,
                'ResolvedDate': item.resolved_date,
                'ClosedDate': item.closed_date,
                'TargetDate': item.target_date,
                'IterationPath': item.iteration_path,
                'AreaPath': item.area_path,
                'AssignedTo': item.assigned_to,
                'PINumber': item.pi_number,
                'StrategyPillar': item.strategy_pillar,
                'Tags': ';'.join(item.tags) if item.tags else ''
            }
            
            if include_metrics:
                row.update({
                    'CycleTimeDays': item.cycle_time_days,
                    'LeadTimeDays': item.lead_time_days,
                    'BlockedDays': item.blocked_days,
                    'IsCompleted': item.is_completed(),
                    'IsCancelled': item.is_cancelled(),
                    'IsActive': item.is_active()
                })
            
            # Add type-specific fields
            if isinstance(item, Epic):
                row['BusinessCase'] = item.business_case
                row['SuccessCriteria'] = item.success_criteria
                row['RevenueImpact'] = item.revenue_impact
                row['CompletionPercentage'] = item.completion_percentage
            elif isinstance(item, PIO):
                row['PIConfidence'] = item.pi_confidence
                row['StretchGoal'] = item.stretch_goal
                row['Committed'] = item.committed
            elif isinstance(item, Feature):
                row['MVPScope'] = item.mvp_scope
                row['EnablerType'] = item.enabler_type
                row['FeatureFlag'] = item.feature_flag
            elif isinstance(item, UserStory):
                row['AcceptanceCriteria'] = item.acceptance_criteria
                row['StoryType'] = item.story_type
                row['TestCasesCount'] = item.test_cases_count
                row['TestAutomationPercentage'] = item.test_automation_percentage
            
            data.append(row)
        
        return pd.DataFrame(data)