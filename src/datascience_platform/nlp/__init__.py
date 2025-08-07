"""NLP Enhancement Module

This module provides advanced NLP capabilities for the DataScience Platform,
including real transformer embeddings, domain-specific models, and risk prediction.
"""

from .core.embedder import SemanticEmbedder
from .domain.model_selector import DomainModelSelector
from .risk.predictor import HistoricalRiskPredictor
from .vector_store.faiss_store import VectorStore

__all__ = [
    'SemanticEmbedder',
    'DomainModelSelector', 
    'HistoricalRiskPredictor',
    'VectorStore'
]

__version__ = '1.0.0'