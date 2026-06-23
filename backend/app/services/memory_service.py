"""MemoryService: persistent storage with recommendation support."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from app.models.knowledge import KnowledgeGraph
from app.models.resource import LearningResource
from app.models.user import User

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
RESOURCES_FILE = DATA_DIR / "resources.json"
KNOWLEDGE_FILE = DATA_DIR / "knowledge.json"


class MemoryService:
    """Manages persistent storage for users, resources, and knowledge graphs."""

    def __init__(self) -> None:
        DATA_DIR.mkdir(exist_ok=True)
        self._users: dict[str, User] = {}
        self._resources: dict[str, LearningResource] = {}
        self._knowledge_graphs: dict[str, KnowledgeGraph] = {}
        self._sessions: dict[str, list[dict]] = {}
        self._load()

    # ---- User operations ----

    def create_user(self, user_id: str) -> User:
        user = User(id=user_id)
        self._users[user_id] = user
        self._save_users()
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def update_user(self, user: User) -> None:
        user.updated_at = datetime.utcnow()
        self._users[user.id] = user
        self._save_users()

    # ---- Session operations ----

    def get_session(self, session_id: str) -> list[dict]:
        return self._sessions.get(session_id, [])

    def add_to_session(self, session_id: str, messages: list[dict]) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].extend(messages)

    def clear_session(self, session_id: str) -> None:
        self._sessions[session_id] = []

    # ---- Resource operations ----

    def save_resource(self, resource: LearningResource) -> None:
        self._resources[resource.id] = resource
        self._save_resources()

    def get_resource(self, resource_id: str) -> Optional[LearningResource]:
        return self._resources.get(resource_id)

    def list_resources(self, user_id: Optional[str] = None) -> list[LearningResource]:
        return list(self._resources.values())

    def get_resources_by_topic(self, topic: str) -> list[LearningResource]:
        """Get resources related to a specific topic."""
        topic_lower = topic.lower()
        return [
            r for r in self._resources.values()
            if topic_lower in r.title.lower()
            or topic_lower in " ".join(r.metadata.tags).lower()
        ]

    def recommend_resources(
        self,
        user_id: str,
        topic: str = "",
        top_k: int = 5,
    ) -> list[LearningResource]:
        """Recommend resources based on user profile and learning history.

        Scoring factors:
        - Difficulty match with user preference
        - Topic relevance
        - User's past feedback (higher scored resources preferred)
        - Variety of resource types
        """
        user = self.get_user(user_id)
        if not user:
            return self.list_resources()[:top_k]

        scored: list[tuple[float, LearningResource]] = []
        resources = (
            self.get_resources_by_topic(topic) if topic
            else list(self._resources.values())
        )

        for res in resources:
            score = 0.0

            # Difficulty match (+3)
            pref_level = {"beginner": 1, "intermediate": 3, "advanced": 5}
            pref_diff = pref_level.get(user.profile.preferred_difficulty.value, 3)
            diff_gap = abs(res.difficulty - pref_diff)
            score += max(0, 3 - diff_gap * 0.5)

            # Learning style match (+2)
            style = user.profile.learning_style.value
            if style == "visual" and res.resource_type in ("mind_map", "article"):
                score += 2
            elif style == "interactive" and res.resource_type in ("quiz", "exercise", "code_example"):
                score += 2
            elif style == "textual" and res.resource_type in ("article", "summary", "study_guide"):
                score += 2

            # Error-prone areas match (+2)
            for area in user.profile.error_prone_areas:
                if area.lower() in res.title.lower():
                    score += 2

            # Past feedback (>80% score gets +1)
            if res.feedback_count > 0 and res.feedback_score / max(res.feedback_count, 1) > 0.8:
                score += 1

            # Variety bonus: prefer types user hasn't seen much of
            seen_types = [r.resource_type for r in resources[:top_k]]
            if res.resource_type not in seen_types:
                score += 0.5

            scored.append((score, res))

        scored.sort(key=lambda x: -x[0])
        return [r for _, r in scored[:top_k]]

    # ---- Knowledge graph operations ----

    def save_knowledge_graph(self, kg: KnowledgeGraph) -> None:
        self._knowledge_graphs[kg.name] = kg
        self._save_knowledge()

    def get_knowledge_graph(self, name: str) -> Optional[KnowledgeGraph]:
        return self._knowledge_graphs.get(name)

    # ---- Persistence ----

    def _load(self) -> None:
        _model_map = {
            USERS_FILE: ("_users", User),
            RESOURCES_FILE: ("_resources", LearningResource),
            KNOWLEDGE_FILE: ("_knowledge_graphs", KnowledgeGraph),
        }
        for path, (attr, model_cls) in _model_map.items():
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                if attr == "_users":
                    setattr(self, attr, {k: model_cls(**v) if isinstance(v, dict) else v for k, v in data.items()})
                elif attr == "_resources":
                    setattr(self, attr, {k: model_cls(**v) if isinstance(v, dict) else v for k, v in data.items()})
                elif attr == "_knowledge_graphs":
                    setattr(self, attr, {k: model_cls(**v) if isinstance(v, dict) else v for k, v in data.items()})
                else:
                    setattr(self, attr, data)

    def _serialize(self, obj: Any) -> Any:
        if isinstance(obj, (User, KnowledgeGraph, LearningResource)):
            return obj.model_dump()
        return str(obj)

    def _save_users(self) -> None:
        USERS_FILE.write_text(
            json.dumps(self._users, default=self._serialize, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _save_resources(self) -> None:
        RESOURCES_FILE.write_text(
            json.dumps(self._resources, default=self._serialize, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _save_knowledge(self) -> None:
        KNOWLEDGE_FILE.write_text(
            json.dumps(self._knowledge_graphs, default=self._serialize, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


memory_service = MemoryService()
from app.models.resource import LearningResource
from app.models.user import User
from app.models.knowledge import KnowledgeGraph
