"""Semantic Data Models for Business Strategy Analysis

This module defines data models for representing strategy documents,
OKRs, and semantically-enhanced work items with text content.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import numpy as np
from pydantic import Field

from ..models import ADOWorkItem


class QuestionType(str, Enum):
    """Types of questions for information gathering."""
    CLARIFICATION = "clarification"
    CONTEXT = "context"
    PRIORITY = "priority"
    DEPENDENCY = "dependency"
    METRIC = "metric"
    TIMELINE = "timeline"


class DocumentType(str, Enum):
    """Types of strategic documents."""
    VISION = "vision"
    MISSION = "mission"
    STRATEGY = "strategy"
    ROADMAP = "roadmap"
    OKR = "okr"
    PRESENTATION = "presentation"
    POLICY = "policy"


@dataclass
class KeyResult:
    """Represents a measurable key result."""
    kr_id: str
    text: str
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    deadline: Optional[datetime] = None
    embedding: Optional[np.ndarray] = None
    
    @property
    def progress(self) -> float:
        """Calculate progress percentage."""
        if self.target_value and self.current_value:
            return min(100.0, (self.current_value / self.target_value) * 100)
        return 0.0
    
    @property
    def is_quantitative(self) -> bool:
        """Check if this is a quantitative KR."""
        return self.target_value is not None


@dataclass
class OKR:
    """Represents an Objective with Key Results."""
    okr_id: str
    period: str  # e.g., "Q3 2025"
    level: str  # company, department, team, individual
    
    # Objective
    objective_text: str
    objective_embedding: Optional[np.ndarray] = None
    
    # Key Results
    key_results: List[KeyResult] = field(default_factory=list)
    
    # Relationships
    parent_okr_id: Optional[str] = None
    child_okr_ids: List[str] = field(default_factory=list)
    aligned_work_items: List[str] = field(default_factory=list)
    
    # Metadata
    owner: str = ""
    team: Optional[str] = None
    status: str = "active"
    progress: float = 0.0
    created_date: Optional[datetime] = None
    
    # Strategic alignment
    strategic_pillars: List[str] = field(default_factory=list)
    business_impact: Optional[str] = None
    
    def calculate_progress(self) -> float:
        """Calculate overall OKR progress from key results."""
        if not self.key_results:
            return 0.0
        
        kr_progress = [kr.progress for kr in self.key_results]
        return sum(kr_progress) / len(kr_progress)
    
    def to_text(self) -> str:
        """Convert OKR to text representation for embedding."""
        parts = [f"Objective: {self.objective_text}"]
        for i, kr in enumerate(self.key_results, 1):
            parts.append(f"KR{i}: {kr.text}")
        if self.business_impact:
            parts.append(f"Impact: {self.business_impact}")
        return "\n".join(parts)


@dataclass
class DocumentSection:
    """Represents a section within a strategy document."""
    section_id: str
    title: str
    content: str
    section_type: str  # heading, paragraph, list, table
    level: int  # hierarchy level (1=top)
    embedding: Optional[np.ndarray] = None
    entities: List[Dict[str, Any]] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)


@dataclass
class StrategyDocument:
    """Represents a strategic document."""
    doc_id: str
    title: str
    document_type: DocumentType
    
    # Content
    full_text: str
    sections: List[DocumentSection] = field(default_factory=list)
    
    # Semantic representation
    document_embedding: Optional[np.ndarray] = None
    section_embeddings: Dict[str, np.ndarray] = field(default_factory=dict)
    
    # Extracted elements
    strategic_themes: List[str] = field(default_factory=list)
    key_metrics: List[str] = field(default_factory=list)
    time_horizons: List[Tuple[str, datetime]] = field(default_factory=list)
    strategic_pillars: List[str] = field(default_factory=list)
    
    # Relationships
    related_okrs: List[str] = field(default_factory=list)
    related_documents: List[str] = field(default_factory=list)
    
    # Metadata
    created_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    approval_status: str = "draft"
    owner: str = ""
    
    def get_summary(self, max_length: int = 500) -> str:
        """Get document summary."""
        if len(self.full_text) <= max_length:
            return self.full_text
        return self.full_text[:max_length] + "..."


@dataclass
class TextEvidence:
    """Evidence supporting a scoring decision."""
    source_type: str  # strategy, okr, work_item
    source_id: str
    text_excerpt: str
    relevance_score: float
    explanation: str
    
    def __str__(self) -> str:
        return f"[{self.source_type}] {self.text_excerpt[:100]}... (relevance: {self.relevance_score:.2f})"


@dataclass
class AlignmentScore:
    """Multi-dimensional alignment score with explanations."""
    # Core scores (0-1)
    strategic_alignment: float
    okr_contribution: float
    thematic_coherence: float
    dependency_impact: float
    
    # Composite score
    total_score: float
    
    # Explanation
    explanation: str
    evidence: List[TextEvidence] = field(default_factory=list)
    confidence: float = 0.0
    
    # Breakdown by source
    strategy_scores: Dict[str, float] = field(default_factory=dict)
    okr_scores: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'strategic_alignment': self.strategic_alignment,
            'okr_contribution': self.okr_contribution,
            'thematic_coherence': self.thematic_coherence,
            'dependency_impact': self.dependency_impact,
            'total_score': self.total_score,
            'explanation': self.explanation,
            'confidence': self.confidence,
            'evidence_count': len(self.evidence)
        }


class SemanticWorkItem(ADOWorkItem):
    """Work item enhanced with semantic information."""
    # Text content
    full_description: Optional[str] = None
    acceptance_criteria_text: Optional[str] = None
    definition_of_done: Optional[str] = None
    business_justification: Optional[str] = None
    technical_notes: Optional[str] = None
    
    # Semantic fields
    description_embedding: Optional[np.ndarray] = None
    title_embedding: Optional[np.ndarray] = None
    combined_embedding: Optional[np.ndarray] = None
    
    # Extracted information
    strategic_themes: List[str] = Field(default_factory=list)
    mentioned_metrics: List[str] = Field(default_factory=list)
    identified_dependencies: List[str] = Field(default_factory=list)
    
    # Alignment results
    alignment_score: Optional[AlignmentScore] = None
    aligned_okrs: List[Tuple[str, float]] = Field(default_factory=list)  # (okr_id, score)
    aligned_strategies: List[Tuple[str, float]] = Field(default_factory=list)  # (doc_id, score)
    
    # Semantic relationships
    semantic_similar_items: List[Tuple[str, float]] = Field(default_factory=list)  # (item_id, similarity)
    semantic_dependencies: List[Dict[str, Any]] = Field(default_factory=list)
    
    def get_text_for_embedding(self) -> str:
        """Combine all text fields for embedding generation."""
        parts = [self.title]
        
        if self.full_description:
            parts.append(f"Description: {self.full_description}")
        if self.acceptance_criteria_text:
            parts.append(f"Acceptance Criteria: {self.acceptance_criteria_text}")
        if self.business_justification:
            parts.append(f"Business Justification: {self.business_justification}")
        if self.strategic_themes:
            parts.append(f"Themes: {', '.join(self.strategic_themes)}")
            
        return "\n".join(parts)
    
    def has_sufficient_text(self) -> bool:
        """Check if item has enough text for meaningful analysis."""
        total_length = len(self.title or "")
        total_length += len(self.full_description or "")
        total_length += len(self.acceptance_criteria_text or "")
        total_length += len(self.business_justification or "")
        
        return total_length > 50  # Minimum 50 characters


@dataclass
class InformationGap:
    """Represents missing information in analysis."""
    gap_type: str  # missing_field, unclear_objective, no_metrics, etc.
    severity: str  # critical, high, medium, low
    affected_items: List[str]
    description: str
    suggested_questions: List[str] = field(default_factory=list)
    potential_impact: str = ""
    
    def to_question(self) -> 'Question':
        """Convert gap to primary question."""
        if self.suggested_questions:
            return Question(
                question_id=f"gap_{self.gap_type}_{hash(self.description)}",
                text=self.suggested_questions[0],
                question_type=QuestionType.CONTEXT,
                context=self.description,
                business_impact=self.potential_impact,
                severity=self.severity
            )
        return None


@dataclass
class Question:
    """Question for gathering missing information."""
    question_id: str
    text: str
    question_type: QuestionType
    context: str
    
    # Metadata
    business_impact: str
    severity: str  # critical, high, medium, low
    affected_items: List[str] = field(default_factory=list)
    
    # Response options
    options: List[str] = field(default_factory=list)  # For multiple choice
    expected_format: Optional[str] = None  # text, number, date, choice
    validation_rules: List[str] = field(default_factory=list)
    
    # Relationships
    related_questions: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)  # Other question IDs
    
    def format_for_display(self) -> str:
        """Format question for user display."""
        display = f"{self.text}\n"
        if self.context:
            display += f"Context: {self.context}\n"
        if self.options:
            display += "Options:\n"
            for i, opt in enumerate(self.options, 1):
                display += f"  {i}. {opt}\n"
        return display


@dataclass
class SemanticAnalysisConfig:
    """Configuration for semantic analysis."""
    # Model settings
    embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    use_cache: bool = True
    cache_ttl_hours: int = 24
    
    # Analysis settings
    min_similarity_threshold: float = 0.3
    top_k_similar: int = 10
    extract_themes: bool = True
    extract_entities: bool = True
    
    # Question generation
    generate_questions: bool = True
    max_questions: int = 10
    question_priority_threshold: float = 0.7
    
    # Performance
    batch_size: int = 32
    max_text_length: int = 512
    use_gpu: bool = False
    
    # Explanation
    generate_explanations: bool = True
    explanation_detail_level: str = "medium"  # low, medium, high
    include_evidence: bool = True
    max_evidence_items: int = 5