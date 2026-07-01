"""
account_agent.py — Investigates customer account, plan, billing, seats.
"""
import json
import re
from typing import Dict
from agents.base_agent import BaseAgent
from memory.shared_context import SharedContext
from tools.account_tools import AccountTools
from monitoring.tracing_utils import log_finding

SYSTEM_PROMPT = """You are the Account Agent for TechCorp's support system.
Analyze customer account data and produce a clear structured finding.

Given the raw account data:
1. Summarize the customer's current plan, status, and seat usage.
2. Flag anomalies (overage, suspension, billing failures).
3. State what this means for their support query.

Respond ONLY with a JSON object — no markdown, no extra text:
{
  "summary": "one-paragraph summary",
  "plan": "starter|pro|enterprise",
  "status": "active|suspended|...",
  "anomalies": ["list or empty"],
  "relevant_to_query": "how account data relates to the query",
  "confidence": "high|medium|low"
}"""


class AccountAgent(BaseAgent):
    name = "AccountAgent"
    role_description = "Investigates customer account, plan, billing, and seat details"

    def __init__(self):
        self.tools = AccountTools()

    def _execute(self, ctx: SharedContext, **kwargs) -> Dict:
        cid = ctx.customer_id
        if not cid:
            ctx.add_finding(self.name, "No customer_id — skipping account lookup")
            return {"agent": self.name, "success": False, "output": "No customer_id provided."}

        customer = self._safe_tool_call(self.tools.lookup_customer,       cid, fallback={})
        billing  = self._safe_tool_call(self.tools.get_billing_history,   cid, fallback=[])
        status   = self._safe_tool_call(self.tools.check_account_status,  cid, fallback={})
        features = self._safe_tool_call(self.tools.list_enabled_features, cid, fallback=[])

        user_msg = (
            f"Customer Query: {ctx.query}\n\n"
            f"Account Data:\n{json.dumps(customer, indent=2)}\n\n"
            f"Status:\n{json.dumps(status, indent=2)}\n\n"
            f"Enabled Features:\n{json.dumps(features, indent=2)}\n\n"
            f"Recent Billing:\n{json.dumps(billing[:3], indent=2)}\n\n"
            f"Analyze and respond with the JSON format specified."
        )
        raw = self._call_llm(SYSTEM_PROMPT, user_msg)
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        try:
            parsed = json.loads(raw)
        except Exception:
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            parsed = json.loads(m.group()) if m else {"summary": raw, "confidence": "low"}

        confidence = parsed.get("confidence", "high")
        summary    = parsed.get("summary", "Account data gathered.")
        log_finding(self.name, summary, confidence)

        ctx.add_finding(
            agent=self.name, finding=summary,
            data={"customer": customer, "status": status,
                  "features": features, "billing": billing[:3], "llm": parsed},
            confidence=confidence,
        )
        ctx.metadata["customer_plan"]  = parsed.get("plan",   customer.get("plan",   "unknown"))
        ctx.metadata["account_status"] = parsed.get("status", status.get("status",   "unknown"))
        ctx.metadata["contract_id"]    = customer.get("contract_id")
        ctx.metadata["customer_name"]  = customer.get("name", "Unknown")

        return {"agent": self.name, "success": True, "output": summary, "data": parsed}
