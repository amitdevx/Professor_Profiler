"""In-memory session service with state management."""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


logger = logging.getLogger(__name__)


class InMemorySessionService:
    """Manage sessions and conversation history in memory."""

    def __init__(self):
        # sessions: {app_name: {user_id: {session_id: session_data}}}
        self._sessions: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = defaultdict(
            lambda: defaultdict(dict)
        )

    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new session."""
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "app_name": app_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
            "context": metadata or {},
            "metadata": metadata or {}
        }

        self._sessions[app_name][user_id][session_id] = session_data
        logger.info(f"Created session {session_id} for user {user_id}")

        return session_data

    async def get_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get session by ID, create if not exists."""
        if session_id not in self._sessions[app_name][user_id]:
            logger.info(f"Session {session_id} not found, creating new one")
            return await self.create_session(app_name, user_id, session_id)

        return self._sessions[app_name][user_id][session_id]

    async def update_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update session data."""
        if session_id not in self._sessions[app_name][user_id]:
            raise ValueError(f"Session {session_id} not found")

        session = self._sessions[app_name][user_id][session_id]
        session.update(updates)
        session["updated_at"] = datetime.now().isoformat()

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
        """Add a message to session history."""
        session = await self.get_session(app_name, user_id, session_id)

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        session["messages"].append(message)
        session["updated_at"] = datetime.now().isoformat()

        logger.debug(f"Added {role} message to session {session_id}")

        return message

    async def get_messages(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        session = await self.get_session(app_name, user_id, session_id)

        if not session:
            return []

        messages = session.get("messages", [])

        if limit:
            return messages[-limit:]

        return messages

    async def delete_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str
    ) -> bool:
        """Delete a session."""
        if session_id in self._sessions[app_name][user_id]:
            del self._sessions[app_name][user_id][session_id]
            logger.info(f"Deleted session {session_id}")
            return True

        return False

    async def list_sessions(
        self,
        app_name: str,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """List all sessions for a user."""
        sessions = list(self._sessions[app_name][user_id].values())
        return sorted(sessions, key=lambda s: s["updated_at"], reverse=True)

    async def update_context(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        context_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update session context (for memory/state management)."""
        session = await self.get_session(app_name, user_id, session_id)

        if "context" not in session:
            session["context"] = {}

        session["context"].update(context_updates)
        session["updated_at"] = datetime.now().isoformat()

        return session["context"]

    async def get_context(
        self,
        app_name: str,
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Get session context."""
        session = await self.get_session(app_name, user_id, session_id)
        return session.get("context", {}) if session else {}

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        total_sessions = sum(
            len(users_sessions)
            for app in self._sessions.values()
            for users_sessions in app.values()
        )

        total_messages = sum(
            len(session.get("messages", []))
            for app in self._sessions.values()
            for users_sessions in app.values()
            for session in users_sessions.values()
        )

        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "apps": list(self._sessions.keys())
        }
