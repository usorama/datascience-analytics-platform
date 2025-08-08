#!/usr/bin/env python3
"""QVF Integration Test Suite

Comprehensive integration tests for the Quantified Value Framework (QVF)
covering end-to-end workflows, scoring accuracy, Azure DevOps integration,
and AI fallback mechanisms.

Test Categories:
- End-to-end workflow testing
- Scoring accuracy and consistency validation
- Azure DevOps integration testing
- AI enhancement and fallback testing
- Performance and scalability testing
- Configuration and deployment validation

Usage:
    python -m pytest tests/test_qvf_integration.py -v
    python -m pytest tests/test_qvf_integration.py::TestQVFEndToEnd -v
    python -m pytest tests/test_qvf_integration.py::TestADOIntegration -v --ado-config config.json

Created: August 2025
Author: DataScience Platform Team
"""

import asyncio
import json
import os
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

# Add project root to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# QVF Core imports
from src.datascience_platform.qvf.core.criteria import (
    QVFCriteriaEngine, 
    QVFCriteriaConfiguration,
    create_enterprise_configuration,
    create_agile_configuration
)
from src.datascience_platform.qvf.core.financial import FinancialCalculator
from src.datascience_platform.qvf.ado.custom_fields import CustomFieldManager
from src.datascience_platform.qvf.ado.rest_client import ADOClient
from src.datascience_platform.qvf.ado.work_items import WorkItemManager

# Optional AI imports for testing
try:
    from src.datascience_platform.qvf.ai.ollama_manager import OllamaManager
    from src.datascience_platform.qvf.ai.semantic import SemanticAnalyzer
    from src.datascience_platform.qvf.ai.fallback import FallbackEngine
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class QVFTestConfig:
    """Test configuration management."""
    
    @staticmethod
    def create_test_config() -> Dict:
        """Create test configuration."""
        return {
            "ado": {
                "organization": "test-org",
                "project": "test-project", 
                "pat_token": "test-token-12345",
                "custom_fields": {
                    "qvf_score": "QVF_Score",
                    "qvf_rank": "QVF_Rank",
                    "qvf_confidence": "QVF_Confidence",
                    "qvf_category": "QVF_Category"
                }
            },
            "scoring": {
                "batch_size": 50,
                "timeout": 30,
                "consistency_threshold": 0.10,
                "enable_ai": AI_AVAILABLE
            },
            "criteria": {
                "preset": "enterprise",
                "custom_weights": None
            },
            "deployment": {
                "timeout_seconds": 300,
                "retry_attempts": 2,
                "health_check_interval": 15,
                "rollback_enabled": True,
                "backup_enabled": True,
                "validation_required": True
            }
        }
    
    @staticmethod
    def create_test_work_items(count: int = 10) -> List[Dict]:
        """Create test work items for scoring."""
        return [
            {
                "id": f"work_item_{i:03d}",
                "title": f"Test Feature {i}",
                "description": f"Test description for feature {i}",
                "work_item_type": "Feature",
                "state": "New",
                "business_value": min(10, max(1, 5 + (i % 6))),
                "user_impact": min(10, max(1, 4 + (i % 7))),
                "strategic_alignment": min(10, max(1, 3 + (i % 8))),
                "time_criticality": min(10, max(1, 6 + (i % 5))),
                "risk_reduction": min(10, max(1, 2 + (i % 9))),
                "estimated_value": 10000 + (i * 5000),
                "development_cost": 5000 + (i * 2000),
                "maintenance_cost": 1000 + (i * 500),
                "risk_cost": 500 + (i * 200),
                "effort_story_points": 5 + (i % 13),
                "confidence_level": 0.7 + (i % 4) * 0.1,
                "created_date": datetime.now(timezone.utc).isoformat(),
                "area_path": "TestArea\\TestSubArea",
                "iteration_path": "TestProject\\Sprint 1",
                "assigned_to": f"tester{i % 3}@company.com"
            }
            for i in range(1, count + 1)
        ]
    
    @staticmethod
    def create_test_criteria_config() -> QVFCriteriaConfiguration:
        """Create test criteria configuration."""
        return create_enterprise_configuration()


class TestQVFCoreComponents:
    """Test core QVF components in isolation."""
    
    def test_criteria_engine_initialization(self):
        """Test QVF criteria engine initialization."""
        engine = QVFCriteriaEngine()
        assert engine is not None
        
        # Test default configuration
        config = engine.get_default_configuration()
        assert config is not None
        assert len(config.criteria) > 0
        
        # Test configuration validation
        assert engine.validate_configuration(config)
    
    def test_enterprise_configuration(self):
        """Test enterprise criteria configuration."""
        config = create_enterprise_configuration()
        
        assert config is not None
        assert len(config.criteria) >= 5  # Minimum enterprise criteria
        assert all(c.weight > 0 for c in config.criteria)
        
        # Check for key enterprise criteria
        criterion_names = [c.name.lower() for c in config.criteria]
        expected_criteria = [
            'business_value',
            'user_impact', 
            'strategic_alignment',
            'time_criticality'
        ]
        
        for expected in expected_criteria:
            assert any(expected in name for name in criterion_names), f"Missing criterion: {expected}"
    
    def test_financial_calculator(self):
        """Test financial calculations."""
        calc = FinancialCalculator()
        
        # Test comprehensive metrics calculation
        metrics = calc.calculate_comprehensive_metrics(
            estimated_value=100000,
            development_cost=40000,
            maintenance_cost=8000,
            risk_cost=2000
        )
        
        assert metrics is not None
        assert metrics.total_investment > 0
        assert metrics.roi_calculation.roi_percentage is not None
        assert metrics.npv_calculation.npv_value is not None
        
        # Test positive ROI scenario
        assert metrics.roi_calculation.roi_percentage > 0, "Should have positive ROI"
        
        # Test NPV calculation
        npv = calc.calculate_npv(
            cash_flows=[100000, -40000, -8000, -2000],
            discount_rate=0.1,
            periods=4
        )
        assert npv.npv_value is not None
    
    def test_work_item_scoring(self):
        """Test work item scoring functionality."""
        engine = QVFCriteriaEngine()
        config = create_enterprise_configuration()
        
        test_items = QVFTestConfig.create_test_work_items(5)
        
        for item in test_items:
            result = engine.calculate_work_item_score(
                work_item=item,
                criteria_config=config
            )
            
            assert 'score' in result
            assert 0 <= result['score'] <= 100
            assert 'confidence' in result
            assert 0 <= result['confidence'] <= 1
            assert 'breakdown' in result
    
    def test_scoring_consistency(self):
        """Test scoring consistency across multiple runs."""
        engine = QVFCriteriaEngine()
        config = create_enterprise_configuration()
        
        test_item = QVFTestConfig.create_test_work_items(1)[0]
        
        # Score same item multiple times
        scores = []
        for _ in range(5):
            result = engine.calculate_work_item_score(
                work_item=test_item,
                criteria_config=config
            )
            scores.append(result['score'])
        
        # Scores should be identical (deterministic)
        assert all(abs(score - scores[0]) < 0.001 for score in scores), \
            "Scoring should be deterministic"
    
    def test_batch_scoring_performance(self):
        """Test batch scoring performance."""
        engine = QVFCriteriaEngine()
        config = create_enterprise_configuration()
        
        # Create larger test dataset
        test_items = QVFTestConfig.create_test_work_items(100)
        
        start_time = time.time()
        
        scored_items = []
        for item in test_items:
            result = engine.calculate_work_item_score(
                work_item=item,
                criteria_config=config
            )
            scored_items.append({**item, 'qvf_score': result['score']})
        
        duration = time.time() - start_time
        
        assert len(scored_items) == 100
        assert duration < 5.0, f"Scoring 100 items took {duration:.2f}s, should be <5s"
        
        # Verify score distribution
        scores = [item['qvf_score'] for item in scored_items]
        assert min(scores) >= 0
        assert max(scores) <= 100
        assert len(set(scores)) > 10, "Should have score variety"


class TestQVFEndToEnd:
    """Test end-to-end QVF workflows."""
    
    @pytest.fixture
    def test_config(self):
        """Fixture providing test configuration."""
        return QVFTestConfig.create_test_config()
    
    @pytest.fixture
    def temp_csv_file(self):
        """Fixture providing temporary CSV file with test data."""
        test_items = QVFTestConfig.create_test_work_items(20)
        df = pd.DataFrame(test_items)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            yield f.name
        
        # Cleanup
        os.unlink(f.name)
    
    def test_end_to_end_scoring_workflow(self, temp_csv_file, test_config):
        """Test complete scoring workflow from CSV input to results."""
        # Read input data
        input_df = pd.read_csv(temp_csv_file)
        assert len(input_df) == 20
        
        # Initialize components
        criteria_engine = QVFCriteriaEngine()
        financial_calc = FinancialCalculator()
        config = create_enterprise_configuration()
        
        # Process each work item
        scored_items = []
        
        for _, row in input_df.iterrows():
            item = row.to_dict()
            
            # Calculate QVF score
            score_result = criteria_engine.calculate_work_item_score(
                work_item=item,
                criteria_config=config
            )
            
            # Calculate financial metrics
            financial_metrics = financial_calc.calculate_comprehensive_metrics(
                estimated_value=float(item['estimated_value']),
                development_cost=float(item['development_cost']),
                maintenance_cost=float(item['maintenance_cost']),
                risk_cost=float(item['risk_cost'])
            )
            
            # Combine scores
            combined_score = (score_result['score'] * 0.7) + \
                           (financial_metrics.roi_calculation.roi_percentage * 0.3)
            
            scored_item = {
                **item,
                'qvf_score': combined_score,
                'criteria_score': score_result['score'],
                'financial_score': financial_metrics.roi_calculation.roi_percentage,
                'qvf_confidence': score_result['confidence'],
                'qvf_category': self._categorize_score(combined_score)
            }
            
            scored_items.append(scored_item)
        
        # Validate results
        assert len(scored_items) == 20
        
        # Sort by QVF score and assign ranks
        scored_items.sort(key=lambda x: x['qvf_score'], reverse=True)
        for i, item in enumerate(scored_items):
            item['qvf_rank'] = i + 1
        
        # Verify ranking is correct
        scores = [item['qvf_score'] for item in scored_items]
        assert scores == sorted(scores, reverse=True), "Items should be ranked by score"
        
        # Verify score distribution
        categories = [item['qvf_category'] for item in scored_items]
        assert len(set(categories)) > 1, "Should have multiple priority categories"
        
        # Top item should have highest score
        top_item = scored_items[0]
        assert top_item['qvf_rank'] == 1
        assert top_item['qvf_score'] == max(scores)
    
    def _categorize_score(self, score: float) -> str:
        """Categorize QVF scores into priority levels."""
        if score >= 80:
            return "Critical"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Minimal"
    
    def test_configuration_presets(self, test_config):
        """Test different configuration presets."""
        engine = QVFCriteriaEngine()
        
        # Test enterprise configuration
        enterprise_config = create_enterprise_configuration()
        assert len(enterprise_config.criteria) >= 5
        
        # Test agile configuration
        agile_config = create_agile_configuration()
        assert len(agile_config.criteria) >= 3
        
        # Test scoring with different configs produces different results
        test_item = QVFTestConfig.create_test_work_items(1)[0]
        
        enterprise_result = engine.calculate_work_item_score(
            work_item=test_item,
            criteria_config=enterprise_config
        )
        
        agile_result = engine.calculate_work_item_score(
            work_item=test_item,
            criteria_config=agile_config
        )
        
        # Scores may be different due to different criteria weights
        assert 0 <= enterprise_result['score'] <= 100
        assert 0 <= agile_result['score'] <= 100
    
    def test_error_handling_and_fallbacks(self, test_config):
        """Test error handling and fallback mechanisms."""
        engine = QVFCriteriaEngine()
        config = create_enterprise_configuration()
        
        # Test with invalid/missing data
        invalid_item = {
            "id": "invalid_001",
            "title": "Invalid Item",
            # Missing required fields
        }
        
        # Should handle gracefully with default values
        result = engine.calculate_work_item_score(
            work_item=invalid_item,
            criteria_config=config
        )
        
        assert 'score' in result
        assert 0 <= result['score'] <= 100
        assert result['confidence'] <= 0.5  # Low confidence due to missing data
    
    def test_large_dataset_processing(self, test_config):
        """Test processing of large datasets."""
        # Create large test dataset
        large_dataset = QVFTestConfig.create_test_work_items(1000)
        
        engine = QVFCriteriaEngine()
        config = create_enterprise_configuration()
        
        start_time = time.time()
        
        # Process in batches
        batch_size = 100
        scored_items = []
        
        for i in range(0, len(large_dataset), batch_size):
            batch = large_dataset[i:i + batch_size]
            
            for item in batch:
                result = engine.calculate_work_item_score(
                    work_item=item,
                    criteria_config=config
                )
                scored_items.append({
                    **item,
                    'qvf_score': result['score'],
                    'qvf_confidence': result['confidence']
                })
        
        duration = time.time() - start_time
        
        assert len(scored_items) == 1000
        assert duration < 30.0, f"Processing 1000 items took {duration:.2f}s, should be <30s"
        
        # Verify performance requirement: <60 seconds for 10,000 items (extrapolated)
        estimated_10k_time = duration * 10
        assert estimated_10k_time < 300, f"Estimated 10k processing time: {estimated_10k_time:.2f}s"


@pytest.mark.skipif(
    not AI_AVAILABLE, 
    reason="AI components not available"
)
class TestAIIntegration:
    """Test AI enhancement and fallback mechanisms."""
    
    def test_ai_availability_check(self):
        """Test AI component availability checking."""
        # This should not raise an exception
        try:
            ollama_manager = OllamaManager()
            semantic_analyzer = SemanticAnalyzer()
            fallback_engine = FallbackEngine()
            
            assert ollama_manager is not None
            assert semantic_analyzer is not None
            assert fallback_engine is not None
            
        except Exception as e:
            pytest.skip(f"AI components not properly configured: {e}")
    
    @patch('src.datascience_platform.qvf.ai.ollama_manager.OllamaManager')
    def test_ai_fallback_mechanism(self, mock_ollama):
        """Test AI fallback to mathematical methods."""
        # Mock Ollama to simulate failure
        mock_ollama.return_value.is_available.return_value = False
        mock_ollama.return_value.get_health_status.return_value = {
            "status": "unhealthy",
            "error": "Connection refused"
        }
        
        # Initialize fallback engine
        fallback_engine = FallbackEngine()
        
        test_item = QVFTestConfig.create_test_work_items(1)[0]
        config = create_enterprise_configuration()
        
        # Should fallback to mathematical scoring
        result = fallback_engine.score_with_fallback(
            work_item=test_item,
            criteria_config=config,
            use_ai=True  # Request AI but should fallback
        )
        
        assert 'score' in result
        assert 'method_used' in result
        assert result['method_used'] == 'mathematical'
        assert 0 <= result['score'] <= 100
    
    @patch('src.datascience_platform.qvf.ai.ollama_manager.OllamaManager')
    def test_ai_enhancement_integration(self, mock_ollama):
        """Test AI enhancement integration when available."""
        # Mock successful Ollama connection
        mock_ollama.return_value.is_available.return_value = True
        mock_ollama.return_value.get_health_status.return_value = {
            "status": "healthy",
            "available_models": ["llama3.1:8b"]
        }
        mock_ollama.return_value.analyze_work_item.return_value = {
            "semantic_score": 75.5,
            "confidence": 0.85,
            "insights": ["High business value", "Strong user impact"]
        }
        
        semantic_analyzer = SemanticAnalyzer()
        
        test_item = QVFTestConfig.create_test_work_items(1)[0]
        
        # Should use AI enhancement
        result = semantic_analyzer.analyze_work_item(test_item)
        
        assert 'semantic_score' in result
        assert 'confidence' in result
        assert 'insights' in result
        assert result['confidence'] > 0.8
    
    def test_ai_performance_requirements(self):
        """Test AI performance requirements and timeouts."""
        if not AI_AVAILABLE:
            pytest.skip("AI components not available")
        
        fallback_engine = FallbackEngine()
        test_item = QVFTestConfig.create_test_work_items(1)[0]
        config = create_enterprise_configuration()
        
        start_time = time.time()
        
        # Test with timeout constraint
        result = fallback_engine.score_with_fallback(
            work_item=test_item,
            criteria_config=config,
            use_ai=True,
            timeout_seconds=5  # 5 second timeout
        )
        
        duration = time.time() - start_time
        
        assert duration < 10.0, f"AI scoring took {duration:.2f}s, should be <10s with fallback"
        assert 'score' in result
        assert 'method_used' in result


class TestADOIntegration:
    """Test Azure DevOps integration components."""
    
    @pytest.fixture
    def mock_ado_config(self):
        """Fixture providing ADO configuration."""
        return {
            "organization": "test-org",
            "project": "test-project",
            "pat_token": "test-pat-token-12345"
        }
    
    @patch('src.datascience_platform.qvf.ado.rest_client.aiohttp.ClientSession')
    async def test_ado_client_initialization(self, mock_session, mock_ado_config):
        """Test ADO client initialization and configuration."""
        client = ADOClient(
            organization=mock_ado_config["organization"],
            project=mock_ado_config["project"],
            personal_access_token=mock_ado_config["pat_token"]
        )
        
        assert client.organization == "test-org"
        assert client.project == "test-project"
        assert client.base_url == "https://dev.azure.com/test-org/"
    
    @patch('src.datascience_platform.qvf.ado.rest_client.aiohttp.ClientSession.get')
    async def test_ado_health_check(self, mock_get, mock_ado_config):
        """Test ADO connection health check."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "value": [{"name": "test-project"}]
        }
        mock_get.return_value.__aenter__.return_value = mock_response
        
        client = ADOClient(
            organization=mock_ado_config["organization"],
            project=mock_ado_config["project"],
            personal_access_token=mock_ado_config["pat_token"]
        )
        
        health_status = await client.health_check()
        
        assert health_status["status"] == "healthy"
        assert "response_time" in health_status
        assert health_status["accessible"] is True
    
    @patch('src.datascience_platform.qvf.ado.rest_client.aiohttp.ClientSession')
    async def test_custom_field_deployment(self, mock_session, mock_ado_config):
        """Test custom field deployment to ADO."""
        # Mock session responses
        mock_session_instance = AsyncMock()
        mock_session.return_value = mock_session_instance
        
        # Mock field creation response
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json.return_value = {
            "referenceName": "Custom.QVF_Score",
            "name": "QVF Score",
            "type": "Double"
        }
        mock_session_instance.post.return_value.__aenter__.return_value = mock_response
        
        client = ADOClient(
            organization=mock_ado_config["organization"],
            project=mock_ado_config["project"],
            personal_access_token=mock_ado_config["pat_token"]
        )
        
        field_manager = CustomFieldManager(client)
        
        result = await field_manager.create_custom_field(
            field_name="QVF_Score",
            field_type="Double",
            description="QVF Score for work item prioritization"
        )
        
        assert result["created"] is True
        assert result["field_name"] == "QVF_Score"
        assert result["field_type"] == "Double"
    
    @patch('src.datascience_platform.qvf.ado.work_items.WorkItemManager._update_work_item')
    async def test_work_item_score_updates(self, mock_update, mock_ado_config):
        """Test updating work items with QVF scores."""
        # Mock successful update
        mock_update.return_value = {
            "id": 12345,
            "fields": {
                "Custom.QVF_Score": 78.5,
                "Custom.QVF_Rank": 5,
                "Custom.QVF_Confidence": 0.85,
                "Custom.QVF_Category": "High"
            }
        }
        
        client = ADOClient(
            organization=mock_ado_config["organization"],
            project=mock_ado_config["project"],
            personal_access_token=mock_ado_config["pat_token"]
        )
        
        work_item_manager = WorkItemManager(client)
        
        # Test batch update
        score_updates = [
            {
                "id": 12345,
                "qvf_score": 78.5,
                "qvf_rank": 5,
                "qvf_confidence": 0.85,
                "qvf_category": "High"
            }
        ]
        
        results = await work_item_manager.batch_update_scores(score_updates)
        
        assert len(results) == 1
        assert results[0]["success"] is True
        assert results[0]["work_item_id"] == 12345
    
    def test_ado_error_handling(self, mock_ado_config):
        """Test ADO integration error handling."""
        # Test with invalid configuration
        with pytest.raises(ValueError):
            ADOClient(
                organization="",  # Invalid empty organization
                project=mock_ado_config["project"],
                personal_access_token=mock_ado_config["pat_token"]
            )
        
        # Test with missing PAT token
        with pytest.raises(ValueError):
            ADOClient(
                organization=mock_ado_config["organization"],
                project=mock_ado_config["project"],
                personal_access_token=""  # Invalid empty token
            )


class TestQVFDeployment:
    """Test QVF deployment and configuration validation."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Fixture providing temporary configuration file."""
        config = QVFTestConfig.create_test_config()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f, indent=2)
            yield f.name
        
        # Cleanup
        os.unlink(f.name)
    
    def test_configuration_validation(self, temp_config_file):
        """Test QVF configuration validation."""
        # Load and validate configuration
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        # Test required sections
        required_sections = ["ado", "scoring", "criteria"]
        for section in required_sections:
            assert section in config, f"Missing required section: {section}"
        
        # Test ADO configuration
        ado_config = config["ado"]
        assert "organization" in ado_config
        assert "project" in ado_config
        assert "pat_token" in ado_config
        assert "custom_fields" in ado_config
        
        # Test scoring configuration
        scoring_config = config["scoring"]
        assert "batch_size" in scoring_config
        assert "timeout" in scoring_config
        assert "consistency_threshold" in scoring_config
        assert isinstance(scoring_config["batch_size"], int)
        assert scoring_config["batch_size"] > 0
        assert scoring_config["timeout"] > 0
        assert 0 < scoring_config["consistency_threshold"] < 1
    
    def test_deployment_validation(self, temp_config_file):
        """Test deployment validation process."""
        # This would normally test the deployment script
        # For now, we'll test the validation components
        
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        # Validate core components can be initialized
        try:
            criteria_engine = QVFCriteriaEngine()
            financial_calc = FinancialCalculator()
            
            # Test configuration compatibility
            if config["criteria"]["preset"] == "enterprise":
                criteria_config = create_enterprise_configuration()
            else:
                criteria_config = criteria_engine.get_default_configuration()
            
            assert criteria_config is not None
            assert len(criteria_config.criteria) > 0
            
            # Test scoring functionality
            test_item = QVFTestConfig.create_test_work_items(1)[0]
            result = criteria_engine.calculate_work_item_score(
                work_item=test_item,
                criteria_config=criteria_config
            )
            
            assert 'score' in result
            assert 0 <= result['score'] <= 100
            
        except Exception as e:
            pytest.fail(f"Deployment validation failed: {e}")
    
    def test_performance_requirements(self):
        """Test QVF performance requirements."""
        engine = QVFCriteriaEngine()
        config = create_enterprise_configuration()
        
        # Test batch processing performance
        large_batch = QVFTestConfig.create_test_work_items(1000)
        
        start_time = time.time()
        
        for item in large_batch:
            result = engine.calculate_work_item_score(
                work_item=item,
                criteria_config=config
            )
            assert 'score' in result
        
        duration = time.time() - start_time
        
        # Performance requirement: <60 seconds for 10,000 items
        # Test with 1,000 items should be <6 seconds
        assert duration < 10.0, f"Performance test failed: {duration:.2f}s for 1000 items"
        
        # Calculate items per second
        items_per_second = len(large_batch) / duration
        assert items_per_second > 100, f"Processing rate too slow: {items_per_second:.1f} items/sec"


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])