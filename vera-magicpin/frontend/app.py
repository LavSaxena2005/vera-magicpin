"""
Vera by magicpin — Streamlit Frontend
Modern dark-glass UI for the Vera Message Engine
"""

import json
import streamlit as st
import requests
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vera · magicpin AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #080c14;
    --surface: #0f1623;
    --surface2: #151e2e;
    --border: rgba(99,179,255,0.12);
    --accent: #3b82f6;
    --accent2: #06b6d4;
    --gold: #f59e0b;
    --green: #10b981;
    --red: #ef4444;
    --text: #e2e8f0;
    --muted: #64748b;
    --glow: 0 0 24px rgba(59,130,246,0.15);
}

html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'Sora', sans-serif !important;
    color: var(--text) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { display: none !important; }
.block-container { padding: 0 2rem 2rem !important; max-width: 100% !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: var(--glow) !important;
}

/* Labels */
label, .stSelectbox label, [data-testid="stMarkdownContainer"] p {
    color: var(--muted) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 2rem !important;
    letter-spacing: 0.04em !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 30px rgba(59,130,246,0.45) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}

/* Cards */
.vera-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: var(--glow);
    transition: all 0.2s;
}
.vera-card:hover { border-color: rgba(99,179,255,0.25); }

.vera-message-box {
    background: linear-gradient(135deg, #0f2040, #091828);
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 16px;
    padding: 1.6rem;
    margin: 1rem 0;
    position: relative;
    overflow: hidden;
}
.vera-message-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.vera-message-text {
    font-size: 1.15rem;
    font-weight: 500;
    color: #f0f9ff;
    line-height: 1.6;
    margin-bottom: 1rem;
}
.vera-cta-pill {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: white;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 0.35rem 1rem;
    border-radius: 100px;
    letter-spacing: 0.05em;
}
.vera-meta-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 0.8rem;
}
.vera-badge {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-size: 0.72rem;
    color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
}
.score-bar-wrap { margin: 0.3rem 0; }
.score-label { font-size: 0.75rem; color: var(--muted); margin-bottom: 0.2rem; }
.score-bar {
    height: 6px;
    background: var(--surface2);
    border-radius: 100px;
    overflow: hidden;
}
.score-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    transition: width 0.6s ease;
}

.header-logo {
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, #3b82f6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.header-sub {
    font-size: 0.78rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px rgba(16,185,129,0.7);
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.chat-bubble-vera {
    background: linear-gradient(135deg, #0f2040, #091828);
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 14px 14px 14px 4px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    max-width: 85%;
    font-size: 0.9rem;
    color: #e0f0ff;
}
.chat-bubble-merchant {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 14px 14px 4px 14px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0 0.5rem auto;
    max-width: 75%;
    font-size: 0.9rem;
    text-align: right;
    color: var(--text);
}
.section-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────

def api_url():
    return st.session_state.get("bot_url", "http://localhost:8000").rstrip("/")


def check_health():
    try:
        r = requests.get(f"{api_url()}/v1/healthz", timeout=4)
        return r.status_code == 200
    except Exception:
        return False


def push_context(scope, context_id, version, payload):
    try:
        r = requests.post(f"{api_url()}/v1/context", json={
            "scope": scope,
            "context_id": context_id,
            "version": version,
            "payload": payload,
            "delivered_at": datetime.utcnow().isoformat() + "Z"
        }, timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500


def call_tick(merchant_id, trigger, customer=None):
    try:
        payload = {
            "session_id": f"session_{merchant_id}",
            "merchant_id": merchant_id,
            "trigger": trigger
        }
        if customer:
            payload["customer"] = customer
        r = requests.post(f"{api_url()}/v1/tick", json=payload, timeout=30)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500


def call_reply(merchant_id, reply_text, prior_message=""):
    try:
        r = requests.post(f"{api_url()}/v1/reply", json={
            "session_id": f"session_{merchant_id}",
            "merchant_id": merchant_id,
            "reply_text": reply_text,
            "prior_message": prior_message
        }, timeout=30)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500


# ── Session State Defaults ─────────────────────────────────────────────────
if "bot_url" not in st.session_state:
    st.session_state.bot_url = "http://localhost:8000"
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "merchant_context_pushed" not in st.session_state:
    st.session_state.merchant_context_pushed = False


# ── SAMPLE DATA ────────────────────────────────────────────────────────────
SAMPLE_MERCHANTS = {
    "Dr. Meera Dental Clinic": {
        "id": "m_001_drmeera",
        "json": {
            "identity": {
                "id": "m_001_drmeera",
                "name": "Dr. Meera Dental Clinic",
                "category": "dentist",
                "locality": "Koramangala, Bengaluru",
                "owner": "Dr. Meera Sharma"
            },
            "performance": {
                "avg_rating": 4.6,
                "total_reviews": 214,
                "monthly_views": 1820,
                "repeat_customer_rate": 0.38,
                "orders_last_30d": 47,
                "orders_prev_30d": 61
            },
            "offers": [
                {"id": "o1", "title": "Dental Check-Up @ ₹299", "original_price": 800, "discount_pct": 63, "active": True},
                {"id": "o2", "title": "Teeth Whitening @ ₹1499", "original_price": 3000, "discount_pct": 50, "active": True}
            ],
            "conversation_history": []
        }
    },
    "Glamour Salon": {
        "id": "m_002_glamour",
        "json": {
            "identity": {
                "id": "m_002_glamour",
                "name": "Glamour Salon",
                "category": "salon",
                "locality": "Indiranagar, Bengaluru",
                "owner": "Priya Kapoor"
            },
            "performance": {
                "avg_rating": 4.4,
                "total_reviews": 189,
                "monthly_views": 2300,
                "repeat_customer_rate": 0.52,
                "orders_last_30d": 88,
                "orders_prev_30d": 72
            },
            "offers": [
                {"id": "o1", "title": "Bridal Package @ ₹4999", "original_price": 8000, "discount_pct": 37, "active": True},
                {"id": "o2", "title": "Hair Spa + Colour @ ₹1799", "original_price": 2800, "discount_pct": 36, "active": True}
            ],
            "conversation_history": []
        }
    },
    "Spice Route Restaurant": {
        "id": "m_003_spiceroute",
        "json": {
            "identity": {
                "id": "m_003_spiceroute",
                "name": "Spice Route Restaurant",
                "category": "restaurant",
                "locality": "HSR Layout, Bengaluru",
                "owner": "Rajesh Nair"
            },
            "performance": {
                "avg_rating": 4.2,
                "total_reviews": 341,
                "monthly_views": 4100,
                "repeat_customer_rate": 0.29,
                "orders_last_30d": 312,
                "orders_prev_30d": 290
            },
            "offers": [
                {"id": "o1", "title": "Lunch Thali @ ₹149", "original_price": 220, "discount_pct": 32, "active": True},
                {"id": "o2", "title": "Family Combo (4 pax) @ ₹599", "original_price": 900, "discount_pct": 33, "active": False}
            ],
            "conversation_history": []
        }
    },
    "FitZone Gym": {
        "id": "m_004_fitzone",
        "json": {
            "identity": {
                "id": "m_004_fitzone",
                "name": "FitZone Gym",
                "category": "gym",
                "locality": "Whitefield, Bengaluru",
                "owner": "Arjun Singh"
            },
            "performance": {
                "avg_rating": 4.5,
                "total_reviews": 127,
                "monthly_views": 890,
                "repeat_customer_rate": 0.65,
                "orders_last_30d": 23,
                "orders_prev_30d": 31
            },
            "offers": [
                {"id": "o1", "title": "1-Month Membership @ ₹999", "original_price": 1800, "discount_pct": 44, "active": True},
                {"id": "o2", "title": "Free Trial Week", "original_price": 0, "discount_pct": 100, "active": True}
            ],
            "conversation_history": []
        }
    },
    "HealthFirst Pharmacy": {
        "id": "m_005_healthfirst",
        "json": {
            "identity": {
                "id": "m_005_healthfirst",
                "name": "HealthFirst Pharmacy",
                "category": "pharmacy",
                "locality": "JP Nagar, Bengaluru",
                "owner": "Sunita Reddy"
            },
            "performance": {
                "avg_rating": 4.7,
                "total_reviews": 98,
                "monthly_views": 650,
                "repeat_customer_rate": 0.71,
                "orders_last_30d": 134,
                "orders_prev_30d": 141
            },
            "offers": [
                {"id": "o1", "title": "Monsoon Health Kit @ ₹299", "original_price": 450, "discount_pct": 33, "active": True},
                {"id": "o2", "title": "10% off on all generics", "original_price": None, "discount_pct": 10, "active": True}
            ],
            "conversation_history": []
        }
    }
}

SAMPLE_TRIGGERS = {
    "Research Spike": {
        "type": "research",
        "search_term": "Dental Check Up",
        "local_searches": 190,
        "locality": "Koramangala",
        "timestamp": "2026-05-02T10:00:00Z"
    },
    "Order Dip": {
        "type": "dip",
        "metric": "orders",
        "change_pct": -23,
        "period": "last_7d",
        "timestamp": "2026-05-02T08:00:00Z"
    },
    "Traffic Spike": {
        "type": "spike",
        "metric": "views",
        "change_pct": 42,
        "period": "last_24h",
        "timestamp": "2026-05-02T09:00:00Z"
    },
    "Festival Recall": {
        "type": "festival",
        "festival": "Eid al-Adha",
        "days_until": 3,
        "date": "2026-05-02",
        "timestamp": "2026-05-02T07:00:00Z"
    },
    "Recall (Lapsed Customer)": {
        "type": "recall",
        "last_visit_days": 45,
        "customer_segment": "lapsed",
        "timestamp": "2026-05-02T11:00:00Z"
    }
}

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="header-logo">✦ Vera</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-sub">by magicpin · Message Engine</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.session_state.bot_url = st.text_input("🔗 Bot Base URL", value=st.session_state.bot_url, help="Your deployed bot URL")

    healthy = check_health()
    if healthy:
        st.markdown('<span class="status-dot"></span><span style="font-size:0.8rem;color:#10b981">Engine Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#ef4444;margin-right:6px;"></span><span style="font-size:0.8rem;color:#ef4444">Engine Offline</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">Quick Reference</div>', unsafe_allow_html=True)
    st.markdown("""
<div style="font-size:0.75rem;color:#64748b;line-height:2">
<b style="color:#3b82f6">POST</b> /v1/context<br>
<b style="color:#3b82f6">POST</b> /v1/tick<br>
<b style="color:#3b82f6">POST</b> /v1/reply<br>
<b style="color:#06b6d4">GET</b> &nbsp;/v1/healthz<br>
<b style="color:#06b6d4">GET</b> &nbsp;/v1/metadata
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">Scoring Rubric</div>', unsafe_allow_html=True)
    dims = [
        ("Decision Quality", 0.9),
        ("Specificity", 0.85),
        ("Category Fit", 0.88),
        ("Merchant Fit", 0.87),
        ("Engagement", 0.92),
    ]
    for label, val in dims:
        st.markdown(f"""
<div class="score-bar-wrap">
<div class="score-label">{label}</div>
<div class="score-bar"><div class="score-fill" style="width:{int(val*100)}%"></div></div>
</div>""", unsafe_allow_html=True)


# ── HEADER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:2rem 0 1.5rem">
  <div style="font-size:2.2rem;font-weight:700;letter-spacing:-0.04em;background:linear-gradient(135deg,#3b82f6,#06b6d4,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent">
    Vera Message Engine
  </div>
  <div style="font-size:0.85rem;color:#64748b;margin-top:0.3rem">
    India's Largest Retailer AI · Merchant Growth Assistant · magicpin Challenge
  </div>
</div>
""", unsafe_allow_html=True)

# ── MAIN TABS ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["⚡ Compose", "📦 Context Manager", "💬 Conversation", "🔧 API Explorer"])

# ════════════════════════════════════════════════════════
# TAB 1 — COMPOSE
# ════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="section-title">Merchant & Trigger</div>', unsafe_allow_html=True)

        merchant_choice = st.selectbox("Select Merchant", list(SAMPLE_MERCHANTS.keys()))
        selected_merchant = SAMPLE_MERCHANTS[merchant_choice]

        trigger_choice = st.selectbox("Select Trigger", list(SAMPLE_TRIGGERS.keys()))
        selected_trigger = SAMPLE_TRIGGERS[trigger_choice]

        with st.expander("✏️ Edit Merchant JSON", expanded=False):
            merchant_json_str = st.text_area(
                "Merchant JSON",
                value=json.dumps(selected_merchant["json"], indent=2),
                height=250,
                label_visibility="collapsed"
            )

        with st.expander("✏️ Edit Trigger JSON", expanded=False):
            trigger_json_str = st.text_area(
                "Trigger JSON",
                value=json.dumps(selected_trigger, indent=2),
                height=150,
                label_visibility="collapsed"
            )

        include_customer = st.checkbox("Include customer context")
        customer_json_str = None
        if include_customer:
            default_customer = {
                "id": "c_001",
                "name": "Priya",
                "consent": True,
                "last_visit_days": 38,
                "relationship": "repeat",
                "preferred_channel": "whatsapp"
            }
            customer_json_str = st.text_area("Customer JSON", value=json.dumps(default_customer, indent=2), height=120)

        if st.button("✦ Generate Message", use_container_width=True):
            try:
                merchant_data = json.loads(merchant_json_str)
                trigger_data = json.loads(trigger_json_str)
                customer_data = json.loads(customer_json_str) if customer_json_str else None
            except json.JSONDecodeError as e:
                st.error(f"JSON parse error: {e}")
                st.stop()

            merchant_id = merchant_data.get("identity", {}).get("id", selected_merchant["id"])

            # Push context if needed
            push_res, push_status = push_context(
                scope="merchant",
                context_id=merchant_id,
                version=int(datetime.utcnow().timestamp()),
                payload=merchant_data
            )

            # Call tick
            with st.spinner("Vera is thinking..."):
                result, status = call_tick(merchant_id, trigger_data, customer_data)

            if status == 200 and "message" in result:
                st.session_state.last_result = result
                st.session_state.chat_history.append({
                    "role": "vera",
                    "text": result["message"],
                    "cta": result.get("cta"),
                    "trigger": trigger_choice
                })
            else:
                st.error(f"Error {status}: {json.dumps(result, indent=2)}")

    with col_right:
        st.markdown('<div class="section-title">Generated Message</div>', unsafe_allow_html=True)

        if st.session_state.last_result:
            r = st.session_state.last_result
            st.markdown(f"""
<div class="vera-message-box">
  <div style="font-size:0.7rem;color:#3b82f6;font-weight:600;letter-spacing:0.12em;margin-bottom:0.8rem">VERA · {datetime.now().strftime("%H:%M")}</div>
  <div class="vera-message-text">{r.get('message','')}</div>
  <span class="vera-cta-pill">▸ {r.get('cta','')}</span>
  <div class="vera-meta-row">
    <span class="vera-badge">as: {r.get('send_as','')}</span>
    <span class="vera-badge">key: {r.get('suppression_key','')[:12]}…</span>
  </div>
</div>
""", unsafe_allow_html=True)

            st.markdown(f"""
<div class="vera-card">
  <div class="section-title">Rationale</div>
  <div style="font-size:0.88rem;color:#94a3b8;line-height:1.6">{r.get('rationale','')}</div>
</div>
""", unsafe_allow_html=True)

            with st.expander("📋 Raw JSON Response"):
                st.json(r)
        else:
            st.markdown("""
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:300px;color:#1e3a5f;border:2px dashed #1e3a5f;border-radius:16px;text-align:center">
  <div style="font-size:2rem;margin-bottom:0.5rem">✦</div>
  <div style="font-size:0.9rem">Select a merchant & trigger,<br>then click Generate Message</div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# TAB 2 — CONTEXT MANAGER
# ════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Push Merchant Context</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        scope = st.selectbox("Scope", ["merchant", "customer", "trigger"])
        context_id = st.text_input("Context ID", value="m_001_drmeera")
        version = st.number_input("Version", min_value=1, value=1, step=1)
        payload_str = st.text_area(
            "Payload JSON",
            value=json.dumps(SAMPLE_MERCHANTS["Dr. Meera Dental Clinic"]["json"], indent=2),
            height=280
        )

        if st.button("📤 Push Context", use_container_width=True):
            try:
                payload = json.loads(payload_str)
            except Exception as e:
                st.error(f"JSON error: {e}")
                st.stop()
            res, status = push_context(scope, context_id, int(version), payload)
            if status == 200:
                if res.get("accepted"):
                    st.success(f"✅ Context stored | ack: `{res.get('ack_id')}`")
                else:
                    st.info(f"ℹ️ No-op: same version already stored | ack: `{res.get('ack_id')}`")
            else:
                st.error(f"Error {status}: {res}")

    with col2:
        st.markdown('<div class="section-title">Sample Payloads</div>', unsafe_allow_html=True)
        for name, data in SAMPLE_MERCHANTS.items():
            with st.expander(f"🏪 {name}"):
                st.json(data["json"])
                if st.button(f"Push {name}", key=f"push_{data['id']}"):
                    res, status = push_context("merchant", data["id"], 1, data["json"])
                    if status == 200:
                        st.success(f"✅ Pushed `{data['id']}`")
                    else:
                        st.error(str(res))


# ════════════════════════════════════════════════════════
# TAB 3 — CONVERSATION
# ════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Merchant Reply Simulation</div>', unsafe_allow_html=True)

    conv_col1, conv_col2 = st.columns([2, 1], gap="large")

    with conv_col1:
        # Render chat history
        if not st.session_state.chat_history:
            st.markdown('<div style="color:#1e3a5f;text-align:center;padding:2rem;font-size:0.85rem">No conversation yet. Generate a message in the Compose tab first.</div>', unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "vera":
                    cta_html = f'<div style="margin-top:0.4rem"><span style="font-size:0.72rem;background:#1e3a5f;color:#60a5fa;padding:0.2rem 0.6rem;border-radius:100px">{msg.get("cta","")}</span></div>' if msg.get("cta") else ""
                    st.markdown(f'<div class="chat-bubble-vera">🤖 <b>Vera</b><br>{msg["text"]}{cta_html}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bubble-merchant">{msg["text"]} <b>🏪</b></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        reply_col1, reply_col2 = st.columns([3, 1])
        with reply_col1:
            reply_text = st.text_input("Merchant reply", placeholder="Type: Yes, send it / Not now / Tell me more...", label_visibility="collapsed")
        with reply_col2:
            send_reply = st.button("Send ↵", use_container_width=True)

        if send_reply and reply_text.strip():
            # Get last merchant from context
            merchant_ids = [m["id"] for m in SAMPLE_MERCHANTS.values()]
            prior = st.session_state.chat_history[-1]["text"] if st.session_state.chat_history else ""

            # Use last used merchant
            merchant_id_for_reply = st.session_state.get("last_merchant_id", merchant_ids[0])

            with st.spinner("Vera is responding..."):
                res, status = call_reply(merchant_id_for_reply, reply_text.strip(), prior)

            st.session_state.chat_history.append({"role": "merchant", "text": reply_text.strip()})
            if status == 200 and "message" in res:
                st.session_state.chat_history.append({"role": "vera", "text": res["message"], "cta": res.get("cta")})
            else:
                st.session_state.chat_history.append({"role": "vera", "text": f"[Error {status}] {json.dumps(res)}", "cta": None})
            st.rerun()

    with conv_col2:
        st.markdown('<div class="section-title">Controls</div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

        st.markdown('<div class="section-title" style="margin-top:1rem">Quick Replies</div>', unsafe_allow_html=True)
        quick_replies = ["Yes, send it now", "Not now", "Tell me more", "Lower the budget", "Yes, 50 people"]
        for qr in quick_replies:
            if st.button(qr, key=f"qr_{qr}", use_container_width=True):
                st.session_state.chat_history.append({"role": "merchant", "text": qr})
                st.rerun()


# ════════════════════════════════════════════════════════
# TAB 4 — API EXPLORER
# ════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Live API Testing</div>', unsafe_allow_html=True)

    endpoint = st.selectbox("Endpoint", [
        "GET /v1/healthz",
        "GET /v1/metadata",
        "POST /v1/context (push merchant)",
        "POST /v1/tick (generate message)",
        "POST /v1/reply (merchant reply)"
    ])

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown('<div class="section-title">Request</div>', unsafe_allow_html=True)

        default_bodies = {
            "GET /v1/healthz": None,
            "GET /v1/metadata": None,
            "POST /v1/context (push merchant)": json.dumps({
                "scope": "merchant",
                "context_id": "m_001_drmeera",
                "version": 1,
                "payload": SAMPLE_MERCHANTS["Dr. Meera Dental Clinic"]["json"],
                "delivered_at": datetime.utcnow().isoformat() + "Z"
            }, indent=2),
            "POST /v1/tick (generate message)": json.dumps({
                "session_id": "sess_001",
                "merchant_id": "m_001_drmeera",
                "trigger": SAMPLE_TRIGGERS["Research Spike"]
            }, indent=2),
            "POST /v1/reply (merchant reply)": json.dumps({
                "session_id": "sess_001",
                "merchant_id": "m_001_drmeera",
                "reply_text": "Yes, send the campaign now",
                "prior_message": "190 people searched for Dental Check-Up. Should I send them a ₹299 offer?"
            }, indent=2)
        }

        body_str = default_bodies[endpoint]
        if body_str:
            body_input = st.text_area("Request Body", value=body_str, height=300)
        else:
            st.info("No body required for GET requests")
            body_input = None

        if st.button("🚀 Execute", use_container_width=True):
            base = api_url()
            try:
                if endpoint == "GET /v1/healthz":
                    resp = requests.get(f"{base}/v1/healthz", timeout=5)
                elif endpoint == "GET /v1/metadata":
                    resp = requests.get(f"{base}/v1/metadata", timeout=5)
                elif endpoint.startswith("POST"):
                    body = json.loads(body_input) if body_input else {}
                    path = endpoint.split()[1].split(" ")[0]
                    resp = requests.post(f"{base}{path}", json=body, timeout=30)

                st.session_state.api_response = (resp.status_code, resp.json())
            except Exception as e:
                st.session_state.api_response = (0, {"error": str(e)})

    with col_b:
        st.markdown('<div class="section-title">Response</div>', unsafe_allow_html=True)
        if "api_response" in st.session_state and st.session_state.api_response:
            status_code, resp_body = st.session_state.api_response
            color = "#10b981" if status_code == 200 else "#ef4444"
            st.markdown(f'<div style="font-size:0.8rem;color:{color};font-family:JetBrains Mono,monospace;margin-bottom:0.5rem">HTTP {status_code}</div>', unsafe_allow_html=True)
            st.json(resp_body)
        else:
            st.markdown('<div style="color:#1e3a5f;text-align:center;padding:2rem;font-size:0.85rem">Response will appear here</div>', unsafe_allow_html=True)

    # curl examples
    with st.expander("📋 cURL Examples"):
        base = api_url()
        st.code(f"""# Health check
curl -s {base}/v1/healthz

# Push merchant context
curl -sS {base}/v1/context \\
  -H "Content-Type: application/json" \\
  -d '{{"scope":"merchant","context_id":"m_001_drmeera","version":1,"payload":{{...}},"delivered_at":"2026-05-02T10:00:00Z"}}'

# Generate message (tick)
curl -sS {base}/v1/tick \\
  -H "Content-Type: application/json" \\
  -d '{{"session_id":"sess_001","merchant_id":"m_001_drmeera","trigger":{{"type":"research","search_term":"Dental Check Up","local_searches":190}}}}'

# Merchant reply
curl -sS {base}/v1/reply \\
  -H "Content-Type: application/json" \\
  -d '{{"session_id":"sess_001","merchant_id":"m_001_drmeera","reply_text":"Yes, send it","prior_message":"..."}}'
""", language="bash")
