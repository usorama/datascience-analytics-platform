"""QVF Mathematical Fallback Engine

This module provides mathematical alternatives to AI-powered semantic analysis.
It ensures that the QVF system works perfectly even when Ollama is unavailable,
using keyword analysis, pattern matching, and rule-based scoring.

Key Features:
- Complete mathematical implementation of all AI features
- Keyword-based business value detection
- Pattern matching for strategic alignment
- Rule-based risk assessment
- Complexity scoring based on text analysis
- Financial impact estimation using heuristics
- Stakeholder impact analysis via keyword mapping

Architecture:
- FallbackEngine: Main orchestrator for mathematical analysis
- Domain-specific analyzers for each analysis type
- Keyword dictionaries and scoring rules
- Pattern recognition algorithms
- Confidence estimation based on signal strength
"""

import re
import math
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import Counter
import statistics

from .prompt_templates import AnalysisType

logger = logging.getLogger(__name__)


@dataclass
class KeywordPattern:
    """Represents a keyword pattern with scoring weight."""
    keywords: List[str]
    weight: float
    category: str
    confidence_boost: float = 0.0
    
    def match_score(self, text: str) -> float:
        """Calculate match score for this pattern."""
        text_lower = text.lower()
        matches = sum(1 for keyword in self.keywords if keyword.lower() in text_lower)
        if matches == 0:
            return 0.0
        
        # Calculate weighted score based on matches
        match_ratio = matches / len(self.keywords)
        return self.weight * match_ratio


class FallbackEngine:
    """Mathematical fallback engine for QVF semantic analysis.
    
    This engine provides rule-based alternatives to AI analysis,
    ensuring QVF functionality when Ollama is unavailable.
    """
    
    def __init__(self):
        """Initialize fallback engine with keyword patterns and rules."""
        self._initialize_patterns()
        self._initialize_financial_rules()
        self._initialize_complexity_factors()
        self._initialize_stakeholder_mapping()
    
    def analyze_work_item(self,
                         work_item: Dict[str, Any],
                         analysis_type: AnalysisType,
                         context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze work item using mathematical methods.
        
        Args:
            work_item: Work item data
            analysis_type: Type of analysis to perform
            context: Additional context
            
        Returns:
            Analysis result dictionary
        """
        if analysis_type == AnalysisType.BUSINESS_VALUE:
            return self._analyze_business_value(work_item, context)
        elif analysis_type == AnalysisType.STRATEGIC_ALIGNMENT:
            return self._analyze_strategic_alignment(work_item, context)
        elif analysis_type == AnalysisType.RISK_ASSESSMENT:
            return self._analyze_risk_assessment(work_item, context)
        elif analysis_type == AnalysisType.COMPLEXITY_ANALYSIS:
            return self._analyze_complexity(work_item, context)
        elif analysis_type == AnalysisType.FINANCIAL_IMPACT:
            return self._analyze_financial_impact(work_item, context)
        elif analysis_type == AnalysisType.STAKEHOLDER_IMPACT:
            return self._analyze_stakeholder_impact(work_item, context)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    def _initialize_patterns(self) -> None:
        """Initialize keyword patterns for analysis."""
        self.business_value_patterns = [
            KeywordPattern(
                keywords=["revenue", "sales", "income", "profit", "monetize", "market share"],
                weight=0.9,
                category="revenue_generation",
                confidence_boost=0.2
            ),
            KeywordPattern(
                keywords=["cost", "save", "efficiency", "optimize", "reduce", "automate"],
                weight=0.8,
                category="cost_reduction",
                confidence_boost=0.15
            ),
            KeywordPattern(
                keywords=["customer", "user", "satisfaction", "experience", "retention"],
                weight=0.85,
                category="customer_value",
                confidence_boost=0.1
            ),
            KeywordPattern(
                keywords=["competitive", "advantage", "differentiation", "innovation", "unique"],
                weight=0.75,
                category="competitive_advantage",
                confidence_boost=0.1
            ),
            KeywordPattern(
                keywords=["compliance", "regulatory", "risk", "security", "audit"],
                weight=0.7,
                category="compliance_value",
                confidence_boost=0.05
            )
        ]
        
        self.strategic_patterns = [
            KeywordPattern(
                keywords=["strategy", "strategic", "vision", "mission", "objective"],
                weight=0.9,
                category="strategic_alignment",
                confidence_boost=0.2
            ),
            KeywordPattern(
                keywords=["platform", "foundation", "architecture", "scalability"],
                weight=0.8,
                category="architectural_alignment",
                confidence_boost=0.15
            ),
            KeywordPattern(
                keywords=["capability", "competency", "skill", "knowledge", "learning"],
                weight=0.75,
                category="capability_building",
                confidence_boost=0.1
            ),
            KeywordPattern(
                keywords=["integration", "ecosystem", "partnership", "synergy"],
                weight=0.7,
                category="ecosystem_alignment",
                confidence_boost=0.1
            )
        ]
        
        self.risk_patterns = [
            KeywordPattern(
                keywords=["dependency", "dependencies", "depends", "requires", "needs"],
                weight=0.8,
                category="dependency_risk",
                confidence_boost=0.1
            ),
            KeywordPattern(
                keywords=["new", "experimental", "prototype", "poc", "unproven"],
                weight=0.85,
                category="technical_risk",
                confidence_boost=0.15
            ),
            KeywordPattern(
                keywords=["complex", "complicated", "difficult", "challenging", "intricate"],
                weight=0.75,
                category="complexity_risk",
                confidence_boost=0.1
            ),
            KeywordPattern(
                keywords=["integration", "third-party", "external", "vendor", "api"],
                weight=0.7,
                category="integration_risk",
                confidence_boost=0.1
            ),
            KeywordPattern(
                keywords=["performance", "scalability", "load", "capacity", "throughput"],
                weight=0.7,
                category="performance_risk",
                confidence_boost=0.1
            )
        ]
        
        self.complexity_patterns = [
            KeywordPattern(
                keywords=["algorithm", "machine learning", "ai", "optimization", "calculation"],
                weight=0.9,
                category="algorithmic_complexity",
                confidence_boost=0.2
            ),
            KeywordPattern(
                keywords=["database", "data model", "migration", "schema", "query"],
                weight=0.8,
                category="data_complexity",
                confidence_boost=0.15
            ),
            KeywordPattern(
                keywords=["ui", "interface", "frontend", "user experience", "design"],
                weight=0.6,
                category="ui_complexity",
                confidence_boost=0.05
            ),
            KeywordPattern(
                keywords=["integration", "api", "service", "microservice", "webhook"],
                weight=0.75,
                category="integration_complexity",
                confidence_boost=0.1
            ),
            KeywordPattern(
                keywords=["security", "authentication", "authorization", "encryption", "compliance"],
                weight=0.8,
                category="security_complexity",
                confidence_boost=0.15
            )
        ]
    
    def _initialize_financial_rules(self) -> None:
        """Initialize financial impact rules."""
        self.financial_indicators = {
            "high_revenue_impact": [
                "subscription", "pricing", "billing", "payment", "checkout", "purchase",
                "sales", "revenue", "monetization", "conversion", "funnel"
            ],
            "cost_savings": [
                "automation", "efficiency", "optimize", "reduce", "eliminate", "streamline",
                "consolidate", "standardize", "simplify"
            ],
            "investment_required": [
                "infrastructure", "platform", "tool", "system", "technology", "hardware",
                "license", "subscription", "training", "hiring"
            ],
            "roi_indicators": [
                "productivity", "throughput", "efficiency", "speed", "performance",
                "quality", "accuracy", "reliability", "availability"
            ]
        }
    
    def _initialize_complexity_factors(self) -> None:
        """Initialize complexity scoring factors."""
        self.complexity_factors = {
            "high_complexity": {
                "keywords": [
                    "algorithm", "optimization", "machine learning", "ai", "neural",
                    "distributed", "concurrent", "parallel", "real-time", "streaming",
                    "encryption", "cryptography", "security", "performance", "scalability"
                ],
                "multiplier": 2.0
            },
            "medium_complexity": {
                "keywords": [
                    "integration", "api", "database", "migration", "transformation",
                    "workflow", "business logic", "validation", "reporting", "analytics"
                ],
                "multiplier": 1.5
            },
            "low_complexity": {
                "keywords": [
                    "configuration", "ui", "frontend", "styling", "text", "content",
                    "documentation", "template", "static", "simple"
                ],
                "multiplier": 0.8
            }
        }
    
    def _initialize_stakeholder_mapping(self) -> None:
        """Initialize stakeholder impact mapping."""
        self.stakeholder_keywords = {
            "customers": [
                "customer", "user", "client", "end user", "consumer", "buyer",
                "subscriber", "member", "visitor", "guest"
            ],
            "internal_teams": [
                "team", "developer", "engineer", "designer", "analyst", "manager",
                "support", "operations", "sales", "marketing", "product"
            ],
            "executives": [
                "executive", "ceo", "cto", "cfo", "vp", "director", "leadership",
                "management", "board", "stakeholder", "sponsor"
            ],
            "partners": [
                "partner", "vendor", "supplier", "third-party", "external",
                "integration", "api", "service provider"
            ]
        }
    
    def _extract_text_features(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text features from work item."""
        # Combine all text fields
        text_parts = []
        for field in ['title', 'description', 'acceptance_criteria', 'notes']:
            value = work_item.get(field, '')
            if value and isinstance(value, str):
                text_parts.append(value)
        
        combined_text = ' '.join(text_parts).lower()
        
        # Calculate text statistics
        word_count = len(combined_text.split())
        sentence_count = len(re.findall(r'[.!?]+', combined_text))
        
        # Extract key phrases (simple n-gram analysis)
        words = re.findall(r'\b\w+\b', combined_text)
        word_freq = Counter(words)
        
        # Identify technical terms
        technical_terms = [
            word for word in words 
            if len(word) > 6 and (
                word.endswith('tion') or word.endswith('ing') or 
                word.endswith('ment') or word.endswith('able') or
                word.endswith('ity') or word.endswith('ical')
            )
        ]
        
        return {
            'combined_text': combined_text,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'word_frequency': word_freq,
            'technical_terms': technical_terms,
            'avg_word_length': sum(len(word) for word in words) / max(len(words), 1)
        }
    
    def _calculate_pattern_scores(self, text: str, patterns: List[KeywordPattern]) -> Dict[str, Any]:
        """Calculate scores for keyword patterns."""
        category_scores = {}
        total_score = 0.0
        confidence_boost = 0.0
        matched_patterns = []
        
        for pattern in patterns:
            score = pattern.match_score(text)
            if score > 0:
                category_scores[pattern.category] = score
                total_score += score
                confidence_boost += pattern.confidence_boost
                matched_patterns.append(pattern.category)
        
        # Normalize total score
        normalized_score = min(1.0, total_score)
        base_confidence = min(1.0, 0.3 + confidence_boost)
        
        return {
            'total_score': normalized_score,
            'confidence': base_confidence,
            'category_scores': category_scores,
            'matched_patterns': matched_patterns
        }
    
    def _analyze_business_value(self, work_item: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze business value using keyword patterns."""
        features = self._extract_text_features(work_item)
        pattern_result = self._calculate_pattern_scores(features['combined_text'], self.business_value_patterns)
        
        # Base score from patterns
        base_score = pattern_result['total_score']
        
        # Adjust based on text complexity (more detailed descriptions might indicate higher value)
        complexity_adjustment = min(0.2, features['word_count'] / 500)  # Up to 20% boost for detailed descriptions
        
        # Adjust based on technical terms (technical work might have different value patterns)
        technical_ratio = len(features['technical_terms']) / max(features['word_count'], 1)
        technical_adjustment = 0.1 if technical_ratio > 0.1 else 0
        
        final_score = min(1.0, base_score + complexity_adjustment + technical_adjustment)
        
        # Generate insights based on matched patterns
        insights = []
        for category, score in pattern_result['category_scores'].items():
            if score > 0.3:
                insights.append(f"Strong {category.replace('_', ' ')} indicators detected")
        
        if features['word_count'] > 100:
            insights.append("Detailed description suggests well-defined value proposition")
        
        if not insights:
            insights.append("Limited business value indicators found in description")
        
        return {
            'score': final_score,
            'confidence': pattern_result['confidence'],
            'insights': insights,
            'structured_data': {
                'business_value_score': int(final_score * 10),
                'value_drivers': [
                    {'driver': cat.replace('_', ' '), 'impact': 'High' if score > 0.7 else 'Medium' if score > 0.4 else 'Low', 'rationale': f"Score: {score:.2f}"}
                    for cat, score in pattern_result['category_scores'].items()
                ],
                'customer_impact': {
                    'direct_impact': "Detected" if 'customer_value' in pattern_result['matched_patterns'] else "Limited",
                    'indirect_impact': "Potential organizational benefits",
                    'impact_timeline': "Short-term" if final_score > 0.7 else "Medium-term"
                },
                'revenue_potential': {
                    'revenue_category': "Revenue Generation" if 'revenue_generation' in pattern_result['matched_patterns'] else "Cost Reduction" if 'cost_reduction' in pattern_result['matched_patterns'] else "Strategic",
                    'confidence': "High" if pattern_result['confidence'] > 0.7 else "Medium" if pattern_result['confidence'] > 0.4 else "Low",
                    'rationale': f"Based on keyword analysis with {pattern_result['confidence']:.1%} confidence"
                },
                'competitive_advantage': {
                    'provides_advantage': 'competitive_advantage' in pattern_result['matched_patterns'],
                    'advantage_type': "Innovation" if 'competitive_advantage' in pattern_result['matched_patterns'] else "Feature Parity",
                    'sustainability': "High" if final_score > 0.8 else "Medium"
                },
                'key_insights': insights,
                'confidence_level': int(pattern_result['confidence'] * 10)
            }
        }
    
    def _analyze_strategic_alignment(self, work_item: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze strategic alignment using keyword patterns."""
        features = self._extract_text_features(work_item)
        pattern_result = self._calculate_pattern_scores(features['combined_text'], self.strategic_patterns)
        
        # Base score from patterns
        base_score = pattern_result['total_score']
        
        # Context-based adjustments
        context_boost = 0.0
        if context:
            pi_objectives = context.get('pi_objectives', [])
            business_outcomes = context.get('business_outcomes', [])
            
            # Check alignment with PI objectives
            for objective in pi_objectives:
                if any(word in features['combined_text'] for word in objective.lower().split()):
                    context_boost += 0.1
            
            # Check alignment with business outcomes
            for outcome in business_outcomes:
                if any(word in features['combined_text'] for word in outcome.lower().split()):
                    context_boost += 0.15
        
        final_score = min(1.0, base_score + context_boost)
        
        # Generate insights
        insights = []
        for category, score in pattern_result['category_scores'].items():
            if score > 0.3:
                insights.append(f"Alignment with {category.replace('_', ' ')} detected")
        
        if context_boost > 0:
            insights.append("Explicit alignment with strategic context identified")
        
        if not insights:
            insights.append("Limited strategic alignment indicators found")
        
        return {
            'score': final_score,
            'confidence': min(1.0, pattern_result['confidence'] + (0.2 if context_boost > 0 else 0)),
            'insights': insights,
            'structured_data': {
                'strategic_alignment_score': int(final_score * 10),
                'alignment_factors': [
                    {'factor': cat.replace('_', ' '), 'alignment_strength': 'Strong' if score > 0.7 else 'Moderate' if score > 0.4 else 'Weak', 'rationale': f"Score: {score:.2f}"}
                    for cat, score in pattern_result['category_scores'].items()
                ],
                'pi_objective_alignment': [
                    {'objective': 'Context-based alignment', 'contribution_level': 'High' if context_boost > 0.2 else 'Medium' if context_boost > 0 else 'Low', 'contribution_type': 'Direct' if context_boost > 0 else 'Indirect'}
                ],
                'business_outcome_impact': [
                    {'outcome': 'Strategic outcomes', 'impact_type': 'Accelerates' if final_score > 0.7 else 'Enables' if final_score > 0.4 else 'Supports', 'impact_magnitude': 'High' if final_score > 0.7 else 'Medium'}
                ],
                'architectural_alignment': {
                    'supports_target_architecture': 'architectural_alignment' in pattern_result['matched_patterns'],
                    'architectural_impact': 'Positive' if 'architectural_alignment' in pattern_result['matched_patterns'] else 'Neutral',
                    'technical_debt_impact': 'Reduces' if 'platform' in features['combined_text'] else 'Neutral'
                },
                'portfolio_coherence': {
                    'fits_portfolio_strategy': final_score > 0.5,
                    'synergy_opportunities': ['Platform synergies' if 'platform' in features['combined_text'] else 'Process synergies'],
                    'dependency_alignment': 'Well-aligned' if final_score > 0.7 else 'Moderately-aligned' if final_score > 0.4 else 'Poorly-aligned'
                },
                'key_insights': insights,
                'confidence_level': int(min(1.0, pattern_result['confidence'] + (0.2 if context_boost > 0 else 0)) * 10)
            }
        }
    
    def _analyze_risk_assessment(self, work_item: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze risk using keyword patterns."""
        features = self._extract_text_features(work_item)
        pattern_result = self._calculate_pattern_scores(features['combined_text'], self.risk_patterns)
        
        # Base risk score (higher pattern score = higher risk)
        base_risk = pattern_result['total_score']
        
        # Complexity-based risk adjustment
        complexity_risk = min(0.3, len(features['technical_terms']) / max(features['word_count'], 1) * 2)
        
        # Length-based risk (very short descriptions might indicate unclear requirements)
        description_risk = 0.2 if features['word_count'] < 20 else 0
        
        final_risk_score = min(1.0, base_risk + complexity_risk + description_risk)
        
        # Generate insights
        insights = []
        for category, score in pattern_result['category_scores'].items():
            if score > 0.3:
                insights.append(f"Identified {category.replace('_', ' ')} concerns")
        
        if complexity_risk > 0.1:
            insights.append("Technical complexity contributes to implementation risk")
        
        if description_risk > 0:
            insights.append("Limited detail may indicate requirement uncertainty")
        
        if not insights:
            insights.append("Standard implementation risk profile")
        
        return {
            'score': final_risk_score,
            'confidence': pattern_result['confidence'],
            'insights': insights,
            'structured_data': {
                'overall_risk_score': int(final_risk_score * 10),
                'risk_factors': [
                    {
                        'risk_category': 'Technical',
                        'risk_description': cat.replace('_', ' '),
                        'probability': 'High' if score > 0.7 else 'Medium' if score > 0.4 else 'Low',
                        'impact': 'High' if score > 0.7 else 'Medium',
                        'risk_score': int(score * 10),
                        'mitigation_strategies': [f"Address {cat.replace('_', ' ')}", "Add detailed planning"]
                    }
                    for cat, score in pattern_result['category_scores'].items() if score > 0.3
                ],
                'technical_risks': [
                    {
                        'risk': 'Implementation complexity',
                        'complexity_factor': 'High' if complexity_risk > 0.2 else 'Medium' if complexity_risk > 0.1 else 'Low',
                        'skill_availability': 'Limited' if complexity_risk > 0.1 else 'Available',
                        'technology_maturity': 'Emerging' if 'experimental' in features['combined_text'] else 'Mature'
                    }
                ],
                'business_risks': [
                    {
                        'risk': 'Requirement uncertainty',
                        'market_impact': 'Low',
                        'stakeholder_impact': 'Medium' if description_risk > 0 else 'Low',
                        'timeline_sensitivity': 'Important' if final_risk_score > 0.6 else 'Flexible'
                    }
                ],
                'dependency_risks': [
                    {
                        'dependency': 'External dependencies',
                        'dependency_risk': 'High' if 'dependency_risk' in pattern_result['matched_patterns'] else 'Medium',
                        'impact_if_delayed': 'High' if final_risk_score > 0.7 else 'Medium',
                        'mitigation_options': ['Early integration', 'Fallback planning']
                    }
                ],
                'risk_mitigation_plan': {
                    'primary_mitigations': ['Detailed technical analysis', 'Prototype development', 'Stakeholder alignment'],
                    'contingency_plans': ['Alternative approaches', 'Scope reduction', 'Timeline adjustment'],
                    'monitoring_indicators': ['Technical progress', 'Integration success', 'Stakeholder feedback']
                },
                'confidence_level': int(pattern_result['confidence'] * 10)
            }
        }
    
    def _analyze_complexity(self, work_item: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze complexity using text analysis."""
        features = self._extract_text_features(work_item)
        text = features['combined_text']
        
        # Calculate complexity factors
        complexity_scores = {}
        base_complexity = 0.4  # Base complexity score
        
        for factor_name, factor_data in self.complexity_factors.items():
            keywords = factor_data['keywords']
            multiplier = factor_data['multiplier']
            
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > 0:
                factor_score = min(1.0, (matches / len(keywords)) * multiplier)
                complexity_scores[factor_name] = factor_score
                base_complexity += factor_score * 0.2
        
        # Text-based complexity indicators
        text_complexity = 0
        text_complexity += min(0.3, features['word_count'] / 1000)  # Longer descriptions = more complex
        text_complexity += min(0.2, len(features['technical_terms']) / max(features['word_count'], 1) * 5)  # Technical density
        text_complexity += min(0.1, features['avg_word_length'] / 10)  # Longer words = more complex
        
        final_complexity = min(1.0, base_complexity + text_complexity)
        
        # Confidence based on signal strength
        signal_strength = sum(complexity_scores.values()) + text_complexity
        confidence = min(1.0, 0.3 + signal_strength * 0.5)
        
        # Generate insights
        insights = []
        for factor, score in complexity_scores.items():
            if score > 0.3:
                insights.append(f"{factor.replace('_', ' ').title()} complexity detected")
        
        if features['word_count'] > 200:
            insights.append("Detailed requirements suggest comprehensive implementation")
        
        if len(features['technical_terms']) > features['word_count'] * 0.1:
            insights.append("High density of technical terms indicates complexity")
        
        if not insights:
            insights.append("Standard implementation complexity expected")
        
        return {
            'score': final_complexity,
            'confidence': confidence,
            'insights': insights,
            'structured_data': {
                'complexity_score': int(final_complexity * 10),
                'complexity_factors': [
                    {
                        'factor': factor.replace('_', ' '),
                        'complexity_level': 'High' if score > 0.7 else 'Medium' if score > 0.4 else 'Low',
                        'rationale': f"Keyword analysis score: {score:.2f}",
                        'effort_multiplier': score
                    }
                    for factor, score in complexity_scores.items()
                ],
                'technical_complexity': {
                    'algorithmic_complexity': 'High' if 'high_complexity' in complexity_scores and complexity_scores['high_complexity'] > 0.5 else 'Medium' if 'high_complexity' in complexity_scores else 'Low',
                    'integration_complexity': 'High' if 'medium_complexity' in complexity_scores and complexity_scores['medium_complexity'] > 0.7 else 'Medium',
                    'data_complexity': 'Medium' if 'database' in text or 'data' in text else 'Low',
                    'ui_complexity': 'Low' if 'low_complexity' in complexity_scores else 'Medium',
                    'infrastructure_complexity': 'Medium' if 'infrastructure' in text else 'Low'
                },
                'skill_requirements': [
                    {
                        'skill': 'Software Development',
                        'proficiency_level': 'Advanced' if final_complexity > 0.7 else 'Intermediate',
                        'availability': 'Available',
                        'learning_curve': 'Moderate' if final_complexity > 0.6 else 'Gentle'
                    }
                ],
                'effort_estimation': {
                    'base_effort': f"{int(final_complexity * 20 + 5)} story points",
                    'complexity_multiplier': final_complexity,
                    'adjusted_effort': f"{int(final_complexity * 25 + 5)} story points",
                    'confidence': 'High' if confidence > 0.7 else 'Medium' if confidence > 0.4 else 'Low'
                },
                'implementation_challenges': [
                    {
                        'challenge': factor.replace('_', ' '),
                        'difficulty': 'High' if score > 0.7 else 'Medium',
                        'solution_approach': f"Focus on {factor.replace('_', ' ')} planning"
                    }
                    for factor, score in complexity_scores.items() if score > 0.4
                ],
                'testing_complexity': {
                    'unit_testing': 'High' if final_complexity > 0.7 else 'Medium',
                    'integration_testing': 'High' if 'integration' in text else 'Medium',
                    'performance_testing': 'Required' if 'performance' in text else 'Optional',
                    'user_acceptance_testing': 'Complex' if final_complexity > 0.8 else 'Standard'
                },
                'key_insights': insights,
                'confidence_level': int(confidence * 10)
            }
        }
    
    def _analyze_financial_impact(self, work_item: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze financial impact using heuristics."""
        features = self._extract_text_features(work_item)
        text = features['combined_text']
        
        # Score different financial impact categories
        impact_scores = {}
        for category, keywords in self.financial_indicators.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > 0:
                impact_scores[category] = min(1.0, matches / len(keywords) * 2)
        
        # Calculate overall financial impact
        revenue_impact = impact_scores.get('high_revenue_impact', 0)
        cost_savings = impact_scores.get('cost_savings', 0)
        investment_required = impact_scores.get('investment_required', 0.3)  # Assume some investment always required
        roi_potential = impact_scores.get('roi_indicators', 0)
        
        # Weighted financial score
        financial_score = (revenue_impact * 0.4 + cost_savings * 0.3 + roi_potential * 0.3) - (investment_required * 0.1)
        financial_score = max(0, min(1.0, financial_score))
        
        # Confidence based on signal clarity
        confidence = min(1.0, 0.4 + sum(impact_scores.values()) * 0.3)
        
        # Generate insights
        insights = []
        if revenue_impact > 0.3:
            insights.append("Direct revenue generation potential identified")
        if cost_savings > 0.3:
            insights.append("Cost reduction opportunities detected")
        if investment_required > 0.5:
            insights.append("Significant investment requirements indicated")
        if roi_potential > 0.3:
            insights.append("Strong ROI indicators present")
        
        if not insights:
            insights.append("Limited financial impact indicators found")
        
        return {
            'score': financial_score,
            'confidence': confidence,
            'insights': insights,
            'structured_data': {
                'financial_impact_score': int(financial_score * 10),
                'revenue_impact': {
                    'revenue_type': 'Direct Revenue' if revenue_impact > 0.5 else 'Cost Avoidance' if cost_savings > 0.5 else 'Strategic',
                    'impact_magnitude': 'High' if max(revenue_impact, cost_savings) > 0.7 else 'Medium' if max(revenue_impact, cost_savings) > 0.3 else 'Low',
                    'timeline': 'Short-term' if financial_score > 0.7 else 'Medium-term',
                    'confidence': 'High' if confidence > 0.7 else 'Medium' if confidence > 0.4 else 'Low',
                    'rationale': f"Based on keyword analysis with {confidence:.1%} confidence"
                },
                'cost_impact': {
                    'cost_category': 'Development',
                    'cost_change': 'Decrease' if cost_savings > 0.5 else 'Increase',
                    'magnitude': 'High' if investment_required > 0.7 else 'Medium' if investment_required > 0.3 else 'Low',
                    'recurring': investment_required > 0.5
                },
                'roi_indicators': [
                    {
                        'indicator': 'Efficiency gains',
                        'measurement': 'Process time reduction',
                        'expected_value': f"{int(roi_potential * 100)}% improvement potential",
                        'timeframe': '3-6 months'
                    }
                ],
                'investment_requirements': {
                    'development_cost': 'High' if investment_required > 0.7 else 'Medium' if investment_required > 0.3 else 'Low',
                    'infrastructure_cost': 'Medium' if 'infrastructure' in text else 'Low',
                    'training_cost': 'Medium' if 'training' in text or 'learning' in text else 'Low',
                    'ongoing_costs': 'Medium' if investment_required > 0.5 else 'Low'
                },
                'financial_risks': [
                    {
                        'risk': 'Investment recovery',
                        'probability': 'Medium' if investment_required > 0.5 else 'Low',
                        'potential_impact': f"{int(investment_required * 100)}% of development cost",
                        'mitigation': 'Phased implementation'
                    }
                ],
                'business_case_strength': {
                    'payback_period': 'Quick' if financial_score > 0.7 else 'Moderate' if financial_score > 0.4 else 'Long',
                    'business_justification': 'Strong' if financial_score > 0.7 else 'Moderate' if financial_score > 0.4 else 'Weak',
                    'financial_certainty': 'High' if confidence > 0.7 else 'Medium' if confidence > 0.4 else 'Low'
                },
                'key_insights': insights,
                'confidence_level': int(confidence * 10)
            }
        }
    
    def _analyze_stakeholder_impact(self, work_item: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze stakeholder impact using keyword mapping."""
        features = self._extract_text_features(work_item)
        text = features['combined_text']
        
        # Identify affected stakeholder groups
        stakeholder_impacts = {}
        for stakeholder_group, keywords in self.stakeholder_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > 0:
                impact_strength = min(1.0, matches / len(keywords) * 3)
                stakeholder_impacts[stakeholder_group] = impact_strength
        
        # Calculate overall stakeholder impact score
        total_impact = sum(stakeholder_impacts.values())
        impact_score = min(1.0, total_impact / 4)  # Normalize by max possible stakeholder groups
        
        # Confidence based on clarity of stakeholder mentions
        confidence = min(1.0, 0.3 + total_impact * 0.2)
        
        # Change complexity assessment
        change_indicators = ['change', 'new', 'replace', 'migrate', 'update', 'modify']
        change_complexity = sum(1 for indicator in change_indicators if indicator in text)
        change_level = 'High' if change_complexity > 3 else 'Medium' if change_complexity > 1 else 'Low'
        
        # Generate insights
        insights = []
        for stakeholder, impact in stakeholder_impacts.items():
            if impact > 0.3:
                insights.append(f"Significant impact on {stakeholder} identified")
        
        if change_complexity > 2:
            insights.append("Substantial change management requirements indicated")
        
        if len(stakeholder_impacts) > 2:
            insights.append("Multi-stakeholder coordination required")
        
        if not insights:
            insights.append("Limited stakeholder impact indicators found")
        
        return {
            'score': impact_score,
            'confidence': confidence,
            'insights': insights,
            'structured_data': {
                'stakeholder_impact_score': int(impact_score * 10),
                'affected_stakeholders': [
                    {
                        'stakeholder_group': group.replace('_', ' '),
                        'impact_type': 'Positive',
                        'impact_magnitude': 'High' if impact > 0.7 else 'Medium' if impact > 0.3 else 'Low',
                        'impact_description': f"Work affects {group.replace('_', ' ')} workflows",
                        'change_required': change_level
                    }
                    for group, impact in stakeholder_impacts.items()
                ],
                'customer_impact': {
                    'external_customers': {
                        'impact_type': 'Positive' if 'customers' in stakeholder_impacts else 'Neutral',
                        'impact_areas': ['User experience', 'Feature availability'],
                        'adoption_effort': change_level
                    },
                    'internal_customers': {
                        'impact_type': 'Positive' if 'internal_teams' in stakeholder_impacts else 'Neutral',
                        'affected_teams': ['Development', 'Operations'],
                        'workflow_changes': 'Major' if change_level == 'High' else 'Minor'
                    }
                },
                'organizational_impact': {
                    'process_changes': ['Workflow updates', 'Procedure modifications'] if change_complexity > 1 else [],
                    'skill_development_needs': ['Training required'] if change_level != 'Low' else [],
                    'cultural_impact': change_level,
                    'communication_complexity': change_level
                },
                'change_management': {
                    'change_readiness': 'Medium',
                    'resistance_factors': ['Learning curve', 'Process changes'] if change_level != 'Low' else [],
                    'success_factors': ['Clear communication', 'Adequate training'],
                    'communication_strategy': 'Complex' if len(stakeholder_impacts) > 2 else 'Standard'
                },
                'support_requirements': {
                    'training_needed': 'Extensive' if change_level == 'High' else 'Moderate' if change_level == 'Medium' else 'Minimal',
                    'documentation_updates': 'Extensive' if change_complexity > 2 else 'Moderate',
                    'ongoing_support': 'High' if impact_score > 0.7 else 'Medium',
                    'transition_support': 'Complex' if change_level == 'High' else 'Standard'
                },
                'stakeholder_alignment': {
                    'consensus_level': 'High' if len(stakeholder_impacts) <= 2 else 'Medium',
                    'conflicting_interests': ['Resource allocation'] if len(stakeholder_impacts) > 2 else [],
                    'alignment_strategies': ['Stakeholder workshops', 'Clear communication']
                },
                'key_insights': insights,
                'confidence_level': int(confidence * 10)
            }
        }