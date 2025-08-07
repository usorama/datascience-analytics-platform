"""ML Pipeline Analysis and Component Detection

This module provides tools to analyze ML pipelines, identify components,
and understand their structure and dependencies.
"""

import ast
import inspect
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    """Types of ML pipeline components."""
    DATA_LOADING = "data_loading"
    DATA_PREPROCESSING = "data_preprocessing"
    FEATURE_ENGINEERING = "feature_engineering"
    FEATURE_SELECTION = "feature_selection"
    MODEL_SELECTION = "model_selection"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    ENSEMBLE_METHODS = "ensemble_methods"
    VALIDATION = "validation"
    POSTPROCESSING = "postprocessing"


@dataclass
class PipelineComponent:
    """Represents a component in an ML pipeline."""
    component_id: str
    component_type: ComponentType
    name: str
    description: str
    code: Optional[str] = None
    parameters: Dict[str, Any] = None
    dependencies: List[str] = None
    performance_impact: Optional[float] = None
    complexity_score: Optional[float] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.dependencies is None:
            self.dependencies = []


class MLPipelineAnalyzer:
    """Analyzes ML pipelines to identify and extract components."""
    
    def __init__(self):
        self.components: Dict[str, PipelineComponent] = {}
        self.component_graph: Dict[str, List[str]] = {}
        
        # Pattern matching for component identification
        self.component_patterns = {
            ComponentType.DATA_LOADING: [
                'read_csv', 'load_data', 'fetch_data', 'read_parquet',
                'read_json', 'read_excel', 'load_dataset'
            ],
            ComponentType.DATA_PREPROCESSING: [
                'fillna', 'dropna', 'handle_missing', 'clean_data',
                'remove_outliers', 'normalize', 'standardize'
            ],
            ComponentType.FEATURE_ENGINEERING: [
                'create_features', 'engineer_features', 'transform',
                'encode_categorical', 'polynomial_features', 'binning'
            ],
            ComponentType.FEATURE_SELECTION: [
                'select_features', 'feature_importance', 'SelectKBest',
                'RFE', 'mutual_info', 'variance_threshold'
            ],
            ComponentType.MODEL_SELECTION: [
                'RandomForest', 'XGBoost', 'LogisticRegression',
                'SVM', 'NeuralNetwork', 'fit', 'train_model'
            ],
            ComponentType.HYPERPARAMETER_TUNING: [
                'GridSearchCV', 'RandomizedSearchCV', 'optuna',
                'hyperopt', 'tune_hyperparameters', 'bayesian_optimization'
            ],
            ComponentType.ENSEMBLE_METHODS: [
                'VotingClassifier', 'StackingClassifier', 'ensemble',
                'blend_models', 'average_predictions'
            ]
        }
    
    def analyze_pipeline_code(self, code: str) -> Dict[str, PipelineComponent]:
        """Analyze Python code to extract ML pipeline components."""
        try:
            tree = ast.parse(code)
            self._extract_components_from_ast(tree)
        except SyntaxError as e:
            logger.error(f"Failed to parse code: {e}")
            raise
        
        return self.components
    
    def analyze_pipeline_config(self, config: Dict[str, Any]) -> Dict[str, PipelineComponent]:
        """Analyze pipeline configuration to extract components."""
        for comp_id, comp_config in config.items():
            component_type = self._infer_component_type(comp_config)
            
            component = PipelineComponent(
                component_id=comp_id,
                component_type=component_type,
                name=comp_config.get('name', comp_id),
                description=comp_config.get('description', ''),
                parameters=comp_config.get('parameters', {}),
                dependencies=comp_config.get('dependencies', [])
            )
            
            self.components[comp_id] = component
            
        self._build_dependency_graph()
        return self.components
    
    def _extract_components_from_ast(self, tree: ast.AST):
        """Extract components from AST tree."""
        class ComponentVisitor(ast.NodeVisitor):
            def __init__(self, analyzer):
                self.analyzer = analyzer
                self.current_function = None
                
            def visit_FunctionDef(self, node):
                self.current_function = node.name
                # Check if function matches component patterns
                component_type = self.analyzer._match_component_pattern(node.name)
                if component_type:
                    component = PipelineComponent(
                        component_id=f"func_{node.name}",
                        component_type=component_type,
                        name=node.name,
                        description=ast.get_docstring(node) or "",
                        code=ast.unparse(node) if hasattr(ast, 'unparse') else None
                    )
                    self.analyzer.components[component.component_id] = component
                
                self.generic_visit(node)
                self.current_function = None
            
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                else:
                    self.generic_visit(node)
                    return
                
                component_type = self.analyzer._match_component_pattern(func_name)
                if component_type and self.current_function:
                    # This is a component call within a function
                    comp_id = f"call_{func_name}_{len(self.analyzer.components)}"
                    component = PipelineComponent(
                        component_id=comp_id,
                        component_type=component_type,
                        name=func_name,
                        description=f"Call to {func_name} in {self.current_function}"
                    )
                    self.analyzer.components[comp_id] = component
                
                self.generic_visit(node)
        
        visitor = ComponentVisitor(self)
        visitor.visit(tree)
    
    def _match_component_pattern(self, name: str) -> Optional[ComponentType]:
        """Match a name against component patterns."""
        name_lower = name.lower()
        for comp_type, patterns in self.component_patterns.items():
            for pattern in patterns:
                if pattern.lower() in name_lower:
                    return comp_type
        return None
    
    def _infer_component_type(self, config: Dict[str, Any]) -> ComponentType:
        """Infer component type from configuration."""
        type_str = config.get('type', '').lower()
        
        type_mapping = {
            'data': ComponentType.DATA_LOADING,
            'preprocessing': ComponentType.DATA_PREPROCESSING,
            'feature': ComponentType.FEATURE_ENGINEERING,
            'selection': ComponentType.FEATURE_SELECTION,
            'model': ComponentType.MODEL_SELECTION,
            'tuning': ComponentType.HYPERPARAMETER_TUNING,
            'ensemble': ComponentType.ENSEMBLE_METHODS
        }
        
        for key, comp_type in type_mapping.items():
            if key in type_str:
                return comp_type
        
        # Check parameters for hints
        params = config.get('parameters', {})
        if 'model' in params or 'estimator' in params:
            return ComponentType.MODEL_SELECTION
        elif 'features' in params:
            return ComponentType.FEATURE_ENGINEERING
        
        return ComponentType.DATA_PREPROCESSING  # Default
    
    def _build_dependency_graph(self):
        """Build dependency graph from components."""
        self.component_graph = {}
        
        for comp_id, component in self.components.items():
            self.component_graph[comp_id] = component.dependencies.copy()
    
    def get_execution_order(self) -> List[str]:
        """Get topological execution order of components."""
        from collections import deque
        
        # If no dependency graph built yet, return all components
        if not self.component_graph:
            return list(self.components.keys())
        
        # Calculate in-degree for each component
        in_degree = {comp_id: 0 for comp_id in self.components}
        
        # Build reverse dependency graph for topological sort
        reverse_graph = {comp_id: [] for comp_id in self.components}
        
        for comp_id, deps in self.component_graph.items():
            for dep in deps:
                if dep in reverse_graph:
                    reverse_graph[dep].append(comp_id)
                    in_degree[comp_id] += 1
        
        # Find components with no dependencies
        queue = deque([comp_id for comp_id, degree in in_degree.items() if degree == 0])
        execution_order = []
        
        while queue:
            current = queue.popleft()
            execution_order.append(current)
            
            # Reduce in-degree for dependent components
            for dependent in reverse_graph.get(current, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # If some components weren't added (circular dependency), add them anyway
        for comp_id in self.components:
            if comp_id not in execution_order:
                execution_order.append(comp_id)
        
        return execution_order
    
    def calculate_complexity_scores(self) -> Dict[str, float]:
        """Calculate complexity scores for each component."""
        complexity_scores = {}
        
        for comp_id, component in self.components.items():
            score = 0.0
            
            # Base complexity by type
            type_complexity = {
                ComponentType.DATA_LOADING: 0.1,
                ComponentType.DATA_PREPROCESSING: 0.3,
                ComponentType.FEATURE_ENGINEERING: 0.5,
                ComponentType.FEATURE_SELECTION: 0.4,
                ComponentType.MODEL_SELECTION: 0.6,
                ComponentType.HYPERPARAMETER_TUNING: 0.8,
                ComponentType.ENSEMBLE_METHODS: 0.9
            }
            score += type_complexity.get(component.component_type, 0.5)
            
            # Complexity based on parameters
            param_count = len(component.parameters)
            score += min(param_count * 0.05, 0.3)
            
            # Complexity based on dependencies
            dep_count = len(component.dependencies)
            score += min(dep_count * 0.1, 0.2)
            
            # Normalize to [0, 1]
            complexity_scores[comp_id] = min(score, 1.0)
            component.complexity_score = complexity_scores[comp_id]
        
        return complexity_scores
    
    def identify_bottlenecks(self) -> List[Tuple[str, str]]:
        """Identify potential bottlenecks in the pipeline."""
        bottlenecks = []
        
        # Check for components with many dependencies
        for comp_id, deps in self.component_graph.items():
            if len(deps) > 3:
                bottlenecks.append((
                    comp_id,
                    f"High dependency count: {len(deps)} dependencies"
                ))
        
        # Check for complex components early in pipeline
        execution_order = self.get_execution_order()
        for i, comp_id in enumerate(execution_order[:len(execution_order)//2]):
            component = self.components[comp_id]
            if component.complexity_score and component.complexity_score > 0.7:
                bottlenecks.append((
                    comp_id,
                    f"Complex component early in pipeline (complexity: {component.complexity_score:.2f})"
                ))
        
        return bottlenecks
    
    def export_pipeline_visualization(self, output_path: Path) -> Dict[str, Any]:
        """Export pipeline structure for visualization."""
        viz_data = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "total_components": len(self.components),
                "execution_order": self.get_execution_order(),
                "bottlenecks": self.identify_bottlenecks()
            }
        }
        
        # Add nodes
        for comp_id, component in self.components.items():
            viz_data["nodes"].append({
                "id": comp_id,
                "label": component.name,
                "type": component.component_type.value,
                "complexity": component.complexity_score,
                "impact": component.performance_impact
            })
        
        # Add edges
        for source, targets in self.component_graph.items():
            for target in targets:
                viz_data["edges"].append({
                    "source": source,
                    "target": target
                })
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(viz_data, f, indent=2)
        
        return viz_data
    
    def generate_component_report(self) -> pd.DataFrame:
        """Generate a detailed report of all components."""
        report_data = []
        
        for comp_id, component in self.components.items():
            report_data.append({
                'Component ID': comp_id,
                'Name': component.name,
                'Type': component.component_type.value,
                'Description': component.description[:100] + '...' if len(component.description) > 100 else component.description,
                'Dependencies': len(component.dependencies),
                'Complexity Score': component.complexity_score,
                'Performance Impact': component.performance_impact,
                'Parameters': len(component.parameters)
            })
        
        return pd.DataFrame(report_data)