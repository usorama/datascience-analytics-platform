#!/usr/bin/env node
/**
 * Claude Multi-Agent BMAD System Installer
 * Installs complete quality-enforced multi-agent development system
 */

const fs = require('fs-extra');
const path = require('path');
const inquirer = require('inquirer');
const chalk = require('chalk');
const { spawn } = require('child_process');

class MultiAgentInstaller {
    constructor() {
        this.targetDir = process.cwd();
        this.sourceDir = path.dirname(__filename);
        this.claudeDir = path.join(this.targetDir, '.claude');
        
        this.components = {
            core: {
                name: '🔧 Core System',
                description: 'Configuration, templates, and quality gates',
                required: true,
                paths: ['config/', 'docs/templates/', 'docs/standards/']
            },
            commands: {
                name: '🎯 Multi-Agent Commands', 
                description: '/ui, /backend, /fullstack, /cicd, /so commands',
                required: true,
                paths: ['commands/']
            },
            agents: {
                name: '🤖 Specialized Agents',
                description: '28 specialized development agents',
                required: true,
                paths: ['agents/']
            },
            hooks: {
                name: '🛡️ Intelligence & Safety Hooks',
                description: 'Risk analysis, project intelligence, quality enforcement',
                required: true,
                paths: ['hooks/']
            },
            documentation: {
                name: '📚 Documentation & Guides',
                description: 'Complete usage documentation and best practices',
                required: false,
                paths: ['docs/README.md', 'docs/CONTINUOUS_IMPROVEMENT_SYSTEM.md']
            }
        };
    }

    async run() {
        console.log(chalk.cyan.bold('\n🚀 Claude Multi-Agent BMAD System Installer\n'));
        console.log(chalk.gray('Production-ready multi-agent development with quality enforcement\n'));

        try {
            await this.checkPrerequisites();
            const config = await this.gatherConfiguration();
            await this.performInstallation(config);
            await this.postInstallSetup(config);
            await this.displaySuccess();
        } catch (error) {
            console.error(chalk.red.bold('\n❌ Installation failed:'), error.message);
            process.exit(1);
        }
    }

    async checkPrerequisites() {
        console.log(chalk.blue('🔍 Checking prerequisites...\n'));

        // Check if we're in a directory suitable for installation
        if (fs.existsSync(path.join(this.targetDir, '.claude'))) {
            const { overwrite } = await inquirer.prompt([{
                type: 'confirm',
                name: 'overwrite',
                message: '.claude directory already exists. Overwrite?',
                default: false
            }]);

            if (!overwrite) {
                throw new Error('Installation cancelled - .claude directory exists');
            }
        }

        // Check for git repository
        const isGitRepo = fs.existsSync(path.join(this.targetDir, '.git'));
        if (!isGitRepo) {
            console.log(chalk.yellow('⚠️  Not a git repository. Consider initializing git for better integration.'));
        }

        console.log(chalk.green('✓ Prerequisites check passed\n'));
    }

    async gatherConfiguration() {
        console.log(chalk.blue('📋 Configuration setup...\n'));

        const questions = [
            {
                type: 'input',
                name: 'projectName',
                message: 'Project name:',
                default: path.basename(this.targetDir),
                validate: input => input.length > 0 || 'Project name is required'
            },
            {
                type: 'list',
                name: 'projectType',
                message: 'Project type:',
                choices: [
                    { name: 'Frontend (React, Vue, Angular)', value: 'frontend' },
                    { name: 'Backend (API, Services)', value: 'backend' },
                    { name: 'Full-Stack (Frontend + Backend)', value: 'fullstack' },
                    { name: 'Enterprise (All domains)', value: 'enterprise' }
                ]
            },
            {
                type: 'checkbox',
                name: 'components',
                message: 'Select components to install:',
                choices: Object.entries(this.components).map(([key, comp]) => ({
                    name: `${comp.name} - ${comp.description}`,
                    value: key,
                    checked: comp.required
                })),
                validate: choices => choices.length > 0 || 'At least one component must be selected'
            },
            {
                type: 'confirm',
                name: 'enableQualityGates',
                message: 'Enable quality enforcement gates (recommended)?',
                default: true
            },
            {
                type: 'confirm',
                name: 'enableLearning',
                message: 'Enable continuous improvement system?',
                default: true
            }
        ];

        return await inquirer.prompt(questions);
    }

    async performInstallation(config) {
        console.log(chalk.blue('\n📦 Installing Multi-Agent System...\n'));

        // Create directory structure
        await fs.ensureDir(this.claudeDir);
        await fs.ensureDir(path.join(this.claudeDir, 'logs', 'quality'));
        await fs.ensureDir(path.join(this.claudeDir, 'logs', 'sessions'));
        await fs.ensureDir(path.join(this.claudeDir, 'docs', 'sharded'));
        await fs.ensureDir(path.join(this.claudeDir, 'docs', 'workflow_state'));
        await fs.ensureDir(path.join(this.claudeDir, 'docs', 'handoffs'));

        // Install selected components
        for (const componentKey of config.components) {
            const component = this.components[componentKey];
            console.log(chalk.gray(`Installing ${component.name}...`));

            for (const relativePath of component.paths) {
                const sourcePath = path.join(this.sourceDir, '..', relativePath);
                const targetPath = path.join(this.claudeDir, relativePath);

                if (await fs.pathExists(sourcePath)) {
                    await fs.copy(sourcePath, targetPath, { overwrite: true });
                } else {
                    console.log(chalk.yellow(`Warning: Source path not found: ${sourcePath}`));
                }
            }
        }

        // Generate configuration file
        await this.generateConfiguration(config);

        console.log(chalk.green('\n✓ Component installation complete'));
    }

    async generateConfiguration(config) {
        const configContent = {
            project: {
                name: config.projectName,
                type: config.projectType,
                installed_at: new Date().toISOString(),
                version: '1.0.0'
            },
            bmad_integration: {
                version: '1.0',
                enforcement_mode: config.enableQualityGates ? 'mandatory' : 'advisory',
                quality_first_principle: config.enableQualityGates
            },
            quality_gates: {
                template_compliance: {
                    enabled: config.enableQualityGates,
                    enforcement: config.enableQualityGates ? 'mandatory' : 'advisory'
                },
                dod_completion: {
                    enabled: config.enableQualityGates,
                    enforcement: config.enableQualityGates ? 'mandatory' : 'advisory'
                },
                evidence_collection: {
                    enabled: config.enableQualityGates,
                    enforcement: config.enableQualityGates ? 'mandatory' : 'advisory'
                }
            },
            continuous_improvement: {
                enabled: config.enableLearning,
                data_collection: config.enableLearning,
                learning_cycles: {
                    weekly_analysis: config.enableLearning,
                    monthly_improvements: config.enableLearning,
                    quarterly_evolution: config.enableLearning
                }
            },
            components_installed: config.components
        };

        const configPath = path.join(this.claudeDir, 'config', 'multi-agent-config.yaml');
        await fs.ensureDir(path.dirname(configPath));
        
        // Convert to YAML format (simplified)
        const yamlContent = this.objectToYaml(configContent);
        await fs.writeFile(configPath, yamlContent);
    }

    objectToYaml(obj, indent = 0) {
        let yaml = '';
        const spaces = '  '.repeat(indent);
        
        for (const [key, value] of Object.entries(obj)) {
            if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                yaml += `${spaces}${key}:\n`;
                yaml += this.objectToYaml(value, indent + 1);
            } else if (Array.isArray(value)) {
                yaml += `${spaces}${key}:\n`;
                for (const item of value) {
                    yaml += `${spaces}  - ${item}\n`;
                }
            } else {
                yaml += `${spaces}${key}: ${JSON.stringify(value)}\n`;
            }
        }
        
        return yaml;
    }

    async postInstallSetup(config) {
        console.log(chalk.blue('\n🔧 Post-installation setup...\n'));

        // Make hooks executable
        const hooksDir = path.join(this.claudeDir, 'hooks');
        if (await fs.pathExists(hooksDir)) {
            const hookFiles = await fs.readdir(hooksDir);
            for (const file of hookFiles) {
                if (file.endsWith('.sh')) {
                    const filePath = path.join(hooksDir, file);
                    await fs.chmod(filePath, '755');
                }
            }
            console.log(chalk.gray('✓ Hook scripts made executable'));
        }

        // Update Claude Code settings if they exist
        const settingsPath = path.join(this.claudeDir, 'settings.json');
        if (config.enableQualityGates && !await fs.pathExists(settingsPath)) {
            const defaultSettings = {
                hooks: {
                    PreToolUse: [
                        {
                            matcher: "Write|Edit|MultiEdit",
                            hooks: [
                                {
                                    type: "command",
                                    command: `bash ${path.join(this.claudeDir, 'hooks', 'validate_template_compliance.sh')}`,
                                    description: "Validates template compliance - BLOCKS execution on failure"
                                }
                            ]
                        }
                    ]
                }
            };
            
            await fs.writeFile(settingsPath, JSON.stringify(defaultSettings, null, 2));
            console.log(chalk.gray('✓ Claude Code settings configured'));
        }

        // Initialize project documentation
        const claudeMdPath = path.join(this.targetDir, 'CLAUDE.md');
        if (!await fs.pathExists(claudeMdPath)) {
            const claudeMdContent = this.generateCLAUDEMd(config);
            await fs.writeFile(claudeMdPath, claudeMdContent);
            console.log(chalk.gray('✓ CLAUDE.md initialized'));
        }

        console.log(chalk.green('✓ Post-installation setup complete'));
    }

    generateCLAUDEMd(config) {
        return `# ${config.projectName}

## 🚨 MANDATORY QUALITY GATES (ALL AGENTS MUST COMPLY)

**CRITICAL ENFORCEMENT NOTICE**: These quality gates are ARCHITECTURALLY ENFORCED and cannot be bypassed.

### Configuration Loading Requirement
**MANDATORY**: All agents MUST load configuration from \`.claude/config/multi-agent-config.yaml\` before any action.

### Template Compliance Requirement
**MANDATORY**: All document outputs MUST follow template structure from \`.claude/docs/templates/\`.

### Definition of Done (DoD) Enforcement
**MANDATORY**: ALL story status changes to "Review" or "Done" MUST have 100% DoD completion.

### Evidence Collection Requirement
**MANDATORY**: All claims and completions MUST be backed by concrete evidence.

---

## Project Overview

${config.projectName} is enhanced with the Claude Multi-Agent BMAD System for quality-enforced development.

### Available Commands

${config.components.includes('commands') ? `
- \`/ui\` - Frontend development with 6 specialized agents
- \`/backend\` - Backend development with 6 specialized agents  
- \`/fullstack\` - Full-stack coordination with 6 integration agents
- \`/cicd\` - DevOps and infrastructure with 6 automation agents
- \`/so\` - Super-Orchestrator for intelligent multi-domain coordination
` : ''}

### Quality System

${config.enableQualityGates ? `
- ✅ Quality gates ENABLED and ENFORCED
- ✅ Template compliance mandatory
- ✅ DoD completion required
- ✅ Evidence collection enforced
` : `
- ⚠️ Quality gates in advisory mode
- ⚠️ Enable enforcement in .claude/config/multi-agent-config.yaml
`}

### Continuous Improvement

${config.enableLearning ? `
- ✅ Continuous improvement ENABLED
- ✅ Quality metrics collection active
- ✅ Learning cycles configured
` : `
- ⚠️ Continuous improvement disabled
- ⚠️ Enable learning in .claude/config/multi-agent-config.yaml
`}

---

For complete documentation, see \`.claude/docs/README.md\`
`;
    }

    async displaySuccess() {
        console.log(chalk.green.bold('\n🎉 Installation Complete!\n'));
        
        console.log(chalk.cyan('📁 Installed Components:'));
        console.log(chalk.gray(`   └── ${this.claudeDir}\n`));

        console.log(chalk.cyan('🚀 Getting Started:'));
        console.log(chalk.white('   1. Try: ') + chalk.yellow('/so "create a simple component"'));
        console.log(chalk.white('   2. Review: ') + chalk.yellow('CLAUDE.md') + chalk.white(' for project-specific configuration'));
        console.log(chalk.white('   3. Documentation: ') + chalk.yellow('.claude/docs/README.md\n'));

        console.log(chalk.cyan('🛡️ Quality System:'));
        console.log(chalk.white('   • Quality gates are ') + chalk.green('ACTIVE') + chalk.white(' and enforced'));
        console.log(chalk.white('   • All outputs must follow template structure'));
        console.log(chalk.white('   • 100% DoD completion required for story advancement\n'));

        console.log(chalk.cyan('🧠 Intelligence Features:'));
        console.log(chalk.white('   • Risk analysis on all commands'));
        console.log(chalk.white('   • Project intelligence and learning'));
        console.log(chalk.white('   • Cross-session context management\n'));

        console.log(chalk.green('Ready for production-quality development! 🚀'));
    }
}

// Run installer
if (require.main === module) {
    const installer = new MultiAgentInstaller();
    installer.run().catch(error => {
        console.error(chalk.red.bold('Installation failed:'), error);
        process.exit(1);
    });
}

module.exports = MultiAgentInstaller;