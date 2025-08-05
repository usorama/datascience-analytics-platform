"""Insight Generation Engine

Combines statistical analysis, pattern detection, and ML results
to generate human-readable insights and actionable recommendations.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

from .statistics import StatisticsEngine
from .patterns import PatternDetector
from .automl import AutoMLEngine

logger = logging.getLogger(__name__)


class InsightGenerator:
    """
    Comprehensive insight generation engine that combines all ML analyses
    to produce ranked, human-readable insights and recommendations.
    """
    
    def __init__(self):
        """Initialize the insight generator."""
        self.statistics_engine = StatisticsEngine()
        self.pattern_detector = PatternDetector()
        self.automl_engine = AutoMLEngine()
        self.insights = []
        self.recommendations = []
        self.priority_scores = {}
        
    def generate_comprehensive_insights(self, 
                                      df: pd.DataFrame,
                                      target_column: Optional[str] = None,
                                      time_column: Optional[str] = None,
                                      business_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive insights from the dataset.
        
        Args:
            df: Input DataFrame
            target_column: Target variable for ML analysis
            time_column: Time column for time series analysis
            business_context: Business context for relevant insights
            
        Returns:
            Dictionary containing all insights and recommendations
        """
        try:
            logger.info("Starting comprehensive insight generation")
            
            # Run all analyses
            statistical_results = self.statistics_engine.analyze_dataset(df)
            pattern_results = self.pattern_detector.detect_patterns(df, time_column, target_column)
            
            # ML analysis if target is provided
            ml_results = None
            if target_column and target_column in df.columns:
                try:
                    ml_results = self.automl_engine.train_model(df, target_column, time_limit=60)
                except Exception as e:
                    logger.warning(f"ML analysis failed: {str(e)}")
                    ml_results = None
            
            # Generate insights
            insights = self._generate_insights(
                df, statistical_results, pattern_results, ml_results,
                target_column, time_column, business_context
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                df, statistical_results, pattern_results, ml_results,
                target_column, business_context
            )
            
            # Combine and rank all insights
            all_insights = self._rank_insights(insights, recommendations)
            
            result = {
                'dataset_overview': self._generate_dataset_overview(df, statistical_results),
                'key_insights': all_insights['high_priority'],
                'detailed_insights': all_insights['medium_priority'],
                'additional_insights': all_insights['low_priority'],
                'actionable_recommendations': recommendations,
                'data_quality_assessment': self._assess_data_quality(df, statistical_results, pattern_results),
                'business_insights': self._generate_business_insights(df, statistical_results, pattern_results, business_context),
                'next_steps': self._suggest_next_steps(df, statistical_results, pattern_results, ml_results),
                'metadata': {
                    'analysis_timestamp': datetime.now().isoformat(),
                    'dataset_shape': df.shape,
                    'analyses_performed': {
                        'statistical_analysis': True,
                        'pattern_detection': True,
                        'ml_modeling': ml_results is not None,
                        'time_series_analysis': time_column is not None
                    }
                }
            }
            
            logger.info("Comprehensive insight generation completed")
            return result
            
        except Exception as e:
            logger.error(f"Error in insight generation: {str(e)}")
            raise
    
    def _generate_insights(self, df: pd.DataFrame,
                          statistical_results: Dict[str, Any],
                          pattern_results: Dict[str, Any],
                          ml_results: Optional[Dict[str, Any]],
                          target_column: Optional[str],
                          time_column: Optional[str],
                          business_context: Optional[str]) -> List[Dict[str, Any]]:
        """Generate detailed insights from all analyses."""
        insights = []
        
        # Statistical insights
        insights.extend(self._extract_statistical_insights(df, statistical_results))
        
        # Pattern insights
        insights.extend(self._extract_pattern_insights(pattern_results))
        
        # ML insights
        if ml_results:
            insights.extend(self._extract_ml_insights(ml_results, target_column))
        
        # Time series insights
        if time_column:
            insights.extend(self._extract_time_series_insights(pattern_results, time_column))
        
        # Cross-analysis insights
        insights.extend(self._extract_cross_analysis_insights(
            df, statistical_results, pattern_results, ml_results
        ))
        
        return insights
    
    def _extract_statistical_insights(self, df: pd.DataFrame,
                                    statistical_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract insights from statistical analysis."""
        insights = []
        
        # Data distribution insights
        distributions = statistical_results.get('distributions', {})
        skewed_columns = []
        normal_columns = []
        
        for col, dist_info in distributions.items():
            characteristics = dist_info.get('characteristics', {})
            if characteristics.get('distribution_type', '').startswith('Right Skewed'):
                skewed_columns.append(col)
            elif characteristics.get('is_symmetric', False):
                normal_columns.append(col)
        
        if skewed_columns:
            insights.append({
                'type': 'statistical',
                'category': 'data_distribution',
                'title': 'Skewed Data Distribution Detected',
                'description': f"Columns {', '.join(skewed_columns)} show right-skewed distributions, indicating presence of outliers or rare high values.",
                'impact': 'medium',
                'columns_affected': skewed_columns,
                'priority_score': 7
            })
        
        # Correlation insights
        correlations = statistical_results.get('correlations', {})
        strong_correlations = correlations.get('strong_correlations', [])
        
        if strong_correlations:
            for corr in strong_correlations[:3]:  # Top 3 correlations
                insights.append({
                    'type': 'statistical',
                    'category': 'correlation',
                    'title': f'Strong Correlation: {corr["column1"]} ↔ {corr["column2"]}',
                    'description': f"Strong {corr['strength'].lower()} correlation ({corr['correlation']:.3f}) between {corr['column1']} and {corr['column2']}. This suggests these variables may be measuring similar underlying phenomena.",
                    'impact': 'high' if abs(corr['correlation']) > 0.9 else 'medium',
                    'columns_affected': [corr['column1'], corr['column2']],
                    'priority_score': 8 if abs(corr['correlation']) > 0.9 else 6
                })
        
        # Missing data insights
        missing_data = statistical_results.get('missing_data', {})
        if missing_data.get('missing_percentage', 0) > 10:
            insights.append({
                'type': 'statistical',
                'category': 'data_quality',
                'title': 'Significant Missing Data',
                'description': f"Dataset has {missing_data['missing_percentage']:.1f}% missing values. This may impact analysis reliability and require imputation strategies.",
                'impact': 'high' if missing_data['missing_percentage'] > 25 else 'medium',
                'priority_score': 9 if missing_data['missing_percentage'] > 25 else 7
            })
        
        # Outlier insights
        outliers = statistical_results.get('outliers', {})
        high_outlier_columns = []
        for col, methods in outliers.items():
            iqr_pct = methods.get('iqr', {}).get('percentage', 0)
            if iqr_pct > 15:  # More than 15% outliers
                high_outlier_columns.append((col, iqr_pct))
        
        if high_outlier_columns:
            col_details = [f"{col} ({pct:.1f}%)" for col, pct in high_outlier_columns]
            insights.append({
                'type': 'statistical',
                'category': 'outliers',
                'title': 'High Outlier Concentration',
                'description': f"Columns {', '.join(col_details)} have unusually high outlier percentages. This may indicate data quality issues or natural variance in the process.",
                'impact': 'medium',
                'columns_affected': [col for col, _ in high_outlier_columns],
                'priority_score': 6
            })
        
        return insights
    
    def _extract_pattern_insights(self, pattern_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract insights from pattern detection."""
        insights = []
        
        # Clustering insights
        clustering = pattern_results.get('clustering', {})
        if 'kmeans' in clustering and 'n_clusters' in clustering['kmeans']:
            n_clusters = clustering['kmeans']['n_clusters']
            silhouette = clustering['kmeans'].get('silhouette_score', 0)
            
            if silhouette > 0.5:
                insights.append({
                    'type': 'pattern',
                    'category': 'clustering',
                    'title': f'Clear Data Groupings Identified',
                    'description': f"Data naturally separates into {n_clusters} distinct groups with good separation (silhouette score: {silhouette:.2f}). This suggests underlying structure in your data.",
                    'impact': 'high',
                    'priority_score': 8
                })
            elif silhouette > 0.25:
                insights.append({
                    'type': 'pattern',
                    'category': 'clustering',
                    'title': f'Moderate Data Groupings Present',
                    'description': f"Data shows {n_clusters} clusters with moderate separation (silhouette score: {silhouette:.2f}). Some structure exists but boundaries may be less clear.",
                    'impact': 'medium',
                    'priority_score': 5
                })
        
        # Anomaly insights
        anomalies = pattern_results.get('anomalies', {})
        if 'isolation_forest' in anomalies:
            anomaly_pct = anomalies['isolation_forest'].get('anomaly_percentage', 0)
            if anomaly_pct > 10:
                insights.append({
                    'type': 'pattern',
                    'category': 'anomalies',
                    'title': 'High Anomaly Rate Detected',
                    'description': f"{anomaly_pct:.1f}% of data points are anomalous. This high rate suggests either data quality issues or a naturally variable process.",
                    'impact': 'high',
                    'priority_score': 8
                })
            elif anomaly_pct > 5:
                insights.append({
                    'type': 'pattern',
                    'category': 'anomalies',
                    'title': 'Notable Anomalies Present',
                    'description': f"{anomaly_pct:.1f}% of data points are anomalous. These outliers may represent special cases or errors worth investigating.",
                    'impact': 'medium',
                    'priority_score': 6
                })
        
        # Trend insights
        trends = pattern_results.get('trends', {})
        strong_trending_columns = []
        for col, trend_data in trends.items():
            if isinstance(trend_data, dict) and 'linear_trend' in trend_data:
                linear = trend_data['linear_trend']
                if linear.get('is_significant') and linear.get('trend_strength') in ['Strong', 'Very Strong']:
                    strong_trending_columns.append({
                        'column': col,
                        'direction': linear.get('trend_direction'),
                        'strength': linear.get('trend_strength'),
                        'r_squared': linear.get('r_squared', 0)
                    })
        
        if strong_trending_columns:
            for trend in strong_trending_columns[:3]:  # Top 3 trends
                insights.append({
                    'type': 'pattern',
                    'category': 'trends',
                    'title': f'{trend["strength"]} {trend["direction"].title()} Trend in {trend["column"]}',
                    'description': f"{trend['column']} shows a {trend['strength'].lower()} {trend['direction']} trend (R² = {trend['r_squared']:.3f}). This indicates a consistent pattern over time.",
                    'impact': 'high' if trend['strength'] == 'Very Strong' else 'medium',
                    'columns_affected': [trend['column']],
                    'priority_score': 7 if trend['strength'] == 'Very Strong' else 5
                })
        
        return insights
    
    def _extract_ml_insights(self, ml_results: Dict[str, Any],
                           target_column: str) -> List[Dict[str, Any]]:
        """Extract insights from ML model results."""
        insights = []
        
        # Model performance insights
        evaluation = ml_results.get('evaluation', {})
        task_type = ml_results.get('task_type', 'unknown')
        
        if task_type == 'regression':
            r2 = evaluation.get('r2', 0)
            if r2 > 0.8:
                insights.append({
                    'type': 'ml',
                    'category': 'model_performance',
                    'title': 'High Predictive Accuracy Achieved',
                    'description': f"ML model explains {r2*100:.1f}% of variance in {target_column}. This indicates strong predictable patterns in your target variable.",
                    'impact': 'high',
                    'priority_score': 9
                })
            elif r2 > 0.5:
                insights.append({
                    'type': 'ml',
                    'category': 'model_performance',
                    'title': 'Moderate Predictive Patterns Found',
                    'description': f"ML model explains {r2*100:.1f}% of variance in {target_column}. Some predictable patterns exist, but there's room for improvement.",
                    'impact': 'medium',
                    'priority_score': 6
                })
            else:
                insights.append({
                    'type': 'ml',
                    'category': 'model_performance',
                    'title': 'Limited Predictive Power',
                    'description': f"ML model explains only {r2*100:.1f}% of variance in {target_column}. The target may be driven by factors not present in your dataset.",
                    'impact': 'medium',
                    'priority_score': 5
                })
        
        elif task_type == 'classification':
            accuracy = evaluation.get('accuracy', 0)
            if accuracy > 0.9:
                insights.append({
                    'type': 'ml',
                    'category': 'model_performance',
                    'title': 'Excellent Classification Performance',
                    'description': f"ML model achieves {accuracy*100:.1f}% accuracy in predicting {target_column}. This suggests very strong predictable patterns.",
                    'impact': 'high',
                    'priority_score': 9
                })
            elif accuracy > 0.75:
                insights.append({
                    'type': 'ml',
                    'category': 'model_performance',
                    'title': 'Good Classification Performance',
                    'description': f"ML model achieves {accuracy*100:.1f}% accuracy in predicting {target_column}. This indicates useful predictive patterns.",
                    'impact': 'medium',
                    'priority_score': 7
                })
        
        # Feature importance insights
        feature_importance = ml_results.get('feature_importance', {})
        if feature_importance:
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            top_features = sorted_features[:3]
            
            if len(top_features) > 0:
                top_feature_names = [f[0] for f in top_features]
                top_feature_scores = [f[1] for f in top_features]
                
                # Check if top features dominate
                total_importance = sum(feature_importance.values())
                top_3_importance = sum(top_feature_scores)
                dominance_ratio = top_3_importance / total_importance if total_importance > 0 else 0
                
                if dominance_ratio > 0.7:
                    insights.append({
                        'type': 'ml',
                        'category': 'feature_importance',
                        'title': 'Few Key Drivers Identified',
                        'description': f"Just 3 features ({', '.join(top_feature_names)}) account for {dominance_ratio*100:.1f}% of predictive power. Focus on these key drivers.",
                        'impact': 'high',
                        'columns_affected': top_feature_names,
                        'priority_score': 8
                    })
                else:
                    insights.append({
                        'type': 'ml',
                        'category': 'feature_importance',
                        'title': 'Multiple Contributing Factors',
                        'description': f"Top predictive features are {', '.join(top_feature_names)}, but many features contribute to the prediction.",
                        'impact': 'medium',
                        'columns_affected': top_feature_names,
                        'priority_score': 6
                    })
        
        return insights
    
    def _extract_time_series_insights(self, pattern_results: Dict[str, Any],
                                    time_column: str) -> List[Dict[str, Any]]:
        """Extract insights from time series analysis."""
        insights = []
        
        ts_patterns = pattern_results.get('time_series_patterns', {})
        if not ts_patterns or not isinstance(ts_patterns, dict):
            return insights
        
        # Seasonality insights
        seasonal_columns = []
        for col, patterns in ts_patterns.items():
            if isinstance(patterns, dict) and 'seasonality' in patterns:
                seasonal_patterns = [s for s in patterns['seasonality'] if s.get('is_seasonal')]
                if seasonal_patterns:
                    seasonal_info = {
                        'column': col,
                        'patterns': [f"{s['lag_type']} (correlation: {s['autocorrelation']:.2f})" for s in seasonal_patterns]
                    }
                    seasonal_columns.append(seasonal_info)
        
        if seasonal_columns:
            for seasonal in seasonal_columns[:2]:  # Top 2 seasonal patterns
                insights.append({
                    'type': 'time_series',
                    'category': 'seasonality',
                    'title': f'Seasonal Patterns in {seasonal["column"]}',
                    'description': f"{seasonal['column']} shows seasonal patterns: {', '.join(seasonal['patterns'])}. This indicates recurring cycles that can be leveraged for forecasting.",
                    'impact': 'high',
                    'columns_affected': [seasonal['column']],
                    'priority_score': 8
                })
        
        # Change point insights
        change_point_columns = []
        for col, patterns in ts_patterns.items():
            if isinstance(patterns, dict) and 'change_points' in patterns:
                change_points = patterns['change_points']
                if len(change_points) > 0:
                    change_point_columns.append({
                        'column': col,
                        'change_points': len(change_points),
                        'max_change': max([cp['change_percentage'] for cp in change_points])
                    })
        
        if change_point_columns:
            for cp_info in change_point_columns[:2]:  # Top 2
                insights.append({
                    'type': 'time_series',
                    'category': 'change_points',
                    'title': f'Significant Changes Detected in {cp_info["column"]}',
                    'description': f"{cp_info['column']} shows {cp_info['change_points']} significant change points, with maximum change of {cp_info['max_change']:.1f}%. These may correspond to important events or policy changes.",
                    'impact': 'medium',
                    'columns_affected': [cp_info['column']],
                    'priority_score': 6
                })
        
        return insights
    
    def _extract_cross_analysis_insights(self, df: pd.DataFrame,
                                       statistical_results: Dict[str, Any],
                                       pattern_results: Dict[str, Any],
                                       ml_results: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract insights that require cross-analysis of multiple methods."""
        insights = []
        
        # Data quality cross-check
        quality_issues = []
        
        # Check if high missing data correlates with poor clustering
        missing_data = statistical_results.get('missing_data', {})
        clustering = pattern_results.get('clustering', {})
        
        if (missing_data.get('missing_percentage', 0) > 15 and 
            clustering.get('kmeans', {}).get('silhouette_score', 1) < 0.3):
            quality_issues.append("High missing data may be affecting pattern detection")
        
        # Check if outliers correlate with anomalies
        outliers = statistical_results.get('outliers', {})
        anomalies = pattern_results.get('anomalies', {})
        
        high_outlier_cols = []
        for col, methods in outliers.items():
            if methods.get('iqr', {}).get('percentage', 0) > 10:
                high_outlier_cols.append(col)
        
        anomaly_pct = anomalies.get('isolation_forest', {}).get('anomaly_percentage', 0)
        
        if len(high_outlier_cols) > 0 and anomaly_pct > 8:
            quality_issues.append(f"Consistent outlier detection across methods in {', '.join(high_outlier_cols)}")
        
        if quality_issues:
            insights.append({
                'type': 'cross_analysis',
                'category': 'data_quality',
                'title': 'Consistent Data Quality Concerns',
                'description': '. '.join(quality_issues) + '. Multiple analysis methods confirm these issues.',
                'impact': 'high',
                'priority_score': 8
            })
        
        # Feature-target relationship insights
        if ml_results:
            feature_importance = ml_results.get('feature_importance', {})
            correlations = statistical_results.get('correlations', {})
            strong_correlations = correlations.get('strong_correlations', [])
            
            # Check if highly correlated features are also important in ML
            corr_and_important = []
            for corr in strong_correlations:
                col1_imp = feature_importance.get(corr['column1'], 0)
                col2_imp = feature_importance.get(corr['column2'], 0)
                if col1_imp > 0.1 or col2_imp > 0.1:  # At least 10% importance
                    corr_and_important.append((corr, max(col1_imp, col2_imp)))
            
            if corr_and_important:
                insights.append({
                    'type': 'cross_analysis',
                    'category': 'feature_relationships',
                    'title': 'Correlated Features Drive Predictions',
                    'description': f"Strongly correlated features are also highly predictive, suggesting these relationships are fundamental to your target variable.",
                    'impact': 'medium',
                    'priority_score': 6
                })
        
        return insights
    
    def _generate_recommendations(self, df: pd.DataFrame,
                                statistical_results: Dict[str, Any],
                                pattern_results: Dict[str, Any],
                                ml_results: Optional[Dict[str, Any]],
                                target_column: Optional[str],
                                business_context: Optional[str]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Data quality recommendations
        missing_data = statistical_results.get('missing_data', {})
        if missing_data.get('missing_percentage', 0) > 10:
            by_column = missing_data.get('by_column', {})
            high_missing_cols = [col for col, info in by_column.items() if info['percentage'] > 20]
            
            if high_missing_cols:
                recommendations.append({
                    'category': 'data_quality',
                    'title': 'Address Missing Data',
                    'description': f"Consider imputation strategies for columns with high missing rates: {', '.join(high_missing_cols)}",
                    'actions': [
                        'Investigate why data is missing in these columns',
                        'Consider multiple imputation methods',
                        'Evaluate if missing data is informative (MNAR)',
                        'Consider collecting more complete data'
                    ],
                    'priority': 'high'
                })
        
        # Outlier handling recommendations
        outliers = statistical_results.get('outliers', {})
        high_outlier_cols = []
        for col, methods in outliers.items():
            if methods.get('iqr', {}).get('percentage', 0) > 15:
                high_outlier_cols.append(col)
        
        if high_outlier_cols:
            recommendations.append({
                'category': 'data_quality',
                'title': 'Investigate High Outlier Rates',
                'description': f"Columns {', '.join(high_outlier_cols)} have unusually high outlier percentages",
                'actions': [
                    'Manually inspect outlier values for validity',
                    'Consider robust scaling methods',
                    'Investigate business reasons for extreme values',
                    'Consider separate modeling for outlier segments'
                ],
                'priority': 'medium'
            })
        
        # Feature engineering recommendations
        correlations = statistical_results.get('correlations', {})
        strong_correlations = correlations.get('strong_correlations', [])
        
        if len(strong_correlations) > 2:
            recommendations.append({
                'category': 'feature_engineering',
                'title': 'Address Multicollinearity',
                'description': 'Multiple strong correlations detected between features',
                'actions': [
                    'Consider PCA or factor analysis for dimension reduction',
                    'Remove redundant highly correlated features',
                    'Create composite indices from correlated variables',
                    'Use regularization techniques in modeling'
                ],
                'priority': 'medium'
            })
        
        # ML-specific recommendations
        if ml_results:
            evaluation = ml_results.get('evaluation', {})
            task_type = ml_results.get('task_type', '')
            
            if task_type == 'regression':
                r2 = evaluation.get('r2', 0)
                if r2 < 0.3:
                    recommendations.append({
                        'category': 'modeling',
                        'title': 'Improve Model Performance',
                        'description': f'Current model explains only {r2*100:.1f}% of variance',
                        'actions': [
                            'Collect additional relevant features',
                            'Try feature engineering (interactions, polynomials)',
                            'Consider non-linear modeling approaches',
                            'Investigate if the target variable is predictable'
                        ],
                        'priority': 'high'
                    })
            
            elif task_type == 'classification':
                accuracy = evaluation.get('accuracy', 0)
                if accuracy < 0.7:
                    recommendations.append({
                        'category': 'modeling',
                        'title': 'Enhance Classification Performance',
                        'description': f'Current accuracy is {accuracy*100:.1f}%',
                        'actions': [
                            'Balance class distributions if needed',
                            'Feature selection and engineering',
                            'Try ensemble methods',
                            'Consider cost-sensitive learning'
                        ],
                        'priority': 'high'
                    })
        
        # Time series recommendations
        ts_patterns = pattern_results.get('time_series_patterns', {})
        if ts_patterns and isinstance(ts_patterns, dict):
            seasonal_detected = any(
                'seasonality' in patterns and any(s.get('is_seasonal') for s in patterns['seasonality'])
                for patterns in ts_patterns.values() if isinstance(patterns, dict)
            )
            
            if seasonal_detected:
                recommendations.append({
                    'category': 'time_series',
                    'title': 'Leverage Seasonal Patterns',
                    'description': 'Seasonal patterns detected in your time series data',
                    'actions': [
                        'Use seasonal decomposition for forecasting',
                        'Consider seasonal ARIMA models',
                        'Align business planning with seasonal cycles',
                        'Monitor for changes in seasonal patterns'
                    ],
                    'priority': 'medium'
                })
        
        # Business context recommendations
        if business_context:
            context_lower = business_context.lower()
            if 'sales' in context_lower or 'revenue' in context_lower:
                recommendations.append({
                    'category': 'business',
                    'title': 'Sales Analytics Focus',
                    'description': 'Based on sales context, consider these analyses',
                    'actions': [
                        'Segment analysis by customer groups',
                        'Time-based trend analysis for forecasting',
                        'Customer lifetime value modeling',
                        'Price elasticity analysis'
                    ],
                    'priority': 'medium'
                })
            
            elif 'marketing' in context_lower:
                recommendations.append({
                    'category': 'business',
                    'title': 'Marketing Analytics Focus',
                    'description': 'Based on marketing context, consider these analyses',
                    'actions': [
                        'Campaign effectiveness measurement',
                        'Customer segmentation for targeting',
                        'Attribution modeling',
                        'A/B testing framework setup'
                    ],
                    'priority': 'medium'
                })
        
        return recommendations
    
    def _rank_insights(self, insights: List[Dict[str, Any]], 
                      recommendations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Rank insights by priority and impact."""
        # Sort insights by priority score
        sorted_insights = sorted(insights, key=lambda x: x.get('priority_score', 0), reverse=True)
        
        # Categorize by priority
        high_priority = [i for i in sorted_insights if i.get('priority_score', 0) >= 8]
        medium_priority = [i for i in sorted_insights if 5 <= i.get('priority_score', 0) < 8]
        low_priority = [i for i in sorted_insights if i.get('priority_score', 0) < 5]
        
        return {
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority
        }
    
    def _generate_dataset_overview(self, df: pd.DataFrame,
                                 statistical_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive dataset overview."""
        overview = statistical_results.get('overview', {})
        missing_data = statistical_results.get('missing_data', {})
        
        return {
            'size': {
                'rows': df.shape[0],
                'columns': df.shape[1],
                'memory_usage_mb': overview.get('memory_usage', 0) / (1024 * 1024)
            },
            'column_types': overview.get('columns', {}),
            'data_quality': {
                'missing_percentage': missing_data.get('missing_percentage', 0),
                'complete_rows': df.shape[0] - df.isnull().any(axis=1).sum(),
                'duplicate_rows': df.duplicated().sum()
            },
            'summary': self._generate_dataset_summary(df, statistical_results)
        }
    
    def _generate_dataset_summary(self, df: pd.DataFrame,
                                statistical_results: Dict[str, Any]) -> str:
        """Generate a natural language summary of the dataset."""
        shape = df.shape
        overview = statistical_results.get('overview', {})
        columns = overview.get('columns', {})
        missing_pct = statistical_results.get('missing_data', {}).get('missing_percentage', 0)
        
        summary = f"This dataset contains {shape[0]:,} rows and {shape[1]} columns. "
        summary += f"It includes {len(columns.get('numerical', []))} numerical features, "
        summary += f"{len(columns.get('categorical', []))} categorical features"
        
        if len(columns.get('datetime', [])) > 0:
            summary += f", and {len(columns.get('datetime', []))} datetime columns"
        
        summary += ". "
        
        if missing_pct > 5:
            summary += f"The dataset has {missing_pct:.1f}% missing values, which may require attention. "
        elif missing_pct > 0:
            summary += f"Data completeness is good with only {missing_pct:.1f}% missing values. "
        else:
            summary += "The dataset is complete with no missing values. "
        
        return summary
    
    def _assess_data_quality(self, df: pd.DataFrame,
                           statistical_results: Dict[str, Any],
                           pattern_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall data quality."""
        missing_pct = statistical_results.get('missing_data', {}).get('missing_percentage', 0)
        duplicate_pct = (df.duplicated().sum() / len(df)) * 100
        
        # Quality patterns from pattern analysis
        quality_patterns = pattern_results.get('data_quality_patterns', {})
        constant_cols = len(quality_patterns.get('constant_columns', []))
        high_cardinality_cols = len(quality_patterns.get('high_cardinality_columns', []))
        
        # Calculate quality score (0-100)
        quality_score = 100
        quality_score -= min(missing_pct * 2, 40)  # Penalize missing data heavily
        quality_score -= min(duplicate_pct * 3, 30)  # Penalize duplicates
        quality_score -= constant_cols * 5  # Penalize constant columns
        quality_score -= high_cardinality_cols * 2  # Penalize high cardinality
        
        quality_score = max(0, quality_score)  # Ensure non-negative
        
        # Quality assessment
        if quality_score >= 85:
            assessment = "Excellent"
        elif quality_score >= 70:
            assessment = "Good"
        elif quality_score >= 50:
            assessment = "Fair"
        else:
            assessment = "Poor"
        
        return {
            'overall_score': quality_score,
            'assessment': assessment,
            'issues': {
                'missing_data_percentage': missing_pct,
                'duplicate_rows_percentage': duplicate_pct,
                'constant_columns': constant_cols,
                'high_cardinality_columns': high_cardinality_cols
            },
            'recommendations': self._get_quality_recommendations(quality_score, missing_pct, duplicate_pct)
        }
    
    def _get_quality_recommendations(self, quality_score: float,
                                   missing_pct: float,
                                   duplicate_pct: float) -> List[str]:
        """Get data quality improvement recommendations."""
        recommendations = []
        
        if quality_score < 70:
            recommendations.append("Consider comprehensive data cleaning before analysis")
        
        if missing_pct > 10:
            recommendations.append("Implement missing data imputation strategies")
        
        if duplicate_pct > 1:
            recommendations.append("Remove or investigate duplicate records")
        
        if quality_score < 50:
            recommendations.append("Consider data collection process improvements")
        
        return recommendations
    
    def _generate_business_insights(self, df: pd.DataFrame,
                                  statistical_results: Dict[str, Any],
                                  pattern_results: Dict[str, Any],
                                  business_context: Optional[str]) -> List[str]:
        """Generate business-specific insights based on context."""
        insights = []
        
        if not business_context:
            return ["No business context provided for domain-specific insights"]
        
        context_lower = business_context.lower()
        
        # Sales context insights
        if 'sales' in context_lower or 'revenue' in context_lower:
            # Look for time-based patterns
            trends = pattern_results.get('trends', {})
            growing_metrics = []
            declining_metrics = []
            
            for col, trend_data in trends.items():
                if isinstance(trend_data, dict) and 'linear_trend' in trend_data:
                    linear = trend_data['linear_trend']
                    if linear.get('is_significant'):
                        if linear.get('trend_direction') == 'increasing':
                            growing_metrics.append(col)
                        elif linear.get('trend_direction') == 'decreasing':
                            declining_metrics.append(col)
            
            if growing_metrics:
                insights.append(f"Growing metrics detected: {', '.join(growing_metrics)}. Consider scaling successful strategies.")
            
            if declining_metrics:
                insights.append(f"Declining metrics identified: {', '.join(declining_metrics)}. Investigate root causes and intervention strategies.")
        
        # Marketing context insights
        elif 'marketing' in context_lower:
            # Look for clustering patterns (customer segments)
            clustering = pattern_results.get('clustering', {})
            if 'kmeans' in clustering and clustering['kmeans'].get('silhouette_score', 0) > 0.5:
                n_clusters = clustering['kmeans']['n_clusters']
                insights.append(f"Clear customer segments identified ({n_clusters} groups). Consider targeted marketing strategies for each segment.")
        
        # Operations context insights
        elif 'operations' in context_lower or 'production' in context_lower:
            # Look for anomalies and quality issues
            anomalies = pattern_results.get('anomalies', {})
            anomaly_pct = anomalies.get('isolation_forest', {}).get('anomaly_percentage', 0)
            
            if anomaly_pct > 5:
                insights.append(f"High anomaly rate ({anomaly_pct:.1f}%) suggests process variability. Consider process control improvements.")
        
        return insights
    
    def _suggest_next_steps(self, df: pd.DataFrame,
                          statistical_results: Dict[str, Any],
                          pattern_results: Dict[str, Any],
                          ml_results: Optional[Dict[str, Any]]) -> List[str]:
        """Suggest logical next steps for analysis."""
        next_steps = []
        
        # Data quality next steps
        missing_pct = statistical_results.get('missing_data', {}).get('missing_percentage', 0)
        if missing_pct > 10:
            next_steps.append("Implement data cleaning and imputation strategies")
        
        # Pattern analysis next steps
        clustering = pattern_results.get('clustering', {})
        if 'kmeans' in clustering and clustering['kmeans'].get('silhouette_score', 0) > 0.5:
            next_steps.append("Perform detailed cluster analysis and profiling")
        
        # Time series next steps
        ts_patterns = pattern_results.get('time_series_patterns', {})
        if ts_patterns and isinstance(ts_patterns, dict):
            seasonal_exists = any(
                'seasonality' in patterns and any(s.get('is_seasonal') for s in patterns['seasonality'])
                for patterns in ts_patterns.values() if isinstance(patterns, dict)
            )
            if seasonal_exists:
                next_steps.append("Build forecasting models leveraging seasonal patterns")
        
        # ML next steps
        if ml_results:
            task_type = ml_results.get('task_type', '')
            evaluation = ml_results.get('evaluation', {})
            
            if task_type == 'regression':
                r2 = evaluation.get('r2', 0)
                if r2 > 0.6:
                    next_steps.append("Deploy predictive model for business use")
                else:
                    next_steps.append("Improve model with feature engineering and additional data")
            
            elif task_type == 'classification':
                accuracy = evaluation.get('accuracy', 0)
                if accuracy > 0.8:
                    next_steps.append("Implement classification model in production")
                else:
                    next_steps.append("Enhance model performance with advanced techniques")
        
        # General analysis next steps
        if len(next_steps) == 0:
            next_steps.extend([
                "Define specific business questions for targeted analysis",
                "Collect additional relevant data sources",
                "Implement automated monitoring and reporting"
            ])
        
        return next_steps
    
    def export_insights_report(self, insights_result: Dict[str, Any],
                             format: str = 'markdown') -> str:
        """Export insights as a formatted report."""
        if format == 'markdown':
            return self._create_markdown_report(insights_result)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _create_markdown_report(self, insights_result: Dict[str, Any]) -> str:
        """Create a markdown report of insights."""
        report = []
        
        # Header
        report.append("# Data Science Insights Report")
        report.append(f"Generated on: {insights_result.get('metadata', {}).get('analysis_timestamp', 'Unknown')}")
        report.append("")
        
        # Dataset Overview
        overview = insights_result.get('dataset_overview', {})
        report.append("## Dataset Overview")
        report.append(overview.get('summary', 'No summary available'))
        report.append("")
        
        size_info = overview.get('size', {})
        report.append(f"- **Size**: {size_info.get('rows', 0):,} rows × {size_info.get('columns', 0)} columns")
        report.append(f"- **Memory Usage**: {size_info.get('memory_usage_mb', 0):.1f} MB")
        report.append("")
        
        # Key Insights
        key_insights = insights_result.get('key_insights', [])
        if key_insights:
            report.append("## Key Insights")
            for i, insight in enumerate(key_insights, 1):
                report.append(f"### {i}. {insight.get('title', 'Untitled')}")
                report.append(insight.get('description', 'No description'))
                report.append("")
        
        # Recommendations
        recommendations = insights_result.get('actionable_recommendations', [])
        if recommendations:
            report.append("## Recommendations")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"### {i}. {rec.get('title', 'Untitled')}")
                report.append(rec.get('description', 'No description'))
                
                actions = rec.get('actions', [])
                if actions:
                    report.append("\n**Suggested Actions:**")
                    for action in actions:
                        report.append(f"- {action}")
                report.append("")
        
        # Data Quality Assessment
        quality = insights_result.get('data_quality_assessment', {})
        if quality:
            report.append("## Data Quality Assessment")
            report.append(f"**Overall Score**: {quality.get('overall_score', 0):.1f}/100 ({quality.get('assessment', 'Unknown')})")
            report.append("")
        
        # Next Steps
        next_steps = insights_result.get('next_steps', [])
        if next_steps:
            report.append("## Recommended Next Steps")
            for i, step in enumerate(next_steps, 1):
                report.append(f"{i}. {step}")
            report.append("")
        
        return "\n".join(report)