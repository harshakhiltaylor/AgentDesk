"""
tracing_utils.py
----------------
Rich terminal tracing for AgentDesk.

Every agent action, tool call, LLM call, and decision prints
a clearly formatted, colored line to the terminal so you can
follow the full investigation in real time — no Langfuse needed.

Color scheme:
  CYAN    → Orchestrator actions.   ... This is the color of the Orchestrator's "guiding light" as it directs the investigation.
  GREEN   → Agent completions / success
  YELLOW  → Tool calls
  BLUE    → LLM calls
  MAGENTA → Decisions / routing
  RED     → Errors / failures
  WHITE   → General info
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any, List

# ── Optional Langfuse ─────────────────────────────────────────
try:
    from monitoring.langfuse_config import get_langfuse, LANGFUSE_ENABLED
except Exception:
    LANGFUSE_ENABLED = False
    def get_langfuse(): return None

logger = logging.getLogger("agentdesk.tracing")

# ── ANSI color codes ──────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

BG_RED    = "\033[41m"
BG_GREEN  = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE   = "\033[44m"

# ── In-memory trace log (also powers /api/traces endpoint) ────
_trace_log: List[Dict] = []

# ── Session tracker (for grouping logs by session) ────────────
_current_session: Dict = {}


def _ts() -> str:
    """Short timestamp: HH:MM:SS.mmm"""
    return datetime.now().strftime("%H:%M:%S.%f")[:12]


def _print(color: str, icon: str, label: str, message: str, dim_suffix: str = ""):
    """Central print — always goes to stdout regardless of log level."""
    ts = f"{DIM}{_ts()}{RESET}"
    icon_part = f"{color}{BOLD}{icon}{RESET}"
    label_part = f"{color}{BOLD}{label:<18}{RESET}"
    msg_part = f"{WHITE}{message}{RESET}"
    suffix = f" {DIM}{dim_suffix}{RESET}" if dim_suffix else ""
    print(f"  {ts}  {icon_part}  {label_part}  {msg_part}{suffix}", flush=True)


# ─────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────

def log_session_start(session_id: str, query: str, customer_id: str = None):
    """Print a prominent header when a new investigation begins."""
    print(flush=True)
    print(f"  {CYAN}{'━' * 64}{RESET}", flush=True)
    print(f"  {CYAN}{BOLD}  🤖  NEW INVESTIGATION{RESET}", flush=True)
    print(f"  {CYAN}  Session  : {BOLD}{session_id}{RESET}", flush=True)
    print(f"  {CYAN}  Customer : {customer_id or 'anonymous'}{RESET}", flush=True)
    print(f"  {CYAN}  Query    : {query[:80]}{'…' if len(query)>80 else ''}{RESET}", flush=True)
    print(f"  {CYAN}{'━' * 64}{RESET}", flush=True)
    print(flush=True)
    _current_session["id"] = session_id
    _append(session_id, "session.start", {"query": query, "customer_id": customer_id})


def log_plan(plan: list, reasoning: str, complexity: str):
    """Print the investigation plan the Orchestrator built."""
    arrow_plan = "  →  ".join(plan)
    _print(MAGENTA, "🗺️ ", "PLAN BUILT", arrow_plan, f"[{complexity.upper()}]")
    _print(MAGENTA, "   ", "REASONING", reasoning[:100])
    _append(_current_session.get("id"), "orchestrator.plan",
            {"plan": plan, "reasoning": reasoning, "complexity": complexity})


def log_agent_start(agent: str, session_id: str = None):
    """Print when an agent begins execution."""
    _print(CYAN, "▶  ", f"{agent}", "starting…")
    _append(session_id or _current_session.get("id"), f"{agent}.start", {})


def log_tool_call(agent: str, tool: str, args: Any, success: bool, result_preview: str = "", latency_ms: float = 0):
    """Print every tool invocation with result."""
    status = f"{GREEN}✓ OK{RESET}" if success else f"{RED}✗ FAIL{RESET}"
    latency = f"{latency_ms:.0f}ms" if latency_ms else ""
    preview = f"→ {str(result_preview)[:60]}" if result_preview else ""
    _print(
        YELLOW, "🔧 ", f"  {tool}",
        f"{status}  {preview}",
        latency,
    )
    _append(_current_session.get("id"), f"tool.{tool}",
            {"agent": agent, "success": success, "latency_ms": latency_ms})


def log_llm_call(agent: str, tokens_in: int = 0, tokens_out: int = 0, latency_ms: float = 0):
    """Print when an agent calls the LLM."""
    toks = f"{tokens_in}→{tokens_out} tokens" if tokens_in else ""
    lat  = f"{latency_ms:.0f}ms" if latency_ms else ""
    _print(BLUE, "🧠 ", f"  LLM [{agent}]", "Groq llama-3.3-70b", f"{toks}  {lat}".strip())
    _append(_current_session.get("id"), f"llm.call.{agent}", {"tokens_in": tokens_in, "latency_ms": latency_ms})


def log_finding(agent: str, finding: str, confidence: str = "high"):
    """Print a finding an agent wrote to SharedContext."""
    icon = "✅" if confidence == "high" else ("🟡" if confidence == "medium" else "🔴")
    color = GREEN if confidence == "high" else (YELLOW if confidence == "medium" else RED)
    _print(color, f"{icon} ", f"  [{agent}]", finding[:100], f"confidence:{confidence}")
    _append(_current_session.get("id"), f"finding.{agent}", {"finding": finding, "confidence": confidence})


def log_conflict(source_a: str, source_b: str, description: str, resolution: str):
    """Print when a data conflict is detected and resolved."""
    print(flush=True)
    _print(YELLOW, "⚠️ ", "CONFLICT", f"{source_a}  vs  {source_b}")
    _print(YELLOW, "   ", "  ISSUE", description[:100])
    _print(GREEN,  "   ", "  RESOLVED", resolution[:100])
    print(flush=True)
    _append(_current_session.get("id"), "conflict.detected",
            {"source_a": source_a, "source_b": source_b, "description": description, "resolution": resolution})


def log_decision(decision_point: str, choice: str, reasoning: str, made_by: str):
    """Print a routing or escalation decision."""
    _print(MAGENTA, "🎯 ", f"DECISION", f"{decision_point}  →  {BOLD}{choice}{RESET}", f"by {made_by}")
    _print(MAGENTA, "   ", "  REASON", reasoning[:100])
    _append(_current_session.get("id"), f"decision.{decision_point}",
            {"choice": choice, "reasoning": reasoning, "made_by": made_by})


def log_agent_complete(agent: str, duration_s: float):
    """Print when an agent finishes successfully."""
    _print(GREEN, "✅ ", f"{agent}", f"complete", f"{duration_s:.2f}s")
    _append(_current_session.get("id"), f"{agent}.complete", {"duration_s": duration_s})


def log_agent_error(agent: str, error: str):
    """Print when an agent fails."""
    _print(RED, "❌ ", f"{agent}", f"FAILED: {error[:80]}")
    _append(_current_session.get("id"), f"{agent}.error", {"error": error})


def log_escalation(ticket_id: str, priority: str, reason: str, team: str):
    """Print escalation ticket creation prominently."""
    print(flush=True)
    print(f"  {BG_RED}{WHITE}{BOLD}  🚨  ESCALATION  {RESET}", flush=True)
    _print(RED, "   ", "  TICKET", ticket_id)
    _print(RED, "   ", "  PRIORITY", priority)
    _print(RED, "   ", "  TEAM", team)
    _print(RED, "   ", "  REASON", reason[:100])
    print(flush=True)
    _append(_current_session.get("id"), "escalation.created",
            {"ticket_id": ticket_id, "priority": priority, "reason": reason, "team": team})


def log_session_end(session_id: str, elapsed_s: float, escalated: bool, conflict_count: int):
    """Print a summary footer when the investigation finishes."""
    esc_str = f"{RED}YES 🚨{RESET}" if escalated else f"{GREEN}NO ✅{RESET}"
    print(flush=True)
    print(f"  {GREEN}{'━' * 64}{RESET}", flush=True)
    print(f"  {GREEN}{BOLD}  ✅  INVESTIGATION COMPLETE{RESET}", flush=True)
    print(f"  {GREEN}  Duration  : {elapsed_s:.2f}s{RESET}", flush=True)
    print(f"  {GREEN}  Escalated : {esc_str}", flush=True)
    print(f"  {GREEN}  Conflicts : {conflict_count}{RESET}", flush=True)
    print(f"  {GREEN}{'━' * 64}{RESET}", flush=True)
    print(flush=True)
    _append(session_id, "session.end",
            {"elapsed_s": elapsed_s, "escalated": escalated, "conflicts": conflict_count})


# ── Legacy log_event (kept for backward compat with old call sites) ──
def log_event(name: str, data: Dict, level: str = "info"):
    """
    Generic event logger — maps to the right rich printer when possible,
    otherwise just appends to the in-memory log quietly.
    """
    _append(_current_session.get("id"), name, data)

    # Route to rich printers for known event patterns
    if name.endswith(".start") and "session" in data:
        pass   # session start handled separately
    elif "error" in name.lower():
        agent = data.get("agent", name)
        _print(RED, "❌ ", agent, data.get("error", name)[:80])
    # All others just go to in-memory log silently (avoid double-printing)


def get_trace_log() -> List[Dict]:
    """Return in-memory trace log — powers the /api/traces endpoint."""
    return list(_trace_log)


def clear_trace_log():
    _trace_log.clear()


# ── Internal ──────────────────────────────────────────────────
def _append(session_id: str, event: str, data: Dict):
    _trace_log.append({
        "ts": datetime.now().isoformat(),
        "session": session_id,
        "event": event,
        "data": data,
    })
    # Also pass to Langfuse if configured
    if LANGFUSE_ENABLED:
        try:
            lf = get_langfuse()
            if lf:
                lf.event(name=event, metadata={"session": session_id, **data})
        except Exception:
            pass
