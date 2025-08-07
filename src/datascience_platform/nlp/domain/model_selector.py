"""Domain-Specific Model Selection Module

This module provides intelligent selection of domain-specific transformer models
based on document type, content analysis, and context.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Try importing required libraries
try:
    from transformers import AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers not available. Install with: pip install transformers")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class DomainType(Enum):
    """Supported domain types for specialized models."""
    FINANCIAL = "financial"
    LEGAL = "legal"
    SECURITY = "security" 
    HEALTHCARE = "healthcare"
    TECHNICAL = "technical"
    GENERAL = "general"
    BUSINESS = "business"
    COMPLIANCE = "compliance"


@dataclass
class ModelConfig:
    """Configuration for a domain-specific model."""
    model_name: str
    domain: DomainType
    description: str
    keywords: List[str]
    confidence_threshold: float = 0.3
    is_available: bool = True
    requires_special_handling: bool = False
    max_length: Optional[int] = None


class DomainModelSelector:
    """Intelligent selector for domain-specific NLP models."""
    
    def __init__(self, cache_dir: Optional[Path] = None, auto_download: bool = False):
        """Initialize the domain model selector.
        
        Args:
            cache_dir: Directory to cache models
            auto_download: Whether to automatically download models
        """
        self.cache_dir = cache_dir or Path.home() / ".cache" / "ds_platform_models"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.auto_download = auto_download
        
        # Initialize model configurations
        self.model_configs = self._init_model_configs()
        
        # Pattern matching for domain detection
        self.domain_patterns = self._init_domain_patterns()
        
        # Cache for loaded models
        self.model_cache = {}
        
        # Statistics
        self.stats = {
            'domain_selections': {},
            'model_loads': {},
            'fallbacks_used': 0
        }
    
    def _init_model_configs(self) -> Dict[DomainType, ModelConfig]:
        """Initialize configurations for domain-specific models."""
        return {
            DomainType.FINANCIAL: ModelConfig(
                model_name="yiyanghkust/finbert-tone",
                domain=DomainType.FINANCIAL,
                description="Financial sentiment and document analysis",
                keywords=[
                    "financial", "revenue", "profit", "loss", "investment", "portfolio",
                    "market", "stock", "bond", "dividend", "earnings", "fiscal",
                    "budget", "expense", "income", "cost", "roi", "valuation",
                    "liquidity", "asset", "liability", "equity", "debt", "credit"
                ],
                confidence_threshold=0.4
            ),
            
            DomainType.LEGAL: ModelConfig(
                model_name="nlpaueb/legal-bert-base-uncased",
                domain=DomainType.LEGAL,
                description="Legal document analysis and compliance",
                keywords=[
                    "legal", "contract", "agreement", "clause", "liability",
                    "compliance", "regulation", "law", "statute", "policy",
                    "terms", "conditions", "jurisdiction", "intellectual property",
                    "copyright", "trademark", "patent", "litigation", "dispute"
                ],
                confidence_threshold=0.35
            ),
            
            DomainType.SECURITY: ModelConfig(
                model_name="jackaduma/SecBERT",
                domain=DomainType.SECURITY,
                description="Cybersecurity and risk analysis",
                keywords=[
                    "security", "vulnerability", "threat", "risk", "attack",
                    "encryption", "authentication", "authorization", "firewall",
                    "malware", "phishing", "breach", "incident", "cyber",
                    "privacy", "data protection", "access control", "audit"
                ],
                confidence_threshold=0.4
            ),
            
            DomainType.HEALTHCARE: ModelConfig(
                model_name="emilyalsentzer/Bio_ClinicalBERT",
                domain=DomainType.HEALTHCARE,
                description="Healthcare and biomedical text analysis",
                keywords=[
                    "healthcare", "medical", "clinical", "patient", "diagnosis",
                    "treatment", "therapy", "medication", "drug", "disease",
                    "symptom", "health", "hospital", "physician", "nurse",
                    "biomedical", "pharmaceutical", "regulatory", "fda"
                ],
                confidence_threshold=0.4
            ),
            
            DomainType.TECHNICAL: ModelConfig(
                model_name="microsoft/codebert-base",
                domain=DomainType.TECHNICAL,
                description="Technical and software development content",
                keywords=[
                    "technical", "software", "development", "programming", "code",
                    "algorithm", "architecture", "api", "database", "system",
                    "infrastructure", "deployment", "testing", "debugging",
                    "framework", "library", "version", "integration", "devops"
                ],
                confidence_threshold=0.35
            ),
            
            DomainType.BUSINESS: ModelConfig(
                model_name="sentence-transformers/all-mpnet-base-v2",
                domain=DomainType.BUSINESS,
                description="General business and strategy analysis",
                keywords=[
                    "business", "strategy", "operations", "management", "customer",
                    "market", "competitive", "growth", "innovation", "process",
                    "efficiency", "optimization", "performance", "metrics",
                    "stakeholder", "objective", "goal", "initiative", "project"
                ],
                confidence_threshold=0.3
            ),
            
            DomainType.COMPLIANCE: ModelConfig(
                model_name="sentence-transformers/all-mpnet-base-v2",
                domain=DomainType.COMPLIANCE,
                description="Compliance and regulatory analysis",
                keywords=[
                    "compliance", "regulatory", "audit", "governance", "policy",
                    "procedure", "standard", "requirement", "certification",
                    "inspection", "assessment", "monitoring", "reporting",
                    "documentation", "control", "framework", "guideline"
                ],
                confidence_threshold=0.35
            ),
            
            DomainType.GENERAL: ModelConfig(
                model_name="sentence-transformers/all-mpnet-base-v2",
                domain=DomainType.GENERAL,
                description="General purpose text analysis",
                keywords=[],
                confidence_threshold=0.0,  # Always available as fallback
                is_available=True
            )
        }
    
    def _init_domain_patterns(self) -> Dict[DomainType, List[re.Pattern]]:
        """Initialize regex patterns for domain detection."""
        return {
            DomainType.FINANCIAL: [
                re.compile(r'\$[\d,]+(?:\.\d{2})?', re.IGNORECASE),  # Money amounts
                re.compile(r'\b(?:Q[1-4]|quarterly|annual|fiscal)\s+(?:report|results)', re.IGNORECASE),
                re.compile(r'\b(?:revenue|profit|ebitda|cash flow)\b', re.IGNORECASE),
                re.compile(r'\b(?:balance sheet|income statement|p&l)\b', re.IGNORECASE)
            ],
            
            DomainType.LEGAL: [
                re.compile(r'\b(?:section|article|clause|paragraph)\s+\d+', re.IGNORECASE),
                re.compile(r'\b(?:hereby|whereas|aforementioned|pursuant)\b', re.IGNORECASE),
                re.compile(r'\b(?:shall|must not|is prohibited|is required)\b', re.IGNORECASE),
                re.compile(r'\b(?:intellectual property|copyright|trademark)\b', re.IGNORECASE)
            ],
            
            DomainType.SECURITY: [
                re.compile(r'\b(?:CVE-\d{4}-\d{4,}|vulnerability|exploit)\b', re.IGNORECASE),
                re.compile(r'\b(?:ssl|tls|https|encryption)\b', re.IGNORECASE),
                re.compile(r'\b(?:firewall|ids|ips|siem)\b', re.IGNORECASE),
                re.compile(r'\b(?:penetration test|security audit|risk assessment)\b', re.IGNORECASE)
            ],
            
            DomainType.TECHNICAL: [
                re.compile(r'\b(?:def|function|class|import|return)\b', re.IGNORECASE),  # Code keywords
                re.compile(r'\b(?:api|rest|json|xml|http)\b', re.IGNORECASE),
                re.compile(r'\b(?:database|sql|nosql|mongodb|postgres)\b', re.IGNORECASE),
                re.compile(r'\b(?:docker|kubernetes|ci/cd|devops)\b', re.IGNORECASE)
            ]
        }
    
    def detect_domain(self, text: str, document_type: Optional[str] = None) -> Tuple[DomainType, float]:
        """Detect the most likely domain for the given text.
        
        Args:
            text: Input text to analyze
            document_type: Optional document type hint
            
        Returns:
            Tuple of (detected_domain, confidence_score)
        """
        if not text or not text.strip():
            return DomainType.GENERAL, 0.0
        
        text_lower = text.lower()
        domain_scores = {}
        
        # Document type hint scoring
        if document_type:
            doc_type_lower = document_type.lower()
            for domain, config in self.model_configs.items():
                if domain.value in doc_type_lower:
                    domain_scores[domain] = domain_scores.get(domain, 0) + 0.3
        
        # Keyword-based scoring
        for domain, config in self.model_configs.items():
            if domain == DomainType.GENERAL:
                continue
                
            score = 0.0
            keyword_matches = 0
            
            for keyword in config.keywords:
                if keyword in text_lower:
                    keyword_matches += 1
                    # Weight by keyword importance (longer keywords get higher weight)
                    score += len(keyword.split()) * 0.1
            
            # Normalize by text length and keyword count
            if keyword_matches > 0:
                text_words = len(text_lower.split())
                normalized_score = (score * keyword_matches) / max(text_words * 0.01, 1.0)
                domain_scores[domain] = domain_scores.get(domain, 0) + normalized_score
        
        # Pattern-based scoring
        for domain, patterns in self.domain_patterns.items():
            pattern_score = 0.0
            for pattern in patterns:
                matches = pattern.findall(text)
                pattern_score += len(matches) * 0.15
            
            if pattern_score > 0:
                domain_scores[domain] = domain_scores.get(domain, 0) + pattern_score
        
        # Find domain with highest score above threshold
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            best_score = domain_scores[best_domain]
            
            config = self.model_configs[best_domain]
            if best_score >= config.confidence_threshold:
                return best_domain, best_score
        
        # Default to general domain
        return DomainType.GENERAL, 0.1
    
    def select_model(
        self,
        text: str,
        document_type: Optional[str] = None,
        preferred_domain: Optional[DomainType] = None
    ) -> Tuple[str, DomainType, Dict[str, Any]]:
        """Select the best model for the given text.
        
        Args:
            text: Input text to analyze
            document_type: Optional document type hint
            preferred_domain: Optional preferred domain override
            
        Returns:
            Tuple of (model_name, selected_domain, metadata)
        """
        # Use preferred domain if specified
        if preferred_domain and preferred_domain in self.model_configs:
            domain = preferred_domain
            confidence = 1.0
        else:
            domain, confidence = self.detect_domain(text, document_type)
        
        config = self.model_configs[domain]
        
        # Check if model is available
        if not config.is_available and not self._check_model_availability(config.model_name):
            logger.warning(f"Model {config.model_name} not available, falling back to general model")
            domain = DomainType.GENERAL
            config = self.model_configs[domain]
            self.stats['fallbacks_used'] += 1
        
        # Update statistics
        domain_key = domain.value
        self.stats['domain_selections'][domain_key] = self.stats['domain_selections'].get(domain_key, 0) + 1
        
        metadata = {
            'confidence': confidence,
            'description': config.description,
            'keywords_matched': self._get_matched_keywords(text, config.keywords),
            'domain': domain.value,
            'requires_special_handling': config.requires_special_handling,
            'max_length': config.max_length
        }
        
        return config.model_name, domain, metadata
    
    def _check_model_availability(self, model_name: str) -> bool:
        """Check if a model is available for download/use."""
        if not TRANSFORMERS_AVAILABLE:
            return model_name in ["sentence-transformers/all-mpnet-base-v2"]
        
        try:
            # Try to get model info without downloading
            from transformers import AutoConfig
            AutoConfig.from_pretrained(model_name)
            return True
        except Exception as e:
            logger.debug(f"Model {model_name} not available: {e}")
            return False
    
    def _get_matched_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Get list of keywords that matched in the text."""
        text_lower = text.lower()
        return [keyword for keyword in keywords if keyword in text_lower]
    
    def load_model(self, model_name: str, domain: DomainType) -> Any:
        """Load and cache a model.
        
        Args:
            model_name: Name of the model to load
            domain: Domain type for the model
            
        Returns:
            Loaded model instance
        """
        if model_name in self.model_cache:
            return self.model_cache[model_name]
        
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                # Try loading as sentence transformer first
                try:
                    model = SentenceTransformer(model_name)
                    self.model_cache[model_name] = model
                    logger.info(f"Loaded sentence transformer: {model_name}")
                    
                except Exception as e:
                    logger.debug(f"Could not load as sentence transformer: {e}")
                    # Fall back to regular transformers
                    if TRANSFORMERS_AVAILABLE:
                        tokenizer = AutoTokenizer.from_pretrained(model_name)
                        model = AutoModel.from_pretrained(model_name)
                        model_wrapper = {'model': model, 'tokenizer': tokenizer}
                        self.model_cache[model_name] = model_wrapper
                        logger.info(f"Loaded transformer model: {model_name}")
                    else:
                        raise Exception("Neither sentence-transformers nor transformers available")
            
            else:
                raise Exception("No transformer libraries available")
                
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            # Fall back to general model
            fallback_model = "sentence-transformers/all-mpnet-base-v2"
            if fallback_model != model_name and fallback_model not in self.model_cache:
                try:
                    model = SentenceTransformer(fallback_model)
                    self.model_cache[fallback_model] = model
                    self.model_cache[model_name] = model  # Cache under original name too
                    logger.info(f"Loaded fallback model: {fallback_model}")
                except:
                    # Ultimate fallback to mock
                    from ..core.embedder import MockSentenceTransformer
                    model = MockSentenceTransformer(model_name)
                    self.model_cache[model_name] = model
                    logger.warning(f"Using mock model for: {model_name}")
        
        # Update statistics
        model_key = model_name
        self.stats['model_loads'][model_key] = self.stats['model_loads'].get(model_key, 0) + 1
        
        return self.model_cache[model_name]
    
    def get_available_domains(self) -> List[Tuple[DomainType, str, bool]]:
        """Get list of available domains with their descriptions and availability."""
        domains = []
        for domain, config in self.model_configs.items():
            is_available = config.is_available and self._check_model_availability(config.model_name)
            domains.append((domain, config.description, is_available))
        return domains
    
    def get_domain_keywords(self, domain: DomainType) -> List[str]:
        """Get keywords associated with a domain."""
        if domain in self.model_configs:
            return self.model_configs[domain].keywords.copy()
        return []
    
    def update_model_config(
        self,
        domain: DomainType,
        model_name: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        confidence_threshold: Optional[float] = None
    ):
        """Update configuration for a domain model."""
        if domain not in self.model_configs:
            logger.warning(f"Unknown domain: {domain}")
            return
        
        config = self.model_configs[domain]
        
        if model_name:
            config.model_name = model_name
            # Remove from cache to force reload
            if model_name in self.model_cache:
                del self.model_cache[model_name]
        
        if keywords is not None:
            config.keywords = keywords
        
        if confidence_threshold is not None:
            config.confidence_threshold = confidence_threshold
        
        logger.info(f"Updated configuration for domain: {domain.value}")
    
    def analyze_text_domains(
        self,
        texts: List[str],
        document_types: Optional[List[str]] = None
    ) -> List[Tuple[str, DomainType, float]]:
        """Analyze multiple texts and return domain classifications.
        
        Args:
            texts: List of texts to analyze
            document_types: Optional list of document types (same length as texts)
            
        Returns:
            List of (text, detected_domain, confidence) tuples
        """
        if document_types and len(document_types) != len(texts):
            raise ValueError("document_types must be same length as texts")
        
        results = []
        for i, text in enumerate(texts):
            doc_type = document_types[i] if document_types else None
            domain, confidence = self.detect_domain(text, doc_type)
            results.append((text[:100] + "..." if len(text) > 100 else text, domain, confidence))
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            'domain_selections': self.stats['domain_selections'],
            'model_loads': self.stats['model_loads'],
            'fallbacks_used': self.stats['fallbacks_used'],
            'cached_models': list(self.model_cache.keys()),
            'available_domains': len([d for d, _, available in self.get_available_domains() if available])
        }
    
    def clear_cache(self):
        """Clear model cache."""
        self.model_cache.clear()
        logger.info("Cleared model cache")
    
    def preload_models(self, domains: Optional[List[DomainType]] = None):
        """Preload models for specified domains.
        
        Args:
            domains: List of domains to preload. If None, preloads all available domains.
        """
        if domains is None:
            domains = [domain for domain, _, available in self.get_available_domains() if available]
        
        logger.info(f"Preloading models for domains: {[d.value for d in domains]}")
        
        for domain in domains:
            if domain in self.model_configs:
                config = self.model_configs[domain]
                try:
                    self.load_model(config.model_name, domain)
                except Exception as e:
                    logger.warning(f"Could not preload model for {domain.value}: {e}")
        
        logger.info(f"Preloaded {len(self.model_cache)} models")