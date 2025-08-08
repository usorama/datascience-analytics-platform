#!/usr/bin/env python3
"""
Dynamic Agent Registry Generator
Scans all agent directories and creates a comprehensive registry of all available agents.
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Agent:
    """Represents an agent in the registry"""
    name: str
    description: str
    category: str
    file_path: str
    color: Optional[str] = None
    tools: List[str] = None
    specializations: List[str] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []
        if self.specializations is None:
            self.specializations = []

class AgentRegistryGenerator:
    """Generates comprehensive agent registry from file system scan"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.agent_dirs = [
            "bmad", "design", "engineering", "marketing", 
            "product", "project-management", "studio-operations", "testing"
        ]
        self.agents: List[Agent] = []
        
    def scan_agents(self) -> List[Agent]:
        """Scan all agent directories and extract metadata"""
        agents_path = self.base_path / ".claude" / "agents"
        
        if not agents_path.exists():
            raise FileNotFoundError(f"Agents directory not found: {agents_path}")
            
        for category in self.agent_dirs:
            category_path = agents_path / category
            if not category_path.exists():
                print(f"Warning: Category directory not found: {category}")
                continue
                
            self._scan_category(category, category_path)
            
        return self.agents
    
    def _scan_category(self, category: str, category_path: Path):
        """Scan a specific category directory for agents"""
        for agent_file in category_path.glob("*.md"):
            try:
                agent = self._parse_agent_file(agent_file, category)
                if agent:
                    self.agents.append(agent)
            except Exception as e:
                print(f"Error parsing {agent_file}: {e}")
                
    def _parse_agent_file(self, file_path: Path, category: str) -> Optional[Agent]:
        """Parse an individual agent file and extract metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract YAML frontmatter
            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not frontmatter_match:
                print(f"No frontmatter found in {file_path}")
                return None
                
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            
            # Extract specializations from content
            specializations = self._extract_specializations(content)
            
            return Agent(
                name=frontmatter.get('name', file_path.stem),
                description=self._clean_description(frontmatter.get('description', '')),
                category=category,
                file_path=str(file_path.relative_to(self.base_path)),
                color=frontmatter.get('color'),
                tools=frontmatter.get('tools', []) if isinstance(frontmatter.get('tools'), list) else [frontmatter.get('tools')] if frontmatter.get('tools') else [],
                specializations=specializations
            )
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
            
    def _clean_description(self, description: str) -> str:
        """Clean and truncate description for registry"""
        # Remove examples and commentary blocks
        description = re.sub(r'<example>.*?</example>', '', description, flags=re.DOTALL)
        description = re.sub(r'<commentary>.*?</commentary>', '', description, flags=re.DOTALL)
        
        # Clean up whitespace and newlines
        description = ' '.join(description.split())
        
        # Truncate if too long
        if len(description) > 300:
            description = description[:297] + "..."
            
        return description
        
    def _extract_specializations(self, content: str) -> List[str]:
        """Extract specializations from agent content"""
        specializations = []
        
        # Look for common specialization patterns
        patterns = [
            r'specializes? in ([^.]+)',
            r'expertise (?:spans|includes?) ([^.]+)',
            r'responsible for ([^.]+)',
            r'focus(?:es)? on ([^.]+)',
            r'expert(?:ise)? (?:in|with) ([^.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Split on commas and clean up
                items = [item.strip() for item in match.split(',')]
                specializations.extend(items[:3])  # Limit to 3 per pattern
                
        # Clean and deduplicate
        specializations = list(dict.fromkeys([
            spec.lower().strip() for spec in specializations 
            if len(spec.strip()) > 3 and len(spec.strip()) < 50
        ]))
        
        return specializations[:10]  # Limit to top 10
        
    def generate_registry(self) -> Dict[str, Any]:
        """Generate the complete agent registry"""
        agents = self.scan_agents()
        
        registry = {
            "meta": {
                "generated": datetime.now().isoformat(),
                "total_agents": len(agents),
                "categories": list(self.agent_dirs),
                "version": "1.0.0"
            },
            "agents": [asdict(agent) for agent in agents],
            "by_category": self._group_by_category(agents),
            "by_specialization": self._group_by_specialization(agents),
            "capabilities": self._extract_capabilities(agents)
        }
        
        return registry
        
    def _group_by_category(self, agents: List[Agent]) -> Dict[str, List[str]]:
        """Group agents by category"""
        by_category = {}
        for agent in agents:
            if agent.category not in by_category:
                by_category[agent.category] = []
            by_category[agent.category].append(agent.name)
        return by_category
        
    def _group_by_specialization(self, agents: List[Agent]) -> Dict[str, List[str]]:
        """Group agents by specialization"""
        by_specialization = {}
        for agent in agents:
            for spec in agent.specializations:
                if spec not in by_specialization:
                    by_specialization[spec] = []
                by_specialization[spec].append(agent.name)
        return by_specialization
        
    def _extract_capabilities(self, agents: List[Agent]) -> Dict[str, Any]:
        """Extract capability summary"""
        all_tools = set()
        all_specializations = set()
        
        for agent in agents:
            all_tools.update(agent.tools)
            all_specializations.update(agent.specializations)
            
        return {
            "total_tools": len(all_tools),
            "available_tools": sorted(list(all_tools)),
            "total_specializations": len(all_specializations),
            "top_specializations": sorted(list(all_specializations))[:20]
        }
        
    def save_registry(self, output_path: str = None) -> str:
        """Save the registry to a JSON file"""
        if not output_path:
            output_path = str(self.base_path / ".claude" / "agent-registry.json")
            
        registry = self.generate_registry()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
            
        print(f"Agent registry saved to: {output_path}")
        print(f"Total agents: {registry['meta']['total_agents']}")
        print(f"Categories: {', '.join(registry['meta']['categories'])}")
        
        return output_path
        
    def generate_markdown_summary(self) -> str:
        """Generate a markdown summary of all agents"""
        registry = self.generate_registry()
        
        md = ["# Agent Registry Summary", ""]
        md.append(f"**Generated**: {registry['meta']['generated']}")
        md.append(f"**Total Agents**: {registry['meta']['total_agents']}")
        md.append("")
        
        # Category breakdown
        md.append("## Categories")
        for category, agent_names in registry['by_category'].items():
            md.append(f"### {category.title()} ({len(agent_names)} agents)")
            for agent_name in sorted(agent_names):
                agent_data = next(a for a in registry['agents'] if a['name'] == agent_name)
                md.append(f"- **{agent_name}**: {agent_data['description'][:100]}...")
            md.append("")
            
        # Capability summary
        md.append("## Capabilities Overview")
        md.append(f"- **Total Tools**: {registry['capabilities']['total_tools']}")
        md.append(f"- **Available Tools**: {', '.join(registry['capabilities']['available_tools'])}")
        md.append(f"- **Total Specializations**: {registry['capabilities']['total_specializations']}")
        md.append("")
        
        # Top specializations
        md.append("### Top Specializations")
        for spec in registry['capabilities']['top_specializations']:
            agents_with_spec = registry['by_specialization'].get(spec, [])
            md.append(f"- **{spec}**: {', '.join(agents_with_spec[:3])}{'...' if len(agents_with_spec) > 3 else ''}")
            
        return "\n".join(md)

def main():
    """Main entry point"""
    generator = AgentRegistryGenerator()
    
    try:
        # Generate and save registry
        output_path = generator.save_registry()
        
        # Generate markdown summary
        markdown_path = str(generator.base_path / ".claude" / "agent-registry-summary.md")
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(generator.generate_markdown_summary())
        print(f"Markdown summary saved to: {markdown_path}")
        
    except Exception as e:
        print(f"Error generating registry: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())