# Vera Message Engine — magicpin AI Challenge

> **Build the message engine behind Vera** — magicpin's AI assistant for merchant growth.

---

## Architecture

```
vera-magicpin/
├── backend/
│   ├── main.py          # FastAPI server (5 endpoints)
│   ├── composer.py      # Core compose() function (LLM + fallback)
│   └── requirements.txt
├── frontend/
│   ├── app.py           # Streamlit UI
│   └── requirements.txt
├── dataset/
│   ├── merchants_seed.json
│   └── triggers_seed.json
└── README.md
```

---

## Quick Start

### 1. Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY=AIzaSy...        # Get free key from aistudio.google.com
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API is live at `http://localhost:8000`

### 2. Frontend (Streamlit)

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/healthz` | Health check |
| `GET` | `/v1/metadata` | Bot metadata |
| `POST` | `/v1/context` | Push merchant/customer context |
| `POST` | `/v1/tick` | Generate next message |
| `POST` | `/v1/reply` | Handle merchant reply |

---

## How compose() Works

```
compose(category, merchant, trigger, customer?) → {
  message, cta, send_as, suppression_key, rationale
}
```

**Step 1**: Extract signal from trigger (type: research/spike/dip/festival/recall/reply)  
**Step 2**: Load merchant performance, offers, and conversation history  
**Step 3**: Apply category voice rules (clinical/trendy/cravings/motivational/utility)  
**Step 4**: Generate specific, grounded message via Claude Sonnet (temperature=0 for determinism)  
**Step 5**: Rule-based fallback if LLM call fails  
**Step 6**: Stable suppression_key via MD5(merchant_id + trigger_type + date)

---

## Model Choice

- **Claude Sonnet 4** (`claude-sonnet-4-20250514`)
- `temperature=0` for full determinism
- Rule-based fallback ensures 100% uptime even without API key

---

## Scoring Strategy

| Dimension | Approach |
|-----------|----------|
| Decision Quality | Trigger type → action mapping before writing |
| Specificity | Real numbers, offers, locality injected in prompt |
| Category Fit | Per-category system prompt with voice/tone rules |
| Merchant Fit | Full merchant JSON in context (offers, metrics, history) |
| Engagement | Single yes/no CTA, urgency signal from trigger |

---

## Deployment

Deploy the FastAPI backend to any public host:
- **Railway**: `railway up`
- **Render**: Connect repo, set `ANTHROPIC_API_KEY`
- **Fly.io**: `fly deploy`

Submit your public URL (e.g. `https://vera-engine.railway.app`)
