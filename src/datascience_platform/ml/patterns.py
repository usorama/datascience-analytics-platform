"""Pattern Detection Engine

Implements clustering, time series analysis, anomaly detection, 
and trend analysis for discovering patterns in datasets.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import silhouette_score
from scipy import signal
from scipy.stats import linregress
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

logger = logging.getLogger(__name__)


class PatternDetector:
    """Comprehensive pattern detection engine for datasets."""
    
    def __init__(self):
        """Initialize the pattern detector."""
        self.results = {}
        self.scaler = StandardScaler()
        
    def detect_patterns(self, df: pd.DataFrame, 
                       time_column: Optional[str] = None,
                       target_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect patterns in the dataset using multiple methods.
        
        Args:
            df: Input DataFrame
            time_column: Name of time column for time series analysis
            target_column: Name of target column for supervised pattern detection
            
        Returns:
            Dictionary containing all pattern detection results
        """
        try:
            logger.info(f"Starting pattern detection for dataset with shape {df.shape}")
            
            results = {
                'clustering': self._perform_clustering(df),
                'anomalies': self._detect_anomalies(df),
                'trends': self._analyze_trends(df, time_column),
                'time_series_patterns': self._detect_time_series_patterns(df, time_column) if time_column else None,
                'feature_interactions': self._analyze_feature_interactions(df),
                'data_quality_patterns': self._detect_data_quality_patterns(df)
            }
            
            self.results = results
            logger.info("Pattern detection completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in pattern detection: {str(e)}")
            raise
    
    def _perform_clustering(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform clustering analysis using multiple algorithms."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return {'message': 'Insufficient numerical columns for clustering'}
        
        # Prepare data
        cluster_data = df[numerical_cols].dropna()
        if len(cluster_data) < 10:
            return {'message': 'Insufficient data points for clustering'}
        
        # Scale the data
        scaled_data = self.scaler.fit_transform(cluster_data)
        
        clustering_results = {}
        
        # K-Means Clustering
        try:
            optimal_k = self._find_optimal_clusters(scaled_data)
            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            kmeans_labels = kmeans.fit_predict(scaled_data)
            
            clustering_results['kmeans'] = {
                'n_clusters': optimal_k,
                'labels': kmeans_labels.tolist(),
                'cluster_centers': kmeans.cluster_centers_.tolist(),
                'inertia': float(kmeans.inertia_),
                'silhouette_score': float(silhouette_score(scaled_data, kmeans_labels)),
                'cluster_sizes': pd.Series(kmeans_labels).value_counts().to_dict()
            }
            
        except Exception as e:
            logger.warning(f"K-Means clustering failed: {str(e)}")
            clustering_results['kmeans'] = {'error': str(e)}
        
        # DBSCAN Clustering
        try:
            dbscan = DBSCAN(eps=0.5, min_samples=5)
            dbscan_labels = dbscan.fit_predict(scaled_data)
            
            n_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
            n_noise = list(dbscan_labels).count(-1)
            
            clustering_results['dbscan'] = {
                'n_clusters': n_clusters,
                'n_noise_points': n_noise,
                'labels': dbscan_labels.tolist(),
                'silhouette_score': float(silhouette_score(scaled_data, dbscan_labels)) if n_clusters > 1 else None,
                'cluster_sizes': pd.Series(dbscan_labels).value_counts().to_dict()
            }
            
        except Exception as e:
            logger.warning(f"DBSCAN clustering failed: {str(e)}")
            clustering_results['dbscan'] = {'error': str(e)}
        
        # Hierarchical Clustering
        try:
            if len(cluster_data) <= 1000:  # Limit for computational efficiency
                hierarchical = AgglomerativeClustering(n_clusters=optimal_k)
                hierarchical_labels = hierarchical.fit_predict(scaled_data)
                
                clustering_results['hierarchical'] = {
                    'n_clusters': optimal_k,
                    'labels': hierarchical_labels.tolist(),
                    'silhouette_score': float(silhouette_score(scaled_data, hierarchical_labels)),
                    'cluster_sizes': pd.Series(hierarchical_labels).value_counts().to_dict()
                }
            else:
                clustering_results['hierarchical'] = {'message': 'Dataset too large for hierarchical clustering'}
                
        except Exception as e:
            logger.warning(f"Hierarchical clustering failed: {str(e)}")
            clustering_results['hierarchical'] = {'error': str(e)}
        
        return clustering_results
    
    def _find_optimal_clusters(self, data: np.ndarray, max_k: int = 10) -> int:
        """Find optimal number of clusters using elbow method."""
        max_k = min(max_k, len(data) // 2, 10)
        inertias = []
        
        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(data)
            inertias.append(kmeans.inertia_)
        
        # Find elbow point
        if len(inertias) >= 2:
            # Simple elbow detection using second derivative
            deltas = np.diff(inertias)
            delta_deltas = np.diff(deltas)
            elbow_idx = np.argmax(delta_deltas) + 2  # +2 because we start from k=2
            return min(elbow_idx, max_k)
        
        return 3  # Default
    
    def _detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies using multiple methods."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) == 0:
            return {'message': 'No numerical columns for anomaly detection'}
        
        anomaly_data = df[numerical_cols].dropna()
        if len(anomaly_data) < 10:
            return {'message': 'Insufficient data for anomaly detection'}
        
        anomaly_results = {}
        
        # Isolation Forest
        try:
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            iso_labels = iso_forest.fit_predict(anomaly_data)
            anomaly_scores = iso_forest.decision_function(anomaly_data)
            
            anomaly_results['isolation_forest'] = {
                'anomaly_count': int(np.sum(iso_labels == -1)),
                'anomaly_percentage': float((np.sum(iso_labels == -1) / len(iso_labels)) * 100),
                'anomaly_indices': np.where(iso_labels == -1)[0].tolist(),
                'anomaly_scores': anomaly_scores.tolist(),
                'threshold': float(np.percentile(anomaly_scores, 10))
            }
            
        except Exception as e:
            logger.warning(f"Isolation Forest failed: {str(e)}")
            anomaly_results['isolation_forest'] = {'error': str(e)}
        
        # Local Outlier Factor
        try:
            lof = LocalOutlierFactor(contamination=0.1)
            lof_labels = lof.fit_predict(anomaly_data)
            lof_scores = lof.negative_outlier_factor_
            
            anomaly_results['local_outlier_factor'] = {
                'anomaly_count': int(np.sum(lof_labels == -1)),
                'anomaly_percentage': float((np.sum(lof_labels == -1) / len(lof_labels)) * 100),
                'anomaly_indices': np.where(lof_labels == -1)[0].tolist(),
                'outlier_scores': lof_scores.tolist(),
                'threshold': float(np.percentile(lof_scores, 10))
            }
            
        except Exception as e:
            logger.warning(f"Local Outlier Factor failed: {str(e)}")
            anomaly_results['local_outlier_factor'] = {'error': str(e)}
        
        return anomaly_results
    
    def _analyze_trends(self, df: pd.DataFrame, 
                       time_column: Optional[str] = None) -> Dict[str, Any]:
        """Analyze trends in numerical columns."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) == 0:
            return {'message': 'No numerical columns for trend analysis'}
        
        trend_results = {}
        
        for col in numerical_cols:
            series = df[col].dropna()
            if len(series) < 3:
                continue
                
            trend_results[col] = {}
            
            # Linear trend analysis
            x = np.arange(len(series))
            slope, intercept, r_value, p_value, std_err = linregress(x, series)
            
            trend_results[col]['linear_trend'] = {
                'slope': float(slope),
                'intercept': float(intercept),
                'r_squared': float(r_value ** 2),
                'p_value': float(p_value),
                'is_significant': p_value < 0.05,
                'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                'trend_strength': self._classify_trend_strength(abs(r_value))
            }
            
            # Moving averages
            if len(series) >= 5:
                ma_5 = series.rolling(window=5).mean()
                ma_10 = series.rolling(window=min(10, len(series)//2)).mean()
                
                trend_results[col]['moving_averages'] = {
                    'ma_5': ma_5.dropna().tolist(),
                    'ma_10': ma_10.dropna().tolist(),
                    'current_vs_ma5': float((series.iloc[-1] - ma_5.iloc[-1]) / ma_5.iloc[-1] * 100) if not pd.isna(ma_5.iloc[-1]) else None,
                    'current_vs_ma10': float((series.iloc[-1] - ma_10.iloc[-1]) / ma_10.iloc[-1] * 100) if not pd.isna(ma_10.iloc[-1]) else None
                }
            
            # Volatility analysis
            if len(series) >= 2:
                returns = series.pct_change().dropna()
                trend_results[col]['volatility'] = {
                    'std_dev': float(series.std()),
                    'coefficient_of_variation': float(series.std() / series.mean()) if series.mean() != 0 else None,
                    'return_volatility': float(returns.std()) if len(returns) > 0 else None,
                    'volatility_classification': self._classify_volatility(series.std() / series.mean()) if series.mean() != 0 else None
                }
        
        return trend_results
    
    def _classify_trend_strength(self, r_value: float) -> str:
        """Classify trend strength based on correlation coefficient."""
        if r_value >= 0.8:
            return "Very Strong"
        elif r_value >= 0.6:
            return "Strong"
        elif r_value >= 0.4:
            return "Moderate"
        elif r_value >= 0.2:
            return "Weak"
        else:
            return "Very Weak"
    
    def _classify_volatility(self, cv: float) -> str:
        """Classify volatility based on coefficient of variation."""
        if cv <= 0.1:
            return "Low"
        elif cv <= 0.25:
            return "Moderate"
        elif cv <= 0.5:
            return "High"
        else:
            return "Very High"
    
    def _detect_time_series_patterns(self, df: pd.DataFrame, 
                                   time_column: str) -> Dict[str, Any]:
        """Detect patterns in time series data."""
        if time_column not in df.columns:
            return {'error': f'Time column {time_column} not found'}
        
        try:
            df_ts = df.copy()
            df_ts[time_column] = pd.to_datetime(df_ts[time_column])
            df_ts = df_ts.sort_values(time_column)
            
            numerical_cols = df_ts.select_dtypes(include=[np.number]).columns
            time_series_results = {}
            
            for col in numerical_cols:
                series = df_ts.set_index(time_column)[col].dropna()
                if len(series) < 10:
                    continue
                
                time_series_results[col] = {}
                
                # Seasonality detection
                try:
                    # Simple seasonality check using autocorrelation
                    autocorr_values = []
                    for lag in [7, 30, 90, 365]:  # Weekly, monthly, quarterly, yearly
                        if len(series) > lag:
                            autocorr = series.autocorr(lag=lag)
                            if not pd.isna(autocorr):
                                autocorr_values.append({
                                    'lag': lag,
                                    'lag_type': self._get_lag_type(lag),
                                    'autocorrelation': float(autocorr),
                                    'is_seasonal': abs(autocorr) > 0.3
                                })
                    
                    time_series_results[col]['seasonality'] = autocorr_values
                    
                except Exception as e:
                    logger.warning(f"Seasonality detection failed for {col}: {str(e)}")
                
                # Trend decomposition (simple)
                try:
                    # Calculate rolling mean and residuals
                    window = min(30, len(series) // 4)
                    if window >= 2:
                        trend = series.rolling(window=window, center=True).mean()
                        residual = series - trend
                        
                        time_series_results[col]['decomposition'] = {
                            'trend_strength': float(1 - (residual.var() / series.var())) if series.var() > 0 else 0,
                            'has_strong_trend': (1 - (residual.var() / series.var())) > 0.6 if series.var() > 0 else False,
                            'residual_variance': float(residual.var()) if not pd.isna(residual.var()) else None
                        }
                        
                except Exception as e:
                    logger.warning(f"Trend decomposition failed for {col}: {str(e)}")
                
                # Change point detection (simple)
                try:
                    # Detect significant changes in mean
                    window_size = len(series) // 10
                    if window_size >= 5:
                        changes = []
                        for i in range(window_size, len(series) - window_size):
                            before = series.iloc[i-window_size:i].mean()
                            after = series.iloc[i:i+window_size].mean()
                            change_pct = abs((after - before) / before * 100) if before != 0 else 0
                            
                            if change_pct > 20:  # 20% change threshold
                                changes.append({
                                    'index': i,
                                    'date': str(series.index[i]),
                                    'change_percentage': float(change_pct),
                                    'before_mean': float(before),
                                    'after_mean': float(after)
                                })
                        
                        time_series_results[col]['change_points'] = changes[:5]  # Limit to top 5
                        
                except Exception as e:
                    logger.warning(f"Change point detection failed for {col}: {str(e)}")
            
            return time_series_results
            
        except Exception as e:
            logger.error(f"Time series pattern detection failed: {str(e)}")
            return {'error': str(e)}
    
    def _get_lag_type(self, lag: int) -> str:
        """Get descriptive name for lag period."""
        if lag == 7:
            return "Weekly"
        elif lag == 30:
            return "Monthly"
        elif lag == 90:
            return "Quarterly"
        elif lag == 365:
            return "Yearly"
        else:
            return f"{lag}-day"
    
    def _analyze_feature_interactions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze interactions between features."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return {'message': 'Insufficient numerical columns for interaction analysis'}
        
        interaction_results = {}
        
        # PCA for dimensionality analysis
        try:
            pca_data = df[numerical_cols].dropna()
            if len(pca_data) > 0:
                scaled_data = StandardScaler().fit_transform(pca_data)
                
                n_components = min(len(numerical_cols), len(pca_data))
                pca = PCA(n_components=n_components)
                pca_result = pca.fit_transform(scaled_data)
                
                interaction_results['pca'] = {
                    'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
                    'cumulative_variance': np.cumsum(pca.explained_variance_ratio_).tolist(),
                    'components': pca.components_.tolist(),
                    'feature_importance': {
                        col: float(abs(pca.components_[0][i]))  # First component importance
                        for i, col in enumerate(numerical_cols)
                    }
                }
                
        except Exception as e:
            logger.warning(f"PCA analysis failed: {str(e)}")
            interaction_results['pca'] = {'error': str(e)}
        
        return interaction_results
    
    def _detect_data_quality_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect data quality issues and patterns."""
        quality_results = {
            'duplicates': {
                'count': int(df.duplicated().sum()),
                'percentage': float((df.duplicated().sum() / len(df)) * 100)
            },
            'constant_columns': [],
            'high_cardinality_columns': [],
            'data_type_inconsistencies': {}
        }
        
        # Constant columns
        for col in df.columns:
            if df[col].nunique() <= 1:
                quality_results['constant_columns'].append(col)
        
        # High cardinality columns
        for col in df.select_dtypes(include=['object', 'category']).columns:
            cardinality_ratio = df[col].nunique() / len(df)
            if cardinality_ratio > 0.9:  # More than 90% unique values
                quality_results['high_cardinality_columns'].append({
                    'column': col,
                    'unique_count': int(df[col].nunique()),
                    'cardinality_ratio': float(cardinality_ratio)
                })
        
        # Data type inconsistencies (simple check)
        for col in df.select_dtypes(include=['object']).columns:
            # Check if numeric strings exist in object columns
            try:
                numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                if numeric_count > 0 and numeric_count < len(df):
                    quality_results['data_type_inconsistencies'][col] = {
                        'potential_numeric': int(numeric_count),
                        'percentage_numeric': float((numeric_count / len(df)) * 100)
                    }
            except:
                pass
        
        return quality_results
    
    def get_pattern_insights(self) -> List[str]:
        """Generate human-readable insights from pattern detection."""
        if not self.results:
            return ["No pattern analysis results available. Run detect_patterns() first."]
        
        insights = []
        
        # Clustering insights
        clustering = self.results.get('clustering', {})
        if 'kmeans' in clustering and 'n_clusters' in clustering['kmeans']:
            n_clusters = clustering['kmeans']['n_clusters']
            silhouette = clustering['kmeans'].get('silhouette_score', 0)
            insights.append(f"Data naturally groups into {n_clusters} clusters (silhouette score: {silhouette:.2f})")
        
        # Anomaly insights
        anomalies = self.results.get('anomalies', {})
        if 'isolation_forest' in anomalies:
            anomaly_pct = anomalies['isolation_forest'].get('anomaly_percentage', 0)
            if anomaly_pct > 5:
                insights.append(f"High anomaly rate detected: {anomaly_pct:.1f}% of data points are anomalous")
        
        # Trend insights
        trends = self.results.get('trends', {})
        strong_trends = []
        for col, trend_data in trends.items():
            if isinstance(trend_data, dict) and 'linear_trend' in trend_data:
                linear = trend_data['linear_trend']
                if linear.get('is_significant') and linear.get('trend_strength') in ['Strong', 'Very Strong']:
                    direction = linear.get('trend_direction', 'unknown')
                    strong_trends.append(f"{col} ({direction})")
        
        if strong_trends:
            insights.append(f"Strong trends detected in: {', '.join(strong_trends)}")
        
        # Time series insights
        ts_patterns = self.results.get('time_series_patterns', {})
        if ts_patterns and isinstance(ts_patterns, dict):
            seasonal_cols = []
            for col, patterns in ts_patterns.items():
                if isinstance(patterns, dict) and 'seasonality' in patterns:
                    seasonal_patterns = [s for s in patterns['seasonality'] if s.get('is_seasonal')]
                    if seasonal_patterns:
                        seasonal_cols.append(col)
            
            if seasonal_cols:
                insights.append(f"Seasonal patterns found in: {', '.join(seasonal_cols)}")
        
        # Data quality insights
        quality = self.results.get('data_quality_patterns', {})
        if quality:
            duplicates_pct = quality.get('duplicates', {}).get('percentage', 0)
            if duplicates_pct > 1:
                insights.append(f"Dataset contains {duplicates_pct:.1f}% duplicate rows")
            
            constant_cols = quality.get('constant_columns', [])
            if constant_cols:
                insights.append(f"Constant columns detected: {', '.join(constant_cols)}")
        
        return insights if insights else ["No significant patterns detected in the data"]