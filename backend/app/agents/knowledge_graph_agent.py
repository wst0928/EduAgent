"""Knowledge Graph Agent: builds and queries domain knowledge structures."""
from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent
from app.models.knowledge import (
    KnowledgeEdge,
    KnowledgeGraph,
    KnowledgeNode,
    NodeType,
    RelationType,
)
from app.services.memory_service import memory_service


PROMPT = """你是一位知识图谱专家，负责构建学科领域的知识结构。
你的职责：
1. 根据学习主题，构建该领域的知识图谱（概念、关系网络）
2. 识别知识间的前置依赖关系
3. 评估每个知识点的难度等级
4. 为个性化学习路径提供知识结构支撑
"""


class KnowledgeGraphAgent(BaseAgent):
    """Builds and manages knowledge graphs for learning domains."""

    def __init__(self) -> None:
        super().__init__(
            name="KnowledgeGraphAgent",
            description="构建领域知识图谱，分析知识间关系",
            system_prompt=PROMPT,
        )

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        action = context.get("action", "build_graph")
        topic = context.get("topic", "")
        graph_name = context.get("graph_name", f"kg_{topic}")

        if action == "build_graph":
            return await self._build_knowledge_graph(topic, graph_name)
        elif action == "query_prerequisites":
            node_id = context.get("node_id", "")
            return self._get_prerequisites(graph_name, node_id)
        elif action == "decompose_topic":
            return await self._decompose_topic(topic)
        else:
            return {"error": f"Unknown action: {action}"}

    async def _build_knowledge_graph(self, topic: str, graph_name: str) -> dict[str, Any]:
        result = await self._llm_structured([
            {"role": "user",
             "content": f"""为以下学习主题构建知识图谱，包括核心概念及其关系。

主题：{topic}

请返回JSON格式（简洁但全面）：
{{
  "nodes": [
    {{"id": "id_1", "name": "概念名称", "description": "简要描述", "node_type": "subject/topic/concept/prerequisite/skill", "difficulty": 1-5, "tags": ["标签"], "estimated_hours": 1.0}}
  ],
  "edges": [
    {{"source_id": "id_1", "target_id": "id_2", "relation_type": "prerequisite/composed_of/related_to/teaches", "weight": 1.0, "description": "关系描述"}}
  ]
}}"""
            }])

        nodes_data = result.get("nodes", [])
        edges_data = result.get("edges", [])

        kg = KnowledgeGraph(name=graph_name)
        for nd in nodes_data:
            node = KnowledgeNode(
                id=nd.get("id", ""),
                name=nd.get("name", ""),
                description=nd.get("description", ""),
                node_type=NodeType(nd.get("node_type", "concept")),
                difficulty=nd.get("difficulty", 1),
                tags=nd.get("tags", []),
                estimated_hours=nd.get("estimated_hours", 1.0),
            )
            kg.add_node(node)

        for ed in edges_data:
            edge = KnowledgeEdge(
                source_id=ed.get("source_id", ""),
                target_id=ed.get("target_id", ""),
                relation_type=RelationType(ed.get("relation_type", "related_to")),
                weight=ed.get("weight", 1.0),
                description=ed.get("description", ""),
            )
            kg.add_edge(edge)

        memory_service.save_knowledge_graph(kg)

        return {
            "graph_name": graph_name,
            "node_count": len(kg.nodes),
            "edge_count": len(kg.edges),
            "nodes": [n.model_dump() for n in kg.nodes.values()],
            "edges": [e.model_dump() for e in kg.edges],
        }

    def _get_prerequisites(self, graph_name: str, node_id: str) -> dict[str, Any]:
        kg = memory_service.get_knowledge_graph(graph_name)
        if not kg:
            return {"error": f"知识图谱 {graph_name} 不存在"}
        prereqs = kg.get_prerequisites(node_id)
        children = kg.get_children(node_id)
        return {
            "node": kg.nodes.get(node_id).model_dump() if node_id in kg.nodes else None,
            "prerequisites": [n.model_dump() for n in prereqs],
            "subtopics": [n.model_dump() for n in children],
        }

    async def _decompose_topic(self, topic: str) -> dict[str, Any]:
        result = await self._llm_structured([
            {"role": "user",
             "content": f"""将学习主题 "{topic}" 分解为子主题列表，并标注学习顺序。

返回JSON格式：
{{
  "subtopics": [
    {{"order": 1, "name": "子主题名称", "description": "简要描述", "estimated_hours": 2.0, "difficulty": 1}}
  ],
  "total_estimated_hours": 10.0
}}"""
            }])
        return result
