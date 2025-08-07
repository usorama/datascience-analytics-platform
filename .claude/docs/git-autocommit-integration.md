# Git Auto-Commit Integration for Claude Code

## Overview

This system provides automated git commits when Claude Code completes tasks, ensuring all development work is properly versioned without manual intervention. It integrates seamlessly with the existing BMAD validation system and project intelligence hooks.

## Architecture

### Components

1. **Task Completion Detector** (`task-completion-detector.py`)
   - Monitors development activity for completion indicators
   - Integrates with BMAD DoD and evidence validation
   - Triggers auto-commits based on configurable criteria

2. **Auto-Commit Script** (`task-completion-autocommit.sh`)
   - Performs the actual git commit operations
   - Generates contextual commit messages
   - Creates safety backups and tags

3. **Configuration System** (`autocommit-config.json`)
   - Configurable triggers and behavior
   - Safety settings and validation requirements
   - Integration with existing hook system

### Integration Points

- **PostToolUse Hook**: Detects completion after tool operations
- **Stop Hook**: Final completion check at session end
- **BMAD Validation**: Leverages existing DoD and evidence validation
- **Project Intelligence**: Coordinates with learning system

## Task Completion Detection

### Completion Triggers

1. **DoD Validation Passed**
   - Monitors `logs/quality/dod_validation.log`
   - Requires recent (within 1 hour) validation success

2. **Evidence Validation Passed**
   - Monitors `logs/quality/evidence_validation.log`
   - Confirms concrete evidence provided

3. **Story Completion Markers**
   - Scans recently modified `.md` files
   - Looks for patterns: "Story Complete", "✅ Complete", "COMPLETED"

4. **Significant Changes**
   - Detects when 3+ files have been modified
   - Indicates substantial development progress

5. **Agent Completion**
   - Identifies recent commits with agent signatures
   - Detects patterns: "🤖", "Agent", "Claude"

### Completion Types

- **Story Completion**: Full story with DoD + evidence validation
- **Task Completion**: Task with validation but no story marker
- **Agent Completion**: AI-generated implementation
- **Development Checkpoint**: Significant progress without validation
- **Epic Milestone**: Major feature implementation

## Auto-Commit Behavior

### Commit Message Templates

```bash
# Story completion
"✅ Story Complete: User authentication system - All acceptance criteria met"

# Task completion  
"✅ Task Complete: API endpoint implementation - Implementation verified"

# Agent completion
"🤖 Agent Task: Frontend dashboard components - Auto-generated implementation"

# Development checkpoint
"💾 Dev Checkpoint: Voice integration progress - Progress saved"
```

### Safety Mechanisms

1. **Backup Branches**
   - Creates `autocommit-backup-YYYYMMDD-HHMMSS` before commits
   - Enables easy rollback if needed

2. **Rate Limiting**
   - Maximum 10 auto-commits per hour
   - Prevents commit spam

3. **Validation Requirements**
   - Configurable validation requirements
   - Can require DoD + evidence validation

4. **Manual Override**
   - `--force` flag for manual triggering
   - `--disable` flag to stop auto-commits

## Configuration

### Auto-Commit Configuration (`config/autocommit-config.json`)

```json
{
  "enabled": true,
  "auto_push": false,
  "commit_message_template": "✅ Task Complete: {task_description}",
  "tag_completions": true,
  "require_dod_validation": true,
  "require_evidence_validation": true,
  "safety_backup": true,
  "completion_triggers": {
    "dod_validation": true,
    "evidence_validation": true,
    "story_markers": true,
    "significant_changes": true,
    "agent_completion": true
  },
  "safety_settings": {
    "create_backup_branch": true,
    "max_commits_per_hour": 10,
    "prevent_force_push": true
  }
}
```

### Claude Code Hook Integration

The system integrates with Claude Code's hook system in `settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/task-completion-detector.py",
            "description": "Detects task completion and triggers auto-commits"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/task-completion-detector.py",
            "description": "Final task completion check at session end"
          }
        ]
      }
    ]
  }
}
```

## Usage

### Automatic Operation

The system operates automatically when:
- Any tool operation completes (PostToolUse hook)
- Claude Code session ends (Stop hook)
- BMAD validation passes
- Story completion markers are detected

### Manual Control

```bash
# Check current configuration
python3 .claude/hooks/task-completion-detector.py --config

# Test detection without committing
python3 .claude/hooks/task-completion-detector.py --test

# Enable/disable detection
python3 .claude/hooks/task-completion-detector.py --enable
python3 .claude/hooks/task-completion-detector.py --disable

# Force auto-commit
bash .claude/hooks/task-completion-autocommit.sh --force

# View auto-commit configuration
bash .claude/hooks/task-completion-autocommit.sh --config
```

### Git Safety Commands

```bash
# View recent auto-commits
git log --oneline --grep="✅\|🤖\|💾" -10

# View completion tags
git tag -l "completion-*" --sort=-version:refname

# View backup branches
git branch -a | grep autocommit-backup

# Rollback to backup if needed
git checkout autocommit-backup-20250805-143022
```

## Monitoring and Logging

### Log Files

- `logs/task_completion.log` - Task completion detection events
- `logs/autocommit/autocommit.log` - Auto-commit operations
- `logs/quality/dod_validation.log` - DoD validation events
- `logs/quality/evidence_validation.log` - Evidence validation events

### Health Monitoring

```bash
# Check recent auto-commit activity
tail -20 .claude/logs/task_completion.log

# Monitor validation logs
tail -f .claude/logs/quality/dod_validation.log

# Check backup branch creation
git branch -a | grep backup | wc -l
```

## Troubleshooting

### Common Issues

1. **Auto-commits not triggering**
   - Check if detection is enabled: `--config`
   - Verify validation logs exist and show PASSED
   - Ensure git repository is initialized

2. **Too many auto-commits**
   - Check rate limiting in configuration
   - Adjust completion trigger sensitivity
   - Review validation requirements

3. **Commit message quality**
   - Customize templates in configuration
   - Check task description extraction logic
   - Review recent commit patterns

### Recovery Procedures

```bash
# Disable auto-commits immediately
python3 .claude/hooks/task-completion-detector.py --disable

# Rollback to backup branch
git branch -a | grep autocommit-backup | tail -1
git checkout <backup-branch>

# Squash multiple auto-commits
git rebase -i HEAD~5  # Interactive rebase last 5 commits

# Reset to specific checkpoint
git log --oneline | grep "Checkpoint"
git reset --hard <checkpoint-hash>
```

## Best Practices

1. **Configuration Management**
   - Review configuration regularly
   - Adjust triggers based on development patterns
   - Monitor commit frequency and quality

2. **Safety First**
   - Always keep backup branches enabled
   - Regular testing in development environment
   - Monitor for commit spam or quality issues

3. **Integration with Team**
   - Coordinate auto-commit settings with team
   - Establish commit message conventions
   - Regular cleanup of backup branches

4. **Monitoring**
   - Regular log review
   - Monitor validation system health
   - Track completion detection accuracy

## Future Enhancements

1. **Smart Commit Squashing**
   - Automatic squashing of related commits
   - Intelligent commit history cleanup

2. **Advanced Trigger Logic**
   - Machine learning-based completion detection
   - Context-aware commit message generation

3. **Team Coordination**
   - Shared completion events across team members
   - Automated pull request creation

4. **Quality Metrics**
   - Completion detection accuracy tracking
   - Commit quality scoring
   - Development velocity correlation

This system transforms git from a manual version control tool into an intelligent, automated development companion that ensures no work is lost and all progress is properly documented.