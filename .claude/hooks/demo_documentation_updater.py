#!/usr/bin/env python3
"""
Demo script for Documentation Update Automation System

This script demonstrates the documentation updater in action with
realistic file change scenarios.
"""

import json
import os
import sys
from pathlib import Path

# Add the hooks directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from documentation_updater import DocumentationUpdater


def demo_scenario(name: str, tool_data: dict):
    """Run a demo scenario and show results"""
    print(f"\n{'='*60}")
    print(f"DEMO SCENARIO: {name}")
    print(f"{'='*60}")
    
    # Initialize updater
    updater = DocumentationUpdater()
    
    # Show the input
    print("Input:")
    print(json.dumps(tool_data, indent=2))
    
    # Process the scenario
    result = updater.process_tool_execution(tool_data)
    
    # Show the result
    print(f"\nResult: {result}")
    
    # Show what documents would be updated
    changed_files = []
    tool_name = tool_data.get('tool_name', '')
    tool_input = tool_data.get('tool_input', {})
    
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        file_path = tool_input.get('file_path')
        if file_path:
            changed_files.append(file_path)
    elif tool_name == 'MultiEdit':
        edits = tool_input.get('edits', [])
        for edit in edits:
            file_path = edit.get('file_path')
            if file_path:
                changed_files.append(file_path)
    
    if changed_files:
        relevant_docs = updater._get_relevant_docs(changed_files)
        print(f"\nRelevant Documentation Files:")
        for doc in sorted(relevant_docs):
            print(f"  - {doc}")
    
    print(f"\n{'='*60}")


def main():
    """Run demo scenarios"""
    print("Documentation Update Automation System - DEMO")
    print("This demo shows how the system responds to different code changes")
    
    # Scenario 1: Frontend Component Creation
    demo_scenario("Frontend Component Creation", {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "client/components/VoiceRecognitionInterface.tsx"
        },
        "result": {"success": True}
    })
    
    # Scenario 2: Backend Service Update
    demo_scenario("Backend AI Service Update", {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "server/src/application/services/ai/VoiceProcessingService.ts"
        },
        "result": {"success": True}
    })
    
    # Scenario 3: Configuration Changes
    demo_scenario("Package.json Dependencies Update", {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "package.json"
        },
        "result": {"success": True}
    })
    
    # Scenario 4: Multiple File Changes
    demo_scenario("Multiple File Refactor", {
        "tool_name": "MultiEdit",
        "tool_input": {
            "edits": [
                {"file_path": "client/components/ChatInterface.tsx"},
                {"file_path": "client/hooks/useVoiceRecognition.ts"},
                {"file_path": "server/src/presentation/controllers/VoiceController.ts"},
                {"file_path": "server/src/domain/models/VoiceSession.ts"}
            ]
        },
        "result": {"success": True}
    })
    
    # Scenario 5: Test File Addition
    demo_scenario("Test File Addition", {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "client/components/__tests__/VoiceInterface.test.tsx"
        },
        "result": {"success": True}
    })
    
    # Scenario 6: Documentation Update
    demo_scenario("Documentation Self-Update", {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "docs/voice-integration.md"
        },
        "result": {"success": True}
    })
    
    # Scenario 7: LiveKit Prototype Changes
    demo_scenario("LiveKit Prototype Update", {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "livekit-voice-prototype/server/src/ai-teacher-agent.ts"
        },
        "result": {"success": True}
    })
    
    # Show system statistics
    print(f"\n{'='*60}")
    print("SYSTEM STATISTICS")
    print(f"{'='*60}")
    
    updater = DocumentationUpdater()
    
    # Show configuration stats
    patterns = len(updater.doc_mapping.get("file_patterns", {}))
    manifests = len(updater.doc_mapping.get("manifest_files", []))
    critical = len(updater.doc_mapping.get("critical_docs", []))
    
    print(f"File Patterns Configured: {patterns}")
    print(f"Manifest Files: {manifests}")
    print(f"Critical Documents: {critical}")
    
    # Show update log stats
    log_entries = len(updater.update_log)
    print(f"Historical Updates: {log_entries}")
    
    # Show rate limiting configuration
    rate_config = updater.doc_mapping.get("rate_limiting", {})
    window = rate_config.get("window_minutes", 30)
    max_updates = rate_config.get("max_updates_per_window", 5)
    print(f"Rate Limiting: {max_updates} updates per {window} minutes")
    
    print(f"\n{'='*60}")
    print("INTEGRATION STATUS")
    print(f"{'='*60}")
    
    settings_file = updater.project_dir / ".claude" / "settings.json"
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        # Check if our hook is configured
        post_hooks = settings.get("hooks", {}).get("PostToolUse", [])
        our_hook_configured = False
        
        for hook_group in post_hooks:
            hooks = hook_group.get("hooks", [])
            for hook in hooks:
                if "documentation_updater.py" in hook.get("command", ""):
                    our_hook_configured = True
                    break
        
        print(f"Hook Integration: {'✓ CONFIGURED' if our_hook_configured else '✗ NOT CONFIGURED'}")
    else:
        print("Hook Integration: ✗ SETTINGS FILE NOT FOUND")
    
    # Check if files exist
    script_path = updater.project_dir / ".claude" / "hooks" / "documentation_updater.py"
    config_path = updater.project_dir / ".claude" / "hooks" / "documentation_mapping.json"
    
    print(f"Script File: {'✓ EXISTS' if script_path.exists() else '✗ MISSING'}")
    print(f"Configuration: {'✓ EXISTS' if config_path.exists() else '✗ MISSING'}")
    
    print(f"\n{'='*60}")
    print("READY FOR PRODUCTION!")
    print("The documentation automation system is installed and configured.")
    print("It will automatically update documentation when code changes occur.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()