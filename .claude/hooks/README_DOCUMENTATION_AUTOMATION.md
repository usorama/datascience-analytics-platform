# Documentation Update Automation System

## Overview

The Documentation Update Automation System intelligently monitors code changes and automatically updates relevant documentation files, including manifests, README files, and architectural documentation. This system ensures that documentation stays synchronized with code changes without manual intervention.

## Components

### 1. Documentation Updater Hook (`documentation_updater.py`)

The main automation engine that:
- Monitors Write, Edit, MultiEdit, and NotebookEdit operations
- Maps changed files to relevant documentation using pattern matching
- Updates documentation files with intelligent content synchronization
- Creates meaningful git commits for documentation updates
- Implements rate limiting to prevent spam updates
- Integrates with existing project intelligence infrastructure

### 2. Documentation Mapping Configuration (`documentation_mapping.json`)

Comprehensive configuration file that defines:
- **File Patterns**: Maps code file patterns to relevant documentation files
- **Manifest Files**: Critical documentation files that require smart updates
- **Auto-Update Sections**: Specific sections within documents that can be automatically updated
- **Rate Limiting Rules**: Controls update frequency to prevent excessive commits
- **Commit Templates**: Customizable commit message templates for different change types

### 3. Hook Integration (`settings.json`)

The system integrates into the existing Claude Code hook infrastructure via PostToolUse hooks, triggering after file modification operations complete successfully.

## Architecture

```
Code Change (Write/Edit) → PostToolUse Hook → Documentation Updater
                                                     ↓
Pattern Matching → Relevant Docs → Rate Limit Check → Smart Update
                                                     ↓
Content Analysis → Section Updates → Git Commit → Logging
```

## File Pattern Mapping

The system uses glob-like patterns to map code changes to documentation updates:

### Frontend Changes
- `client/**/*.tsx` → Updates `CLAUDE.md`, `design.md`, `docs/frontend-architecture.md`
- `client/components/**/*` → Updates `design.md`, `docs/component-library.md`
- `client/app/**/*` → Updates routing and structure documentation

### Backend Changes
- `server/**/*.ts` → Updates `CLAUDE.md`, `docs/api-documentation.md`
- `server/src/application/**/*` → Updates business logic documentation
- `server/src/domain/**/*` → Updates domain model documentation
- `server/src/infrastructure/**/*` → Updates infrastructure documentation

### Configuration Changes
- `package.json` → Updates `CLAUDE.md`, `DEPLOYMENT-GUIDE.md`, `ENVIRONMENT_SETUP.md`
- `pnpm-workspace.yaml` → Updates workspace configuration documentation
- `.env*` files → Updates environment setup documentation

### AI Integration Changes
- `server/src/application/services/ai/**/*` → Updates AI integration documentation
- `livekit-voice-prototype/**/*` → Updates voice prototype documentation

## Smart Update Features

### 1. Rate Limiting
- **Default Window**: 30 minutes
- **Max Updates**: 5 per window per document
- **Critical Documents**: Stricter limits (15 minutes, 3 updates)
- Prevents spam commits from frequent code changes

### 2. Content Analysis
- Extracts structural information from code files (functions, classes, exports, imports)
- Updates documentation sections based on actual code changes
- Maintains change history and metrics

### 3. Intelligent Commit Messages
- Templates based on change type (frontend, backend, config, tests)
- Includes file counts and change summaries
- Follows project commit message conventions
- Includes Claude Code attribution

### 4. Manifest Section Updates
Automatically updates specific sections in key documents:
- **CLAUDE.md**: Tech stack, codebase structure, development commands
- **design.md**: Component rules, custom CSS classes
- **DEPLOYMENT-GUIDE.md**: Deployment steps, environment configuration

## Usage

### Automatic Operation
The system runs automatically on every file modification operation. No manual intervention required.

### Manual Testing
```bash
# Test the documentation updater directly
python3 .claude/hooks/documentation_updater.py

# Test with sample data
export CLAUDE_HOOK_INPUT='{"tool_name":"Write","tool_input":{"file_path":"client/components/ChatInterface.tsx"}}'
python3 .claude/hooks/documentation_updater.py
```

### Configuration Customization
Edit `documentation_mapping.json` to:
- Add new file patterns
- Modify documentation targets
- Adjust rate limiting settings
- Customize commit templates

## Logging and Monitoring

### Update Log (`analytics/documentation_updates.json`)
Tracks all documentation updates with:
- Timestamp of update
- Changed files that triggered update
- Updated documentation files
- File types involved
- Update type classification

### Rate Limiting Log (`analytics/doc_update_rate_limit.json`)
Monitors update frequency to enforce rate limits:
- Last update timestamps per document
- Update counts within time windows
- Rate limiting decisions

### Integration with Project Intelligence
The system integrates with existing project intelligence to:
- Learn from documentation update patterns
- Track effectiveness of different update strategies
- Provide insights on documentation health

## Safety Features

### 1. Error Handling
- Non-blocking: Errors don't prevent code operations
- Graceful degradation: System continues working with partial failures
- Comprehensive logging: All errors logged for debugging

### 2. Git Safety
- Only commits when updates are successful
- Meaningful commit messages with context
- Rollback capability through git history

### 3. Content Preservation
- Never overwrites existing content unless explicitly configured
- Adds timestamp comments for traceability
- Maintains document structure and formatting

## Performance Considerations

### 1. Efficient Pattern Matching
- Optimized regex patterns for file matching
- Early exit for non-matching files
- Cached pattern compilation

### 2. Minimal File I/O
- Only reads files when updates are needed
- Batches multiple changes into single commits
- Uses file hashing to detect actual changes

### 3. Rate Limiting
- Prevents excessive git operations
- Batches related updates
- Prioritizes critical documentation

## Troubleshooting

### Common Issues

1. **Updates Not Triggering**
   - Check file patterns in `documentation_mapping.json`
   - Verify PostToolUse hook is configured correctly
   - Check rate limiting hasn't blocked updates

2. **Git Commit Failures**
   - Ensure git is properly configured
   - Check file permissions
   - Verify documentation files exist

3. **Rate Limiting Too Restrictive**
   - Adjust `rate_limiting` settings in configuration
   - Check update logs for frequency patterns
   - Consider different limits for different document types

### Debug Mode
Enable verbose logging by setting environment variable:
```bash
export CLAUDE_DOC_UPDATER_DEBUG=1
```

## Future Enhancements

### Planned Features
1. **AI-Powered Content Generation**: Use AI to generate relevant documentation sections
2. **Dependency Graph Analysis**: Update documentation based on code dependency changes
3. **Multi-Project Support**: Handle documentation updates across related projects
4. **Webhook Integration**: Notify external systems of documentation changes
5. **Validation Rules**: Ensure documentation quality and completeness

### Integration Opportunities
1. **CI/CD Integration**: Validate documentation updates in pull requests
2. **Documentation Site**: Auto-deploy updated documentation
3. **Slack/Teams Notifications**: Alert teams about documentation changes
4. **Analytics Dashboard**: Visual insights into documentation health

## Contributing

When modifying the documentation automation system:

1. **Test Changes**: Always test with sample file operations
2. **Update Patterns**: Add new file patterns for new code areas
3. **Rate Limit Consideration**: Adjust limits based on project activity
4. **Logging**: Ensure new features include appropriate logging
5. **Error Handling**: Maintain non-blocking error handling

## Example Scenarios

### Scenario 1: Frontend Component Addition
```
Action: Create new component `client/components/VoiceInterface.tsx`
Trigger: Write tool operation
Updates: design.md, docs/component-library.md
Commit: "📱 Update frontend documentation for 1 component changes"
```

### Scenario 2: Backend API Endpoint Addition
```
Action: Add new endpoint in `server/src/presentation/controllers/VoiceController.ts`
Trigger: Write tool operation
Updates: CLAUDE.md, docs/api-documentation.md, docs/controllers.md
Commit: "🔧 Update backend documentation for 1 API changes"
```

### Scenario 3: Configuration Change
```
Action: Modify `package.json` to add new dependency
Trigger: Edit tool operation
Updates: CLAUDE.md, DEPLOYMENT-GUIDE.md, ENVIRONMENT_SETUP.md
Commit: "📦 Update dependencies documentation"
```

## Security Considerations

1. **File Access**: System only accesses files within project directory
2. **Git Operations**: Limited to documentation files only
3. **Rate Limiting**: Prevents potential abuse or spam
4. **Error Isolation**: Failures don't affect main development workflow
5. **Audit Trail**: Complete logging of all operations

This documentation automation system ensures that the AI Tutor project's documentation remains current and accurate as the codebase evolves, reducing maintenance overhead while improving documentation quality.