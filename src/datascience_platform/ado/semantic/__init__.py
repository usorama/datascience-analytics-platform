"""Semantic Analysis Module for ADO

This module provides text-based strategic alignment analysis,
enabling quantification of relationships between strategy documents,
OKRs, and work items through natural language processing.
"""

from .models import (
    OKR,
    KeyResult,
    StrategyDocument,
    DocumentSection,
    SemanticWorkItem,
    TextEvidence,
    AlignmentScore,
    InformationGap,
    Question,
    QuestionType,
    DocumentType
)

from .text_processor import (
    TextPreprocessor,
    DocumentParser,
    BusinessEntityExtractor
)

from .embedder import (
    SemanticEmbedder,
    EmbeddingCache
)

from .alignment import (
    StrategicAlignmentCalculator,
    ThemeExtractor,
    SemanticScorer
)

from .qa_system import (
    IntelligentQASystem,
    QASession,
    AnswerValidation
)

from .relationship_extractor import (
    RelationshipExtractor,
    RelationshipGraph,
    RelationshipType,
    EntityNode,
    Relationship
)

from .explainability import (
    ExplainableScorer,
    ExplanationType,
    ScoringFactor,
    ScoreExplanation
)

__all__ = [
    # Models
    'OKR',
    'KeyResult',
    'StrategyDocument',
    'DocumentSection',
    'SemanticWorkItem',
    'TextEvidence',
    'AlignmentScore',
    'InformationGap',
    'Question',
    'QuestionType',
    'DocumentType',
    # Processors
    'TextPreprocessor',
    'DocumentParser',
    'BusinessEntityExtractor',
    # Embedders
    'SemanticEmbedder',
    'EmbeddingCache',
    # Alignment
    'StrategicAlignmentCalculator',
    'ThemeExtractor',
    'SemanticScorer',
    # Q&A System
    'IntelligentQASystem',
    'QASession',
    'AnswerValidation',
    # Relationship Extraction
    'RelationshipExtractor',
    'RelationshipGraph',
    'RelationshipType',
    'EntityNode',
    'Relationship',
    # Explainability
    'ExplainableScorer',
    'ExplanationType',
    'ScoringFactor',
    'ScoreExplanation'
]