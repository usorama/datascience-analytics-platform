"""Text Processing Module for Business Documents

This module provides text preprocessing, parsing, and entity extraction
capabilities for strategy documents, OKRs, and work item descriptions.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime

import pandas as pd
from ..models import WorkItemState, WorkItemType
from .models import (
    OKR, KeyResult, StrategyDocument, DocumentSection, 
    SemanticWorkItem, DocumentType
)

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """Preprocess text for semantic analysis."""
    
    def __init__(self):
        # Common business stopwords to keep (unlike standard NLP)
        self.business_keywords = {
            'roi', 'kpi', 'okr', 'revenue', 'cost', 'customer', 'user',
            'product', 'feature', 'epic', 'story', 'sprint', 'quarter',
            'target', 'goal', 'objective', 'metric', 'performance'
        }
        
        # Regex patterns
        self.url_pattern = re.compile(r'https?://\S+')
        self.email_pattern = re.compile(r'\S+@\S+')
        self.mention_pattern = re.compile(r'@\w+')
        self.ticket_pattern = re.compile(r'[A-Z]+-\d+')  # JIRA-style
        
    def preprocess(self, text: str, preserve_structure: bool = False) -> str:
        """Clean and normalize text while preserving business meaning."""
        if not text:
            return ""
        
        # Preserve original for structure analysis
        original = text
        
        # Basic cleaning
        text = self._normalize_whitespace(text)
        text = self._clean_special_chars(text)
        
        # Preserve important patterns
        tickets = self.ticket_pattern.findall(text)
        
        # Remove URLs but keep domains
        text = self._clean_urls(text)
        
        # Normalize case but preserve acronyms
        text = self._smart_lowercase(text)
        
        # Restore important patterns
        for ticket in tickets:
            text = text.replace(ticket.lower(), ticket)
        
        if preserve_structure:
            return text, self._extract_structure(original)
        
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace while preserving paragraph structure."""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def _clean_special_chars(self, text: str) -> str:
        """Remove special characters while keeping business-relevant ones."""
        # Keep: alphanumeric, spaces, common punctuation, currency symbols
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\/\$\£\€\%\@\#]', ' ', text)
        return text
    
    def _clean_urls(self, text: str) -> str:
        """Replace URLs with domain names."""
        def extract_domain(match):
            url = match.group(0)
            domain = re.search(r'://([^/]+)', url)
            return f"[link:{domain.group(1) if domain else 'url'}]"
        
        return self.url_pattern.sub(extract_domain, text)
    
    def _smart_lowercase(self, text: str) -> str:
        """Lowercase text but preserve acronyms and special terms."""
        words = text.split()
        processed = []
        
        for word in words:
            # Keep all-caps words (likely acronyms)
            if word.isupper() and len(word) > 1:
                processed.append(word)
            # Keep mixed case technical terms
            elif any(c.isupper() for c in word[1:]):
                processed.append(word)
            else:
                processed.append(word.lower())
        
        return ' '.join(processed)
    
    def _extract_structure(self, text: str) -> Dict[str, Any]:
        """Extract structural information from text."""
        return {
            'paragraphs': len(text.split('\n\n')),
            'sentences': len(re.split(r'[.!?]+', text)),
            'bullet_points': text.count('\n•') + text.count('\n-') + text.count('\n*'),
            'has_sections': bool(re.search(r'\n#+\s', text) or re.search(r'\n\d+\.\s', text))
        }
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key business phrases from text."""
        # Simple approach - can be enhanced with more sophisticated methods
        phrases = []
        
        # Look for quoted phrases
        quoted = re.findall(r'"([^"]+)"', text)
        phrases.extend(quoted)
        
        # Look for capitalized phrases (likely important)
        cap_phrases = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', text)
        phrases.extend(cap_phrases)
        
        # Look for metric-like phrases
        metric_phrases = re.findall(r'\d+%?\s+\w+', text)
        phrases.extend(metric_phrases)
        
        return list(set(phrases))


class DocumentParser:
    """Parse various document formats into structured format."""
    
    def __init__(self, preprocessor: Optional[TextPreprocessor] = None):
        self.preprocessor = preprocessor or TextPreprocessor()
        
    def parse_strategy_document(
        self, 
        file_path: Path,
        document_type: Optional[DocumentType] = None
    ) -> StrategyDocument:
        """Parse a strategy document from file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        # Determine document type
        if document_type is None:
            document_type = self._infer_document_type(file_path)
        
        # Read content based on file type
        if file_path.suffix == '.txt':
            content = file_path.read_text(encoding='utf-8')
        elif file_path.suffix == '.md':
            content = file_path.read_text(encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Create document
        doc = StrategyDocument(
            doc_id=f"doc_{file_path.stem}_{hash(file_path)}",
            title=file_path.stem.replace('_', ' ').title(),
            document_type=document_type,
            full_text=content,
            created_date=datetime.fromtimestamp(file_path.stat().st_ctime),
            last_updated=datetime.fromtimestamp(file_path.stat().st_mtime)
        )
        
        # Parse sections
        doc.sections = self._parse_sections(content)
        
        # Extract strategic elements
        doc.strategic_themes = self._extract_themes(content)
        doc.key_metrics = self._extract_metrics(content)
        doc.strategic_pillars = self._extract_pillars(content)
        
        return doc
    
    def parse_okr_csv(self, file_path: Path) -> List[OKR]:
        """Parse OKRs from CSV file."""
        df = pd.read_csv(file_path)
        
        # Expected columns: Objective, KR1, KR2, KR3, Owner, Period, Level
        okrs = []
        
        for _, row in df.iterrows():
            okr = OKR(
                okr_id=f"okr_{row.name}_{hash(row['Objective'])}",
                period=row.get('Period', 'Q1 2025'),
                level=row.get('Level', 'team').lower(),
                objective_text=row['Objective'],
                owner=row.get('Owner', ''),
                team=row.get('Team', '')
            )
            
            # Extract key results
            for i in range(1, 6):  # Support up to 5 KRs
                kr_col = f'KR{i}'
                if kr_col in row and pd.notna(row[kr_col]):
                    kr_text = str(row[kr_col])
                    kr = self._parse_key_result(kr_text, i)
                    okr.key_results.append(kr)
            
            # Extract strategic alignment
            if 'Strategic Pillar' in row and pd.notna(row['Strategic Pillar']):
                okr.strategic_pillars = [p.strip() for p in str(row['Strategic Pillar']).split(',')]
            
            if 'Business Impact' in row and pd.notna(row['Business Impact']):
                okr.business_impact = str(row['Business Impact'])
            
            okrs.append(okr)
        
        return okrs
    
    def parse_work_item_text(self, work_item: Any) -> SemanticWorkItem:
        """Enhance work item with parsed text content."""
        # Create semantic work item from base work item
        semantic_item = SemanticWorkItem(**work_item.__dict__)
        
        # Combine available text fields
        text_parts = []
        
        if hasattr(work_item, 'description') and work_item.description:
            semantic_item.full_description = work_item.description
            text_parts.append(work_item.description)
        
        # Parse acceptance criteria if in description
        if semantic_item.full_description:
            ac_match = re.search(
                r'acceptance criteria:?\s*\n(.*?)(?:\n\n|$)',
                semantic_item.full_description,
                re.IGNORECASE | re.DOTALL
            )
            if ac_match:
                semantic_item.acceptance_criteria_text = ac_match.group(1).strip()
        
        # Extract themes from title and description
        all_text = ' '.join(text_parts)
        if all_text:
            semantic_item.strategic_themes = self._extract_themes(all_text)
            semantic_item.mentioned_metrics = self._extract_metrics(all_text)
        
        return semantic_item
    
    def _infer_document_type(self, file_path: Path) -> DocumentType:
        """Infer document type from filename and content."""
        name_lower = file_path.stem.lower()
        
        if 'vision' in name_lower:
            return DocumentType.VISION
        elif 'mission' in name_lower:
            return DocumentType.MISSION
        elif 'strategy' in name_lower or 'strategic' in name_lower:
            return DocumentType.STRATEGY
        elif 'roadmap' in name_lower:
            return DocumentType.ROADMAP
        elif 'okr' in name_lower:
            return DocumentType.OKR
        else:
            return DocumentType.STRATEGY
    
    def _parse_sections(self, content: str) -> List[DocumentSection]:
        """Parse document into sections."""
        sections = []
        
        # Split by markdown headers or numbered sections
        lines = content.split('\n')
        current_section = []
        current_title = "Introduction"
        current_level = 0
        
        for line in lines:
            # Check for markdown header
            header_match = re.match(r'^(#+)\s+(.+)$', line)
            if header_match:
                # Save previous section
                if current_section:
                    sections.append(DocumentSection(
                        section_id=f"sec_{len(sections)}",
                        title=current_title,
                        content='\n'.join(current_section).strip(),
                        section_type='heading',
                        level=current_level
                    ))
                
                # Start new section
                current_level = len(header_match.group(1))
                current_title = header_match.group(2)
                current_section = []
            else:
                current_section.append(line)
        
        # Save last section
        if current_section:
            sections.append(DocumentSection(
                section_id=f"sec_{len(sections)}",
                title=current_title,
                content='\n'.join(current_section).strip(),
                section_type='heading',
                level=current_level
            ))
        
        return sections
    
    def _parse_key_result(self, kr_text: str, index: int) -> KeyResult:
        """Parse key result from text."""
        kr = KeyResult(
            kr_id=f"kr_{index}_{hash(kr_text)}",
            text=kr_text
        )
        
        # Try to extract target value
        # Pattern: "Achieve X [unit]" or "X% of Y"
        number_match = re.search(r'(\d+(?:\.\d+)?)\s*(%|k|K|M|users|customers|revenue)?', kr_text)
        if number_match:
            kr.target_value = float(number_match.group(1))
            if number_match.group(2):
                kr.unit = number_match.group(2)
        
        # Extract deadline
        deadline_match = re.search(r'by (Q\d|end of|EOY|EOM)', kr_text, re.IGNORECASE)
        if deadline_match:
            # Simple deadline parsing - can be enhanced
            deadline_text = deadline_match.group(1)
            # TODO: Convert to actual date
        
        return kr
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract strategic themes from text."""
        themes = []
        
        # Common strategic themes to look for
        theme_keywords = {
            'growth': ['growth', 'scale', 'expand', 'increase'],
            'efficiency': ['efficiency', 'optimize', 'streamline', 'automate'],
            'innovation': ['innovation', 'innovate', 'transform', 'disrupt'],
            'customer': ['customer', 'user', 'client', 'satisfaction'],
            'quality': ['quality', 'excellence', 'reliability', 'performance'],
            'security': ['security', 'compliance', 'privacy', 'protection']
        }
        
        text_lower = text.lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _extract_metrics(self, text: str) -> List[str]:
        """Extract mentioned metrics from text."""
        metrics = []
        
        # Pattern for metrics: number + unit/description
        metric_patterns = [
            r'(\d+%?\s+(?:increase|decrease|reduction|improvement|growth))',
            r'(\$?\d+(?:\.\d+)?[KMB]?\s+(?:revenue|cost|savings|budget))',
            r'(\d+\s+(?:users|customers|downloads|visits|sessions))',
            r'(NPS|CSAT|CAC|LTV|MRR|ARR|ROI)\s*(?:of\s+)?(\d+)?'
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics.extend(matches)
        
        return list(set(metrics))
    
    def _extract_pillars(self, text: str) -> List[str]:
        """Extract strategic pillars from text."""
        pillars = []
        
        # Look for numbered or bulleted lists after "pillars" or "priorities"
        pillar_section = re.search(
            r'(?:strategic\s+)?(?:pillars?|priorities)\s*:?\s*\n((?:[\s\-\*\d\.]+.+\n?)+)',
            text,
            re.IGNORECASE
        )
        
        if pillar_section:
            pillar_text = pillar_section.group(1)
            # Extract individual items
            items = re.findall(r'[\-\*\d\.]+\s*(.+)', pillar_text)
            pillars.extend([item.strip() for item in items])
        
        return pillars


class BusinessEntityExtractor:
    """Extract business entities and relationships from text."""
    
    def __init__(self):
        # Business entity patterns
        self.patterns = {
            'team': re.compile(r'(?:team|department|division|group):\s*(\w+)', re.IGNORECASE),
            'person': re.compile(r'(?:owner|lead|manager|PM):\s*([A-Z]\w+(?:\s+[A-Z]\w+)?)', re.IGNORECASE),
            'timeline': re.compile(r'(?:by|before|until|deadline:?)\s*(Q\d\s+\d{4}|[A-Z][a-z]+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', re.IGNORECASE),
            'dependency': re.compile(r'(?:depends on|blocked by|requires|needs):\s*([^,\n]+)', re.IGNORECASE),
            'product': re.compile(r'(?:product|feature|component|module):\s*(\w+(?:\s+\w+)?)', re.IGNORECASE)
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract all business entities from text."""
        entities = {}
        
        for entity_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                entities[entity_type] = list(set(matches))
        
        return entities
    
    def extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """Extract relationships between entities."""
        relationships = []
        
        # Dependency relationships
        dep_patterns = [
            r'(\w+)\s+depends on\s+(\w+)',
            r'(\w+)\s+blocks\s+(\w+)',
            r'(\w+)\s+requires\s+(\w+)',
            r'(\w+)\s+enables\s+(\w+)'
        ]
        
        for pattern in dep_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for source, target in matches:
                relationships.append({
                    'source': source,
                    'target': target,
                    'type': 'dependency',
                    'pattern': pattern
                })
        
        return relationships