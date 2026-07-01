"""
app.py — AgentDesk Flask Backend
"""
import os, sys, logging
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

log = logging.getLogger("werkzeug"); log.setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO,
    format="  %(asctime)s.%(msecs)03d  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S", stream=sys.stdout)

from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.graph import run_investigation
from monitoring.tracer import get_events, clear_events
from data.mock_data import CUSTOMERS

app = Flask(__name__)
CORS(app)


def _banner():
    c="\033[36m"; g="\033[32m"; b="\033[1m"; r="\033[0m"
    print(flush=True)
    print(f"  {c}{'━'*60}{r}", flush=True)
    print(f"  {c}{b}  🤖  AgentDesk (Agent Days) — LangGraph + Groq + Langfuse{r}", flush=True)
    print(f"  {c}  Stack    : LangGraph · llama-3.3-70b-versatile · Langfuse{r}", flush=True)
    print(f"  {c}  API      : http://localhost:5001{r}", flush=True)
    print(f"  {c}  Traces   : http://localhost:5001/api/traces{r}", flush=True)
    print(f"  {c}{'━'*60}{r}", flush=True)
    print(flush=True)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "stack": "LangGraph+Groq+Langfuse"})

@app.route("/api/customers")
def customers():
    return jsonify([
        {"id": cid, "name": c["name"], "company": c["company"],
         "plan": c["plan"], "status": c["account_status"]}
        for cid, c in CUSTOMERS.items()
    ])

@app.route("/api/query", methods=["POST"])
def query():
    body        = request.get_json(force=True)
    q           = (body.get("query") or "").strip()
    customer_id = (body.get("customer_id") or "").strip() or None
    if not q:
        return jsonify({"error": "query is required"}), 400
    try:
        result = run_investigation(q, customer_id)
        return jsonify({"success": True, **result})
    except Exception as e:
        logging.error(f"Query failed: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/traces")
def traces():
    return jsonify(get_events())

@app.route("/api/traces/clear", methods=["POST"])
def clear():
    clear_events(); return jsonify({"cleared": True})

@app.route("/api/session/<sid>")
def session(sid):
    return jsonify({"note": "Use /api/traces for full event log", "session_id": sid})

if __name__ == "__main__":
    _banner()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)), debug=False, use_reloader=False)
