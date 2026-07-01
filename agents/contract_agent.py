"""
contract_agent.py — SLA validation, contract review, entitlement check.
"""
import json
import re
from typing import Dict
from agents.base_agent import BaseAgent
from memory.shared_context import SharedContext
from tools.contract_tools import ContractTools
from monitoring.tracing_utils import log_finding, log_decision

SYSTEM_PROMPT = """You are the Contract Agent for TechCorp's support system.
Review contract terms and determine if any violations have occurred.

Given contract data and the customer's issue:
1. State what the contract guarantees (SLA hours, features, seats).
2. Determine if any SLA violation occurred and its severity.
3. Identify mismatches between entitlements and what the customer has.
4. Recommend escalation if a violation is confirmed.

Respond ONLY with a JSON object — no markdown, no extra text:
{
  "contract_id": "...",
  "sla_hours": 4,
  "sla_violated": true/false,
  "hours_elapsed": 10.5,
  "violation_severity": "critical|high|medium|none",
  "contract_features": ["list"],
  "special_terms": "or null",
  "escalation_recommended": true/false,
  "escalation_reason": "reason or null",
  "summary": "one paragraph summary",
  "confidence": "high|medium|low"
}"""


class ContractAgent(BaseAgent):
    name = "ContractAgent"
    role_description = "Reviews contracts, SLA compliance, and entitlements"

    def __init__(self):
        self.tools = ContractTools()

    def _execute(self, ctx: SharedContext, issue_date: str = None, **kwargs) -> Dict:
        contract_id = ctx.metadata.get("contract_id")
        if not contract_id:
            ctx.add_finding(self.name, "No contract_id in context — skipping contract review")
            return {"agent": self.name, "success": False, "output": "No contract ID available."}

        contract  = self._safe_tool_call(self.tools.lookup_contract,       contract_id, fallback={})
        terms     = self._safe_tool_call(self.tools.get_contract_terms,    contract_id, fallback={})
        features  = self._safe_tool_call(self.tools.get_included_features, contract_id, fallback=[])
        sla_check = {}
        if issue_date:
            sla_check = self._safe_tool_call(
                self.tools.validate_sla_compliance, contract_id, issue_date, fallback={}
            ) or {}

        user_msg = (
            f"Customer Query: {ctx.query}\n\n"
            f"Contract:\n{json.dumps(contract, indent=2)}\n\n"
            f"Terms:\n{json.dumps(terms, indent=2)}\n\n"
            f"Included Features:\n{json.dumps(features, indent=2)}\n\n"
            f"SLA Check:\n{json.dumps(sla_check, indent=2)}\n\n"
            f"Previous Findings:\n{ctx.get_all_findings_text()}\n\n"
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
        summary    = parsed.get("summary", "Contract reviewed.")
        log_finding(self.name, summary, confidence)

        ctx.add_finding(
            agent=self.name, finding=summary,
            data={"contract": contract, "sla_check": sla_check, "llm": parsed},
            confidence=confidence,
        )
        if parsed.get("escalation_recommended"):
            ctx.should_escalate   = True
            ctx.escalation_reason = parsed.get("escalation_reason", "Contract violation detected.")
            log_decision(
                "escalation_trigger", "escalate",
                ctx.escalation_reason, self.name,
            )
            ctx.add_decision(
                decision_point="escalation_trigger",
                choice="escalate",
                reasoning=ctx.escalation_reason,
                made_by=self.name,
            )
        return {"agent": self.name, "success": True, "output": summary, "data": parsed}
