"""Data Analysis and Visualization Recommendation

This module analyzes ML outputs and recommends appropriate visualizations
based on data characteristics and patterns.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DataType(Enum):
    """Types of data for visualization selection."""
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"
    TEMPORAL = "temporal"
    GEOGRAPHICAL = "geographical"
    HIERARCHICAL = "hierarchical"
    TEXT = "text"
    MIXED = "mixed"


class ChartType(Enum):
    """Available chart types."""
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    PIE = "pie"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    NETWORK = "network"
    TABLE = "table"
    KPI_CARD = "kpi"
    WORD_CLOUD = "wordcloud"
    TIMELINE = "timeline"
    FUNNEL = "funnel"
    RADAR = "radar"
    BOX_PLOT = "boxplot"


@dataclass
class ColumnAnalysis:
    """Analysis results for a single column."""
    column_name: str
    data_type: DataType
    unique_values: int
    null_percentage: float
    is_filterable: bool
    filter_type: str  # 'dropdown', 'range', 'multiselect', 'daterange'
    summary_stats: Dict[str, Any]
    value_distribution: Optional[Dict[str, int]] = None


@dataclass
class VisualizationRecommendation:
    """Recommendation for a visualization."""
    chart_type: ChartType
    priority: int  # 1-10, higher is better
    data_columns: List[str]
    title: str
    description: str
    config: Dict[str, Any]
    rationale: str


class DataAnalyzer:
    """Analyzes data to understand its characteristics."""
    
    def __init__(self):
        self.analysis_results: Dict[str, ColumnAnalysis] = {}
        self.data_shape: Optional[Tuple[int, int]] = None
        
    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive analysis of a dataframe."""
        self.data_shape = df.shape
        
        # Analyze each column
        for column in df.columns:
            self.analysis_results[column] = self._analyze_column(df[column], column)
        
        # Analyze relationships
        relationships = self._analyze_relationships(df)
        
        # Detect patterns
        patterns = self._detect_patterns(df)
        
        return {
            'shape': self.data_shape,
            'columns': self.analysis_results,
            'relationships': relationships,
            'patterns': patterns,
            'summary': self._generate_summary()
        }
    
    def _analyze_column(self, series: pd.Series, column_name: str) -> ColumnAnalysis:
        """Analyze a single column."""
        # Determine data type
        data_type = self._infer_data_type(series)
        
        # Calculate statistics
        unique_values = series.nunique()
        null_percentage = (series.isna().sum() / len(series)) * 100
        
        # Determine filterability
        is_filterable = unique_values < 100 or data_type in [
            DataType.CATEGORICAL, DataType.TEMPORAL
        ]
        
        # Determine filter type
        filter_type = self._determine_filter_type(series, data_type, unique_values)
        
        # Summary statistics
        summary_stats = self._calculate_summary_stats(series, data_type)
        
        # Value distribution for categorical data
        value_distribution = None
        if data_type == DataType.CATEGORICAL and unique_values < 50:
            value_distribution = series.value_counts().to_dict()
        
        return ColumnAnalysis(
            column_name=column_name,
            data_type=data_type,
            unique_values=unique_values,
            null_percentage=null_percentage,
            is_filterable=is_filterable,
            filter_type=filter_type,
            summary_stats=summary_stats,
            value_distribution=value_distribution
        )
    
    def _infer_data_type(self, series: pd.Series) -> DataType:
        """Infer the data type of a series."""
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return DataType.TEMPORAL
        
        # Check for numeric
        if pd.api.types.is_numeric_dtype(series):
            return DataType.NUMERICAL
        
        # Check for categorical
        if pd.api.types.is_categorical_dtype(series) or series.dtype == 'object':
            # Check if it's hierarchical (contains separators)
            sample = series.dropna().head(10)
            if any('/' in str(val) or '\\' in str(val) for val in sample):
                return DataType.HIERARCHICAL
            
            # Check for geographical
            geo_keywords = ['country', 'state', 'city', 'region', 'location']
            if any(keyword in series.name.lower() for keyword in geo_keywords):
                return DataType.GEOGRAPHICAL
            
            return DataType.CATEGORICAL
        
        return DataType.MIXED
    
    def _determine_filter_type(
        self, 
        series: pd.Series, 
        data_type: DataType, 
        unique_values: int
    ) -> str:
        """Determine the appropriate filter type."""
        if data_type == DataType.TEMPORAL:
            return 'daterange'
        elif data_type == DataType.NUMERICAL:
            return 'range'
        elif unique_values <= 10:
            return 'dropdown'
        elif unique_values <= 50:
            return 'multiselect'
        else:
            return 'search'
    
    def _calculate_summary_stats(
        self, 
        series: pd.Series, 
        data_type: DataType
    ) -> Dict[str, Any]:
        """Calculate summary statistics based on data type."""
        stats = {}
        
        if data_type == DataType.NUMERICAL:
            stats = {
                'mean': series.mean(),
                'median': series.median(),
                'std': series.std(),
                'min': series.min(),
                'max': series.max(),
                'q1': series.quantile(0.25),
                'q3': series.quantile(0.75)
            }
        elif data_type == DataType.TEMPORAL:
            stats = {
                'min': series.min(),
                'max': series.max(),
                'range_days': (series.max() - series.min()).days if pd.notna(series.min()) else 0
            }
        elif data_type == DataType.CATEGORICAL:
            stats = {
                'mode': series.mode()[0] if len(series.mode()) > 0 else None,
                'unique_count': series.nunique()
            }
        
        return stats
    
    def _analyze_relationships(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze relationships between columns."""
        relationships = {
            'correlations': {},
            'associations': {},
            'hierarchies': []
        }
        
        # Numeric correlations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            high_corr = []
            
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        high_corr.append({
                            'col1': numeric_cols[i],
                            'col2': numeric_cols[j],
                            'correlation': corr_val
                        })
            
            relationships['correlations'] = high_corr
        
        # Detect hierarchies
        for col in df.columns:
            if self.analysis_results[col].data_type == DataType.HIERARCHICAL:
                relationships['hierarchies'].append(col)
        
        return relationships
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect patterns in the data."""
        patterns = {
            'trends': [],
            'anomalies': [],
            'clusters': []
        }
        
        # Detect time-based trends
        time_cols = [col for col in df.columns 
                     if self.analysis_results[col].data_type == DataType.TEMPORAL]
        
        if time_cols:
            # Simple trend detection
            for time_col in time_cols:
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for num_col in numeric_cols:
                    try:
                        # Sort by time and check if values are increasing/decreasing
                        sorted_df = df.sort_values(time_col)
                        values = sorted_df[num_col].values
                        
                        # Simple linear trend check
                        x = np.arange(len(values))
                        if len(values) > 10:
                            coef = np.polyfit(x, values, 1)[0]
                            if abs(coef) > 0.1:
                                patterns['trends'].append({
                                    'time_column': time_col,
                                    'value_column': num_col,
                                    'direction': 'increasing' if coef > 0 else 'decreasing',
                                    'strength': abs(coef)
                                })
                    except:
                        continue
        
        return patterns
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the analysis."""
        return {
            'total_rows': self.data_shape[0],
            'total_columns': self.data_shape[1],
            'data_types': {
                dt.value: sum(1 for col in self.analysis_results.values() 
                            if col.data_type == dt)
                for dt in DataType
            },
            'filterable_columns': [
                col.column_name for col in self.analysis_results.values()
                if col.is_filterable
            ],
            'high_cardinality_columns': [
                col.column_name for col in self.analysis_results.values()
                if col.unique_values > 100
            ]
        }


class VisualizationRecommender:
    """Recommends visualizations based on data analysis."""
    
    def __init__(self):
        # Visualization rules based on data characteristics
        self.visualization_rules = self._initialize_rules()
    
    def _initialize_rules(self) -> List[Dict[str, Any]]:
        """Initialize visualization recommendation rules."""
        return [
            # KPI Cards for single metrics
            {
                'condition': lambda cols: len(cols) == 1 and cols[0].data_type == DataType.NUMERICAL,
                'chart_type': ChartType.KPI_CARD,
                'priority': 9
            },
            # Time series
            {
                'condition': lambda cols: any(c.data_type == DataType.TEMPORAL for c in cols),
                'chart_type': ChartType.LINE,
                'priority': 8
            },
            # Categorical comparisons
            {
                'condition': lambda cols: any(c.data_type == DataType.CATEGORICAL for c in cols),
                'chart_type': ChartType.BAR,
                'priority': 7
            },
            # Correlation scatter
            {
                'condition': lambda cols: len([c for c in cols if c.data_type == DataType.NUMERICAL]) >= 2,
                'chart_type': ChartType.SCATTER,
                'priority': 6
            },
            # Distribution
            {
                'condition': lambda cols: any(c.data_type == DataType.NUMERICAL for c in cols),
                'chart_type': ChartType.BOX_PLOT,
                'priority': 5
            },
            # Hierarchical data
            {
                'condition': lambda cols: any(c.data_type == DataType.HIERARCHICAL for c in cols),
                'chart_type': ChartType.TREEMAP,
                'priority': 8
            },
            # Part-to-whole
            {
                'condition': lambda cols: (
                    any(c.data_type == DataType.CATEGORICAL for c in cols) and
                    any(c.unique_values <= 10 for c in cols)
                ),
                'chart_type': ChartType.PIE,
                'priority': 4
            }
        ]
    
    def recommend_visualizations(
        self, 
        analysis_results: Dict[str, Any],
        ml_outputs: Optional[Dict[str, Any]] = None
    ) -> List[VisualizationRecommendation]:
        """Recommend visualizations based on data analysis."""
        recommendations = []
        columns_analysis = list(analysis_results['columns'].values())
        
        # Apply rules to generate recommendations
        for rule in self.visualization_rules:
            if rule['condition'](columns_analysis):
                recommendations.extend(
                    self._generate_recommendations_for_chart_type(
                        rule['chart_type'],
                        rule['priority'],
                        columns_analysis,
                        analysis_results
                    )
                )
        
        # Add ML-specific visualizations
        if ml_outputs:
            recommendations.extend(self._recommend_ml_visualizations(ml_outputs))
        
        # Sort by priority
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        return recommendations[:12]  # Return top 12 recommendations
    
    def _generate_recommendations_for_chart_type(
        self,
        chart_type: ChartType,
        base_priority: int,
        columns: List[ColumnAnalysis],
        analysis_results: Dict[str, Any]
    ) -> List[VisualizationRecommendation]:
        """Generate specific recommendations for a chart type."""
        recommendations = []
        
        if chart_type == ChartType.LINE:
            # Find time series combinations
            time_cols = [c for c in columns if c.data_type == DataType.TEMPORAL]
            numeric_cols = [c for c in columns if c.data_type == DataType.NUMERICAL]
            
            for time_col in time_cols[:1]:  # Use first time column
                for num_col in numeric_cols[:3]:  # Top 3 numeric columns
                    recommendations.append(VisualizationRecommendation(
                        chart_type=ChartType.LINE,
                        priority=base_priority,
                        data_columns=[time_col.column_name, num_col.column_name],
                        title=f"{num_col.column_name} Over Time",
                        description=f"Trend of {num_col.column_name} across {time_col.column_name}",
                        config={
                            'x': time_col.column_name,
                            'y': num_col.column_name,
                            'smooth': True
                        },
                        rationale="Time series data is best visualized with line charts"
                    ))
        
        elif chart_type == ChartType.BAR:
            # Find categorical-numeric combinations
            cat_cols = [c for c in columns if c.data_type == DataType.CATEGORICAL and c.unique_values <= 20]
            numeric_cols = [c for c in columns if c.data_type == DataType.NUMERICAL]
            
            for cat_col in cat_cols[:2]:
                for num_col in numeric_cols[:2]:
                    recommendations.append(VisualizationRecommendation(
                        chart_type=ChartType.BAR,
                        priority=base_priority,
                        data_columns=[cat_col.column_name, num_col.column_name],
                        title=f"{num_col.column_name} by {cat_col.column_name}",
                        description=f"Comparison of {num_col.column_name} across different {cat_col.column_name}",
                        config={
                            'x': cat_col.column_name,
                            'y': num_col.column_name,
                            'orientation': 'vertical'
                        },
                        rationale="Bar charts effectively compare values across categories"
                    ))
        
        elif chart_type == ChartType.SCATTER:
            # Find numeric pairs with high correlation
            numeric_cols = [c for c in columns if c.data_type == DataType.NUMERICAL]
            
            if 'correlations' in analysis_results['relationships']:
                for corr in analysis_results['relationships']['correlations'][:2]:
                    recommendations.append(VisualizationRecommendation(
                        chart_type=ChartType.SCATTER,
                        priority=base_priority + 1,  # Higher priority for correlated data
                        data_columns=[corr['col1'], corr['col2']],
                        title=f"Correlation: {corr['col1']} vs {corr['col2']}",
                        description=f"Scatter plot showing relationship (r={corr['correlation']:.2f})",
                        config={
                            'x': corr['col1'],
                            'y': corr['col2'],
                            'showTrendLine': True
                        },
                        rationale=f"High correlation detected: {corr['correlation']:.2f}"
                    ))
        
        elif chart_type == ChartType.KPI_CARD:
            # Create KPI cards for important numeric columns
            numeric_cols = [c for c in columns if c.data_type == DataType.NUMERICAL]
            
            for num_col in numeric_cols[:4]:
                recommendations.append(VisualizationRecommendation(
                    chart_type=ChartType.KPI_CARD,
                    priority=base_priority,
                    data_columns=[num_col.column_name],
                    title=num_col.column_name,
                    description=f"Key metric: {num_col.column_name}",
                    config={
                        'metric': num_col.column_name,
                        'aggregation': 'sum',
                        'format': 'number',
                        'showTrend': True
                    },
                    rationale="KPI cards highlight important single metrics"
                ))
        
        return recommendations
    
    def _recommend_ml_visualizations(
        self, 
        ml_outputs: Dict[str, Any]
    ) -> List[VisualizationRecommendation]:
        """Recommend visualizations specific to ML outputs."""
        recommendations = []
        
        # Feature importance
        if 'feature_importance' in ml_outputs:
            recommendations.append(VisualizationRecommendation(
                chart_type=ChartType.BAR,
                priority=10,
                data_columns=['feature', 'importance'],
                title="Feature Importance",
                description="ML model feature importance scores",
                config={
                    'x': 'importance',
                    'y': 'feature',
                    'orientation': 'horizontal',
                    'sorted': True
                },
                rationale="Feature importance helps understand model decisions"
            ))
        
        # Confusion matrix
        if 'confusion_matrix' in ml_outputs:
            recommendations.append(VisualizationRecommendation(
                chart_type=ChartType.HEATMAP,
                priority=9,
                data_columns=['actual', 'predicted', 'count'],
                title="Confusion Matrix",
                description="Model prediction accuracy breakdown",
                config={
                    'x': 'predicted',
                    'y': 'actual',
                    'value': 'count',
                    'colorScale': 'blues'
                },
                rationale="Confusion matrix shows model performance patterns"
            ))
        
        # Model performance over time
        if 'performance_history' in ml_outputs:
            recommendations.append(VisualizationRecommendation(
                chart_type=ChartType.LINE,
                priority=8,
                data_columns=['iteration', 'score'],
                title="Model Performance History",
                description="Model performance improvement over iterations",
                config={
                    'x': 'iteration',
                    'y': 'score',
                    'smooth': False,
                    'showPoints': True
                },
                rationale="Track model improvement through optimization"
            ))
        
        return recommendations