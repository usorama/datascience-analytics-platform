#!/usr/bin/env python3
"""
Project-level notification filter for Claude Code Automation v3.0
Filters and enhances notifications with intelligent processing
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
from datetime import datetime

def should_filter_notification(notification: str) -> tuple[bool, str]:
    """Determine if notification should be filtered"""
    
    # Filter out noisy notifications
    noise_patterns = [
        "Tool completed successfully",
        "Standard operation",
        "Normal file access",
        "Routine command execution"
    ]
    
    for pattern in noise_patterns:
        if pattern.lower() in notification.lower():
            return True, f"Filtered noise: {pattern}"
    
    return False, ""

def enhance_notification(notification: str) -> dict:
    """Enhance notification with additional context"""
    
    should_filter, reason = should_filter_notification(notification)
    
    if should_filter:
        return {
            "action": "FILTER",
            "reason": reason,
            "enhanced_notification": None
        }
    
    # Enhance important notifications
    enhancement_rules = [
        ("error", "🚨 Error detected"),
        ("warning", "⚠️ Warning issued"),
        ("success", "✅ Success confirmed"),
        ("blocked", "🛡️ Action blocked for safety"),
        ("risk", "⚠️ Risk assessment triggered")
    ]
    
    enhanced = notification
    for keyword, prefix in enhancement_rules:
        if keyword.lower() in notification.lower():
            enhanced = f"{prefix}: {notification}"
            break
    
    return {
        "action": "SHOW",
        "reason": "Important notification",
        "enhanced_notification": enhanced
    }

def log_notification(notification: str, result: dict):
    """Log notification processing"""
    log_dir = ".claude/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "notification_filter",
        "original_length": len(notification),
        "action": result["action"],
        "reason": result["reason"]
    }
    
    log_file = os.path.join(log_dir, f"notifications_{datetime.now().strftime('%Y%m%d')}.jsonl")
    
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Warning: Could not log notification: {e}", file=sys.stderr)

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: notification_filter.py <notification>"}))
        sys.exit(1)
    
    notification = sys.argv[1]
    
    try:
        result = enhance_notification(notification)
        log_notification(notification, result)
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        error_result = {
            "error": f"Notification processing failed: {str(e)}",
            "action": "SHOW",
            "enhanced_notification": notification
        }
        print(json.dumps(error_result))
        sys.exit(0)

if __name__ == "__main__":
    main()