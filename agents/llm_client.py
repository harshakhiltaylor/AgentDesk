"""
llm_client.py
-------------
Single Groq client shared across all LangGraph nodes.
Uses the OpenAI-compatible SDK.
"""
import os, time
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

from openai import OpenAI

_key = os.getenv("GROQ_API_KEY", "")
if not _key:
    import sys
    print("\n  \033[31m\033[1m❌  GROQ_API_KEY missing!\033[0m")
    print("  \033[33m  1. Create AgentDesk/.env\033[0m")
    print("  \033[33m  2. Add: GROQ_API_KEY=gsk_your_key\033[0m")
    print("  \033[33m  3. Free key: https://console.groq.com/keys\033[0m\n")
    sys.exit(1)

groq = OpenAI(api_key=_key, base_url="https://api.groq.com/openai/v1")
MODEL = "llama-3.3-70b-versatile"


def chat(system: str, user: str, max_tokens: int = 1024, retries: int = 2) -> tuple[str, int, int, float]:
    """
    Call Groq. Returns (content, prompt_tokens, completion_tokens, latency_ms).
    Retries on transient failures with exponential backoff.
    """
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            resp = groq.chat.completions.create(
                model=MODEL,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
            )
            latency = (time.time() - t0) * 1000
            usage   = resp.usage
            return (
                resp.choices[0].message.content,
                getattr(usage, "prompt_tokens",     0),
                getattr(usage, "completion_tokens", 0),
                latency,
            )
        except Exception as e:
            if attempt < retries:
                time.sleep(1.5 ** attempt)
            else:
                raise
