"""
langfuse_config.py
------------------
Langfuse setup. If keys are not set, falls back to a no-op tracer
so the rest of the system works without Langfuse credentials.
"""
import os
import logging

logger = logging.getLogger("agentdesk.monitoring")

try:
    from langfuse import Langfuse
    _lf_client = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    )
    LANGFUSE_ENABLED = bool(os.getenv("LANGFUSE_PUBLIC_KEY"))
except Exception as e:
    logger.warning(f"Langfuse not available: {e}. Tracing disabled.")
    _lf_client = None
    LANGFUSE_ENABLED = False


def get_langfuse():
    return _lf_client
