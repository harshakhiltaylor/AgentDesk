"""
escalation_agent.py — Final escalation decision, ticket creation, routing.
"""
import json
import re
from typing import Dict
from agents.base_agent import BaseAgent
from memory.shared_context import SharedContext
from tools.escalation_tools import EscalationTools
from monitoring.tracing_utils import log_finding, log_escalation, log_decision

SYSTEM_PROMPT = """You are the Escalation Agent for AgentDesk's support system.
Make the final escalation decision with clear reasoning.

Review all prior agent findings and determine:
1. Does this issue need human intervention? (yes/no)
2. If yes: priority (P1/P2/P3), team, and why?
3. What is the customer-facing explanation?

Escalation triggers:
- SLA violation confirmed → always escalate (P1)
- Account suspended unexpectedly → P1
- Confirmed product bug → P2 Engineering
- Billing dispute → P2 Finance
- Onboarding 15+ users → P2 Onboarding
- Revenue impact + urgent tone → P1
- Simple feature questions → NO escalation

Respond ONLY with a JSON object — no markdown, no extra text:
{
  "should_escalate": true/false,
  "priority": "P1|P2|P3|null",
  "team": "team name or null",
  "issue_type": "sla_violation|technical_bug|billing_dispute|onboarding|general_inquiry|...",
  "reason": "detailed reason",
  "customer_message": "what to tell the customer",
  "confidence": "high|medium|low"
}"""


class EscalationAgent(BaseAgent):
    name = "EscalationAgent"
    role_description = "Decides escalation, creates tickets, routes to human teams"

    def __init__(self):
        self.tools = EscalationTools()

    def _execute(self, ctx: SharedContext, **kwargs) -> Dict:
        user_msg = (
            f"Customer Query: {ctx.query}\n\n"
            f"All Agent Findings:\n{ctx.get_all_findings_text()}\n\n"
            f"Conflicts:\n{json.dumps(ctx.conflicts, indent=2) if ctx.conflicts else 'None'}\n\n"
            f"Prior Decisions:\n{json.dumps([vars(d) for d in ctx.decisions], indent=2, default=str)}\n\n"
            f"Context signal — should_escalate: {ctx.should_escalate}\n"
            f"Context signal — escalation_reason: {ctx.escalation_reason or 'None'}\n\n"
            f"Make the final escalation decision and respond with the JSON format specified."
        )
        raw = self._call_llm(SYSTEM_PROMPT, user_msg)
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        try:
            parsed = json.loads(raw)
        except Exception:
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            parsed = json.loads(m.group()) if m else {"should_escalate": False, "customer_message": raw}

        ticket_data = None

        if parsed.get("should_escalate"):
            issue_type = parsed.get("issue_type", "general_inquiry")
            routing    = self._safe_tool_call(
                self.tools.get_escalation_routing, issue_type,
                fallback={"team": "Support", "priority": "P2"}
            ) or {}
            ticket = self._safe_tool_call(
                self.tools.create_escalation_ticket,
                parsed.get("reason", "Escalation required"),
                parsed.get("priority", routing.get("priority", "P2")),
                {"session_id": ctx.session_id, "customer_id": ctx.customer_id, "query": ctx.query},
                fallback=None,
            )
            if ticket:
                ticket_data      = ticket
                ctx.escalation_ticket = ticket
                self._safe_tool_call(self.tools.notify_support_team, ticket["ticket_id"], fallback=None)
                self._safe_tool_call(
                    self.tools.log_escalation_reason,
                    ticket["ticket_id"], parsed.get("reason", ""), fallback=None,
                )
                log_escalation(
                    ticket["ticket_id"],
                    parsed.get("priority", "P2"),
                    parsed.get("reason", ""),
                    routing.get("team", "Support"),
                )

        confidence = parsed.get("confidence", "high")
        decision   = "ESCALATE" if parsed.get("should_escalate") else "RESOLVE (no escalation)"
        log_finding(self.name, f"Final decision: {decision}. {parsed.get('reason','')}", confidence)
        log_decision(
            "final_escalation",
            "escalate" if parsed.get("should_escalate") else "resolve",
            parsed.get("reason", ""),
            self.name,
        )

        ctx.add_finding(
            agent=self.name,
            finding=f"Decision: {decision}. {parsed.get('reason','')}",
            data={"decision": parsed, "ticket": ticket_data},
            confidence=confidence,
        )
        ctx.add_decision(
            decision_point="final_escalation",
            choice="escalate" if parsed.get("should_escalate") else "resolve",
            reasoning=parsed.get("reason", ""),
            made_by=self.name,
        )
        return {
            "agent": self.name, "success": True,
            "output": parsed.get("customer_message", ""),
            "data": parsed, "ticket": ticket_data,
        }
