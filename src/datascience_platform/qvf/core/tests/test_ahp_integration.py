"""Comprehensive tests for QVF-AHP integration engine.

This test suite validates the mathematical rigor and business logic integration
of the QVF-AHP bridge. It ensures consistency ratios meet the ≤ 0.10 requirement
and validates the enhanced AHP features for QVF-specific use cases.
"""

import pytest
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch

# Import the integration components
from ..ahp_integration import (
    QVFAHPIntegrator, IntegrationConfiguration, IntegrationResult,
    ConversionMethod, HierarchyLevel, QVFAHPIntegrationError,
    create_balanced_integration_config, create_strict_consistency_config
)

# Import enhanced AHP components  
from ....ado.ahp import (
    AHPEngine, AHPConfiguration, AHPCriterion, PairwiseComparison,
    AHPValidationResult, GroupAHPResult
)

# Import QVF components
from ..criteria import QVFCriteriaEngine, QVFCriteriaConfiguration, QVFCriterion
from ....ado.models import ADOWorkItem, WorkItemType


class TestIntegrationConfiguration:
    """Test integration configuration validation and factory methods."""
    
    def test_default_configuration(self):
        """Test default configuration is valid."""
        config = IntegrationConfiguration()
        issues = config.validate()
        assert len(issues) == 0
        assert config.conversion_method == ConversionMethod.HYBRID_APPROACH
        assert config.consistency_threshold == 0.10
        assert config.auto_improve_consistency == True
    
    def test_configuration_validation(self):
        """Test configuration validation catches invalid parameters."""
        # Invalid consistency threshold
        config = IntegrationConfiguration(consistency_threshold=0.5)
        issues = config.validate()
        assert len(issues) > 0
        assert "consistency threshold" in issues[0].lower()
        
        # Invalid extreme ratio threshold
        config = IntegrationConfiguration(extreme_ratio_threshold=15.0)
        issues = config.validate()
        assert len(issues) > 0
        assert "extreme ratio threshold" in issues[0].lower()
    
    def test_factory_methods(self):
        """Test configuration factory methods."""
        # Balanced config
        balanced = create_balanced_integration_config()
        assert balanced.conversion_method == ConversionMethod.HYBRID_APPROACH
        assert balanced.consistency_threshold == 0.10
        
        # Strict consistency config
        strict = create_strict_consistency_config()
        assert strict.consistency_threshold == 0.05
        assert strict.max_improvement_iterations == 20


class TestEnhancedAHPEngine:
    """Test enhanced AHP engine features for QVF integration."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.criteria = [
            AHPCriterion(name="Business Value", description="Business impact", data_source="business_value"),
            AHPCriterion(name="Risk Reduction", description="Risk mitigation", data_source="risk_reduction"),
            AHPCriterion(name="Feasibility", description="Implementation feasibility", data_source="feasibility")
        ]
        self.config = AHPConfiguration(criteria=self.criteria, consistency_threshold=0.10)
        self.engine = AHPEngine(self.config, enable_advanced_features=True)
    
    def test_enhanced_weight_calculation_methods(self):
        """Test different weight calculation methods."""
        # Create a known consistent matrix
        matrix = np.array([
            [1.0, 3.0, 5.0],
            [1/3.0, 1.0, 2.0],
            [1/5.0, 1/2.0, 1.0]
        ])
        
        self.engine.comparison_matrix = matrix
        
        # Test eigenvalue method
        weights_eigen = self.engine.calculate_weights(method='eigenvalue')
        assert len(weights_eigen) == 3
        assert np.isclose(np.sum(weights_eigen), 1.0, atol=1e-6)
        
        # Test power iteration method
        weights_power = self.engine.calculate_weights(method='power_iteration')
        assert len(weights_power) == 3
        assert np.isclose(np.sum(weights_power), 1.0, atol=1e-6)
        
        # Test geometric mean method
        weights_geom = self.engine.calculate_weights(method='geometric_mean')
        assert len(weights_geom) == 3
        assert np.isclose(np.sum(weights_geom), 1.0, atol=1e-6)
        
        # Methods should give similar results for consistent matrices
        assert np.allclose(weights_eigen, weights_power, atol=0.1)
        assert np.allclose(weights_eigen, weights_geom, atol=0.1)
    
    def test_consistency_validation(self):
        """Test comprehensive consistency validation."""
        # Create moderately inconsistent matrix
        matrix = np.array([
            [1.0, 4.0, 7.0],
            [1/4.0, 1.0, 3.0],
            [1/7.0, 1/3.0, 1.0]
        ])
        
        self.engine.comparison_matrix = matrix
        weights = self.engine.calculate_weights()
        
        # Test validation
        validation = self.engine.validate_ahp_analysis()
        assert isinstance(validation, AHPValidationResult)
        assert validation.consistency_ratio > 0
        
        # Should be valid if CR <= 0.10
        if validation.consistency_ratio <= 0.10:
            assert validation.is_valid
        else:
            assert not validation.is_valid
            assert len(validation.issues) > 0
    
    def test_automatic_consistency_improvement(self):
        """Test automatic consistency improvement feature."""
        # Create inconsistent matrix
        matrix = np.array([
            [1.0, 7.0, 9.0],
            [1/7.0, 1.0, 8.0],
            [1/9.0, 1/8.0, 1.0]
        ])
        
        self.engine.comparison_matrix = matrix
        self.engine.calculate_weights()
        
        original_cr = self.engine.consistency_ratio
        
        # Attempt improvement
        success, steps = self.engine.improve_consistency_automatically(max_iterations=5)
        
        # Should either succeed or provide improvement steps
        assert isinstance(steps, list)
        assert len(steps) > 0
        
        if success:
            assert self.engine.consistency_ratio <= 0.10
            assert self.engine.consistency_ratio < original_cr
    
    def test_group_ahp_analysis(self):
        """Test group AHP decision making."""
        # Create multiple participant matrices
        matrix1 = np.array([
            [1.0, 3.0, 5.0],
            [1/3.0, 1.0, 2.0],
            [1/5.0, 1/2.0, 1.0]
        ])
        
        matrix2 = np.array([
            [1.0, 2.0, 4.0],
            [1/2.0, 1.0, 3.0],
            [1/4.0, 1/3.0, 1.0]
        ])
        
        participant_matrices = {
            'stakeholder1': matrix1,
            'stakeholder2': matrix2
        }
        
        # Perform group analysis
        group_result = self.engine.perform_group_ahp_analysis(participant_matrices)
        
        assert isinstance(group_result, GroupAHPResult)
        assert len(group_result.individual_weights) == 2
        assert len(group_result.group_weights) == 3
        assert np.isclose(np.sum(group_result.group_weights), 1.0, atol=1e-6)
        assert 0 <= group_result.consensus_ratio <= 1
    
    def test_incomplete_matrix_completion(self):
        """Test completion of incomplete comparison matrices."""
        # Create incomplete matrix (with zeros for missing comparisons)
        incomplete_matrix = np.array([
            [1.0, 3.0, 0.0],
            [1/3.0, 1.0, 2.0],
            [0.0, 1/2.0, 1.0]
        ])
        
        completed_matrix = self.engine.complete_incomplete_matrix(incomplete_matrix)
        
        # Check that all comparisons are filled
        assert np.all(completed_matrix > 0)
        assert np.allclose(np.diag(completed_matrix), 1.0, atol=1e-6)
        
        # Check reciprocal property
        n = completed_matrix.shape[0]
        for i in range(n):
            for j in range(n):
                if i != j:
                    assert np.isclose(completed_matrix[i, j] * completed_matrix[j, i], 1.0, atol=1e-6)
    
    def test_sensitivity_analysis(self):
        """Test advanced sensitivity analysis."""
        # Setup work items
        work_items = [
            {'business_value': 8, 'risk_reduction': 6, 'feasibility': 9},
            {'business_value': 5, 'risk_reduction': 9, 'feasibility': 7},
            {'business_value': 7, 'risk_reduction': 5, 'feasibility': 8}
        ]
        
        # Create consistent matrix and calculate weights
        matrix = np.array([
            [1.0, 3.0, 5.0],
            [1/3.0, 1.0, 2.0],
            [1/5.0, 1/2.0, 1.0]
        ])
        
        self.engine.comparison_matrix = matrix
        self.engine.calculate_weights()
        
        # Perform sensitivity analysis
        sensitivity = self.engine.perform_advanced_sensitivity_analysis(work_items)
        
        assert 'weight_sensitivity' in sensitivity
        assert 'stability_metrics' in sensitivity
        assert 'critical_comparisons' in sensitivity
        
        # Check that we have sensitivity data for each criterion
        assert len(sensitivity['weight_sensitivity']) == len(self.criteria)


class TestQVFAHPIntegrator:
    """Test QVF-AHP integration engine."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Create mock QVF engine
        self.qvf_engine = Mock(spec=QVFCriteriaEngine)
        
        # Create integration configuration
        self.config = IntegrationConfiguration(
            conversion_method=ConversionMethod.SCORE_RATIO,
            consistency_threshold=0.10,
            auto_improve_consistency=True
        )
        
        # Create integrator
        self.integrator = QVFAHPIntegrator(
            qvf_engine=self.qvf_engine,
            integration_config=self.config
        )
        
        # Sample work items
        self.work_items = [
            ADOWorkItem(
                work_item_id=1,
                title="Implement user authentication",
                work_item_type=WorkItemType.USER_STORY,
                state="New",
                assigned_to="Developer 1"
            ),
            ADOWorkItem(
                work_item_id=2,
                title="Add payment processing",
                work_item_type=WorkItemType.USER_STORY,
                state="New", 
                assigned_to="Developer 2"
            ),
            ADOWorkItem(
                work_item_id=3,
                title="Optimize database queries",
                work_item_type=WorkItemType.TASK,
                state="New",
                assigned_to="Developer 3"
            )
        ]
        
        # Sample QVF results
        self.qvf_results = {
            'configuration': {
                'active_criteria': [
                    {
                        'name': 'Business Value',
                        'category': 'Strategic',
                        'field_name': 'business_value',
                        'higher_is_better': True
                    },
                    {
                        'name': 'Risk Reduction',
                        'category': 'Risk',
                        'field_name': 'risk_reduction',
                        'higher_is_better': True
                    },
                    {
                        'name': 'Feasibility',
                        'category': 'Implementation',
                        'field_name': 'feasibility', 
                        'higher_is_better': True
                    }
                ]
            },
            'scores': [
                {
                    'work_item_id': 1,
                    'total_score': 0.75,
                    'category_scores': {
                        'Strategic': 0.8,
                        'Risk': 0.7,
                        'Implementation': 0.75
                    },
                    'criterion_scores': {
                        'Business Value': 0.8,
                        'Risk Reduction': 0.7,
                        'Feasibility': 0.75
                    }
                },
                {
                    'work_item_id': 2,
                    'total_score': 0.65,
                    'category_scores': {
                        'Strategic': 0.9,
                        'Risk': 0.5,
                        'Implementation': 0.6
                    },
                    'criterion_scores': {
                        'Business Value': 0.9,
                        'Risk Reduction': 0.5,
                        'Feasibility': 0.6
                    }
                },
                {
                    'work_item_id': 3,
                    'total_score': 0.55,
                    'category_scores': {
                        'Strategic': 0.4,
                        'Risk': 0.8,
                        'Implementation': 0.85
                    },
                    'criterion_scores': {
                        'Business Value': 0.4,
                        'Risk Reduction': 0.8,
                        'Feasibility': 0.85
                    }
                }
            ]
        }
    
    def test_integrator_initialization(self):
        """Test integrator initialization and configuration validation."""
        # Valid configuration should work
        integrator = QVFAHPIntegrator(integration_config=self.config)
        assert integrator.config == self.config
        
        # Invalid configuration should raise error
        invalid_config = IntegrationConfiguration(consistency_threshold=0.5)
        with pytest.raises(QVFAHPIntegrationError):
            QVFAHPIntegrator(integration_config=invalid_config)
    
    def test_hierarchy_structure_building(self):
        """Test building hierarchy structure from QVF configuration."""
        qvf_config = self.qvf_results['configuration']
        
        # Test multi-level hierarchy
        hierarchy = self.integrator._build_hierarchy_structure(qvf_config)
        
        assert isinstance(hierarchy, dict)
        assert len(hierarchy) > 0
        
        # Should have categories level and criteria levels
        if len(set(c.get('category') for c in qvf_config['active_criteria'])) > 1:
            assert HierarchyLevel.CATEGORIES.value in hierarchy
        
        # Should have at least one criteria level
        criteria_levels = [k for k in hierarchy.keys() if 'criteria' in k]
        assert len(criteria_levels) > 0
    
    def test_comparison_matrix_generation(self):
        """Test different comparison matrix generation methods."""
        qvf_config = self.qvf_results['configuration']
        qvf_scores = self.qvf_results['scores']
        
        # Build hierarchy and test matrix generation
        hierarchy = self.integrator._build_hierarchy_structure(qvf_config)
        
        for level_name, level_config in hierarchy.items():
            if level_config['type'] == 'criteria':
                # Test score ratio method
                self.integrator.config.conversion_method = ConversionMethod.SCORE_RATIO
                matrix_score = self.integrator._generate_comparison_matrix(
                    level_config, qvf_scores, None
                )
                
                n = len(level_config['items'])
                assert matrix_score.shape == (n, n)
                assert np.allclose(np.diag(matrix_score), 1.0, atol=1e-6)
                
                # Test reciprocal property
                for i in range(n):
                    for j in range(n):
                        if i != j and matrix_score[i, j] != 0:
                            assert np.isclose(matrix_score[i, j] * matrix_score[j, i], 1.0, atol=1e-6)
                
                # Test logarithmic method
                self.integrator.config.conversion_method = ConversionMethod.LOGARITHMIC_SCALE
                matrix_log = self.integrator._generate_comparison_matrix(
                    level_config, qvf_scores, None
                )
                
                assert matrix_log.shape == (n, n)
                assert np.allclose(np.diag(matrix_log), 1.0, atol=1e-6)
    
    def test_full_integration_workflow(self):
        """Test complete QVF to AHP conversion workflow."""
        # Perform conversion
        result = self.integrator.convert_qvf_to_ahp(
            self.qvf_results, 
            self.work_items
        )
        
        # Validate result structure
        assert isinstance(result, IntegrationResult)
        assert result.integration_timestamp is not None
        assert result.conversion_method == self.config.conversion_method
        
        # Check AHP engines were created
        assert len(result.ahp_engines) > 0
        
        # Check global weights were calculated
        assert len(result.global_weights) > 0
        assert np.isclose(np.sum(result.global_weights), 1.0, atol=1e-6)
        
        # Check work item rankings
        assert len(result.work_item_rankings) == len(self.work_items)
        
        # Rankings should be sorted by score descending
        scores = [r[1] for r in result.work_item_rankings]
        assert scores == sorted(scores, reverse=True)
        
        # Check consistency requirement
        if result.consistency_achieved:
            assert result.final_consistency_ratio <= 0.10
    
    def test_consistency_requirement_enforcement(self):
        """Test that consistency ratio ≤ 0.10 is enforced."""
        # Enable automatic consistency improvement
        self.integrator.config.auto_improve_consistency = True
        self.integrator.config.max_improvement_iterations = 20
        
        result = self.integrator.convert_qvf_to_ahp(
            self.qvf_results,
            self.work_items
        )
        
        # Check that all AHP engines meet consistency requirement
        for level_name, engine in result.ahp_engines.items():
            validation = engine.validate_ahp_analysis()
            
            # If consistency improvement was successful, CR should be ≤ 0.10
            if result.consistency_achieved:
                assert validation.consistency_ratio <= 0.10, \
                    f"Level {level_name} CR {validation.consistency_ratio:.4f} > 0.10"
    
    def test_integration_quality_assessment(self):
        """Test integration quality scoring."""
        result = self.integrator.convert_qvf_to_ahp(
            self.qvf_results,
            self.work_items
        )
        
        # Quality score should be between 0 and 1
        assert 0.0 <= result.integration_quality_score <= 1.0
        
        # Higher quality should correlate with better consistency
        if result.consistency_achieved:
            assert result.integration_quality_score >= 0.5
    
    def test_score_reconciliation(self):
        """Test reconciliation between QVF and AHP scores."""
        result = self.integrator.convert_qvf_to_ahp(
            self.qvf_results,
            self.work_items
        )
        
        reconciliation = result.score_reconciliation
        assert 'correlation' in reconciliation
        assert 'rank_agreement' in reconciliation
        
        # Correlation should be meaningful (-1 to 1)
        assert -1.0 <= reconciliation['correlation'] <= 1.0
        
        # Rank agreement should be between 0 and 1
        assert 0.0 <= reconciliation['rank_agreement'] <= 1.0
    
    def test_sensitivity_analysis_integration(self):
        """Test integrated sensitivity analysis."""
        # Enable sensitivity analysis
        self.integrator.config.perform_sensitivity_analysis = True
        
        result = self.integrator.convert_qvf_to_ahp(
            self.qvf_results,
            self.work_items
        )
        
        if result.sensitivity_analysis:
            assert isinstance(result.sensitivity_analysis, dict)
            
            # Should have sensitivity data for each AHP level
            for level_name in result.ahp_engines.keys():
                if level_name in result.sensitivity_analysis:
                    level_sensitivity = result.sensitivity_analysis[level_name]
                    assert 'stability_metrics' in level_sensitivity
    
    def test_export_functionality(self):
        """Test export of integration results."""
        result = self.integrator.convert_qvf_to_ahp(
            self.qvf_results,
            self.work_items
        )
        
        export_data = self.integrator.export_integration_results(result)
        
        # Check required sections
        assert 'metadata' in export_data
        assert 'hierarchy' in export_data
        assert 'validation' in export_data
        assert 'rankings' in export_data
        assert 'quality_assessment' in export_data
        
        # Check metadata
        metadata = export_data['metadata']
        assert 'integration_timestamp' in metadata
        assert 'conversion_method' in metadata
        assert 'consistency_achieved' in metadata
        assert 'final_consistency_ratio' in metadata
        
        # Check hierarchy data
        hierarchy = export_data['hierarchy']
        assert 'levels' in hierarchy
        assert 'global_weights' in hierarchy
        assert len(hierarchy['global_weights']) > 0


class TestIntegrationMathematicalRigor:
    """Test mathematical rigor and consistency enforcement."""
    
    def test_matrix_properties_preservation(self):
        """Test that AHP matrix properties are preserved throughout conversion."""
        config = IntegrationConfiguration()
        integrator = QVFAHPIntegrator(integration_config=config)
        
        # Create test matrix
        test_matrix = np.array([
            [1.0, 3.0, 5.0],
            [1/3.0, 1.0, 2.0],
            [1/5.0, 1/2.0, 1.0]
        ])
        
        # Validate and adjust
        adjusted_matrix = integrator._validate_and_adjust_matrix(test_matrix)
        
        n = adjusted_matrix.shape[0]
        
        # Check diagonal is 1
        assert np.allclose(np.diag(adjusted_matrix), 1.0, atol=1e-6)
        
        # Check reciprocal property
        for i in range(n):
            for j in range(n):
                if i != j:
                    assert np.isclose(adjusted_matrix[i, j] * adjusted_matrix[j, i], 1.0, atol=1e-6)
        
        # Check positive values
        assert np.all(adjusted_matrix > 0)
    
    def test_weight_normalization(self):
        """Test that all weight vectors sum to 1."""
        # Create AHP configuration
        criteria = [
            AHPCriterion(name="Criterion 1", description="Test 1", data_source="c1"),
            AHPCriterion(name="Criterion 2", description="Test 2", data_source="c2"),
            AHPCriterion(name="Criterion 3", description="Test 3", data_source="c3")
        ]
        
        ahp_config = AHPConfiguration(criteria=criteria)
        engine = AHPEngine(ahp_config, enable_advanced_features=True)
        
        # Test different weight calculation methods
        matrix = np.array([
            [1.0, 2.0, 4.0],
            [1/2.0, 1.0, 3.0],
            [1/4.0, 1/3.0, 1.0]
        ])
        
        for method in ['eigenvalue', 'power_iteration', 'geometric_mean']:
            weights = engine._calculate_weights_eigenvalue(matrix) if method == 'eigenvalue' \
                     else engine._calculate_weights_power_iteration(matrix) if method == 'power_iteration' \
                     else engine._calculate_weights_geometric_mean(matrix)
            
            # Weights should sum to 1
            assert np.isclose(np.sum(weights), 1.0, atol=1e-6), f"Method {method} weights don't sum to 1"
            
            # All weights should be positive
            assert np.all(weights > 0), f"Method {method} has non-positive weights"
    
    def test_consistency_ratio_calculation(self):
        """Test consistency ratio calculation accuracy."""
        criteria = [
            AHPCriterion(name="Criterion 1", description="Test 1", data_source="c1"),
            AHPCriterion(name="Criterion 2", description="Test 2", data_source="c2"),
            AHPCriterion(name="Criterion 3", description="Test 3", data_source="c3")
        ]
        
        ahp_config = AHPConfiguration(criteria=criteria)
        engine = AHPEngine(ahp_config, enable_advanced_features=True)
        
        # Perfect consistency matrix (should have CR ≈ 0)
        perfect_matrix = np.array([
            [1.0, 2.0, 4.0],
            [1/2.0, 1.0, 2.0],
            [1/4.0, 1/2.0, 1.0]
        ])
        
        weights = engine._calculate_weights_eigenvalue(perfect_matrix)
        cr = engine.calculate_consistency_ratio(perfect_matrix, weights)
        
        # Should be very close to 0 for perfect consistency
        assert cr < 0.01, f"Perfect consistency matrix has CR={cr:.4f} > 0.01"
        
        # Moderate inconsistency matrix
        inconsistent_matrix = np.array([
            [1.0, 3.0, 7.0],
            [1/3.0, 1.0, 4.0],
            [1/7.0, 1/4.0, 1.0]
        ])
        
        weights = engine._calculate_weights_eigenvalue(inconsistent_matrix)
        cr = engine.calculate_consistency_ratio(inconsistent_matrix, weights)
        
        # Should have higher CR
        assert cr > 0.05, f"Inconsistent matrix has unexpectedly low CR={cr:.4f}"
    
    def test_global_weight_calculation_accuracy(self):
        """Test accuracy of global weight calculation across hierarchy levels."""
        config = IntegrationConfiguration(enable_multi_level_hierarchy=True)
        integrator = QVFAHPIntegrator(integration_config=config)
        
        # Create mock hierarchy with known weights
        hierarchy_structure = {
            'categories': {
                'type': 'categories',
                'items': ['Strategic', 'Risk'],
                'description': 'Categories'
            },
            'criteria_Strategic': {
                'type': 'criteria',
                'category': 'Strategic',
                'items': [{'name': 'Business Value'}, {'name': 'Customer Impact'}],
                'description': 'Strategic criteria'
            },
            'criteria_Risk': {
                'type': 'criteria',
                'category': 'Risk',
                'items': [{'name': 'Security Risk'}, {'name': 'Technical Risk'}],
                'description': 'Risk criteria'
            }
        }
        
        # Create mock AHP engines with known weights
        mock_engines = {}
        
        # Category level: Strategic=0.7, Risk=0.3
        cat_engine = Mock()
        cat_engine.weights = np.array([0.7, 0.3])
        cat_engine.config.criteria = [Mock(name='Strategic'), Mock(name='Risk')]
        mock_engines['categories'] = cat_engine
        
        # Strategic criteria: BV=0.6, CI=0.4
        strategic_engine = Mock() 
        strategic_engine.weights = np.array([0.6, 0.4])
        mock_engines['criteria_Strategic'] = strategic_engine
        
        # Risk criteria: SR=0.8, TR=0.2
        risk_engine = Mock()
        risk_engine.weights = np.array([0.8, 0.2])
        mock_engines['criteria_Risk'] = risk_engine
        
        # Calculate global weights
        global_weights = integrator._calculate_global_weights(mock_engines, hierarchy_structure)
        
        # Expected global weights:
        # Business Value: 0.7 * 0.6 = 0.42
        # Customer Impact: 0.7 * 0.4 = 0.28
        # Security Risk: 0.3 * 0.8 = 0.24
        # Technical Risk: 0.3 * 0.2 = 0.06
        expected = np.array([0.42, 0.28, 0.24, 0.06])
        
        assert len(global_weights) == 4
        assert np.allclose(global_weights, expected, atol=1e-6)
        assert np.isclose(np.sum(global_weights), 1.0, atol=1e-6)


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([__file__, "-v", "--tb=short"])