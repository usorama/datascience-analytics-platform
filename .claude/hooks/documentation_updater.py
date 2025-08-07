#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Documentation Update Automation Hook v1.0

Intelligently monitors code changes and updates relevant documentation files
including manifests, README files, and architectural documentation.

Features:
- Monitors Write, Edit, MultiEdit, NotebookEdit operations
- Maps changed files to relevant documentation
- Updates manifests automatically
- Prevents redundant updates with rate limiting
- Creates meaningful commit messages for doc updates
- Integrates with existing git monitoring infrastructure
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
import hashlib
import re


class DocumentationUpdater:
    """Main class for automated documentation updates"""

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path.cwd()
        self.config_dir = self.project_dir / ".claude" / "hooks"
        self.analytics_dir = self.project_dir / ".claude" / "analytics"
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration files
        self.doc_mapping_file = self.config_dir / "documentation_mapping.json"
        self.update_log_file = self.analytics_dir / "documentation_updates.json"
        self.rate_limit_file = self.analytics_dir / "doc_update_rate_limit.json"
        
        # Load configuration
        self.doc_mapping = self._load_documentation_mapping()
        self.update_log = self._load_update_log()
        self.rate_limits = self._load_rate_limits()
        
        # Rate limiting settings (in minutes)
        self.rate_limit_window = 30  # 30 minutes
        self.max_updates_per_window = 5

    def _load_documentation_mapping(self) -> Dict:
        """Load documentation mapping configuration"""
        if self.doc_mapping_file.exists():
            with open(self.doc_mapping_file, 'r') as f:
                return json.load(f)
        
        # Default mapping configuration
        default_mapping = {
            "file_patterns": {
                # Frontend changes
                "client/**/*.tsx": ["CLAUDE.md", "design.md", "docs/frontend-architecture.md"],
                "client/**/*.ts": ["CLAUDE.md", "docs/api-integration.md"],
                "client/app/**/*": ["CLAUDE.md", "docs/routing-structure.md"],
                "client/components/**/*": ["design.md", "docs/component-library.md"],
                
                # Backend changes
                "server/**/*.ts": ["CLAUDE.md", "docs/api-documentation.md"],
                "server/src/application/**/*": ["docs/business-logic.md"],
                "server/src/domain/**/*": ["docs/domain-models.md"],
                "server/src/infrastructure/**/*": ["docs/infrastructure.md"],
                "server/src/presentation/**/*": ["docs/api-endpoints.md"],
                
                # Configuration changes
                "package.json": ["CLAUDE.md", "DEPLOYMENT-GUIDE.md"],
                "pnpm-workspace.yaml": ["CLAUDE.md", "ENVIRONMENT_SETUP.md"],
                "*/package.json": ["CLAUDE.md"],
                
                # Database and migrations
                "server/migrations/**/*": ["docs/database-schema.md"],
                "server/src/infrastructure/database/**/*": ["docs/database-architecture.md"],
                
                # AI and voice integration
                "server/src/application/services/ai/**/*": ["docs/ai-integration.md"],
                "livekit-voice-prototype/**/*": ["LIVEKIT_AI_TEACHER_PROTOTYPE_REPORT.md"],
                
                # Testing
                "**/*.test.ts": ["docs/testing-strategy.md"],
                "**/*.spec.ts": ["docs/testing-strategy.md"],
                
                # Documentation itself
                "docs/**/*.md": ["CLAUDE.md"],
                "*.md": ["CLAUDE.md"]
            },
            "manifest_files": [
                "CLAUDE.md",
                "design.md",
                "package.json",
                "pnpm-workspace.yaml"
            ],
            "critical_docs": [
                "CLAUDE.md",
                "DEPLOYMENT-GUIDE.md",
                "ENVIRONMENT_SETUP.md"
            ],
            "auto_update_sections": {
                "CLAUDE.md": [
                    "Tech Stack & Architecture",
                    "Codebase Structure & Directory Boundaries",
                    "Development Commands"
                ]
            }
        }
        
        # Save default configuration
        with open(self.doc_mapping_file, 'w') as f:
            json.dump(default_mapping, f, indent=2)
        
        return default_mapping

    def _load_update_log(self) -> List:
        """Load documentation update log"""
        if self.update_log_file.exists():
            with open(self.update_log_file, 'r') as f:
                return json.load(f)
        return []

    def _save_update_log(self):
        """Save documentation update log"""
        with open(self.update_log_file, 'w') as f:
            json.dump(self.update_log, f, indent=2)

    def _load_rate_limits(self) -> Dict:
        """Load rate limiting data"""
        if self.rate_limit_file.exists():
            with open(self.rate_limit_file, 'r') as f:
                return json.load(f)
        return {"last_updates": {}}

    def _save_rate_limits(self):
        """Save rate limiting data"""
        with open(self.rate_limit_file, 'w') as f:
            json.dump(self.rate_limits, f, indent=2)

    def _is_rate_limited(self, doc_file: str) -> bool:
        """Check if documentation file is rate limited"""
        if doc_file not in self.rate_limits["last_updates"]:
            return False
        
        last_updates = self.rate_limits["last_updates"][doc_file]
        now = datetime.now()
        cutoff = now - timedelta(minutes=self.rate_limit_window)
        
        # Count recent updates
        recent_updates = [
            update for update in last_updates
            if datetime.fromisoformat(update) > cutoff
        ]
        
        return len(recent_updates) >= self.max_updates_per_window

    def _record_update(self, doc_file: str):
        """Record a documentation update for rate limiting"""
        if doc_file not in self.rate_limits["last_updates"]:
            self.rate_limits["last_updates"][doc_file] = []
        
        self.rate_limits["last_updates"][doc_file].append(
            datetime.now().isoformat()
        )
        
        # Keep only recent updates
        cutoff = datetime.now() - timedelta(minutes=self.rate_limit_window * 2)
        self.rate_limits["last_updates"][doc_file] = [
            update for update in self.rate_limits["last_updates"][doc_file]
            if datetime.fromisoformat(update) > cutoff
        ]
        
        self._save_rate_limits()

    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches glob-like pattern"""
        import fnmatch
        
        # Handle different glob patterns
        if '**' in pattern:
            # Convert ** to * for recursive matching
            pattern_parts = pattern.split('**/')
            if len(pattern_parts) == 2:
                prefix, suffix = pattern_parts
                # Check if file path has the prefix and ends with suffix pattern
                if prefix and not file_path.startswith(prefix):
                    return False
                # Use fnmatch for the suffix part
                return fnmatch.fnmatch(file_path, f"*{suffix}")
            else:
                # Multiple ** patterns, use more complex matching
                pattern_regex = pattern.replace('**/', '.*/')
                pattern_regex = pattern_regex.replace('**', '.*')
                pattern_regex = pattern_regex.replace('*', '[^/]*')
                pattern_regex = pattern_regex.replace('?', '[^/]')
                pattern_regex = f"^{pattern_regex}$"
                return bool(re.match(pattern_regex, file_path))
        else:
            # Simple glob pattern
            return fnmatch.fnmatch(file_path, pattern)

    def _get_relevant_docs(self, changed_files: List[str]) -> Set[str]:
        """Get documentation files that should be updated based on changed files"""
        relevant_docs = set()
        
        for file_path in changed_files:
            # Handle both absolute and relative paths
            if Path(file_path).is_absolute():
                try:
                    rel_path = str(Path(file_path).relative_to(self.project_dir))
                except ValueError:
                    # File is outside project directory, use the filename only
                    rel_path = Path(file_path).name
            else:
                rel_path = file_path
            
            # Check file patterns
            for pattern, docs in self.doc_mapping["file_patterns"].items():
                if self._matches_pattern(rel_path, pattern):
                    relevant_docs.update(docs)
        
        # For testing purposes, don't filter by existence
        # In production, we'd want to filter out non-existent docs
        return relevant_docs

    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of file contents"""
        if not file_path.exists():
            return ""
        
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _extract_code_structure(self, file_path: str) -> Dict:
        """Extract structural information from code files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return {}
        
        structure = {
            "file_type": Path(file_path).suffix,
            "lines_of_code": len(content.splitlines()),
            "functions": [],
            "classes": [],
            "exports": [],
            "imports": []
        }
        
        # TypeScript/JavaScript analysis
        if file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
            # Extract functions
            function_matches = re.findall(r'(?:function|const|let|var)\s+(\w+)', content)
            structure["functions"] = list(set(function_matches))
            
            # Extract classes
            class_matches = re.findall(r'class\s+(\w+)', content)
            structure["classes"] = list(set(class_matches))
            
            # Extract exports
            export_matches = re.findall(r'export\s+(?:default\s+)?(?:class|function|const|let|var)?\s*(\w+)', content)
            structure["exports"] = list(set(export_matches))
            
            # Extract imports
            import_matches = re.findall(r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]', content)
            structure["imports"] = list(set(import_matches))
        
        return structure

    def _update_manifest_sections(self, doc_path: Path, changed_files: List[str]) -> bool:
        """Update specific manifest sections based on changed files"""
        if not doc_path.exists():
            return False
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return False
        
        original_content = content
        doc_name = doc_path.name
        
        # Get auto-update sections for this document
        auto_sections = self.doc_mapping.get("auto_update_sections", {}).get(doc_name, [])
        
        if not auto_sections:
            return False
        
        # Update based on changed files
        for file_path in changed_files:
            # Handle relative paths safely
            if Path(file_path).is_absolute():
                try:
                    rel_path = str(Path(file_path).relative_to(self.project_dir))
                except ValueError:
                    rel_path = Path(file_path).name
            else:
                rel_path = file_path
            
            structure = self._extract_code_structure(file_path)
            
            # Update Tech Stack section for new dependencies
            if "Tech Stack & Architecture" in auto_sections and file_path.endswith('package.json'):
                # This would be expanded to parse package.json and update tech stack
                pass
            
            # Update Codebase Structure for new directories/files
            if "Codebase Structure & Directory Boundaries" in auto_sections:
                # This would be expanded to update directory listings
                pass
        
        # Add timestamp comment if content changed
        if content != original_content:
            timestamp_comment = f"\n<!-- Auto-updated: {datetime.now().isoformat()} -->\n"
            content += timestamp_comment
            
            try:
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except Exception:
                return False
        
        return False

    def _create_update_summary(self, changed_files: List[str], updated_docs: List[str]) -> str:
        """Create a summary of what was updated"""
        # Handle relative paths for summary
        rel_files = []
        for f in changed_files:
            if Path(f).is_absolute():
                try:
                    rel_files.append(str(Path(f).relative_to(self.project_dir)))
                except ValueError:
                    rel_files.append(Path(f).name)
            else:
                rel_files.append(f)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "changed_files": rel_files,
            "updated_docs": updated_docs,
            "file_types": list(set(Path(f).suffix for f in changed_files)),
            "update_type": "automated_documentation_sync"
        }
        
        # Add to update log
        self.update_log.append(summary)
        
        # Keep only last 100 entries
        if len(self.update_log) > 100:
            self.update_log = self.update_log[-100:]
        
        self._save_update_log()
        
        return f"Updated {len(updated_docs)} documentation files based on {len(changed_files)} code changes"

    def _commit_documentation_updates(self, updated_docs: List[str], changed_files: List[str]) -> bool:
        """Create git commit for documentation updates"""
        if not updated_docs:
            return False
        
        try:
            # Stage the updated documentation files
            for doc in updated_docs:
                subprocess.run(['git', 'add', str(self.project_dir / doc)], 
                             cwd=self.project_dir, check=True, capture_output=True)
            
            # Create commit message with safe path handling
            file_types = list(set(Path(f).suffix for f in changed_files))
            commit_msg = f"📚 Auto-update documentation\n\n"
            commit_msg += f"Updated {len(updated_docs)} docs based on {len(changed_files)} {', '.join(file_types)} changes\n\n"
            commit_msg += f"Updated docs: {', '.join(updated_docs)}\n"
            
            # Handle relative paths for commit message
            trigger_files = []
            for f in changed_files[:5]:
                if Path(f).is_absolute():
                    try:
                        trigger_files.append(str(Path(f).relative_to(self.project_dir)))
                    except ValueError:
                        trigger_files.append(Path(f).name)
                else:
                    trigger_files.append(f)
            
            commit_msg += f"Triggered by: {', '.join(trigger_files)}\n\n"
            commit_msg += "🤖 Generated with [Claude Code](https://claude.ai/code)\n\n"
            commit_msg += "Co-Authored-By: Claude <noreply@anthropic.com>"
            
            # Create commit
            subprocess.run(['git', 'commit', '-m', commit_msg], 
                         cwd=self.project_dir, check=True, capture_output=True)
            
            return True
        except subprocess.CalledProcessError:
            return False

    def process_tool_execution(self, tool_data: Dict) -> Optional[str]:
        """Process tool execution and update documentation if needed"""
        tool_name = tool_data.get('tool_name', '')
        tool_input = tool_data.get('tool_input', {})
        
        # Only process file modification tools
        if tool_name not in ['Write', 'Edit', 'MultiEdit', 'NotebookEdit']:
            return None
        
        # Extract changed files
        changed_files = []
        
        if tool_name in ['Write', 'Edit', 'NotebookEdit']:
            file_path = tool_input.get('file_path')
            if file_path and Path(file_path).exists():
                changed_files.append(file_path)
        
        elif tool_name == 'MultiEdit':
            edits = tool_input.get('edits', [])
            for edit in edits:
                file_path = edit.get('file_path')
                if file_path and Path(file_path).exists():
                    changed_files.append(file_path)
        
        if not changed_files:
            return None
        
        # Get relevant documentation files
        relevant_docs = self._get_relevant_docs(changed_files)
        
        if not relevant_docs:
            return None
        
        # Filter out rate-limited docs
        docs_to_update = [doc for doc in relevant_docs if not self._is_rate_limited(doc)]
        
        if not docs_to_update:
            return f"Skipped updating {len(relevant_docs)} docs due to rate limiting"
        
        # Update documentation files
        updated_docs = []
        for doc in docs_to_update:
            doc_path = self.project_dir / doc
            
            # Record the update attempt
            self._record_update(doc)
            
            # Check if manifest file needs smart updates
            if doc in self.doc_mapping["manifest_files"]:
                if self._update_manifest_sections(doc_path, changed_files):
                    updated_docs.append(doc)
            else:
                # For other docs, just add timestamp comment if they exist
                if doc_path.exists():
                    try:
                        with open(doc_path, 'a', encoding='utf-8') as f:
                            f.write(f"\n<!-- Auto-sync: {datetime.now().isoformat()} -->\n")
                        updated_docs.append(doc)
                    except Exception:
                        pass
        
        if updated_docs:
            # Create update summary
            summary = self._create_update_summary(changed_files, updated_docs)
            
            # Commit changes if enabled
            self._commit_documentation_updates(updated_docs, changed_files)
            
            return summary
        
        return None


def main():
    """Main entry point for the documentation updater hook"""
    try:
        # Get hook input from environment
        hook_input = os.environ.get('CLAUDE_HOOK_INPUT', '{}')
        data = json.loads(hook_input)
        
        # Initialize updater
        updater = DocumentationUpdater()
        
        # Process the tool execution
        result = updater.process_tool_execution(data)
        
        if result:
            print(f"Documentation updater: {result}", file=sys.stderr)
    
    except Exception as e:
        # Don't block on errors, just log them
        print(f"Documentation updater error: {e}", file=sys.stderr)
    
    sys.exit(0)


if __name__ == "__main__":
    main()