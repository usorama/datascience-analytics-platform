"""AutoML Engine

Integrates AutoGluon for automated machine learning tasks including
regression, classification, feature importance, and model performance evaluation.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple
import warnings
import os
import tempfile
import shutil

# Try to import AutoGluon - graceful fallback if not available
try:
    from autogluon.tabular import TabularDataset, TabularPredictor
    AUTOGLUON_AVAILABLE = True
except ImportError:
    AUTOGLUON_AVAILABLE = False
    logging.warning("AutoGluon not available. AutoML functionality will be limited.")

# Sklearn fallbacks
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder
import joblib

warnings.filterwarnings('ignore', category=FutureWarning)

logger = logging.getLogger(__name__)


class AutoMLEngine:
    """Automated machine learning engine with AutoGluon integration and sklearn fallback."""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the AutoML engine."""
        self.model_path = model_path or tempfile.mkdtemp(prefix="automl_models_")
        self.predictor = None
        self.sklearn_model = None
        self.task_type = None
        self.target_column = None
        self.feature_columns = None
        self.label_encoder = None
        self.results = {}
        
    def train_model(self, df: pd.DataFrame, 
                   target_column: str,
                   task_type: str = 'auto',
                   time_limit: int = 300,
                   quality_preset: str = 'medium_quality',
                   exclude_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Train an automated machine learning model.
        
        Args:
            df: Input DataFrame
            target_column: Name of target column
            task_type: 'regression', 'classification', or 'auto'
            time_limit: Training time limit in seconds
            quality_preset: AutoGluon quality preset
            exclude_columns: Columns to exclude from training
            
        Returns:
            Dictionary containing training results and model performance
        """
        try:
            logger.info(f"Starting AutoML training for target: {target_column}")
            
            # Validate inputs
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found in DataFrame")
            
            # Prepare data
            prepared_data = self._prepare_data(df, target_column, exclude_columns)
            
            # Determine task type
            self.task_type = self._determine_task_type(prepared_data[target_column], task_type)
            self.target_column = target_column
            self.feature_columns = [col for col in prepared_data.columns if col != target_column]
            
            logger.info(f"Detected task type: {self.task_type}")
            
            # Train model
            if AUTOGLUON_AVAILABLE:
                results = self._train_autogluon_model(prepared_data, target_column, 
                                                    time_limit, quality_preset)
            else:
                results = self._train_sklearn_model(prepared_data, target_column)
            
            self.results = results
            logger.info("AutoML training completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in AutoML training: {str(e)}")
            raise
    
    def _prepare_data(self, df: pd.DataFrame, 
                     target_column: str,
                     exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Prepare data for training."""
        # Create a copy
        data = df.copy()
        
        # Remove exclude columns
        if exclude_columns:
            exclude_columns = [col for col in exclude_columns if col in data.columns and col != target_column]
            data = data.drop(columns=exclude_columns)
        
        # Remove rows with missing target
        data = data.dropna(subset=[target_column])
        
        # Basic data cleaning
        # Remove columns with too many missing values (>50%)
        missing_threshold = 0.5
        columns_to_drop = []
        for col in data.columns:
            if col != target_column:
                missing_ratio = data[col].isnull().sum() / len(data)
                if missing_ratio > missing_threshold:
                    columns_to_drop.append(col)
        
        if columns_to_drop:
            data = data.drop(columns=columns_to_drop)
            logger.info(f"Dropped columns with >50% missing values: {columns_to_drop}")
        
        # Remove constant columns
        constant_columns = []
        for col in data.columns:
            if col != target_column and data[col].nunique() <= 1:
                constant_columns.append(col)
        
        if constant_columns:
            data = data.drop(columns=constant_columns)
            logger.info(f"Dropped constant columns: {constant_columns}")
        
        return data
    
    def _determine_task_type(self, target_series: pd.Series, task_type: str) -> str:
        """Determine if the task is regression or classification."""
        if task_type in ['regression', 'classification']:
            return task_type
        
        # Auto-detect task type
        if target_series.dtype in ['int64', 'float64']:
            # Check if it looks like classification
            unique_values = target_series.nunique()
            total_values = len(target_series)
            
            # If less than 20 unique values and they represent < 10% of total, likely classification
            if unique_values < 20 and (unique_values / total_values) < 0.1:
                return 'classification'
            else:
                return 'regression'
        else:
            return 'classification'
    
    def _train_autogluon_model(self, data: pd.DataFrame, 
                              target_column: str,
                              time_limit: int,
                              quality_preset: str) -> Dict[str, Any]:
        """Train model using AutoGluon."""
        try:
            # Create TabularDataset
            train_data = TabularDataset(data)
            
            # Split data for evaluation
            train_data_split, test_data_split = train_test_split(data, test_size=0.2, random_state=42)
            train_dataset = TabularDataset(train_data_split)
            test_dataset = TabularDataset(test_data_split)
            
            # Configure predictor
            predictor_args = {
                'path': self.model_path,
                'label': target_column,
                'problem_type': self.task_type,
                'eval_metric': self._get_eval_metric(self.task_type)
            }
            
            # Create and train predictor
            self.predictor = TabularPredictor(**predictor_args)
            
            # Train with time limit
            self.predictor.fit(
                train_data=train_dataset,
                time_limit=time_limit,
                presets=quality_preset,
                verbosity=0  # Reduce output
            )
            
            # Evaluate model
            evaluation_results = self._evaluate_autogluon_model(test_dataset, target_column)
            
            # Get feature importance
            try:
                feature_importance = self.predictor.feature_importance(train_dataset)
                feature_importance_dict = {
                    row['feature']: float(row['importance']) 
                    for _, row in feature_importance.iterrows()
                }
            except Exception as e:
                logger.warning(f"Could not get feature importance: {str(e)}")
                feature_importance_dict = {}
            
            # Get model leaderboard
            try:
                leaderboard = self.predictor.leaderboard(test_dataset, silent=True)
                model_summary = []
                for _, row in leaderboard.head(5).iterrows():  # Top 5 models
                    model_summary.append({
                        'model': str(row['model']),
                        'score_val': float(row['score_val']),
                        'score_test': float(row.get('score_test', row['score_val'])),
                        'fit_time': float(row.get('fit_time', 0)),
                        'pred_time_val': float(row.get('pred_time_val', 0))
                    })
            except Exception as e:
                logger.warning(f"Could not get leaderboard: {str(e)}")
                model_summary = []
            
            results = {
                'framework': 'AutoGluon',
                'task_type': self.task_type,
                'target_column': target_column,
                'feature_columns': self.feature_columns,
                'data_shape': data.shape,
                'training_time': time_limit,
                'model_summary': model_summary,
                'feature_importance': feature_importance_dict,
                'evaluation': evaluation_results,
                'model_path': self.model_path
            }
            
            return results
            
        except Exception as e:
            logger.error(f"AutoGluon training failed: {str(e)}")
            # Fall back to sklearn
            return self._train_sklearn_model(data, target_column)
    
    def _train_sklearn_model(self, data: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """Train model using sklearn as fallback."""
        logger.info("Using sklearn fallback for model training")
        
        # Prepare features and target
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        # Handle categorical variables
        categorical_columns = X.select_dtypes(include=['object', 'category']).columns
        if len(categorical_columns) > 0:
            # Simple encoding for categorical variables
            X_encoded = X.copy()
            for col in categorical_columns:
                # Use frequency encoding for high cardinality
                if X_encoded[col].nunique() > 10:
                    freq_encoding = X_encoded[col].value_counts(normalize=True)
                    X_encoded[col] = X_encoded[col].map(freq_encoding)
                else:
                    # Use label encoding for low cardinality
                    le = LabelEncoder()
                    X_encoded[col] = le.fit_transform(X_encoded[col].astype(str))
        else:
            X_encoded = X
        
        # Handle missing values
        X_encoded = X_encoded.fillna(X_encoded.mean() if self.task_type == 'regression' else X_encoded.mode().iloc[0])
        
        # Encode target if classification
        if self.task_type == 'classification':
            self.label_encoder = LabelEncoder()
            y_encoded = self.label_encoder.fit_transform(y.astype(str))
        else:
            y_encoded = y
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y_encoded, test_size=0.2, random_state=42
        )
        
        # Choose and train model
        if self.task_type == 'regression':
            self.sklearn_model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            self.sklearn_model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Train model
        self.sklearn_model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = self.sklearn_model.predict(X_test)
        
        # Calculate metrics
        evaluation_results = self._evaluate_sklearn_model(y_test, y_pred, X_test)
        
        # Get feature importance
        feature_importance_dict = {}
        if hasattr(self.sklearn_model, 'feature_importances_'):
            for feature, importance in zip(X_encoded.columns, self.sklearn_model.feature_importances_):
                feature_importance_dict[feature] = float(importance)
        
        # Cross-validation
        cv_scores = cross_val_score(self.sklearn_model, X_encoded, y_encoded, cv=5)
        
        results = {
            'framework': 'sklearn',
            'task_type': self.task_type,
            'target_column': target_column,
            'feature_columns': self.feature_columns,
            'data_shape': data.shape,
            'model_type': type(self.sklearn_model).__name__,
            'feature_importance': feature_importance_dict,
            'evaluation': evaluation_results,
            'cross_validation': {
                'mean_score': float(cv_scores.mean()),
                'std_score': float(cv_scores.std()),
                'scores': cv_scores.tolist()
            }
        }
        
        return results
    
    def _get_eval_metric(self, task_type: str) -> str:
        """Get appropriate evaluation metric for task type."""
        if task_type == 'regression':
            return 'root_mean_squared_error'
        else:
            return 'accuracy'
    
    def _evaluate_autogluon_model(self, test_data: 'TabularDataset', 
                                 target_column: str) -> Dict[str, Any]:
        """Evaluate AutoGluon model."""
        try:
            # Get predictions
            predictions = self.predictor.predict(test_data)
            true_values = test_data[target_column]
            
            if self.task_type == 'regression':
                metrics = {
                    'rmse': float(np.sqrt(mean_squared_error(true_values, predictions))),
                    'mae': float(mean_absolute_error(true_values, predictions)),
                    'r2': float(r2_score(true_values, predictions))
                }
            else:
                # Get prediction probabilities for classification
                try:
                    pred_probs = self.predictor.predict_proba(test_data)
                    if len(pred_probs.columns) == 2:  # Binary classification
                        auc_score = roc_auc_score(true_values, pred_probs.iloc[:, 1])
                    else:
                        auc_score = None
                except:
                    auc_score = None
                
                metrics = {
                    'accuracy': float(accuracy_score(true_values, predictions)),
                    'precision': float(precision_score(true_values, predictions, average='weighted')),
                    'recall': float(recall_score(true_values, predictions, average='weighted')),
                    'f1': float(f1_score(true_values, predictions, average='weighted'))
                }
                
                if auc_score is not None:
                    metrics['auc'] = float(auc_score)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Model evaluation failed: {str(e)}")
            return {'error': str(e)}
    
    def _evaluate_sklearn_model(self, y_true: np.ndarray, 
                               y_pred: np.ndarray,
                               X_test: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate sklearn model."""
        try:
            if self.task_type == 'regression':
                metrics = {
                    'rmse': float(np.sqrt(mean_squared_error(y_true, y_pred))),
                    'mae': float(mean_absolute_error(y_true, y_pred)),
                    'r2': float(r2_score(y_true, y_pred))
                }
            else:
                metrics = {
                    'accuracy': float(accuracy_score(y_true, y_pred))
                }
                
                try:
                    metrics['precision'] = float(precision_score(y_true, y_pred, average='weighted'))
                    metrics['recall'] = float(recall_score(y_true, y_pred, average='weighted'))
                    metrics['f1'] = float(f1_score(y_true, y_pred, average='weighted'))
                except:
                    pass  # Skip if multiclass issues
                
                # AUC for binary classification
                try:
                    if len(np.unique(y_true)) == 2:
                        y_pred_proba = self.sklearn_model.predict_proba(X_test)[:, 1]
                        metrics['auc'] = float(roc_auc_score(y_true, y_pred_proba))
                except:
                    pass
            
            return metrics
            
        except Exception as e:
            logger.error(f"Sklearn model evaluation failed: {str(e)}")
            return {'error': str(e)}
    
    def predict(self, df: pd.DataFrame) -> Union[pd.Series, np.ndarray]:
        """Make predictions on new data."""
        if self.predictor is not None:
            return self.predictor.predict(df)
        elif self.sklearn_model is not None:
            # Prepare data similar to training
            X = df[self.feature_columns] if self.feature_columns else df
            
            # Handle categorical encoding (simplified)
            categorical_columns = X.select_dtypes(include=['object', 'category']).columns
            if len(categorical_columns) > 0:
                X_encoded = X.copy()
                for col in categorical_columns:
                    # Simple frequency encoding fallback
                    X_encoded[col] = pd.Categorical(X_encoded[col]).codes
            else:
                X_encoded = X
            
            # Handle missing values
            X_encoded = X_encoded.fillna(X_encoded.mean())
            
            predictions = self.sklearn_model.predict(X_encoded)
            
            # Decode predictions if classification
            if self.task_type == 'classification' and self.label_encoder is not None:
                predictions = self.label_encoder.inverse_transform(predictions)
            
            return predictions
        else:
            raise ValueError("No trained model available for predictions")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the trained model."""
        if not self.results:
            return {}
        
        return self.results.get('feature_importance', {})
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance metrics."""
        if not self.results:
            return {}
        
        return self.results.get('evaluation', {})
    
    def save_model(self, path: str) -> None:
        """Save the trained model."""
        if self.predictor is not None:
            # AutoGluon models are automatically saved to model_path
            logger.info(f"AutoGluon model saved to: {self.model_path}")
        elif self.sklearn_model is not None:
            joblib.dump({
                'model': self.sklearn_model,
                'label_encoder': self.label_encoder,
                'feature_columns': self.feature_columns,
                'task_type': self.task_type
            }, path)
            logger.info(f"Sklearn model saved to: {path}")
        else:
            raise ValueError("No trained model to save")
    
    def load_model(self, path: str) -> None:
        """Load a previously trained model."""
        if AUTOGLUON_AVAILABLE and os.path.exists(os.path.join(path, 'predictor.pkl')):
            # Load AutoGluon model
            self.predictor = TabularPredictor.load(path)
            self.model_path = path
            logger.info(f"AutoGluon model loaded from: {path}")
        else:
            # Load sklearn model
            model_data = joblib.load(path)
            self.sklearn_model = model_data['model']
            self.label_encoder = model_data.get('label_encoder')
            self.feature_columns = model_data.get('feature_columns')
            self.task_type = model_data.get('task_type')
            logger.info(f"Sklearn model loaded from: {path}")
    
    def get_model_insights(self) -> List[str]:
        """Generate human-readable insights from the model training."""
        if not self.results:
            return ["No model training results available. Train a model first."]
        
        insights = []
        
        # Basic model info
        framework = self.results.get('framework', 'Unknown')
        task_type = self.results.get('task_type', 'Unknown')
        data_shape = self.results.get('data_shape', (0, 0))
        
        insights.append(f"Trained {framework} {task_type} model on {data_shape[0]:,} samples with {data_shape[1]-1} features")
        
        # Performance insights
        evaluation = self.results.get('evaluation', {})
        if self.task_type == 'regression':
            r2 = evaluation.get('r2', 0)
            rmse = evaluation.get('rmse', 0)
            insights.append(f"Model explains {r2*100:.1f}% of variance (R²={r2:.3f}, RMSE={rmse:.3f})")
        else:
            accuracy = evaluation.get('accuracy', 0)
            f1 = evaluation.get('f1', 0)
            insights.append(f"Classification accuracy: {accuracy*100:.1f}%" + 
                          (f", F1-score: {f1:.3f}" if f1 > 0 else ""))
        
        # Feature importance insights
        feature_importance = self.results.get('feature_importance', {})
        if feature_importance:
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
            feature_names = [f[0] for f in top_features]
            insights.append(f"Most important features: {', '.join(feature_names)}")
        
        # Model complexity insights
        if framework == 'AutoGluon':
            model_summary = self.results.get('model_summary', [])
            if model_summary:
                best_model = model_summary[0]['model'] if model_summary else 'Unknown'
                insights.append(f"Best performing model: {best_model}")
        
        return insights
    
    def cleanup(self) -> None:
        """Clean up temporary files and models."""
        if self.model_path and os.path.exists(self.model_path) and 'tmp' in self.model_path:
            try:
                shutil.rmtree(self.model_path)
                logger.info(f"Cleaned up temporary model directory: {self.model_path}")
            except Exception as e:
                logger.warning(f"Could not clean up model directory: {str(e)}")
    
    def __del__(self):
        """Destructor to clean up resources."""
        self.cleanup()