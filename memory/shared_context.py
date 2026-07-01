"""
shared_context.py
-----------------
Central shared memory that ALL agents read from and write to.
This is the single source of truth for the entire investigation.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


@dataclass
class AgentFinding:
    agent: str
    finding: str
    data: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: str = "high"   # high | medium | low


@dataclass
class Decision:
    decision_point: str
    choice: str
    reasoning: str
    made_by: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SharedContext:
    """
    Shared memory across all agents for one support session.
    Agents READ each other's findings and WRITE their own.
    """

    def __init__(self, session_id: str, customer_id: Optional[str] = None):
        self.session_id = session_id
        self.customer_id = customer_id
        self.query: str = ""
        self.conversation_history: List[Dict] = []
        self.agent_findings: List[AgentFinding] = []
        self.decisions: List[Decision] = []
        self.investigation_plan: List[str] = []
        self.completed_agents: List[str] = []
        self.failed_agents: List[str] = []
        self.conflicts: List[Dict] = []
        self.final_resolution: Optional[str] = None
        self.escalation_ticket: Optional[Dict] = None
        self.should_escalate: bool = False
        self.escalation_reason: Optional[str] = None
        self.metadata: Dict = {}

    # ── Write ──────────────────────────────────────────
    def add_finding(self, agent: str, finding: str, data: Any = None, confidence: str = "high"):
        self.agent_findings.append(
            AgentFinding(agent=agent, finding=finding, data=data, confidence=confidence)
        )

    def add_decision(self, decision_point: str, choice: str, reasoning: str, made_by: str):
        self.decisions.append(
            Decision(decision_point=decision_point, choice=choice, reasoning=reasoning, made_by=made_by)
        )

    def add_conflict(self, source_a: str, source_b: str, description: str, resolution: str = ""):
        self.conflicts.append({
            "source_a": source_a, "source_b": source_b,
            "description": description, "resolution": resolution,
            "timestamp": datetime.now().isoformat(),
        })

    def mark_agent_complete(self, agent: str):
        if agent not in self.completed_agents:
            self.completed_agents.append(agent)

    def mark_agent_failed(self, agent: str, reason: str):
        if agent not in self.failed_agents:
            self.failed_agents.append(agent)
        self.add_finding(agent=agent, finding=f"FAILED: {reason}", confidence="low")

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content, "ts": datetime.now().isoformat()})

    # ── Read ───────────────────────────────────────────
    def get_findings_by_agent(self, agent: str) -> List[AgentFinding]:
        return [f for f in self.agent_findings if f.agent == agent]

    def get_all_findings_text(self) -> str:
        lines = []
        for f in self.agent_findings:
            lines.append(f"[{f.agent}] {f.finding}")
        return "\n".join(lines) if lines else "No findings yet."

    def get_summary(self) -> Dict:
        return {
            "session_id": self.session_id,
            "customer_id": self.customer_id,
            "query": self.query,
            "completed_agents": self.completed_agents,
            "failed_agents": self.failed_agents,
            "findings_count": len(self.agent_findings),
            "decisions_count": len(self.decisions),
            "conflicts": self.conflicts,
            "should_escalate": self.should_escalate,
            "escalation_reason": self.escalation_reason,
            "final_resolution": self.final_resolution,
        }

    def to_json(self) -> str:
        d = self.get_summary()
        d["findings"] = [vars(f) for f in self.agent_findings]
        d["decisions"] = [vars(d2) for d2 in self.decisions]
        return json.dumps(d, indent=2, default=str)
