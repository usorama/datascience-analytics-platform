#!/usr/bin/env python3
"""
Project-level risk analyzer for Claude Code Automation v3.0
Analyzes tool usage for potential risks and learning opportunities
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "json",
# ]
# ///

import json
import sys
import os
import re
import argparse
import subprocess
import platform
from datetime import datetime

def voice_alert(message: str):
    """Provide voice alert on macOS"""
    try:
        if platform.system() == "Darwin":
            subprocess.run(["say", "-v", "Alex", message],
                         capture_output=True, timeout=5)
    except:
        pass  # Fail silently

def check_critical_patterns(command: str) -> tuple[bool, str]:
    """Check for critical dangerous patterns that must be blocked"""
    critical_patterns = [
        (r'rm\s+-rf\s+/', 'Attempting to delete root directory'),
        (r'rm\s+-rf\s+/\*', 'Attempting to delete all root files'),
        (r':\(\)\s*\{\s*:\|\:&\s*\}\s*\;\s*:', 'Fork bomb detected'),
        (r'sudo\s+rm\s+-rf\s+/', 'Dangerous root deletion with sudo'),
        (r'format\s+[cC]:', 'Attempting to format C: drive'),
        (r'sudo\s+dd\s+if=/dev/zero\s+of=/dev/', 'Dangerous disk overwrite'),
        (r'curl\s+[^|]*\|\s*bash', 'Piped remote execution'),
        (r'wget\s+[^|]*\|\s*sh', 'Piped remote execution'),
    ]

    for pattern, reason in critical_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True, reason

    return False, ""

def analyze_bash_command(command: str) -> dict:
    """Analyze a bash command for risks"""
    is_critical, reason = check_critical_patterns(command)

    if is_critical:
        voice_alert("Dangerous command blocked by Claude Code Automation")
        return {
            "decision": "BLOCK",
            "risk_level": 1.0,
            "reason": reason,
            "recommendation": "Command blocked for safety"
        }

    # Check for risky patterns
    risky_patterns = [
        (r'sudo\s+', 'Administrative privileges requested', 0.6),
        (r'rm\s+-rf', 'Recursive force deletion', 0.7),
        (r'chmod\s+777', 'World-writable permissions', 0.5),
        (r'git\s+push\s+--force', 'Forced git push', 0.4),
        (r'npm\s+install\s+-g', 'Global package installation', 0.3),
        (r'pip\s+install', 'Package installation', 0.2),
        (r'curl\s+', 'Network request', 0.1),
        (r'wget\s+', 'Network download', 0.1),
    ]

    risk_score = 0.0
    found_patterns = []

    for pattern, description, score in risky_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            risk_score = max(risk_score, score)
            found_patterns.append(description)

    if risk_score >= 0.6:
        return {
            "decision": "ANALYZE",
            "risk_level": risk_score,
            "reason": f"High-risk patterns detected: {', '.join(found_patterns)}",
            "recommendation": "Review command carefully before execution"
        }
    elif risk_score >= 0.3:
        return {
            "decision": "MONITOR",
            "risk_level": risk_score,
            "reason": f"Medium-risk patterns detected: {', '.join(found_patterns)}",
            "recommendation": "Standard monitoring applies"
        }

    return {
        "decision": "SAFE",
        "risk_level": risk_score,
        "reason": "No significant risk patterns detected",
        "recommendation": "Proceed normally"
    }

def analyze_tool_use(tool_name: str, tool_input: dict, use_v3: bool = False) -> dict:
    """Analyze any tool use for risks and learning opportunities"""

    # Handle Bash commands specially
    if tool_name == "Bash":
        command = tool_input.get('command', '')
        return analyze_bash_command(command)

    # For other tools, do basic risk assessment
    risk_score = 0.0

    # Check for potentially risky tools
    risky_tools = {
        'Write': 0.2,
        'Edit': 0.1,
        'MultiEdit': 0.3,
        'Task': 0.1
    }

    risk_score = risky_tools.get(tool_name, 0.0)

    # Check tool input for risky patterns
    input_str = json.dumps(tool_input).lower()
    if any(dangerous in input_str for dangerous in ['delete', 'remove', 'destroy', 'format']):
        risk_score += 0.2

    return {
        "decision": "SAFE" if risk_score < 0.3 else "MONITOR",
        "risk_level": risk_score,
        "reason": f"Tool {tool_name} analysis complete",
        "recommendation": "Normal operation"
    }

def log_analysis(tool_name: str, tool_input: dict, result: dict, use_v3: bool):
    """Log the risk analysis"""
    log_dir = ".claude/logs"
    os.makedirs(log_dir, exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "risk_analysis",
        "tool_name": tool_name,
        "tool_input_size": len(json.dumps(tool_input)),
        "decision": result["decision"],
        "risk_level": result["risk_level"],
        "reason": result["reason"],
        "v3_features": use_v3
    }

    log_file = os.path.join(log_dir, f"risk_{datetime.now().strftime('%Y%m%d')}.jsonl")

    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Warning: Could not log analysis: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='Analyze tool use for risks')
    parser.add_argument('--tool', required=True, help='Tool name being used')
    parser.add_argument('--input', required=True, help='Tool input as JSON string')
    parser.add_argument('--v3', action='store_true', help='Use v3 enhanced features')

    # Parse known arguments and ignore unknown ones for robustness
    try:
        args, unknown = parser.parse_known_args()
        if unknown:
            print(f"Warning: Ignoring unknown arguments: {unknown}", file=sys.stderr)

        # Validate required arguments
        if not hasattr(args, 'tool') or not args.tool:
            raise ValueError("Missing required --tool argument")
        if not hasattr(args, 'input') or not args.input:
            raise ValueError("Missing required --input argument")

    except Exception as e:
        print(f"Argument parsing error: {e}", file=sys.stderr)
        error_result = {
            "error": f"Invalid arguments: {str(e)}",
            "decision": "SAFE",
            "risk_level": 0.0,
            "reason": "Argument parsing error - allowing by default"
        }
        print(json.dumps(error_result))
        sys.exit(0)

    try:
        tool_input = json.loads(args.input)
        result = analyze_tool_use(args.tool, tool_input, args.v3)

        log_analysis(args.tool, tool_input, result, args.v3)

        print(json.dumps(result))

        # Exit with appropriate code
        if result["decision"] == "BLOCK":
            sys.exit(1)
        elif result["decision"] in ["ANALYZE", "MONITOR"]:
            sys.exit(2)
        else:
            sys.exit(0)

    except Exception as e:
        error_result = {
            "error": f"Analysis failed: {str(e)}",
            "decision": "SAFE",
            "risk_level": 0.0,
            "reason": "Analysis error - allowing by default"
        }
        print(json.dumps(error_result))
        sys.exit(0)

if __name__ == "__main__":
    main()
