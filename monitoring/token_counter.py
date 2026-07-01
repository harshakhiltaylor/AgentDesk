"""
token_counter.py
----------------
Utility to calculate token counts for Groq/Llama inputs and outputs.

Three methods available:
  1. EXACT   — via tiktoken (cl100k_base encoding, close enough for Llama)
  2. APPROX  — chars / 4  (good rule of thumb, no dependencies)
  3. GROQ    — actual tokens returned in API response (already logged in llm_call)

Usage:
  from monitoring.token_counter import count_tokens, estimate_cost, summarise

  count_tokens("your text here")          → int
  estimate_cost(prompt_tokens=500,
                completion_tokens=200)    → dict with cost breakdown
  summarise(prompt, response)             → prints a full report
"""
import re


# ── Groq Llama-3.3-70b pricing (as of 2025) ──────────────────
# Free tier: no charge. Paid tier (if applicable):
PRICE_PER_1K_INPUT_TOKENS  = 0.00059   # USD per 1K input tokens
PRICE_PER_1K_OUTPUT_TOKENS = 0.00079   # USD per 1K output tokens


# ─────────────────────────────────────────────────────────────
# CORE COUNTER
# ─────────────────────────────────────────────────────────────

def count_tokens(text: str, method: str = "auto") -> int:
    """
    Count tokens in a string.

    method:
      "tiktoken" — exact, uses tiktoken library (pip install tiktoken)
      "approx"   — chars/4, no dependencies, ~±10% accuracy
      "auto"     — tries tiktoken first, falls back to approx
    """
    if not text:
        return 0

    if method in ("tiktoken", "auto"):
        try:
            import tiktoken
            # cl100k_base is used by GPT-4 and is close to Llama tokenisation
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except ImportError:
            if method == "tiktoken":
                raise ImportError(
                    "tiktoken not installed. Run: pip install tiktoken"
                )
            # fall through to approx

    # Approx: ~4 chars per token (standard rule of thumb)
    return max(1, len(text) // 4)


def count_messages(messages: list, method: str = "auto") -> dict:
    """
    Count tokens for a list of OpenAI-style message dicts.
    Returns {"total": N, "by_role": {"system": N, "user": N, ...}}
    """
    by_role = {}
    for msg in messages:
        role    = msg.get("role", "unknown")
        content = msg.get("content", "")
        toks    = count_tokens(content, method)
        by_role[role] = by_role.get(role, 0) + toks

    return {
        "total":   sum(by_role.values()),
        "by_role": by_role,
    }


# ─────────────────────────────────────────────────────────────
# COST CALCULATOR
# ─────────────────────────────────────────────────────────────

def estimate_cost(prompt_tokens: int, completion_tokens: int) -> dict:
    """
    Estimate USD cost for one API call.
    Returns a breakdown dict.
    """
    input_cost  = (prompt_tokens    / 1000) * PRICE_PER_1K_INPUT_TOKENS
    output_cost = (completion_tokens / 1000) * PRICE_PER_1K_OUTPUT_TOKENS
    total_cost  = input_cost + output_cost

    return {
        "prompt_tokens":     prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens":      prompt_tokens + completion_tokens,
        "input_cost_usd":    round(input_cost,  6),
        "output_cost_usd":   round(output_cost, 6),
        "total_cost_usd":    round(total_cost,  6),
    }


# ─────────────────────────────────────────────────────────────
# FULL REPORT
# ─────────────────────────────────────────────────────────────

def summarise(prompt: str, response: str,
              method: str = "auto",
              actual_prompt_tokens: int = None,
              actual_completion_tokens: int = None):
    """
    Print a full token + cost report for one LLM call.

    Pass actual_prompt_tokens / actual_completion_tokens if you have
    them from the Groq API response (they are logged in llm_call).
    If not passed, estimates are used.
    """
    est_prompt     = count_tokens(prompt,   method)
    est_completion = count_tokens(response, method)

    pt = actual_prompt_tokens     if actual_prompt_tokens     is not None else est_prompt
    ct = actual_completion_tokens if actual_completion_tokens is not None else est_completion

    cost = estimate_cost(pt, ct)

    mode = "actual (from API)" if actual_prompt_tokens is not None else "estimated"

    CYAN  = "\033[36m"; GREEN = "\033[32m"; YELLOW = "\033[33m"
    BOLD  = "\033[1m";  DIM   = "\033[2m";  R      = "\033[0m"

    print(flush=True)
    print(f"  {CYAN}{'─'*52}{R}", flush=True)
    print(f"  {CYAN}{BOLD}  🔢  TOKEN REPORT  ({mode}){R}", flush=True)
    print(f"  {CYAN}{'─'*52}{R}", flush=True)
    print(f"  {YELLOW}  Input  (prompt)   : {BOLD}{pt:>8,} tokens{R}", flush=True)
    print(f"  {GREEN}  Output (response) : {BOLD}{ct:>8,} tokens{R}", flush=True)
    print(f"  {BOLD}  Total             : {BOLD}{pt+ct:>8,} tokens{R}", flush=True)
    print(f"  {DIM}  ── Cost breakdown ──────────────────{R}", flush=True)
    print(f"  {DIM}  Input  cost : ${cost['input_cost_usd']:.6f}{R}", flush=True)
    print(f"  {DIM}  Output cost : ${cost['output_cost_usd']:.6f}{R}", flush=True)
    print(f"  {BOLD}  Total  cost : ${cost['total_cost_usd']:.6f} USD{R}", flush=True)
    print(f"  {CYAN}{'─'*52}{R}", flush=True)
    print(flush=True)

    return cost
