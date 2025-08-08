"""QVF Semantic Analysis Engine

This module provides semantic analysis of work items using Ollama-powered LLMs.
It extracts business value, strategic alignment, risk factors, and complexity
indicators from work item descriptions to enhance QVF mathematical scoring.

Key Features:
- Multi-faceted work item analysis using local LLMs
- Structured output parsing for consistent results
- Automatic fallback to mathematical analysis
- Caching for performance optimization
- Batch processing for efficiency
- Confidence scoring and validation

Architecture:
- SemanticAnalyzer: Main analysis orchestrator
- Analysis pipeline with validation and fallback
- Integration with QVF scoring engine
- Performance monitoring and optimization
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import time

from .ollama_manager import OllamaManager, InferenceResponse
from .prompt_templates import QVFPromptTemplates, AnalysisType
from .fallback import FallbackEngine

logger = logging.getLogger(__name__)


@dataclass
class SemanticAnalysisResult:
    """Result of semantic analysis for a work item."""
    work_item_id: str
    analysis_type: AnalysisType
    score: float
    confidence: float
    insights: List[str]
    structured_data: Dict[str, Any]
    processing_time: float
    used_ai: bool
    model_used: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['analysis_type'] = self.analysis_type.value
        return result


@dataclass
class BatchAnalysisResult:
    """Result of batch semantic analysis."""
    total_items: int
    successful_analyses: int
    failed_analyses: int
    ai_analyses: int
    fallback_analyses: int
    total_processing_time: float
    results: List[SemanticAnalysisResult]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return self.successful_analyses / max(self.total_items, 1)
    
    @property
    def ai_usage_rate(self) -> float:
        """Calculate AI usage rate."""
        return self.ai_analyses / max(self.successful_analyses, 1)


class AnalysisPriority(Enum):
    """Priority levels for analysis processing."""
    HIGH = "high"
    NORMAL = "normal" 
    LOW = "low"
    BATCH = "batch"


class SemanticAnalyzer:
    """Semantic analysis engine for QVF work items.
    
    This class orchestrates the analysis of work items using Ollama-powered LLMs,
    with automatic fallback to mathematical analysis when AI is unavailable.
    """
    
    def __init__(self,
                 ollama_manager: Optional[OllamaManager] = None,
                 fallback_engine: Optional[FallbackEngine] = None,
                 enable_caching: bool = True,
                 max_concurrent: int = 5):
        """Initialize semantic analyzer.
        
        Args:
            ollama_manager: Ollama connection manager
            fallback_engine: Mathematical fallback engine
            enable_caching: Whether to cache analysis results
            max_concurrent: Maximum concurrent analyses
        """
        self.ollama_manager = ollama_manager or OllamaManager()
        self.fallback_engine = fallback_engine or FallbackEngine()
        self.enable_caching = enable_caching
        self.max_concurrent = max_concurrent
        
        # Performance tracking
        self._analysis_count = 0
        self._ai_analysis_count = 0
        self._fallback_count = 0
        self._total_processing_time = 0.0
        self._error_count = 0
        
        # Cache for analysis results
        self._analysis_cache: Dict[str, SemanticAnalysisResult] = {}
        self._cache_ttl = 3600  # 1 hour TTL
    
    def analyze_work_item(self,
                         work_item: Dict[str, Any],
                         analysis_types: List[AnalysisType],
                         priority: AnalysisPriority = AnalysisPriority.NORMAL,
                         context: Optional[Dict[str, Any]] = None) -> List[SemanticAnalysisResult]:
        """Analyze a single work item for multiple analysis types.
        
        Args:
            work_item: Work item data
            analysis_types: Types of analysis to perform
            priority: Analysis priority level
            context: Additional context for analysis
            
        Returns:
            List of analysis results
        """
        work_item_id = str(work_item.get('id', hash(str(work_item))))
        results = []
        
        for analysis_type in analysis_types:
            start_time = time.time()
            
            try:
                # Check cache first
                if self.enable_caching:
                    cache_key = self._get_cache_key(work_item, analysis_type, context)
                    cached_result = self._get_cached_result(cache_key)
                    if cached_result:
                        results.append(cached_result)
                        continue
                
                # Perform analysis
                result = self._analyze_single(work_item, analysis_type, context)
                
                # Cache successful result
                if self.enable_caching and result.error_message is None:
                    self._cache_result(cache_key, result)
                
                results.append(result)
                
                # Update metrics
                self._analysis_count += 1
                if result.used_ai:
                    self._ai_analysis_count += 1
                else:
                    self._fallback_count += 1
                    
                processing_time = time.time() - start_time
                self._total_processing_time += processing_time
                
                logger.debug(f"Analyzed {work_item_id} for {analysis_type.value} "
                           f"in {processing_time:.2f}s (AI: {result.used_ai})")
                
            except Exception as e:
                self._error_count += 1
                logger.error(f"Analysis failed for {work_item_id}: {e}")
                
                # Create error result
                error_result = SemanticAnalysisResult(
                    work_item_id=work_item_id,
                    analysis_type=analysis_type,
                    score=0.0,
                    confidence=0.0,
                    insights=[],
                    structured_data={},
                    processing_time=time.time() - start_time,
                    used_ai=False,
                    error_message=str(e)
                )
                results.append(error_result)
        
        return results
    
    async def analyze_work_item_async(self,
                                    work_item: Dict[str, Any],
                                    analysis_types: List[AnalysisType],
                                    priority: AnalysisPriority = AnalysisPriority.NORMAL,
                                    context: Optional[Dict[str, Any]] = None) -> List[SemanticAnalysisResult]:
        """Async version of work item analysis."""
        work_item_id = str(work_item.get('id', hash(str(work_item))))
        
        # Create async tasks for each analysis type
        tasks = []
        for analysis_type in analysis_types:
            task = self._analyze_single_async(work_item, analysis_type, context)
            tasks.append(task)
        
        # Run analyses concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self._error_count += 1
                logger.error(f"Async analysis failed for {work_item_id}: {result}")
                
                error_result = SemanticAnalysisResult(
                    work_item_id=work_item_id,
                    analysis_type=analysis_types[i],
                    score=0.0,
                    confidence=0.0,
                    insights=[],
                    structured_data={},
                    processing_time=0.0,
                    used_ai=False,
                    error_message=str(result)
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
                self._analysis_count += 1
                if result.used_ai:
                    self._ai_analysis_count += 1
                else:
                    self._fallback_count += 1
        
        return processed_results
    
    def analyze_batch(self,
                     work_items: List[Dict[str, Any]],
                     analysis_types: List[AnalysisType],
                     context: Optional[Dict[str, Any]] = None,
                     max_concurrent: Optional[int] = None) -> BatchAnalysisResult:
        """Analyze a batch of work items.
        
        Args:
            work_items: List of work items to analyze
            analysis_types: Types of analysis to perform
            context: Additional context for analysis
            max_concurrent: Override default concurrency limit
            
        Returns:
            Batch analysis result
        """
        start_time = time.time()
        max_concurrent = max_concurrent or self.max_concurrent
        
        all_results = []
        successful_count = 0
        failed_count = 0
        ai_count = 0
        fallback_count = 0
        
        # Process in batches to manage concurrency
        for i in range(0, len(work_items), max_concurrent):
            batch = work_items[i:i + max_concurrent]
            
            # Process batch synchronously for now (can be made async)
            batch_results = []
            for work_item in batch:
                item_results = self.analyze_work_item(
                    work_item=work_item,
                    analysis_types=analysis_types,
                    priority=AnalysisPriority.BATCH,
                    context=context
                )
                batch_results.extend(item_results)
            
            # Collect statistics
            for result in batch_results:
                all_results.append(result)
                if result.error_message is None:
                    successful_count += 1
                    if result.used_ai:
                        ai_count += 1
                    else:
                        fallback_count += 1
                else:
                    failed_count += 1
        
        total_time = time.time() - start_time
        
        return BatchAnalysisResult(
            total_items=len(work_items) * len(analysis_types),
            successful_analyses=successful_count,
            failed_analyses=failed_count,
            ai_analyses=ai_count,
            fallback_analyses=fallback_count,
            total_processing_time=total_time,
            results=all_results
        )
    
    def _analyze_single(self,
                       work_item: Dict[str, Any],
                       analysis_type: AnalysisType,
                       context: Optional[Dict[str, Any]] = None) -> SemanticAnalysisResult:
        """Perform single analysis with AI/fallback logic."""
        work_item_id = str(work_item.get('id', hash(str(work_item))))
        start_time = time.time()
        
        # Try AI analysis first if available
        if self.ollama_manager.is_available():
            try:
                result = self._perform_ai_analysis(work_item, analysis_type, context)
                if result:
                    result.processing_time = time.time() - start_time
                    return result
            except Exception as e:
                logger.warning(f"AI analysis failed for {work_item_id}: {e}")
        
        # Fallback to mathematical analysis
        try:
            result = self._perform_fallback_analysis(work_item, analysis_type, context)
            result.processing_time = time.time() - start_time
            return result
        except Exception as e:
            logger.error(f"Fallback analysis failed for {work_item_id}: {e}")
            raise
    
    async def _analyze_single_async(self,
                                  work_item: Dict[str, Any],
                                  analysis_type: AnalysisType,
                                  context: Optional[Dict[str, Any]] = None) -> SemanticAnalysisResult:
        """Async version of single analysis."""
        work_item_id = str(work_item.get('id', hash(str(work_item))))
        start_time = time.time()
        
        # Try async AI analysis first if available
        if self.ollama_manager.is_available():
            try:
                result = await self._perform_ai_analysis_async(work_item, analysis_type, context)
                if result:
                    result.processing_time = time.time() - start_time
                    return result
            except Exception as e:
                logger.warning(f"Async AI analysis failed for {work_item_id}: {e}")
        
        # Fallback to mathematical analysis (sync)
        try:
            result = self._perform_fallback_analysis(work_item, analysis_type, context)
            result.processing_time = time.time() - start_time
            return result
        except Exception as e:
            logger.error(f"Async fallback analysis failed for {work_item_id}: {e}")
            raise
    
    def _perform_ai_analysis(self,
                           work_item: Dict[str, Any],
                           analysis_type: AnalysisType,
                           context: Optional[Dict[str, Any]] = None) -> Optional[SemanticAnalysisResult]:
        """Perform AI-powered analysis using Ollama."""
        work_item_id = str(work_item.get('id', hash(str(work_item))))
        
        try:
            # Get system prompt and user prompt
            system_prompt = QVFPromptTemplates.get_system_prompt(analysis_type)
            user_prompt = QVFPromptTemplates.get_analysis_prompt(analysis_type, work_item, context)
            options = QVFPromptTemplates.get_default_options(analysis_type)
            
            # Generate response
            response = self.ollama_manager.generate(
                prompt=user_prompt,
                system=system_prompt,
                options=options,
                use_cache=True
            )
            
            if response and response.response:
                # Parse structured response
                parsed_data = self._parse_ai_response(response.response, analysis_type)
                if parsed_data:
                    return SemanticAnalysisResult(
                        work_item_id=work_item_id,
                        analysis_type=analysis_type,
                        score=self._extract_score(parsed_data, analysis_type),
                        confidence=parsed_data.get('confidence_level', 5) / 10.0,
                        insights=parsed_data.get('key_insights', []),
                        structured_data=parsed_data,
                        processing_time=0.0,  # Will be set by caller
                        used_ai=True,
                        model_used=response.model
                    )
            
            logger.warning(f"Failed to parse AI response for {work_item_id}")
            return None
            
        except Exception as e:
            logger.error(f"AI analysis error for {work_item_id}: {e}")
            return None
    
    async def _perform_ai_analysis_async(self,
                                       work_item: Dict[str, Any],
                                       analysis_type: AnalysisType,
                                       context: Optional[Dict[str, Any]] = None) -> Optional[SemanticAnalysisResult]:
        """Async version of AI analysis."""
        work_item_id = str(work_item.get('id', hash(str(work_item))))
        
        try:
            # Get prompts and options
            system_prompt = QVFPromptTemplates.get_system_prompt(analysis_type)
            user_prompt = QVFPromptTemplates.get_analysis_prompt(analysis_type, work_item, context)
            options = QVFPromptTemplates.get_default_options(analysis_type)
            
            # Generate async response
            response = await self.ollama_manager.generate_async(
                prompt=user_prompt,
                system=system_prompt,
                options=options,
                use_cache=True
            )
            
            if response and response.response:
                # Parse structured response
                parsed_data = self._parse_ai_response(response.response, analysis_type)
                if parsed_data:
                    return SemanticAnalysisResult(
                        work_item_id=work_item_id,
                        analysis_type=analysis_type,
                        score=self._extract_score(parsed_data, analysis_type),
                        confidence=parsed_data.get('confidence_level', 5) / 10.0,
                        insights=parsed_data.get('key_insights', []),
                        structured_data=parsed_data,
                        processing_time=0.0,  # Will be set by caller
                        used_ai=True,
                        model_used=response.model
                    )
            
            logger.warning(f"Failed to parse async AI response for {work_item_id}")
            return None
            
        except Exception as e:
            logger.error(f"Async AI analysis error for {work_item_id}: {e}")
            return None
    
    def _perform_fallback_analysis(self,
                                 work_item: Dict[str, Any],
                                 analysis_type: AnalysisType,
                                 context: Optional[Dict[str, Any]] = None) -> SemanticAnalysisResult:
        """Perform mathematical fallback analysis."""
        work_item_id = str(work_item.get('id', hash(str(work_item))))
        
        # Use fallback engine to get mathematical analysis
        result = self.fallback_engine.analyze_work_item(work_item, analysis_type, context)
        
        return SemanticAnalysisResult(
            work_item_id=work_item_id,
            analysis_type=analysis_type,
            score=result['score'],
            confidence=result['confidence'],
            insights=result['insights'],
            structured_data=result['structured_data'],
            processing_time=0.0,  # Will be set by caller
            used_ai=False,
            model_used=None
        )
    
    def _parse_ai_response(self, response: str, analysis_type: AnalysisType) -> Optional[Dict[str, Any]]:
        """Parse AI response into structured data."""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Find JSON block
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                if end > start:
                    json_str = response[start:end].strip()
                else:
                    json_str = response[start:].strip()
            elif '{' in response and '}' in response:
                # Try to extract JSON directly
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
            else:
                logger.warning(f"No JSON found in response: {response[:100]}...")
                return None
            
            # Parse JSON
            parsed_data = json.loads(json_str)
            
            # Validate response format
            if QVFPromptTemplates.validate_response_format(json_str, analysis_type):
                return parsed_data
            else:
                logger.warning(f"Response format validation failed for {analysis_type.value}")
                return None
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Response parsing error: {e}")
            return None
    
    def _extract_score(self, parsed_data: Dict[str, Any], analysis_type: AnalysisType) -> float:
        """Extract numerical score from parsed data."""
        score_fields = {
            AnalysisType.BUSINESS_VALUE: "business_value_score",
            AnalysisType.STRATEGIC_ALIGNMENT: "strategic_alignment_score",
            AnalysisType.RISK_ASSESSMENT: "overall_risk_score",
            AnalysisType.COMPLEXITY_ANALYSIS: "complexity_score", 
            AnalysisType.FINANCIAL_IMPACT: "financial_impact_score",
            AnalysisType.STAKEHOLDER_IMPACT: "stakeholder_impact_score"
        }
        
        score_field = score_fields.get(analysis_type, "score")
        score = parsed_data.get(score_field, 5)
        
        # Normalize to 0-1 range
        return max(0.0, min(1.0, float(score) / 10.0))
    
    def _get_cache_key(self, 
                      work_item: Dict[str, Any], 
                      analysis_type: AnalysisType,
                      context: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key for analysis."""
        key_data = {
            'work_item': {
                'title': work_item.get('title', ''),
                'description': work_item.get('description', ''),
                'acceptance_criteria': work_item.get('acceptance_criteria', '')
            },
            'analysis_type': analysis_type.value,
            'context': context or {}
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[SemanticAnalysisResult]:
        """Retrieve cached analysis result."""
        if cache_key in self._analysis_cache:
            cached_result = self._analysis_cache[cache_key]
            # Check if cache is still valid (simple time-based TTL)
            if hasattr(cached_result, '_cache_time'):
                cache_age = time.time() - cached_result._cache_time
                if cache_age < self._cache_ttl:
                    return cached_result
                else:
                    # Remove expired cache entry
                    del self._analysis_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: SemanticAnalysisResult) -> None:
        """Cache analysis result."""
        # Add cache timestamp
        result._cache_time = time.time()
        self._analysis_cache[cache_key] = result
        
        # Simple cache size management
        if len(self._analysis_cache) > 1000:
            # Remove oldest entries
            sorted_items = sorted(
                self._analysis_cache.items(),
                key=lambda x: getattr(x[1], '_cache_time', 0)
            )
            # Keep newest 800 entries
            for key, _ in sorted_items[:-800]:
                del self._analysis_cache[key]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "total_analyses": self._analysis_count,
            "ai_analyses": self._ai_analysis_count,
            "fallback_analyses": self._fallback_count,
            "error_count": self._error_count,
            "ai_usage_rate": self._ai_analysis_count / max(self._analysis_count, 1),
            "success_rate": (self._analysis_count - self._error_count) / max(self._analysis_count, 1),
            "avg_processing_time": self._total_processing_time / max(self._analysis_count, 1),
            "cache_size": len(self._analysis_cache),
            "ollama_status": self.ollama_manager.get_health_status()
        }
    
    def clear_cache(self) -> int:
        """Clear analysis cache."""
        cache_size = len(self._analysis_cache)
        self._analysis_cache.clear()
        logger.info(f"Cleared {cache_size} cached analysis results")
        return cache_size