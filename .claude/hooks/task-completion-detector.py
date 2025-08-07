#!/usr/bin/env python3.12
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Task Completion Detection Hook for Claude Code

Monitors development activity and triggers auto-commits when task completion is detected.
Integrates with BMAD validation system and project intelligence.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import re
from typing import Dict, List, Optional, Tuple

class TaskCompletionDetector:
    """Detects task completion events and triggers appropriate git actions"""
    
    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path.cwd()
        self.claude_dir = self.project_dir / ".claude"
        self.hooks_dir = self.claude_dir / "hooks"
        self.config_dir = self.claude_dir / "config"
        self.logs_dir = self.claude_dir / "logs"
        
        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration files
        self.autocommit_config = self.config_dir / "autocommit-config.json"
        self.log_file = self.logs_dir / "task_completion.log"
        self.dedup_file = self.config_dir / "completion_history.json"
        
    def log(self, level: str, message: str):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} [{level}] task-completion-detector: {message}"
        print(log_entry)
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
    
    def load_config(self) -> Dict:
        """Load auto-commit configuration"""
        if self.autocommit_config.exists():
            with open(self.autocommit_config, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "enabled": True,
            "completion_triggers": {
                "dod_validation": True,
                "evidence_validation": True,
                "story_markers": True,
                "significant_changes": True,
                "agent_completion": True
            }
        }
    
    def load_completion_history(self) -> Dict:
        """Load completion history for deduplication"""
        if self.dedup_file.exists():
            try:
                with open(self.dedup_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def save_completion_history(self, history: Dict):
        """Save completion history for deduplication"""
        try:
            with open(self.dedup_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            self.log("WARNING", f"Failed to save completion history: {e}")
    
    def is_duplicate_completion(self, completion_type: str, description: str) -> bool:
        """Check if this completion has already been processed"""
        history = self.load_completion_history()
        completion_key = f"{completion_type}:{description}"
        
        # Check if we've seen this exact completion in the last 24 hours
        if completion_key in history:
            last_processed = datetime.fromisoformat(history[completion_key])
            time_diff = datetime.now() - last_processed
            if time_diff.total_seconds() < 86400:  # 24 hours
                return True
        
        return False
    
    def record_completion(self, completion_type: str, description: str):
        """Record a completion to prevent future duplicates"""
        history = self.load_completion_history()
        completion_key = f"{completion_type}:{description}"
        history[completion_key] = datetime.now().isoformat()
        
        # Clean up old entries (older than 7 days)
        cutoff = datetime.now() - timedelta(days=7)
        history = {k: v for k, v in history.items() 
                  if datetime.fromisoformat(v) > cutoff}
        
        self.save_completion_history(history)
    
    def check_dod_validation(self) -> bool:
        """Check if DoD validation has passed recently"""
        dod_log = self.logs_dir / "quality" / "dod_validation.log"
        if not dod_log.exists():
            return False
        
        try:
            # Check last 20 lines for recent validation
            with open(dod_log, 'r') as f:
                lines = f.readlines()[-20:]
            
            for line in reversed(lines):
                if "DoD validation PASSED" in line:
                    # Check if it's recent (within last hour)
                    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        log_time = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                        time_diff = datetime.now() - log_time
                        if time_diff.total_seconds() < 3600:  # Within 1 hour
                            return True
        except Exception as e:
            self.log("WARNING", f"Error checking DoD validation: {e}")
        
        return False
    
    def check_evidence_validation(self) -> bool:
        """Check if evidence validation has passed recently"""
        evidence_log = self.logs_dir / "quality" / "evidence_validation.log"
        if not evidence_log.exists():
            return False
        
        try:
            with open(evidence_log, 'r') as f:
                lines = f.readlines()[-20:]
            
            for line in reversed(lines):
                if "Evidence validation PASSED" in line:
                    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        log_time = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                        time_diff = datetime.now() - log_time
                        if time_diff.total_seconds() < 3600:
                            return True
        except Exception as e:
            self.log("WARNING", f"Error checking evidence validation: {e}")
        
        return False
    
    def check_story_markers(self) -> Optional[str]:
        """Check for story completion markers in recently modified files"""
        try:
            # Find recently modified markdown files
            result = subprocess.run([
                'find', str(self.project_dir), '-name', '*.md', '-mtime', '-1'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return None
            
            recent_files = result.stdout.strip().split('\n')
            completion_patterns = [
                r'Story.*Complete[d]?',
                r'✅.*Complete[d]?',
                r'COMPLETED',
                r'Implementation.*Complete[d]?',
                r'Epic.*Complete[d]?',
                r'Task.*Complete[d]?'
            ]
            
            for file_path in recent_files:
                if not file_path:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in completion_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            return f"Found completion marker '{matches[0]}' in {file_path}"
                except Exception:
                    continue
        
        except Exception as e:
            self.log("WARNING", f"Error checking story markers: {e}")
        
        return None
    
    def check_significant_changes(self) -> bool:
        """Check if there are significant changes in the working directory"""
        try:
            result = subprocess.run([
                'git', 'status', '--porcelain'
            ], capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode != 0:
                return False
            
            changed_files = [line for line in result.stdout.strip().split('\n') if line]
            return len(changed_files) >= 3  # Significant if 3+ files changed
        
        except Exception as e:
            self.log("WARNING", f"Error checking git status: {e}")
            return False
    
    def check_agent_completion(self) -> Optional[str]:
        """Check for recent agent completion indicators"""
        try:
            # Check recent git commits for agent signatures  
            result = subprocess.run([
                'git', 'log', '--oneline', '-10', '--grep=🤖\\|Agent\\|Claude'
            ], capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode == 0 and result.stdout.strip():
                recent_commits = result.stdout.strip().split('\n')
                if recent_commits and recent_commits[0]:
                    return f"Recent agent activity: {recent_commits[0]}"
        except Exception as e:
            self.log("WARNING", f"Error checking agent completion: {e}")
        
        return None
    
    def detect_completion_events(self) -> Dict[str, any]:
        """Detect all completion events"""
        config = self.load_config()
        triggers = config.get("completion_triggers", {})
        events = {}
        
        if triggers.get("dod_validation", True):
            events["dod_validated"] = self.check_dod_validation()
        
        if triggers.get("evidence_validation", True):
            events["evidence_validated"] = self.check_evidence_validation()
        
        if triggers.get("story_markers", True):
            story_marker = self.check_story_markers()
            events["story_marker"] = story_marker
        
        if triggers.get("significant_changes", True):
            events["significant_changes"] = self.check_significant_changes()
        
        if triggers.get("agent_completion", True):
            agent_completion = self.check_agent_completion()
            events["agent_completion"] = agent_completion
        
        return events
    
    def determine_completion_type(self, events: Dict[str, any]) -> Optional[Tuple[str, str]]:
        """Determine the type of completion and generate description"""
        
        # Priority order for completion types
        if events.get("dod_validated") and events.get("evidence_validated"):
            if events.get("story_marker"):
                return ("story_completion", "Story implementation with full validation")
            else:
                return ("task_completion", "Task implementation with validation")
        
        elif events.get("story_marker"):
            return ("story_completion", events["story_marker"])
        
        elif events.get("agent_completion"):
            return ("agent_completion", events["agent_completion"])
        
        elif events.get("significant_changes"):
            return ("development_checkpoint", "Significant development progress")
        
        return None
    
    def trigger_autocommit(self, completion_type: str, description: str) -> bool:
        """Trigger the auto-commit script"""
        autocommit_script = self.hooks_dir / "simple-autocommit.sh"
        
        if not autocommit_script.exists():
            self.log("ERROR", "Auto-commit script not found")
            return False
        
        try:
            result = subprocess.run([
                'bash', str(autocommit_script), completion_type, description
            ], capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode == 0:
                self.log("SUCCESS", f"Auto-commit triggered: {completion_type} - {description}")
                if result.stdout:
                    self.log("INFO", f"Auto-commit output: {result.stdout.strip()}")
                return True
            else:
                self.log("ERROR", f"Auto-commit failed: {result.stderr}")
                return False
        
        except Exception as e:
            self.log("ERROR", f"Failed to trigger auto-commit: {e}")
            return False
    
    def run_detection(self) -> bool:
        """Main detection and execution logic"""
        config = self.load_config()
        
        if not config.get("enabled", True):
            self.log("INFO", "Task completion detection disabled")
            return False
        
        self.log("INFO", "Starting task completion detection")
        
        # Detect completion events
        events = self.detect_completion_events()
        
        # Log detected events
        active_events = {k: v for k, v in events.items() if v}
        if active_events:
            self.log("INFO", f"Detected completion events: {list(active_events.keys())}")
        else:
            self.log("INFO", "No completion events detected")
            return False
        
        # Determine completion type
        completion_info = self.determine_completion_type(events)
        if not completion_info:
            self.log("INFO", "No significant completion detected")
            return False
        
        completion_type, description = completion_info
        self.log("INFO", f"Completion detected: {completion_type} - {description}")
        
        # Check for duplicates
        if self.is_duplicate_completion(completion_type, description):
            self.log("INFO", f"Duplicate completion detected, skipping: {completion_type} - {description}")
            return False  # Return False for duplicates - no action needed
        
        # Trigger auto-commit
        success = self.trigger_autocommit(completion_type, description)
        
        if success:
            # Record the completion to prevent future duplicates
            self.record_completion(completion_type, description)
        
        return success

def main():
    parser = argparse.ArgumentParser(description='Task Completion Detection for Claude Code')
    parser.add_argument('--project-dir', type=Path, help='Project directory path')
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    parser.add_argument('--test', action='store_true', help='Test detection without committing')
    parser.add_argument('--enable', action='store_true', help='Enable detection')
    parser.add_argument('--disable', action='store_true', help='Disable detection')
    
    args = parser.parse_args()
    
    detector = TaskCompletionDetector(args.project_dir)
    
    if args.config:
        config = detector.load_config()
        print(json.dumps(config, indent=2))
        return
    
    if args.enable:
        config = detector.load_config()
        config['enabled'] = True
        with open(detector.autocommit_config, 'w') as f:
            json.dump(config, f, indent=2)
        print("Task completion detection enabled")
        return
    
    if args.disable:
        config = detector.load_config()
        config['enabled'] = False
        with open(detector.autocommit_config, 'w') as f:
            json.dump(config, f, indent=2)
        print("Task completion detection disabled")
        return
    
    if args.test:
        events = detector.detect_completion_events()
        completion_info = detector.determine_completion_type(events)
        
        print("Detected events:")
        for event, value in events.items():
            if value:
                print(f"  {event}: {value}")
        
        if completion_info:
            completion_type, description = completion_info
            print(f"\nCompletion type: {completion_type}")
            print(f"Description: {description}")
        else:
            print("\nNo completion detected")
        return
    
    # Run detection with comprehensive error handling
    try:
        success = detector.run_detection()
        detector.log("DEBUG", f"run_detection() returned: {success}")
        
        # Always exit cleanly with code 0 for Claude Code compatibility
        # This prevents the "failed with non-blocking status code 1" error
        if success:
            detector.log("DEBUG", "Completion detected and processed - exiting with code 0")
        else:
            detector.log("DEBUG", "No action needed - exiting with code 0")
        
        sys.exit(0)  # Always use exit code 0 for proper Claude Code integration
            
    except KeyboardInterrupt:
        detector.log("INFO", "Hook interrupted by user")
        sys.exit(0)
    except SystemExit as e:
        # Let system exits pass through
        raise
    except Exception as e:
        detector.log("ERROR", f"Unhandled exception in main: {e}")
        detector.log("ERROR", f"Exception type: {type(e).__name__}")
        import traceback
        detector.log("ERROR", f"Traceback: {traceback.format_exc()}")
        # Exit with 0 even on errors to prevent blocking
        # Log the error for debugging but don't disrupt workflow
        sys.exit(0)

if __name__ == "__main__":
    main()