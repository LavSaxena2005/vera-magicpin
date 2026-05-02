"""
Vera Message Engine — FastAPI Backend
Implements: POST /v1/context, POST /v1/tick, POST /v1/reply, GET /v1/healthz, GET /v1/metadata
"""

import uuid
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from composer import compose

app = FastAPI(title="Vera Message Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store (keyed by scope+context_id)
context_store: Dict[str, Dict] = {}
session_store: Dict[str, list] = {}  # conversation history per merchant


# ── Schemas ────────────────────────────────────────────────────────────────

class ContextRequest(BaseModel):
    scope: str
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: Optional[str] = None


class TickRequest(BaseModel):
    session_id: str
    merchant_id: str
    trigger: Dict[str, Any]
    customer: Optional[Dict[str, Any]] = None


class ReplyRequest(BaseModel):
    session_id: str
    merchant_id: str
    reply_text: str
    prior_message: Optional[str] = None


# ── Helpers ─────────────────────────────────────────────────────────────────

def _store_key(scope: str, context_id: str) -> str:
    return f"{scope}::{context_id}"


def _get_merchant_context(merchant_id: str) -> Optional[Dict]:
    key = _store_key("merchant", merchant_id)
    return context_store.get(key, {}).get("payload")


def _get_category_context(category: str) -> Dict:
    CATEGORY_PROFILES = {
        "dentist": {
            "tone": "clinical, trust-driven, professional",
            "offer_patterns": ["free consultation", "discounted check-up", "whitening packages"],
            "avoid": ["slang", "emoji overuse", "pushy sales language"],
            "seasonal": ["World Oral Health Day (Mar 20)", "Diwali smile campaigns"],
            "voice": "Dr. [Name]'s clinic"
        },
        "salon": {
            "tone": "trendy, visual, urgency-first",
            "offer_patterns": ["flat % off", "combo deals", "festive packages"],
            "avoid": ["clinical language", "overly formal tone"],
            "seasonal": ["Wedding season", "Diwali", "New Year glam"],
            "voice": "Your stylist at [Name]"
        },
        "restaurant": {
            "tone": "cravings-driven, timing-sensitive, offer-led",
            "offer_patterns": ["BOGO", "free delivery", "combo meals", "happy hour"],
            "avoid": ["health-first language", "clinical comparisons"],
            "seasonal": ["Lunch rush (12–2pm)", "Dinner peak (7–10pm)", "Weekend brunches"],
            "voice": "Chef/Team at [Name]"
        },
        "gym": {
            "tone": "motivational, habit-focused, data-backed",
            "offer_patterns": ["free trial week", "membership discounts", "batch timing"],
            "avoid": ["fear-based messaging", "body shaming language"],
            "seasonal": ["New Year resolution season", "Summer shred", "Post-Diwali reset"],
            "voice": "Your trainer at [Name]"
        },
        "pharmacy": {
            "tone": "utility-first, urgency, trust",
            "offer_patterns": ["refill reminders", "seasonal health kits", "discounts on generics"],
            "avoid": ["medical advice claims", "fear mongering"],
            "seasonal": ["Monsoon health", "Winter immunity", "Summer hydration"],
            "voice": "Your pharmacist at [Name]"
        }
    }
    cat_lower = category.lower()
    for key, profile in CATEGORY_PROFILES.items():
        if key in cat_lower:
            return {"category": key, **profile}
    return {"category": category, "tone": "professional", "offer_patterns": [], "avoid": [], "seasonal": [], "voice": "Vera"}


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/v1/healthz")
def healthz():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/v1/metadata")
def metadata():
    return {
        "name": "Vera Message Engine",
        "version": "1.0.0",
        "author": "Vera AI",
        "model": "claude-sonnet-4-20250514",
        "capabilities": ["compose", "context", "tick", "reply"],
        "categories": ["dentist", "salon", "restaurant", "gym", "pharmacy"],
        "judge_simulator_compatible": True
    }


@app.post("/v1/context")
def push_context(req: ContextRequest):
    key = _store_key(req.scope, req.context_id)
    existing = context_store.get(key)

    # Idempotent: same version → no-op
    if existing and existing.get("version") == req.version:
        return {
            "accepted": False,
            "ack_id": existing.get("ack_id"),
            "stored_at": existing.get("stored_at"),
            "note": "no-op: same version already stored"
        }

    # Higher version replaces atomically
    if existing and existing.get("version", -1) > req.version:
        raise HTTPException(status_code=409, detail="Older version rejected; higher version already stored.")

    ack_id = f"ack_{uuid.uuid4().hex[:8]}"
    stored_at = datetime.now(timezone.utc).isoformat()

    context_store[key] = {
        "scope": req.scope,
        "context_id": req.context_id,
        "version": req.version,
        "payload": req.payload,
        "delivered_at": req.delivered_at,
        "ack_id": ack_id,
        "stored_at": stored_at
    }

    return {"accepted": True, "ack_id": ack_id, "stored_at": stored_at}


@app.post("/v1/tick")
def tick(req: TickRequest):
    merchant_payload = _get_merchant_context(req.merchant_id)
    if not merchant_payload:
        raise HTTPException(status_code=404, detail=f"No context found for merchant_id='{req.merchant_id}'. POST /v1/context first.")

    # Infer category
    identity = merchant_payload.get("identity", {})
    category_raw = identity.get("category", identity.get("vertical", "restaurant"))
    category_ctx = _get_category_context(category_raw)

    result = compose(
        category=category_ctx,
        merchant=merchant_payload,
        trigger=req.trigger,
        customer=req.customer,
        history=session_store.get(req.merchant_id, [])
    )

    # Store in session
    if req.merchant_id not in session_store:
        session_store[req.merchant_id] = []
    session_store[req.merchant_id].append({
        "role": "vera",
        "message": result["message"],
        "trigger_type": req.trigger.get("type"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return result


@app.post("/v1/reply")
def reply(req: ReplyRequest):
    merchant_payload = _get_merchant_context(req.merchant_id)
    if not merchant_payload:
        raise HTTPException(status_code=404, detail="Merchant context not found.")

    identity = merchant_payload.get("identity", {})
    category_raw = identity.get("category", identity.get("vertical", "restaurant"))
    category_ctx = _get_category_context(category_raw)

    # Build a "reply" trigger
    reply_trigger = {
        "type": "reply",
        "subtype": "merchant_reply",
        "reply_text": req.reply_text,
        "prior_message": req.prior_message or ""
    }

    result = compose(
        category=category_ctx,
        merchant=merchant_payload,
        trigger=reply_trigger,
        customer=None,
        history=session_store.get(req.merchant_id, [])
    )

    if req.merchant_id not in session_store:
        session_store[req.merchant_id] = []
    session_store[req.merchant_id].append({
        "role": "merchant",
        "message": req.reply_text,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    session_store[req.merchant_id].append({
        "role": "vera",
        "message": result["message"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return result


@app.get("/v1/sessions/{merchant_id}")
def get_session(merchant_id: str):
    return {"merchant_id": merchant_id, "history": session_store.get(merchant_id, [])}


@app.get("/v1/contexts")
def list_contexts():
    return {"count": len(context_store), "keys": list(context_store.keys())}
