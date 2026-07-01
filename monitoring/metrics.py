"""
metrics.py — Custom metrics and performance tracking for AgentDesk
"""

from datetime import datetime
from typing import Dict, List
import time


class SessionMetrics:
    """Tracks per-session performance metrics."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = time.time()
        self.agent_timings: Dict[str, float] = {}
        self.tool_call_count: int = 0
        self.tool_failure_count: int = 0
        self.conflict_count: int = 0
        self.escalation_triggered: bool = False
        self.total_tokens_estimate: int = 0

    def record_agent_time(self, agent_name: str, elapsed_seconds: float):
        self.agent_timings[agent_name] = round(elapsed_seconds, 2)

    def record_tool_call(self, success: bool):
        self.tool_call_count += 1
        if not success:
            self.tool_failure_count += 1

    def record_conflict(self):
        self.conflict_count += 1

    def total_elapsed(self) -> float:
        return round(time.time() - self.start_time, 2)

    def tool_success_rate(self) -> float:
        if self.tool_call_count == 0:
            return 1.0
        return round((self.tool_call_count - self.tool_failure_count) / self.tool_call_count, 2)

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "total_elapsed_seconds": self.total_elapsed(),
            "agent_timings": self.agent_timings,
            "tool_calls_total": self.tool_call_count,
            "tool_failures": self.tool_failure_count,
            "tool_success_rate": self.tool_success_rate(),
            "conflicts_detected": self.conflict_count,
            "escalation_triggered": self.escalation_triggered,
        }
