"""ML Technique Repository and Performance Benchmarking

This module provides a curated repository of ML techniques and methods for
benchmarking their performance, replacing LLM-based web search with a
structured knowledge base.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import logging
from datetime import datetime

from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, QuantileTransformer,
    OneHotEncoder, OrdinalEncoder, TargetEncoder, LabelEncoder,
    PolynomialFeatures, KBinsDiscretizer
)
from sklearn.feature_selection import (
    SelectKBest, RFE, SelectFromModel, VarianceThreshold,
    mutual_info_classif, mutual_info_regression, f_classif, chi2
)
from sklearn.decomposition import PCA, TruncatedSVD, NMF, FastICA
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor,
    ExtraTreesClassifier, ExtraTreesRegressor
)
from sklearn.linear_model import (
    LogisticRegression, LinearRegression, Ridge, Lasso,
    ElasticNet, SGDClassifier, SGDRegressor
)
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB, MultinomialNB

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

try:
    import lightgbm as lgb
    LGB_AVAILABLE = True
except ImportError:
    LGB_AVAILABLE = False

try:
    import catboost as cb
    CB_AVAILABLE = True
except ImportError:
    CB_AVAILABLE = False

logger = logging.getLogger(__name__)


class TechniqueCategory(Enum):
    """Categories of ML techniques."""
    SCALING = "scaling"
    ENCODING = "encoding"
    FEATURE_CREATION = "feature_creation"
    FEATURE_SELECTION = "feature_selection"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    ENSEMBLE = "ensemble"
    VALIDATION = "validation"


@dataclass
class MLTechnique:
    """Represents an ML technique with metadata."""
    technique_id: str
    name: str
    category: TechniqueCategory
    description: str
    implementation: Any  # Class or function
    default_params: Dict[str, Any]
    param_ranges: Dict[str, Any]
    complexity: str  # 'low', 'medium', 'high'
    scalability: str  # 'small', 'medium', 'large'
    interpretability: float  # 0-1 score
    typical_use_cases: List[str]
    pros: List[str]
    cons: List[str]
    references: List[str]


@dataclass
class BenchmarkResult:
    """Results from benchmarking a technique."""
    technique_id: str
    dataset_characteristics: Dict[str, Any]
    performance_scores: Dict[str, float]
    execution_time: float
    memory_usage: float
    timestamp: datetime


class MLTechniqueRepository:
    """Repository of ML techniques and methods."""
    
    def __init__(self):
        """Initialize repository with curated techniques."""
        self.techniques: Dict[str, MLTechnique] = {}
        self.benchmark_history: List[BenchmarkResult] = []
        
        # Initialize with built-in techniques
        self._initialize_techniques()
    
    def _initialize_techniques(self):
        """Initialize repository with curated ML techniques."""
        # Scaling techniques
        self._add_scaling_techniques()
        
        # Encoding techniques
        self._add_encoding_techniques()
        
        # Feature engineering techniques
        self._add_feature_engineering_techniques()
        
        # Feature selection techniques
        self._add_feature_selection_techniques()
        
        # Classification models
        self._add_classification_techniques()
        
        # Regression models
        self._add_regression_techniques()
        
        # Ensemble methods
        self._add_ensemble_techniques()
    
    def _add_scaling_techniques(self):
        """Add data scaling techniques."""
        techniques = [
            MLTechnique(
                technique_id="standard_scaler",
                name="Standard Scaler",
                category=TechniqueCategory.SCALING,
                description="Standardize features by removing mean and scaling to unit variance",
                implementation=StandardScaler,
                default_params={},
                param_ranges={},
                complexity="low",
                scalability="large",
                interpretability=1.0,
                typical_use_cases=["Linear models", "Neural networks", "SVM"],
                pros=["Handles outliers well", "Preserves shape", "Fast"],
                cons=["Assumes normal distribution", "Sensitive to outliers"],
                references=["sklearn.preprocessing.StandardScaler"]
            ),
            MLTechnique(
                technique_id="minmax_scaler",
                name="MinMax Scaler",
                category=TechniqueCategory.SCALING,
                description="Scale features to a given range (default [0,1])",
                implementation=MinMaxScaler,
                default_params={"feature_range": (0, 1)},
                param_ranges={"feature_range": [(0, 1), (-1, 1)]},
                complexity="low",
                scalability="large",
                interpretability=1.0,
                typical_use_cases=["Neural networks", "Image data", "Distance-based algorithms"],
                pros=["Bounded output", "Preserves zero values", "Simple"],
                cons=["Very sensitive to outliers", "Different scale for each feature"],
                references=["sklearn.preprocessing.MinMaxScaler"]
            ),
            MLTechnique(
                technique_id="robust_scaler",
                name="Robust Scaler",
                category=TechniqueCategory.SCALING,
                description="Scale features using statistics robust to outliers",
                implementation=RobustScaler,
                default_params={"quantile_range": (25.0, 75.0)},
                param_ranges={"quantile_range": [(10.0, 90.0), (25.0, 75.0), (5.0, 95.0)]},
                complexity="low",
                scalability="large",
                interpretability=0.9,
                typical_use_cases=["Data with outliers", "Robust models"],
                pros=["Robust to outliers", "Uses median and IQR"],
                cons=["May not handle extreme outliers", "Less common"],
                references=["sklearn.preprocessing.RobustScaler"]
            ),
            MLTechnique(
                technique_id="quantile_transformer",
                name="Quantile Transformer",
                category=TechniqueCategory.SCALING,
                description="Transform features to follow uniform or normal distribution",
                implementation=QuantileTransformer,
                default_params={"n_quantiles": 1000, "output_distribution": "uniform"},
                param_ranges={
                    "n_quantiles": [100, 500, 1000, 2000],
                    "output_distribution": ["uniform", "normal"]
                },
                complexity="medium",
                scalability="medium",
                interpretability=0.7,
                typical_use_cases=["Non-linear transformations", "Ranking problems"],
                pros=["Handles non-linear relationships", "Robust to outliers"],
                cons=["Can distort linear relationships", "Computationally intensive"],
                references=["sklearn.preprocessing.QuantileTransformer"]
            )
        ]
        
        for technique in techniques:
            self.techniques[technique.technique_id] = technique
    
    def _add_encoding_techniques(self):
        """Add categorical encoding techniques."""
        techniques = [
            MLTechnique(
                technique_id="onehot_encoder",
                name="One-Hot Encoder",
                category=TechniqueCategory.ENCODING,
                description="Encode categorical features as one-hot numeric array",
                implementation=OneHotEncoder,
                default_params={"drop": None, "sparse_output": False},
                param_ranges={"drop": [None, "first", "if_binary"]},
                complexity="low",
                scalability="medium",
                interpretability=1.0,
                typical_use_cases=["Low cardinality categoricals", "Linear models"],
                pros=["No ordinal assumption", "Works with all models", "Interpretable"],
                cons=["High dimensionality", "Sparse data", "Memory intensive"],
                references=["sklearn.preprocessing.OneHotEncoder"]
            ),
            MLTechnique(
                technique_id="target_encoder",
                name="Target Encoder",
                category=TechniqueCategory.ENCODING,
                description="Encode categorical features based on target statistics",
                implementation=TargetEncoder,
                default_params={"smooth": "auto"},
                param_ranges={"smooth": ["auto", 0.0, 1.0, 10.0]},
                complexity="medium",
                scalability="large",
                interpretability=0.6,
                typical_use_cases=["High cardinality categoricals", "Tree models"],
                pros=["Compact representation", "Captures target relationship"],
                cons=["Risk of overfitting", "Target leakage", "Less interpretable"],
                references=["category_encoders.TargetEncoder"]
            ),
            MLTechnique(
                technique_id="ordinal_encoder",
                name="Ordinal Encoder",
                category=TechniqueCategory.ENCODING,
                description="Encode categorical features as integer array",
                implementation=OrdinalEncoder,
                default_params={},
                param_ranges={},
                complexity="low",
                scalability="large",
                interpretability=0.8,
                typical_use_cases=["Ordinal categories", "Tree models"],
                pros=["Memory efficient", "Fast", "Preserves order"],
                cons=["Assumes ordinality", "May mislead linear models"],
                references=["sklearn.preprocessing.OrdinalEncoder"]
            )
        ]
        
        for technique in techniques:
            self.techniques[technique.technique_id] = technique
    
    def _add_feature_engineering_techniques(self):
        """Add feature engineering techniques."""
        techniques = [
            MLTechnique(
                technique_id="polynomial_features",
                name="Polynomial Features",
                category=TechniqueCategory.FEATURE_CREATION,
                description="Generate polynomial and interaction features",
                implementation=PolynomialFeatures,
                default_params={"degree": 2, "interaction_only": False, "include_bias": False},
                param_ranges={
                    "degree": [2, 3, 4],
                    "interaction_only": [True, False]
                },
                complexity="medium",
                scalability="small",
                interpretability=0.7,
                typical_use_cases=["Non-linear relationships", "Linear models"],
                pros=["Captures interactions", "Improves linear models"],
                cons=["Exponential feature growth", "Overfitting risk"],
                references=["sklearn.preprocessing.PolynomialFeatures"]
            ),
            MLTechnique(
                technique_id="binning",
                name="K-Bins Discretizer",
                category=TechniqueCategory.FEATURE_CREATION,
                description="Bin continuous data into intervals",
                implementation=KBinsDiscretizer,
                default_params={"n_bins": 5, "encode": "ordinal", "strategy": "quantile"},
                param_ranges={
                    "n_bins": [3, 5, 10, 20],
                    "encode": ["ordinal", "onehot"],
                    "strategy": ["uniform", "quantile", "kmeans"]
                },
                complexity="low",
                scalability="large",
                interpretability=0.9,
                typical_use_cases=["Non-linear patterns", "Decision trees"],
                pros=["Handles non-linearity", "Reduces noise", "Interpretable"],
                cons=["Information loss", "Boundary sensitivity"],
                references=["sklearn.preprocessing.KBinsDiscretizer"]
            )
        ]
        
        for technique in techniques:
            self.techniques[technique.technique_id] = technique
    
    def _add_feature_selection_techniques(self):
        """Add feature selection techniques."""
        techniques = [
            MLTechnique(
                technique_id="selectkbest",
                name="Select K Best",
                category=TechniqueCategory.FEATURE_SELECTION,
                description="Select features based on univariate statistical tests",
                implementation=SelectKBest,
                default_params={"k": 10},
                param_ranges={"k": [5, 10, 20, 50, 100]},
                complexity="low",
                scalability="large",
                interpretability=0.9,
                typical_use_cases=["High dimensional data", "Initial filtering"],
                pros=["Fast", "Simple", "No model needed"],
                cons=["Ignores feature interactions", "Univariate only"],
                references=["sklearn.feature_selection.SelectKBest"]
            ),
            MLTechnique(
                technique_id="rfe",
                name="Recursive Feature Elimination",
                category=TechniqueCategory.FEATURE_SELECTION,
                description="Select features by recursively considering smaller sets",
                implementation=RFE,
                default_params={"n_features_to_select": None, "step": 1},
                param_ranges={
                    "n_features_to_select": [5, 10, 20, 50],
                    "step": [1, 2, 5]
                },
                complexity="high",
                scalability="small",
                interpretability=0.8,
                typical_use_cases=["Model-based selection", "Feature ranking"],
                pros=["Considers interactions", "Model-specific"],
                cons=["Computationally expensive", "Requires good base model"],
                references=["sklearn.feature_selection.RFE"]
            ),
            MLTechnique(
                technique_id="variance_threshold",
                name="Variance Threshold",
                category=TechniqueCategory.FEATURE_SELECTION,
                description="Remove low-variance features",
                implementation=VarianceThreshold,
                default_params={"threshold": 0.0},
                param_ranges={"threshold": [0.0, 0.01, 0.1, 0.5]},
                complexity="low",
                scalability="large",
                interpretability=1.0,
                typical_use_cases=["Remove constants", "Initial filtering"],
                pros=["Very fast", "Simple", "Unsupervised"],
                cons=["Ignores target", "May remove informative features"],
                references=["sklearn.feature_selection.VarianceThreshold"]
            )
        ]
        
        for technique in techniques:
            self.techniques[technique.technique_id] = technique
    
    def _add_classification_techniques(self):
        """Add classification model techniques."""
        techniques = [
            MLTechnique(
                technique_id="random_forest_classifier",
                name="Random Forest Classifier",
                category=TechniqueCategory.CLASSIFICATION,
                description="Ensemble of decision trees with bagging",
                implementation=RandomForestClassifier,
                default_params={"n_estimators": 100, "max_depth": None, "random_state": 42},
                param_ranges={
                    "n_estimators": [50, 100, 200, 500],
                    "max_depth": [5, 10, 20, None],
                    "min_samples_split": [2, 5, 10],
                    "min_samples_leaf": [1, 2, 4]
                },
                complexity="medium",
                scalability="large",
                interpretability=0.6,
                typical_use_cases=["General purpose", "Feature importance", "Non-linear"],
                pros=["Robust", "Handles mixed types", "Feature importance"],
                cons=["Can overfit", "Memory intensive", "Slower prediction"],
                references=["sklearn.ensemble.RandomForestClassifier"]
            ),
            MLTechnique(
                technique_id="logistic_regression",
                name="Logistic Regression",
                category=TechniqueCategory.CLASSIFICATION,
                description="Linear model for classification",
                implementation=LogisticRegression,
                default_params={"penalty": "l2", "C": 1.0, "random_state": 42},
                param_ranges={
                    "penalty": ["l1", "l2", "elasticnet", None],
                    "C": [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
                },
                complexity="low",
                scalability="large",
                interpretability=0.9,
                typical_use_cases=["Binary classification", "Interpretability", "Baseline"],
                pros=["Fast", "Interpretable", "Probabilistic"],
                cons=["Assumes linearity", "Sensitive to scale"],
                references=["sklearn.linear_model.LogisticRegression"]
            )
        ]
        
        # Add XGBoost if available
        if XGB_AVAILABLE:
            techniques.append(
                MLTechnique(
                    technique_id="xgboost_classifier",
                    name="XGBoost Classifier",
                    category=TechniqueCategory.CLASSIFICATION,
                    description="Gradient boosting with regularization",
                    implementation=xgb.XGBClassifier,
                    default_params={"n_estimators": 100, "learning_rate": 0.1, "random_state": 42},
                    param_ranges={
                        "n_estimators": [50, 100, 200, 500],
                        "learning_rate": [0.01, 0.05, 0.1, 0.3],
                        "max_depth": [3, 5, 7, 9],
                        "subsample": [0.6, 0.8, 1.0]
                    },
                    complexity="high",
                    scalability="large",
                    interpretability=0.5,
                    typical_use_cases=["Competitions", "High performance", "Structured data"],
                    pros=["State-of-the-art", "Handles missing", "Regularization"],
                    cons=["Complex tuning", "Overfitting risk", "Less interpretable"],
                    references=["xgboost.XGBClassifier"]
                )
            )
        
        for technique in techniques:
            self.techniques[technique.technique_id] = technique
    
    def _add_regression_techniques(self):
        """Add regression model techniques."""
        techniques = [
            MLTechnique(
                technique_id="ridge_regression",
                name="Ridge Regression",
                category=TechniqueCategory.REGRESSION,
                description="Linear regression with L2 regularization",
                implementation=Ridge,
                default_params={"alpha": 1.0},
                param_ranges={"alpha": [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]},
                complexity="low",
                scalability="large",
                interpretability=0.9,
                typical_use_cases=["Multicollinearity", "Many features", "Stable predictions"],
                pros=["Handles collinearity", "Stable", "Fast"],
                cons=["Assumes linearity", "All features kept"],
                references=["sklearn.linear_model.Ridge"]
            ),
            MLTechnique(
                technique_id="lasso_regression",
                name="Lasso Regression",
                category=TechniqueCategory.REGRESSION,
                description="Linear regression with L1 regularization",
                implementation=Lasso,
                default_params={"alpha": 1.0},
                param_ranges={"alpha": [0.001, 0.01, 0.1, 1.0, 10.0]},
                complexity="low",
                scalability="large",
                interpretability=0.9,
                typical_use_cases=["Feature selection", "Sparse solutions", "Interpretability"],
                pros=["Feature selection", "Interpretable", "Sparse"],
                cons=["Unstable selection", "Biased for large coefficients"],
                references=["sklearn.linear_model.Lasso"]
            )
        ]
        
        for technique in techniques:
            self.techniques[technique.technique_id] = technique
    
    def _add_ensemble_techniques(self):
        """Add ensemble method techniques."""
        # Basic ensemble methods are covered in model sections
        # Additional ensemble strategies can be added here
        pass
    
    def search_techniques(
        self,
        category: Optional[TechniqueCategory] = None,
        problem_type: Optional[str] = None,
        data_characteristics: Optional[Dict[str, Any]] = None
    ) -> List[MLTechnique]:
        """
        Search for suitable techniques based on criteria.
        
        Args:
            category: Specific category to search in
            problem_type: 'classification', 'regression', etc.
            data_characteristics: Dataset properties (size, features, etc.)
            
        Returns:
            List of matching techniques
        """
        results = []
        
        for technique in self.techniques.values():
            # Filter by category
            if category and technique.category != category:
                continue
            
            # Filter by problem type
            if problem_type:
                if problem_type == "classification" and technique.category not in [
                    TechniqueCategory.CLASSIFICATION,
                    TechniqueCategory.SCALING,
                    TechniqueCategory.ENCODING,
                    TechniqueCategory.FEATURE_SELECTION
                ]:
                    continue
                elif problem_type == "regression" and technique.category not in [
                    TechniqueCategory.REGRESSION,
                    TechniqueCategory.SCALING,
                    TechniqueCategory.ENCODING,
                    TechniqueCategory.FEATURE_SELECTION
                ]:
                    continue
            
            # Filter by data characteristics
            if data_characteristics:
                if "n_samples" in data_characteristics:
                    n_samples = data_characteristics["n_samples"]
                    if n_samples > 100000 and technique.scalability == "small":
                        continue
                    elif n_samples < 1000 and technique.complexity == "high":
                        continue
            
            results.append(technique)
        
        return results
    
    def get_technique(self, technique_id: str) -> Optional[MLTechnique]:
        """Get a specific technique by ID."""
        return self.techniques.get(technique_id)
    
    def get_technique_metadata(self, technique_id: str) -> Dict[str, Any]:
        """Get detailed metadata for a technique."""
        technique = self.get_technique(technique_id)
        if not technique:
            return {}
        
        return {
            "name": technique.name,
            "category": technique.category.value,
            "description": technique.description,
            "complexity": technique.complexity,
            "scalability": technique.scalability,
            "interpretability": technique.interpretability,
            "default_params": technique.default_params,
            "param_ranges": technique.param_ranges,
            "use_cases": technique.typical_use_cases,
            "pros": technique.pros,
            "cons": technique.cons
        }
    
    def recommend_techniques(
        self,
        task: str,
        data_stats: Dict[str, Any],
        requirements: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[MLTechnique, float]]:
        """
        Recommend techniques based on task and data.
        
        Args:
            task: Task type (e.g., 'feature_engineering', 'model_selection')
            data_stats: Statistics about the dataset
            requirements: Additional requirements (interpretability, speed, etc.)
            
        Returns:
            List of (technique, score) tuples
        """
        recommendations = []
        
        # Map task to categories
        task_category_map = {
            'preprocessing': [TechniqueCategory.SCALING, TechniqueCategory.ENCODING],
            'feature_engineering': [TechniqueCategory.FEATURE_CREATION, TechniqueCategory.FEATURE_SELECTION],
            'model_selection': [TechniqueCategory.CLASSIFICATION, TechniqueCategory.REGRESSION],
            'dimensionality_reduction': [TechniqueCategory.DIMENSIONALITY_REDUCTION]
        }
        
        categories = task_category_map.get(task, [])
        
        for technique in self.techniques.values():
            if technique.category not in categories:
                continue
            
            # Calculate suitability score
            score = self._calculate_suitability_score(
                technique, data_stats, requirements
            )
            
            recommendations.append((technique, score))
        
        # Sort by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _calculate_suitability_score(
        self,
        technique: MLTechnique,
        data_stats: Dict[str, Any],
        requirements: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate suitability score for a technique."""
        score = 0.5  # Base score
        
        # Adjust based on data size
        n_samples = data_stats.get('n_samples', 1000)
        if n_samples > 10000:
            if technique.scalability == "large":
                score += 0.2
            elif technique.scalability == "small":
                score -= 0.3
        else:
            if technique.complexity == "low":
                score += 0.1
        
        # Adjust based on requirements
        if requirements:
            if 'interpretability' in requirements:
                required_interp = requirements['interpretability']
                score += 0.3 * (1 - abs(technique.interpretability - required_interp))
            
            if 'max_complexity' in requirements:
                if technique.complexity == requirements['max_complexity']:
                    score += 0.2
                elif technique.complexity == "high" and requirements['max_complexity'] == "low":
                    score -= 0.5
        
        # Adjust based on feature count
        n_features = data_stats.get('n_features', 10)
        if technique.category == TechniqueCategory.FEATURE_SELECTION and n_features > 100:
            score += 0.3
        
        return max(0, min(1, score))  # Clamp to [0, 1]


class PerformanceBenchmark:
    """Benchmark ML techniques on specific datasets."""
    
    def __init__(self, repository: MLTechniqueRepository):
        """
        Initialize benchmark system.
        
        Args:
            repository: ML technique repository
        """
        self.repository = repository
        self.benchmark_results: List[BenchmarkResult] = []
    
    def evaluate_technique(
        self,
        technique_id: str,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: int = 5,
        scoring: str = 'accuracy'
    ) -> BenchmarkResult:
        """
        Evaluate a single technique on data.
        
        Args:
            technique_id: ID of technique to evaluate
            X: Feature data
            y: Target data
            cv_folds: Number of cross-validation folds
            scoring: Scoring metric
            
        Returns:
            Benchmark results
        """
        from sklearn.model_selection import cross_val_score
        from sklearn.pipeline import Pipeline
        import psutil
        import time
        
        technique = self.repository.get_technique(technique_id)
        if not technique:
            raise ValueError(f"Technique {technique_id} not found")
        
        # Create instance with default parameters
        if technique.category in [TechniqueCategory.CLASSIFICATION, TechniqueCategory.REGRESSION]:
            model = technique.implementation(**technique.default_params)
        else:
            # For preprocessing techniques, create a simple pipeline
            from sklearn.ensemble import RandomForestClassifier
            preprocessor = technique.implementation(**technique.default_params)
            model = Pipeline([
                ('preprocessor', preprocessor),
                ('classifier', RandomForestClassifier(n_estimators=50, random_state=42))
            ])
        
        # Measure performance
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            scores = cross_val_score(model, X, y, cv=cv_folds, scoring=scoring)
            performance_scores = {
                f"{scoring}_mean": np.mean(scores),
                f"{scoring}_std": np.std(scores),
                f"{scoring}_min": np.min(scores),
                f"{scoring}_max": np.max(scores)
            }
        except Exception as e:
            logger.error(f"Error evaluating {technique_id}: {e}")
            performance_scores = {f"{scoring}_mean": 0.0}
        
        execution_time = time.time() - start_time
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_usage = end_memory - start_memory
        
        # Create benchmark result
        result = BenchmarkResult(
            technique_id=technique_id,
            dataset_characteristics={
                'n_samples': len(X),
                'n_features': X.shape[1],
                'feature_types': X.dtypes.value_counts().to_dict()
            },
            performance_scores=performance_scores,
            execution_time=execution_time,
            memory_usage=memory_usage,
            timestamp=datetime.now()
        )
        
        self.benchmark_results.append(result)
        return result
    
    def compare_techniques(
        self,
        technique_ids: List[str],
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: int = 5,
        scoring: str = 'accuracy'
    ) -> pd.DataFrame:
        """
        Compare multiple techniques on the same dataset.
        
        Args:
            technique_ids: List of technique IDs to compare
            X: Feature data
            y: Target data
            cv_folds: Number of cross-validation folds
            scoring: Scoring metric
            
        Returns:
            DataFrame with comparison results
        """
        results = []
        
        for technique_id in technique_ids:
            result = self.evaluate_technique(technique_id, X, y, cv_folds, scoring)
            
            technique = self.repository.get_technique(technique_id)
            results.append({
                'Technique': technique.name,
                'Category': technique.category.value,
                f'{scoring}_mean': result.performance_scores[f'{scoring}_mean'],
                f'{scoring}_std': result.performance_scores[f'{scoring}_std'],
                'Execution Time (s)': result.execution_time,
                'Memory Usage (MB)': result.memory_usage,
                'Complexity': technique.complexity,
                'Interpretability': technique.interpretability
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values(f'{scoring}_mean', ascending=False)
        
        return df
    
    def find_best_technique(
        self,
        category: TechniqueCategory,
        X: pd.DataFrame,
        y: pd.Series,
        requirements: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, BenchmarkResult]:
        """
        Find the best technique in a category for given data.
        
        Args:
            category: Category to search in
            X: Feature data  
            y: Target data
            requirements: Additional requirements
            
        Returns:
            Tuple of (best_technique_id, benchmark_result)
        """
        # Get candidate techniques
        candidates = self.repository.search_techniques(category=category)
        
        # Filter by requirements
        if requirements:
            if 'max_complexity' in requirements:
                candidates = [
                    t for t in candidates
                    if t.complexity <= requirements['max_complexity']
                ]
            
            if 'min_interpretability' in requirements:
                candidates = [
                    t for t in candidates
                    if t.interpretability >= requirements['min_interpretability']
                ]
        
        # Benchmark all candidates
        best_score = -np.inf
        best_technique = None
        best_result = None
        
        for technique in candidates:
            try:
                result = self.evaluate_technique(technique.technique_id, X, y)
                score = result.performance_scores.get('accuracy_mean', 0)
                
                if score > best_score:
                    best_score = score
                    best_technique = technique.technique_id
                    best_result = result
            except Exception as e:
                logger.warning(f"Failed to evaluate {technique.technique_id}: {e}")
        
        return best_technique, best_result
    
    def export_benchmark_history(self, output_path: Path):
        """Export benchmark history to file."""
        data = []
        
        for result in self.benchmark_results:
            technique = self.repository.get_technique(result.technique_id)
            data.append({
                'timestamp': result.timestamp.isoformat(),
                'technique': technique.name,
                'category': technique.category.value,
                'dataset_samples': result.dataset_characteristics['n_samples'],
                'dataset_features': result.dataset_characteristics['n_features'],
                'performance': result.performance_scores,
                'execution_time': result.execution_time,
                'memory_usage': result.memory_usage
            })
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)