"""
feature_agent.py — Feature availability, docs, limits, conflict detection.
"""
import json
import re
from typing import Dict
from agents.base_agent import BaseAgent
from memory.shared_context import SharedContext
from tools.feature_tools import FeatureTools
from monitoring.tracing_utils import log_finding

SYSTEM_PROMPT = """You are the Feature Agent for TechCorp's support system.
Investigate feature availability and provide accurate documentation.

Given feature data and the customer's plan:
1. Confirm whether the feature is available on their plan.
2. If available: provide setup instructions.
3. If not available: explain what plan they need.
4. Flag conflicts between documentation and actual limits.
5. Mention any rate limits or caps.

Respond ONLY with a JSON object — no markdown, no extra text:
{
  "feature_available": true/false,
  "feature_name": "name",
  "current_plan": "plan",
  "required_plan": "plan needed or null",
  "setup_instructions": "steps or null",
  "limits": "any limits or null",
  "documentation_note": "conflicts or important notes",
  "summary": "one paragraph summary",
  "confidence": "high|medium|low"
}"""


class FeatureAgent(BaseAgent):
    name = "FeatureAgent"
    role_description = "Checks feature availability, documentation, and limits"

    def __init__(self):
        self.tools = FeatureTools()

    def _execute(self, ctx: SharedContext, feature_hint: str = None, **kwargs) -> Dict:
        plan    = ctx.metadata.get("customer_plan", "starter")
        feature = feature_hint or self._extract_feature(ctx.query)

        matrix = self._safe_tool_call(self.tools.get_feature_matrix, fallback={})
        doc    = self._safe_tool_call(self.tools.get_feature_documentation, feature, fallback={}) if feature else {}
        config = self._safe_tool_call(self.tools.validate_configuration, feature, plan, fallback={}) if feature else {}
        limits = self._safe_tool_call(self.tools.check_feature_limits, feature, plan, fallback={}) if feature else {}

        user_msg = (
            f"Customer Query: {ctx.query}\n\n"
            f"Customer Plan: {plan}\n"
            f"Feature: {feature or 'auto-detect'}\n\n"
            f"Feature Matrix for {plan}:\n{json.dumps(matrix.get(plan, {}), indent=2)}\n\n"
            f"Documentation:\n{json.dumps(doc, indent=2)}\n\n"
            f"Config Validation:\n{json.dumps(config, indent=2)}\n\n"
            f"Limits:\n{json.dumps(limits, indent=2)}\n\n"
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

        # Conflict: docs say unlimited, matrix says 1000
        if feature == "api_access" and plan == "pro":
            note = doc.get("note", "") if isinstance(doc, dict) else ""
            if "1,000" in note:
                ctx.add_conflict(
                    source_a="marketing_documentation",
                    source_b="feature_matrix_database",
                    description="Marketing docs claim 'unlimited API calls' for Pro plan — actual limit is 1,000/month.",
                    resolution="Feature matrix (live system data) is authoritative. Documentation is outdated.",
                )

        confidence = parsed.get("confidence", "high")
        summary    = parsed.get("summary", "Feature investigation complete.")
        log_finding(self.name, summary, confidence)

        ctx.add_finding(
            agent=self.name, finding=summary,
            data={"feature": feature, "plan": plan, "llm": parsed},
            confidence=confidence,
        )
        return {"agent": self.name, "success": True, "output": summary, "data": parsed}

    def _extract_feature(self, query: str) -> str:
        q = query.lower()
        if "dark mode" in q:          return "dark_mode"
        if "api" in q:                return "api_access"
        if "analytic" in q:           return "advanced_analytics"
        if "sso" in q or "sign-on" in q: return "sso"
        if "webhook" in q:            return "webhooks"
        return "basic_dashboard"
