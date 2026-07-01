"""
escalation_tools.py
-------------------
Mock tools for the Escalation Agent.
"""
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from tools.tool_base import BaseTool, ToolResult

# In-memory store for created tickets (simulates DB)
ESCALATION_TICKETS = {}

ROUTING_TABLE = {
    "sla_violation":      {"team": "Customer Success", "priority": "P1"},
    "billing_dispute":    {"team": "Finance",           "priority": "P2"},
    "technical_bug":      {"team": "Engineering",       "priority": "P2"},
    "account_suspension": {"team": "Account Management","priority": "P1"},
    "feature_request":    {"team": "Product",           "priority": "P3"},
    "general_inquiry":    {"team": "Support Tier 1",    "priority": "P3"},
    "onboarding":         {"team": "Onboarding",        "priority": "P2"},
    "default":            {"team": "Support Tier 2",    "priority": "P2"},
}


class EscalationTools(BaseTool):

    def create_escalation_ticket(self, reason: str, priority: str, context: dict) -> ToolResult:
        def _inner():
            ticket_id = f"ESC-{uuid.uuid4().hex[:6].upper()}"
            ticket = {
                "ticket_id": ticket_id,
                "reason": reason,
                "priority": priority,
                "context": context,
                "created_at": datetime.now().isoformat(),
                "status": "open",
            }
            ESCALATION_TICKETS[ticket_id] = ticket
            return ticket
        return self._call("create_escalation_ticket", _inner)

    def get_escalation_routing(self, issue_type: str) -> ToolResult:
        def _inner():
            route = ROUTING_TABLE.get(issue_type, ROUTING_TABLE["default"])
            return {"issue_type": issue_type, **route}
        return self._call("get_escalation_routing", _inner)

    def notify_support_team(self, ticket_id: str) -> ToolResult:
        def _inner():
            ticket = ESCALATION_TICKETS.get(ticket_id)
            if not ticket:
                raise ValueError(f"Ticket {ticket_id} not found")
            # Simulate notification
            return {"notified": True, "ticket_id": ticket_id, "channel": "slack+email"}
        return self._call("notify_support_team", _inner)

    def log_escalation_reason(self, ticket_id: str, reason: str) -> ToolResult:
        def _inner():
            ticket = ESCALATION_TICKETS.get(ticket_id)
            if not ticket:
                raise ValueError(f"Ticket {ticket_id} not found")
            ticket["logged_reason"] = reason
            return {"logged": True, "ticket_id": ticket_id}
        return self._call("log_escalation_reason", _inner)
