"""Redis-backed session service for distributed deployments."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RedisSessionService:
    """Manage sessions and conversation history in Redis."""

    def __init__(self, redis_url: str = "redis://localhost:6379", ttl_seconds: int = 86400):
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds
        self.redis = None

    async def initialize(self):
        """Connect to Redis on first use."""
        if self.redis is None:
            try:
                import redis.asyncio as redis
            except ImportError as exc:  # pragma: no cover - optional backend
                raise RuntimeError("redis package is required for RedisSessionService") from exc
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
        return self.redis

    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "app_name": app_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
            "context": metadata or {},
            "metadata": metadata or {},
        }
        await self.save_session(app_name, user_id, session_id, session_data)
        logger.info("Created Redis session %s for user %s", session_id, user_id)
        return session_data

    async def get_session(self, app_name: str, user_id: str, session_id: str) -> Dict[str, Any]:
        redis = await self.initialize()
        data = await redis.get(self._key(app_name, user_id, session_id))
        if not data:
            return await self.create_session(app_name, user_id, session_id)
        return json.loads(data)

    async def save_session(self, app_name: str, user_id: str, session_id: str, data: Dict[str, Any]) -> None:
        redis = await self.initialize()
        data["updated_at"] = datetime.now().isoformat()
        await redis.setex(self._key(app_name, user_id, session_id), self.ttl_seconds, json.dumps(data))

    async def update_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        session = await self.get_session(app_name, user_id, session_id)
        session.update(updates)
        await self.save_session(app_name, user_id, session_id, session)
        return session

    async def add_message(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        session = await self.get_session(app_name, user_id, session_id)
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        session.setdefault("messages", []).append(message)
        await self.save_session(app_name, user_id, session_id, session)
        return message

    async def get_messages(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        session = await self.get_session(app_name, user_id, session_id)
        messages = session.get("messages", [])
        return messages[-limit:] if limit else messages

    async def delete_session(self, app_name: str, user_id: str, session_id: str) -> bool:
        redis = await self.initialize()
        deleted = await redis.delete(self._key(app_name, user_id, session_id))
        return bool(deleted)

    async def list_sessions(self, app_name: str, user_id: str) -> List[Dict[str, Any]]:
        redis = await self.initialize()
        keys = await redis.keys(self._key(app_name, user_id, "*"))
        sessions = []
        for key in keys:
            data = await redis.get(key)
            if data:
                sessions.append(json.loads(data))
        return sorted(sessions, key=lambda s: s.get("updated_at", ""), reverse=True)

    async def update_context(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        context_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        session = await self.get_session(app_name, user_id, session_id)
        session.setdefault("context", {}).update(context_updates)
        await self.save_session(app_name, user_id, session_id, session)
        return session["context"]

    async def get_context(self, app_name: str, user_id: str, session_id: str) -> Dict[str, Any]:
        session = await self.get_session(app_name, user_id, session_id)
        return session.get("context", {})

    def _key(self, app_name: str, user_id: str, session_id: str) -> str:
        return f"{app_name}:{user_id}:{session_id}"
