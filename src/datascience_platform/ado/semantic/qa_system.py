"""Intelligent Q&A System for Strategic Information Gathering

This module provides an interactive Q&A system that identifies missing
information and collects contextual answers to improve alignment scoring.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable
from datetime import datetime
from enum import Enum
import re

import numpy as np

from .models import (
    Question, QuestionType, InformationGap,
    SemanticWorkItem, OKR, StrategyDocument,
    AlignmentScore
)
from .alignment import StrategicAlignmentCalculator, SemanticScorer
from .embedder import SemanticEmbedder


logger = logging.getLogger(__name__)


class AnswerValidation:
    """Validates answers based on question constraints."""
    
    @staticmethod
    def validate_text(answer: str, rules: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate text answer against rules."""
        for rule in rules:
            if rule.startswith('min_length:'):
                min_len = int(rule.split(':')[1])
                if len(answer) < min_len:
                    return False, f"Answer must be at least {min_len} characters"
            
            elif rule.startswith('max_length:'):
                max_len = int(rule.split(':')[1])
                if len(answer) > max_len:
                    return False, f"Answer must be at most {max_len} characters"
            
            elif rule.startswith('pattern:'):
                pattern = rule.split(':', 1)[1]
                if not re.match(pattern, answer):
                    return False, f"Answer must match pattern: {pattern}"
        
        return True, None
    
    @staticmethod
    def validate_choice(answer: str, options: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate choice answer."""
        if answer not in options:
            # Try case-insensitive match
            lower_options = {opt.lower(): opt for opt in options}
            if answer.lower() in lower_options:
                return True, None
            
            # Try numeric choice (1, 2, 3...)
            if answer.isdigit():
                idx = int(answer) - 1
                if 0 <= idx < len(options):
                    return True, None
            
            return False, f"Please choose from: {', '.join(options)}"
        
        return True, None
    
    @staticmethod
    def validate_number(answer: str) -> Tuple[bool, Optional[str]]:
        """Validate numeric answer."""
        try:
            float(answer)
            return True, None
        except ValueError:
            return False, "Please provide a numeric value"
    
    @staticmethod
    def validate_date(answer: str) -> Tuple[bool, Optional[str]]:
        """Validate date answer."""
        date_patterns = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%b %d, %Y",
            "%B %d, %Y"
        ]
        
        for pattern in date_patterns:
            try:
                datetime.strptime(answer, pattern)
                return True, None
            except ValueError:
                continue
        
        return False, "Please provide a valid date (e.g., 2025-08-15 or Aug 15, 2025)"


class QASession:
    """Manages a Q&A session for gathering information."""
    
    def __init__(
        self,
        session_id: str,
        work_items: List[SemanticWorkItem],
        gaps: List[InformationGap],
        questions: List[Question]
    ):
        self.session_id = session_id
        self.work_items = {item.work_item_id: item for item in work_items}
        self.gaps = gaps
        self.questions = questions
        self.answers = {}
        self.answered_questions = set()
        self.created_at = datetime.now()
        self.completed_at = None
        
        # Question graph for dependencies
        self.question_graph = self._build_question_graph()
        
        # Session state
        self.current_question_idx = 0
        self.skipped_questions = []
        self.validation_attempts = {}
    
    def _build_question_graph(self) -> Dict[str, Question]:
        """Build question dependency graph."""
        graph = {q.question_id: q for q in self.questions}
        return graph
    
    def get_next_question(self) -> Optional[Question]:
        """Get next unanswered question based on priority and dependencies."""
        # Filter available questions
        available = []
        
        for question in self.questions:
            if question.question_id in self.answered_questions:
                continue
            
            # Check dependencies
            if question.depends_on:
                deps_satisfied = all(
                    dep_id in self.answered_questions 
                    for dep_id in question.depends_on
                )
                if not deps_satisfied:
                    continue
            
            available.append(question)
        
        if not available:
            return None
        
        # Sort by severity and type priority
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        available.sort(
            key=lambda q: (
                severity_order.get(q.severity, 4),
                q.question_type != QuestionType.CONTEXT
            )
        )
        
        return available[0]
    
    def answer_question(
        self,
        question_id: str,
        answer: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[List[Question]]]:
        """Process answer and return validation result and follow-up questions.
        
        Returns:
            Tuple of (is_valid, error_message, follow_up_questions)
        """
        question = self.question_graph.get(question_id)
        if not question:
            return False, "Question not found", None
        
        # Validate answer
        is_valid, error_msg = self._validate_answer(question, answer)
        if not is_valid:
            self.validation_attempts[question_id] = \
                self.validation_attempts.get(question_id, 0) + 1
            return False, error_msg, None
        
        # Store answer
        self.answers[question_id] = {
            'question': question,
            'answer': answer,
            'metadata': metadata or {},
            'answered_at': datetime.now(),
            'attempts': self.validation_attempts.get(question_id, 0) + 1
        }
        self.answered_questions.add(question_id)
        
        # Generate follow-up questions based on answer
        follow_ups = self._generate_follow_ups(question, answer)
        
        # Update affected work items
        self._update_work_items(question, answer)
        
        return True, None, follow_ups
    
    def _validate_answer(self, question: Question, answer: str) -> Tuple[bool, Optional[str]]:
        """Validate answer based on question type and rules."""
        if not answer or not answer.strip():
            return False, "Answer cannot be empty"
        
        answer = answer.strip()
        
        # Type-specific validation
        if question.expected_format == 'choice' and question.options:
            return AnswerValidation.validate_choice(answer, question.options)
        
        elif question.expected_format == 'number':
            return AnswerValidation.validate_number(answer)
        
        elif question.expected_format == 'date':
            return AnswerValidation.validate_date(answer)
        
        elif question.expected_format == 'text':
            return AnswerValidation.validate_text(answer, question.validation_rules)
        
        # Default validation
        return True, None
    
    def _generate_follow_ups(
        self,
        question: Question,
        answer: str
    ) -> List[Question]:
        """Generate follow-up questions based on answer."""
        follow_ups = []
        
        # Context-based follow-ups
        if question.question_type == QuestionType.CONTEXT:
            if "not strategically aligned" in answer.lower():
                # Ask about potential cancellation
                follow_ups.append(Question(
                    question_id=f"{question.question_id}_cancel",
                    text="Should this item be cancelled or deferred to focus on strategic work?",
                    question_type=QuestionType.PRIORITY,
                    context=f"Item marked as not strategically aligned",
                    business_impact="Free up resources for strategic initiatives",
                    severity='high',
                    affected_items=question.affected_items,
                    options=["Cancel", "Defer to next quarter", "Keep but deprioritize", "Reconsider alignment"],
                    expected_format='choice'
                ))
            
            elif "other" in answer.lower():
                # Ask for specification
                follow_ups.append(Question(
                    question_id=f"{question.question_id}_specify",
                    text="Please specify the strategic objective or alignment:",
                    question_type=QuestionType.CONTEXT,
                    context="Custom strategic alignment specified",
                    business_impact="Understand unique strategic value",
                    severity='medium',
                    affected_items=question.affected_items,
                    expected_format='text',
                    validation_rules=['min_length:20', 'max_length:200']
                ))
        
        elif question.question_type == QuestionType.METRIC:
            # Ask for measurement approach if metric provided
            if answer and len(answer) > 10:
                follow_ups.append(Question(
                    question_id=f"{question.question_id}_measure",
                    text=f"How will '{answer}' be measured?",
                    question_type=QuestionType.METRIC,
                    context="Metric measurement definition needed",
                    business_impact="Enable tracking and reporting",
                    severity='medium',
                    affected_items=question.affected_items,
                    expected_format='text',
                    validation_rules=['min_length:20']
                ))
        
        return follow_ups
    
    def _update_work_items(self, question: Question, answer: str):
        """Update work items based on answer."""
        for item_id in question.affected_items:
            if item_id not in self.work_items:
                continue
            
            item = self.work_items[item_id]
            
            # Update based on question type
            if question.question_type == QuestionType.CONTEXT:
                if not item.business_justification:
                    item.business_justification = answer
                else:
                    item.business_justification += f"\n\n[Q&A Update]: {answer}"
            
            elif question.question_type == QuestionType.METRIC:
                if not item.mentioned_metrics:
                    item.mentioned_metrics = []
                item.mentioned_metrics.append(answer)
            
            # Mark as updated
            if not hasattr(item, 'qa_updates'):
                item.qa_updates = []
            
            item.qa_updates.append({
                'question_id': question.question_id,
                'timestamp': datetime.now(),
                'update_type': question.question_type.value
            })
    
    def skip_question(self, question_id: str, reason: str = ""):
        """Skip a question with optional reason."""
        self.skipped_questions.append({
            'question_id': question_id,
            'reason': reason,
            'skipped_at': datetime.now()
        })
        self.answered_questions.add(question_id)
    
    def get_progress(self) -> Dict[str, Any]:
        """Get session progress statistics."""
        total_questions = len(self.questions)
        answered = len(self.answered_questions) - len(self.skipped_questions)
        
        return {
            'total_questions': total_questions,
            'answered': answered,
            'skipped': len(self.skipped_questions),
            'remaining': total_questions - len(self.answered_questions),
            'completion_rate': answered / total_questions if total_questions > 0 else 0,
            'by_severity': self._get_progress_by_severity(),
            'by_type': self._get_progress_by_type()
        }
    
    def _get_progress_by_severity(self) -> Dict[str, Dict[str, int]]:
        """Get progress breakdown by severity."""
        severity_stats = {}
        
        for severity in ['critical', 'high', 'medium', 'low']:
            questions = [q for q in self.questions if q.severity == severity]
            answered = [
                q for q in questions 
                if q.question_id in self.answered_questions
                and q.question_id not in [s['question_id'] for s in self.skipped_questions]
            ]
            
            severity_stats[severity] = {
                'total': len(questions),
                'answered': len(answered),
                'completion_rate': len(answered) / len(questions) if questions else 0
            }
        
        return severity_stats
    
    def _get_progress_by_type(self) -> Dict[str, Dict[str, int]]:
        """Get progress breakdown by question type."""
        type_stats = {}
        
        for qtype in QuestionType:
            questions = [q for q in self.questions if q.question_type == qtype]
            answered = [
                q for q in questions 
                if q.question_id in self.answered_questions
                and q.question_id not in [s['question_id'] for s in self.skipped_questions]
            ]
            
            type_stats[qtype.value] = {
                'total': len(questions),
                'answered': len(answered),
                'completion_rate': len(answered) / len(questions) if questions else 0
            }
        
        return type_stats
    
    def complete_session(self) -> Dict[str, Any]:
        """Complete the Q&A session and return summary."""
        self.completed_at = datetime.now()
        
        return {
            'session_id': self.session_id,
            'duration': (self.completed_at - self.created_at).total_seconds(),
            'progress': self.get_progress(),
            'answers_collected': len(self.answers),
            'work_items_updated': len([
                item for item in self.work_items.values()
                if hasattr(item, 'qa_updates')
            ])
        }


class IntelligentQASystem:
    """Main Q&A system for strategic information gathering."""
    
    def __init__(
        self,
        scorer: Optional[SemanticScorer] = None,
        embedder: Optional[SemanticEmbedder] = None,
        history_path: Optional[Path] = None
    ):
        self.scorer = scorer or SemanticScorer()
        self.embedder = embedder or SemanticEmbedder()
        self.history_path = history_path or Path.home() / ".ado_qa" / "history"
        self.history_path.mkdir(parents=True, exist_ok=True)
        
        # Active sessions
        self.active_sessions = {}
        
        # Question templates
        self.question_templates = self._load_question_templates()
        
        # Learning cache
        self.answer_patterns = self._load_answer_patterns()
    
    def _load_question_templates(self) -> Dict[str, List[str]]:
        """Load question templates for different scenarios."""
        return {
            'missing_strategy': [
                "What strategic objective does '{title}' support?",
                "How does '{title}' align with our company goals?",
                "Which strategic pillar does '{title}' contribute to?"
            ],
            'missing_metrics': [
                "What metrics will measure the success of '{title}'?",
                "What are the target KPIs for '{title}'?",
                "How will we track progress on '{title}'?"
            ],
            'missing_justification': [
                "What is the business justification for '{title}'?",
                "What problem does '{title}' solve?",
                "What value does '{title}' deliver to customers?"
            ],
            'missing_timeline': [
                "When should '{title}' be completed?",
                "What is the target delivery date for '{title}'?",
                "Are there any critical deadlines for '{title}'?"
            ],
            'missing_dependencies': [
                "What does '{title}' depend on?",
                "Are there any blockers for '{title}'?",
                "What other work must complete before '{title}'?"
            ]
        }
    
    def _load_answer_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load learned answer patterns from history."""
        patterns_file = self.history_path / "answer_patterns.json"
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                return json.load(f)
        return {}
    
    def create_session(
        self,
        work_items: List[SemanticWorkItem],
        strategy_docs: List[StrategyDocument],
        okrs: List[OKR],
        focus_areas: Optional[List[str]] = None
    ) -> QASession:
        """Create new Q&A session for work items.
        
        Args:
            work_items: Items to analyze
            strategy_docs: Available strategy documents
            okrs: Available OKRs
            focus_areas: Optional list of areas to focus on
            
        Returns:
            New QASession instance
        """
        # Run semantic scoring to identify gaps
        results = self.scorer.score_work_items(
            work_items,
            strategy_docs,
            okrs,
            generate_questions=True
        )
        
        gaps = results['gaps']
        questions = results['questions']
        
        # Filter by focus areas if provided
        if focus_areas:
            questions = self._filter_questions_by_focus(questions, focus_areas)
        
        # Enhance questions with learned patterns
        questions = self._enhance_questions_with_patterns(questions, work_items)
        
        # Create session
        session_id = f"qa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = QASession(session_id, work_items, gaps, questions)
        
        # Store in active sessions
        self.active_sessions[session_id] = session
        
        # Log session creation
        logger.info(f"Created Q&A session {session_id} with {len(questions)} questions")
        
        return session
    
    def _filter_questions_by_focus(
        self,
        questions: List[Question],
        focus_areas: List[str]
    ) -> List[Question]:
        """Filter questions by focus areas."""
        filtered = []
        
        for question in questions:
            # Check if question relates to focus areas
            q_text_lower = question.text.lower()
            q_context_lower = question.context.lower()
            
            for area in focus_areas:
                area_lower = area.lower()
                if (area_lower in q_text_lower or 
                    area_lower in q_context_lower or
                    area_lower in question.question_type.value):
                    filtered.append(question)
                    break
        
        return filtered
    
    def _enhance_questions_with_patterns(
        self,
        questions: List[Question],
        work_items: List[SemanticWorkItem]
    ) -> List[Question]:
        """Enhance questions using learned answer patterns."""
        work_item_map = {item.work_item_id: item for item in work_items}
        
        for question in questions:
            # Check if we have patterns for this question type
            pattern_key = f"{question.question_type.value}_{question.severity}"
            if pattern_key in self.answer_patterns:
                patterns = self.answer_patterns[pattern_key]
                
                # Add common answers as options if not already present
                if not question.options and len(patterns) >= 3:
                    top_patterns = sorted(
                        patterns,
                        key=lambda p: p.get('frequency', 0),
                        reverse=True
                    )[:5]
                    
                    question.options = [p['answer'] for p in top_patterns]
                    question.options.append("Other (please specify)")
        
        return questions
    
    def process_interactive(
        self,
        session: QASession,
        input_func: Optional[Callable] = None,
        output_func: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Process Q&A session interactively.
        
        Args:
            session: QASession to process
            input_func: Function to get user input (defaults to input())
            output_func: Function to display output (defaults to print())
            
        Returns:
            Session completion summary
        """
        if input_func is None:
            input_func = input
        if output_func is None:
            output_func = print
        
        output_func("\n" + "="*70)
        output_func(f"Strategic Information Q&A Session")
        output_func(f"Session ID: {session.session_id}")
        output_func("="*70 + "\n")
        
        # Show initial progress
        progress = session.get_progress()
        output_func(f"Total questions: {progress['total_questions']}")
        output_func(f"Critical: {progress['by_severity']['critical']['total']}")
        output_func(f"High: {progress['by_severity']['high']['total']}")
        output_func(f"Medium: {progress['by_severity']['medium']['total']}")
        output_func(f"Low: {progress['by_severity']['low']['total']}")
        output_func("\n")
        
        # Process questions
        while True:
            question = session.get_next_question()
            if not question:
                break
            
            # Display question
            output_func("-" * 50)
            output_func(f"\n[{question.severity.upper()}] {question.text}")
            
            if question.context:
                output_func(f"Context: {question.context}")
            
            if question.business_impact:
                output_func(f"Impact: {question.business_impact}")
            
            if question.options:
                output_func("\nOptions:")
                for i, option in enumerate(question.options, 1):
                    output_func(f"  {i}. {option}")
            
            # Get answer
            while True:
                answer = input_func("\nYour answer (or 'skip' to skip): ").strip()
                
                if answer.lower() == 'skip':
                    reason = input_func("Reason for skipping (optional): ").strip()
                    session.skip_question(question.question_id, reason)
                    break
                
                # Handle numeric choice
                if question.options and answer.isdigit():
                    idx = int(answer) - 1
                    if 0 <= idx < len(question.options):
                        answer = question.options[idx]
                
                # Validate and process answer
                is_valid, error_msg, follow_ups = session.answer_question(
                    question.question_id,
                    answer
                )
                
                if is_valid:
                    output_func("✓ Answer recorded\n")
                    
                    # Show follow-up questions if any
                    if follow_ups:
                        output_func(f"Generated {len(follow_ups)} follow-up questions")
                        # Add to session
                        session.questions.extend(follow_ups)
                        for q in follow_ups:
                            session.question_graph[q.question_id] = q
                    
                    break
                else:
                    output_func(f"❌ {error_msg}")
            
            # Show progress
            progress = session.get_progress()
            output_func(f"\nProgress: {progress['answered']}/{progress['total_questions']} " +
                       f"({progress['completion_rate']:.0%})")
        
        # Complete session
        summary = session.complete_session()
        
        output_func("\n" + "="*70)
        output_func("Session Complete!")
        output_func("="*70)
        output_func(f"Duration: {summary['duration']:.0f} seconds")
        output_func(f"Answers collected: {summary['answers_collected']}")
        output_func(f"Work items updated: {summary['work_items_updated']}")
        
        # Save session history
        self._save_session_history(session)
        
        # Update answer patterns
        self._update_answer_patterns(session)
        
        return summary
    
    def process_batch(
        self,
        session: QASession,
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Process Q&A session with batch answers.
        
        Args:
            session: QASession to process
            answers: Dictionary mapping question_id to answer
            
        Returns:
            Processing results
        """
        results = {
            'processed': [],
            'errors': [],
            'follow_ups': []
        }
        
        for question_id, answer in answers.items():
            question = session.question_graph.get(question_id)
            if not question:
                results['errors'].append({
                    'question_id': question_id,
                    'error': 'Question not found'
                })
                continue
            
            is_valid, error_msg, follow_ups = session.answer_question(
                question_id,
                answer
            )
            
            if is_valid:
                results['processed'].append(question_id)
                if follow_ups:
                    results['follow_ups'].extend(follow_ups)
                    # Add to session
                    session.questions.extend(follow_ups)
                    for q in follow_ups:
                        session.question_graph[q.question_id] = q
            else:
                results['errors'].append({
                    'question_id': question_id,
                    'error': error_msg
                })
        
        # Complete session if all questions answered
        if not session.get_next_question():
            results['summary'] = session.complete_session()
            self._save_session_history(session)
            self._update_answer_patterns(session)
        
        return results
    
    def recalculate_alignment(
        self,
        session: QASession,
        strategy_docs: List[StrategyDocument],
        okrs: List[OKR]
    ) -> Dict[str, AlignmentScore]:
        """Recalculate alignment scores after Q&A session.
        
        Returns:
            Dictionary mapping work_item_id to new AlignmentScore
        """
        new_scores = {}
        
        for item_id, item in session.work_items.items():
            # Recalculate with updated information
            new_score = self.scorer.alignment_calculator.calculate_alignment(
                item,
                strategy_docs,
                okrs,
                include_evidence=True
            )
            
            # Add Q&A confidence boost
            if hasattr(item, 'qa_updates') and item.qa_updates:
                # Boost confidence based on questions answered
                qa_boost = min(0.2, len(item.qa_updates) * 0.05)
                new_score.confidence = min(1.0, new_score.confidence + qa_boost)
            
            new_scores[item_id] = new_score
            item.alignment_score = new_score
        
        return new_scores
    
    def _save_session_history(self, session: QASession):
        """Save session to history."""
        session_file = self.history_path / f"{session.session_id}.json"
        
        history_data = {
            'session_id': session.session_id,
            'created_at': session.created_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'questions_count': len(session.questions),
            'answers': {
                qid: {
                    'question': data['question'].text,
                    'answer': data['answer'],
                    'answered_at': data['answered_at'].isoformat()
                }
                for qid, data in session.answers.items()
            },
            'skipped': session.skipped_questions,
            'progress': session.get_progress()
        }
        
        with open(session_file, 'w') as f:
            json.dump(history_data, f, indent=2)
    
    def _update_answer_patterns(self, session: QASession):
        """Update answer patterns from session."""
        for qid, data in session.answers.items():
            question = data['question']
            answer = data['answer']
            
            pattern_key = f"{question.question_type.value}_{question.severity}"
            
            if pattern_key not in self.answer_patterns:
                self.answer_patterns[pattern_key] = []
            
            # Check if pattern exists
            pattern_exists = False
            for pattern in self.answer_patterns[pattern_key]:
                if pattern['answer'].lower() == answer.lower():
                    pattern['frequency'] += 1
                    pattern['last_used'] = datetime.now().isoformat()
                    pattern_exists = True
                    break
            
            if not pattern_exists:
                self.answer_patterns[pattern_key].append({
                    'answer': answer,
                    'frequency': 1,
                    'first_used': datetime.now().isoformat(),
                    'last_used': datetime.now().isoformat()
                })
        
        # Save patterns
        patterns_file = self.history_path / "answer_patterns.json"
        with open(patterns_file, 'w') as f:
            json.dump(self.answer_patterns, f, indent=2)
    
    def get_session_history(
        self,
        limit: int = 10,
        include_answers: bool = False
    ) -> List[Dict[str, Any]]:
        """Get recent session history."""
        sessions = []
        
        # Get all session files
        session_files = sorted(
            self.history_path.glob("qa_session_*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )[:limit]
        
        for session_file in session_files:
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            if not include_answers:
                data.pop('answers', None)
            
            sessions.append(data)
        
        return sessions
    
    def export_insights(self) -> Dict[str, Any]:
        """Export learned insights from Q&A history."""
        insights = {
            'total_sessions': len(list(self.history_path.glob("qa_session_*.json"))),
            'answer_patterns': {},
            'common_gaps': {},
            'improvement_areas': []
        }
        
        # Analyze answer patterns
        for pattern_key, patterns in self.answer_patterns.items():
            top_answers = sorted(
                patterns,
                key=lambda p: p['frequency'],
                reverse=True
            )[:5]
            
            insights['answer_patterns'][pattern_key] = {
                'total_unique_answers': len(patterns),
                'top_answers': [
                    {
                        'answer': p['answer'],
                        'frequency': p['frequency']
                    }
                    for p in top_answers
                ]
            }
        
        # Identify common gaps
        gap_frequency = {}
        for session_file in self.history_path.glob("qa_session_*.json"):
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            for qid, answer_data in data.get('answers', {}).items():
                q_text = answer_data['question']
                gap_type = self._classify_gap_type(q_text)
                
                if gap_type not in gap_frequency:
                    gap_frequency[gap_type] = 0
                gap_frequency[gap_type] += 1
        
        insights['common_gaps'] = gap_frequency
        
        # Suggest improvement areas
        if gap_frequency:
            top_gaps = sorted(
                gap_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            for gap_type, frequency in top_gaps:
                insights['improvement_areas'].append({
                    'area': gap_type,
                    'frequency': frequency,
                    'recommendation': self._get_improvement_recommendation(gap_type)
                })
        
        return insights
    
    def _classify_gap_type(self, question_text: str) -> str:
        """Classify gap type from question text."""
        q_lower = question_text.lower()
        
        if 'strategic' in q_lower or 'objective' in q_lower:
            return 'strategic_alignment'
        elif 'metric' in q_lower or 'measure' in q_lower:
            return 'missing_metrics'
        elif 'justification' in q_lower or 'why' in q_lower:
            return 'missing_justification'
        elif 'when' in q_lower or 'deadline' in q_lower:
            return 'missing_timeline'
        elif 'depend' in q_lower or 'block' in q_lower:
            return 'missing_dependencies'
        else:
            return 'other'
    
    def _get_improvement_recommendation(self, gap_type: str) -> str:
        """Get improvement recommendation for gap type."""
        recommendations = {
            'strategic_alignment': 
                "Consider adding strategic objectives to work item templates",
            'missing_metrics': 
                "Implement mandatory success metrics for all epics and features",
            'missing_justification': 
                "Require business justification in work item creation process",
            'missing_timeline': 
                "Add target completion dates to planning templates",
            'missing_dependencies': 
                "Use dependency mapping tools during PI planning"
        }
        
        return recommendations.get(gap_type, "Review work item creation process")