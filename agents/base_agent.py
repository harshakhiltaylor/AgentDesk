"""
base_agent.py
-------------
Abstract base every specialized agent inherits from.
Handles: LLM call, retry logic, structured output, memory write-back,
         and rich terminal tracing for every action.
"""
import os

# Load .env — ensures GROQ_API_KEY is available
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict

from openai import OpenAI  # Groq uses the OpenAI-compatible SDK

from memory.shared_context import SharedContext
from monitoring.tracing_utils import (
    log_agent_start, log_agent_complete, log_agent_error,
    log_tool_call, log_llm_call, log_finding,
)

logger = logging.getLogger("agentdesk.agents")

# ── Groq client (OpenAI-compatible endpoint) ─────────────────
_groq_key = os.getenv("GROQ_API_KEY", "")
if not _groq_key:
    print("\n  \033[31m\033[1m❌  ERROR: GROQ_API_KEY is not set!\033[0m")
    print("  \033[33m  1. Make sure your .env file exists in the project root (AgentDesk/.env)\033[0m")
    print("  \033[33m  2. It must contain:  GROQ_API_KEY=gsk_your_key_here\033[0m")
    print("  \033[33m  3. Get a free key at: https://console.groq.com/keys\033[0m\n")
    import sys; sys.exit(1)

_client = OpenAI(
    api_key=_groq_key,
    base_url="https://api.groq.com/openai/v1",
)
MODEL       = "llama-3.3-70b-versatile"
MAX_RETRIES = 2


class BaseAgent(ABC):

    name: str = "BaseAgent"
    role_description: str = "Generic support agent"

    def run(self, ctx: SharedContext, **kwargs) -> Dict:
        self._current_session_id = ctx.session_id  # used by _call_llm for token tracking
        log_agent_start(self.name, ctx.session_id)
        start = time.time()
        try:
            result = self._execute(ctx, **kwargs)
            duration = round(time.time() - start, 2)
            ctx.mark_agent_complete(self.name)
            log_agent_complete(self.name, duration)
            return result
        except Exception as e:
            ctx.mark_agent_failed(self.name, str(e))
            log_agent_error(self.name, str(e))
            return {"agent": self.name, "success": False, "error": str(e), "output": "Agent encountered an error."}

    @abstractmethod
    def _execute(self, ctx: SharedContext, **kwargs) -> Dict:
        """Subclasses implement real logic here."""

    def _call_llm(self, system: str, user: str, retries: int = MAX_RETRIES,
                  ctx=None) -> str:
        """
        Call Groq via OpenAI-compatible chat completions API.
        Logs every call + latency to terminal.
        Records token usage in TokenCounter.
        """
        t0 = time.time()
        for attempt in range(retries + 1):
            try:
                response = _client.chat.completions.create(
                    model=MODEL,
                    max_tokens=1024,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                )
                latency_ms = (time.time() - t0) * 1000
                usage      = getattr(response, "usage", None)
                p_tok      = getattr(usage, "prompt_tokens",     0)
                c_tok      = getattr(usage, "completion_tokens", 0)
                reply_text = response.choices[0].message.content

                log_llm_call(
                    agent=self.name,
                    tokens_in=p_tok,
                    tokens_out=c_tok,
                    latency_ms=latency_ms,
                )

                return reply_text
            except Exception as e:
                if attempt < retries:
                    logger.warning(f"[{self.name}] LLM retry {attempt+1}: {e}")
                    time.sleep(1.5 ** attempt)
                else:
                    raise

    def _safe_tool_call(self, tool_fn, *args, fallback=None, **kwargs):
        """
        Call a tool, log the result to terminal, return fallback on failure.
        """
        t0 = time.time()
        result = tool_fn(*args, **kwargs)
        latency_ms = (time.time() - t0) * 1000
        preview = str(result.data)[:60] if result.success and result.data else ""
        log_tool_call(
            agent=self.name,
            tool=result.tool_name,
            args=args,
            success=result.success,
            result_preview=preview,
            latency_ms=latency_ms,
        )
        if not result.success:
            return fallback
        return result.data
