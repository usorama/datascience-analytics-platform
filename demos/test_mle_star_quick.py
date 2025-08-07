#!/usr/bin/env python3
"""Quick test of MLE-STAR implementation"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

from datascience_platform.mle_star import (
    MLPipelineAnalyzer,
    AblationStudyEngine,
    ComponentType
)

# Create simple data
X, y = make_classification(n_samples=200, n_features=20, n_informative=15, random_state=42)
X = pd.DataFrame(X)
y = pd.Series(y)

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('selector', SelectKBest(k=10)),
    ('classifier', RandomForestClassifier(n_estimators=10, random_state=42))
])

# Test 1: Pipeline Analysis
print("Test 1: Pipeline Analysis")
analyzer = MLPipelineAnalyzer()
config = {
    "scaler": {"type": "preprocessing", "dependencies": []},
    "selector": {"type": "feature_selection", "dependencies": ["scaler"]},
    "classifier": {"type": "model", "dependencies": ["selector"]}
}
components = analyzer.analyze_pipeline_config(config)
print(f"Components found: {list(components.keys())}")
print(f"Execution order: {analyzer.get_execution_order()}")

# Test 2: Simple Ablation
print("\nTest 2: Ablation Test")
ablation = AblationStudyEngine(n_cv_folds=2)

# Test baseline
baseline_scores = cross_val_score(pipeline, X, y, cv=2)
print(f"Baseline scores: {baseline_scores}")
print(f"Baseline mean: {np.mean(baseline_scores):.4f}")

# Test ablated pipeline manually
from sklearn.preprocessing import FunctionTransformer
ablated_pipeline = Pipeline([
    ('scaler', FunctionTransformer(lambda x: x)),  # Pass through
    ('selector', SelectKBest(k=10)),
    ('classifier', RandomForestClassifier(n_estimators=10, random_state=42))
])

ablated_scores = cross_val_score(ablated_pipeline, X, y, cv=2)
print(f"Ablated scores: {ablated_scores}")
print(f"Ablated mean: {np.mean(ablated_scores):.4f}")
print(f"Impact: {np.mean(baseline_scores) - np.mean(ablated_scores):.4f}")

print("\nQuick test complete!")