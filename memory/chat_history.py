"""
chat_history.py
---------------
Persistent in-memory chat history for a support conversation.

Stores every (query, response, token_stats, metadata) turn so:
  1. The UI can render a full scrollable conversation history
  2. The orchestrator can include prior context in its prompts
  3. Token counts accumulate across turns and are visible in the UI

One ChatHistory object per customer_id — spans multiple sessions.
"""
from datetime import datetime
from typing import Dict, List, Optional
from monitoring.token_counter import token_stats, cumulative_stats


class ChatTurn:
    def __init__(
        self,
        session_id:   str,
        query:        str,
        response:     str,
        customer_id:  Optional[str],
        plan_used:    List[str],
        escalated:    bool,
        conflicts:    List[Dict],
        token_info:   Dict,
    ):
        self.session_id  = session_id
        self.query       = query
        self.response    = response
        self.customer_id = customer_id
        self.plan_used   = plan_used
        self.escalated   = escalated
        self.conflicts   = conflicts
        self.token_info  = token_info
        self.timestamp   = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "session_id":  self.session_id,
            "query":       self.query,
            "response":    self.response,
            "customer_id": self.customer_id,
            "plan_used":   self.plan_used,
            "escalated":   self.escalated,
            "conflicts":   self.conflicts,
            "token_info":  self.token_info,
            "timestamp":   self.timestamp,
        }


class ChatHistory:
    """
    Maintains the full conversation history for one customer (or anonymous).
    Key: customer_id (or "anonymous")
    """
    def __init__(self, customer_id: Optional[str] = None):
        self.customer_id = customer_id or "anonymous"
        self.turns: List[ChatTurn] = []

    def add_turn(
        self,
        session_id:  str,
        query:       str,
        response:    str,
        plan_used:   List[str],
        escalated:   bool       = False,
        conflicts:   List[Dict] = None,
    ) -> ChatTurn:
        stats = token_stats(query, response)
        turn  = ChatTurn(
            session_id=session_id, query=query, response=response,
            customer_id=self.customer_id, plan_used=plan_used,
            escalated=escalated, conflicts=conflicts or [],
            token_info=stats,
        )
        self.turns.append(turn)
        return turn

    def get_context_window(self, last_n: int = 5) -> List[Dict]:
        """
        Return last N turns as flat messages list for LLM context injection.
        Format: [{"role": "user"|"assistant", "content": "..."}]
        """
        messages = []
        for turn in self.turns[-last_n:]:
            messages.append({"role": "user",      "content": turn.query})
            messages.append({"role": "assistant",  "content": turn.response})
        return messages

    def get_all_turns(self) -> List[Dict]:
        return [t.to_dict() for t in self.turns]

    def get_token_summary(self) -> Dict:
        return cumulative_stats([t.token_info for t in self.turns])

    def clear(self):
        self.turns.clear()


# ── Global registry: customer_id → ChatHistory ───────────────
class ChatHistoryStore:
    def __init__(self):
        self._store: Dict[str, ChatHistory] = {}

    def get_or_create(self, customer_id: Optional[str]) -> ChatHistory:
        key = customer_id or "anonymous"
        if key not in self._store:
            self._store[key] = ChatHistory(customer_id=customer_id)
        return self._store[key]

    def get(self, customer_id: Optional[str]) -> Optional[ChatHistory]:
        return self._store.get(customer_id or "anonymous")

    def clear(self, customer_id: Optional[str]):
        key = customer_id or "anonymous"
        if key in self._store:
            self._store[key].clear()

    def all_histories(self) -> Dict:
        return {k: v.get_all_turns() for k, v in self._store.items()}


# Global singleton
chat_history_store = ChatHistoryStore()
