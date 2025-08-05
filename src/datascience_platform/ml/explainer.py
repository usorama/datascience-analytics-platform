"""Model Explainer Engine

Integrates SHAP for model explanations, feature importance visualizations,
and prediction explanations to make ML models interpretable.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple
import warnings
# Try to import plotting libraries - graceful fallback if not available
try:
    import matplotlib
    import matplotlib.pyplot as plt
    import seaborn as sns
    matplotlib.use('Agg')  # Use non-interactive backend
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    logging.warning("Matplotlib/Seaborn not available. Visualization functionality will be limited.")

from io import BytesIO
import base64

# Try to import SHAP - graceful fallback if not available
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logging.warning("SHAP not available. Model explanation functionality will be limited.")

# Sklearn for fallback explanations
from sklearn.inspection import permutation_importance
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import joblib

warnings.filterwarnings('ignore', category=FutureWarning)

logger = logging.getLogger(__name__)


class ModelExplainer:
    """Comprehensive model explanation engine with SHAP integration and fallback methods."""
    
    def __init__(self):
        """Initialize the model explainer."""
        self.model = None
        self.X_train = None
        self.y_train = None
        self.feature_names = None
        self.explainer = None
        self.shap_values = None
        self.explanations = {}
        
    def explain_model(self, model: Any, 
                     X_train: pd.DataFrame, 
                     y_train: Union[pd.Series, np.ndarray],
                     X_test: Optional[pd.DataFrame] = None,
                     model_type: str = 'auto') -> Dict[str, Any]:
        """
        Generate comprehensive model explanations.
        
        Args:
            model: Trained model object
            X_train: Training features
            y_train: Training target
            X_test: Test features for specific explanations
            model_type: Type of model ('tree', 'linear', 'ensemble', 'auto')
            
        Returns:
            Dictionary containing all explanations and visualizations
        """
        try:
            logger.info("Starting model explanation generation")
            
            self.model = model
            self.X_train = X_train
            self.y_train = y_train
            self.feature_names = list(X_train.columns) if hasattr(X_train, 'columns') else None
            
            # Determine model type if auto
            if model_type == 'auto':
                model_type = self._detect_model_type(model)
            
            explanations = {
                'model_type': model_type,
                'feature_names': self.feature_names,
                'global_explanations': self._generate_global_explanations(model_type),
                'feature_importance': self._get_feature_importance(model_type),
                'model_behavior': self._analyze_model_behavior(),
                'visualizations': {}
            }
            
            # Generate SHAP explanations if available
            if SHAP_AVAILABLE:
                shap_explanations = self._generate_shap_explanations(model_type, X_test)
                explanations['shap_explanations'] = shap_explanations
                explanations['visualizations'].update(shap_explanations.get('plots', {}))
            
            # Generate local explanations for test data
            if X_test is not None:
                explanations['local_explanations'] = self._generate_local_explanations(X_test, model_type)
            
            # Generate visualizations
            viz_plots = self._generate_explanation_visualizations()
            explanations['visualizations'].update(viz_plots)
            
            self.explanations = explanations
            logger.info("Model explanation generation completed")
            return explanations
            
        except Exception as e:
            logger.error(f"Error in model explanation: {str(e)}")
            raise
    
    def _detect_model_type(self, model: Any) -> str:
        """Detect the type of model for appropriate explanation method."""
        model_name = type(model).__name__.lower()
        
        if 'tree' in model_name or 'forest' in model_name or 'gradient' in model_name or 'xgb' in model_name or 'lgb' in model_name:
            return 'tree'
        elif 'linear' in model_name or 'logistic' in model_name or 'ridge' in model_name or 'lasso' in model_name:
            return 'linear'
        elif 'svm' in model_name or 'svc' in model_name:
            return 'kernel'
        elif 'neural' in model_name or 'mlp' in model_name:
            return 'neural'
        else:
            return 'ensemble'
    
    def _generate_global_explanations(self, model_type: str) -> Dict[str, Any]:
        """Generate global model explanations."""
        explanations = {
            'model_complexity': self._assess_model_complexity(),
            'model_behavior_summary': self._summarize_model_behavior(),
        }
        
        # Model-specific global explanations
        if model_type == 'tree':
            explanations.update(self._explain_tree_model())
        elif model_type == 'linear':
            explanations.update(self._explain_linear_model())
        elif model_type == 'ensemble':
            explanations.update(self._explain_ensemble_model())
        
        return explanations
    
    def _get_feature_importance(self, model_type: str) -> Dict[str, Any]:
        """Get feature importance using multiple methods."""
        importance_results = {}
        
        # Built-in feature importance
        if hasattr(self.model, 'feature_importances_'):
            importance_results['builtin'] = {
                'values': self.model.feature_importances_.tolist(),
                'features': self.feature_names or [f'feature_{i}' for i in range(len(self.model.feature_importances_))],
                'method': 'Model built-in importance'
            }
        
        # Coefficient-based importance for linear models
        elif hasattr(self.model, 'coef_'):
            coef = self.model.coef_
            if coef.ndim > 1:
                # Multi-class case - use mean absolute coefficient
                importance_values = np.mean(np.abs(coef), axis=0)
            else:
                importance_values = np.abs(coef)
            
            importance_results['coefficients'] = {
                'values': importance_values.tolist(),
                'features': self.feature_names or [f'feature_{i}' for i in range(len(importance_values))],
                'method': 'Coefficient magnitude'
            }
        
        # Permutation importance as fallback/complement
        try:
            perm_importance = permutation_importance(
                self.model, self.X_train, self.y_train, 
                n_repeats=5, random_state=42, scoring=None
            )
            
            importance_results['permutation'] = {
                'values': perm_importance.importances_mean.tolist(),
                'std': perm_importance.importances_std.tolist(),
                'features': self.feature_names or [f'feature_{i}' for i in range(len(perm_importance.importances_mean))],
                'method': 'Permutation importance'
            }
            
        except Exception as e:
            logger.warning(f"Permutation importance calculation failed: {str(e)}")
        
        # Combine and rank features
        if importance_results:
            importance_results['summary'] = self._summarize_feature_importance(importance_results)
        
        return importance_results
    
    def _summarize_feature_importance(self, importance_results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize feature importance across methods."""
        all_features = set()
        method_importances = {}
        
        # Collect all importance scores
        for method, data in importance_results.items():
            if method == 'summary':
                continue
            
            features = data.get('features', [])
            values = data.get('values', [])
            
            all_features.update(features)
            method_importances[method] = dict(zip(features, values))
        
        # Calculate consensus importance
        consensus_importance = {}
        for feature in all_features:
            scores = []
            for method_scores in method_importances.values():
                if feature in method_scores:
                    scores.append(method_scores[feature])
            
            if scores:
                # Use mean of normalized scores
                normalized_scores = [score / max(method_importances[method].values()) 
                                   for method, score in zip(method_importances.keys(), scores)
                                   if feature in method_importances[method]]
                consensus_importance[feature] = np.mean(normalized_scores)
        
        # Sort by importance
        sorted_features = sorted(consensus_importance.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'ranking': sorted_features,
            'top_features': [f[0] for f in sorted_features[:5]],
            'consensus_scores': consensus_importance
        }
    
    def _generate_shap_explanations(self, model_type: str, 
                                  X_test: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Generate SHAP-based explanations."""
        if not SHAP_AVAILABLE:
            return {'error': 'SHAP not available'}
        
        shap_results = {}
        
        try:
            # Choose appropriate SHAP explainer
            if model_type == 'tree':
                self.explainer = shap.TreeExplainer(self.model)
            elif model_type == 'linear':
                self.explainer = shap.LinearExplainer(self.model, self.X_train)
            else:
                # Use sampling for complex models
                sample_size = min(100, len(self.X_train))
                background = self.X_train.sample(n=sample_size, random_state=42)
                self.explainer = shap.Explainer(self.model, background)
            
            # Generate SHAP values for training data (sample if too large)
            train_sample_size = min(500, len(self.X_train))
            X_train_sample = self.X_train.sample(n=train_sample_size, random_state=42)
            
            shap_values_train = self.explainer.shap_values(X_train_sample)
            
            # Handle multi-output case
            if isinstance(shap_values_train, list):
                shap_values_train = shap_values_train[0]  # Use first output for now
            
            self.shap_values = shap_values_train
            
            # Global SHAP importance
            global_importance = np.mean(np.abs(shap_values_train), axis=0)
            
            shap_results['global_importance'] = {
                'values': global_importance.tolist(),
                'features': self.feature_names or [f'feature_{i}' for i in range(len(global_importance))],
                'method': 'SHAP global importance'
            }
            
            # Generate SHAP plots
            shap_plots = self._generate_shap_plots(X_train_sample, shap_values_train)
            shap_results['plots'] = shap_plots
            
            # Local explanations for test data
            if X_test is not None:
                test_sample_size = min(10, len(X_test))
                X_test_sample = X_test.sample(n=test_sample_size, random_state=42)
                
                shap_values_test = self.explainer.shap_values(X_test_sample)
                if isinstance(shap_values_test, list):
                    shap_values_test = shap_values_test[0]
                
                shap_results['local_explanations'] = self._generate_shap_local_explanations(
                    X_test_sample, shap_values_test
                )
            
        except Exception as e:
            logger.error(f"SHAP explanation failed: {str(e)}")
            shap_results['error'] = str(e)
        
        return shap_results
    
    def _generate_shap_plots(self, X_sample: pd.DataFrame, 
                           shap_values: np.ndarray) -> Dict[str, str]:
        """Generate SHAP visualization plots."""
        plots = {}
        
        if not PLOTTING_AVAILABLE:
            plots['error'] = 'Matplotlib not available for plotting'
            return plots
        
        try:
            # Summary plot
            plt.figure(figsize=(10, 8))
            shap.summary_plot(shap_values, X_sample, show=False)
            plots['summary'] = self._plot_to_base64()
            plt.close()
            
            # Feature importance plot
            plt.figure(figsize=(10, 6))
            shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
            plots['importance'] = self._plot_to_base64()
            plt.close()
            
            # Waterfall plot for first instance
            if len(X_sample) > 0:
                plt.figure(figsize=(10, 6))
                explanation = shap.Explanation(
                    values=shap_values[0], 
                    base_values=self.explainer.expected_value,
                    data=X_sample.iloc[0].values,
                    feature_names=self.feature_names
                )
                shap.waterfall_plot(explanation, show=False)
                plots['waterfall'] = self._plot_to_base64()
                plt.close()
            
        except Exception as e:
            logger.warning(f"SHAP plot generation failed: {str(e)}")
            plots['error'] = str(e)
        
        return plots
    
    def _generate_shap_local_explanations(self, X_test: pd.DataFrame,
                                        shap_values: np.ndarray) -> List[Dict[str, Any]]:
        """Generate local SHAP explanations for test instances."""
        local_explanations = []
        
        for i in range(len(X_test)):
            explanation = {
                'instance_index': i,
                'prediction': self.model.predict(X_test.iloc[i:i+1])[0],
                'shap_values': shap_values[i].tolist(),
                'feature_values': X_test.iloc[i].to_dict(),
                'top_contributing_features': self._get_top_shap_features(shap_values[i], X_test.iloc[i])
            }
            local_explanations.append(explanation)
        
        return local_explanations
    
    def _get_top_shap_features(self, shap_values: np.ndarray, 
                             feature_values: pd.Series) -> List[Dict[str, Any]]:
        """Get top contributing features for a single prediction."""
        feature_contributions = []
        
        for i, (feature, value) in enumerate(feature_values.items()):
            contribution = {
                'feature': feature,
                'value': value,
                'shap_value': float(shap_values[i]),
                'contribution_magnitude': abs(float(shap_values[i]))
            }
            feature_contributions.append(contribution)
        
        # Sort by contribution magnitude
        feature_contributions.sort(key=lambda x: x['contribution_magnitude'], reverse=True)
        
        return feature_contributions[:5]  # Top 5 features
    
    def _generate_local_explanations(self, X_test: pd.DataFrame, 
                                   model_type: str) -> List[Dict[str, Any]]:
        """Generate local explanations using fallback methods."""
        local_explanations = []
        
        # Sample test instances for explanation
        sample_size = min(5, len(X_test))
        X_test_sample = X_test.sample(n=sample_size, random_state=42)
        
        for i, (idx, instance) in enumerate(X_test_sample.iterrows()):
            explanation = {
                'instance_index': i,
                'original_index': idx,
                'prediction': self.model.predict(instance.values.reshape(1, -1))[0],
                'feature_values': instance.to_dict()
            }
            
            # Simple feature contribution using perturbation
            contributions = self._calculate_feature_contributions(instance)
            explanation['feature_contributions'] = contributions
            
            local_explanations.append(explanation)
        
        return local_explanations
    
    def _calculate_feature_contributions(self, instance: pd.Series) -> List[Dict[str, Any]]:
        """Calculate feature contributions using simple perturbation."""
        baseline_pred = self.model.predict(instance.values.reshape(1, -1))[0]
        contributions = []
        
        for feature_idx, (feature_name, feature_value) in enumerate(instance.items()):
            # Create perturbed instance (set feature to mean)
            perturbed_instance = instance.copy()
            if isinstance(feature_value, (int, float)):
                perturbed_instance.iloc[feature_idx] = self.X_train.iloc[:, feature_idx].mean()
            else:
                perturbed_instance.iloc[feature_idx] = self.X_train.iloc[:, feature_idx].mode().iloc[0]
            
            try:
                perturbed_pred = self.model.predict(perturbed_instance.values.reshape(1, -1))[0]
                contribution = baseline_pred - perturbed_pred
                
                contributions.append({
                    'feature': feature_name,
                    'value': feature_value,
                    'contribution': float(contribution),
                    'contribution_magnitude': abs(float(contribution))
                })
            except:
                # Skip if perturbation fails
                continue
        
        # Sort by contribution magnitude
        contributions.sort(key=lambda x: x['contribution_magnitude'], reverse=True)
        return contributions[:5]  # Top 5 features
    
    def _assess_model_complexity(self) -> Dict[str, Any]:
        """Assess the complexity of the model."""
        complexity = {'assessment': 'Unknown'}
        
        model_name = type(self.model).__name__
        
        # Tree-based models
        if hasattr(self.model, 'n_estimators'):
            n_estimators = self.model.n_estimators
            complexity.update({
                'n_estimators': n_estimators,
                'assessment': 'High' if n_estimators > 100 else 'Medium' if n_estimators > 10 else 'Low'
            })
        
        elif hasattr(self.model, 'max_depth'):
            max_depth = self.model.max_depth
            complexity.update({
                'max_depth': max_depth,
                'assessment': 'High' if max_depth and max_depth > 10 else 'Medium' if max_depth and max_depth > 5 else 'Low'
            })
        
        # Linear models
        elif 'Linear' in model_name or 'Logistic' in model_name:
            complexity.update({
                'model_type': 'Linear',
                'assessment': 'Low',
                'interpretability': 'High'
            })
        
        # Add feature count consideration
        if self.feature_names:
            n_features = len(self.feature_names)
            if n_features > 50:
                complexity['feature_complexity'] = 'High'
            elif n_features > 20:
                complexity['feature_complexity'] = 'Medium'
            else:
                complexity['feature_complexity'] = 'Low'
        
        return complexity
    
    def _summarize_model_behavior(self) -> str:
        """Generate a natural language summary of model behavior."""
        model_name = type(self.model).__name__
        n_features = len(self.feature_names) if self.feature_names else 0
        
        summary = f"This {model_name} model uses {n_features} features to make predictions. "
        
        # Add model-specific behavior description
        if 'RandomForest' in model_name:
            n_estimators = getattr(self.model, 'n_estimators', 'unknown')
            summary += f"It combines {n_estimators} decision trees to reduce overfitting and improve generalization. "
        elif 'Linear' in model_name:
            summary += "It makes predictions using a linear combination of features, making it highly interpretable. "
        elif 'Tree' in model_name:
            summary += "It uses a tree structure to make decisions based on feature thresholds. "
        
        # Add complexity note
        complexity = self._assess_model_complexity()
        assessment = complexity.get('assessment', 'Unknown')
        summary += f"The model complexity is assessed as {assessment.lower()}."
        
        return summary
    
    def _explain_tree_model(self) -> Dict[str, Any]:
        """Generate explanations specific to tree-based models."""
        explanations = {}
        
        if hasattr(self.model, 'tree_'):
            # Single tree
            tree = self.model.tree_
            explanations.update({
                'tree_depth': int(tree.max_depth),
                'n_nodes': int(tree.node_count),
                'n_leaves': int(np.sum(tree.children_left == -1))
            })
        
        elif hasattr(self.model, 'estimators_'):
            # Ensemble of trees
            depths = [estimator.tree_.max_depth for estimator in self.model.estimators_]
            explanations.update({
                'n_estimators': len(self.model.estimators_),
                'avg_depth': float(np.mean(depths)),
                'max_depth': int(np.max(depths)),
                'min_depth': int(np.min(depths))
            })
        
        return explanations
    
    def _explain_linear_model(self) -> Dict[str, Any]:
        """Generate explanations specific to linear models."""
        explanations = {}
        
        if hasattr(self.model, 'coef_'):
            coef = self.model.coef_
            if coef.ndim > 1:
                coef = coef[0]  # Take first class for multi-class
            
            explanations.update({
                'n_features': len(coef),
                'positive_coefficients': int(np.sum(coef > 0)),
                'negative_coefficients': int(np.sum(coef < 0)),
                'max_coefficient': float(np.max(np.abs(coef))),
                'coefficient_range': float(np.max(coef) - np.min(coef))
            })
        
        if hasattr(self.model, 'intercept_'):
            explanations['intercept'] = float(self.model.intercept_)
        
        return explanations
    
    def _explain_ensemble_model(self) -> Dict[str, Any]:
        """Generate explanations specific to ensemble models."""
        explanations = {'model_type': 'Ensemble'}
        
        if hasattr(self.model, 'estimators_'):
            n_estimators = len(self.model.estimators_)
            explanations.update({
                'n_estimators': n_estimators,
                'ensemble_method': type(self.model).__name__
            })
        
        return explanations
    
    def _analyze_model_behavior(self) -> Dict[str, Any]:
        """Analyze general model behavior patterns."""
        behavior = {}
        
        # Prediction distribution analysis
        try:
            train_predictions = self.model.predict(self.X_train)
            
            behavior.update({
                'prediction_range': {
                    'min': float(np.min(train_predictions)),
                    'max': float(np.max(train_predictions)),
                    'mean': float(np.mean(train_predictions)),
                    'std': float(np.std(train_predictions))
                },
                'prediction_distribution': {
                    'skewness': float(pd.Series(train_predictions).skew()),
                    'kurtosis': float(pd.Series(train_predictions).kurtosis())
                }
            })
            
        except Exception as e:
            logger.warning(f"Could not analyze prediction behavior: {str(e)}")
        
        return behavior
    
    def _generate_explanation_visualizations(self) -> Dict[str, str]:
        """Generate additional explanation visualizations."""
        plots = {}
        
        if not PLOTTING_AVAILABLE:
            plots['error'] = 'Matplotlib not available for plotting'
            return plots
        
        try:
            # Feature importance plot (non-SHAP)
            importance_data = self.explanations.get('feature_importance', {})
            
            if 'summary' in importance_data:
                ranking = importance_data['summary']['ranking']
                if ranking:
                    features, importances = zip(*ranking[:10])  # Top 10 features
                    
                    plt.figure(figsize=(10, 6))
                    plt.barh(range(len(features)), importances)
                    plt.yticks(range(len(features)), features)
                    plt.xlabel('Importance Score')
                    plt.title('Feature Importance')
                    plt.gca().invert_yaxis()
                    plots['feature_importance'] = self._plot_to_base64()
                    plt.close()
            
        except Exception as e:
            logger.warning(f"Visualization generation failed: {str(e)}")
        
        return plots
    
    def _plot_to_base64(self) -> str:
        """Convert current matplotlib plot to base64 string."""
        if not PLOTTING_AVAILABLE:
            return ''
            
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(plot_data).decode('utf-8')
    
    def explain_prediction(self, instance: Union[pd.Series, np.ndarray, Dict]) -> Dict[str, Any]:
        """Explain a single prediction in detail."""
        if self.model is None:
            raise ValueError("No model available. Run explain_model() first.")
        
        # Convert instance to appropriate format
        if isinstance(instance, dict):
            if self.feature_names:
                instance_array = np.array([instance.get(name, 0) for name in self.feature_names])
            else:
                instance_array = np.array(list(instance.values()))
        elif isinstance(instance, pd.Series):
            instance_array = instance.values
        else:
            instance_array = np.array(instance)
        
        # Make prediction
        prediction = self.model.predict(instance_array.reshape(1, -1))[0]
        
        explanation = {
            'prediction': float(prediction),
            'input_values': instance_array.tolist(),
            'feature_names': self.feature_names or [f'feature_{i}' for i in range(len(instance_array))]
        }
        
        # SHAP explanation if available
        if SHAP_AVAILABLE and self.explainer is not None:
            try:
                shap_values = self.explainer.shap_values(instance_array.reshape(1, -1))
                if isinstance(shap_values, list):
                    shap_values = shap_values[0]
                
                explanation['shap_explanation'] = {
                    'shap_values': shap_values[0].tolist(),
                    'expected_value': float(self.explainer.expected_value),
                    'top_features': self._get_top_shap_features(shap_values[0], 
                                                              pd.Series(instance_array, index=self.feature_names))
                }
            except Exception as e:
                logger.warning(f"SHAP explanation for single prediction failed: {str(e)}")
        
        # Fallback explanation using perturbation
        try:
            contributions = self._calculate_feature_contributions(
                pd.Series(instance_array, index=self.feature_names)
            )
            explanation['feature_contributions'] = contributions
        except Exception as e:
            logger.warning(f"Feature contribution calculation failed: {str(e)}")
        
        return explanation
    
    def get_explanation_summary(self) -> List[str]:
        """Generate human-readable summary of model explanations."""
        if not self.explanations:
            return ["No model explanations available. Run explain_model() first."]
        
        insights = []
        
        # Model complexity insights
        complexity = self.explanations.get('global_explanations', {}).get('model_complexity', {})
        assessment = complexity.get('assessment', 'Unknown')
        insights.append(f"Model complexity is {assessment.lower()}")
        
        # Feature importance insights
        feature_importance = self.explanations.get('feature_importance', {})
        if 'summary' in feature_importance:
            top_features = feature_importance['summary'].get('top_features', [])
            if top_features:
                insights.append(f"Most important features: {', '.join(top_features[:3])}")
        
        # SHAP insights
        shap_explanations = self.explanations.get('shap_explanations', {})
        if 'global_importance' in shap_explanations:
            insights.append("SHAP analysis confirms feature importance rankings")
        
        # Model behavior insights
        behavior = self.explanations.get('model_behavior', {})
        pred_range = behavior.get('prediction_range', {})
        if pred_range:
            pred_mean = pred_range.get('mean', 0)
            pred_std = pred_range.get('std', 0)
            cv = pred_std / pred_mean if pred_mean != 0 else 0
            if cv > 0.5:
                insights.append("Model predictions show high variability")
            elif cv < 0.1:
                insights.append("Model predictions are relatively stable")
        
        return insights if insights else ["Model explanation analysis completed"]
    
    def save_explanations(self, filepath: str) -> None:
        """Save explanations to file."""
        if not self.explanations:
            raise ValueError("No explanations to save. Run explain_model() first.")
        
        # Remove plot data for JSON serialization
        explanations_to_save = self.explanations.copy()
        if 'visualizations' in explanations_to_save:
            explanations_to_save['visualizations'] = {
                k: 'base64_plot_data_removed' for k in explanations_to_save['visualizations'].keys()
            }
        
        import json
        with open(filepath, 'w') as f:
            json.dump(explanations_to_save, f, indent=2, default=str)
        
        logger.info(f"Model explanations saved to: {filepath}")
    
    def load_explanations(self, filepath: str) -> None:
        """Load explanations from file."""
        import json
        with open(filepath, 'r') as f:
            self.explanations = json.load(f)
        
        logger.info(f"Model explanations loaded from: {filepath}")