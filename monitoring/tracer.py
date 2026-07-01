"""
tracer.py
---------
Langfuse v3 — correct API usage.

start_as_current_observation() takes ONLY: name (and optionally input/output)
Type (SPAN vs GENERATION) and metadata are set via:
  update_current_span()       for spans
  update_current_generation() for LLM calls
"""
from datetime import datetime
from typing import Optional, Dict, Any, List

# ── ANSI colors ───────────────────────────────────────────────
R="\033[0m"; BOLD="\033[1m"; DIM="\033[2m"
RED="\033[31m"; GREEN="\033[32m"; YELLOW="\033[33m"
BLUE="\033[34m"; MAGENTA="\033[35m"; CYAN="\033[36m"
WHITE="\033[37m"; BG_RED="\033[41m"

# ── In-memory event log ───────────────────────────────────────
_events: List[Dict] = []

# ── Open context managers per session/agent ───────────────────
_root_cms:  Dict[str, Any] = {}
_agent_cms: Dict[str, Any] = {}


# ─────────────────────────────────────────────────────────────
# LANGFUSE HELPERS
# ─────────────────────────────────────────────────────────────

def _lf_enabled() -> bool:
    try:
        from monitoring.langfuse_setup import LANGFUSE_ENABLED
        return bool(LANGFUSE_ENABLED)
    except Exception:
        return False


def _lf():
    try:
        from monitoring.langfuse_setup import get_langfuse
        return get_langfuse()
    except Exception:
        return None


def _lf_open_root(session_id: str, query: str, customer_id: Optional[str]):
    client = _lf()
    if not client:
        return
    try:
        cm = client.start_as_current_observation(name="agentdesk.investigation")
        cm.__enter__()
        _root_cms[session_id] = cm
        try:
            client.update_current_span(
                input={"query": query, "customer_id": customer_id},
                metadata={"session_id": session_id},
            )
        except Exception:
            pass
    except Exception as e:
        _warn(f"Langfuse root open failed: {e}")


def _lf_close_root(session_id: str, response: str,
                   escalated: bool, elapsed: float):
    client = _lf()
    cm = _root_cms.pop(session_id, None)
    if not cm:
        return
    try:
        if client:
            try:
                client.update_current_span(
                    output={"response": response[:400]},
                    metadata={"escalated": escalated,
                              "elapsed_s": round(elapsed, 2)},
                )
            except Exception:
                pass
        cm.__exit__(None, None, None)
        if client:
            try:
                client.flush()
            except Exception:
                pass
    except Exception:
        pass


def _lf_open_agent(session_id: str, agent: str):
    client = _lf()
    if not client:
        return
    try:
        cm = client.start_as_current_observation(name=agent)
        cm.__enter__()
        _agent_cms[f"{session_id}:{agent}"] = cm
        try:
            client.update_current_span(metadata={"agent": agent})
        except Exception:
            pass
    except Exception as e:
        _warn(f"Langfuse agent open failed ({agent}): {e}")


def _lf_close_agent(session_id: str, agent: str,
                    duration: float, success: bool):
    client = _lf()
    cm = _agent_cms.pop(f"{session_id}:{agent}", None)
    if not cm:
        return
    try:
        if client:
            try:
                client.update_current_span(
                    metadata={"duration_s": round(duration, 3),
                              "success": success}
                )
            except Exception:
                pass
        cm.__exit__(None, None, None)
    except Exception:
        pass


def _lf_log_generation(session_id: str, agent: str, model: str,
                        prompt_tokens: int, completion_tokens: int,
                        latency_ms: float):
    client = _lf()
    if not client:
        return
    try:
        cm = client.start_as_current_observation(name=f"llm.{agent}")
        cm.__enter__()
        try:
            client.update_current_generation(
                model=model,
                usage={
                    "input":  prompt_tokens,
                    "output": completion_tokens,
                    "total":  prompt_tokens + completion_tokens,
                },
                metadata={"latency_ms": round(latency_ms, 1)},
            )
        except Exception:
            pass
        cm.__exit__(None, None, None)
    except Exception:
        pass


def _lf_update(session_id: str, agent: str, key: str, value: Any):
    """Safely enrich the active agent span with one metadata key."""
    client = _lf()
    if not client:
        return
    if f"{session_id}:{agent}" not in _agent_cms:
        return
    try:
        client.update_current_span(metadata={key: value})
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# TERMINAL HELPERS
# ─────────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:12]


def _p(color: str, icon: str, label: str, msg: str, suffix: str = ""):
    ts_str = f"{DIM}{_ts()}{R}"
    lbl    = f"{color}{BOLD}{label:<22}{R}"
    sfx    = f"  {DIM}{suffix}{R}" if suffix else ""
    print(f"  {ts_str}  {color}{BOLD}{icon}{R}  {lbl}  {WHITE}{msg}{R}{sfx}",
          flush=True)


def _warn(msg: str):
    print(f"  {YELLOW}⚠️   {msg}{R}", flush=True)


def _log(session: str, event: str, data: Dict):
    _events.append({
        "ts":      datetime.now().isoformat(),
        "session": session,
        "event":   event,
        "data":    data,
    })


# ─────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────

def session_start(session_id: str, query: str, customer_id: Optional[str]):
    print(flush=True)
    print(f"  {CYAN}{'━'*66}{R}", flush=True)
    print(f"  {CYAN}{BOLD}  🤖  NEW INVESTIGATION{R}", flush=True)
    print(f"  {CYAN}  Session  : {BOLD}{session_id}{R}", flush=True)
    print(f"  {CYAN}  Customer : {customer_id or 'anonymous'}{R}", flush=True)
    print(f"  {CYAN}  Query    : {query[:80]}{'…' if len(query)>80 else ''}{R}",
          flush=True)
    print(f"  {CYAN}{'━'*66}{R}", flush=True)
    print(flush=True)
    _log(session_id, "session.start",
         {"query": query, "customer_id": customer_id})
    if _lf_enabled():
        _lf_open_root(session_id, query, customer_id)


def session_end(session_id: str, elapsed: float, escalated: bool,
                conflict_count: int, response: str):
    esc = f"{RED}YES 🚨{R}" if escalated else f"{GREEN}NO ✅{R}"
    print(flush=True)
    print(f"  {GREEN}{'━'*66}{R}", flush=True)
    print(f"  {GREEN}{BOLD}  ✅  INVESTIGATION COMPLETE{R}", flush=True)
    print(f"  {GREEN}  Duration  : {elapsed:.2f}s{R}", flush=True)
    print(f"  {GREEN}  Escalated : {esc}", flush=True)
    print(f"  {GREEN}  Conflicts : {conflict_count}{R}", flush=True)
    print(f"  {GREEN}{'━'*66}{R}", flush=True)
    print(flush=True)
    _log(session_id, "session.end",
         {"elapsed_s": elapsed, "escalated": escalated,
          "conflicts": conflict_count})
    if _lf_enabled():
        _lf_close_root(session_id, response, escalated, elapsed)


def plan_built(session_id: str, plan: List[str],
               reasoning: str, complexity: str):
    _p(MAGENTA, "🗺️ ", "PLAN", "  →  ".join(plan), f"[{complexity.upper()}]")
    _p(MAGENTA, "   ", "  REASONING", reasoning[:110])
    _log(session_id, "orchestrator.plan",
         {"plan": plan, "reasoning": reasoning, "complexity": complexity})


def agent_start(session_id: str, agent: str):
    _p(CYAN, "▶  ", agent, "starting…")
    _log(session_id, f"{agent}.start", {})
    if _lf_enabled():
        _lf_open_agent(session_id, agent)


def agent_end(session_id: str, agent: str,
              duration: float, success: bool = True):
    color = GREEN if success else RED
    icon  = "✅" if success else "❌"
    _p(color, f"{icon} ", agent,
       "complete" if success else "FAILED", f"{duration:.2f}s")
    _log(session_id, f"{agent}.end",
         {"duration_s": duration, "success": success})
    if _lf_enabled():
        _lf_close_agent(session_id, agent, duration, success)


def tool_call(session_id: str, agent: str, tool: str,
              success: bool, preview: str = "", latency_ms: float = 0):
    status = f"{GREEN}✓ OK{R}" if success else f"{RED}✗ FAIL{R}"
    prev   = f"→ {preview[:55]}" if preview else ""
    _p(YELLOW, "🔧 ", f"  {tool}", f"{status}  {prev}", f"{latency_ms:.0f}ms")
    _log(session_id, f"tool.{tool}",
         {"agent": agent, "success": success,
          "latency_ms": round(latency_ms, 1)})
    _lf_update(session_id, agent, f"tool.{tool}",
               {"success": success, "latency_ms": round(latency_ms, 1)})


def llm_call(session_id: str, agent: str,
             prompt_tokens: int = 0, completion_tokens: int = 0,
             latency_ms: float = 0):
    toks = f"{prompt_tokens}→{completion_tokens} tok" if prompt_tokens else ""
    _p(BLUE, "🧠 ", f"  LLM [{agent}]",
       "llama-3.3-70b-versatile (Groq)", f"{toks}  {latency_ms:.0f}ms")
    _log(session_id, f"llm.{agent}",
         {"prompt_tokens": prompt_tokens,
          "completion_tokens": completion_tokens,
          "latency_ms": round(latency_ms, 1)})
    if _lf_enabled():
        _lf_log_generation(session_id, agent,
                           "llama-3.3-70b-versatile",
                           prompt_tokens, completion_tokens, latency_ms)


def finding(session_id: str, agent: str,
            text: str, confidence: str = "high"):
    icon  = {"high": "✅", "medium": "🟡", "low": "🔴"}.get(confidence, "✅")
    color = (GREEN if confidence == "high"
             else YELLOW if confidence == "medium" else RED)
    _p(color, f"{icon} ", f"  [{agent}]", text[:110], f"conf:{confidence}")
    _log(session_id, f"finding.{agent}",
         {"text": text, "confidence": confidence})
    _lf_update(session_id, agent, "finding",
               {"text": text[:200], "confidence": confidence})


def decision(session_id: str, point: str, choice: str,
             reasoning: str, by: str):
    _p(MAGENTA, "🎯 ", "DECISION",
       f"{point}  →  {BOLD}{choice}{R}", f"by {by}")
    _p(MAGENTA, "   ", "  REASON", reasoning[:110])
    _log(session_id, f"decision.{point}",
         {"choice": choice, "reasoning": reasoning, "by": by})
    _lf_update(session_id, by, f"decision.{point}",
               {"choice": choice, "reasoning": reasoning})


def conflict(session_id: str, src_a: str, src_b: str,
             desc: str, resolution: str):
    print(flush=True)
    _p(YELLOW, "⚠️ ", "CONFLICT DETECTED", f"{src_a}  vs  {src_b}")
    _p(YELLOW, "   ", "  ISSUE",    desc[:110])
    _p(GREEN,  "   ", "  RESOLVED", resolution[:110])
    print(flush=True)
    _log(session_id, "conflict.detected",
         {"src_a": src_a, "src_b": src_b,
          "description": desc, "resolution": resolution})


def escalation(session_id: str, ticket_id: str,
               priority: str, reason: str, team: str):
    print(flush=True)
    print(f"  {BG_RED}{WHITE}{BOLD}  🚨  ESCALATION TRIGGERED  {R}",
          flush=True)
    _p(RED, "   ", "  TICKET",   ticket_id)
    _p(RED, "   ", "  PRIORITY", priority)
    _p(RED, "   ", "  TEAM",     team)
    _p(RED, "   ", "  REASON",   reason[:110])
    print(flush=True)
    _log(session_id, "escalation.created",
         {"ticket_id": ticket_id, "priority": priority,
          "reason": reason, "team": team})
    _lf_update(session_id, "EscalationAgent", "escalation",
               {"ticket_id": ticket_id, "priority": priority, "team": team})


# ── Flask /api/traces endpoint ────────────────────────────────
def get_events() -> List[Dict]:
    return list(_events)


def clear_events():
    _events.clear()
