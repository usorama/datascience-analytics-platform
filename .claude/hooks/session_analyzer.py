#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
v3.0 Project Session Analyzer Hook

Enhanced session analysis with aggregation support for cross-project learning.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
import argparse
import subprocess
import platform

class SessionAnalyzer:
    """Analyze and generate insights from project sessions"""

    def __init__(self, project_dir: Path = None):
        if project_dir is None:
            # Find project root by looking for .claude/settings.json
            current_dir = Path.cwd()
            while current_dir != current_dir.parent:
                if (current_dir / ".claude" / "settings.json").exists():
                    project_dir = current_dir
                    break
                current_dir = current_dir.parent
            else:
                # Fallback to current directory
                project_dir = Path.cwd()

        self.project_dir = project_dir
        self.analytics_dir = self.project_dir / ".claude" / "analytics"
        self.cross_project_dir = Path.home() / ".claude" / "cross-project"

    def generate_insights(self) -> list:
        """Generate insights from current session"""
        insights = []

        # Load patterns
        patterns_file = self.analytics_dir / "learned_patterns.json"
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                patterns = json.load(f)

            # Most used command
            successful = patterns.get('successful_commands', {})
            if successful:
                # Sort by effectiveness score * count for v3
                sorted_cmds = sorted(
                    successful.items(),
                    key=lambda x: x[1].get('count', 0) * x[1].get('effectiveness_score', 1.0),
                    reverse=True
                )

                if sorted_cmds:
                    top_cmd = sorted_cmds[0]
                    insights.append(f"Most effective command: {top_cmd[0]} ({top_cmd[1]['count']} uses)")

            # Failed patterns
            failed = patterns.get('failed_patterns', {})
            if failed:
                insights.append(f"Found {len(failed)} failing patterns to review")

        # Load metrics
        metrics_file = self.analytics_dir / "project_metrics.json"
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)

            insights.append(f"Project health: {metrics.get('project_health', 'unknown')}")
            insights.append(f"Success rate: {metrics.get('success_rate', 0):.1f}%")

            # Performance insight
            avg_time = metrics.get('avg_response_time', 0)
            if avg_time > 1000:
                insights.append(f"Average response time: {avg_time:.0f}ms (consider optimization)")

        return insights

    def aggregate_to_global(self):
        """Aggregate project data to global learning (v3 feature)"""
        try:
            # Ensure cross-project directory exists
            self.cross_project_dir.mkdir(parents=True, exist_ok=True)

            # Load project patterns
            patterns_file = self.analytics_dir / "learned_patterns.json"
            if not patterns_file.exists():
                return

            with open(patterns_file, 'r') as f:
                project_patterns = json.load(f)

            # Load or create aggregation file
            agg_file = self.cross_project_dir / "aggregated_patterns.json"
            if agg_file.exists():
                with open(agg_file, 'r') as f:
                    global_patterns = json.load(f)
            else:
                global_patterns = {
                    "command_usage": {},
                    "failure_patterns": {},
                    "project_contributions": {},
                    "last_aggregation": None
                }

            # Get project identifier
            project_name = self.project_dir.name
            project_hash = str(hash(str(self.project_dir)))[:8]
            project_id = f"{project_name}_{project_hash}"

            # Aggregate successful commands
            for cmd, data in project_patterns.get('successful_commands', {}).items():
                if cmd not in global_patterns['command_usage']:
                    global_patterns['command_usage'][cmd] = {
                        "total_count": 0,
                        "project_count": 0,
                        "effectiveness_avg": 0
                    }

                global_patterns['command_usage'][cmd]['total_count'] += data['count']

                # Track unique projects
                if project_id not in global_patterns['project_contributions']:
                    global_patterns['project_contributions'][project_id] = {
                        "last_seen": datetime.now().isoformat(),
                        "contributions": 0
                    }

                global_patterns['project_contributions'][project_id]['contributions'] += 1

            # Update aggregation timestamp
            global_patterns['last_aggregation'] = datetime.now().isoformat()

            # Save aggregated patterns
            with open(agg_file, 'w') as f:
                json.dump(global_patterns, f, indent=2)

        except Exception as e:
            # Don't fail on aggregation errors
            print(f"Aggregation error (non-critical): {e}", file=sys.stderr)

    def save_session_insights(self, insights: list):
        """Save insights to file"""
        insights_file = self.analytics_dir / "session_insights.json"

        # Load existing insights
        if insights_file.exists():
            with open(insights_file, 'r') as f:
                all_insights = json.load(f)
        else:
            all_insights = []

        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "insights": insights
        }

        all_insights.append(entry)

        # Keep only last 20 sessions
        if len(all_insights) > 20:
            all_insights = all_insights[-20:]

        # Save back
        with open(insights_file, 'w') as f:
            json.dump(all_insights, f, indent=2)

    def announce_completion(self):
        """Announce session completion with voice"""
        try:
            project_name = self.project_dir.name
            message = f"Claude Code session complete in {project_name}. Ready for next command."

            if platform.system() == "Darwin":  # macOS
                subprocess.run(["say", "-v", "Alex", message], capture_output=True)
            elif platform.system() == "Linux":
                subprocess.run(["espeak", message], capture_output=True)
        except:
            pass

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate-insights', action='store_true',
                       help='Generate session insights')
    parser.add_argument('--aggregate', action='store_true',
                       help='Aggregate patterns across projects')
    parser.add_argument('--v3', action='store_true',
                       help='v3 compatibility mode')

    # Parse known arguments and ignore unknown ones for robustness
    try:
        args, unknown = parser.parse_known_args()
        if unknown:
            print(f"Warning: Ignoring unknown arguments: {unknown}", file=sys.stderr)
    except Exception as e:
        print(f"Argument parsing error: {e}", file=sys.stderr)
        # Create a minimal args object if parsing fails
        class Args:
            generate_insights = False
            aggregate = False
            v3 = False
        args = Args()

    # Get hook input
    hook_input = os.environ.get('CLAUDE_HOOK_INPUT', '{}')

    try:
        data = json.loads(hook_input)

        # Initialize analyzer
        analyzer = SessionAnalyzer()

        if args.generate_insights:
            # Generate insights
            insights = analyzer.generate_insights()

            # Save insights
            analyzer.save_session_insights(insights)

            # Print summary for logging
            if insights:
                print(f"Generated {len(insights)} insights", file=sys.stderr)

        if args.aggregate:
            # Aggregate to global patterns
            analyzer.aggregate_to_global()
            print("Aggregated patterns to global learning", file=sys.stderr)

        # Always announce completion (v3 feature)
        if args.v3 or args.generate_insights or args.aggregate:
            analyzer.announce_completion()

    except Exception as e:
        print(f"Session analyzer error: {e}", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
