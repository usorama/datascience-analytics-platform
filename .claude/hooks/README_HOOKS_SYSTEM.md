# Git Checkpoint & Documentation Currency Hooks System

## Overview

This hooks system provides automated quality control for the Virtual Tutor AI project through:

1. **Git Checkpoint Management** - Automated rollback points before risky operations
2. **Documentation Currency Validation** - Ensures docs stay current with code changes
3. **Manifest Auto-Updates** - Keeps project manifests synchronized with codebase
4. **Commit-Triggered Alerts** - Flags when documentation updates are needed

## Hook Files

### Core Hooks

#### 1. `pre-implementation-checkpoint.sh`
Creates named git checkpoints before major code changes to enable easy rollback.

**Usage:**
```bash
# Manual checkpoint creation
.claude/hooks/pre-implementation-checkpoint.sh [operation-name] [description]

# Via pnpm scripts
pnpm run checkpoint
pnpm run checkpoint:create
```

**Features:**
- Creates tagged checkpoints with metadata
- Stashes uncommitted changes safely
- Generates automatic rollback scripts
- Maintains checkpoint history log
- Cleanup of old checkpoint metadata

**Example:**
```bash
./pre-implementation-checkpoint.sh "epic-3.9-voice-integration" "Before implementing voice AI features"
```

#### 2. `documentation-currency-check.sh`
Validates documentation freshness and flags outdated content.

**Usage:**
```bash
# Standard check
.claude/hooks/documentation-currency-check.sh

# With auto-fix
.claude/hooks/documentation-currency-check.sh --fix

# Verbose output
.claude/hooks/documentation-currency-check.sh --verbose

# Via pnpm scripts
pnpm run docs:check
pnpm run docs:check:verbose  
pnpm run docs:fix
```

**Validation Checks:**
- ✅ Critical file staleness (CLAUDE.md, design.md, README.md)
- ✅ Missing README files in code directories
- ✅ API documentation vs route changes consistency
- ✅ Dependency changes vs setup documentation
- ✅ Broken internal documentation links
- ✅ Documentation structure completeness

#### 3. `manifest-auto-updater.sh`
Automatically updates project manifests when code structure changes.

**Usage:**
```bash
# Update manifests
.claude/hooks/manifest-auto-updater.sh

# Force update all manifests
.claude/hooks/manifest-auto-updater.sh --force

# Dry run to see what would change
.claude/hooks/manifest-auto-updater.sh --dry-run

# Via pnpm scripts
pnpm run manifest:update
pnpm run manifest:update:force
pnpm run manifest:dry-run
```

**Generated Manifests:**
- `docs/manifests/file-structure.json` - Complete project structure
- `docs/manifests/api-endpoints.json` - API routes and middleware
- `docs/manifests/dependencies.json` - All workspace dependencies
- `docs/manifests/index.json` - Manifest index and metadata

#### 4. `post-commit-doc-check.sh`
Flags documentation updates needed after code commits.

**Features:**
- Analyzes commit changes for documentation impact
- Creates TODO files for required documentation updates
- Auto-runs manifest updater when needed
- Tracks documentation debt over time
- Provides actionable recommendations

**Triggered automatically by:**
- API route changes
- Core business logic changes
- Database schema modifications
- Frontend component changes
- Configuration file changes
- Deployment configuration changes

### Installation & Management

#### 5. `install-git-hooks.sh`
Installs all hooks into the git hooks directory.

**Usage:**
```bash
# Install hooks (preserves existing hooks)
.claude/hooks/install-git-hooks.sh

# Force reinstall (overwrites existing)
.claude/hooks/install-git-hooks.sh --force

# Via pnpm script
pnpm run hooks:install
```

#### 6. `manage-git-hooks.sh`
Manages hook installation and status.

**Usage:**
```bash
# Check hook status
.claude/hooks/manage-git-hooks.sh status

# Enable hooks
.claude/hooks/manage-git-hooks.sh enable

# Disable hooks
.claude/hooks/manage-git-hooks.sh disable

# Reinstall hooks
.claude/hooks/manage-git-hooks.sh reinstall

# Via pnpm scripts
pnpm run hooks:status
pnpm run hooks:enable
pnpm run hooks:disable
```

## Git Hook Integration

The system integrates with standard git hooks:

### Pre-Commit Hook
- Runs documentation currency check
- Maintains existing BMAD and lint-staged functionality
- Blocks commits if critical documentation issues found
- Provides auto-fix suggestions

### Post-Commit Hook
- Analyzes commit for documentation impacts
- Creates TODO files for needed updates
- Logs documentation debt metrics
- Auto-updates manifests when dependencies change

### Pre-Push Hook
- Creates checkpoint before pushing to remote
- Updates manifests to ensure they're current
- Runs existing type-check and lint validation

### Post-Merge Hook
- Force-updates all manifests after merges
- Runs documentation currency check
- Ensures documentation consistency across branches

## NPM/PNPM Script Integration

All hooks are integrated into the project's pnpm scripts:

```json
{
  "scripts": {
    "hooks:install": ".claude/hooks/install-git-hooks.sh",
    "hooks:status": ".claude/hooks/manage-git-hooks.sh status",
    "hooks:disable": ".claude/hooks/manage-git-hooks.sh disable", 
    "hooks:enable": ".claude/hooks/manage-git-hooks.sh enable",
    "checkpoint": ".claude/hooks/pre-implementation-checkpoint.sh",
    "checkpoint:create": ".claude/hooks/pre-implementation-checkpoint.sh manual 'Manual checkpoint creation'",
    "docs:check": ".claude/hooks/documentation-currency-check.sh",
    "docs:check:verbose": ".claude/hooks/documentation-currency-check.sh --verbose",
    "docs:fix": ".claude/hooks/documentation-currency-check.sh --fix",
    "manifest:update": ".claude/hooks/manifest-auto-updater.sh",
    "manifest:update:force": ".claude/hooks/manifest-auto-updater.sh --force",
    "manifest:dry-run": ".claude/hooks/manifest-auto-updater.sh --dry-run"
  }
}
```

## Usage Examples

### Creating a Checkpoint Before Major Work
```bash
# Before starting Epic 3.9 implementation
pnpm run checkpoint "epic-3.9-start" "Checkpoint before voice integration work"

# Implement features...

# If something goes wrong, rollback:
git reset --hard checkpoint-epic-3.9-start-20250805-143022
# or run the generated rollback script:
.claude/hooks/rollback-to-checkpoint-epic-3.9-start-20250805-143022.sh
```

### Documentation Maintenance Workflow
```bash
# Check documentation currency
pnpm run docs:check:verbose

# Auto-fix minor issues
pnpm run docs:fix

# Update manifests after code changes
pnpm run manifest:update

# Check what manifests would change
pnpm run manifest:dry-run
```

### Troubleshooting Failed Commits
```bash
# If pre-commit hook blocks commit due to docs
pnpm run docs:fix
git add -A
git commit -m "Fix documentation currency issues"

# Or bypass temporarily (not recommended)
git commit --no-verify -m "WIP: bypass docs check"
```

## File Locations

### Hook Scripts
- `.claude/hooks/` - All hook scripts
- `.claude/hooks/doc-todos/` - Generated documentation TODO files
- `.claude/hooks/currency-reports/` - Documentation currency reports
- `.claude/hooks/doc-check-logs/` - Daily documentation check logs
- `.claude/hooks/checkpoint-history.log` - Checkpoint creation history

### Generated Files
- `docs/manifests/` - Auto-generated project manifests
- `.claude/hooks/.checkpoint-*.json` - Checkpoint metadata
- `.claude/hooks/rollback-to-*.sh` - Auto-generated rollback scripts

### Git Hooks
- `.git/hooks/pre-commit` - Enhanced with documentation checks
- `.git/hooks/post-commit` - Runs documentation impact analysis
- `.git/hooks/pre-push` - Creates checkpoints and updates manifests
- `.git/hooks/post-merge` - Updates manifests after merges
- `.git/hooks/*.backup` - Original hook backups

## Configuration

### Environment Variables
- `CLAUDE_PROJECT_DIR` - Override project directory (defaults to `pwd`)
- `AGENT_NAME` - Set agent name for checkpoint attribution

### Customization
- Modify `MAX_AGE_DAYS` in documentation-currency-check.sh
- Add file patterns to checkpoint triggers
- Customize manifest generation logic
- Adjust documentation validation rules

## Quality Gates

The hooks system enforces these quality gates:

1. **Pre-Commit**: Documentation must be reasonably current
2. **Post-Commit**: Documentation impact must be assessed and logged
3. **Pre-Push**: Checkpoints created, manifests current
4. **Post-Merge**: All manifests updated, documentation consistency verified

## Monitoring & Reporting

### Daily Reports
- `.claude/hooks/doc-check-logs/YYYYMMDD.log` - Daily documentation check summaries
- `.claude/hooks/currency-reports/` - Detailed currency analysis reports

### Metrics Tracked
- Documentation debt accumulation
- Checkpoint creation frequency  
- Manifest update frequency
- Hook execution success/failure rates

## Integration with CI/CD

The hooks integrate seamlessly with existing CI/CD:

```yaml
# GitHub Actions example
- name: Install Git Hooks
  run: pnpm run hooks:install

- name: Check Documentation Currency
  run: pnpm run docs:check

- name: Update Manifests
  run: pnpm run manifest:update
```

## Best Practices

1. **Create checkpoints before risky operations**
   ```bash
   pnpm run checkpoint "refactor-auth-system" "Before major auth refactoring"
   ```

2. **Run documentation checks regularly**
   ```bash
   pnpm run docs:check:verbose
   ```

3. **Keep manifests current**
   ```bash
   pnpm run manifest:update
   ```

4. **Review TODO files created by post-commit hook**
   ```bash
   find .claude/hooks/doc-todos -name "*.md" -newer .git/refs/heads/main
   ```

5. **Monitor documentation debt**
   ```bash
   tail -f .claude/hooks/doc-check-logs/$(date +%Y%m%d).log
   ```

## Troubleshooting

### Hook Not Running
```bash
# Check hook status
pnpm run hooks:status

# Reinstall if needed
pnpm run hooks:install --force
```

### Documentation Check Failures
```bash
# Get detailed information
pnpm run docs:check:verbose

# Auto-fix common issues
pnpm run docs:fix
```

### Checkpoint Rollback
```bash
# List recent checkpoints
git tag -l "checkpoint-*" --sort=-version:refname | head -10

# Rollback to specific checkpoint
git reset --hard checkpoint-operation-timestamp

# Use generated rollback script
.claude/hooks/rollback-to-checkpoint-operation-timestamp.sh
```

### Manifest Issues
```bash
# See what would change
pnpm run manifest:dry-run

# Force update everything
pnpm run manifest:update:force
```

## Security Notes

- All hooks validate input and use safe file operations
- Temporary files are cleaned up automatically
- Git operations are performed with error checking
- No sensitive information is logged or stored
- Rollback scripts include confirmation prompts

## Future Enhancements

Planned improvements:
- Integration with external documentation systems
- Slack/Discord notifications for documentation debt
- Automated documentation generation from code
- Advanced checkpoint management with branch tracking
- Documentation coverage metrics
- AI-powered documentation suggestions

---

This hooks system provides enterprise-grade automation for maintaining code-documentation consistency and enabling safe, reversible development workflows. It's designed to be unobtrusive while providing powerful safety nets and quality assurance.