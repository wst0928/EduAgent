"""Knowledge graph models for domain structure representation."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    subject = "subject"
    topic = "topic"
    concept = "concept"
    prerequisite = "prerequisite"
    skill = "skill"


class RelationType(str, Enum):
    prerequisite = "prerequisite"
    composed_of = "composed_of"
    related_to = "related_to"
    teaches = "teaches"


class KnowledgeNode(BaseModel):
    id: str
    name: str
    description: str = ""
    node_type: NodeType = NodeType.concept
    difficulty: int = 1
    tags: list[str] = Field(default_factory=list)
    estimated_hours: float = 1.0


class KnowledgeEdge(BaseModel):
    source_id: str
    target_id: str
    relation_type: RelationType = RelationType.related_to
    weight: float = 1.0
    description: str = ""


class KnowledgeGraph(BaseModel):
    name: str
    nodes: dict[str, KnowledgeNode] = Field(default_factory=dict)
    edges: list[KnowledgeEdge] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_node(self, node: KnowledgeNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: KnowledgeEdge) -> None:
        self.edges.append(edge)

    def get_prerequisites(self, node_id: str) -> list[KnowledgeNode]:
        prereq_ids = [
            e.source_id for e in self.edges
            if e.target_id == node_id and e.relation_type == RelationType.prerequisite
        ]
        return [self.nodes[pid] for pid in prereq_ids if pid in self.nodes]

    def get_children(self, node_id: str) -> list[KnowledgeNode]:
        child_ids = [
            e.target_id for e in self.edges
            if e.source_id == node_id and e.relation_type == RelationType.composed_of
        ]
        return [self.nodes[cid] for cid in child_ids if cid in self.nodes]
