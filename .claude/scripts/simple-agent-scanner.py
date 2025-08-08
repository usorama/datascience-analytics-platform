#!/usr/bin/env python3
"""
Simple Agent Scanner - No external dependencies
Scans all agent files and creates a basic registry
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

def extract_frontmatter(content):
    """Extract YAML-like frontmatter without yaml library"""
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not frontmatter_match:
        return {}
        
    lines = frontmatter_match.group(1).strip().split('\n')
    data = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Handle lists
            if value.startswith('[') and value.endswith(']'):
                # Simple list parsing
                value = [item.strip().strip('"\'') for item in value[1:-1].split(',')]
                value = [item for item in value if item]
            else:
                value = value.strip('"\'')
                
            data[key] = value
            
    return data

def scan_agents_simple():
    """Simple agent scanning without external dependencies"""
    base_path = Path(__file__).parent.parent
    agents_path = base_path / ".claude" / "agents"
    
    if not agents_path.exists():
        print(f"Agents directory not found: {agents_path}")
        return {}
        
    agents = []
    categories = {}
    
    for category_dir in agents_path.iterdir():
        if not category_dir.is_dir():
            continue
            
        category = category_dir.name
        category_agents = []
        
        for agent_file in category_dir.glob("*.md"):
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                frontmatter = extract_frontmatter(content)
                
                if 'name' in frontmatter:
                    agent_info = {
                        'name': frontmatter.get('name', agent_file.stem),
                        'category': category,
                        'description': frontmatter.get('description', '')[:200],
                        'color': frontmatter.get('color', ''),
                        'tools': frontmatter.get('tools', []),
                        'file_path': str(agent_file.relative_to(base_path))
                    }
                    
                    agents.append(agent_info)
                    category_agents.append(agent_info['name'])
                    
            except Exception as e:
                print(f"Error reading {agent_file}: {e}")
                
        if category_agents:
            categories[category] = category_agents
    
    registry = {
        "meta": {
            "generated": datetime.now().isoformat(),
            "total_agents": len(agents),
            "categories": list(categories.keys()),
            "scanner_version": "simple-1.0"
        },
        "agents": agents,
        "by_category": categories
    }
    
    return registry

def main():
    registry = scan_agents_simple()
    
    output_path = Path(__file__).parent.parent / ".claude" / "agent-registry.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"Registry saved to: {output_path}")
    print(f"Total agents found: {registry['meta']['total_agents']}")
    print("\nCategories:")
    for category, agent_list in registry['by_category'].items():
        print(f"  {category}: {len(agent_list)} agents")
        for agent in agent_list:
            print(f"    - {agent}")
    
    return registry

if __name__ == "__main__":
    main()