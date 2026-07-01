"""
tool_base.py
------------
Base class for all AgentDesk tools.
Provides: latency simulation, failure injection, structured logging.
"""
import time
import random
import logging
from typing import Any, Dict

logger = logging.getLogger("agentdesk.tools")


class ToolResult:
    def __init__(self, success: bool, data: Any = None, error: str = None, tool_name: str = ""):
        self.success = success
        self.data = data
        self.error = error
        self.tool_name = tool_name

    def to_dict(self) -> Dict:
        return {"success": self.success, "data": self.data, "error": self.error, "tool": self.tool_name}


class BaseTool:
    """
    All tools inherit from this. Wraps every call with:
      - Simulated network latency (50-300 ms)
      - Random failure injection (configurable rate)
      - Structured log entry
    """
    FAILURE_RATE = 0.08   # 8% chance of random tool failure
    MIN_LATENCY = 0.05
    MAX_LATENCY = 0.30

    def _simulate_latency(self):
        time.sleep(random.uniform(self.MIN_LATENCY, self.MAX_LATENCY))

    def _maybe_fail(self, tool_name: str) -> ToolResult | None:
        if random.random() < self.FAILURE_RATE:
            err = f"[{tool_name}] Simulated tool failure: database timeout"
            logger.warning(err)
            return ToolResult(success=False, error=err, tool_name=tool_name)
        return None

    def _call(self, tool_name: str, fn, *args, **kwargs) -> ToolResult:
        self._simulate_latency()
        failure = self._maybe_fail(tool_name)
        if failure:
            return failure
        try:
            result = fn(*args, **kwargs)
            logger.info(f"[{tool_name}] SUCCESS | args={args} kwargs={kwargs}")
            return ToolResult(success=True, data=result, tool_name=tool_name)
        except Exception as e:
            logger.error(f"[{tool_name}] ERROR: {e}")
            return ToolResult(success=False, error=str(e), tool_name=tool_name)
