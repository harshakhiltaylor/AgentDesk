"""
orchestrator.py
---------------
The brain of AgentDesk. Plans the investigation, routes agents,
detects conflicts, and synthesizes the final customer response.
All actions are traced to the terminal in real time.
"""
import json
import re
import time
import logging
from typing import Dict, List

from memory.shared_context import SharedContext
from agents.base_agent import _client, MODEL
from agents.account_agent   import AccountAgent
from agents.feature_agent   import FeatureAgent
from agents.contract_agent  import ContractAgent
from agents.escalation_agent import EscalationAgent
from memory.chat_history import chat_history_store
from monitoring.tracing_utils import (
    log_session_start, log_plan, log_decision,
    log_conflict, log_session_end, log_llm_call, log_event,
)

logger = logging.getLogger("agentdesk.orchestrator")

# ─────────────────────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────────────────────

PLAN_SYSTEM = """You are the Orchestrator for TechCorp's multi-agent customer support system.
Your ONLY job right now is to analyze the customer query and produce an investigation plan.

Available agents:
- AccountAgent: use when plan, billing, seat count, or account status matters
- FeatureAgent: use when feature availability, setup, or limits are asked about
- ContractAgent: use when SLA, contract terms, entitlements, or violations are involved
- EscalationAgent: ALWAYS include last — it makes the final decision

Rules:
- Always include EscalationAgent at the end
- Pure feature question (e.g. dark mode setup): [FeatureAgent, EscalationAgent]
- Account/plan info needed: start with AccountAgent
- SLA or contract mentioned: include ContractAgent
- Extract any feature keyword for FeatureAgent
- If SLA is mentioned and no date given, use "2024-03-01T09:00:00" as default issue_date

Respond ONLY with a JSON object — no extra text, no markdown:
{
  "complexity": "low|medium|high",
  "domains": ["list of domains"],
  "plan": ["AccountAgent", "FeatureAgent", "EscalationAgent"],
  "reasoning": "why this plan in one sentence",
  "feature_hint": "feature keyword or null",
  "issue_date": "ISO datetime or null"
}"""

SYNTHESIS_SYSTEM = """You are the Orchestrator synthesizing a final customer support response.

You have received findings from multiple specialized agents. Your job:
1. Combine all findings into a clear, helpful, customer-facing response.
2. Resolve conflicts intelligently — always trust live system data over documentation.
3. Provide concrete actionable next steps.
4. If escalation occurred, mention the ticket ID.
5. Be warm, professional, and direct. Do NOT expose internal agent names.

Write the response the customer will actually read. Be concise but complete."""


class OrchestratorAgent:

    def __init__(self):
        self.account_agent    = AccountAgent()
        self.feature_agent    = FeatureAgent()
        self.contract_agent   = ContractAgent()
        self.escalation_agent = EscalationAgent()
        self._agent_map = {
            "AccountAgent":    self.account_agent,
            "FeatureAgent":    self.feature_agent,
            "ContractAgent":   self.contract_agent,
            "EscalationAgent": self.escalation_agent,
        }

    def handle(self, ctx: SharedContext) -> Dict:
        t_start = time.time()

        # ── Step 1: Announce session ───────────────────
        log_session_start(ctx.session_id, ctx.query, ctx.customer_id)

        # this where we are using the history and memory to inject prior context into the SharedContext for agents to read. 
        # We also log this as an event so it shows up in the trace  
        # and we can measure its impact in future iterations when we add more sophisticated memory retrieval

        # ── Step 1b: Inject prior conversation context ─
        # Pull last 3 turns from chat history so agents know what was discussed
        prior_history = chat_history_store.get(ctx.customer_id)
        if prior_history and prior_history.turns:
            last_turns = prior_history.get_context_window(last_n=3)
            
            # Summarise prior context into SharedContext so all agents can read it
            
            prior_summary_lines = []
            for t in prior_history.turns[-3:]:
                prior_summary_lines.append(f"Q: {t.query[:120]}")
                prior_summary_lines.append(f"A: {t.response[:200]}")
            ctx.metadata["prior_context"] = "\n".join(prior_summary_lines)
            ctx.metadata["has_prior_context"] = True
        else:
            ctx.metadata["prior_context"] = ""
            ctx.metadata["has_prior_context"] = False

        # ── Step 2: Build plan ─────────────────────────
        plan_data      = self._build_plan(ctx)
        agent_sequence = plan_data.get("plan", ["EscalationAgent"])
        feature_hint   = plan_data.get("feature_hint")
        issue_date     = plan_data.get("issue_date")
        complexity     = plan_data.get("complexity", "medium")

        ctx.investigation_plan = agent_sequence
        log_plan(agent_sequence, plan_data.get("reasoning", ""), complexity)

        ctx.add_decision(
            decision_point="investigation_plan",
            choice=str(agent_sequence),
            reasoning=plan_data.get("reasoning", ""),
            made_by="OrchestratorAgent",
        )
        log_decision(
            "investigation_plan",
            " → ".join(agent_sequence),
            plan_data.get("reasoning", ""),
            "OrchestratorAgent",
        )

        # ── Step 3: Run agents ─────────────────────────
        agent_results = {}
        for agent_name in agent_sequence:
            agent = self._agent_map.get(agent_name)
            if not agent:
                logger.warning(f"Unknown agent: {agent_name}")
                continue

            kwargs = {}
            if agent_name == "FeatureAgent"  and feature_hint: kwargs["feature_hint"] = feature_hint
            if agent_name == "ContractAgent" and issue_date:    kwargs["issue_date"]   = issue_date

            result = agent.run(ctx, **kwargs)
            agent_results[agent_name] = result

            # Adaptive: suspended account → force escalation
            if agent_name == "AccountAgent":
                if ctx.metadata.get("account_status") == "suspended":
                    ctx.should_escalate  = True
                    ctx.escalation_reason = "Account is suspended — requires Account Management review."
                    log_decision(
                        "adaptive_routing", "force_escalate",
                        "Account status is suspended", "OrchestratorAgent",
                    )

        # ── Step 4: Surface conflicts ──────────────────
        for conflict in ctx.conflicts:
            log_conflict(
                conflict["source_a"], conflict["source_b"],
                conflict["description"], conflict.get("resolution", ""),
            )
        if ctx.conflicts:
            ctx.add_decision(
                decision_point="conflict_resolution",
                choice="trust_system_data",
                reasoning="Live system data always takes precedence over documentation.",
                made_by="OrchestratorAgent",
            )

        # ── Step 5: Synthesize response ────────────────
        final_response = self._synthesize(ctx, agent_results)
        ctx.final_resolution = final_response
        ctx.add_message("assistant", final_response)

        elapsed = round(time.time() - t_start, 2)
        log_session_end(
            ctx.session_id, elapsed,
            ctx.should_escalate, len(ctx.conflicts),
        )

        return {
            "session_id":        ctx.session_id,
            "response":          final_response,
            "plan":              agent_sequence,
            "plan_reasoning":    plan_data.get("reasoning", ""),
            "complexity":        complexity,
            "escalated":         ctx.should_escalate,
            "escalation_ticket": ctx.escalation_ticket,
            "conflicts":         ctx.conflicts,
            "findings":          [vars(f) for f in ctx.agent_findings],
            "decisions":         [vars(d) for d in ctx.decisions],
        }

    # ─────────────────────────────────────────────────────────
    # PRIVATE
    # ─────────────────────────────────────────────────────────

    def _build_plan(self, ctx: SharedContext) -> Dict:
        prior = ctx.metadata.get("prior_context", "")
        prior_block = f"\nPrior conversation context (last 3 turns):\n{prior}\n" if prior else ""
        user_msg = (
            f"Customer Query: {ctx.query}\n"
            f"Customer ID (if known): {ctx.customer_id or 'not provided'}"
            f"{prior_block}\n"
            f"Build the investigation plan."
        )
        t0 = time.time()
        try:
            resp = _client.chat.completions.create(
                model=MODEL,
                max_tokens=400,
                messages=[
                    {"role": "system", "content": PLAN_SYSTEM},
                    {"role": "user",   "content": user_msg},
                ],
            )
            latency_ms = (time.time() - t0) * 1000
            usage = getattr(resp, "usage", None)
            log_llm_call(
                agent="OrchestratorAgent[plan]",
                tokens_in=getattr(usage, "prompt_tokens", 0),
                tokens_out=getattr(usage, "completion_tokens", 0),
                latency_ms=latency_ms,
            )
            raw = resp.choices[0].message.content
            # Strip markdown fences if model wraps output
            raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
            try:
                return json.loads(raw)
            except Exception:
                m = re.search(r'\{.*\}', raw, re.DOTALL)
                return json.loads(m.group()) if m else self._fallback_plan(ctx)
        except Exception as e:
            logger.error(f"Plan generation failed: {e}")
            return self._fallback_plan(ctx)

    def _fallback_plan(self, ctx: SharedContext) -> Dict:
        """Keyword-based fallback when LLM planning fails."""
        q = ctx.query.lower()
        plan = []
        if ctx.customer_id:                                                     plan.append("AccountAgent")
        if any(w in q for w in ["feature","dark","api","analytic","sso","webhook"]): plan.append("FeatureAgent")
        if any(w in q for w in ["sla","contract","violation","days","escalate"]): plan.append("ContractAgent")
        plan.append("EscalationAgent")
        return {
            "plan": plan, "complexity": "medium",
            "reasoning": "Fallback plan via keyword detection (LLM plan call failed).",
            "feature_hint": None, "issue_date": None,
        }

    def _synthesize(self, ctx: SharedContext, agent_results: Dict) -> str:
        findings_text  = ctx.get_all_findings_text()
        conflicts_text = json.dumps(ctx.conflicts, indent=2) if ctx.conflicts else "None"
        ticket_info    = (
            f"Escalation ticket created: {ctx.escalation_ticket['ticket_id']}"
            if ctx.escalation_ticket else "No escalation ticket."
        )
        prior = ctx.metadata.get("prior_context", "")
        prior_block = f"Prior conversation context:\n{prior}\n\n" if prior else ""
        user_msg = (
            f"{prior_block}"
            f"Current Query: {ctx.query}\n\n"
            f"Agent Findings:\n{findings_text}\n\n"
            f"Conflicts Detected & Resolved:\n{conflicts_text}\n\n"
            f"Escalation: {'YES — ' + (ctx.escalation_reason or '') if ctx.should_escalate else 'NO'}\n"
            f"{ticket_info}\n\n"
            f"Write the final customer-facing response. If this is a follow-up question, "
            f"acknowledge the conversation context naturally."
        )
        t0 = time.time()
        try:
            resp = _client.chat.completions.create(
                model=MODEL,
                max_tokens=800,
                messages=[
                    {"role": "system", "content": SYNTHESIS_SYSTEM},
                    {"role": "user",   "content": user_msg},
                ],
            )
            latency_ms = (time.time() - t0) * 1000
            usage = getattr(resp, "usage", None)
            log_llm_call(
                agent="OrchestratorAgent[synthesis]",
                tokens_in=getattr(usage, "prompt_tokens", 0),
                tokens_out=getattr(usage, "completion_tokens", 0),
                latency_ms=latency_ms,
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return "We've investigated your query and our team will follow up shortly."
