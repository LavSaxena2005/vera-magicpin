"""
Vera Composer — deterministic compose() function
compose(category, merchant, trigger, customer?) → message, cta, send_as, suppression_key, rationale
Uses Google Gemini API (free tier)
"""

import hashlib
import json
import os
import re
from typing import Optional, Dict, Any, List

import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyCVIl5f5L2iq5N8epbFzIsynzvtobAIl9Q"))
gemini_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=genai.types.GenerationConfig(
        temperature=0.0,   # deterministic
        max_output_tokens=512,
    )
)

SYSTEM_PROMPT = """You are Vera, magicpin's AI assistant for merchant growth.
Your ONLY job is to generate the NEXT BEST MESSAGE for a merchant based STRICTLY on provided context.

STRICT RULES:
1. DECISION FIRST: Use trigger + merchant state + category to decide WHAT action, THEN write.
2. SPECIFIC: Use real numbers, names, offers, metrics from input. NEVER invent data.
3. CATEGORY VOICE:
   - dentist → clinical, professional, trust-driven
   - salon → trendy, visual, urgency
   - restaurant → cravings, timing, offers
   - gym → motivation, habit, data
   - pharmacy → utility, urgency, trust
4. ONE CTA: Exactly one action (Yes/No or single tap).
5. NO FAKE CLAIMS: Only facts from input.
6. DETERMINISTIC: Same input → same output always.
7. CONCISE: Message under 200 characters. Punchy and actionable.

Return ONLY valid JSON (no markdown, no explanation):
{
  "message": "<message to send>",
  "cta": "<single clear action>",
  "send_as": "<identity>",
  "suppression_key": "<stable key>",
  "rationale": "<1-line why>"
}"""


def _build_user_prompt(
    category: Dict,
    merchant: Dict,
    trigger: Dict,
    customer: Optional[Dict],
    history: List[Dict]
) -> str:
    history_snippet = history[-3:] if history else []
    parts = [
        f"CATEGORY:\n{json.dumps(category, ensure_ascii=False)}",
        f"MERCHANT:\n{json.dumps(merchant, ensure_ascii=False)}",
        f"TRIGGER:\n{json.dumps(trigger, ensure_ascii=False)}",
    ]
    if customer:
        parts.append(f"CUSTOMER:\n{json.dumps(customer, ensure_ascii=False)}")
    if history_snippet:
        parts.append(f"RECENT HISTORY (last 3):\n{json.dumps(history_snippet, ensure_ascii=False)}")

    parts.append("""
STEPS:
1. What is the core signal from the trigger? (recall/spike/dip/research/festival/reply)
2. What merchant fact makes this timely right now?
3. What single action benefits the merchant most?
4. Write the message using real numbers/offers from context.
5. One CTA. No vague phrases. No fake data.

OUTPUT: ONLY the JSON object.""")
    return "\n\n".join(parts)


def _make_suppression_key(trigger: Dict, merchant: Dict) -> str:
    identity = merchant.get("identity", {})
    merchant_id = identity.get("id", identity.get("merchant_id", "unknown"))
    trigger_type = trigger.get("type", "unknown")
    trigger_date = trigger.get("date", trigger.get("timestamp", ""))[:10] if trigger.get("date") or trigger.get("timestamp") else "nodate"
    raw = f"{merchant_id}::{trigger_type}::{trigger_date}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _fallback_compose(category: Dict, merchant: Dict, trigger: Dict, customer: Optional[Dict]) -> Dict:
    """Rule-based fallback if LLM call fails."""
    identity = merchant.get("identity", {})
    performance = merchant.get("performance", {})
    offers = merchant.get("offers", [])

    name = identity.get("name", "your business")
    trigger_type = trigger.get("type", "recall")
    cat = category.get("category", "restaurant")

    offer_str = ""
    if offers:
        o = offers[0]
        offer_str = f" with {o.get('title', 'a special offer')}"

    searches = trigger.get("local_searches", trigger.get("search_volume", 0))
    search_term = trigger.get("search_term", trigger.get("keyword", "your service"))

    if searches and trigger_type in ("research", "spike"):
        msg = f"{searches} people nearby searched '{search_term}' today. Launch a targeted campaign{offer_str}?"
        cta = "Yes, launch campaign"
    elif trigger_type == "dip":
        rating = performance.get("rating", performance.get("avg_rating", ""))
        msg = f"Your orders dipped this week. A quick offer{offer_str} could bring customers back. Activate?"
        cta = "Yes, activate offer"
    elif trigger_type == "festival":
        festival = trigger.get("festival", trigger.get("event", "upcoming festival"))
        msg = f"{festival} is coming. Set up a special campaign{offer_str} to capture the surge?"
        cta = "Yes, set it up"
    else:
        msg = f"{name}: {search_term} demand is live. Send a targeted message{offer_str} to nearby customers?"
        cta = "Yes, send now"

    merchant_name = identity.get("name", "Vera")
    send_as = f"Vera for {merchant_name}"

    return {
        "message": msg,
        "cta": cta,
        "send_as": send_as,
        "suppression_key": _make_suppression_key(trigger, merchant),
        "rationale": f"Trigger type '{trigger_type}' detected; fallback rule-based response applied."
    }


def compose(
    category: Dict,
    merchant: Dict,
    trigger: Dict,
    customer: Optional[Dict] = None,
    history: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Deterministic message composer.
    Returns: {message, cta, send_as, suppression_key, rationale}
    """
    history = history or []
    suppression_key = _make_suppression_key(trigger, merchant)

    user_prompt = _build_user_prompt(category, merchant, trigger, customer, history)

    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        response = gemini_model.generate_content(full_prompt)

        raw = response.text.strip()
        # Strip markdown fences if any
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        result = json.loads(raw)

        # Ensure suppression_key is stable (override LLM's if needed)
        result["suppression_key"] = suppression_key

        # Validate required fields
        for field in ("message", "cta", "send_as", "rationale"):
            if field not in result:
                raise ValueError(f"Missing field: {field}")

        return result

    except Exception as e:
        print(f"[Composer] LLM error: {e} — falling back to rule-based")
        fallback = _fallback_compose(category, merchant, trigger, customer)
        fallback["suppression_key"] = suppression_key
        return fallback
