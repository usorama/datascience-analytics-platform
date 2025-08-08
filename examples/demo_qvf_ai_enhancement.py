#!/usr/bin/env python3
"""QVF AI Enhancement Demo

This demo showcases the optional AI enhancement capabilities of the QVF system,
including Ollama integration, semantic analysis, and mathematical fallback.

Key Features Demonstrated:
1. Ollama health checking and model management
2. AI-powered semantic analysis of work items
3. Automatic fallback to mathematical analysis
4. Batch processing with mixed AI/fallback results
5. Performance monitoring and caching
6. Comprehensive analysis across all QVF dimensions

Requirements:
- Ollama installed and running (optional - will fallback if unavailable)
- QVF package installed: pip install -e .

Usage:
    python examples/demo_qvf_ai_enhancement.py
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add the package to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datascience_platform.qvf.ai import (
    OllamaManager,
    SemanticAnalyzer, 
    FallbackEngine,
    QVFPromptTemplates
)
from datascience_platform.qvf.ai.prompt_templates import AnalysisType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QVFAIDemo:
    """QVF AI Enhancement Demonstration."""
    
    def __init__(self):
        """Initialize demo components."""
        print("🚀 QVF AI Enhancement Demo")
        print("=" * 50)
        
        # Initialize components
        self.ollama_manager = OllamaManager()
        self.fallback_engine = FallbackEngine()
        self.analyzer = SemanticAnalyzer(
            ollama_manager=self.ollama_manager,
            fallback_engine=self.fallback_engine,
            enable_caching=True,
            max_concurrent=3
        )
        
        # Sample work items representing different scenarios
        self.sample_work_items = [
            {
                'id': 'HIGH-VALUE-001',
                'title': 'Customer Payment Platform Enhancement',
                'description': '''
                Enhance the customer payment platform to increase revenue by 15% and
                reduce payment processing costs by 20%. Implement new payment methods,
                optimize checkout flow, and add real-time fraud detection. Platform
                must handle 10,000+ transactions per minute with 99.9% uptime.
                ''',
                'acceptance_criteria': '''
                - Support Apple Pay, Google Pay, and cryptocurrency payments
                - Reduce checkout abandonment by 25%
                - Implement ML-based fraud detection with 95% accuracy
                - Maintain sub-200ms response times
                - Provide real-time analytics dashboard
                ''',
                'notes': 'Critical for Q1 revenue targets. High stakeholder visibility.'
            },
            {
                'id': 'COMPLEX-TECH-002', 
                'title': 'Distributed Microservices Migration',
                'description': '''
                Migrate monolithic e-commerce platform to cloud-native microservices
                architecture using Kubernetes. Decompose into 20+ services with
                event-driven communication. Implement distributed tracing, service mesh,
                and automated deployment pipelines. Complex data migration required.
                ''',
                'acceptance_criteria': '''
                - Decompose monolith into domain-bounded services
                - Implement CQRS and event sourcing patterns
                - Zero-downtime rolling deployments
                - Comprehensive observability and monitoring
                - Database per service pattern implementation
                ''',
                'dependencies': 'Platform team, DevOps infrastructure, data migration tools'
            },
            {
                'id': 'STRATEGIC-003',
                'title': 'AI-Powered Personalization Engine',
                'description': '''
                Build strategic AI-powered personalization engine to deliver tailored
                customer experiences across all touchpoints. Engine will use machine
                learning to analyze customer behavior, preferences, and context to
                provide real-time personalized content, product recommendations,
                and dynamic pricing. Foundation for future AI initiatives.
                ''',
                'acceptance_criteria': '''
                - Process real-time customer events at 100k+ per second
                - Deliver personalized experiences within 50ms
                - Support A/B testing and multi-armed bandit optimization
                - Provide explainable AI recommendations
                - Privacy-compliant data processing (GDPR/CCPA)
                '''
            },
            {
                'id': 'RISKY-004',
                'title': 'Third-Party Integration Hub',
                'description': '''
                Implement integration hub for connecting with 50+ third-party systems
                including ERP, CRM, payment processors, and shipping providers.
                High dependency on external APIs with varying reliability and
                performance characteristics. Requires complex error handling,
                retry logic, and data transformation capabilities.
                ''',
                'acceptance_criteria': '''
                - Support REST, SOAP, and webhook integration patterns
                - Implement circuit breaker and retry patterns
                - Data mapping and transformation engine
                - Real-time monitoring and alerting
                - Compliance with partner SLAs and rate limits
                ''',
                'dependencies': 'Multiple external vendors, legal agreements, security reviews'
            },
            {
                'id': 'SIMPLE-005',
                'title': 'User Profile UI Updates',
                'description': '''
                Update user profile interface to match new brand guidelines and
                improve user experience. Changes include new color scheme, typography,
                and layout adjustments. Simple frontend updates with no backend changes.
                ''',
                'acceptance_criteria': '''
                - Apply new brand color palette
                - Update typography to new brand fonts
                - Responsive design for mobile and tablet
                - Accessibility compliance (WCAG 2.1 AA)
                '''
            }
        ]
    
    def check_ollama_status(self) -> None:
        """Check and display Ollama status."""
        print("\n🔍 Checking Ollama Status")
        print("-" * 30)
        
        health_status = self.ollama_manager.get_health_status()
        
        print(f"Status: {health_status['status'].upper()}")
        print(f"Available Models: {health_status['available_models']}")
        print(f"Preferred Model: {health_status.get('preferred_model', 'None')}")
        
        if self.ollama_manager.is_available():
            print("✅ Ollama is available - AI analysis enabled")
            models = self.ollama_manager.get_available_models()
            for model in models:
                print(f"   📦 {model.name} ({model.parameter_size}, {model.family})")
        else:
            print("⚠️  Ollama unavailable - will use mathematical fallback")
        
        perf_stats = health_status['performance_stats']
        print(f"Performance: {perf_stats['requests']} requests, "
              f"{perf_stats['cache_hit_rate']:.1%} cache hit rate")
    
    def demonstrate_single_analysis(self) -> None:
        """Demonstrate single work item analysis."""
        print("\n📊 Single Work Item Analysis")
        print("-" * 35)
        
        work_item = self.sample_work_items[0]  # High-value payment platform
        print(f"Analyzing: {work_item['title']}")
        
        # Analyze multiple dimensions
        analysis_types = [
            AnalysisType.BUSINESS_VALUE,
            AnalysisType.STRATEGIC_ALIGNMENT,
            AnalysisType.RISK_ASSESSMENT,
            AnalysisType.COMPLEXITY_ANALYSIS
        ]
        
        # Add context for strategic alignment
        context = {
            'pi_objectives': [
                'Increase customer payment success rate',
                'Reduce operational costs',
                'Improve customer satisfaction'
            ],
            'business_outcomes': [
                'Revenue growth',
                'Cost optimization',
                'Market expansion'
            ]
        }
        
        start_time = time.time()
        results = self.analyzer.analyze_work_item(
            work_item=work_item,
            analysis_types=analysis_types,
            context=context
        )
        analysis_time = time.time() - start_time
        
        print(f"\nAnalysis completed in {analysis_time:.2f} seconds")
        print(f"Results: {len(results)} analyses")
        
        # Display results
        for result in results:
            print(f"\n🔸 {result.analysis_type.value.replace('_', ' ').title()}")
            print(f"   Score: {result.score:.2f}/1.0")
            print(f"   Confidence: {result.confidence:.2f}/1.0")
            print(f"   Method: {'AI' if result.used_ai else 'Mathematical Fallback'}")
            if result.model_used:
                print(f"   Model: {result.model_used}")
            
            # Show key insights
            if result.insights:
                print("   Key Insights:")
                for insight in result.insights[:3]:  # Show top 3
                    print(f"   • {insight}")
    
    def demonstrate_batch_analysis(self) -> None:
        """Demonstrate batch analysis of multiple work items."""
        print("\n📈 Batch Analysis")
        print("-" * 20)
        
        print(f"Analyzing {len(self.sample_work_items)} work items...")
        
        start_time = time.time()
        batch_result = self.analyzer.analyze_batch(
            work_items=self.sample_work_items,
            analysis_types=[AnalysisType.BUSINESS_VALUE, AnalysisType.RISK_ASSESSMENT]
        )
        batch_time = time.time() - start_time
        
        print(f"\nBatch analysis completed in {batch_time:.2f} seconds")
        print(f"Total Items: {batch_result.total_items}")
        print(f"Successful: {batch_result.successful_analyses}")
        print(f"Failed: {batch_result.failed_analyses}")
        print(f"AI Analyses: {batch_result.ai_analyses}")
        print(f"Fallback Analyses: {batch_result.fallback_analyses}")
        print(f"Success Rate: {batch_result.success_rate:.1%}")
        print(f"AI Usage Rate: {batch_result.ai_usage_rate:.1%}")
        
        # Show summary by work item
        print("\n📋 Work Item Summary:")
        work_item_results = {}
        for result in batch_result.results:
            if result.work_item_id not in work_item_results:
                work_item_results[result.work_item_id] = []
            work_item_results[result.work_item_id].append(result)
        
        for work_item_id, results in work_item_results.items():
            work_item = next(item for item in self.sample_work_items if item['id'] == work_item_id)
            avg_score = sum(r.score for r in results) / len(results)
            ai_count = sum(1 for r in results if r.used_ai)
            
            print(f"   {work_item_id}: {work_item['title'][:40]}...")
            print(f"      Average Score: {avg_score:.2f}, AI Usage: {ai_count}/{len(results)}")
    
    def demonstrate_comparative_analysis(self) -> None:
        """Demonstrate comparison between AI and fallback analysis."""
        print("\n⚖️  AI vs Fallback Comparison")
        print("-" * 35)
        
        work_item = self.sample_work_items[2]  # Strategic AI item
        print(f"Comparing analysis methods for: {work_item['title'][:50]}...")
        
        # Force AI analysis (if available)
        if self.ollama_manager.is_available():
            ai_results = self.analyzer.analyze_work_item(
                work_item=work_item,
                analysis_types=[AnalysisType.BUSINESS_VALUE]
            )
            ai_result = ai_results[0]
        else:
            ai_result = None
        
        # Force fallback analysis
        fallback_result_data = self.fallback_engine.analyze_work_item(
            work_item, AnalysisType.BUSINESS_VALUE
        )
        
        print("\n📊 Comparison Results:")
        
        if ai_result:
            print(f"🤖 AI Analysis:")
            print(f"   Score: {ai_result.score:.2f}")
            print(f"   Confidence: {ai_result.confidence:.2f}")
            print(f"   Model: {ai_result.model_used}")
            print(f"   Insights: {len(ai_result.insights)} generated")
            if ai_result.insights:
                print(f"   Sample: {ai_result.insights[0][:60]}...")
        else:
            print("🤖 AI Analysis: Not available (Ollama unavailable)")
        
        print(f"\n🧮 Mathematical Fallback:")
        print(f"   Score: {fallback_result_data['score']:.2f}")
        print(f"   Confidence: {fallback_result_data['confidence']:.2f}")
        print(f"   Insights: {len(fallback_result_data['insights'])} generated")
        if fallback_result_data['insights']:
            print(f"   Sample: {fallback_result_data['insights'][0][:60]}...")
        
        if ai_result:
            score_diff = abs(ai_result.score - fallback_result_data['score'])
            conf_diff = abs(ai_result.confidence - fallback_result_data['confidence'])
            print(f"\n📈 Differences:")
            print(f"   Score Difference: {score_diff:.2f}")
            print(f"   Confidence Difference: {conf_diff:.2f}")
    
    def demonstrate_prompt_engineering(self) -> None:
        """Demonstrate prompt template generation."""
        print("\n📝 Prompt Engineering")
        print("-" * 25)
        
        work_item = self.sample_work_items[0]
        analysis_type = AnalysisType.BUSINESS_VALUE
        
        system_prompt = QVFPromptTemplates.get_system_prompt(analysis_type)
        user_prompt = QVFPromptTemplates.get_analysis_prompt(analysis_type, work_item)
        options = QVFPromptTemplates.get_default_options(analysis_type)
        
        print(f"Analysis Type: {analysis_type.value.replace('_', ' ').title()}")
        print(f"System Prompt Length: {len(system_prompt)} characters")
        print(f"User Prompt Length: {len(user_prompt)} characters")
        print(f"Temperature: {options.get('temperature', 'Not set')}")
        print(f"Max Tokens: {options.get('num_predict', 'Not set')}")
        
        print(f"\n📄 System Prompt Preview:")
        print(f"   {system_prompt[:100]}...")
        
        print(f"\n📄 User Prompt Preview:")
        print(f"   {user_prompt[:200]}...")
    
    def demonstrate_performance_monitoring(self) -> None:
        """Demonstrate performance monitoring capabilities."""
        print("\n📊 Performance Monitoring")
        print("-" * 30)
        
        # Get analyzer performance stats
        analyzer_stats = self.analyzer.get_performance_stats()
        print("🔍 Semantic Analyzer Stats:")
        print(f"   Total Analyses: {analyzer_stats['total_analyses']}")
        print(f"   AI Analyses: {analyzer_stats['ai_analyses']}")
        print(f"   Fallback Analyses: {analyzer_stats['fallback_analyses']}")
        print(f"   Error Count: {analyzer_stats['error_count']}")
        print(f"   AI Usage Rate: {analyzer_stats['ai_usage_rate']:.1%}")
        print(f"   Success Rate: {analyzer_stats['success_rate']:.1%}")
        print(f"   Avg Processing Time: {analyzer_stats['avg_processing_time']:.3f}s")
        print(f"   Cache Size: {analyzer_stats['cache_size']}")
        
        # Get Ollama performance stats
        if self.ollama_manager.is_available():
            ollama_stats = self.ollama_manager.get_performance_stats()
            print(f"\n🤖 Ollama Manager Stats:")
            print(f"   Total Requests: {ollama_stats['requests_total']}")
            print(f"   Cache Hits: {ollama_stats['cache_hits']}")
            print(f"   Cache Hit Rate: {ollama_stats['cache_hit_rate']:.1%}")
            print(f"   Avg Inference Time: {ollama_stats['avg_inference_time']:.3f}s")
    
    def demonstrate_error_resilience(self) -> None:
        """Demonstrate error handling and resilience."""
        print("\n🛡️  Error Resilience")
        print("-" * 25)
        
        # Test with problematic work item
        problematic_item = {
            'id': 'ERROR-TEST-001',
            'title': '',  # Empty title
            'description': None,  # None description
            'acceptance_criteria': ''  # Empty criteria
        }
        
        print("Testing with problematic work item (empty/None fields)...")
        
        try:
            start_time = time.time()
            results = self.analyzer.analyze_work_item(
                work_item=problematic_item,
                analysis_types=[AnalysisType.BUSINESS_VALUE]
            )
            processing_time = time.time() - start_time
            
            result = results[0]
            print(f"✅ Analysis succeeded in {processing_time:.2f}s")
            print(f"   Method: {'AI' if result.used_ai else 'Mathematical Fallback'}")
            print(f"   Score: {result.score:.2f}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Error: {result.error_message or 'None'}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    
    def demonstrate_caching_efficiency(self) -> None:
        """Demonstrate caching efficiency."""
        print("\n🗄️  Caching Efficiency")
        print("-" * 25)
        
        work_item = self.sample_work_items[0]
        
        # First analysis (cache miss)
        print("First analysis (cache miss)...")
        start_time = time.time()
        results1 = self.analyzer.analyze_work_item(
            work_item=work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        time1 = time.time() - start_time
        print(f"   Time: {time1:.3f}s")
        
        # Second identical analysis (cache hit)
        print("Second identical analysis (cache hit)...")
        start_time = time.time()
        results2 = self.analyzer.analyze_work_item(
            work_item=work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        time2 = time.time() - start_time
        print(f"   Time: {time2:.3f}s")
        
        # Calculate cache effectiveness
        if time1 > 0:
            speedup = time1 / max(time2, 0.001)  # Avoid division by zero
            print(f"   Cache Speedup: {speedup:.1f}x")
        
        # Verify results are identical
        result1, result2 = results1[0], results2[0]
        identical = (result1.score == result2.score and 
                    result1.confidence == result2.confidence)
        print(f"   Results Identical: {'✅' if identical else '❌'}")
    
    def run_comprehensive_demo(self) -> None:
        """Run the comprehensive demonstration."""
        try:
            # Core demonstrations
            self.check_ollama_status()
            self.demonstrate_single_analysis()
            self.demonstrate_batch_analysis()
            self.demonstrate_comparative_analysis()
            self.demonstrate_prompt_engineering()
            self.demonstrate_performance_monitoring()
            self.demonstrate_error_resilience()
            self.demonstrate_caching_efficiency()
            
            # Final summary
            print("\n🎉 Demo Complete!")
            print("=" * 50)
            print("Key Takeaways:")
            print("• QVF AI enhancement provides semantic analysis capabilities")
            print("• Automatic fallback ensures 100% functionality without AI")
            print("• Batch processing supports large-scale analysis")
            print("• Comprehensive caching optimizes performance")
            print("• Robust error handling ensures system reliability")
            
            if self.ollama_manager.is_available():
                print("• Ollama integration enables local, privacy-preserving AI")
            else:
                print("• Mathematical fallback provides consistent analysis")
            
            print("\nTo enable AI features:")
            print("1. Install Ollama: https://ollama.ai/")
            print("2. Pull a model: ollama pull llama2:7b")
            print("3. Start Ollama service: ollama serve")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            logger.exception("Demo error")
        finally:
            # Cleanup
            if hasattr(self.analyzer, 'clear_cache'):
                cache_cleared = self.analyzer.clear_cache()
                if cache_cleared > 0:
                    print(f"\n🧹 Cleared {cache_cleared} cache entries")


def main():
    """Run the QVF AI enhancement demo."""
    demo = QVFAIDemo()
    demo.run_comprehensive_demo()


if __name__ == "__main__":
    main()