"""QVF AI Enhancement Module

This module provides optional AI-powered enhancements to the QVF mathematical
prioritization engine. The AI module operates on a local-first principle using
Ollama for privacy and performance, with complete mathematical fallback when
AI is unavailable.

Key Design Principles:
1. **Local-First**: Uses Ollama for on-device processing
2. **Privacy-Preserving**: No external API calls for sensitive data
3. **Fallback-Ready**: 100% functionality without AI enabled
4. **Optional Enhancement**: AI adds value but never blocks core functionality

Components:
- OllamaManager: Server connection and model management
- SemanticAnalyzer: Text-based work item analysis
- FallbackEngine: Mathematical alternatives to AI operations
- PromptTemplates: Optimized prompts for consistent results

Usage:
    from datascience_platform.qvf.ai import OllamaManager, SemanticAnalyzer
    
    # Initialize with automatic fallback
    ollama = OllamaManager()
    analyzer = SemanticAnalyzer(ollama_manager=ollama)
    
    # Analyze work item (falls back to math if AI unavailable)
    analysis = analyzer.analyze_work_item(work_item)
"""

from .ollama_manager import OllamaManager, OllamaHealth
from .semantic import SemanticAnalyzer
from .fallback import FallbackEngine
from .prompt_templates import QVFPromptTemplates

__all__ = [
    "OllamaManager",
    "OllamaHealth", 
    "SemanticAnalyzer",
    "FallbackEngine",
    "QVFPromptTemplates"
]