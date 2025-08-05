"""Statistical Analysis Engine

Provides comprehensive descriptive statistics, correlation analysis, 
outlier detection, and distribution identification for datasets.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats
from scipy.stats import shapiro, normaltest, kstest
import warnings

# Suppress scipy warnings for cleaner output
warnings.filterwarnings('ignore', category=RuntimeWarning)

logger = logging.getLogger(__name__)


class StatisticsEngine:
    """Comprehensive statistical analysis engine for datasets."""
    
    def __init__(self):
        """Initialize the statistics engine."""
        self.results = {}
        
    def analyze_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive statistical analysis on the entire dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary containing all statistical analyses
        """
        try:
            logger.info(f"Starting statistical analysis for dataset with shape {df.shape}")
            
            results = {
                'overview': self._get_dataset_overview(df),
                'descriptive_stats': self._calculate_descriptive_stats(df),
                'correlations': self._calculate_correlations(df),
                'outliers': self._detect_outliers(df),
                'distributions': self._identify_distributions(df),
                'missing_data': self._analyze_missing_data(df)
            }
            
            self.results = results
            logger.info("Statistical analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in statistical analysis: {str(e)}")
            raise
    
    def _get_dataset_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic dataset overview information."""
        return {
            'shape': df.shape,
            'memory_usage': df.memory_usage(deep=True).sum(),
            'dtypes': df.dtypes.value_counts().to_dict(),
            'columns': {
                'numerical': df.select_dtypes(include=[np.number]).columns.tolist(),
                'categorical': df.select_dtypes(include=['object', 'category']).columns.tolist(),
                'datetime': df.select_dtypes(include=['datetime64']).columns.tolist()
            }
        }
    
    def _calculate_descriptive_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive descriptive statistics."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        results = {
            'numerical': {},
            'categorical': {}
        }
        
        # Numerical statistics
        if len(numerical_cols) > 0:
            numerical_stats = df[numerical_cols].describe()
            
            # Add additional statistics
            for col in numerical_cols:
                if df[col].notna().sum() > 0:  # Only if there are non-null values
                    series = df[col].dropna()
                    results['numerical'][col] = {
                        'count': int(series.count()),
                        'mean': float(series.mean()),
                        'median': float(series.median()),
                        'mode': float(series.mode().iloc[0]) if len(series.mode()) > 0 else None,
                        'std': float(series.std()),
                        'var': float(series.var()),
                        'min': float(series.min()),
                        'max': float(series.max()),
                        'range': float(series.max() - series.min()),
                        'q1': float(series.quantile(0.25)),
                        'q3': float(series.quantile(0.75)),
                        'iqr': float(series.quantile(0.75) - series.quantile(0.25)),
                        'skewness': float(series.skew()),
                        'kurtosis': float(series.kurtosis()),
                        'coefficient_of_variation': float(series.std() / series.mean()) if series.mean() != 0 else None
                    }
        
        # Categorical statistics
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                if df[col].notna().sum() > 0:
                    series = df[col].dropna()
                    value_counts = series.value_counts()
                    results['categorical'][col] = {
                        'count': int(series.count()),
                        'unique': int(series.nunique()),
                        'most_frequent': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                        'most_frequent_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                        'least_frequent': str(value_counts.index[-1]) if len(value_counts) > 0 else None,
                        'least_frequent_count': int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
                        'entropy': float(-np.sum(value_counts / len(series) * np.log2(value_counts / len(series))))
                    }
        
        return results
    
    def _calculate_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate correlation matrices using different methods."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return {'message': 'Insufficient numerical columns for correlation analysis'}
        
        numerical_df = df[numerical_cols].dropna()
        
        correlations = {
            'pearson': numerical_df.corr(method='pearson').to_dict(),
            'spearman': numerical_df.corr(method='spearman').to_dict(),
            'kendall': numerical_df.corr(method='kendall').to_dict()
        }
        
        # Find strong correlations
        pearson_corr = numerical_df.corr(method='pearson')
        strong_correlations = []
        
        for i in range(len(pearson_corr.columns)):
            for j in range(i + 1, len(pearson_corr.columns)):
                col1, col2 = pearson_corr.columns[i], pearson_corr.columns[j]
                corr_value = pearson_corr.iloc[i, j]
                
                if abs(corr_value) > 0.7:  # Strong correlation threshold
                    strong_correlations.append({
                        'column1': col1,
                        'column2': col2,
                        'correlation': float(corr_value),
                        'strength': 'Very Strong' if abs(corr_value) > 0.9 else 'Strong'
                    })
        
        correlations['strong_correlations'] = strong_correlations
        return correlations
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers using multiple methods."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        outlier_results = {}
        
        for col in numerical_cols:
            if df[col].notna().sum() > 0:
                series = df[col].dropna()
                outlier_results[col] = {}
                
                # IQR Method
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                iqr_outliers = series[(series < lower_bound) | (series > upper_bound)]
                outlier_results[col]['iqr'] = {
                    'count': len(iqr_outliers),
                    'percentage': (len(iqr_outliers) / len(series)) * 100,
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'outlier_values': iqr_outliers.tolist()[:10]  # Limit to first 10
                }
                
                # Z-Score Method
                z_scores = np.abs(stats.zscore(series))
                z_outliers = series[z_scores > 3]  # 3 standard deviations
                outlier_results[col]['zscore'] = {
                    'count': len(z_outliers),
                    'percentage': (len(z_outliers) / len(series)) * 100,
                    'threshold': 3.0,
                    'outlier_values': z_outliers.tolist()[:10]
                }
                
                # Modified Z-Score Method (using median)
                median = series.median()
                mad = np.median(np.abs(series - median))
                if mad != 0:
                    modified_z_scores = 0.6745 * (series - median) / mad
                    modified_z_outliers = series[np.abs(modified_z_scores) > 3.5]
                    outlier_results[col]['modified_zscore'] = {
                        'count': len(modified_z_outliers),
                        'percentage': (len(modified_z_outliers) / len(series)) * 100,
                        'threshold': 3.5,
                        'outlier_values': modified_z_outliers.tolist()[:10]
                    }
        
        return outlier_results
    
    def _identify_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify the distribution of numerical columns."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        distribution_results = {}
        
        for col in numerical_cols:
            if df[col].notna().sum() > 3:  # Need at least 4 values for tests
                series = df[col].dropna()
                distribution_results[col] = {}
                
                # Normality tests
                try:
                    # Shapiro-Wilk test (best for small samples)
                    if len(series) <= 5000:
                        shapiro_stat, shapiro_p = shapiro(series)
                        distribution_results[col]['shapiro_wilk'] = {
                            'statistic': float(shapiro_stat),
                            'p_value': float(shapiro_p),
                            'is_normal': shapiro_p > 0.05
                        }
                    
                    # D'Agostino's normality test
                    if len(series) >= 8:
                        dagostino_stat, dagostino_p = normaltest(series)
                        distribution_results[col]['dagostino'] = {
                            'statistic': float(dagostino_stat),
                            'p_value': float(dagostino_p),
                            'is_normal': dagostino_p > 0.05
                        }
                    
                    # Kolmogorov-Smirnov test against normal distribution
                    ks_stat, ks_p = kstest(series, 'norm', args=(series.mean(), series.std()))
                    distribution_results[col]['kolmogorov_smirnov'] = {
                        'statistic': float(ks_stat),
                        'p_value': float(ks_p),
                        'is_normal': ks_p > 0.05
                    }
                    
                    # Distribution characteristics
                    distribution_results[col]['characteristics'] = {
                        'skewness': float(series.skew()),
                        'kurtosis': float(series.kurtosis()),
                        'is_symmetric': abs(series.skew()) < 0.5,
                        'distribution_type': self._classify_distribution(series)
                    }
                    
                except Exception as e:
                    logger.warning(f"Could not perform distribution tests for column {col}: {str(e)}")
                    distribution_results[col]['error'] = str(e)
        
        return distribution_results
    
    def _classify_distribution(self, series: pd.Series) -> str:
        """Classify the distribution type based on statistical properties."""
        skewness = series.skew()
        kurtosis = series.kurtosis()
        
        if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
            return "Approximately Normal"
        elif skewness > 1:
            return "Right Skewed (Positive Skew)"
        elif skewness < -1:
            return "Left Skewed (Negative Skew)"
        elif kurtosis > 3:
            return "Heavy Tailed (Leptokurtic)"
        elif kurtosis < -1:
            return "Light Tailed (Platykurtic)"
        else:
            return "Moderately Skewed"
    
    def _analyze_missing_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze missing data patterns."""
        missing_data = {
            'total_missing': int(df.isnull().sum().sum()),
            'missing_percentage': float((df.isnull().sum().sum() / df.size) * 100)
        }
        
        # Per column missing data
        column_missing = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                column_missing[col] = {
                    'count': int(missing_count),
                    'percentage': float((missing_count / len(df)) * 100)
                }
        
        missing_data['by_column'] = column_missing
        
        # Missing data patterns
        if len(column_missing) > 0:
            missing_patterns = df.isnull().value_counts().head(10)
            missing_data['patterns'] = [
                {
                    'pattern': pattern,
                    'count': int(count),
                    'percentage': float((count / len(df)) * 100)
                }
                for pattern, count in missing_patterns.items()
            ]
        
        return missing_data
    
    def get_summary_insights(self) -> List[str]:
        """Generate human-readable summary insights from the statistical analysis."""
        if not self.results:
            return ["No analysis results available. Run analyze_dataset() first."]
        
        insights = []
        
        # Dataset overview insights
        overview = self.results.get('overview', {})
        if overview:
            shape = overview.get('shape', (0, 0))
            insights.append(f"Dataset contains {shape[0]:,} rows and {shape[1]} columns")
            
            cols = overview.get('columns', {})
            insights.append(f"Column types: {len(cols.get('numerical', []))} numerical, "
                          f"{len(cols.get('categorical', []))} categorical, "
                          f"{len(cols.get('datetime', []))} datetime")
        
        # Missing data insights
        missing = self.results.get('missing_data', {})
        if missing.get('missing_percentage', 0) > 5:
            insights.append(f"Dataset has {missing['missing_percentage']:.1f}% missing data")
        
        # Correlation insights
        correlations = self.results.get('correlations', {})
        strong_corrs = correlations.get('strong_correlations', [])
        if strong_corrs:
            insights.append(f"Found {len(strong_corrs)} strong correlations between variables")
        
        # Outlier insights
        outliers = self.results.get('outliers', {})
        high_outlier_cols = []
        for col, methods in outliers.items():
            iqr_pct = methods.get('iqr', {}).get('percentage', 0)
            if iqr_pct > 10:
                high_outlier_cols.append(col)
        
        if high_outlier_cols:
            insights.append(f"High outlier percentage detected in: {', '.join(high_outlier_cols)}")
        
        return insights