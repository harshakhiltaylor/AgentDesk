"""
langfuse_setup.py
-----------------
Langfuse v3 SDK — correct initialisation.

v3 uses an OpenTelemetry-style context manager pattern.
The client manages trace context internally via Python's
contextvars — no trace_id needs to be passed around manually.

Correct v3 pattern:
  with client.start_as_current_observation(name="root", type="SPAN") as root:
      client.update_current_span(input={...}, metadata={...})
      with client.start_as_current_observation(name="agent", type="SPAN") as span:
          client.update_current_generation(model=..., usage={...})
      # span auto-closes on __exit__
  # root auto-closes on __exit__
  client.flush()
"""
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

LANGFUSE_ENABLED = False
_lf_client       = None

_pk   = os.getenv("LANGFUSE_PUBLIC_KEY",  "")
_sk   = os.getenv("LANGFUSE_SECRET_KEY",  "")
_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

if _pk and _sk:
    try:
        from langfuse import Langfuse
        _lf_client = Langfuse(
            public_key=_pk,
            secret_key=_sk,
            host=_host,
        )
        _lf_client.auth_check()
        LANGFUSE_ENABLED = True
        print(f"  \033[32m✅  Langfuse v3 connected → {_host}\033[0m")
    except ImportError:
        print("  \033[33m⚠️   langfuse not installed. Run: pip install langfuse\033[0m")
    except Exception as e:
        print(f"  \033[33m⚠️   Langfuse init error: {e}\033[0m")
        _lf_client = None
else:
    print("  \033[33m⚠️   Langfuse keys not set — terminal tracing only.\033[0m")
    print("  \033[33m     Add LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY to .env\033[0m")


def get_langfuse():
    return _lf_client
