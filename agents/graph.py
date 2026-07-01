"""
graph.py
--------
Dynamic Routing Loop — Strategy .

The Orchestrator is the ONLY router. Every agent returns to it.
It re-evaluates after each agent using fresh findings.

Graph:
  START
    │
    ▼
  orchestrator ◄─────────────────────────────────┐
    │                                             │
    ├─ next_agent="account"  → account_node  ────┤
    ├─ next_agent="feature"  → feature_node  ────┤
    ├─ next_agent="contract" → contract_node ────┤
    └─ next_agent="escalation" → escalation_node
                                      │
                                 synthesis_node
                                      │
                                     END

Key design points:
  1. initial_state has next_agent="" — Orchestrator decides FIRST call too.
  2. Every specialist loops back to Orchestrator via route_after_agent.
  3. Only after EscalationAgent does the graph go to synthesis → END.
  4. MAX_ITERATIONS cap prevents infinite loops.
"""
import uuid
import time
from typing import Literal

from langgraph.graph import StateGraph, START, END

from memory.graph_state import SupportState
from agents.nodes import (
    orchestrator_node, account_node, feature_node,
    contract_node, escalation_node, synthesis_node,
)
import monitoring.tracer as T

MAX_ITERATIONS = 8


# ─────────────────────────────────────────────────────────────
# ROUTING FUNCTIONS
# ─────────────────────────────────────────────────────────────

def route_from_orchestrator(state: SupportState) -> Literal[
    "account", "feature", "contract", "escalation"
]:
    """
    Called after every Orchestrator run.
    Reads next_agent from state and routes there.
    Falls back to escalation if max iterations exceeded.
    """
    if state.get("iteration", 0) >= MAX_ITERATIONS:
        return "escalation"
    next_agent = state.get("next_agent", "escalation")
    # Ensure it's a valid target
    if next_agent not in {"account", "feature", "contract", "escalation"}:
        return "escalation"
    return next_agent


def route_after_agent(state: SupportState) -> Literal["orchestrator", "synthesis"]:
    """
    Called after every specialist agent.
    - After EscalationAgent → go to synthesis (investigation complete)
    - After any other agent → return to Orchestrator for re-evaluation
    """
    last_agent = (state.get("completed_agents") or [""])[-1]
    if "Escalation" in last_agent:
        return "synthesis"
    return "orchestrator"


# ─────────────────────────────────────────────────────────────
# BUILD GRAPH
# ─────────────────────────────────────────────────────────────

def build_graph():
    g = StateGraph(SupportState)

    # Register nodes
    g.add_node("orchestrator", orchestrator_node)
    g.add_node("account",      account_node)
    g.add_node("feature",      feature_node)
    g.add_node("contract",     contract_node)
    g.add_node("escalation",   escalation_node)
    g.add_node("synthesis",    synthesis_node)

    # START always goes to Orchestrator — it decides everything from here
    g.add_edge(START, "orchestrator")

    # Orchestrator → one of the four specialists (dynamic, based on next_agent)
    g.add_conditional_edges(
        "orchestrator",
        route_from_orchestrator,
        {
            "account":    "account",
            "feature":    "feature",
            "contract":   "contract",
            "escalation": "escalation",
        },
    )

    # Every specialist → back to Orchestrator OR to synthesis
    for node in ["account", "feature", "contract", "escalation"]:
        g.add_conditional_edges(
            node,
            route_after_agent,
            {
                "orchestrator": "orchestrator",
                "synthesis":    "synthesis",
            },
        )

    # Synthesis → END
    g.add_edge("synthesis", END)

    return g.compile()


support_graph = build_graph()


# ─────────────────────────────────────────────────────────────
# PUBLIC RUN FUNCTION
# ─────────────────────────────────────────────────────────────

def run_investigation(query: str, customer_id: str = None) -> dict:
    session_id = f"SIQ-{uuid.uuid4().hex[:8].upper()}"
    T.session_start(session_id, query, customer_id)
    t0 = time.time()

    initial_state: SupportState = {
        "session_id":   session_id,
        "query":        query,
        "customer_id":  customer_id,

        # ── Dynamic routing ───────────────────────────────
        # next_agent is EMPTY — Orchestrator decides on its very first call
        "next_agent":   "",
        "iteration":    0,

        # ── Display / plan info ───────────────────────────
        "investigation_plan": [],
        "plan_reasoning":     "",
        "complexity":         "medium",
        "feature_hint":       None,
        "issue_date":         None,

        # ── Account metadata (filled by AccountAgent) ─────
        "customer_plan":  "unknown",
        "account_status": "unknown",
        "contract_id":    None,

        # ── Accumulating lists ────────────────────────────
        "findings":  [],
        "decisions": [],
        "conflicts": [],
        "messages":  [{"role": "user", "content": query}],

        # ── Escalation ────────────────────────────────────
        "should_escalate":   False,
        "escalation_reason": None,
        "escalation_ticket": None,

        # ── Output ────────────────────────────────────────
        "final_response": "",

        # ── Tracking ──────────────────────────────────────
        "completed_agents": [],
        "failed_agents":    [],
    }

    final_state = support_graph.invoke(initial_state)

    elapsed = time.time() - t0
    T.session_end(
        session_id, elapsed,
        final_state.get("should_escalate", False),
        len(final_state.get("conflicts", [])),
        final_state.get("final_response", ""),
    )

    return {
        "session_id":        session_id,
        "response":          final_state.get("final_response", ""),
        "plan":              final_state.get("completed_agents", []),
        "plan_reasoning":    final_state.get("plan_reasoning", ""),
        "complexity":        final_state.get("complexity", "medium"),
        "escalated":         final_state.get("should_escalate", False),
        "escalation_ticket": final_state.get("escalation_ticket"),
        "conflicts":         final_state.get("conflicts", []),
        "findings":          final_state.get("findings", []),
        "decisions":         final_state.get("decisions", []),
        "elapsed_s":         round(elapsed, 2),
    }
