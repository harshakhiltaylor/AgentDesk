"""
state_manager.py
----------------
Manages multiple SharedContext sessions.
Provides session lifecycle, retrieval, and cleanup.
"""
import uuid
from typing import Dict, Optional
from memory.shared_context import SharedContext


class StateManager:
    """Singleton-like store of all active support sessions."""

    def __init__(self):
        self._sessions: Dict[str, SharedContext] = {}

    def create_session(self, customer_id: Optional[str] = None) -> SharedContext:
        session_id = f"SIQ-{uuid.uuid4().hex[:8].upper()}"
        ctx = SharedContext(session_id=session_id, customer_id=customer_id)
        self._sessions[session_id] = ctx
        return ctx

    def get_session(self, session_id: str) -> Optional[SharedContext]:
        return self._sessions.get(session_id)

    def all_sessions(self) -> Dict[str, SharedContext]:
        return dict(self._sessions)

    def delete_session(self, session_id: str):
        self._sessions.pop(session_id, None)


# Global singleton used by Flask app and agents
state_manager = StateManager()
