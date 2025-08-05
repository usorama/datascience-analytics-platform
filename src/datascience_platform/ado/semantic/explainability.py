"""Explainable Scoring System for Strategic Alignment

This module provides comprehensive explanations for alignment scores,
making the scoring process transparent and actionable.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np

from .models import (
    SemanticWorkItem, OKR, StrategyDocument,
    AlignmentScore, TextEvidence, KeyResult
)
from .alignment import StrategicAlignmentCalculator
from .relationship_extractor import RelationshipGraph, RelationshipType


logger = logging.getLogger(__name__)


class ExplanationType(str, Enum):
    """Types of explanations."""
    SUMMARY = "summary"
    DETAILED = "detailed"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    VISUAL = "visual"
    COUNTERFACTUAL = "counterfactual"


@dataclass
class ScoringFactor:
    """Represents a single factor in scoring calculation."""
    factor_name: str
    weight: float
    raw_score: float
    weighted_score: float
    description: str
    evidence: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    
    @property
    def contribution_percentage(self) -> float:
        """Calculate this factor's contribution to total score."""
        return self.weight * 100


@dataclass
class ScoreExplanation:
    """Comprehensive explanation of an alignment score."""
    work_item_id: int
    work_item_title: str
    total_score: float
    confidence: float
    
    # Score components
    factors: List[ScoringFactor]
    
    # Explanations
    summary: str
    detailed_explanation: str
    executive_summary: str
    
    # Evidence and reasoning
    key_evidence: List[TextEvidence]
    reasoning_path: List[str]
    
    # Improvements
    improvement_suggestions: List[Dict[str, Any]]
    score_potential: float  # Maximum achievable score
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    explanation_version: str = "1.0"
    
    def to_markdown(self) -> str:
        """Generate markdown report of explanation."""
        md = []
        
        # Header
        md.append(f"# Alignment Score Explanation: {self.work_item_title}")
        md.append(f"\n**Total Score**: {self.total_score:.2f}/1.00 "
                  f"(Confidence: {self.confidence:.0%})")
        md.append(f"\n**Generated**: {self.generated_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Executive Summary
        md.append("\n## Executive Summary")
        md.append(self.executive_summary)
        
        # Score Breakdown
        md.append("\n## Score Breakdown")
        md.append("| Factor | Weight | Score | Contribution |")
        md.append("|--------|--------|-------|--------------|")
        
        for factor in sorted(self.factors, key=lambda f: f.weighted_score, reverse=True):
            md.append(f"| {factor.factor_name} | {factor.weight:.0%} | "
                     f"{factor.raw_score:.2f} | {factor.weighted_score:.2f} |")
        
        # Key Evidence
        md.append("\n## Key Evidence")
        for i, evidence in enumerate(self.key_evidence[:5], 1):
            md.append(f"\n**{i}. {evidence.source_type.title()} Evidence** "
                     f"(Relevance: {evidence.relevance_score:.2f})")
            md.append(f"> {evidence.text_excerpt}")
            md.append(f"*{evidence.explanation}*")
        
        # Improvement Opportunities
        md.append("\n## Improvement Opportunities")
        md.append(f"\n**Score Potential**: {self.score_potential:.2f}/1.00 "
                  f"(+{self.score_potential - self.total_score:.2f})")
        
        for i, suggestion in enumerate(self.improvement_suggestions[:5], 1):
            impact = suggestion.get('impact', 0)
            md.append(f"\n{i}. **{suggestion['title']}** (+{impact:.2f} points)")
            md.append(f"   - {suggestion['description']}")
            if 'actions' in suggestion:
                for action in suggestion['actions']:
                    md.append(f"   - [ ] {action}")
        
        # Detailed Explanation
        md.append("\n## Detailed Analysis")
        md.append(self.detailed_explanation)
        
        return "\n".join(md)
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            'work_item_id': self.work_item_id,
            'work_item_title': self.work_item_title,
            'total_score': self.total_score,
            'confidence': self.confidence,
            'factors': [
                {
                    'name': f.factor_name,
                    'weight': f.weight,
                    'raw_score': f.raw_score,
                    'weighted_score': f.weighted_score,
                    'description': f.description,
                    'contribution_percentage': f.contribution_percentage
                }
                for f in self.factors
            ],
            'summary': self.summary,
            'executive_summary': self.executive_summary,
            'key_evidence_count': len(self.key_evidence),
            'improvement_potential': self.score_potential - self.total_score,
            'generated_at': self.generated_at.isoformat()
        }


class ExplainableScorer:
    """Provides explainable scoring with detailed reasoning."""
    
    def __init__(
        self,
        alignment_calculator: Optional[StrategicAlignmentCalculator] = None,
        relationship_graph: Optional[RelationshipGraph] = None
    ):
        self.alignment_calculator = alignment_calculator or StrategicAlignmentCalculator()
        self.relationship_graph = relationship_graph
        
        # Scoring weights (must sum to 1.0)
        self.default_weights = {
            'strategic_alignment': 0.3,
            'okr_contribution': 0.4,
            'thematic_coherence': 0.2,
            'dependency_impact': 0.1
        }
    
    def explain_score(
        self,
        work_item: SemanticWorkItem,
        strategy_docs: List[StrategyDocument],
        okrs: List[OKR],
        explanation_type: ExplanationType = ExplanationType.DETAILED
    ) -> ScoreExplanation:
        """Generate comprehensive explanation for alignment score.
        
        Args:
            work_item: Work item to explain
            strategy_docs: Available strategy documents
            okrs: Available OKRs
            explanation_type: Type of explanation to generate
            
        Returns:
            ScoreExplanation with detailed reasoning
        """
        # Calculate alignment score if not already done
        if work_item.alignment_score is None:
            work_item.alignment_score = self.alignment_calculator.calculate_alignment(
                work_item, strategy_docs, okrs, include_evidence=True
            )
        
        score = work_item.alignment_score
        
        # Extract scoring factors
        factors = self._extract_scoring_factors(work_item, score)
        
        # Generate reasoning path
        reasoning_path = self._generate_reasoning_path(work_item, score, factors)
        
        # Calculate improvement potential
        improvements = self._analyze_improvements(work_item, strategy_docs, okrs)
        score_potential = self._calculate_score_potential(work_item, improvements)
        
        # Generate explanations based on type
        if explanation_type == ExplanationType.EXECUTIVE:
            summary = self._generate_executive_summary(work_item, score, improvements)
            detailed = ""
            executive = summary
        else:
            summary = self._generate_summary(work_item, score)
            detailed = self._generate_detailed_explanation(
                work_item, score, factors, reasoning_path
            )
            executive = self._generate_executive_summary(work_item, score, improvements)
        
        return ScoreExplanation(
            work_item_id=work_item.work_item_id,
            work_item_title=work_item.title,
            total_score=score.total_score,
            confidence=score.confidence,
            factors=factors,
            summary=summary,
            detailed_explanation=detailed,
            executive_summary=executive,
            key_evidence=score.evidence[:5],
            reasoning_path=reasoning_path,
            improvement_suggestions=improvements,
            score_potential=score_potential
        )
    
    def _extract_scoring_factors(
        self,
        work_item: SemanticWorkItem,
        score: AlignmentScore
    ) -> List[ScoringFactor]:
        """Extract individual scoring factors."""
        factors = []
        
        # Strategic Alignment Factor
        strategic_factor = ScoringFactor(
            factor_name="Strategic Alignment",
            weight=self.default_weights['strategic_alignment'],
            raw_score=score.strategic_alignment,
            weighted_score=score.strategic_alignment * self.default_weights['strategic_alignment'],
            description="Measures alignment with company strategy documents and vision",
            evidence=self._get_strategic_evidence(score),
            improvements=self._get_strategic_improvements(work_item, score)
        )
        factors.append(strategic_factor)
        
        # OKR Contribution Factor
        okr_factor = ScoringFactor(
            factor_name="OKR Contribution",
            weight=self.default_weights['okr_contribution'],
            raw_score=score.okr_contribution,
            weighted_score=score.okr_contribution * self.default_weights['okr_contribution'],
            description="Measures direct contribution to current OKRs and key results",
            evidence=self._get_okr_evidence(score),
            improvements=self._get_okr_improvements(work_item, score)
        )
        factors.append(okr_factor)
        
        # Thematic Coherence Factor
        theme_factor = ScoringFactor(
            factor_name="Thematic Coherence",
            weight=self.default_weights['thematic_coherence'],
            raw_score=score.thematic_coherence,
            weighted_score=score.thematic_coherence * self.default_weights['thematic_coherence'],
            description="Measures alignment with strategic themes and initiatives",
            evidence=[f"Themes: {', '.join(work_item.strategic_themes)}"],
            improvements=self._get_theme_improvements(work_item, score)
        )
        factors.append(theme_factor)
        
        # Dependency Impact Factor
        dependency_factor = ScoringFactor(
            factor_name="Dependency Impact",
            weight=self.default_weights['dependency_impact'],
            raw_score=score.dependency_impact,
            weighted_score=score.dependency_impact * self.default_weights['dependency_impact'],
            description="Measures the item's impact on other work through dependencies",
            evidence=self._get_dependency_evidence(work_item),
            improvements=self._get_dependency_improvements(work_item, score)
        )
        factors.append(dependency_factor)
        
        return factors
    
    def _generate_reasoning_path(
        self,
        work_item: SemanticWorkItem,
        score: AlignmentScore,
        factors: List[ScoringFactor]
    ) -> List[str]:
        """Generate step-by-step reasoning path."""
        path = []
        
        # Step 1: Work item analysis
        path.append(
            f"1. Analyzed '{work_item.title}' ({work_item.work_item_type.value}) "
            f"with {len(work_item.get_text_for_embedding().split())} words of context"
        )
        
        # Step 2: Strategic alignment check
        if score.strategic_alignment > 0.5:
            path.append(
                f"2. Found strong strategic alignment ({score.strategic_alignment:.2f}) "
                f"with {len(score.strategy_scores)} strategy documents"
            )
        else:
            path.append(
                f"2. Limited strategic alignment found ({score.strategic_alignment:.2f})"
            )
        
        # Step 3: OKR contribution check
        okr_matches = len([s for s in score.okr_scores.values() if s > 0.5])
        path.append(
            f"3. Identified contribution to {okr_matches} OKRs "
            f"(score: {score.okr_contribution:.2f})"
        )
        
        # Step 4: Theme analysis
        theme_count = len(work_item.strategic_themes)
        path.append(
            f"4. Extracted {theme_count} strategic themes "
            f"(coherence: {score.thematic_coherence:.2f})"
        )
        
        # Step 5: Dependency analysis
        if hasattr(work_item, 'children_ids') and work_item.children_ids:
            path.append(
                f"5. Item enables {len(work_item.children_ids)} child items "
                f"(impact: {score.dependency_impact:.2f})"
            )
        else:
            path.append(
                f"5. Dependency impact assessed at {score.dependency_impact:.2f}"
            )
        
        # Step 6: Final calculation
        path.append(
            f"6. Calculated weighted total score: {score.total_score:.2f} "
            f"with {score.confidence:.0%} confidence"
        )
        
        return path
    
    def _generate_summary(
        self,
        work_item: SemanticWorkItem,
        score: AlignmentScore
    ) -> str:
        """Generate concise summary explanation."""
        level = "strong" if score.total_score >= 0.7 else "moderate" if score.total_score >= 0.5 else "limited"
        
        summary = f"'{work_item.title}' shows {level} strategic alignment "
        summary += f"with a score of {score.total_score:.2f}/1.00. "
        
        # Highlight strongest factor
        if score.okr_contribution >= 0.7:
            summary += "The item strongly contributes to current OKRs. "
        elif score.strategic_alignment >= 0.7:
            summary += "The item aligns well with strategic documents. "
        elif score.total_score < 0.5:
            summary += "Consider improving strategic alignment and OKR contribution. "
        
        summary += f"Confidence in this assessment is {score.confidence:.0%}."
        
        return summary
    
    def _generate_detailed_explanation(
        self,
        work_item: SemanticWorkItem,
        score: AlignmentScore,
        factors: List[ScoringFactor],
        reasoning_path: List[str]
    ) -> str:
        """Generate detailed technical explanation."""
        explanation = []
        
        # Overview
        explanation.append("## Detailed Score Analysis\n")
        explanation.append(
            f"This {work_item.work_item_type.value} was evaluated across "
            f"{len(factors)} dimensions using semantic analysis and "
            f"strategic alignment algorithms.\n"
        )
        
        # Factor Analysis
        explanation.append("### Factor-by-Factor Analysis\n")
        
        for factor in sorted(factors, key=lambda f: f.weighted_score, reverse=True):
            explanation.append(f"**{factor.factor_name}** "
                             f"(Weight: {factor.weight:.0%}, Score: {factor.raw_score:.2f})")
            explanation.append(f"- {factor.description}")
            
            if factor.evidence:
                explanation.append("- Evidence:")
                for evidence in factor.evidence[:3]:
                    explanation.append(f"  - {evidence}")
            
            if factor.improvements:
                explanation.append("- Improvement opportunities:")
                for improvement in factor.improvements[:2]:
                    explanation.append(f"  - {improvement}")
            
            explanation.append("")
        
        # Confidence Analysis
        explanation.append("### Confidence Analysis\n")
        explanation.append(f"The {score.confidence:.0%} confidence rating is based on:")
        
        confidence_factors = []
        if work_item.has_sufficient_text():
            confidence_factors.append("✓ Sufficient text content for analysis")
        else:
            confidence_factors.append("✗ Limited text content available")
        
        if len(score.evidence) >= 3:
            confidence_factors.append(f"✓ Strong evidence ({len(score.evidence)} sources)")
        else:
            confidence_factors.append(f"✗ Limited evidence ({len(score.evidence)} sources)")
        
        for factor in confidence_factors:
            explanation.append(f"- {factor}")
        
        # Reasoning Path
        explanation.append("\n### Scoring Logic Path\n")
        for step in reasoning_path:
            explanation.append(f"- {step}")
        
        return "\n".join(explanation)
    
    def _generate_executive_summary(
        self,
        work_item: SemanticWorkItem,
        score: AlignmentScore,
        improvements: List[Dict[str, Any]]
    ) -> str:
        """Generate executive-level summary."""
        summary = []
        
        # Strategic Value Statement
        if score.total_score >= 0.7:
            summary.append(
                f"✅ **HIGH STRATEGIC VALUE**: '{work_item.title}' is well-aligned "
                f"with organizational objectives and should be prioritized."
            )
        elif score.total_score >= 0.5:
            summary.append(
                f"⚡ **MODERATE STRATEGIC VALUE**: '{work_item.title}' partially "
                f"supports strategic goals but could be better aligned."
            )
        else:
            summary.append(
                f"⚠️  **LIMITED STRATEGIC VALUE**: '{work_item.title}' shows weak "
                f"alignment with current strategy. Consider re-evaluation."
            )
        
        # Key Insights
        summary.append("\n**Key Insights:**")
        
        if score.okr_contribution >= 0.6:
            summary.append(f"• Directly contributes to quarterly OKRs")
        
        if score.strategic_alignment >= 0.6:
            summary.append(f"• Aligns with strategic initiatives")
        
        if score.dependency_impact >= 0.7:
            summary.append(f"• Enables multiple dependent work items")
        
        if score.total_score < 0.5:
            summary.append(f"• May not be the best use of resources currently")
        
        # Top Recommendation
        if improvements:
            top_improvement = improvements[0]
            summary.append(
                f"\n**Primary Recommendation:** {top_improvement['title']} "
                f"(potential +{top_improvement['impact']:.2f} score improvement)"
            )
        
        return "\n".join(summary)
    
    def _analyze_improvements(
        self,
        work_item: SemanticWorkItem,
        strategy_docs: List[StrategyDocument],
        okrs: List[OKR]
    ) -> List[Dict[str, Any]]:
        """Analyze potential improvements and their impact."""
        improvements = []
        
        # Check for missing business justification
        if not work_item.business_justification:
            improvements.append({
                'title': 'Add Business Justification',
                'description': 'Clearly articulate the business value and problem being solved',
                'impact': 0.15,
                'effort': 'low',
                'actions': [
                    'Define the specific problem this addresses',
                    'Quantify the business impact',
                    'Link to customer needs or pain points'
                ]
            })
        
        # Check for OKR alignment
        if work_item.alignment_score.okr_contribution < 0.5:
            improvements.append({
                'title': 'Strengthen OKR Alignment',
                'description': 'Explicitly connect work to current quarter OKRs',
                'impact': 0.20,
                'effort': 'medium',
                'actions': [
                    'Identify which key results this impacts',
                    'Add metrics that tie to OKR targets',
                    'Update description to reference OKRs'
                ]
            })
        
        # Check for strategic theme coverage
        if not work_item.strategic_themes:
            improvements.append({
                'title': 'Identify Strategic Themes',
                'description': 'Map work to organizational strategic themes',
                'impact': 0.10,
                'effort': 'low',
                'actions': [
                    'Review strategy documents for applicable themes',
                    'Add relevant theme tags',
                    'Ensure description uses strategic terminology'
                ]
            })
        
        # Check for metrics
        if not work_item.mentioned_metrics:
            improvements.append({
                'title': 'Define Success Metrics',
                'description': 'Add measurable success criteria',
                'impact': 0.12,
                'effort': 'medium',
                'actions': [
                    'Define quantitative success metrics',
                    'Set measurement targets',
                    'Establish tracking mechanism'
                ]
            })
        
        # Check for dependencies
        if work_item.work_item_type.value in ['Epic', 'Feature'] and not work_item.children_ids:
            improvements.append({
                'title': 'Decompose into Smaller Items',
                'description': 'Break down into manageable child items',
                'impact': 0.08,
                'effort': 'high',
                'actions': [
                    'Identify logical components',
                    'Create child features or stories',
                    'Define clear boundaries between components'
                ]
            })
        
        # Sort by impact
        improvements.sort(key=lambda x: x['impact'], reverse=True)
        
        return improvements
    
    def _calculate_score_potential(
        self,
        work_item: SemanticWorkItem,
        improvements: List[Dict[str, Any]]
    ) -> float:
        """Calculate maximum achievable score with improvements."""
        current_score = work_item.alignment_score.total_score
        
        # Sum potential improvements (with diminishing returns)
        cumulative_improvement = 0
        for i, improvement in enumerate(improvements):
            # Each subsequent improvement has 80% of its stated impact
            diminished_impact = improvement['impact'] * (0.8 ** i)
            cumulative_improvement += diminished_impact
        
        # Cap at 0.95 (perfect score is rare)
        potential_score = min(0.95, current_score + cumulative_improvement)
        
        return potential_score
    
    def _get_strategic_evidence(self, score: AlignmentScore) -> List[str]:
        """Extract strategic alignment evidence."""
        evidence = []
        
        for doc_id, similarity in score.strategy_scores.items():
            if similarity > 0.5:
                evidence.append(f"Aligns with document {doc_id} (similarity: {similarity:.2f})")
        
        return evidence[:3]
    
    def _get_okr_evidence(self, score: AlignmentScore) -> List[str]:
        """Extract OKR contribution evidence."""
        evidence = []
        
        for okr_id, similarity in score.okr_scores.items():
            if similarity > 0.5:
                evidence.append(f"Contributes to {okr_id} (score: {similarity:.2f})")
        
        return evidence[:3]
    
    def _get_dependency_evidence(self, work_item: SemanticWorkItem) -> List[str]:
        """Extract dependency evidence."""
        evidence = []
        
        if hasattr(work_item, 'parent_id') and work_item.parent_id:
            evidence.append(f"Child of item {work_item.parent_id}")
        
        if hasattr(work_item, 'children_ids') and work_item.children_ids:
            evidence.append(f"Enables {len(work_item.children_ids)} child items")
        
        if hasattr(work_item, 'blocked_days') and work_item.blocked_days:
            evidence.append(f"Blocked for {work_item.blocked_days} days")
        
        return evidence
    
    def _get_strategic_improvements(
        self,
        work_item: SemanticWorkItem,
        score: AlignmentScore
    ) -> List[str]:
        """Get strategic alignment improvements."""
        improvements = []
        
        if score.strategic_alignment < 0.5:
            improvements.append("Link work to specific strategic initiatives")
            improvements.append("Use terminology from strategy documents")
        
        return improvements
    
    def _get_okr_improvements(
        self,
        work_item: SemanticWorkItem,
        score: AlignmentScore
    ) -> List[str]:
        """Get OKR contribution improvements."""
        improvements = []
        
        if score.okr_contribution < 0.5:
            improvements.append("Explicitly reference target OKRs in description")
            improvements.append("Define how this impacts key results")
        
        return improvements
    
    def _get_theme_improvements(
        self,
        work_item: SemanticWorkItem,
        score: AlignmentScore
    ) -> List[str]:
        """Get thematic coherence improvements."""
        improvements = []
        
        if score.thematic_coherence < 0.5:
            improvements.append("Add relevant strategic theme tags")
            improvements.append("Align vocabulary with organizational themes")
        
        return improvements
    
    def _get_dependency_improvements(
        self,
        work_item: SemanticWorkItem,
        score: AlignmentScore
    ) -> List[str]:
        """Get dependency impact improvements."""
        improvements = []
        
        if score.dependency_impact < 0.5:
            improvements.append("Identify and document dependencies")
            improvements.append("Consider breaking into smaller items if too large")
        
        return improvements
    
    def generate_comparison_explanation(
        self,
        work_items: List[SemanticWorkItem],
        strategy_docs: List[StrategyDocument],
        okrs: List[OKR]
    ) -> str:
        """Generate explanation comparing multiple work items."""
        explanations = []
        
        # Score all items
        scored_items = []
        for item in work_items:
            if item.alignment_score is None:
                item.alignment_score = self.alignment_calculator.calculate_alignment(
                    item, strategy_docs, okrs
                )
            scored_items.append((item, item.alignment_score.total_score))
        
        # Sort by score
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Generate comparison
        explanations.append("# Comparative Strategic Alignment Analysis\n")
        explanations.append(f"Comparing {len(work_items)} work items:\n")
        
        # Ranking table
        explanations.append("| Rank | Work Item | Score | Strategic Value |")
        explanations.append("|------|-----------|-------|-----------------|")
        
        for i, (item, score) in enumerate(scored_items, 1):
            value = "High" if score >= 0.7 else "Medium" if score >= 0.5 else "Low"
            explanations.append(
                f"| {i} | {item.title[:40]}... | {score:.2f} | {value} |"
            )
        
        # Key differences
        explanations.append("\n## Key Differentiators\n")
        
        if scored_items:
            top_item = scored_items[0][0]
            bottom_item = scored_items[-1][0]
            
            explanations.append(f"**Highest scoring**: '{top_item.title}'")
            explanations.append(f"- Strong OKR alignment: "
                              f"{top_item.alignment_score.okr_contribution:.2f}")
            explanations.append(f"- Clear strategic fit: "
                              f"{top_item.alignment_score.strategic_alignment:.2f}")
            
            explanations.append(f"\n**Lowest scoring**: '{bottom_item.title}'")
            explanations.append(f"- Weak OKR alignment: "
                              f"{bottom_item.alignment_score.okr_contribution:.2f}")
            explanations.append(f"- Limited strategic fit: "
                              f"{bottom_item.alignment_score.strategic_alignment:.2f}")
        
        # Recommendations
        explanations.append("\n## Prioritization Recommendations\n")
        
        high_value = [item for item, score in scored_items if score >= 0.7]
        low_value = [item for item, score in scored_items if score < 0.5]
        
        if high_value:
            explanations.append(f"✅ **Prioritize** ({len(high_value)} items):")
            for item in high_value[:3]:
                explanations.append(f"   - {item.title}")
        
        if low_value:
            explanations.append(f"\n⚠️  **Consider deferring** ({len(low_value)} items):")
            for item in low_value[:3]:
                explanations.append(f"   - {item.title}")
        
        return "\n".join(explanations)
    
    def generate_visual_explanation(
        self,
        work_item: SemanticWorkItem,
        score: AlignmentScore
    ) -> Dict[str, Any]:
        """Generate data for visual explanation (charts, graphs)."""
        
        # Radar chart data
        radar_data = {
            'categories': [
                'Strategic Alignment',
                'OKR Contribution',
                'Thematic Coherence',
                'Dependency Impact'
            ],
            'values': [
                score.strategic_alignment,
                score.okr_contribution,
                score.thematic_coherence,
                score.dependency_impact
            ],
            'max_value': 1.0
        }
        
        # Score breakdown pie chart
        factors = self._extract_scoring_factors(work_item, score)
        pie_data = {
            'labels': [f.factor_name for f in factors],
            'values': [f.weighted_score for f in factors],
            'total': score.total_score
        }
        
        # Evidence distribution
        evidence_types = {}
        for evidence in score.evidence:
            evidence_types[evidence.source_type] = \
                evidence_types.get(evidence.source_type, 0) + 1
        
        evidence_data = {
            'labels': list(evidence_types.keys()),
            'values': list(evidence_types.values())
        }
        
        # Improvement impact waterfall
        improvements = self._analyze_improvements(work_item, [], [])
        waterfall_data = {
            'categories': ['Current Score'] + [imp['title'] for imp in improvements[:5]],
            'values': [score.total_score] + [imp['impact'] for imp in improvements[:5]]
        }
        
        return {
            'radar_chart': radar_data,
            'pie_chart': pie_data,
            'evidence_distribution': evidence_data,
            'improvement_waterfall': waterfall_data,
            'metadata': {
                'work_item_id': work_item.work_item_id,
                'work_item_title': work_item.title,
                'total_score': score.total_score,
                'confidence': score.confidence
            }
        }