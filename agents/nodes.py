"""
nodes.py
--------
All LangGraph nodes for AgentDesk — Dynamic Routing Loop architecture.

Flow per investigation:
  Orchestrator → [any agent] → Orchestrator → [any agent] → ... → Escalation → Synthesis

The Orchestrator is the ONLY decision-maker. It is called:
  - At the very start (no findings yet) → picks first agent based on query
  - After every specialist agent → re-evaluates, picks next agent
  - Until it decides "escalation" → investigation ends

No agent order is hardcoded. The Orchestrator reasons dynamically.
"""
import json
import re
import time
from datetime import datetime

from memory.graph_state import SupportState
from agents.llm_client import chat
from tools.account_tools    import AccountTools
from tools.feature_tools    import FeatureTools
from tools.contract_tools   import ContractTools
from tools.escalation_tools import EscalationTools
import monitoring.tracer as T

_account_tools    = AccountTools()
_feature_tools    = FeatureTools()
_contract_tools   = ContractTools()
_escalation_tools = EscalationTools()


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _safe(session_id: str, agent: str, tool_fn, *args, fallback=None):
    t0 = time.time()
    r  = tool_fn(*args)
    ms = (time.time() - t0) * 1000
    T.tool_call(session_id, agent, r.tool_name, r.success,
                str(r.data)[:60] if r.success else (r.error or ""), ms)
    return r.data if r.success else fallback


def _parse_json(raw: str) -> dict:
    if not raw:
        return {}
    clean = re.sub(r"```(?:json|JSON)?", "", raw).strip().strip("`").strip()
    try:
        return json.loads(clean)
    except Exception:
        pass
    for start_match in re.finditer(r'\{', clean):
        start = start_match.start()
        depth = 0
        for i, ch in enumerate(clean[start:], start):
            if ch == '{':   depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    try:    return json.loads(clean[start:i+1])
                    except: break
    return {"summary": raw[:500], "confidence": "low"}


def _fmt(data) -> str:
    if data is None:                    return "Not available"
    if isinstance(data, (dict, list)):  return json.dumps(data, indent=2)
    return str(data)


def _finding(agent: str, summary: str, data: dict, confidence: str) -> dict:
    return {"agent": agent, "finding": summary, "data": data,
            "confidence": confidence, "timestamp": datetime.now().isoformat()}


def _decision(point: str, choice: str, reasoning: str, by: str) -> dict:
    return {"decision_point": point, "choice": choice,
            "reasoning": reasoning, "made_by": by,
            "timestamp": datetime.now().isoformat()}


def _conflict(src_a: str, src_b: str, desc: str, resolution: str) -> dict:
    return {"source_a": src_a, "source_b": src_b,
            "description": desc, "resolution": resolution,
            "timestamp": datetime.now().isoformat()}


def _prev_findings_text(state: SupportState) -> str:
    findings = state.get("findings", [])
    if not findings:
        return "None yet."
    return "\n".join(f"  [{f['agent']}] {f['finding']}" for f in findings)


def _done_agents(state: SupportState) -> list:
    """Return lowercase agent names already completed, without the 'Agent' suffix."""
    return [
        c.lower().replace("agent", "").strip()
        for c in state.get("completed_agents", [])
    ]


# ─────────────────────────────────────────────────────────────
# NODE 1 — ORCHESTRATOR  (the dynamic router — runs multiple times)
# ─────────────────────────────────────────────────────────────

ROUTER_SYSTEM = """You are the Orchestrator for TechCorp SaaS customer support intelligence system.

You are called MULTIPLE TIMES during one investigation.
Each time, you see the customer query AND all findings gathered so far.
Your ONLY job: decide the single best NEXT action.

AVAILABLE AGENTS:
  account    → fetches plan, billing, seat count, account status from DB
  feature    → checks feature availability, setup docs, rate limits
  contract   → validates SLA compliance, contract entitlements, violations
  escalation → FINAL STEP: makes escalation decision and creates ticket if needed

RULES:
1. On the first call (no findings yet): pick the most relevant agent for the query.
   - If query is purely about a feature (dark mode, API, SSO etc.) → start with feature
   - If query mentions account, plan, billing, seats → start with account
   - If query mentions SLA, contract, waiting days → start with account first (need contract_id)
   - If no customer is selected (customer_id=null) → go straight to feature or escalation

2. On subsequent calls (you have findings): re-evaluate based on what you learned.
   - Did account reveal a suspended status? → go to escalation immediately
   - Did account reveal the plan? Does the query need feature validation? → go to feature
   - Is there an SLA/contract issue and you have contract_id now? → go to contract
   - Do you have enough to make the final decision? → go to escalation

3. Never call the same agent twice (list of completed agents is given).
4. escalation is always the LAST step — call it only when all needed investigation is done.
5. You do NOT need to call all agents — only the ones relevant to this query.

OUTPUT: Respond ONLY with valid JSON, no markdown:
{
  "next_agent": "feature",
  "reasoning": "Query is purely about dark mode setup — no account context needed.",
  "feature_hint": "dark_mode",
  "issue_date": null
}"""


def orchestrator_node(state: SupportState) -> dict:
    sid       = state["session_id"]
    iteration = state.get("iteration", 0)
    completed = state.get("completed_agents", [])
    done      = _done_agents(state)

    T.agent_start(sid, f"OrchestratorAgent[iter={iteration}]")
    t0 = time.time()

    # Available agents not yet called
    all_agents = ["account", "feature", "contract", "escalation"]
    available  = [a for a in all_agents if a not in done]

    findings_text = _prev_findings_text(state)
    conflicts_txt = _fmt(state.get("conflicts", [])) if state.get("conflicts") else "None"

    user_msg = (
        f"Customer Query: \"{state['query']}\"\n"
        f"Customer ID: {state.get('customer_id') or 'NOT PROVIDED — anonymous query'}\n\n"
        f"=== INVESTIGATION STATUS ===\n"
        f"Iteration       : {iteration}\n"
        f"Completed agents: {completed if completed else 'none yet'}\n"
        f"Available agents: {available}\n\n"
        f"=== FINDINGS SO FAR ===\n"
        f"{findings_text}\n\n"
        f"=== CONFLICTS ===\n"
        f"{conflicts_txt}\n\n"
        f"=== ESCALATION SIGNALS ===\n"
        f"should_escalate : {state.get('should_escalate', False)}\n"
        f"escalation_reason: {state.get('escalation_reason') or 'None'}\n\n"
        f"Based on all of the above, what is the single best NEXT agent to call?\n"
        f"Remember: pick from available agents only: {available}"
    )

    raw, pt, ct, ms = chat(ROUTER_SYSTEM, user_msg, max_tokens=300)
    T.llm_call(sid, f"OrchestratorAgent[iter={iteration}]", pt, ct, ms)

    parsed    = _parse_json(raw)
    reasoning = parsed.get("reasoning", "")
    next_agent = parsed.get("next_agent", "").lower().strip()

    # ── Validate: must be from available agents ────────────
    if next_agent not in available:
        # Smart fallback based on query context
        q = state["query"].lower()
        if "escalation" in available:
            if "account" in available and state.get("customer_id"):
                next_agent = "account"
            elif "feature" in available and any(
                w in q for w in ["feature","dark","api","analytic","sso","webhook","enable","how"]
            ):
                next_agent = "feature"
            elif "contract" in available and any(
                w in q for w in ["sla","contract","violation","days","waiting"]
            ):
                next_agent = "contract"
            else:
                next_agent = "escalation"
        else:
            next_agent = available[0] if available else "escalation"

    # ── Log decision ───────────────────────────────────────
    T.decision(
        sid, f"route[iter={iteration}]",
        next_agent, reasoning,
        f"OrchestratorAgent[iter={iteration}]"
    )
    T.agent_end(sid, f"OrchestratorAgent[iter={iteration}]", time.time() - t0)

    update: dict = {
        "next_agent":   next_agent,
        "iteration":    iteration + 1,
        "feature_hint": parsed.get("feature_hint") or state.get("feature_hint"),
        "issue_date":   parsed.get("issue_date")    or state.get("issue_date"),
        "decisions": [_decision(
            f"route[iter={iteration}]", next_agent,
            reasoning, f"OrchestratorAgent[iter={iteration}]"
        )],
    }

    # First call: capture the initial reasoning for display
    if iteration == 0:
        update["plan_reasoning"] = reasoning
        update["complexity"]     = "high" if state.get("customer_id") else "low"

    return update


# ─────────────────────────────────────────────────────────────
# NODE 2 — ACCOUNT
# ─────────────────────────────────────────────────────────────

ACCOUNT_SYSTEM = """You are the Account Agent for TechCorp SaaS customer support.
You have been given REAL data retrieved from the customer database.
Use ONLY this data — do not invent anything.

TASK:
1. Summarize the customer's plan, account status, seat usage, and enabled features.
2. Flag anomalies: seat overage, suspended status, failed billing, missing features.
3. State clearly how this data is relevant to the customer's query.

Respond ONLY with valid JSON, no markdown:
{
  "summary": "Clear paragraph using the actual data.",
  "plan": "starter",
  "status": "active",
  "seats_total": 10,
  "seats_used": 15,
  "anomalies": ["Seat overage: 15 used, 10 allowed"],
  "enabled_features": ["basic_dashboard"],
  "relevant_to_query": "...",
  "confidence": "high"
}"""


def account_node(state: SupportState) -> dict:
    sid = state["session_id"]
    cid = state.get("customer_id")

    if not cid:
        return {
            "findings": [_finding("AccountAgent",
                "No customer selected — running anonymous mode.", {}, "low")],
            "completed_agents": ["AccountAgent"],
        }

    T.agent_start(sid, "AccountAgent")
    t0 = time.time()

    _account_tools.FAILURE_RATE = 0.0
    customer = _safe(sid, "AccountAgent", _account_tools.lookup_customer,       cid, fallback={})
    billing  = _safe(sid, "AccountAgent", _account_tools.get_billing_history,   cid, fallback=[])
    status   = _safe(sid, "AccountAgent", _account_tools.check_account_status,  cid, fallback={})
    features = _safe(sid, "AccountAgent", _account_tools.list_enabled_features, cid, fallback=[])

    user_msg = (
        f"Customer Query: \"{state['query']}\"\n\n"
        f"=== REAL CUSTOMER DATA ===\n"
        f"Profile:\n{_fmt(customer)}\n\n"
        f"Status:\n{_fmt(status)}\n\n"
        f"Features: {_fmt(features)}\n\n"
        f"Recent Billing:\n{_fmt((billing or [])[:3])}\n\n"
        f"Analyze and return your JSON finding."
    )
    raw, pt, ct, ms = chat(ACCOUNT_SYSTEM, user_msg)
    T.llm_call(sid, "AccountAgent", pt, ct, ms)
    parsed = _parse_json(raw)

    summary    = parsed.get("summary", "Account data retrieved.")
    confidence = parsed.get("confidence", "high")
    T.finding(sid, "AccountAgent", summary, confidence)

    account_status_val = parsed.get("status", (status or {}).get("status", "active"))
    should_escalate    = state.get("should_escalate", False)
    escalation_reason  = state.get("escalation_reason")
    extra_decisions    = []

    if account_status_val == "suspended":
        should_escalate   = True
        escalation_reason = "Account is suspended — requires Account Management."
        T.decision(sid, "adaptive_signal", "force_escalate",
                   escalation_reason, "AccountAgent")
        extra_decisions.append(_decision(
            "adaptive_signal", "force_escalate",
            escalation_reason, "AccountAgent"
        ))

    T.agent_end(sid, "AccountAgent", time.time() - t0)

    return {
        "customer_plan":    parsed.get("plan",   (customer or {}).get("plan",   "unknown")),
        "account_status":   account_status_val,
        "contract_id":      (customer or {}).get("contract_id"),
        "should_escalate":  should_escalate,
        "escalation_reason": escalation_reason,
        "findings": [_finding("AccountAgent", summary, {
            "customer": customer, "status": status,
            "features": features, "billing": (billing or [])[:3],
            "analysis": parsed,
        }, confidence)],
        "decisions": extra_decisions,
        "completed_agents": ["AccountAgent"],
    }


# ─────────────────────────────────────────────────────────────
# NODE 3 — FEATURE
# ─────────────────────────────────────────────────────────────

FEATURE_SYSTEM = """You are the Feature Agent for TechCorp SaaS customer support.
You have been given REAL data from the feature database.
Use ONLY this data — do not invent anything.

TASK:
1. State whether the requested feature is available on the customer's plan.
2. If available: give exact setup steps from the documentation.
3. If NOT available: state clearly which plan includes it.
4. Report any rate limits or caps exactly as in the data.
5. Flag documentation conflicts.

Respond ONLY with valid JSON, no markdown:
{
  "feature_available": false,
  "feature_name": "api_access",
  "current_plan": "starter",
  "required_plan": "pro",
  "setup_instructions": "...",
  "limits": "1000 calls/month on Pro",
  "documentation_note": "...",
  "summary": "Clear paragraph from actual data.",
  "confidence": "high"
}"""


def feature_node(state: SupportState) -> dict:
    sid  = state["session_id"]
    plan = state.get("customer_plan") or "starter"
    hint = state.get("feature_hint")

    if not hint:
        q = state["query"].lower()
        if "dark" in q:                      hint = "dark_mode"
        elif "api" in q:                     hint = "api_access"
        elif "analytic" in q:                hint = "advanced_analytics"
        elif "sso" in q or "sign-on" in q:   hint = "sso"
        elif "webhook" in q:                 hint = "webhooks"
        elif "seat" in q or "user" in q:     hint = "seats"
        else:                                hint = "dark_mode"

    T.agent_start(sid, "FeatureAgent")
    t0 = time.time()

    _feature_tools.FAILURE_RATE = 0.0
    matrix = _safe(sid, "FeatureAgent", _feature_tools.get_feature_matrix, fallback={})
    doc    = _safe(sid, "FeatureAgent", _feature_tools.get_feature_documentation, hint, fallback={}) if hint != "seats" else {}
    config = _safe(sid, "FeatureAgent", _feature_tools.validate_configuration, hint, plan, fallback={}) if hint != "seats" else {}
    limits = _safe(sid, "FeatureAgent", _feature_tools.check_feature_limits, hint, plan, fallback={}) if hint != "seats" else {}

    starter_f    = (matrix or {}).get("starter", {})
    pro_f        = (matrix or {}).get("pro", {})
    enterprise_f = (matrix or {}).get("enterprise", {})

    user_msg = (
        f"Customer Query: \"{state['query']}\"\n"
        f"Customer Plan : {plan} | Feature: {hint}\n\n"
        f"=== REAL FEATURE DATA ===\n"
        f"Plan matrix ({plan}):\n{_fmt((matrix or {}).get(plan, {}))}\n\n"
        f"Documentation:\n{_fmt(doc)}\n\n"
        f"Config validation:\n{_fmt(config)}\n\n"
        f"Limits:\n{_fmt(limits)}\n\n"
        f"Cross-plan reference:\n"
        f"  Starter : api_rate_limit={starter_f.get('api_rate_limit')}, seats={starter_f.get('seats_limit')}\n"
        f"  Pro     : api_rate_limit={pro_f.get('api_rate_limit')}, seats={pro_f.get('seats_limit')}\n"
        f"  Enterprise: api_rate_limit={enterprise_f.get('api_rate_limit')}, seats={enterprise_f.get('seats_limit')}\n\n"
        f"Previous findings:\n{_prev_findings_text(state)}\n\n"
        f"Analyze and return your JSON finding."
    )
    raw, pt, ct, ms = chat(FEATURE_SYSTEM, user_msg)
    T.llm_call(sid, "FeatureAgent", pt, ct, ms)
    parsed = _parse_json(raw)

    summary    = parsed.get("summary", "Feature investigation complete.")
    confidence = parsed.get("confidence", "high")
    T.finding(sid, "FeatureAgent", summary, confidence)

    new_conflicts = []
    if hint == "api_access" and plan == "pro":
        note = (doc or {}).get("note", "") if isinstance(doc, dict) else ""
        if "1,000" in note or "1000" in note:
            c = _conflict(
                "marketing_documentation", "feature_matrix_database",
                "Marketing docs claim 'unlimited API calls' for Pro — actual limit is 1,000/month.",
                "Feature matrix (live system data) is authoritative. Docs are outdated.",
            )
            new_conflicts.append(c)
            T.conflict(sid, c["source_a"], c["source_b"],
                       c["description"], c["resolution"])

    T.agent_end(sid, "FeatureAgent", time.time() - t0)

    return {
        "findings": [_finding("FeatureAgent", summary, {
            "feature": hint, "plan": plan,
            "available": parsed.get("feature_available"),
            "limits": parsed.get("limits"),
            "setup": parsed.get("setup_instructions"),
            "analysis": parsed,
        }, confidence)],
        "conflicts": new_conflicts,
        "completed_agents": ["FeatureAgent"],
    }


# ─────────────────────────────────────────────────────────────
# NODE 4 — CONTRACT
# ─────────────────────────────────────────────────────────────

CONTRACT_SYSTEM = """You are the Contract Agent for TechCorp SaaS customer support.
You have been given REAL contract data from the contract database.
Use ONLY this data — do not invent anything.

TASK:
1. State the exact SLA hours guaranteed in this contract.
2. Calculate if the SLA was violated based on elapsed hours.
3. List features and seats included in the contract.
4. State any special terms or penalties.
5. Recommend escalation if violation confirmed.

Respond ONLY with valid JSON, no markdown:
{
  "contract_id": "CONTRACT-003",
  "sla_hours": 4,
  "sla_violated": true,
  "hours_elapsed": 243.5,
  "violation_severity": "critical",
  "contract_features": ["api_access"],
  "special_terms": "10% MRR credit per day",
  "escalation_recommended": true,
  "escalation_reason": "SLA violated by 239 hours.",
  "summary": "Clear paragraph from actual data.",
  "confidence": "high"
}"""


def contract_node(state: SupportState) -> dict:
    sid         = state["session_id"]
    contract_id = state.get("contract_id")

    if not contract_id:
        return {
            "findings": [_finding("ContractAgent",
                "No contract_id in state — AccountAgent must run first.", {}, "low")],
            "completed_agents": ["ContractAgent"],
        }

    T.agent_start(sid, "ContractAgent")
    t0 = time.time()

    _contract_tools.FAILURE_RATE = 0.0
    issue_date = state.get("issue_date")
    contract = _safe(sid, "ContractAgent", _contract_tools.lookup_contract,       contract_id, fallback={})
    terms    = _safe(sid, "ContractAgent", _contract_tools.get_contract_terms,    contract_id, fallback={})
    features = _safe(sid, "ContractAgent", _contract_tools.get_included_features, contract_id, fallback=[])
    sla_check = {}
    if issue_date:
        sla_check = _safe(sid, "ContractAgent",
                          _contract_tools.validate_sla_compliance,
                          contract_id, issue_date, fallback={}) or {}

    user_msg = (
        f"Customer Query: \"{state['query']}\"\n"
        f"Contract ID: {contract_id}\n\n"
        f"=== REAL CONTRACT DATA ===\n"
        f"Contract:\n{_fmt(contract)}\n\n"
        f"Terms:\n{_fmt(terms)}\n\n"
        f"Included features: {_fmt(features)}\n\n"
        f"SLA check (issue_date={issue_date or 'not provided'}):\n{_fmt(sla_check)}\n\n"
        f"Previous findings:\n{_prev_findings_text(state)}\n\n"
        f"Analyze and return your JSON finding."
    )
    raw, pt, ct, ms = chat(CONTRACT_SYSTEM, user_msg)
    T.llm_call(sid, "ContractAgent", pt, ct, ms)
    parsed = _parse_json(raw)

    summary    = parsed.get("summary", "Contract reviewed.")
    confidence = parsed.get("confidence", "high")
    T.finding(sid, "ContractAgent", summary, confidence)

    should_escalate   = state.get("should_escalate", False)
    escalation_reason = state.get("escalation_reason")
    extra_decisions   = []

    if parsed.get("escalation_recommended"):
        should_escalate   = True
        escalation_reason = parsed.get("escalation_reason", "Contract violation detected.")
        T.decision(sid, "escalation_signal", "escalate",
                   escalation_reason, "ContractAgent")
        extra_decisions.append(_decision(
            "escalation_signal", "escalate",
            escalation_reason, "ContractAgent"
        ))

    T.agent_end(sid, "ContractAgent", time.time() - t0)

    return {
        "findings": [_finding("ContractAgent", summary, {
            "contract": contract, "terms": terms,
            "features": features, "sla_check": sla_check,
            "analysis": parsed,
        }, confidence)],
        "decisions":          extra_decisions,
        "should_escalate":   should_escalate,
        "escalation_reason": escalation_reason,
        "completed_agents":  ["ContractAgent"],
    }


# ─────────────────────────────────────────────────────────────
# NODE 5 — ESCALATION
# ─────────────────────────────────────────────────────────────

ESCALATION_SYSTEM = """You are the Escalation Agent for TechCorp SaaS customer support.
Review all prior agent findings and make the FINAL escalation decision.

ESCALATION TRIGGERS:
- SLA violation confirmed           → YES, P1, Customer Success
- Account suspended                 → YES, P1, Account Management
- Revenue impact stated ($/day)     → YES, P1, Customer Success
- Product bug confirmed             → YES, P2, Engineering
- Billing failure or dispute        → YES, P2, Finance
- Onboarding 10+ users              → YES, P2, Onboarding
- Simple feature question           → NO escalation
- Plan upgrade needed               → NO escalation

Respond ONLY with valid JSON, no markdown:
{
  "should_escalate": false,
  "priority": null,
  "team": null,
  "issue_type": "general_inquiry",
  "reason": "Why this decision, referencing specific findings.",
  "customer_message": "Warm, helpful message for the customer.",
  "confidence": "high"
}"""


def escalation_node(state: SupportState) -> dict:
    sid = state["session_id"]
    T.agent_start(sid, "EscalationAgent")
    t0  = time.time()

    findings_text = _prev_findings_text(state)
    conflicts_txt = _fmt(state.get("conflicts", [])) if state.get("conflicts") else "None"
    decisions_txt = _fmt([
        {k: v for k, v in d.items() if k != "timestamp"}
        for d in state.get("decisions", [])
    ])

    user_msg = (
        f"Customer Query: \"{state['query']}\"\n\n"
        f"=== ALL FINDINGS ===\n{findings_text}\n\n"
        f"=== CONFLICTS ===\n{conflicts_txt}\n\n"
        f"=== PRIOR DECISIONS ===\n{decisions_txt}\n\n"
        f"Escalation signals:\n"
        f"  should_escalate: {state.get('should_escalate', False)}\n"
        f"  reason: {state.get('escalation_reason') or 'None'}\n\n"
        f"Make the final escalation decision."
    )
    raw, pt, ct, ms = chat(ESCALATION_SYSTEM, user_msg)
    T.llm_call(sid, "EscalationAgent", pt, ct, ms)
    parsed = _parse_json(raw)

    ticket_data = None
    if parsed.get("should_escalate"):
        _escalation_tools.FAILURE_RATE = 0.0
        issue_type = parsed.get("issue_type", "general_inquiry")
        routing = _safe(sid, "EscalationAgent",
                        _escalation_tools.get_escalation_routing, issue_type,
                        fallback={"team": "Support Tier 2", "priority": "P2"}) or {}
        ticket = _safe(sid, "EscalationAgent",
                       _escalation_tools.create_escalation_ticket,
                       parsed.get("reason", "Escalation required"),
                       parsed.get("priority", routing.get("priority", "P2")),
                       {"session_id": sid, "customer_id": state.get("customer_id"),
                        "query": state["query"]},
                       fallback=None)
        if ticket:
            ticket_data = ticket
            _safe(sid, "EscalationAgent",
                  _escalation_tools.notify_support_team, ticket["ticket_id"], fallback=None)
            _safe(sid, "EscalationAgent",
                  _escalation_tools.log_escalation_reason,
                  ticket["ticket_id"], parsed.get("reason", ""), fallback=None)
            T.escalation(sid, ticket["ticket_id"],
                         parsed.get("priority", "P2"),
                         parsed.get("reason", ""),
                         routing.get("team", "Support"))

    decision_str = "escalate" if parsed.get("should_escalate") else "resolve"
    T.finding(sid, "EscalationAgent",
              f"Decision: {decision_str.upper()} — {parsed.get('reason', '')}",
              parsed.get("confidence", "high"))
    T.decision(sid, "final_escalation", decision_str,
               parsed.get("reason", ""), "EscalationAgent")
    T.agent_end(sid, "EscalationAgent", time.time() - t0)

    return {
        "should_escalate":   parsed.get("should_escalate", False),
        "escalation_ticket": ticket_data,
        "escalation_reason": parsed.get("reason", ""),
        "findings": [_finding("EscalationAgent",
                               f"Decision: {decision_str.upper()} — {parsed.get('reason','')}",
                               {"decision": parsed, "ticket": ticket_data},
                               parsed.get("confidence", "high"))],
        "decisions": [_decision("final_escalation", decision_str,
                                parsed.get("reason", ""), "EscalationAgent")],
        "completed_agents": ["EscalationAgent"],
    }


# ─────────────────────────────────────────────────────────────
# NODE 6 — SYNTHESIS
# ─────────────────────────────────────────────────────────────

SYNTHESIS_SYSTEM = """You are writing the final reply to a customer support query for TechCorp SaaS.

You have verified findings from multiple specialist agents.
Write a response that:
1. Directly and clearly answers what the customer asked.
2. Uses the EXACT data from findings (plan names, limits, steps).
3. If a data conflict was found — state the CORRECT information clearly.
4. Gives concrete, actionable next steps.
5. If escalated — mention the ticket ID and what happens next.
6. Do NOT mention agent names or internal systems.
7. Be warm, professional, and concise.

Write ONLY the customer-facing message — no JSON, no headers."""


def synthesis_node(state: SupportState) -> dict:
    sid = state["session_id"]
    T.agent_start(sid, "OrchestratorAgent[synthesis]")
    t0  = time.time()

    findings_text  = _prev_findings_text(state)
    conflicts_text = _fmt(state.get("conflicts", [])) if state.get("conflicts") else "None"
    ticket         = state.get("escalation_ticket")
    ticket_info    = (f"Escalation ticket: {ticket['ticket_id']}, "
                      f"Priority: {ticket.get('priority')}")  if ticket else "No ticket."

    user_msg = (
        f"Customer Query: \"{state['query']}\"\n\n"
        f"Agent findings:\n{findings_text}\n\n"
        f"Conflicts resolved:\n{conflicts_text}\n\n"
        f"Escalation: {'YES — ' + (state.get('escalation_reason') or '') if state.get('should_escalate') else 'NO'}\n"
        f"{ticket_info}\n\n"
        f"Write the final customer-facing support response."
    )
    raw, pt, ct, ms = chat(SYNTHESIS_SYSTEM, user_msg, max_tokens=800)
    T.llm_call(sid, "OrchestratorAgent[synthesis]", pt, ct, ms)
    T.agent_end(sid, "OrchestratorAgent[synthesis]", time.time() - t0)

    return {"final_response": raw.strip()}
