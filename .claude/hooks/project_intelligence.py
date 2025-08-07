#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
v3.0 Project Intelligence Hook

Enhanced learning and metrics tracking with v3 features including
cross-project integration and advanced analytics.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
import argparse
from collections import defaultdict

class ProjectIntelligence:
    """Main intelligence engine for project-level learning"""

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path.cwd()
        self.analytics_dir = self.project_dir / ".claude" / "analytics"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.patterns_file = self.analytics_dir / "learned_patterns.json"
        self.metrics_file = self.analytics_dir / "project_metrics.json"
        self.insights_file = self.analytics_dir / "session_insights.json"

    def load_patterns(self) -> dict:
        """Load existing learned patterns"""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {
            "successful_commands": {},
            "failed_patterns": {},
            "performance_insights": {},
            "last_learning_update": None
        }

    def save_patterns(self, patterns: dict):
        """Save learned patterns"""
        patterns['last_learning_update'] = datetime.now().isoformat()
        with open(self.patterns_file, 'w') as f:
            json.dump(patterns, f, indent=2)

    def load_metrics(self) -> dict:
        """Load project metrics"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {
            "total_interactions": 0,
            "success_rate": 100.0,
            "avg_response_time": 0,
            "tool_usage": {},
            "project_health": "new",
            "total_successes": 0,
            "performance_trends": [],
            "last_updated": None
        }

    def save_metrics(self, metrics: dict):
        """Save project metrics"""
        metrics['last_updated'] = datetime.now().isoformat()
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)

    def learn_from_execution(self, data: dict, use_v3: bool = False):
        """Learn from command execution"""
        patterns = self.load_patterns()

        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})
        result = data.get('result', {})

        if tool_name == "Bash":
            command = tool_input.get('command', '')
            exit_code = result.get('exit_code', 0)
            duration = result.get('duration_ms', 0)

            # Extract command pattern
            cmd_parts = command.split()
            if cmd_parts:
                base_cmd = cmd_parts[0]

                # Track successful commands
                if exit_code == 0:
                    if base_cmd not in patterns['successful_commands']:
                        patterns['successful_commands'][base_cmd] = {
                            "count": 0,
                            "avg_duration": 0,
                            "last_used": None,
                            "effectiveness_score": 1.0
                        }

                    cmd_data = patterns['successful_commands'][base_cmd]
                    cmd_data['count'] += 1
                    cmd_data['last_used'] = datetime.now().isoformat()

                    # Update average duration
                    total_duration = cmd_data['avg_duration'] * (cmd_data['count'] - 1) + duration
                    cmd_data['avg_duration'] = total_duration / cmd_data['count']

                    # v3 feature: effectiveness scoring
                    if use_v3:
                        # Increase effectiveness for frequently successful commands
                        cmd_data['effectiveness_score'] = min(
                            cmd_data['effectiveness_score'] + 0.1,
                            2.0
                        )
                else:
                    # Track failed patterns
                    if command not in patterns['failed_patterns']:
                        patterns['failed_patterns'][command] = {
                            "count": 0,
                            "exit_codes": [],
                            "first_seen": datetime.now().isoformat(),
                            "last_seen": None
                        }

                    fail_data = patterns['failed_patterns'][command]
                    fail_data['count'] += 1
                    fail_data['last_seen'] = datetime.now().isoformat()
                    fail_data['exit_codes'].append(exit_code)

            # Track performance insights
            if duration > 5000:  # Commands taking more than 5 seconds
                if tool_name not in patterns['performance_insights']:
                    patterns['performance_insights'][tool_name] = {
                        "slow_commands": [],
                        "optimization_opportunities": []
                    }

                patterns['performance_insights'][tool_name]['slow_commands'].append({
                    "command": command[:100],  # Truncate long commands
                    "duration": duration,
                    "timestamp": datetime.now().isoformat()
                })

                # Keep only last 20 slow commands
                if len(patterns['performance_insights'][tool_name]['slow_commands']) > 20:
                    patterns['performance_insights'][tool_name]['slow_commands'] = \
                        patterns['performance_insights'][tool_name]['slow_commands'][-20:]

        # v3 feature: Learn from other tools too
        elif use_v3 and tool_name in ["Read", "Write", "Edit", "MultiEdit"]:
            file_path = tool_input.get('file_path', '')
            if file_path:
                extension = Path(file_path).suffix

                if 'file_operations' not in patterns:
                    patterns['file_operations'] = {}

                if extension not in patterns['file_operations']:
                    patterns['file_operations'][extension] = {
                        "count": 0,
                        "tools": defaultdict(int)
                    }

                patterns['file_operations'][extension]['count'] += 1
                patterns['file_operations'][extension]['tools'][tool_name] += 1

        self.save_patterns(patterns)

    def update_metrics(self, data: dict, use_v3: bool = False):
        """Update project metrics"""
        metrics = self.load_metrics()

        # Basic metrics update
        metrics['total_interactions'] += 1

        tool_name = data.get('tool_name', 'unknown')
        if tool_name not in metrics['tool_usage']:
            metrics['tool_usage'][tool_name] = 0
        metrics['tool_usage'][tool_name] += 1

        # Success tracking
        result = data.get('result', {})
        if tool_name == "Bash":
            is_success = result.get('exit_code', 0) == 0
        else:
            is_success = True  # Non-bash tools are considered successful

        if is_success:
            metrics['total_successes'] += 1

        # Update success rate
        metrics['success_rate'] = (metrics['total_successes'] /
                                 metrics['total_interactions'] * 100)

        # Update response time
        duration = result.get('duration_ms', 0)
        if duration > 0:
            current_avg = metrics['avg_response_time']
            total = metrics['total_interactions']
            metrics['avg_response_time'] = ((current_avg * (total - 1)) + duration) / total

        # Performance trends (v3 feature)
        if use_v3:
            trend_entry = {
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "duration": duration,
                "success": is_success
            }

            if 'performance_trends' not in metrics:
                metrics['performance_trends'] = []

            metrics['performance_trends'].append(trend_entry)

            # Keep only last 100 trends
            if len(metrics['performance_trends']) > 100:
                metrics['performance_trends'] = metrics['performance_trends'][-100:]

        # Update project health
        if metrics['success_rate'] >= 95:
            metrics['project_health'] = 'excellent'
        elif metrics['success_rate'] >= 90:
            metrics['project_health'] = 'good'
        elif metrics['success_rate'] >= 80:
            metrics['project_health'] = 'fair'
        else:
            metrics['project_health'] = 'needs_attention'

        self.save_metrics(metrics)

    def generate_ai_insights(self) -> list:
        """Generate AI-powered insights (v3 feature)"""
        insights = []

        patterns = self.load_patterns()
        metrics = self.load_metrics()

        # Insight: Most used commands
        if patterns['successful_commands']:
            top_commands = sorted(
                patterns['successful_commands'].items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:3]

            for cmd, data in top_commands:
                if data['count'] > 5:
                    insights.append(
                        f"{cmd} is frequently used ({data['count']} times) - consider optimization"
                    )

        # Insight: Slow commands
        if patterns.get('performance_insights'):
            for tool, perf_data in patterns['performance_insights'].items():
                slow_cmds = perf_data.get('slow_commands', [])
                if len(slow_cmds) > 3:
                    insights.append(
                        f"{tool} has {len(slow_cmds)} slow operations - review for optimization"
                    )

        # Insight: Project health
        if metrics['project_health'] == 'needs_attention':
            insights.append(
                f"Project health needs attention - success rate is {metrics['success_rate']:.1f}%"
            )

        return insights

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--learn', action='store_true', help='Learn from execution')
    parser.add_argument('--metrics', action='store_true', help='Update metrics')
    parser.add_argument('--v3', action='store_true', help='Use v3 enhanced features')

    # Parse known arguments and ignore unknown ones for robustness
    try:
        args, unknown = parser.parse_known_args()
        if unknown:
            print(f"Warning: Ignoring unknown arguments: {unknown}", file=sys.stderr)
    except Exception as e:
        print(f"Argument parsing error: {e}", file=sys.stderr)
        # Create a minimal args object if parsing fails
        class Args:
            learn = False
            metrics = False
            v3 = False
        args = Args()

    # Get hook input
    hook_input = os.environ.get('CLAUDE_HOOK_INPUT', '{}')

    try:
        data = json.loads(hook_input)

        # Initialize intelligence engine
        intelligence = ProjectIntelligence()

        if args.learn:
            intelligence.learn_from_execution(data, args.v3)

        if args.metrics:
            intelligence.update_metrics(data, args.v3)

            # Generate AI insights if v3
            if args.v3:
                insights = intelligence.generate_ai_insights()
                if insights:
                    # Save insights
                    insights_data = []
                    if intelligence.insights_file.exists():
                        with open(intelligence.insights_file, 'r') as f:
                            insights_data = json.load(f)

                    # Find or create today's entry
                    today = datetime.now().date().isoformat()
                    today_entry = None
                    for entry in insights_data:
                        if entry.get('timestamp', '').startswith(today):
                            today_entry = entry
                            break

                    if not today_entry:
                        today_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "insights": [],
                            "ai_insights": []
                        }
                        insights_data.append(today_entry)

                    today_entry['ai_insights'] = insights

                    with open(intelligence.insights_file, 'w') as f:
                        json.dump(insights_data, f, indent=2)

    except Exception as e:
        # Don't block on errors
        print(f"Project intelligence error: {e}", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
