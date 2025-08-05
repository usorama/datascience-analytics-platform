"""Relationship Extraction Module for Strategic Alignment

This module extracts and analyzes relationships between work items,
OKRs, strategy documents, and other business entities.
"""

import re
import logging
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json

import numpy as np
import networkx as nx

from .models import (
    SemanticWorkItem, OKR, StrategyDocument,
    DocumentSection, KeyResult
)
from .embedder import SemanticEmbedder
from .text_processor import BusinessEntityExtractor


logger = logging.getLogger(__name__)


class RelationshipType(str, Enum):
    """Types of relationships between entities."""
    HIERARCHICAL = "hierarchical"  # parent-child
    DEPENDENCY = "dependency"      # depends on / blocks
    SEMANTIC = "semantic"          # similar content
    STRATEGIC = "strategic"        # aligns with
    TEMPORAL = "temporal"          # before/after
    OWNERSHIP = "ownership"        # owns/owned by
    REFERENCE = "reference"        # mentions/referenced by
    CONTRIBUTION = "contribution"  # contributes to


@dataclass
class EntityNode:
    """Represents an entity in the relationship graph."""
    entity_id: str
    entity_type: str  # work_item, okr, strategy, team, person
    title: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None
    
    def __hash__(self):
        return hash(self.entity_id)
    
    def __eq__(self, other):
        if isinstance(other, EntityNode):
            return self.entity_id == other.entity_id
        return False


@dataclass
class Relationship:
    """Represents a relationship between two entities."""
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    
    def reverse(self) -> 'Relationship':
        """Create reverse relationship."""
        reverse_types = {
            RelationshipType.DEPENDENCY: RelationshipType.DEPENDENCY,
            RelationshipType.HIERARCHICAL: RelationshipType.HIERARCHICAL,
            RelationshipType.OWNERSHIP: RelationshipType.OWNERSHIP,
        }
        
        return Relationship(
            source_id=self.target_id,
            target_id=self.source_id,
            relationship_type=reverse_types.get(
                self.relationship_type,
                self.relationship_type
            ),
            confidence=self.confidence,
            metadata={
                **self.metadata,
                'reversed': True,
                'original_direction': f"{self.source_id} -> {self.target_id}"
            },
            evidence=self.evidence
        )


class RelationshipExtractor:
    """Extracts relationships from text and metadata."""
    
    def __init__(
        self,
        embedder: Optional[SemanticEmbedder] = None,
        similarity_threshold: float = 0.7
    ):
        self.embedder = embedder or SemanticEmbedder()
        self.similarity_threshold = similarity_threshold
        self.entity_extractor = BusinessEntityExtractor()
        
        # Relationship patterns
        self.dependency_patterns = [
            (r'depends?\s+on\s+([^,\\.]+)', 'depends_on'),
            (r'blocked\s+by\s+([^,\\.]+)', 'blocked_by'),
            (r'blocks?\s+([^,\\.]+)', 'blocks'),
            (r'requires?\s+([^,\\.]+)', 'requires'),
            (r'prerequisite:?\s*([^,\\.]+)', 'prerequisite'),
            (r'enables?\s+([^,\\.]+)', 'enables'),
            (r'after\s+([^,\\.]+)', 'after'),
            (r'before\s+([^,\\.]+)', 'before')
        ]
        
        self.reference_patterns = [
            (r'see\s+([A-Z]+-\d+)', 'reference'),
            (r'relates?\s+to\s+([A-Z]+-\d+)', 'relates_to'),
            (r'implements?\s+([^,\\.]+)', 'implements'),
            (r'supports?\s+([^,\\.]+)', 'supports'),
            (r'aligns?\s+with\s+([^,\\.]+)', 'aligns_with'),
            (r'contributes?\s+to\s+([^,\\.]+)', 'contributes_to')
        ]
    
    def extract_from_work_items(
        self,
        work_items: List[SemanticWorkItem]
    ) -> Tuple[List[EntityNode], List[Relationship]]:
        """Extract entities and relationships from work items."""
        nodes = []
        relationships = []
        
        # Create nodes for work items
        for item in work_items:
            node = EntityNode(
                entity_id=f"wi_{item.work_item_id}",
                entity_type="work_item",
                title=item.title,
                metadata={
                    'work_item_type': item.work_item_type.value,
                    'state': item.state,
                    'area_path': item.area_path,
                    'story_points': item.story_points
                },
                embedding=item.combined_embedding
            )
            nodes.append(node)
        
        # Extract relationships
        for item in work_items:
            item_id = f"wi_{item.work_item_id}"
            
            # 1. Hierarchical relationships
            if item.parent_id:
                relationships.append(Relationship(
                    source_id=f"wi_{item.parent_id}",
                    target_id=item_id,
                    relationship_type=RelationshipType.HIERARCHICAL,
                    metadata={'direction': 'parent_to_child'}
                ))
            
            for child_id in item.children_ids:
                relationships.append(Relationship(
                    source_id=item_id,
                    target_id=f"wi_{child_id}",
                    relationship_type=RelationshipType.HIERARCHICAL,
                    metadata={'direction': 'parent_to_child'}
                ))
            
            # 2. Extract from text
            text_parts = []
            if item.full_description:
                text_parts.append(item.full_description)
            if item.acceptance_criteria_text:
                text_parts.append(item.acceptance_criteria_text)
            
            combined_text = " ".join(text_parts)
            
            if combined_text:
                # Dependency relationships
                for pattern, rel_type in self.dependency_patterns:
                    matches = re.findall(pattern, combined_text, re.IGNORECASE)
                    for match in matches:
                        relationships.append(Relationship(
                            source_id=item_id,
                            target_id=match.strip(),
                            relationship_type=RelationshipType.DEPENDENCY,
                            confidence=0.8,
                            metadata={'extraction_type': rel_type},
                            evidence=[f"Found '{match}' in {rel_type} pattern"]
                        ))
                
                # Reference relationships
                for pattern, rel_type in self.reference_patterns:
                    matches = re.findall(pattern, combined_text, re.IGNORECASE)
                    for match in matches:
                        relationships.append(Relationship(
                            source_id=item_id,
                            target_id=match.strip(),
                            relationship_type=RelationshipType.REFERENCE,
                            confidence=0.9,
                            metadata={'reference_type': rel_type},
                            evidence=[f"Found '{match}' in {rel_type} pattern"]
                        ))
            
            # 3. Team relationships
            if item.area_path:
                team_id = f"team_{item.area_path.lower().replace(' ', '_')}"
                team_node = EntityNode(
                    entity_id=team_id,
                    entity_type="team",
                    title=item.area_path,
                    metadata={'type': 'area_path'}
                )
                
                if team_node not in nodes:
                    nodes.append(team_node)
                
                relationships.append(Relationship(
                    source_id=team_id,
                    target_id=item_id,
                    relationship_type=RelationshipType.OWNERSHIP,
                    metadata={'ownership_type': 'team_owns_item'}
                ))
        
        return nodes, relationships
    
    def extract_from_okrs(
        self,
        okrs: List[OKR],
        work_items: Optional[List[SemanticWorkItem]] = None
    ) -> Tuple[List[EntityNode], List[Relationship]]:
        """Extract entities and relationships from OKRs."""
        nodes = []
        relationships = []
        
        # Create nodes for OKRs
        for okr in okrs:
            okr_node = EntityNode(
                entity_id=f"okr_{okr.okr_id}",
                entity_type="okr",
                title=okr.objective_text,
                metadata={
                    'period': okr.period,
                    'level': okr.level,
                    'owner': okr.owner,
                    'progress': okr.progress
                },
                embedding=okr.objective_embedding
            )
            nodes.append(okr_node)
            
            # Create nodes for key results
            for kr in okr.key_results:
                kr_node = EntityNode(
                    entity_id=f"kr_{kr.kr_id}",
                    entity_type="key_result",
                    title=kr.text,
                    metadata={
                        'target': kr.target_value,
                        'current': kr.current_value,
                        'unit': kr.unit
                    },
                    embedding=kr.embedding
                )
                nodes.append(kr_node)
                
                # OKR -> KR relationship
                relationships.append(Relationship(
                    source_id=okr_node.entity_id,
                    target_id=kr_node.entity_id,
                    relationship_type=RelationshipType.HIERARCHICAL,
                    metadata={'hierarchy_type': 'objective_to_kr'}
                ))
            
            # OKR hierarchical relationships
            if okr.parent_okr_id:
                relationships.append(Relationship(
                    source_id=f"okr_{okr.parent_okr_id}",
                    target_id=okr_node.entity_id,
                    relationship_type=RelationshipType.HIERARCHICAL,
                    metadata={'hierarchy_type': 'okr_cascade'}
                ))
            
            # Owner relationships
            if okr.owner:
                owner_id = f"person_{okr.owner.lower().replace(' ', '_')}"
                owner_node = EntityNode(
                    entity_id=owner_id,
                    entity_type="person",
                    title=okr.owner,
                    metadata={'role': 'okr_owner'}
                )
                
                if owner_node not in nodes:
                    nodes.append(owner_node)
                
                relationships.append(Relationship(
                    source_id=owner_id,
                    target_id=okr_node.entity_id,
                    relationship_type=RelationshipType.OWNERSHIP,
                    metadata={'ownership_type': 'person_owns_okr'}
                ))
            
            # Find work items that align with this OKR
            if work_items and okr.objective_embedding is not None:
                aligned_items = self._find_aligned_work_items(
                    okr, work_items
                )
                
                for item_id, confidence in aligned_items:
                    relationships.append(Relationship(
                        source_id=f"wi_{item_id}",
                        target_id=okr_node.entity_id,
                        relationship_type=RelationshipType.CONTRIBUTION,
                        confidence=confidence,
                        metadata={'alignment_type': 'semantic'},
                        evidence=[f"Semantic similarity: {confidence:.2f}"]
                    ))
        
        return nodes, relationships
    
    def extract_from_strategy_docs(
        self,
        docs: List[StrategyDocument]
    ) -> Tuple[List[EntityNode], List[Relationship]]:
        """Extract entities and relationships from strategy documents."""
        nodes = []
        relationships = []
        
        for doc in docs:
            # Create node for document
            doc_node = EntityNode(
                entity_id=f"doc_{doc.doc_id}",
                entity_type="strategy_document",
                title=doc.title,
                metadata={
                    'document_type': doc.document_type.value,
                    'created_date': doc.created_date.isoformat() if doc.created_date else None,
                    'themes': doc.strategic_themes
                },
                embedding=doc.document_embedding
            )
            nodes.append(doc_node)
            
            # Create nodes for strategic pillars
            for pillar in doc.strategic_pillars:
                pillar_id = f"pillar_{pillar.lower().replace(' ', '_')}"
                pillar_node = EntityNode(
                    entity_id=pillar_id,
                    entity_type="strategic_pillar",
                    title=pillar,
                    metadata={'source_doc': doc.doc_id}
                )
                
                if pillar_node not in nodes:
                    nodes.append(pillar_node)
                
                relationships.append(Relationship(
                    source_id=doc_node.entity_id,
                    target_id=pillar_id,
                    relationship_type=RelationshipType.STRATEGIC,
                    metadata={'strategy_type': 'defines_pillar'}
                ))
            
            # Extract entities from text
            entities = self.entity_extractor.extract_entities(doc.full_text)
            
            # Process timeline entities
            for timeline in entities.get('timeline', []):
                timeline_id = f"timeline_{timeline.lower().replace(' ', '_')}"
                timeline_node = EntityNode(
                    entity_id=timeline_id,
                    entity_type="timeline",
                    title=timeline,
                    metadata={'source': doc_node.entity_id}
                )
                
                if timeline_node not in nodes:
                    nodes.append(timeline_node)
                
                relationships.append(Relationship(
                    source_id=doc_node.entity_id,
                    target_id=timeline_id,
                    relationship_type=RelationshipType.TEMPORAL,
                    confidence=0.8,
                    evidence=[f"Found timeline reference: {timeline}"]
                ))
        
        return nodes, relationships
    
    def find_semantic_relationships(
        self,
        nodes: List[EntityNode],
        top_k: int = 5
    ) -> List[Relationship]:
        """Find semantic relationships based on embedding similarity."""
        relationships = []
        
        # Filter nodes with embeddings
        embedded_nodes = [n for n in nodes if n.embedding is not None]
        
        if len(embedded_nodes) < 2:
            return relationships
        
        # Calculate pairwise similarities
        for i, node1 in enumerate(embedded_nodes):
            similarities = []
            
            for j, node2 in enumerate(embedded_nodes):
                if i == j:
                    continue
                
                similarity = self.embedder.calculate_similarity(
                    node1.embedding,
                    node2.embedding
                )
                
                if similarity >= self.similarity_threshold:
                    similarities.append((j, node2, similarity))
            
            # Sort by similarity and take top_k
            similarities.sort(key=lambda x: x[2], reverse=True)
            
            for _, node2, similarity in similarities[:top_k]:
                relationships.append(Relationship(
                    source_id=node1.entity_id,
                    target_id=node2.entity_id,
                    relationship_type=RelationshipType.SEMANTIC,
                    confidence=similarity,
                    metadata={
                        'similarity_score': similarity,
                        'source_type': node1.entity_type,
                        'target_type': node2.entity_type
                    },
                    evidence=[f"Semantic similarity: {similarity:.2f}"]
                ))
        
        return relationships
    
    def _find_aligned_work_items(
        self,
        okr: OKR,
        work_items: List[SemanticWorkItem],
        threshold: float = 0.6
    ) -> List[Tuple[int, float]]:
        """Find work items aligned with an OKR."""
        aligned = []
        
        for item in work_items:
            if item.combined_embedding is None:
                continue
            
            # Check objective similarity
            obj_sim = self.embedder.calculate_similarity(
                okr.objective_embedding,
                item.combined_embedding
            )
            
            # Check KR similarities
            kr_sims = []
            for kr in okr.key_results:
                if kr.embedding is not None:
                    kr_sim = self.embedder.calculate_similarity(
                        kr.embedding,
                        item.combined_embedding
                    )
                    kr_sims.append(kr_sim)
            
            # Combined score
            max_kr_sim = max(kr_sims) if kr_sims else 0
            combined_sim = 0.7 * obj_sim + 0.3 * max_kr_sim
            
            if combined_sim >= threshold:
                aligned.append((item.work_item_id, combined_sim))
        
        return aligned
    
    def resolve_entity_references(
        self,
        relationships: List[Relationship],
        nodes: List[EntityNode]
    ) -> List[Relationship]:
        """Resolve text references to actual entity IDs."""
        # Create lookup maps
        node_by_id = {n.entity_id: n for n in nodes}
        node_by_title = defaultdict(list)
        for n in nodes:
            node_by_title[n.title.lower()].append(n)
        
        # Work item pattern
        wi_pattern = re.compile(r'([A-Z]+-\d+)')
        
        resolved = []
        for rel in relationships:
            # Check if target needs resolution
            if not rel.target_id.startswith(('wi_', 'okr_', 'doc_', 'kr_')):
                # Try to resolve the reference
                target_lower = rel.target_id.lower()
                
                # Check work item pattern
                wi_match = wi_pattern.match(rel.target_id)
                if wi_match:
                    # This looks like a work item reference
                    # In real system, would look up by ID
                    resolved_rel = Relationship(
                        source_id=rel.source_id,
                        target_id=f"wi_unresolved_{rel.target_id}",
                        relationship_type=rel.relationship_type,
                        confidence=rel.confidence * 0.8,  # Lower confidence
                        metadata={
                            **rel.metadata,
                            'resolution': 'unresolved_reference',
                            'original_target': rel.target_id
                        },
                        evidence=rel.evidence + ["Reference could not be resolved"]
                    )
                    resolved.append(resolved_rel)
                
                # Check title match
                elif target_lower in node_by_title:
                    candidates = node_by_title[target_lower]
                    if len(candidates) == 1:
                        # Exact match
                        resolved_rel = Relationship(
                            source_id=rel.source_id,
                            target_id=candidates[0].entity_id,
                            relationship_type=rel.relationship_type,
                            confidence=rel.confidence * 0.9,
                            metadata={
                                **rel.metadata,
                                'resolution': 'title_match',
                                'original_target': rel.target_id
                            },
                            evidence=rel.evidence + ["Resolved by title match"]
                        )
                        resolved.append(resolved_rel)
                    else:
                        # Multiple matches - ambiguous
                        for candidate in candidates:
                            resolved_rel = Relationship(
                                source_id=rel.source_id,
                                target_id=candidate.entity_id,
                                relationship_type=rel.relationship_type,
                                confidence=rel.confidence * 0.5,  # Lower confidence
                                metadata={
                                    **rel.metadata,
                                    'resolution': 'ambiguous_match',
                                    'candidates': len(candidates),
                                    'original_target': rel.target_id
                                },
                                evidence=rel.evidence + [f"Ambiguous match (1 of {len(candidates)})"]
                            )
                            resolved.append(resolved_rel)
                else:
                    # Could not resolve
                    resolved.append(rel)
            else:
                # Already resolved
                resolved.append(rel)
        
        return resolved


class RelationshipGraph:
    """Graph structure for entity relationships."""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.nodes_by_type = defaultdict(list)
        self.relationships_by_type = defaultdict(list)
    
    def add_nodes(self, nodes: List[EntityNode]):
        """Add nodes to the graph."""
        for node in nodes:
            self.graph.add_node(
                node.entity_id,
                entity_type=node.entity_type,
                title=node.title,
                metadata=node.metadata,
                embedding=node.embedding
            )
            self.nodes_by_type[node.entity_type].append(node.entity_id)
    
    def add_relationships(self, relationships: List[Relationship]):
        """Add relationships to the graph."""
        for rel in relationships:
            self.graph.add_edge(
                rel.source_id,
                rel.target_id,
                relationship_type=rel.relationship_type.value,
                confidence=rel.confidence,
                metadata=rel.metadata,
                evidence=rel.evidence
            )
            self.relationships_by_type[rel.relationship_type].append(rel)
    
    def find_paths(
        self,
        source_id: str,
        target_id: str,
        max_length: int = 5
    ) -> List[List[str]]:
        """Find all paths between two entities."""
        try:
            paths = list(nx.all_simple_paths(
                self.graph,
                source_id,
                target_id,
                cutoff=max_length
            ))
            return paths
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
    
    def get_impact_analysis(
        self,
        entity_id: str,
        impact_types: Optional[List[RelationshipType]] = None
    ) -> Dict[str, Any]:
        """Analyze impact of changes to an entity."""
        if impact_types is None:
            impact_types = [
                RelationshipType.DEPENDENCY,
                RelationshipType.HIERARCHICAL,
                RelationshipType.CONTRIBUTION
            ]
        
        impact = {
            'directly_impacts': [],
            'indirectly_impacts': [],
            'blocked_by': [],
            'total_affected': 0
        }
        
        # Direct impacts (outgoing edges)
        for _, target, data in self.graph.out_edges(entity_id, data=True):
            if RelationshipType(data['relationship_type']) in impact_types:
                impact['directly_impacts'].append({
                    'entity_id': target,
                    'relationship': data['relationship_type'],
                    'confidence': data['confidence']
                })
        
        # What blocks this entity (incoming dependencies)
        for source, _, data in self.graph.in_edges(entity_id, data=True):
            if (data['relationship_type'] == RelationshipType.DEPENDENCY.value and
                data.get('metadata', {}).get('extraction_type') in ['blocks', 'blocked_by']):
                impact['blocked_by'].append({
                    'entity_id': source,
                    'confidence': data['confidence']
                })
        
        # Find indirect impacts (2-3 hops)
        visited = set()
        queue = [(entity_id, 0)]
        
        while queue:
            current, depth = queue.pop(0)
            if depth > 3 or current in visited:
                continue
            
            visited.add(current)
            
            for _, target, data in self.graph.out_edges(current, data=True):
                if (RelationshipType(data['relationship_type']) in impact_types and
                    target not in visited):
                    if depth > 0:  # Indirect
                        impact['indirectly_impacts'].append({
                            'entity_id': target,
                            'path_length': depth + 1,
                            'confidence': data['confidence'] * (0.8 ** depth)
                        })
                    queue.append((target, depth + 1))
        
        impact['total_affected'] = (
            len(impact['directly_impacts']) +
            len(impact['indirectly_impacts'])
        )
        
        return impact
    
    def find_clusters(
        self,
        min_cluster_size: int = 3
    ) -> List[Set[str]]:
        """Find clusters of highly connected entities."""
        # Use community detection
        communities = nx.community.louvain_communities(
            self.graph.to_undirected()
        )
        
        # Filter by size
        clusters = [
            comm for comm in communities
            if len(comm) >= min_cluster_size
        ]
        
        return clusters
    
    def get_centrality_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate various centrality metrics."""
        metrics = {}
        
        # Degree centrality
        metrics['degree'] = nx.degree_centrality(self.graph)
        
        # Betweenness centrality (entities that connect others)
        metrics['betweenness'] = nx.betweenness_centrality(self.graph)
        
        # PageRank (importance based on connections)
        metrics['pagerank'] = nx.pagerank(self.graph)
        
        # Eigenvector centrality (connected to important nodes)
        try:
            metrics['eigenvector'] = nx.eigenvector_centrality(self.graph)
        except:
            metrics['eigenvector'] = {}
        
        return metrics
    
    def export_to_json(self) -> Dict[str, Any]:
        """Export graph to JSON format."""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            node_data = {
                'id': node_id,
                'type': data['entity_type'],
                'title': data['title'],
                'metadata': data['metadata']
            }
            nodes.append(node_data)
        
        edges = []
        for source, target, data in self.graph.edges(data=True):
            edge_data = {
                'source': source,
                'target': target,
                'type': data['relationship_type'],
                'confidence': data['confidence'],
                'metadata': data.get('metadata', {}),
                'evidence': data.get('evidence', [])
            }
            edges.append(edge_data)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'statistics': {
                'node_count': self.graph.number_of_nodes(),
                'edge_count': self.graph.number_of_edges(),
                'node_types': {k: len(v) for k, v in self.nodes_by_type.items()},
                'relationship_types': {
                    k.value: len(v) for k, v in self.relationships_by_type.items()
                }
            }
        }
    
    def generate_cypher_queries(self) -> List[str]:
        """Generate Neo4j Cypher queries for graph database."""
        queries = []
        
        # Create nodes
        for node_id, data in self.graph.nodes(data=True):
            node_type = data['entity_type'].upper()
            title = data['title'].replace("'", "\\'")
            
            query = f"CREATE (n:{node_type} {{id: '{node_id}', title: '{title}'"
            
            # Add metadata
            for key, value in data['metadata'].items():
                if isinstance(value, str):
                    value = value.replace("'", "\\'")
                    query += f", {key}: '{value}'"
                elif isinstance(value, (int, float)):
                    query += f", {key}: {value}"
            
            query += "})"
            queries.append(query)
        
        # Create relationships
        for source, target, data in self.graph.edges(data=True):
            rel_type = data['relationship_type'].upper()
            confidence = data['confidence']
            
            query = (
                f"MATCH (a {{id: '{source}'}}), (b {{id: '{target}'}}) "
                f"CREATE (a)-[r:{rel_type} {{confidence: {confidence}}}]->(b)"
            )
            queries.append(query)
        
        return queries