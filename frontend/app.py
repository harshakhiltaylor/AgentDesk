"""
AgentDesk — Streamlit Frontend
LangGraph + Groq + Langfuse
"""
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

import streamlit as st
import requests
import time
import threading

API = "http://localhost:5001/api"

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="AgentDesk · Multi-Agent Support",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
.siq-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    padding: 1.4rem 2rem;
    border-radius: 12px;
    color: white;
    margin-bottom: 1.2rem;
    border: 1px solid #e94560;
}
.siq-header h1 { margin: 0; font-size: 1.85rem; letter-spacing: -0.5px; }
.siq-header p  { margin: 0.3rem 0 0; opacity: 0.78; font-size: 0.9rem; }

.siq-card { border: 1px solid #e2e8f0; border-radius: 9px; padding: 0.85rem 1rem; margin-bottom: 0.6rem; background: #f8fafc; }
.siq-card.ok   { border-left: 4px solid #48bb78; }
.siq-card.warn { border-left: 4px solid #ed8936; }
.siq-card.err  { border-left: 4px solid #fc8181; }

.siq-resp {
    background: #f0f7ff;
    border: 1px solid #90cdf4;
    border-left: 5px solid #3182ce;
    border-radius: 9px;
    padding: 1.3rem 1.5rem;
    font-size: 1.03rem;
    line-height: 1.8;
    color: #1a202c;
    white-space: pre-wrap;
}
.siq-esc {
    background: #fff5f5;
    border: 2px solid #fc8181;
    border-radius: 9px;
    padding: 0.9rem 1.3rem;
    margin-top: 0.8rem;
    color: #742a2a;
}
.siq-conflict {
    background: #fffaf0;
    border: 1px solid #f6ad55;
    border-left: 4px solid #ed8936;
    border-radius: 9px;
    padding: 0.85rem 1.2rem;
    margin-bottom: 0.6rem;
}
.siq-badge {
    display: inline-block;
    background: #2d3748;
    color: #e2e8f0;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.76rem;
    margin-right: 3px;
    margin-bottom: 3px;
    font-family: monospace;
}
.siq-cust-info {
    border-radius: 8px;
    padding: 0.65rem 0.9rem;
    font-size: 0.83rem;
    line-height: 1.65;
}
</style>
""", unsafe_allow_html=True)

# ── Scenario presets ───────────────────────────────────────────
SCENARIOS = {
    "1️⃣  Dark Mode Setup (Starter)": {
        "query": "How do I enable dark mode in my account?",
        "cid": "CUST-001",
        "hint": "Simple · 1 agent · No escalation",
    },
    "2️⃣  API Access on Starter Plan": {
        "query": "I'm on the Starter plan but I need API access for my automation workflow. What are my options?",
        "cid": "CUST-001",
        "hint": "Medium · Account + Feature agents",
    },
    "3️⃣  Pro Plan API Rate Limit Conflict": {
        "query": "Your documentation says the Pro plan includes unlimited API calls, but I'm getting rate limit errors after 1000 calls/month. My account shows Pro. Is this a bug or am I misunderstanding something?",
        "cid": "CUST-002",
        "hint": "High · Conflict detection · 3+ agents",
    },
    "4️⃣  SLA Violation — Escalate Now": {
        "query": "I have been waiting 10 days for a response on a critical production issue. My company has a contract with a 24-hour SLA guarantee. This is costing us $500 per day in lost revenue. Please verify the SLA was violated and escalate immediately.",
        "cid": "CUST-003",
        "hint": "High · P1 escalation · Contract agent",
    },
    "5️⃣  Seat Mismatch After Migration": {
        "query": "Our company just migrated from a competitor platform. We have 15 users but the plan shows only 10 seats. Can you help me understand the licensing model and set up all our users?",
        "cid": "CUST-004",
        "hint": "Medium · Seat overage · Onboarding",
    },
}

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 AgentDesk")
    st.caption("Multi-Agent Customer Support Intelligence")
    st.divider()

    # ── Backend health ────────────────────────────────────────
    try:
        h = requests.get(f"{API}/health", timeout=3)
        if h.ok:
            st.success("✅ Backend online")
        else:
            st.error("❌ Backend returned error")
    except Exception:
        st.error("❌ Backend offline")
        st.code("python app.py", language="bash")

    st.divider()

    # ── Customer selector ─────────────────────────────────────
    st.markdown("### 👤 Select Customer")
    try:
        custs_resp = requests.get(f"{API}/customers", timeout=5)
        custs = custs_resp.json() if custs_resp.ok else []
    except Exception:
        custs = []

    cmap = {"— Anonymous (no customer) —": None}
    for c in custs:
        icon = "🟢" if c["status"] == "active" else "🔴"
        label = f"{icon} {c['name']} · {c['plan'].upper()}"
        cmap[label] = c["id"]

    sel_label = st.selectbox(
        "Customer",
        list(cmap.keys()),
        label_visibility="collapsed",
    )
    sel_cid = cmap[sel_label]

    if sel_cid:
        cust_detail = next((x for x in custs if x["id"] == sel_cid), None)
        if cust_detail:
            is_active = cust_detail["status"] == "active"
            bg = "#f0fff4" if is_active else "#fff5f5"
            bd = "#9ae6b4" if is_active else "#fc8181"
            st.markdown(
                f'<div class="siq-cust-info" style="background:{bg};border:1px solid {bd};">'
                f'<b>ID:</b> {cust_detail["id"]}<br>'
                f'<b>Company:</b> {cust_detail["company"]}<br>'
                f'<b>Plan:</b> {cust_detail["plan"].upper()}<br>'
                f'<b>Status:</b> {cust_detail["status"].upper()}'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Scenario picker ───────────────────────────────────────
    st.markdown("### 📋 Test Scenarios")
    sc_choice = st.selectbox(
        "Preset",
        ["— Type your own query —"] + list(SCENARIOS.keys()),
        label_visibility="collapsed",
    )
    if sc_choice != "— Type your own query —":
        st.caption(f"💡 {SCENARIOS[sc_choice]['hint']}")

    st.divider()
    st.markdown("### ⚙️ Tech Stack")
    st.caption("**Orchestration:** LangGraph")
    st.caption("**LLM:** Groq · llama-3.3-70b-versatile")
    st.caption("**Observability:** Langfuse")
    st.caption("**Backend:** Flask  |  **UI:** Streamlit")


# ─────────────────────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="siq-header">'
    '<h1>🤖 AgentDesk</h1>'
    '<p>Multi-Agent Customer Support Intelligence &nbsp;·&nbsp; '
    'LangGraph + Groq + Langfuse</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Query input ────────────────────────────────────────────────
if sc_choice != "— Type your own query —":
    default_query = SCENARIOS[sc_choice]["query"]
else:
    default_query = ""

query = st.text_area(
    "💬 Customer Query",
    value=default_query,
    height=110,
    placeholder="Type a support query here, or load a preset scenario from the sidebar…",
)

btn_col, tip_col = st.columns([1, 5])
with btn_col:
    go = st.button("🚀  Investigate", use_container_width=True)
with tip_col:
    if not sel_cid:
        st.info("💡 Select a customer from the sidebar to enable account, billing and contract investigation.")


# ─────────────────────────────────────────────────────────────
# PROCESSING
# ─────────────────────────────────────────────────────────────
if go:
    if not query.strip():
        st.warning("⚠️ Please enter a query before clicking Investigate.")
        st.stop()

    st.divider()
    st.markdown("### 🔄 Investigation Running…")
    prog_bar  = st.progress(0)
    status_el = st.empty()

    STEPS = [
        "🧠 Orchestrator analyzing query and building plan…",
        "🔍 Agents gathering data from tools…",
        "⚖️  Cross-referencing findings…",
        "✍️  Synthesizing final response…",
    ]

    t_start = time.time()
    result_holder: dict = {}

    def _api_call():
        try:
            r = requests.post(
                f"{API}/query",
                json={"query": query, "customer_id": sel_cid},
                timeout=180,
            )
            result_holder["response"] = r
        except Exception as exc:
            result_holder["error"] = str(exc)

    thread = threading.Thread(target=_api_call, daemon=True)
    thread.start()

    step_i = 0
    while thread.is_alive():
        status_el.info(STEPS[step_i % len(STEPS)])
        prog_bar.progress(min(10 + step_i * 18, 88))
        step_i += 1
        time.sleep(1.8)

    thread.join()
    prog_bar.progress(100)
    status_el.empty()
    elapsed = round(time.time() - t_start, 1)

    # ── Error handling ─────────────────────────────────────────
    if "error" in result_holder:
        st.error(f"❌ Connection error: {result_holder['error']}\n\nMake sure Flask is running: `python app.py`")
        st.stop()

    api_resp = result_holder.get("response")
    if api_resp is None or not api_resp.ok:
        code = api_resp.status_code if api_resp else "?"
        body = api_resp.text[:300] if api_resp else "No response"
        st.error(f"❌ Backend error {code}: {body}")
        st.stop()

    data = api_resp.json()
    if not data.get("success"):
        st.error(f"❌ Processing failed: {data.get('error', 'Unknown error')}")
        if data.get("error"):
            with st.expander("Error details"):
                st.code(data["error"])
        st.stop()

    # ── Summary metrics ────────────────────────────────────────
    plan       = data.get("plan", [])
    complexity = data.get("complexity", "medium")
    escalated  = data.get("escalated", False)
    conflicts  = data.get("conflicts", [])
    findings   = data.get("findings", [])
    decisions  = data.get("decisions", [])
    cx_icon    = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(complexity, "🟡")

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    mc1.metric("⏱️ Duration",    f"{elapsed}s")
    mc2.metric("🤖 Agents Run", len([a for a in plan if a != "EscalationAgent"]) + 1)
    mc3.metric(f"{cx_icon} Complexity", complexity.capitalize())
    mc4.metric("⚠️ Conflicts",  len(conflicts))
    mc5.metric("🚨 Escalated",  "YES 🚨" if escalated else "NO ✅")
    st.divider()

    # ── Investigation plan ─────────────────────────────────────
    st.markdown("### 🗺️ Investigation Plan")
    badges_html = ""
    for idx, agent_name in enumerate(plan):
        arrow = "→ " if idx > 0 else ""
        badges_html += f'<span class="siq-badge">{arrow}{agent_name}</span>'
    st.markdown(f'<div style="margin: 0.4rem 0 0.3rem">{badges_html}</div>', unsafe_allow_html=True)
    if data.get("plan_reasoning"):
        st.caption(f"**Orchestrator reasoning:** {data['plan_reasoning']}")
    st.divider()

    # ── Final response ─────────────────────────────────────────
    st.markdown("### 💬 Support Response")
    response_text = data.get("response", "No response generated.")
    # Use st.markdown inside a container for proper rendering
    with st.container():
        st.markdown(
            f'<div class="siq-resp">{response_text}</div>',
            unsafe_allow_html=True,
        )

    # Escalation ticket
    ticket = data.get("escalation_ticket")
    if escalated and ticket:
        st.markdown(
            f'<div class="siq-esc">'
            f'<b>🚨 Escalation Ticket Created</b><br>'
            f'<b>Ticket ID:</b> <code>{ticket.get("ticket_id", "N/A")}</code>'
            f' &nbsp;|&nbsp; <b>Priority:</b> {ticket.get("priority", "N/A")}'
            f' &nbsp;|&nbsp; <b>Created:</b> {str(ticket.get("created_at", ""))[:19]}<br>'
            f'<b>Reason:</b> {ticket.get("reason", "N/A")}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Detail tabs ────────────────────────────────────────────
    tab_findings, tab_decisions, tab_conflicts, tab_raw = st.tabs([
        f"🔍 Agent Findings ({len(findings)})",
        f"📊 Decision Log ({len(decisions)})",
        f"⚠️ Conflicts ({len(conflicts)})",
        "🗂️ Raw JSON",
    ])

    with tab_findings:
        if findings:
            for finding in findings:
                agent      = finding.get("agent", "?")
                finding_text = finding.get("finding", "")
                confidence = finding.get("confidence", "high")
                conf_icon  = {"high": "✅", "medium": "🟡", "low": "🔴"}.get(confidence, "✅")
                card_cls   = "ok" if confidence == "high" else ("warn" if confidence == "medium" else "err")
                st.markdown(
                    f'<div class="siq-card {card_cls}">'
                    f'<b>{conf_icon} {agent}</b>'
                    f' &nbsp;<small style="color:#718096; font-size:0.78rem;">confidence: {confidence}</small><br>'
                    f'<span style="color:#2d3748; font-size:0.95rem;">{finding_text}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                raw_data = finding.get("data")
                if raw_data:
                    with st.expander(f"📦 {agent} — raw tool data"):
                        st.json(raw_data)
        else:
            st.info("No agent findings recorded for this session.")

    with tab_decisions:
        if decisions:
            for dec in decisions:
                st.markdown(
                    f'<div class="siq-card ok">'
                    f'<b>🎯 {dec.get("decision_point", "?")}</b>'
                    f' &nbsp;<small style="color:#718096; font-size:0.78rem;">by {dec.get("made_by", "?")}</small><br>'
                    f'<b>Choice:</b> <code>{dec.get("choice", "?")}</code><br>'
                    f'<span style="color:#4a5568; font-size:0.93rem;">{dec.get("reasoning", "")}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No decisions recorded for this session.")

    with tab_conflicts:
        if conflicts:
            for conf_item in conflicts:
                st.markdown(
                    f'<div class="siq-conflict">'
                    f'<b>⚠️ Conflict Detected &amp; Resolved</b><br>'
                    f'<b>Source A:</b> <code>{conf_item.get("source_a", "?")}</code><br>'
                    f'<b>Source B:</b> <code>{conf_item.get("source_b", "?")}</code><br>'
                    f'<b>Issue:</b> {conf_item.get("description", "")}<br>'
                    f'<b>Resolution:</b> {conf_item.get("resolution", "")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("✅ No data conflicts detected in this investigation.")

    with tab_raw:
        st.json(data)

# ── Footer ─────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center; color:#a0aec0; font-size:0.78rem;'>"
    "AgentDesk &nbsp;·&nbsp; LangGraph + Groq (Llama-3.3-70B) + Langfuse + Flask + Streamlit"
    "</p>",
    unsafe_allow_html=True,
)
