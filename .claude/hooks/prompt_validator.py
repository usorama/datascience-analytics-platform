#!/usr/bin/env python3
"""
Project-level prompt validation for Claude Code Automation v3.0
Validates user prompts for potentially dangerous patterns
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
from datetime import datetime

def check_dangerous_prompts(prompt: str) -> tuple[bool, str]:
    """Check for dangerous patterns in prompts"""
    dangerous_patterns = [
        (r'rm\s+-rf\s+/', 'Dangerous file deletion detected'),
        (r':\(\)\s*\{\s*:\|\:&\s*\}\s*\;\s*:', 'Fork bomb pattern detected'),
        (r'format\s+[cC]:', 'Disk formatting command detected'),
        (r'sudo\s+dd\s+if=', 'Dangerous disk operation detected'),
        (r'curl\s+[^|]*\|\s*bash', 'Piped download execution detected'),
        (r'wget\s+[^|]*\|\s*sh', 'Piped download execution detected'),
        (r'chmod\s+777\s+/', 'Dangerous permission change detected'),
        (r'chown\s+-R\s+[^/]*\s+/', 'Dangerous ownership change detected'),
        (r'>/dev/sd[a-z]', 'Direct disk write detected'),
        (r'git\s+push\s+--force', 'Forced git push detected'),
    ]
    
    for pattern, reason in dangerous_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return True, reason
    
    return False, ""

def validate_prompt(prompt: str) -> dict:
    """Validate a user prompt and return assessment"""
    
    # Quick check for dangerous patterns
    is_dangerous, reason = check_dangerous_prompts(prompt)
    if is_dangerous:
        return {
            "decision": "BLOCK",
            "risk_level": 0.9,
            "reason": reason,
            "recommendation": "Please rephrase your request without dangerous language"
        }
    
    # Check for potentially risky patterns
    risky_keywords = [
        'delete', 'remove', 'force', 'overwrite', 'destructive',
        'system', 'admin', 'root', 'sudo', 'chmod', 'chown'
    ]
    
    risk_score = 0.0
    found_keywords = []
    
    for keyword in risky_keywords:
        if keyword.lower() in prompt.lower():
            risk_score += 0.1
            found_keywords.append(keyword)
    
    # Normalize risk score
    risk_score = min(risk_score, 0.8)
    
    if risk_score > 0.5:
        return {
            "decision": "ANALYZE",
            "risk_level": risk_score,
            "reason": f"Contains potentially risky keywords: {', '.join(found_keywords)}",
            "recommendation": "Review the request for potential risks"
        }
    
    return {
        "decision": "SAFE",
        "risk_level": risk_score,
        "reason": "No significant risk patterns detected",
        "recommendation": "Proceed normally"
    }

def log_validation(prompt: str, result: dict):
    """Log validation result"""
    log_dir = ".claude/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "prompt_validation",
        "prompt_length": len(prompt),
        "prompt_hash": hash(prompt),
        "decision": result["decision"],
        "risk_level": result["risk_level"],
        "reason": result["reason"]
    }
    
    log_file = os.path.join(log_dir, f"validation_{datetime.now().strftime('%Y%m%d')}.jsonl")
    
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Warning: Could not log validation: {e}", file=sys.stderr)

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: prompt_validator.py <prompt>"}))
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    try:
        result = validate_prompt(prompt)
        log_validation(prompt, result)
        
        print(json.dumps(result))
        
        # Exit with appropriate code
        if result["decision"] == "BLOCK":
            sys.exit(1)
        elif result["decision"] == "ANALYZE":
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        error_result = {
            "error": f"Validation failed: {str(e)}",
            "decision": "SAFE",
            "risk_level": 0.0,
            "reason": "Validation error - allowing by default"
        }
        print(json.dumps(error_result))
        sys.exit(0)

if __name__ == "__main__":
    main()