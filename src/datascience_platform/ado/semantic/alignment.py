"""Strategic Alignment Calculator

This module calculates semantic alignment between work items,
OKRs, and strategy documents using embeddings and business logic.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict
import logging

from .models import (
    SemanticWorkItem, OKR, StrategyDocument,
    AlignmentScore, TextEvidence, Question, InformationGap,
    QuestionType
)
from .embedder import SemanticEmbedder

logger = logging.getLogger(__name__)


class StrategicAlignmentCalculator:
    """Calculate multi-level strategic alignment scores."""
    
    def __init__(
        self,
        embedder: Optional[SemanticEmbedder] = None,
        similarity_threshold: float = 0.3,
        evidence_threshold: float = 0.5
    ):
        """Initialize alignment calculator.
        
        Args:
            embedder: Semantic embedder instance
            similarity_threshold: Minimum similarity for alignment
            evidence_threshold: Minimum score for evidence inclusion
        """
        self.embedder = embedder or SemanticEmbedder()
        self.similarity_threshold = similarity_threshold
        self.evidence_threshold = evidence_threshold
    
    def calculate_alignment(
        self,
        work_item: SemanticWorkItem,
        strategy_docs: List[StrategyDocument],
        okrs: List[OKR],
        include_evidence: bool = True
    ) -> AlignmentScore:
        """Calculate comprehensive alignment score for work item.
        
        Args:
            work_item: Work item to score
            strategy_docs: Available strategy documents
            okrs: Available OKRs
            include_evidence: Whether to collect evidence
            
        Returns:
            AlignmentScore with multi-dimensional scoring
        """
        # Ensure work item has embeddings
        if work_item.combined_embedding is None:
            embeddings = self.embedder.embed_work_item(work_item)
            work_item.combined_embedding = embeddings['combined']
            work_item.title_embedding = embeddings['title']
            work_item.description_embedding = embeddings.get('description')
        
        # Calculate strategy alignment
        strategy_score, strategy_evidence = self._calculate_strategy_alignment(
            work_item, strategy_docs, include_evidence
        )
        
        # Calculate OKR contribution
        okr_score, okr_evidence = self._calculate_okr_contribution(
            work_item, okrs, include_evidence
        )
        
        # Calculate thematic coherence
        theme_score = self._calculate_thematic_coherence(
            work_item, strategy_docs, okrs
        )
        
        # Calculate dependency impact
        dependency_score = self._calculate_dependency_impact(work_item)
        
        # Calculate weighted total score
        weights = {
            'strategy': 0.3,
            'okr': 0.4,
            'theme': 0.2,
            'dependency': 0.1
        }
        
        total_score = (
            weights['strategy'] * strategy_score +
            weights['okr'] * okr_score +
            weights['theme'] * theme_score +
            weights['dependency'] * dependency_score
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            work_item,
            strategy_score,
            okr_score,
            theme_score,
            dependency_score,
            weights
        )
        
        # Combine evidence
        all_evidence = []
        if include_evidence:
            all_evidence.extend(strategy_evidence)
            all_evidence.extend(okr_evidence)
            # Sort by relevance
            all_evidence.sort(key=lambda x: x.relevance_score, reverse=True)
            all_evidence = all_evidence[:5]  # Top 5 evidence
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            work_item,
            strategy_score,
            okr_score,
            len(all_evidence)
        )
        
        return AlignmentScore(
            strategic_alignment=strategy_score,
            okr_contribution=okr_score,
            thematic_coherence=theme_score,
            dependency_impact=dependency_score,
            total_score=total_score,
            explanation=explanation,
            evidence=all_evidence,
            confidence=confidence
        )
    
    def _calculate_strategy_alignment(
        self,
        work_item: SemanticWorkItem,
        strategy_docs: List[StrategyDocument],
        include_evidence: bool
    ) -> Tuple[float, List[TextEvidence]]:
        """Calculate alignment with strategy documents."""
        if not strategy_docs:
            return 0.0, []
        
        scores = []
        evidence = []
        
        for doc in strategy_docs:
            # Ensure document has embedding
            if doc.document_embedding is None:
                doc.document_embedding = self.embedder.embed_strategy_document(doc)
            
            # Calculate similarity
            similarity = self.embedder.calculate_similarity(
                work_item.combined_embedding,
                doc.document_embedding
            )
            
            if similarity >= self.similarity_threshold:
                scores.append(similarity)
                
                # Find best matching section for evidence
                if include_evidence and similarity >= self.evidence_threshold:
                    best_section = self._find_best_section_match(work_item, doc)
                    if best_section:
                        evidence.append(TextEvidence(
                            source_type='strategy',
                            source_id=doc.doc_id,
                            text_excerpt=best_section['text'][:200],
                            relevance_score=best_section['score'],
                            explanation=f"Aligns with {doc.document_type.value}: {doc.title}"
                        ))
        
        # Use max similarity as strategy score
        strategy_score = max(scores) if scores else 0.0
        
        return strategy_score, evidence
    
    def _calculate_okr_contribution(
        self,
        work_item: SemanticWorkItem,
        okrs: List[OKR],
        include_evidence: bool
    ) -> Tuple[float, List[TextEvidence]]:
        """Calculate contribution to OKRs."""
        if not okrs:
            return 0.0, []
        
        scores = []
        evidence = []
        
        for okr in okrs:
            # Ensure OKR has embeddings
            if okr.objective_embedding is None:
                okr.objective_embedding, kr_embeddings = self.embedder.embed_okr(okr)
                # Store KR embeddings
                for kr, embedding in zip(okr.key_results, kr_embeddings):
                    kr.embedding = embedding
            
            # Calculate objective similarity
            obj_similarity = self.embedder.calculate_similarity(
                work_item.combined_embedding,
                okr.objective_embedding
            )
            
            # Calculate KR similarities
            kr_similarities = []
            for kr in okr.key_results:
                if kr.embedding is not None:
                    kr_sim = self.embedder.calculate_similarity(
                        work_item.combined_embedding,
                        kr.embedding
                    )
                    kr_similarities.append(kr_sim)
            
            # Combined OKR score (weighted average)
            if kr_similarities:
                okr_score = 0.6 * obj_similarity + 0.4 * max(kr_similarities)
            else:
                okr_score = obj_similarity
            
            if okr_score >= self.similarity_threshold:
                scores.append(okr_score)
                
                # Add evidence
                if include_evidence and okr_score >= self.evidence_threshold:
                    # Find best matching KR
                    best_kr_idx = np.argmax(kr_similarities) if kr_similarities else None
                    
                    if best_kr_idx is not None and kr_similarities[best_kr_idx] > obj_similarity:
                        # KR is better match
                        kr = okr.key_results[best_kr_idx]
                        evidence.append(TextEvidence(
                            source_type='okr',
                            source_id=okr.okr_id,
                            text_excerpt=f"KR: {kr.text}",
                            relevance_score=kr_similarities[best_kr_idx],
                            explanation=f"Contributes to {okr.level} OKR: {okr.objective_text[:50]}..."
                        ))
                    else:
                        # Objective is better match
                        evidence.append(TextEvidence(
                            source_type='okr',
                            source_id=okr.okr_id,
                            text_excerpt=okr.objective_text,
                            relevance_score=obj_similarity,
                            explanation=f"Aligns with {okr.level} objective for {okr.period}"
                        ))
        
        # Use weighted average of top scores
        if scores:
            scores.sort(reverse=True)
            top_scores = scores[:3]  # Top 3 OKRs
            okr_score = sum(top_scores) / len(top_scores)
        else:
            okr_score = 0.0
        
        return okr_score, evidence
    
    def _calculate_thematic_coherence(
        self,
        work_item: SemanticWorkItem,
        strategy_docs: List[StrategyDocument],
        okrs: List[OKR]
    ) -> float:
        """Calculate thematic coherence score."""
        # Extract all themes
        all_themes = set()
        
        # From strategy documents
        for doc in strategy_docs:
            all_themes.update(doc.strategic_themes)
        
        # From OKRs
        for okr in okrs:
            all_themes.update(okr.strategic_pillars)
        
        # From work item
        work_item_themes = set(work_item.strategic_themes)
        
        if not all_themes or not work_item_themes:
            return 0.5  # Neutral score if no themes
        
        # Calculate overlap
        overlap = work_item_themes.intersection(all_themes)
        coherence_score = len(overlap) / len(work_item_themes) if work_item_themes else 0
        
        return coherence_score
    
    def _calculate_dependency_impact(self, work_item: SemanticWorkItem) -> float:
        """Calculate dependency impact score."""
        # Simple heuristic based on work item properties
        base_score = 0.5
        
        # Higher score for epics and features (they enable other work)
        if work_item.work_item_type.value in ['Epic', 'Feature']:
            base_score += 0.3
        
        # Higher score if has many children
        if len(work_item.children_ids) > 5:
            base_score += 0.2
        elif len(work_item.children_ids) > 0:
            base_score += 0.1
        
        # Lower score if blocked
        if work_item.blocked_days and work_item.blocked_days > 5:
            base_score -= 0.2
        
        return max(0.0, min(1.0, base_score))
    
    def _find_best_section_match(
        self,
        work_item: SemanticWorkItem,
        doc: StrategyDocument
    ) -> Optional[Dict[str, Any]]:
        """Find best matching section in document."""
        best_match = None
        best_score = 0.0
        
        for section in doc.sections:
            if section.embedding is None:
                section.embedding = self.embedder.embed_text(section.content)
            
            similarity = self.embedder.calculate_similarity(
                work_item.combined_embedding,
                section.embedding
            )
            
            if similarity > best_score:
                best_score = similarity
                best_match = {
                    'section': section,
                    'score': similarity,
                    'text': section.content
                }
        
        return best_match if best_score >= self.evidence_threshold else None
    
    def _generate_explanation(
        self,
        work_item: SemanticWorkItem,
        strategy_score: float,
        okr_score: float,
        theme_score: float,
        dependency_score: float,
        weights: Dict[str, float]
    ) -> str:
        """Generate natural language explanation of scoring."""
        explanations = []
        
        # Headline
        if work_item.alignment_score and work_item.alignment_score.total_score >= 0.7:
            explanations.append(f"'{work_item.title}' shows strong strategic alignment.")
        elif work_item.alignment_score and work_item.alignment_score.total_score >= 0.5:
            explanations.append(f"'{work_item.title}' has moderate strategic alignment.")
        else:
            explanations.append(f"'{work_item.title}' has limited strategic alignment.")
        
        # Component explanations
        if okr_score >= 0.7:
            explanations.append(
                f"Strongly contributes to current OKRs (score: {okr_score:.2f}, "
                f"weight: {weights['okr']:.0%})."
            )
        elif okr_score >= 0.4:
            explanations.append(
                f"Moderately supports OKR achievement (score: {okr_score:.2f}, "
                f"weight: {weights['okr']:.0%})."
            )
        else:
            explanations.append(
                f"Limited direct OKR contribution (score: {okr_score:.2f}, "
                f"weight: {weights['okr']:.0%})."
            )
        
        if strategy_score >= 0.6:
            explanations.append(
                f"Aligns well with strategic documents (score: {strategy_score:.2f}, "
                f"weight: {weights['strategy']:.0%})."
            )
        
        if theme_score >= 0.7:
            explanations.append("Themes are highly coherent with organizational priorities.")
        elif theme_score <= 0.3:
            explanations.append("Consider aligning themes with strategic priorities.")
        
        if dependency_score >= 0.7:
            explanations.append("This item enables significant other work.")
        
        return " ".join(explanations)
    
    def _calculate_confidence(
        self,
        work_item: SemanticWorkItem,
        strategy_score: float,
        okr_score: float,
        evidence_count: int
    ) -> float:
        """Calculate confidence in the scoring."""
        confidence_factors = []
        
        # Text completeness
        if work_item.has_sufficient_text():
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.5)
        
        # Evidence availability
        if evidence_count >= 3:
            confidence_factors.append(1.0)
        elif evidence_count >= 1:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.3)
        
        # Score consistency
        score_variance = np.var([strategy_score, okr_score])
        if score_variance < 0.1:  # Scores are consistent
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.6)
        
        return np.mean(confidence_factors)


class ThemeExtractor:
    """Extract and analyze strategic themes."""
    
    def __init__(self, embedder: Optional[SemanticEmbedder] = None):
        self.embedder = embedder or SemanticEmbedder()
        
        # Predefined strategic themes with example keywords
        self.strategic_themes = {
            'customer_experience': ['customer', 'user', 'experience', 'satisfaction', 'NPS'],
            'operational_excellence': ['efficiency', 'optimize', 'automate', 'streamline', 'process'],
            'innovation': ['innovate', 'transform', 'disrupt', 'new', 'breakthrough'],
            'growth': ['growth', 'expand', 'scale', 'market', 'revenue'],
            'security_compliance': ['security', 'compliance', 'privacy', 'protection', 'risk'],
            'quality': ['quality', 'reliability', 'performance', 'stability', 'excellence'],
            'collaboration': ['collaboration', 'team', 'communication', 'partnership', 'integration'],
            'sustainability': ['sustainable', 'environment', 'social', 'responsibility', 'ESG']
        }
    
    def extract_themes(self, text: str) -> List[str]:
        """Extract strategic themes from text."""
        themes = []
        text_lower = text.lower()
        
        for theme, keywords in self.strategic_themes.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def analyze_theme_coverage(
        self,
        work_items: List[SemanticWorkItem],
        strategy_docs: List[StrategyDocument]
    ) -> Dict[str, float]:
        """Analyze how well work items cover strategic themes."""
        # Extract themes from strategy
        strategy_themes = set()
        for doc in strategy_docs:
            strategy_themes.update(doc.strategic_themes)
        
        if not strategy_themes:
            return {}
        
        # Count theme coverage in work items
        theme_counts = defaultdict(int)
        for item in work_items:
            for theme in item.strategic_themes:
                if theme in strategy_themes:
                    theme_counts[theme] += 1
        
        # Calculate coverage percentages
        coverage = {}
        for theme in strategy_themes:
            coverage[theme] = theme_counts[theme] / len(work_items) if work_items else 0
        
        return coverage


class SemanticScorer:
    """High-level semantic scoring orchestrator."""
    
    def __init__(
        self,
        embedder: Optional[SemanticEmbedder] = None,
        alignment_calculator: Optional[StrategicAlignmentCalculator] = None,
        theme_extractor: Optional[ThemeExtractor] = None
    ):
        self.embedder = embedder or SemanticEmbedder()
        self.alignment_calculator = alignment_calculator or StrategicAlignmentCalculator(self.embedder)
        self.theme_extractor = theme_extractor or ThemeExtractor(self.embedder)
    
    def score_work_items(
        self,
        work_items: List[SemanticWorkItem],
        strategy_docs: List[StrategyDocument],
        okrs: List[OKR],
        generate_questions: bool = True
    ) -> Dict[str, Any]:
        """Score all work items and generate insights.
        
        Returns:
            Dictionary with scored items, insights, and questions
        """
        results = {
            'scored_items': [],
            'insights': {},
            'questions': [],
            'gaps': []
        }
        
        # Prepare embeddings for strategy and OKRs
        logger.info("Generating embeddings for strategy documents and OKRs...")
        self._prepare_embeddings(strategy_docs, okrs)
        
        # Score each work item
        logger.info(f"Scoring {len(work_items)} work items...")
        for item in work_items:
            # Calculate alignment
            alignment_score = self.alignment_calculator.calculate_alignment(
                item, strategy_docs, okrs
            )
            item.alignment_score = alignment_score
            
            results['scored_items'].append({
                'work_item_id': item.work_item_id,
                'title': item.title,
                'type': item.work_item_type.value,
                'alignment_score': alignment_score.to_dict(),
                'evidence': [str(e) for e in alignment_score.evidence[:3]]
            })
        
        # Analyze theme coverage
        theme_coverage = self.theme_extractor.analyze_theme_coverage(
            work_items, strategy_docs
        )
        results['insights']['theme_coverage'] = theme_coverage
        
        # Identify gaps and generate questions
        if generate_questions:
            gaps = self._identify_gaps(work_items, strategy_docs, okrs)
            results['gaps'] = gaps
            
            questions = self._generate_questions(gaps, work_items)
            results['questions'] = questions
        
        # Generate summary insights
        results['insights']['summary'] = self._generate_summary_insights(
            work_items, theme_coverage
        )
        
        return results
    
    def _prepare_embeddings(
        self,
        strategy_docs: List[StrategyDocument],
        okrs: List[OKR]
    ):
        """Pre-generate embeddings for efficiency."""
        # Strategy documents
        for doc in strategy_docs:
            if doc.document_embedding is None:
                doc.document_embedding = self.embedder.embed_strategy_document(doc)
                
                # Embed sections
                for section in doc.sections:
                    section.embedding = self.embedder.embed_text(section.content)
        
        # OKRs
        for okr in okrs:
            if okr.objective_embedding is None:
                okr.objective_embedding, kr_embeddings = self.embedder.embed_okr(okr)
                for kr, embedding in zip(okr.key_results, kr_embeddings):
                    kr.embedding = embedding
    
    def _identify_gaps(
        self,
        work_items: List[SemanticWorkItem],
        strategy_docs: List[StrategyDocument],
        okrs: List[OKR]
    ) -> List[InformationGap]:
        """Identify information gaps in alignment."""
        gaps = []
        
        # Check for items with low alignment
        low_alignment_items = [
            item for item in work_items
            if item.alignment_score and item.alignment_score.total_score < 0.3
        ]
        
        if len(low_alignment_items) > len(work_items) * 0.2:  # >20% low alignment
            gaps.append(InformationGap(
                gap_type='low_strategic_alignment',
                severity='high',
                affected_items=[item.work_item_id for item in low_alignment_items[:10]],
                description=f"{len(low_alignment_items)} items have low strategic alignment",
                suggested_questions=[
                    "What strategic objectives should these items support?",
                    "Should these items be reprioritized or cancelled?",
                    "Are there missing strategy documents that would show alignment?"
                ],
                potential_impact="Resources may be spent on non-strategic work"
            ))
        
        # Check for missing text content
        items_missing_text = [
            item for item in work_items
            if not item.has_sufficient_text()
        ]
        
        if items_missing_text:
            gaps.append(InformationGap(
                gap_type='insufficient_descriptions',
                severity='medium',
                affected_items=[item.work_item_id for item in items_missing_text[:10]],
                description=f"{len(items_missing_text)} items lack sufficient description",
                suggested_questions=[
                    "What is the business justification for these items?",
                    "What are the acceptance criteria?",
                    "How do these items contribute to our goals?"
                ],
                potential_impact="Cannot accurately assess strategic alignment"
            ))
        
        # Check for OKR coverage
        okr_covered = sum(1 for item in work_items if item.alignment_score and item.alignment_score.okr_contribution > 0.5)
        okr_coverage_rate = okr_covered / len(work_items) if work_items else 0
        
        if okr_coverage_rate < 0.3:  # <30% OKR coverage
            gaps.append(InformationGap(
                gap_type='low_okr_coverage',
                severity='high',
                affected_items=[],
                description=f"Only {okr_coverage_rate:.0%} of work items clearly support OKRs",
                suggested_questions=[
                    "How does current work contribute to this quarter's OKRs?",
                    "Should we adjust OKRs to reflect actual work?",
                    "What work should we stop to focus on OKRs?"
                ],
                potential_impact="May not achieve quarterly objectives"
            ))
        
        return gaps
    
    def _generate_questions(
        self,
        gaps: List[InformationGap],
        work_items: List[SemanticWorkItem]
    ) -> List[Question]:
        """Generate specific questions based on gaps."""
        questions = []
        question_id = 0
        
        for gap in gaps:
            # Convert gap to questions
            if gap.gap_type == 'low_strategic_alignment':
                # Ask about specific items
                for item_id in gap.affected_items[:3]:  # Top 3
                    item = next((i for i in work_items if i.work_item_id == item_id), None)
                    if item:
                        questions.append(Question(
                            question_id=f"q_{question_id}",
                            text=f"What strategic objective does '{item.title}' support?",
                            question_type=QuestionType.CONTEXT,
                            context=f"This {item.work_item_type.value} currently shows low strategic alignment",
                            business_impact="Ensure resources are spent on strategic work",
                            severity='high',
                            affected_items=[item_id],
                            options=[
                                "Customer Experience improvement",
                                "Operational Excellence",
                                "Revenue Growth",
                                "Technical Debt Reduction",
                                "Not strategically aligned (consider cancelling)",
                                "Other (please specify)"
                            ],
                            expected_format='choice'
                        ))
                        question_id += 1
            
            elif gap.gap_type == 'insufficient_descriptions':
                # Ask for descriptions
                for item_id in gap.affected_items[:2]:  # Top 2
                    item = next((i for i in work_items if i.work_item_id == item_id), None)
                    if item:
                        questions.append(Question(
                            question_id=f"q_{question_id}",
                            text=f"Please provide a business justification for: '{item.title}'",
                            question_type=QuestionType.CONTEXT,
                            context="This item lacks sufficient description for strategic analysis",
                            business_impact="Enable accurate prioritization",
                            severity='medium',
                            affected_items=[item_id],
                            expected_format='text',
                            validation_rules=['min_length:50', 'max_length:500']
                        ))
                        question_id += 1
        
        return questions
    
    def _generate_summary_insights(
        self,
        work_items: List[SemanticWorkItem],
        theme_coverage: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate summary insights from scoring."""
        insights = {}
        
        # Alignment distribution
        scores = [
            item.alignment_score.total_score 
            for item in work_items 
            if item.alignment_score
        ]
        
        if scores:
            insights['alignment_distribution'] = {
                'high': sum(1 for s in scores if s >= 0.7) / len(scores),
                'medium': sum(1 for s in scores if 0.3 <= s < 0.7) / len(scores),
                'low': sum(1 for s in scores if s < 0.3) / len(scores),
                'mean': np.mean(scores),
                'std': np.std(scores)
            }
        
        # Theme insights
        if theme_coverage:
            insights['theme_analysis'] = {
                'well_covered': [t for t, c in theme_coverage.items() if c >= 0.3],
                'under_covered': [t for t, c in theme_coverage.items() if c < 0.1],
                'coverage_balance': np.std(list(theme_coverage.values()))
            }
        
        # Work type distribution
        type_scores = defaultdict(list)
        for item in work_items:
            if item.alignment_score:
                type_scores[item.work_item_type.value].append(
                    item.alignment_score.total_score
                )
        
        insights['alignment_by_type'] = {
            work_type: {
                'mean': np.mean(scores),
                'count': len(scores)
            }
            for work_type, scores in type_scores.items()
        }
        
        return insights