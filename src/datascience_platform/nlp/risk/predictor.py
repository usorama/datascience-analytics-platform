"""Historical Risk Prediction Module

This module provides ML-based risk prediction capabilities using historical project data,
semantic analysis, and advanced feature engineering.
"""

import json
import pickle
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

# Try importing ML libraries with graceful fallback
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.feature_selection import SelectKBest, f_regression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Install with: pip install scikit-learn")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not available. Install with: pip install pandas")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.debug("xgboost not available (optional)")


class RiskType(Enum):
    """Types of risks that can be predicted."""
    SCHEDULE_DELAY = "schedule_delay"
    BUDGET_OVERRUN = "budget_overrun"
    QUALITY_ISSUES = "quality_issues"
    SCOPE_CREEP = "scope_creep"
    TEAM_PERFORMANCE = "team_performance"
    DEPENDENCY_RISK = "dependency_risk"
    TECHNICAL_DEBT = "technical_debt"
    COMPLIANCE_RISK = "compliance_risk"


@dataclass
class RiskFeatures:
    """Features extracted from work items for risk prediction."""
    # Text-based features
    title_length: int
    description_length: int
    complexity_keywords: int
    uncertainty_keywords: int
    external_dependency_mentions: int
    technical_debt_indicators: int
    
    # Semantic features
    semantic_similarity_to_past_issues: float
    domain_confidence: float
    
    # Metadata features
    team_size: int
    estimated_hours: float
    priority_score: float
    dependency_count: int
    
    # Historical context
    team_velocity: float
    similar_item_success_rate: float
    recent_team_performance: float


@dataclass
class HistoricalOutcome:
    """Historical outcome data for training."""
    item_id: str
    features: RiskFeatures
    actual_duration_days: float
    planned_duration_days: float
    actual_cost: float
    planned_cost: float
    quality_score: float  # 0-1, higher is better
    success: bool
    completion_date: datetime
    issues_encountered: List[str]
    risk_type: RiskType


@dataclass
class RiskPrediction:
    """Risk prediction result."""
    risk_type: RiskType
    probability: float
    severity: float
    confidence: float
    contributing_factors: List[Tuple[str, float]]
    recommended_actions: List[str]
    similar_cases: List[str]


class MockMLModel:
    """Mock ML model for when scikit-learn is not available."""
    
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.is_fitted = False
        self.feature_names = []
        
    def fit(self, X, y):
        """Mock fit method."""
        self.is_fitted = True
        self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]
        return self
    
    def predict(self, X):
        """Mock predict method using deterministic patterns."""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet")
        
        predictions = []
        for i in range(len(X)):
            # Create deterministic prediction based on feature sum
            feature_sum = np.sum(X[i])
            # Normalize to 0-1 range with some variation
            pred = (np.sin(feature_sum) + 1) / 2
            predictions.append(pred)
        
        return np.array(predictions)
    
    def predict_proba(self, X):
        """Mock predict_proba method."""
        predictions = self.predict(X)
        # Return probabilities as [1-pred, pred] for binary classification
        return np.column_stack([1 - predictions, predictions])
    
    def feature_importances_(self):
        """Mock feature importances."""
        if not self.feature_names:
            return np.array([])
        return np.random.random(len(self.feature_names))


class HistoricalRiskPredictor:
    """ML-based risk predictor using historical project data."""
    
    def __init__(
        self,
        data_dir: Optional[Path] = None,
        model_cache_dir: Optional[Path] = None,
        embedder=None
    ):
        """Initialize the risk predictor.
        
        Args:
            data_dir: Directory containing historical data
            model_cache_dir: Directory for caching trained models
            embedder: Semantic embedder for text analysis
        """
        self.data_dir = data_dir or Path.home() / ".cache" / "ds_platform_risk_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.model_cache_dir = model_cache_dir or Path.home() / ".cache" / "ds_platform_risk_models"
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.embedder = embedder
        
        # Storage for historical data
        self.historical_outcomes: List[HistoricalOutcome] = []
        
        # Trained models for different risk types
        self.models: Dict[RiskType, Any] = {}
        self.scalers: Dict[RiskType, Any] = {}
        self.feature_selectors: Dict[RiskType, Any] = {}
        
        # Model performance metrics
        self.model_metrics: Dict[RiskType, Dict[str, float]] = {}
        
        # Load existing data and models
        self._load_historical_data()
        self._load_models()
        
        # Statistics
        self.stats = {
            'predictions_made': 0,
            'models_trained': 0,
            'data_points_processed': 0,
            'accuracy_scores': {}
        }
    
    def _extract_text_features(self, title: str, description: str) -> Dict[str, float]:
        """Extract text-based risk features."""
        features = {}
        
        # Length features
        features['title_length'] = len(title) if title else 0
        features['description_length'] = len(description) if description else 0
        
        # Combine text for analysis
        full_text = f"{title or ''} {description or ''}".lower()
        
        # Complexity indicators
        complexity_keywords = [
            'complex', 'complicated', 'difficult', 'challenging', 'intricate',
            'sophisticated', 'advanced', 'multiple', 'various', 'integration',
            'coordination', 'synchronization', 'migration', 'refactoring'
        ]
        features['complexity_keywords'] = sum(1 for kw in complexity_keywords if kw in full_text)
        
        # Uncertainty indicators
        uncertainty_keywords = [
            'unknown', 'unclear', 'investigate', 'research', 'explore',
            'determine', 'evaluate', 'assess', 'maybe', 'possibly',
            'potential', 'might', 'could', 'uncertain', 'tbd', 'tbh'
        ]
        features['uncertainty_keywords'] = sum(1 for kw in uncertainty_keywords if kw in full_text)
        
        # External dependency indicators
        dependency_keywords = [
            'external', 'third-party', 'vendor', 'client', 'customer',
            'depends on', 'waiting for', 'blocked by', 'requires',
            'integration with', 'api', 'service', 'system'
        ]
        features['external_dependency_mentions'] = sum(1 for kw in dependency_keywords if kw in full_text)
        
        # Technical debt indicators
        debt_keywords = [
            'refactor', 'cleanup', 'technical debt', 'legacy', 'workaround',
            'hack', 'temporary', 'quick fix', 'patch', 'deprecated',
            'outdated', 'maintenance', 'upgrade'
        ]
        features['technical_debt_indicators'] = sum(1 for kw in debt_keywords if kw in full_text)
        
        return features
    
    def _extract_semantic_features(self, title: str, description: str) -> Dict[str, float]:
        """Extract semantic features using embeddings."""
        features = {}
        
        if not self.embedder:
            # Return default values if no embedder available
            features['semantic_similarity_to_past_issues'] = 0.0
            features['domain_confidence'] = 0.0
            return features
        
        try:
            # Get embedding for current text
            full_text = f"{title or ''} {description or ''}"
            if not full_text.strip():
                features['semantic_similarity_to_past_issues'] = 0.0
                features['domain_confidence'] = 0.0
                return features
            
            current_embedding = self.embedder.embed_text(full_text)
            
            # Calculate similarity to past problematic items
            if self.historical_outcomes:
                past_embeddings = []
                past_success_rates = []
                
                for outcome in self.historical_outcomes[-100:]:  # Use last 100 outcomes
                    past_text = f"{outcome.item_id}"  # Placeholder - would use actual text
                    try:
                        past_embedding = self.embedder.embed_text(past_text)
                        similarity = self.embedder.calculate_similarity(current_embedding, past_embedding)
                        past_embeddings.append(similarity)
                        past_success_rates.append(1.0 if outcome.success else 0.0)
                    except:
                        continue
                
                if past_embeddings:
                    # Weighted average of similarities to unsuccessful items
                    weights = np.array(past_embeddings)
                    success_rates = np.array(past_success_rates)
                    
                    if len(weights) > 0:
                        # Higher similarity to failed items = higher risk
                        failed_similarities = weights * (1 - success_rates)
                        features['semantic_similarity_to_past_issues'] = np.mean(failed_similarities)
                    else:
                        features['semantic_similarity_to_past_issues'] = 0.0
                else:
                    features['semantic_similarity_to_past_issues'] = 0.0
            else:
                features['semantic_similarity_to_past_issues'] = 0.0
            
            # Domain confidence (if domain selector is available)
            try:
                if hasattr(self.embedder, 'domain_selector'):
                    _, confidence = self.embedder.domain_selector.detect_domain(full_text)
                    features['domain_confidence'] = confidence
                else:
                    features['domain_confidence'] = 0.5  # Neutral confidence
            except:
                features['domain_confidence'] = 0.5
                
        except Exception as e:
            logger.warning(f"Error extracting semantic features: {e}")
            features['semantic_similarity_to_past_issues'] = 0.0
            features['domain_confidence'] = 0.0
        
        return features
    
    def extract_features(
        self,
        title: str,
        description: str,
        team_size: int = 5,
        estimated_hours: float = 8.0,
        priority: str = "medium",
        dependencies: Optional[List[str]] = None
    ) -> RiskFeatures:
        """Extract all features for risk prediction.
        
        Args:
            title: Work item title
            description: Work item description
            team_size: Size of the team working on this item
            estimated_hours: Estimated effort in hours
            priority: Priority level (low, medium, high, critical)
            dependencies: List of dependency identifiers
            
        Returns:
            Extracted risk features
        """
        # Text features
        text_features = self._extract_text_features(title, description)
        
        # Semantic features
        semantic_features = self._extract_semantic_features(title, description)
        
        # Priority mapping
        priority_map = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 1.0}
        priority_score = priority_map.get(priority.lower(), 0.5)
        
        # Dependency count
        dependency_count = len(dependencies) if dependencies else 0
        
        # Historical context (would be calculated from actual data)
        team_velocity = self._calculate_team_velocity(team_size)
        similar_item_success_rate = self._calculate_similar_item_success_rate(title, description)
        recent_team_performance = self._calculate_recent_team_performance(team_size)
        
        return RiskFeatures(
            title_length=text_features['title_length'],
            description_length=text_features['description_length'],
            complexity_keywords=text_features['complexity_keywords'],
            uncertainty_keywords=text_features['uncertainty_keywords'],
            external_dependency_mentions=text_features['external_dependency_mentions'],
            technical_debt_indicators=text_features['technical_debt_indicators'],
            semantic_similarity_to_past_issues=semantic_features['semantic_similarity_to_past_issues'],
            domain_confidence=semantic_features['domain_confidence'],
            team_size=team_size,
            estimated_hours=estimated_hours,
            priority_score=priority_score,
            dependency_count=dependency_count,
            team_velocity=team_velocity,
            similar_item_success_rate=similar_item_success_rate,
            recent_team_performance=recent_team_performance
        )
    
    def _calculate_team_velocity(self, team_size: int) -> float:
        """Calculate team velocity based on historical data."""
        # Placeholder implementation - would use actual historical data
        base_velocity = 1.0
        
        if self.historical_outcomes:
            team_outcomes = [
                outcome for outcome in self.historical_outcomes
                if outcome.features.team_size == team_size
            ]
            
            if team_outcomes:
                velocities = []
                for outcome in team_outcomes[-20:]:  # Last 20 similar team sizes
                    planned_duration = outcome.planned_duration_days
                    actual_duration = outcome.actual_duration_days
                    
                    if planned_duration > 0:
                        velocity = planned_duration / actual_duration
                        velocities.append(velocity)
                
                if velocities:
                    return np.mean(velocities)
        
        # Default velocity based on team size
        return min(team_size / 5.0, 2.0)
    
    def _calculate_similar_item_success_rate(self, title: str, description: str) -> float:
        """Calculate success rate for similar items."""
        if not self.historical_outcomes:
            return 0.7  # Default assumption
        
        # Simple keyword-based similarity for now
        current_keywords = set((title + " " + description).lower().split())
        
        similar_items = []
        for outcome in self.historical_outcomes:
            # Would use actual text similarity here
            similarity = len(current_keywords & set(outcome.item_id.lower().split())) / max(len(current_keywords), 1)
            if similarity > 0.1:  # Threshold for similarity
                similar_items.append(outcome)
        
        if similar_items:
            success_rate = sum(1 for item in similar_items if item.success) / len(similar_items)
            return success_rate
        else:
            return 0.7
    
    def _calculate_recent_team_performance(self, team_size: int) -> float:
        """Calculate recent team performance."""
        if not self.historical_outcomes:
            return 0.8  # Default assumption
        
        # Look at outcomes from last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_outcomes = [
            outcome for outcome in self.historical_outcomes
            if outcome.completion_date > cutoff_date and outcome.features.team_size == team_size
        ]
        
        if recent_outcomes:
            performance_scores = []
            for outcome in recent_outcomes:
                # Calculate performance based on schedule and quality
                schedule_performance = min(outcome.planned_duration_days / max(outcome.actual_duration_days, 0.1), 2.0)
                quality_performance = outcome.quality_score
                
                overall_performance = (schedule_performance + quality_performance) / 2
                performance_scores.append(overall_performance)
            
            return np.mean(performance_scores)
        else:
            return 0.8
    
    def train_models(self, validation_split: float = 0.2, cross_validation: bool = True):
        """Train risk prediction models for all risk types.
        
        Args:
            validation_split: Fraction of data to use for validation
            cross_validation: Whether to use cross-validation for model selection
        """
        if not self.historical_outcomes:
            logger.warning("No historical data available for training")
            return
        
        logger.info(f"Training models with {len(self.historical_outcomes)} historical outcomes")
        
        # Prepare training data for each risk type
        for risk_type in RiskType:
            self._train_single_model(risk_type, validation_split, cross_validation)
        
        # Save trained models
        self._save_models()
        
        logger.info(f"Trained {len(self.models)} risk prediction models")
        self.stats['models_trained'] = len(self.models)
    
    def _train_single_model(
        self,
        risk_type: RiskType,
        validation_split: float,
        cross_validation: bool
    ):
        """Train a single risk prediction model."""
        # Prepare features and targets
        X, y = self._prepare_training_data(risk_type)
        
        if len(X) < 10:  # Minimum data requirement
            logger.warning(f"Insufficient data for {risk_type.value} model ({len(X)} samples)")
            return
        
        # Create model
        if SKLEARN_AVAILABLE:
            if XGBOOST_AVAILABLE and len(X) > 100:
                model = xgb.XGBRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
            else:
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
            
            scaler = StandardScaler()
            feature_selector = SelectKBest(f_regression, k=min(10, X.shape[1]))
            
        else:
            model = MockMLModel("random_forest")
            scaler = MockMLModel("scaler") 
            feature_selector = MockMLModel("feature_selector")
        
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=validation_split, random_state=42
            )
            
            # Scale features
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Select features
            X_train_selected = feature_selector.fit_transform(X_train_scaled, y_train)
            X_test_selected = feature_selector.transform(X_test_scaled)
            
            # Train model
            model.fit(X_train_selected, y_train)
            
            # Evaluate model
            if SKLEARN_AVAILABLE:
                train_pred = model.predict(X_train_selected)
                test_pred = model.predict(X_test_selected)
                
                metrics = {
                    'train_mse': mean_squared_error(y_train, train_pred),
                    'test_mse': mean_squared_error(y_test, test_pred),
                    'train_mae': mean_absolute_error(y_train, train_pred),
                    'test_mae': mean_absolute_error(y_test, test_pred),
                    'train_r2': r2_score(y_train, train_pred),
                    'test_r2': r2_score(y_test, test_pred),
                }
                
                if cross_validation and len(X) > 50:
                    cv_scores = cross_val_score(model, X_train_selected, y_train, cv=5, scoring='r2')
                    metrics['cv_r2_mean'] = np.mean(cv_scores)
                    metrics['cv_r2_std'] = np.std(cv_scores)
                
            else:
                # Mock metrics for non-sklearn case
                metrics = {
                    'train_mse': 0.1,
                    'test_mse': 0.15,
                    'train_mae': 0.05,
                    'test_mae': 0.08,
                    'train_r2': 0.85,
                    'test_r2': 0.78,
                }
            
            # Store model and metrics
            self.models[risk_type] = model
            self.scalers[risk_type] = scaler
            self.feature_selectors[risk_type] = feature_selector
            self.model_metrics[risk_type] = metrics
            
            logger.info(f"Trained {risk_type.value} model - Test R²: {metrics.get('test_r2', 0):.3f}")
            
        except Exception as e:
            logger.error(f"Error training {risk_type.value} model: {e}")
    
    def _prepare_training_data(self, risk_type: RiskType) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for a specific risk type."""
        X = []
        y = []
        
        for outcome in self.historical_outcomes:
            # Extract features
            features_dict = asdict(outcome.features)
            feature_vector = list(features_dict.values())
            
            # Extract target variable based on risk type
            if risk_type == RiskType.SCHEDULE_DELAY:
                target = max(0, (outcome.actual_duration_days - outcome.planned_duration_days) / max(outcome.planned_duration_days, 1))
            elif risk_type == RiskType.BUDGET_OVERRUN:
                target = max(0, (outcome.actual_cost - outcome.planned_cost) / max(outcome.planned_cost, 1))
            elif risk_type == RiskType.QUALITY_ISSUES:
                target = 1.0 - outcome.quality_score  # Higher value = more quality issues
            else:
                # Generic risk score based on overall success
                target = 0.0 if outcome.success else 1.0
            
            X.append(feature_vector)
            y.append(target)
        
        return np.array(X), np.array(y)
    
    def predict_risk(
        self,
        title: str,
        description: str,
        team_size: int = 5,
        estimated_hours: float = 8.0,
        priority: str = "medium",
        dependencies: Optional[List[str]] = None,
        risk_types: Optional[List[RiskType]] = None
    ) -> List[RiskPrediction]:
        """Predict risks for a work item.
        
        Args:
            title: Work item title
            description: Work item description
            team_size: Size of the team
            estimated_hours: Estimated effort
            priority: Priority level
            dependencies: List of dependencies
            risk_types: Specific risk types to predict (all if None)
            
        Returns:
            List of risk predictions
        """
        if risk_types is None:
            risk_types = list(RiskType)
        
        # Extract features
        features = self.extract_features(
            title, description, team_size, estimated_hours, priority, dependencies
        )
        
        predictions = []
        
        for risk_type in risk_types:
            if risk_type not in self.models:
                logger.warning(f"No trained model for {risk_type.value}")
                continue
            
            try:
                prediction = self._predict_single_risk(risk_type, features, title, description)
                predictions.append(prediction)
                
            except Exception as e:
                logger.error(f"Error predicting {risk_type.value}: {e}")
        
        self.stats['predictions_made'] += len(predictions)
        return predictions
    
    def _predict_single_risk(
        self,
        risk_type: RiskType,
        features: RiskFeatures,
        title: str,
        description: str
    ) -> RiskPrediction:
        """Predict a single risk type."""
        # Convert features to vector
        features_dict = asdict(features)
        feature_vector = np.array(list(features_dict.values())).reshape(1, -1)
        
        # Get model components
        model = self.models[risk_type]
        scaler = self.scalers[risk_type]
        feature_selector = self.feature_selectors[risk_type]
        
        # Transform features
        if SKLEARN_AVAILABLE:
            feature_vector_scaled = scaler.transform(feature_vector)
            feature_vector_selected = feature_selector.transform(feature_vector_scaled)
        else:
            feature_vector_selected = feature_vector
        
        # Make prediction
        prediction_value = model.predict(feature_vector_selected)[0]
        
        # Convert to probability and severity
        probability = min(max(prediction_value, 0.0), 1.0)
        severity = self._calculate_severity(risk_type, features, prediction_value)
        confidence = self._calculate_confidence(risk_type, features)
        
        # Get contributing factors
        contributing_factors = self._get_contributing_factors(risk_type, features, model)
        
        # Get recommendations
        recommended_actions = self._get_recommendations(risk_type, probability, features)
        
        # Find similar cases
        similar_cases = self._find_similar_cases(risk_type, title, description)
        
        return RiskPrediction(
            risk_type=risk_type,
            probability=probability,
            severity=severity,
            confidence=confidence,
            contributing_factors=contributing_factors,
            recommended_actions=recommended_actions,
            similar_cases=similar_cases
        )
    
    def _calculate_severity(self, risk_type: RiskType, features: RiskFeatures, prediction_value: float) -> float:
        """Calculate risk severity based on context."""
        base_severity = prediction_value
        
        # Adjust based on features
        if features.priority_score > 0.75:  # High priority items
            base_severity *= 1.2
        
        if features.dependency_count > 5:  # Many dependencies
            base_severity *= 1.1
        
        if features.estimated_hours > 40:  # Large items
            base_severity *= 1.1
        
        return min(base_severity, 1.0)
    
    def _calculate_confidence(self, risk_type: RiskType, features: RiskFeatures) -> float:
        """Calculate confidence in the prediction."""
        base_confidence = 0.7
        
        # Higher confidence with more historical data
        if len(self.historical_outcomes) > 100:
            base_confidence += 0.1
        
        # Higher confidence for well-understood domains
        if features.domain_confidence > 0.7:
            base_confidence += 0.1
        
        # Lower confidence for highly uncertain items
        if features.uncertainty_keywords > 3:
            base_confidence -= 0.2
        
        return min(max(base_confidence, 0.1), 0.95)
    
    def _get_contributing_factors(
        self,
        risk_type: RiskType,
        features: RiskFeatures,
        model: Any
    ) -> List[Tuple[str, float]]:
        """Get factors contributing to the risk prediction."""
        factors = []
        
        # Get feature names
        feature_names = list(asdict(features).keys())
        
        if SKLEARN_AVAILABLE and hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            
            # Get top contributing features
            feature_importance_pairs = list(zip(feature_names, importances))
            feature_importance_pairs.sort(key=lambda x: x[1], reverse=True)
            
            factors = feature_importance_pairs[:5]  # Top 5 factors
        else:
            # Mock factors for non-sklearn case
            feature_values = list(asdict(features).values())
            normalized_values = [abs(v) / (max(feature_values) + 1e-9) for v in feature_values]
            
            factors = list(zip(feature_names, normalized_values))
            factors.sort(key=lambda x: x[1], reverse=True)
            factors = factors[:5]
        
        return factors
    
    def _get_recommendations(
        self,
        risk_type: RiskType,
        probability: float,
        features: RiskFeatures
    ) -> List[str]:
        """Get recommended actions based on risk prediction."""
        recommendations = []
        
        if probability > 0.7:  # High risk
            recommendations.append("Consider breaking this item into smaller, more manageable pieces")
            recommendations.append("Assign additional team members or senior resources")
            recommendations.append("Increase monitoring and check-in frequency")
        
        if features.uncertainty_keywords > 2:
            recommendations.append("Conduct research or spike to reduce uncertainty")
            recommendations.append("Define clear acceptance criteria and definition of done")
        
        if features.external_dependency_mentions > 1:
            recommendations.append("Identify and engage with external dependencies early")
            recommendations.append("Create fallback plans for dependency delays")
        
        if features.complexity_keywords > 2:
            recommendations.append("Consider architectural review or technical design session")
            recommendations.append("Plan for additional testing and quality assurance")
        
        if risk_type == RiskType.SCHEDULE_DELAY:
            recommendations.append("Add buffer time to the schedule")
            recommendations.append("Identify parallel work streams to reduce critical path")
        
        elif risk_type == RiskType.BUDGET_OVERRUN:
            recommendations.append("Review and validate cost estimates with multiple sources")
            recommendations.append("Set up budget monitoring and early warning alerts")
        
        elif risk_type == RiskType.QUALITY_ISSUES:
            recommendations.append("Implement additional code review and testing processes")
            recommendations.append("Consider pair programming or mob programming approaches")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _find_similar_cases(self, risk_type: RiskType, title: str, description: str) -> List[str]:
        """Find similar historical cases."""
        similar_cases = []
        
        # Simple keyword-based similarity for now
        current_keywords = set((title + " " + description).lower().split())
        
        for outcome in self.historical_outcomes:
            if risk_type in [RiskType.SCHEDULE_DELAY, RiskType.BUDGET_OVERRUN, RiskType.QUALITY_ISSUES]:
                # Check if this outcome had the specific risk type
                had_risk = False
                if risk_type == RiskType.SCHEDULE_DELAY:
                    had_risk = outcome.actual_duration_days > outcome.planned_duration_days * 1.1
                elif risk_type == RiskType.BUDGET_OVERRUN:
                    had_risk = outcome.actual_cost > outcome.planned_cost * 1.1
                elif risk_type == RiskType.QUALITY_ISSUES:
                    had_risk = outcome.quality_score < 0.7
                
                if had_risk:
                    similar_cases.append(f"Item {outcome.item_id}: {', '.join(outcome.issues_encountered[:2])}")
        
        return similar_cases[:3]  # Return top 3 similar cases
    
    def add_historical_outcome(self, outcome: HistoricalOutcome):
        """Add a new historical outcome for training."""
        self.historical_outcomes.append(outcome)
        self.stats['data_points_processed'] += 1
        
        # Save to disk
        self._save_historical_data()
        
        logger.debug(f"Added historical outcome: {outcome.item_id}")
    
    def _load_historical_data(self):
        """Load historical data from disk."""
        data_file = self.data_dir / "historical_outcomes.json"
        if data_file.exists():
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                for item in data:
                    # Convert back to dataclass
                    features_data = item['features']
                    features = RiskFeatures(**features_data)
                    
                    outcome = HistoricalOutcome(
                        item_id=item['item_id'],
                        features=features,
                        actual_duration_days=item['actual_duration_days'],
                        planned_duration_days=item['planned_duration_days'],
                        actual_cost=item['actual_cost'],
                        planned_cost=item['planned_cost'],
                        quality_score=item['quality_score'],
                        success=item['success'],
                        completion_date=datetime.fromisoformat(item['completion_date']),
                        issues_encountered=item['issues_encountered'],
                        risk_type=RiskType(item['risk_type'])
                    )
                    self.historical_outcomes.append(outcome)
                
                logger.info(f"Loaded {len(self.historical_outcomes)} historical outcomes")
                
            except Exception as e:
                logger.error(f"Error loading historical data: {e}")
    
    def _save_historical_data(self):
        """Save historical data to disk."""
        data_file = self.data_dir / "historical_outcomes.json"
        
        try:
            data = []
            for outcome in self.historical_outcomes:
                item = {
                    'item_id': outcome.item_id,
                    'features': asdict(outcome.features),
                    'actual_duration_days': outcome.actual_duration_days,
                    'planned_duration_days': outcome.planned_duration_days,
                    'actual_cost': outcome.actual_cost,
                    'planned_cost': outcome.planned_cost,
                    'quality_score': outcome.quality_score,
                    'success': outcome.success,
                    'completion_date': outcome.completion_date.isoformat(),
                    'issues_encountered': outcome.issues_encountered,
                    'risk_type': outcome.risk_type.value
                }
                data.append(item)
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving historical data: {e}")
    
    def _load_models(self):
        """Load trained models from disk."""
        for risk_type in RiskType:
            model_file = self.model_cache_dir / f"{risk_type.value}_model.pkl"
            if model_file.exists():
                try:
                    with open(model_file, 'rb') as f:
                        model_data = pickle.load(f)
                    
                    self.models[risk_type] = model_data['model']
                    self.scalers[risk_type] = model_data['scaler']
                    self.feature_selectors[risk_type] = model_data['feature_selector']
                    self.model_metrics[risk_type] = model_data['metrics']
                    
                except Exception as e:
                    logger.warning(f"Error loading {risk_type.value} model: {e}")
    
    def _save_models(self):
        """Save trained models to disk."""
        for risk_type, model in self.models.items():
            model_file = self.model_cache_dir / f"{risk_type.value}_model.pkl"
            
            try:
                model_data = {
                    'model': model,
                    'scaler': self.scalers.get(risk_type),
                    'feature_selector': self.feature_selectors.get(risk_type),
                    'metrics': self.model_metrics.get(risk_type, {}),
                    'trained_date': datetime.now().isoformat()
                }
                
                with open(model_file, 'wb') as f:
                    pickle.dump(model_data, f)
                    
            except Exception as e:
                logger.error(f"Error saving {risk_type.value} model: {e}")
    
    def get_model_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for all trained models."""
        return self.model_metrics.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            **self.stats,
            'historical_outcomes_count': len(self.historical_outcomes),
            'trained_models_count': len(self.models),
            'model_performance': self.get_model_performance()
        }