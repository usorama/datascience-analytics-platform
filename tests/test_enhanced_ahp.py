"""Enhanced tests for the enhanced AHP engine.

This test suite validates the enhanced AHP features specifically added for QVF integration,
including multi-level hierarchies, automated consistency improvement, group decision making,
and advanced sensitivity analysis.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from src.datascience_platform.ado.ahp import (
    AHPEngine, AHPConfiguration, AHPCriterion, 
    AHPValidationResult, GroupAHPResult, PairwiseComparison
)


class TestEnhancedAHPFeatures:
    """Test enhanced AHP features for QVF integration."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.criteria = [
            AHPCriterion(
                name="Business Value",
                description="Impact on business objectives",
                data_source="business_value",
                higher_is_better=True,
                normalization_method="minmax"
            ),
            AHPCriterion(
                name="Implementation Risk",
                description="Technical and resource risks",
                data_source="implementation_risk",
                higher_is_better=False,  # Lower risk is better
                normalization_method="minmax"
            ),
            AHPCriterion(
                name="Customer Impact",
                description="Effect on customer experience",
                data_source="customer_impact",
                higher_is_better=True,
                normalization_method="minmax"
            ),
            AHPCriterion(
                name="Regulatory Compliance",
                description="Compliance requirements",
                data_source="regulatory_compliance",
                higher_is_better=True,
                normalization_method="minmax"
            )
        ]
        
        self.config = AHPConfiguration(
            criteria=self.criteria,
            consistency_threshold=0.10
        )
        
        self.engine = AHPEngine(self.config, enable_advanced_features=True)
    
    def test_enhanced_initialization(self):
        """Test enhanced AHP engine initialization."""
        assert self.engine.enable_advanced_features == True
        assert self.engine.eigenvector_method == 'power_iteration'
        assert self.engine.max_iterations == 1000
        assert self.engine.tolerance == 1e-8
        assert hasattr(self.engine, 'hierarchy_levels')
        assert hasattr(self.engine, 'group_participants')
    
    def test_multiple_eigenvector_methods(self):
        """Test different eigenvector calculation methods."""
        # Create a moderately consistent comparison matrix
        matrix = np.array([
            [1.0, 3.0, 5.0, 7.0],
            [1/3.0, 1.0, 2.0, 4.0],
            [1/5.0, 1/2.0, 1.0, 2.0],
            [1/7.0, 1/4.0, 1/2.0, 1.0]
        ])
        
        self.engine.comparison_matrix = matrix
        
        # Test eigenvalue method
        weights_eigen = self.engine.calculate_weights(method='eigenvalue')
        assert len(weights_eigen) == 4
        assert np.isclose(np.sum(weights_eigen), 1.0, atol=1e-6)
        assert np.all(weights_eigen > 0)
        
        # Test power iteration method
        weights_power = self.engine.calculate_weights(method='power_iteration')
        assert len(weights_power) == 4
        assert np.isclose(np.sum(weights_power), 1.0, atol=1e-6)
        assert np.all(weights_power > 0)
        
        # Test geometric mean method
        weights_geom = self.engine.calculate_weights(method='geometric_mean')
        assert len(weights_geom) == 4
        assert np.isclose(np.sum(weights_geom), 1.0, atol=1e-6)
        assert np.all(weights_geom > 0)
        
        # Results should be reasonably similar for consistent matrices
        assert np.allclose(weights_eigen, weights_power, atol=0.05)
    
    def test_matrix_validation(self):
        """Test comprehensive matrix validation."""
        # Valid matrix
        valid_matrix = np.array([
            [1.0, 3.0, 5.0],
            [1/3.0, 1.0, 2.0],
            [1/5.0, 1/2.0, 1.0]
        ])
        assert self.engine._is_valid_comparison_matrix(valid_matrix)
        
        # Invalid matrix - not square
        invalid_matrix = np.array([
            [1.0, 3.0],
            [1/3.0, 1.0],
            [1/5.0, 1/2.0]
        ])
        assert not self.engine._is_valid_comparison_matrix(invalid_matrix)
        
        # Invalid matrix - negative values
        invalid_matrix = np.array([
            [1.0, 3.0, -2.0],
            [1/3.0, 1.0, 2.0],
            [1/2.0, 1/2.0, 1.0]
        ])
        assert not self.engine._is_valid_comparison_matrix(invalid_matrix)
        
        # Invalid matrix - diagonal not 1
        invalid_matrix = np.array([
            [2.0, 3.0, 5.0],
            [1/3.0, 1.0, 2.0],
            [1/5.0, 1/2.0, 1.0]
        ])
        assert not self.engine._is_valid_comparison_matrix(invalid_matrix)
    
    def test_comprehensive_validation(self):
        """Test comprehensive AHP validation."""
        # Create a moderately inconsistent matrix
        matrix = np.array([
            [1.0, 4.0, 7.0, 2.0],
            [1/4.0, 1.0, 3.0, 1/2.0],
            [1/7.0, 1/3.0, 1.0, 1/4.0],
            [1/2.0, 2.0, 4.0, 1.0]
        ])
        
        self.engine.comparison_matrix = matrix
        self.engine.calculate_weights()
        
        validation = self.engine.validate_ahp_analysis()
        
        assert isinstance(validation, AHPValidationResult)
        assert isinstance(validation.is_valid, bool)
        assert isinstance(validation.consistency_ratio, float)
        assert isinstance(validation.issues, list)
        assert isinstance(validation.suggestions, list)
        assert 0.0 <= validation.quality_score <= 1.0
        
        # If inconsistent, should have issues and suggestions
        if not validation.is_valid:
            assert len(validation.issues) > 0
            assert validation.consistency_ratio > self.config.consistency_threshold
    
    def test_automatic_consistency_improvement(self):
        """Test automated consistency improvement algorithm."""
        # Create an inconsistent matrix
        inconsistent_matrix = np.array([
            [1.0, 9.0, 8.0, 7.0],
            [1/9.0, 1.0, 6.0, 5.0],
            [1/8.0, 1/6.0, 1.0, 4.0],
            [1/7.0, 1/5.0, 1/4.0, 1.0]
        ])
        
        self.engine.comparison_matrix = inconsistent_matrix
        self.engine.calculate_weights()
        
        # Check initial inconsistency
        initial_cr = self.engine.consistency_ratio
        assert initial_cr > 0.10  # Should be inconsistent
        
        # Attempt to improve consistency
        success, improvement_steps = self.engine.improve_consistency_automatically(max_iterations=10)
        
        assert isinstance(success, bool)
        assert isinstance(improvement_steps, list)
        assert len(improvement_steps) > 0
        
        # If successful, consistency should be improved
        if success:
            assert self.engine.consistency_ratio <= 0.10
            assert self.engine.consistency_ratio < initial_cr
            
        # Steps should contain meaningful information
        for step in improvement_steps:
            assert isinstance(step, str)
            assert len(step) > 0
    
    def test_find_most_inconsistent_comparisons(self):
        """Test identification of most inconsistent comparisons."""
        # Create matrix with known inconsistencies
        matrix = np.array([
            [1.0, 3.0, 9.0],  # 9 is inconsistent with the pattern
            [1/3.0, 1.0, 2.0],
            [1/9.0, 1/2.0, 1.0]
        ])
        
        self.engine.comparison_matrix = matrix
        self.engine.calculate_weights()
        
        inconsistent_comparisons = self.engine._find_most_inconsistent_comparisons()
        
        assert isinstance(inconsistent_comparisons, list)
        if len(inconsistent_comparisons) > 0:
            # Each inconsistency should have required fields
            for i, j, suggested, current in inconsistent_comparisons:
                assert isinstance(i, int) and isinstance(j, int)
                assert isinstance(suggested, float) and isinstance(current, float)
                assert 0 <= i < matrix.shape[0] and 0 <= j < matrix.shape[1]
    
    def test_group_ahp_analysis_geometric_mean(self):
        """Test group AHP analysis using geometric mean method."""
        # Create participant matrices
        participant1_matrix = np.array([
            [1.0, 3.0, 5.0],
            [1/3.0, 1.0, 2.0],
            [1/5.0, 1/2.0, 1.0]
        ])
        
        participant2_matrix = np.array([
            [1.0, 2.0, 4.0],
            [1/2.0, 1.0, 3.0],
            [1/4.0, 1/3.0, 1.0]
        ])
        
        participant3_matrix = np.array([
            [1.0, 4.0, 6.0],
            [1/4.0, 1.0, 2.5],
            [1/6.0, 1/2.5, 1.0]
        ])
        
        participant_matrices = {
            'stakeholder1': participant1_matrix,
            'stakeholder2': participant2_matrix,
            'stakeholder3': participant3_matrix
        }
        
        # Reduce criteria to 3 for this test
        self.engine.config.criteria = self.criteria[:3]
        
        group_result = self.engine.perform_group_ahp_analysis(
            participant_matrices, method='geometric_mean'
        )
        
        assert isinstance(group_result, GroupAHPResult)
        assert len(group_result.individual_weights) == 3
        assert len(group_result.group_weights) == 3
        assert np.isclose(np.sum(group_result.group_weights), 1.0, atol=1e-6)
        assert 0.0 <= group_result.consensus_ratio <= 1.0
        
        # Check individual weights
        for participant_id, weights in group_result.individual_weights.items():
            assert len(weights) == 3
            assert np.isclose(np.sum(weights), 1.0, atol=1e-6)
        
        # Check consistency tracking
        for participant_id, cr in group_result.participant_consistency.items():
            assert isinstance(cr, float)
            assert cr >= 0.0
        
        # Agreement matrix should be symmetric
        agreement = group_result.agreement_matrix
        assert agreement.shape == (3, 3)
        assert np.allclose(agreement, agreement.T, atol=1e-6)  # Symmetric
        assert np.allclose(np.diag(agreement), 1.0, atol=1e-6)  # Diagonal = 1
    
    def test_group_ahp_analysis_weighted_average(self):
        """Test group AHP analysis using consistency-weighted average method."""
        # Create participant matrices with different consistency levels
        consistent_matrix = np.array([
            [1.0, 2.0, 4.0],
            [1/2.0, 1.0, 2.0],
            [1/4.0, 1/2.0, 1.0]
        ])
        
        inconsistent_matrix = np.array([
            [1.0, 5.0, 9.0],
            [1/5.0, 1.0, 7.0],
            [1/9.0, 1/7.0, 1.0]
        ])
        
        participant_matrices = {
            'consistent_stakeholder': consistent_matrix,
            'inconsistent_stakeholder': inconsistent_matrix
        }
        
        # Reduce criteria for this test
        self.engine.config.criteria = self.criteria[:3]
        
        group_result = self.engine.perform_group_ahp_analysis(
            participant_matrices, method='weighted_average'
        )
        
        assert isinstance(group_result, GroupAHPResult)
        assert len(group_result.individual_weights) == 2
        assert len(group_result.group_weights) == 3
        
        # Consistent stakeholder should have lower CR
        consistent_cr = group_result.participant_consistency['consistent_stakeholder']
        inconsistent_cr = group_result.participant_consistency['inconsistent_stakeholder']
        assert consistent_cr < inconsistent_cr
        
        # Group weights should be influenced more by consistent stakeholder
        consistent_weights = group_result.individual_weights['consistent_stakeholder']
        
        # The group weights should be closer to consistent stakeholder's weights
        # (This is a rough check - exact values depend on the weighting algorithm)
        correlation_consistent = np.corrcoef(group_result.group_weights, consistent_weights)[0, 1]
        assert not np.isnan(correlation_consistent)
    
    def test_incomplete_matrix_completion(self):
        """Test completion of matrices with missing comparisons."""
        # Create matrix with some missing comparisons (zeros)
        incomplete_matrix = np.array([
            [1.0, 3.0, 0.0, 5.0],
            [1/3.0, 1.0, 2.0, 0.0],
            [0.0, 1/2.0, 1.0, 3.0],
            [1/5.0, 0.0, 1/3.0, 1.0]
        ])
        
        completed_matrix = self.engine.complete_incomplete_matrix(incomplete_matrix)
        
        # All entries should be positive
        assert np.all(completed_matrix > 0)
        
        # Diagonal should be 1
        assert np.allclose(np.diag(completed_matrix), 1.0, atol=1e-6)
        
        # Reciprocal property should hold
        n = completed_matrix.shape[0]
        for i in range(n):
            for j in range(n):
                if i != j:
                    assert np.isclose(completed_matrix[i, j] * completed_matrix[j, i], 1.0, atol=1e-6)
        
        # Known values should be preserved
        assert np.isclose(completed_matrix[0, 1], 3.0, atol=1e-6)
        assert np.isclose(completed_matrix[1, 0], 1/3.0, atol=1e-6)
        assert np.isclose(completed_matrix[1, 2], 2.0, atol=1e-6)
        assert np.isclose(completed_matrix[2, 1], 1/2.0, atol=1e-6)
    
    def test_transitivity_estimation(self):
        """Test transitivity-based estimation of missing comparisons."""
        # Create matrix where we can test transitivity
        matrix = np.array([
            [1.0, 2.0, 0.0],  # a13 missing, should be ≈ a12 * a23 = 2 * 3 = 6
            [1/2.0, 1.0, 3.0],
            [0.0, 1/3.0, 1.0]
        ])
        
        # Test the estimation method directly
        estimated_value = self.engine._estimate_comparison_transitivity(matrix, 0, 2)
        
        if estimated_value is not None:
            # Should estimate a13 ≈ a12 * a23 = 2 * 3 = 6
            assert 4.0 <= estimated_value <= 8.0  # Allow some tolerance
        
        # Test reverse direction
        estimated_reverse = self.engine._estimate_comparison_transitivity(matrix, 2, 0)
        
        if estimated_reverse is not None:
            # Should estimate a31 ≈ a32 * a21 = (1/3) * (1/2) = 1/6
            assert 0.1 <= estimated_reverse <= 0.2
    
    def test_advanced_sensitivity_analysis(self):
        """Test comprehensive sensitivity analysis features."""
        # Create work items for testing
        work_items = [
            {
                'business_value': 8.5,
                'implementation_risk': 3.0,  # Lower is better
                'customer_impact': 7.0,
                'regulatory_compliance': 9.0
            },
            {
                'business_value': 6.0,
                'implementation_risk': 5.0,
                'customer_impact': 8.5,
                'regulatory_compliance': 6.0
            },
            {
                'business_value': 9.0,
                'implementation_risk': 2.0,
                'customer_impact': 6.5,
                'regulatory_compliance': 8.0
            },
            {
                'business_value': 7.5,
                'implementation_risk': 4.0,
                'customer_impact': 9.0,
                'regulatory_compliance': 7.0
            }
        ]
        
        # Create comparison matrix and calculate weights
        matrix = np.array([
            [1.0, 3.0, 2.0, 4.0],
            [1/3.0, 1.0, 1/2.0, 2.0],
            [1/2.0, 2.0, 1.0, 3.0],
            [1/4.0, 1/2.0, 1/3.0, 1.0]
        ])
        
        self.engine.comparison_matrix = matrix
        self.engine.calculate_weights()
        
        # Perform sensitivity analysis
        sensitivity_results = self.engine.perform_advanced_sensitivity_analysis(
            work_items, weight_perturbation=0.15
        )
        
        # Check required sections
        assert 'original_ranking' in sensitivity_results
        assert 'weight_sensitivity' in sensitivity_results
        assert 'stability_metrics' in sensitivity_results
        assert 'critical_comparisons' in sensitivity_results
        
        # Check weight sensitivity for each criterion
        weight_sensitivity = sensitivity_results['weight_sensitivity']
        assert len(weight_sensitivity) == len(self.criteria)
        
        for criterion_name, sensitivity_data in weight_sensitivity.items():
            assert isinstance(sensitivity_data, list)
            assert len(sensitivity_data) > 0
            
            for variation_result in sensitivity_data:
                assert 'variation' in variation_result
                assert 'new_weight' in variation_result
                assert 'ranking_changes' in variation_result
                assert 'kendall_tau' in variation_result
                
                # Kendall's tau should be between -1 and 1
                tau = variation_result['kendall_tau']
                assert -1.0 <= tau <= 1.0
        
        # Check stability metrics
        stability = sensitivity_results['stability_metrics']
        assert 'average_kendall_tau' in stability
        assert 'min_kendall_tau' in stability
        assert 'overall_stability_score' in stability
        
        assert 0.0 <= stability['overall_stability_score'] <= 1.0
        
        # Check critical comparisons
        critical_comps = sensitivity_results['critical_comparisons']
        assert isinstance(critical_comps, list)
        
        for comparison in critical_comps:
            assert 'criteria_pair' in comparison
            assert 'original_value' in comparison
            assert 'impact_score' in comparison
            assert comparison['impact_score'] > 0
    
    def test_matrix_completeness_calculation(self):
        """Test calculation of matrix completeness percentage."""
        # Complete matrix
        complete_matrix = np.array([
            [1.0, 2.0, 3.0],
            [1/2.0, 1.0, 4.0],
            [1/3.0, 1/4.0, 1.0]
        ])
        
        self.engine.comparison_matrix = complete_matrix
        completeness = self.engine._calculate_matrix_completeness()
        assert completeness == 1.0
        
        # Partially complete matrix
        partial_matrix = np.array([
            [1.0, 2.0, 0.0],  # Missing comparison
            [1/2.0, 1.0, 4.0],
            [0.0, 1/4.0, 1.0]  # Missing reciprocal
        ])
        
        self.engine.comparison_matrix = partial_matrix
        completeness = self.engine._calculate_matrix_completeness()
        assert 0.0 < completeness < 1.0  # Should be between 0 and 1
    
    def test_weight_balance_metrics(self):
        """Test weight distribution balance calculations."""
        # Balanced weights
        balanced_weights = np.array([0.25, 0.25, 0.25, 0.25])
        self.engine.weights = balanced_weights
        
        balance_metrics = self.engine._calculate_weight_balance()
        
        assert 'entropy' in balance_metrics
        assert 'max_weight' in balance_metrics
        assert 'min_weight' in balance_metrics
        assert 'weight_range' in balance_metrics
        assert 'coefficient_of_variation' in balance_metrics
        
        # Balanced weights should have high entropy
        assert balance_metrics['entropy'] > 1.0  # log(4) ≈ 1.39 is maximum
        assert balance_metrics['max_weight'] == 0.25
        assert balance_metrics['min_weight'] == 0.25
        assert balance_metrics['weight_range'] == 0.0
        
        # Unbalanced weights
        unbalanced_weights = np.array([0.7, 0.2, 0.05, 0.05])
        self.engine.weights = unbalanced_weights
        
        balance_metrics = self.engine._calculate_weight_balance()
        
        # Unbalanced weights should have lower entropy and higher range
        assert balance_metrics['entropy'] < 1.2  # Less than balanced case
        assert balance_metrics['max_weight'] == 0.7
        assert balance_metrics['min_weight'] == 0.05
        assert balance_metrics['weight_range'] == 0.65
        assert balance_metrics['coefficient_of_variation'] > 0
    
    def test_extreme_weights_detection(self):
        """Test detection of extreme weight distributions."""
        # Normal weights - no single weight dominates
        normal_weights = np.array([0.4, 0.3, 0.2, 0.1])
        self.engine.weights = normal_weights
        assert not self.engine._has_extreme_weights(threshold=0.8)
        
        # Extreme weights - one weight dominates
        extreme_weights = np.array([0.85, 0.05, 0.05, 0.05])
        self.engine.weights = extreme_weights
        assert self.engine._has_extreme_weights(threshold=0.8)
        
        # Test custom threshold
        assert not self.engine._has_extreme_weights(threshold=0.9)  # Higher threshold
        assert self.engine._has_extreme_weights(threshold=0.7)     # Lower threshold
    
    def test_export_enhanced_results(self):
        """Test export of enhanced AHP analysis results."""
        # Setup matrix and calculate weights
        matrix = np.array([
            [1.0, 3.0, 5.0, 2.0],
            [1/3.0, 1.0, 2.0, 1/2.0],
            [1/5.0, 1/2.0, 1.0, 1/3.0],
            [1/2.0, 2.0, 3.0, 1.0]
        ])
        
        self.engine.comparison_matrix = matrix
        self.engine.calculate_weights()
        
        # Export results
        export_data = self.engine.export_results()
        
        # Check enhanced analysis section
        analysis = export_data['analysis']
        assert 'eigenvector_method' in analysis
        assert 'matrix_completeness' in analysis
        assert 'weight_distribution_balance' in analysis
        
        assert analysis['eigenvector_method'] == self.engine.eigenvector_method
        assert isinstance(analysis['matrix_completeness'], float)
        assert 0.0 <= analysis['matrix_completeness'] <= 1.0
        
        # Check weight balance metrics
        balance = analysis['weight_distribution_balance']
        assert isinstance(balance, dict)
        assert 'entropy' in balance
        assert 'max_weight' in balance
        assert 'coefficient_of_variation' in balance


class TestAHPPerformanceAndScalability:
    """Test AHP engine performance with larger matrices."""
    
    def test_large_matrix_performance(self):
        """Test AHP performance with larger matrices (up to 15x15)."""
        # Create criteria for larger matrix
        n_criteria = 12
        criteria = []
        
        for i in range(n_criteria):
            criteria.append(AHPCriterion(
                name=f"Criterion_{i+1}",
                description=f"Test criterion {i+1}",
                data_source=f"criterion_{i+1}"
            ))
        
        config = AHPConfiguration(criteria=criteria, consistency_threshold=0.10)
        engine = AHPEngine(config, enable_advanced_features=True)
        
        # Generate random but approximately consistent matrix
        np.random.seed(42)  # For reproducibility
        base_weights = np.random.dirichlet(np.ones(n_criteria))
        
        # Create matrix from base weights with some noise
        matrix = np.eye(n_criteria)
        for i in range(n_criteria):
            for j in range(i+1, n_criteria):
                if base_weights[j] > 0:
                    ratio = base_weights[i] / base_weights[j]
                    # Add some noise but keep within AHP scale
                    noise_factor = np.random.uniform(0.8, 1.2)
                    matrix[i, j] = min(9.0, max(1/9.0, ratio * noise_factor))
                    matrix[j, i] = 1.0 / matrix[i, j]
        
        # Test weight calculation performance
        import time
        start_time = time.time()
        
        engine.comparison_matrix = matrix
        weights = engine.calculate_weights()
        
        calculation_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert calculation_time < 5.0  # 5 seconds for 12x12 matrix
        
        # Results should be valid
        assert len(weights) == n_criteria
        assert np.isclose(np.sum(weights), 1.0, atol=1e-6)
        assert np.all(weights > 0)
        
        # Consistency should be calculable
        cr = engine.calculate_consistency_ratio()
        assert isinstance(cr, float)
        assert cr >= 0.0
    
    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        # Create matrix with values close to AHP limits
        matrix = np.array([
            [1.0, 9.0, 1/9.0],
            [1/9.0, 1.0, 9.0],
            [9.0, 1/9.0, 1.0]
        ])
        
        criteria = [
            AHPCriterion(name="A", description="A", data_source="a"),
            AHPCriterion(name="B", description="B", data_source="b"),
            AHPCriterion(name="C", description="C", data_source="c")
        ]
        
        config = AHPConfiguration(criteria=criteria)
        engine = AHPEngine(config, enable_advanced_features=True)
        
        engine.comparison_matrix = matrix
        
        # Should handle extreme values without numerical issues
        weights = engine.calculate_weights()
        
        assert not np.any(np.isnan(weights))
        assert not np.any(np.isinf(weights))
        assert np.all(weights > 0)
        assert np.isclose(np.sum(weights), 1.0, atol=1e-6)
        
        # Consistency ratio should be calculable
        cr = engine.calculate_consistency_ratio()
        assert not np.isnan(cr)
        assert not np.isinf(cr)
        assert cr >= 0.0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])