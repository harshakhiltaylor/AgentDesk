"""
graph_state.py
--------------
SupportState for the DYNAMIC ROUTING LOOP architecture.

Key change from the old design:
  OLD: Orchestrator sets run_account/run_feature/run_contract upfront.
       Agents run in a fixed sequence.

  NEW: Orchestrator sets `next_agent` (one string) after seeing the
       current state. After every agent completes, control returns to
       the Orchestrator which re-evaluates and picks the next agent.
       This is the Dynamic Routing Loop from Strategy 1.

Flow:
  START → orchestrator → account → orchestrator → feature → orchestrator
        → contract → orchestrator → escalation → synthesis → END

The Orchestrator is called N+1 times (once before each agent, once
to signal "done"). It sees all findings so far before deciding what
to invoke next — true dynamic routing.
"""
from typing import TypedDict, Annotated, List, Optional, Any
import operator


def _merge_list(a: list, b: list) -> list:
    return a + b


class SupportState(TypedDict):
    # ── Query input ───────────────────────────────────────
    session_id:   str
    query:        str
    customer_id:  Optional[str]

    # ── Dynamic routing — set by Orchestrator each loop ───
    # One of: "account" | "feature" | "contract" | "escalation" | "done"
    next_agent:   str

    # ── Orchestrator context (written on first call) ──────
    investigation_plan: List[str]   # full intended plan for display
    plan_reasoning:     str
    complexity:         str         # low | medium | high
    feature_hint:       Optional[str]
    issue_date:         Optional[str]
    iteration:          int         # how many times Orchestrator has run

    # ── Shared metadata (written by AccountAgent) ────────
    customer_plan:  str
    account_status: str
    contract_id:    Optional[str]

    # ── Append-only lists — all agents write to these ─────
    findings:  Annotated[List[dict], _merge_list]
    decisions: Annotated[List[dict], _merge_list]
    conflicts: Annotated[List[dict], _merge_list]
    messages:  Annotated[List[dict], _merge_list]

    # ── Escalation ────────────────────────────────────────
    should_escalate:   bool
    escalation_reason: Optional[str]
    escalation_ticket: Optional[dict]

    # ── Final output ──────────────────────────────────────
    final_response: str

    # ── Tracking ──────────────────────────────────────────
    completed_agents: Annotated[List[str], _merge_list]
    failed_agents:    Annotated[List[str], _merge_list]
