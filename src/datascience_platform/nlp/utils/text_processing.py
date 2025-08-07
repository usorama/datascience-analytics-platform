"""Text Processing Utilities

This module provides text preprocessing and cleaning utilities for NLP tasks.
"""

import re
import string
import logging
from typing import List, Optional, Dict, Any, Tuple
import unicodedata

logger = logging.getLogger(__name__)

# Try importing optional libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer, PorterStemmer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logger.debug("NLTK not available. Basic text processing only.")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.debug("spaCy not available. Basic text processing only.")


class TextProcessor:
    """Advanced text processor with multiple preprocessing options."""
    
    def __init__(
        self,
        language: str = "english",
        use_stemming: bool = False,
        use_lemmatization: bool = True,
        remove_stopwords: bool = True,
        min_word_length: int = 2,
        max_word_length: int = 50
    ):
        """Initialize text processor.
        
        Args:
            language: Language for processing (e.g., "english")
            use_stemming: Whether to apply stemming
            use_lemmatization: Whether to apply lemmatization
            remove_stopwords: Whether to remove stopwords
            min_word_length: Minimum word length to keep
            max_word_length: Maximum word length to keep
        """
        self.language = language
        self.use_stemming = use_stemming
        self.use_lemmatization = use_lemmatization
        self.remove_stopwords = remove_stopwords
        self.min_word_length = min_word_length
        self.max_word_length = max_word_length
        
        # Initialize components
        self._init_nltk_components()
        self._init_spacy_components()
        
        # Compile regex patterns
        self._compile_patterns()
        
        # Statistics
        self.stats = {
            'documents_processed': 0,
            'total_tokens_before': 0,
            'total_tokens_after': 0,
            'average_reduction': 0.0
        }
    
    def _init_nltk_components(self):
        """Initialize NLTK components."""
        self.stopwords = set()
        self.lemmatizer = None
        self.stemmer = None
        
        if NLTK_AVAILABLE:
            try:
                # Download required NLTK data if not present
                import nltk
                nltk.data.find('corpora/stopwords')
            except LookupError:
                logger.info("Downloading NLTK stopwords...")
                nltk.download('stopwords', quiet=True)
            
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                logger.info("Downloading NLTK punkt tokenizer...")
                nltk.download('punkt', quiet=True)
            
            try:
                nltk.data.find('corpora/wordnet')
            except LookupError:
                logger.info("Downloading NLTK wordnet...")
                nltk.download('wordnet', quiet=True)
            
            # Initialize components
            try:
                self.stopwords = set(stopwords.words(self.language))
            except:
                logger.warning(f"Could not load stopwords for {self.language}")
                self.stopwords = set()
            
            if self.use_lemmatization:
                try:
                    self.lemmatizer = WordNetLemmatizer()
                except:
                    logger.warning("Could not initialize lemmatizer")
            
            if self.use_stemming:
                try:
                    self.stemmer = PorterStemmer()
                except:
                    logger.warning("Could not initialize stemmer")
    
    def _init_spacy_components(self):
        """Initialize spaCy components."""
        self.nlp = None
        
        if SPACY_AVAILABLE:
            try:
                # Try to load English model
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("Loaded spaCy English model")
            except OSError:
                logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            except Exception as e:
                logger.warning(f"Could not load spaCy model: {e}")
    
    def _compile_patterns(self):
        """Compile regex patterns for text cleaning."""
        # URL pattern
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone number pattern
        self.phone_pattern = re.compile(
            r'(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        )
        
        # Special characters pattern (keep basic punctuation)
        self.special_chars_pattern = re.compile(r'[^\w\s.,!?;:\-\(\)]')
        
        # Multiple whitespace pattern
        self.whitespace_pattern = re.compile(r'\s+')
        
        # Number pattern
        self.number_pattern = re.compile(r'\b\d+\.?\d*\b')
        
        # Repeated character pattern
        self.repeated_chars_pattern = re.compile(r'(.)\1{2,}')
    
    def clean_text(
        self,
        text: str,
        remove_urls: bool = True,
        remove_emails: bool = True,
        remove_phone_numbers: bool = True,
        remove_numbers: bool = False,
        remove_special_chars: bool = True,
        normalize_whitespace: bool = True,
        fix_repeated_chars: bool = True,
        to_lowercase: bool = True
    ) -> str:
        """Clean text with various preprocessing options.
        
        Args:
            text: Input text to clean
            remove_urls: Remove URLs
            remove_emails: Remove email addresses
            remove_phone_numbers: Remove phone numbers
            remove_numbers: Remove all numbers
            remove_special_chars: Remove special characters
            normalize_whitespace: Normalize whitespace
            fix_repeated_chars: Fix repeated characters (e.g., 'goooood' -> 'good')
            to_lowercase: Convert to lowercase
            
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Remove URLs
        if remove_urls:
            text = self.url_pattern.sub(' ', text)
        
        # Remove emails
        if remove_emails:
            text = self.email_pattern.sub(' ', text)
        
        # Remove phone numbers
        if remove_phone_numbers:
            text = self.phone_pattern.sub(' ', text)
        
        # Remove numbers
        if remove_numbers:
            text = self.number_pattern.sub(' ', text)
        
        # Fix repeated characters
        if fix_repeated_chars:
            text = self.repeated_chars_pattern.sub(r'\1\1', text)
        
        # Remove special characters
        if remove_special_chars:
            text = self.special_chars_pattern.sub(' ', text)
        
        # Convert to lowercase
        if to_lowercase:
            text = text.lower()
        
        # Normalize whitespace
        if normalize_whitespace:
            text = self.whitespace_pattern.sub(' ', text).strip()
        
        return text
    
    def tokenize(self, text: str, method: str = "simple") -> List[str]:
        """Tokenize text into words.
        
        Args:
            text: Input text
            method: Tokenization method ("simple", "nltk", "spacy")
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        if method == "spacy" and self.nlp:
            doc = self.nlp(text)
            tokens = [token.text for token in doc if not token.is_space]
        elif method == "nltk" and NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(text, language=self.language)
            except:
                tokens = text.split()
        else:  # simple
            tokens = text.split()
        
        return tokens
    
    def extract_sentences(self, text: str, method: str = "nltk") -> List[str]:
        """Extract sentences from text.
        
        Args:
            text: Input text
            method: Method to use ("nltk", "spacy", "simple")
            
        Returns:
            List of sentences
        """
        if not text:
            return []
        
        if method == "spacy" and self.nlp:
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents]
        elif method == "nltk" and NLTK_AVAILABLE:
            try:
                sentences = sent_tokenize(text, language=self.language)
            except:
                # Fallback to simple splitting
                sentences = re.split(r'[.!?]+', text)
        else:  # simple
            sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def remove_stopwords_from_tokens(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from token list.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens
        """
        if not self.remove_stopwords:
            return tokens
        
        if self.stopwords:
            return [token for token in tokens if token.lower() not in self.stopwords]
        else:
            # Basic English stopwords if NLTK not available
            basic_stopwords = {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
                'had', 'what', 'said', 'each', 'which', 'she', 'do', 'how', 'their',
                'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
                'her', 'would', 'make', 'like', 'into', 'him', 'time', 'two',
                'more', 'very', 'when', 'come', 'may', 'such', 'where', 'i', 'can',
                'should', 'could', 'did'
            }
            return [token for token in tokens if token.lower() not in basic_stopwords]
    
    def apply_stemming_lemmatization(self, tokens: List[str]) -> List[str]:
        """Apply stemming or lemmatization to tokens.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Processed tokens
        """
        processed_tokens = []
        
        for token in tokens:
            processed_token = token
            
            # Apply lemmatization
            if self.use_lemmatization and self.lemmatizer:
                try:
                    processed_token = self.lemmatizer.lemmatize(processed_token)
                except:
                    pass
            
            # Apply stemming (if lemmatization not used or failed)
            elif self.use_stemming and self.stemmer:
                try:
                    processed_token = self.stemmer.stem(processed_token)
                except:
                    pass
            
            processed_tokens.append(processed_token)
        
        return processed_tokens
    
    def filter_tokens(self, tokens: List[str]) -> List[str]:
        """Filter tokens by length and other criteria.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens
        """
        filtered = []
        
        for token in tokens:
            # Filter by length
            if len(token) < self.min_word_length or len(token) > self.max_word_length:
                continue
            
            # Filter out purely numeric tokens
            if token.isdigit():
                continue
            
            # Filter out punctuation-only tokens
            if all(c in string.punctuation for c in token):
                continue
            
            filtered.append(token)
        
        return filtered
    
    def process_text(
        self,
        text: str,
        return_tokens: bool = False,
        return_sentences: bool = False,
        **clean_kwargs
    ) -> Dict[str, Any]:
        """Process text with full pipeline.
        
        Args:
            text: Input text
            return_tokens: Whether to return tokenized text
            return_sentences: Whether to return sentences
            **clean_kwargs: Additional arguments for clean_text
            
        Returns:
            Dictionary with processed text and optional tokens/sentences
        """
        if not text:
            return {
                'cleaned_text': '',
                'tokens': [],
                'sentences': [],
                'token_count_before': 0,
                'token_count_after': 0
            }
        
        # Track statistics
        original_tokens = self.tokenize(text, method="simple")
        tokens_before = len(original_tokens)
        
        # Clean text
        cleaned_text = self.clean_text(text, **clean_kwargs)
        
        # Tokenize
        tokens = self.tokenize(cleaned_text)
        
        # Remove stopwords
        tokens = self.remove_stopwords_from_tokens(tokens)
        
        # Apply stemming/lemmatization
        tokens = self.apply_stemming_lemmatization(tokens)
        
        # Filter tokens
        tokens = self.filter_tokens(tokens)
        
        # Reconstruct cleaned text from tokens
        final_text = ' '.join(tokens) if tokens else ''
        
        # Extract sentences if requested
        sentences = []
        if return_sentences:
            sentences = self.extract_sentences(cleaned_text)
        
        # Update statistics
        tokens_after = len(tokens)
        self.stats['documents_processed'] += 1
        self.stats['total_tokens_before'] += tokens_before
        self.stats['total_tokens_after'] += tokens_after
        
        if self.stats['documents_processed'] > 0:
            self.stats['average_reduction'] = (
                1 - (self.stats['total_tokens_after'] / self.stats['total_tokens_before'])
            ) * 100
        
        result = {
            'cleaned_text': final_text,
            'token_count_before': tokens_before,
            'token_count_after': tokens_after,
            'reduction_percentage': ((tokens_before - tokens_after) / max(tokens_before, 1)) * 100
        }
        
        if return_tokens:
            result['tokens'] = tokens
        
        if return_sentences:
            result['sentences'] = sentences
        
        return result
    
    def extract_keywords(
        self,
        text: str,
        method: str = "frequency",
        max_keywords: int = 10,
        min_frequency: int = 2
    ) -> List[Tuple[str, float]]:
        """Extract keywords from text.
        
        Args:
            text: Input text
            method: Extraction method ("frequency", "tfidf")
            max_keywords: Maximum number of keywords
            min_frequency: Minimum frequency for a word to be considered
            
        Returns:
            List of (keyword, score) tuples
        """
        # Process text
        processed = self.process_text(text, return_tokens=True)
        tokens = processed['tokens']
        
        if not tokens:
            return []
        
        if method == "frequency":
            # Simple frequency-based extraction
            from collections import Counter
            
            # Count token frequencies
            token_counts = Counter(tokens)
            
            # Filter by minimum frequency
            filtered_counts = {
                token: count for token, count in token_counts.items()
                if count >= min_frequency and len(token) > 2
            }
            
            # Get top keywords by frequency
            top_keywords = sorted(
                filtered_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:max_keywords]
            
            # Normalize scores
            max_count = max(count for _, count in top_keywords) if top_keywords else 1
            keywords = [(token, count / max_count) for token, count in top_keywords]
            
        else:
            # For TF-IDF, we'd need a document collection
            # For now, return frequency-based results
            keywords = self.extract_keywords(text, "frequency", max_keywords, min_frequency)
        
        return keywords
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset processing statistics."""
        self.stats = {
            'documents_processed': 0,
            'total_tokens_before': 0,
            'total_tokens_after': 0,
            'average_reduction': 0.0
        }