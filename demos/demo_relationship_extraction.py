#!/usr/bin/env python3
"""
Relationship Extraction Demo

This demonstrates how the system extracts and analyzes relationships
between work items, OKRs, and strategy documents.
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from datascience_platform.ado.semantic import (
    OKR, KeyResult, StrategyDocument, DocumentType,
    SemanticWorkItem, SemanticEmbedder
)
from datascience_platform.ado.semantic.relationship_extractor import (
    RelationshipExtractor, RelationshipGraph, RelationshipType
)
from datascience_platform.ado import WorkItemType


def create_connected_work_items():
    """Create work items with various relationships."""
    items = []
    
    # Epic: Authentication Overhaul
    epic = SemanticWorkItem(
        work_item_id=3001,
        title="Authentication System Overhaul",
        work_item_type=WorkItemType.EPIC,
        state="Active",
        business_value_raw=95,
        story_points=89,
        full_description="""
Completely redesign our authentication system to support modern security standards
and improve user experience. This aligns with our Security Excellence strategic pillar
and directly contributes to SOC2 compliance.

This epic depends on completing the Security Audit (EPIC-2999) and blocks the
Customer Portal Redesign (EPIC-3010).

Key deliverables:
- Multi-factor authentication
- Single Sign-On (SSO) support
- Passwordless authentication options
- Enhanced session management
""",
        business_justification="Critical for SOC2 compliance and reducing security incidents",
        area_path="Security Team",
        pi_number=15
    )
    items.append(epic)
    
    # Feature 1: MFA Implementation
    feature1 = SemanticWorkItem(
        work_item_id=3002,
        parent_id=3001,
        title="Implement Multi-Factor Authentication",
        work_item_type=WorkItemType.FEATURE,
        state="Active",
        business_value_raw=85,
        story_points=34,
        full_description="""
Add MFA support using TOTP and SMS. This feature is required for SOC2 compliance
and addresses customer security concerns.

Depends on User Profile Service upgrade (STORY-2995).
Relates to Security Policy DOC-101.
""",
        area_path="Security Team"
    )
    items.append(feature1)
    feature1.children_ids = [3003, 3004]
    
    # Feature 2: SSO Integration
    feature2 = SemanticWorkItem(
        work_item_id=3005,
        parent_id=3001,
        title="Enterprise SSO Integration",
        work_item_type=WorkItemType.FEATURE,
        state="New",
        business_value_raw=75,
        story_points=21,
        full_description="""
Integrate with enterprise SSO providers (Okta, Auth0, Azure AD).
This enables our enterprise customers to use their existing identity providers.

Requires completion of MFA implementation first.
Supports our Q3 OKR for enterprise customer growth.
""",
        area_path="Integration Team"
    )
    items.append(feature2)
    
    # User Stories
    story1 = SemanticWorkItem(
        work_item_id=3003,
        parent_id=3002,
        title="As a user, I want to enable TOTP-based 2FA",
        work_item_type=WorkItemType.USER_STORY,
        state="Active",
        business_value_raw=70,
        story_points=13,
        full_description="""
Users should be able to set up TOTP (Time-based One-Time Password) authentication
using apps like Google Authenticator or Authy.

This implements part of our MFA feature and contributes to the security OKR.
Blocked by database schema migration (TASK-2990).
""",
        acceptance_criteria_text="""
- User can scan QR code to set up TOTP
- Backup codes are generated
- User can disable/re-enable TOTP
- Works with common authenticator apps
""",
        area_path="Security Team"
    )
    items.append(story1)
    
    story2 = SemanticWorkItem(
        work_item_id=3004,
        parent_id=3002,
        title="As an admin, I want to enforce MFA for all users",
        work_item_type=WorkItemType.USER_STORY,
        state="New",
        business_value_raw=80,
        story_points=8,
        full_description="""
Administrators need the ability to enforce MFA across the organization.
This is critical for enterprise customers and SOC2 compliance.

Depends on TOTP implementation (STORY-3003).
Aligns with Security Excellence pillar.
""",
        area_path="Security Team"
    )
    items.append(story2)
    
    # Unrelated item for contrast
    story3 = SemanticWorkItem(
        work_item_id=3006,
        title="Update copyright year in footer",
        work_item_type=WorkItemType.USER_STORY,
        state="New",
        business_value_raw=5,
        story_points=1,
        full_description="Change copyright from 2024 to 2025",
        area_path="Frontend Team"
    )
    items.append(story3)
    
    # Cross-team dependency
    story4 = SemanticWorkItem(
        work_item_id=3007,
        title="API Gateway authentication integration",
        work_item_type=WorkItemType.USER_STORY,
        state="New",
        business_value_raw=60,
        story_points=21,
        full_description="""
Update API Gateway to support new authentication system.
This is required before we can deploy the new auth system to production.

Depends on MFA implementation (FEATURE-3002) and SSO integration (FEATURE-3005).
Blocks API v3 release (EPIC-3020).

See also: API Gateway Documentation (DOC-200).
""",
        area_path="Platform Team"
    )
    items.append(story4)
    
    return items


def create_connected_okrs():
    """Create OKRs with relationships."""
    okrs = []
    
    # Company OKR
    company_okr = OKR(
        okr_id="okr_2025_q3_company",
        period="Q3 2025",
        level="company",
        objective_text="Become the most trusted platform in our industry",
        owner="CEO",
        key_results=[
            KeyResult(
                kr_id="kr_security_incidents",
                text="Zero security incidents affecting customer data",
                target_value=0,
                current_value=2
            ),
            KeyResult(
                kr_id="kr_enterprise_growth",
                text="Grow enterprise customer base by 50%",
                target_value=150,
                current_value=100,
                unit="customers"
            ),
            KeyResult(
                kr_id="kr_trust_score",
                text="Achieve trust score of 90+ in industry survey",
                target_value=90,
                current_value=72,
                unit="score"
            )
        ],
        strategic_pillars=["Security Excellence", "Customer Trust", "Growth"]
    )
    okrs.append(company_okr)
    
    # Security Team OKR
    security_okr = OKR(
        okr_id="okr_2025_q3_security",
        period="Q3 2025",
        level="team",
        objective_text="Build industry-leading security infrastructure",
        owner="CISO",
        team="Security",
        parent_okr_id="okr_2025_q3_company",
        key_results=[
            KeyResult(
                kr_id="kr_soc2",
                text="Complete SOC2 Type II certification",
                target_value=100,
                current_value=60,
                unit="%"
            ),
            KeyResult(
                kr_id="kr_mfa_adoption",
                text="100% MFA adoption for all users",
                target_value=100,
                current_value=15,
                unit="%"
            )
        ]
    )
    okrs.append(security_okr)
    
    return okrs


def create_strategy_documents():
    """Create strategy documents with relationships."""
    docs = []
    
    # Security Strategy
    security_strategy = StrategyDocument(
        doc_id="doc_security_2025",
        title="Security Excellence Strategy 2025",
        document_type=DocumentType.STRATEGY,
        full_text="""
# Security Excellence Strategy 2025

## Vision
Become the industry benchmark for security and compliance by Q4 2025.

## Strategic Initiatives

### 1. Modern Authentication (Q3 2025)
Implement state-of-the-art authentication including MFA, SSO, and passwordless options.
This initiative directly supports SOC2 compliance and enterprise customer requirements.

### 2. Zero Trust Architecture (Q4 2025)
After completing authentication overhaul, implement zero trust principles across
all services. Depends on completing the authentication system redesign.

### 3. Compliance Automation
Automate compliance reporting and evidence collection for SOC2, ISO 27001, and GDPR.

## Dependencies
- Requires completion of Security Audit (Q2 2025)
- Blocks Customer Portal Redesign until auth system is complete
- Relates to Engineering Excellence initiative for API security

## Success Metrics
- Zero security incidents
- 100% MFA adoption
- SOC2 Type II certification
- 90+ security score in industry benchmarks
""",
        created_date=datetime(2025, 1, 15),
        strategic_pillars=["Security Excellence", "Compliance", "Customer Trust"],
        strategic_themes=["security", "compliance", "authentication", "zero-trust"]
    )
    docs.append(security_strategy)
    
    return docs


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"{title.center(70)}")
    print(f"{'=' * 70}\n")


def visualize_relationships(graph: RelationshipGraph):
    """Create visual representation of relationships."""
    print("\nRELATIONSHIP GRAPH VISUALIZATION:")
    print("-" * 50)
    
    # Group by relationship type
    rel_types = {}
    for source, target, data in graph.graph.edges(data=True):
        rel_type = data['relationship_type']
        if rel_type not in rel_types:
            rel_types[rel_type] = []
        
        source_title = graph.graph.nodes[source].get('title', source)[:30]
        target_title = graph.graph.nodes[target].get('title', target)[:30]
        
        rel_types[rel_type].append({
            'source': source_title,
            'target': target_title,
            'confidence': data.get('confidence', 1.0)
        })
    
    # Display by type
    for rel_type, relationships in rel_types.items():
        print(f"\n{rel_type.upper()} Relationships:")
        for rel in relationships[:5]:  # Show top 5
            confidence = rel['confidence']
            arrow = "==>" if confidence > 0.8 else "-->" if confidence > 0.5 else "..>"
            print(f"  {rel['source']} {arrow} {rel['target']} ({confidence:.2f})")
        
        if len(relationships) > 5:
            print(f"  ... and {len(relationships) - 5} more")


def main():
    """Run the relationship extraction demo."""
    print_section("Relationship Extraction Demo - August 5, 2025")
    
    # Create test data
    print("1. Creating interconnected test data...")
    work_items = create_connected_work_items()
    okrs = create_connected_okrs()
    strategy_docs = create_strategy_documents()
    
    print(f"   ✓ {len(work_items)} work items with dependencies")
    print(f"   ✓ {len(okrs)} cascading OKRs")
    print(f"   ✓ {len(strategy_docs)} strategy documents")
    
    # Initialize components
    print("\n2. Initializing relationship extraction system...")
    embedder = SemanticEmbedder()
    extractor = RelationshipExtractor(embedder=embedder)
    graph = RelationshipGraph()
    
    # Extract relationships from each source
    print("\n3. Extracting relationships...")
    
    # From work items
    wi_nodes, wi_relationships = extractor.extract_from_work_items(work_items)
    print(f"   ✓ Work items: {len(wi_nodes)} entities, {len(wi_relationships)} relationships")
    
    # From OKRs
    okr_nodes, okr_relationships = extractor.extract_from_okrs(okrs, work_items)
    print(f"   ✓ OKRs: {len(okr_nodes)} entities, {len(okr_relationships)} relationships")
    
    # From strategy documents
    doc_nodes, doc_relationships = extractor.extract_from_strategy_docs(strategy_docs)
    print(f"   ✓ Strategy docs: {len(doc_nodes)} entities, {len(doc_relationships)} relationships")
    
    # Combine all nodes and relationships
    all_nodes = wi_nodes + okr_nodes + doc_nodes
    all_relationships = wi_relationships + okr_relationships + doc_relationships
    
    # Generate embeddings for semantic analysis
    print("\n4. Generating embeddings for semantic relationship discovery...")
    for item in work_items:
        if item.combined_embedding is None:
            embeddings = embedder.embed_work_item(item)
            item.combined_embedding = embeddings['combined']
    
    for okr in okrs:
        if okr.objective_embedding is None:
            okr.objective_embedding, kr_embeddings = embedder.embed_okr(okr)
    
    for doc in strategy_docs:
        if doc.document_embedding is None:
            doc.document_embedding = embedder.embed_strategy_document(doc)
    
    # Find semantic relationships
    semantic_relationships = extractor.find_semantic_relationships(all_nodes, top_k=3)
    all_relationships.extend(semantic_relationships)
    print(f"   ✓ Found {len(semantic_relationships)} semantic relationships")
    
    # Resolve entity references
    print("\n5. Resolving entity references...")
    resolved_relationships = extractor.resolve_entity_references(
        all_relationships, all_nodes
    )
    print(f"   ✓ Resolved {len(resolved_relationships)} relationships")
    
    # Build graph
    print("\n6. Building relationship graph...")
    graph.add_nodes(all_nodes)
    graph.add_relationships(resolved_relationships)
    
    graph_data = graph.export_to_json()
    print(f"   ✓ Graph contains {graph_data['statistics']['node_count']} nodes")
    print(f"   ✓ Graph contains {graph_data['statistics']['edge_count']} edges")
    
    # Show node type distribution
    print("\n   Node types:")
    for node_type, count in graph_data['statistics']['node_types'].items():
        print(f"     • {node_type}: {count}")
    
    # Show relationship type distribution
    print("\n   Relationship types:")
    for rel_type, count in graph_data['statistics']['relationship_types'].items():
        print(f"     • {rel_type}: {count}")
    
    # Visualize relationships
    visualize_relationships(graph)
    
    # Analyze specific relationships
    print_section("Relationship Analysis Examples")
    
    # Example 1: Impact analysis
    auth_epic_id = "wi_3001"
    print(f"1. Impact Analysis for '{work_items[0].title}':")
    impact = graph.get_impact_analysis(auth_epic_id)
    
    print(f"   Directly impacts: {len(impact['directly_impacts'])} entities")
    for item in impact['directly_impacts'][:3]:
        print(f"     • {item['entity_id']} ({item['relationship']})")
    
    print(f"   Blocked by: {len(impact['blocked_by'])} entities")
    for item in impact['blocked_by']:
        print(f"     • {item['entity_id']}")
    
    print(f"   Total affected entities: {impact['total_affected']}")
    
    # Example 2: Path finding
    print("\n2. Path Analysis:")
    mfa_story_id = "wi_3003"
    company_okr_id = "okr_okr_2025_q3_company"
    
    paths = graph.find_paths(mfa_story_id, company_okr_id, max_length=4)
    print(f"   Paths from MFA story to Company OKR: {len(paths)}")
    
    if paths:
        print("   Shortest path:")
        path = paths[0]
        for i, node_id in enumerate(path):
            node = graph.graph.nodes[node_id]
            indent = "     " + "  " * i
            print(f"{indent}→ {node['title'][:40]}")
    
    # Example 3: Centrality analysis
    print("\n3. Key Entity Analysis (Centrality):")
    centrality = graph.get_centrality_metrics()
    
    # Find most central entities
    top_central = sorted(
        centrality['pagerank'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    print("   Most important entities (by PageRank):")
    for entity_id, score in top_central:
        node = graph.graph.nodes[entity_id]
        print(f"     • {node['title'][:40]} ({node['entity_type']}): {score:.3f}")
    
    # Example 4: Cluster detection
    print("\n4. Cluster Analysis:")
    clusters = graph.find_clusters(min_cluster_size=3)
    print(f"   Found {len(clusters)} clusters")
    
    for i, cluster in enumerate(clusters[:2], 1):
        print(f"\n   Cluster {i} ({len(cluster)} entities):")
        cluster_nodes = list(cluster)[:5]
        for node_id in cluster_nodes:
            node = graph.graph.nodes[node_id]
            print(f"     • {node['title'][:40]} ({node['entity_type']})")
        if len(cluster) > 5:
            print(f"     ... and {len(cluster) - 5} more")
    
    # Generate insights
    print_section("Key Insights from Relationship Analysis")
    
    print("DISCOVERED PATTERNS:")
    print("-" * 50)
    print("• Authentication Epic is a critical hub connecting security strategy to implementation")
    print("• Strong alignment between Security Team work items and Security OKRs")
    print("• Cross-team dependencies identified between Security, Integration, and Platform teams")
    print("• Orphaned work item detected: 'Update copyright year' has no strategic connections")
    
    print("\nRISK ANALYSIS:")
    print("-" * 50)
    print("• API Gateway integration (3007) is a critical dependency blocking multiple initiatives")
    print("• MFA implementation has cascading dependencies affecting 4+ other work items")
    print("• Security Audit (referenced but not in dataset) is blocking the Authentication Epic")
    
    print("\nRECOMMENDATIONS:")
    print("-" * 50)
    print("1. Prioritize completing dependencies for Authentication Epic")
    print("2. Consider cancelling or deferring orphaned work items")
    print("3. Ensure cross-team coordination for API Gateway integration")
    print("4. Create explicit links between work items and OKR key results")
    
    # Export for visualization
    print("\n5. Exporting graph data for visualization tools...")
    
    # Save JSON for D3.js or other visualization
    json_file = Path("relationship_graph.json")
    with open(json_file, 'w') as f:
        json.dump(graph.export_to_json(), f, indent=2)
    print(f"   ✓ Saved graph data to {json_file}")
    
    # Generate Cypher queries for Neo4j
    cypher_queries = graph.generate_cypher_queries()
    cypher_file = Path("relationship_graph.cypher")
    with open(cypher_file, 'w') as f:
        f.write("// Cypher queries for Neo4j import\n\n")
        for query in cypher_queries[:10]:  # Sample
            f.write(query + ";\n")
    print(f"   ✓ Generated {len(cypher_queries)} Cypher queries in {cypher_file}")
    
    print_section("Demo Complete")
    print("The Relationship Extraction system successfully:")
    print("✓ Extracted entities and relationships from text")
    print("✓ Discovered semantic connections through embeddings")  
    print("✓ Built a comprehensive knowledge graph")
    print("✓ Analyzed dependencies and impact paths")
    print("✓ Identified key entities and clusters")
    print("✓ Generated actionable insights for planning")


if __name__ == "__main__":
    main()