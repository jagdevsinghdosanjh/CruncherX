from datetime import datetime, date
from supabase import create_client
import streamlit as st
from typing import Optional, Dict, Any


# -----------------------------
# Supabase Client
# -----------------------------
@st.cache_resource
def supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])


# -----------------------------
# 1. Get User + Plan (SAFE)
# -----------------------------
def get_user_plan(user_id: str) -> Optional[Dict[str, Any]]:
    sb = supabase()

    user_res = sb.table("users").select("*").eq("id", user_id).single().execute()
    user = user_res.data

    # If no user found → return None
    if not isinstance(user, dict):
        return None

    plan_id = user.get("plan_id")
    if not plan_id:
        return None

    plan_res = (
        sb.table("subscription_plans")
        .select("*")
        .eq("id", plan_id)
        .single()
        .execute()
    )
    plan = plan_res.data

    if not isinstance(plan, dict):
        return None

    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "plan_id": plan_id,
        "plan_expiry": user.get("plan_expiry"),
        "plan": plan,
    }


# -----------------------------
# 2. Check if plan expired (SAFE)
# -----------------------------
def is_plan_expired(user: Dict[str, Any]) -> bool:
    expiry = user.get("plan_expiry")
    if not expiry:
        return True

    try:
        expiry_dt = datetime.fromisoformat(expiry.replace("Z", ""))
    except Exception:
        return True

    return expiry_dt < datetime.utcnow()


# -----------------------------
# 3. Daily Limit Check (SAFE)
# -----------------------------
def check_daily_limit(user_id: str) -> int:
    sb = supabase()

    today_str = date.today().isoformat()

    res = (
        sb.table("usage_logs")
        .select("id")
        .eq("user_id", user_id)
        .eq("action", "compress")
        .gte("created_at", today_str)
        .execute()
    )

    if not isinstance(res.data, list):
        return 0

    return len(res.data)


# -----------------------------
# 4. Enforce Plan Rules (SAFE)
# -----------------------------
def enforce_plan_rules(user: Dict[str, Any]) -> Dict[str, Any]:
    plan = user["plan"].get("name")

    if not plan:
        return {"allowed": False, "reason": "Invalid plan."}

    if is_plan_expired(user):
        return {"allowed": False, "reason": "Plan expired. Please renew."}

    if plan == "Free":
        if check_daily_limit(user["id"]) >= 5:
            return {"allowed": False, "reason": "Daily limit reached (5/day)."}
        return {"allowed": True, "watermark": True, "priority": False, "bulk": False, "api": False}

    if plan == "Basic":
        return {"allowed": True, "watermark": False, "priority": False, "bulk": True, "api": False}

    if plan == "Pro":
        return {"allowed": True, "watermark": False, "priority": True, "bulk": True, "api": False}

    if plan == "Business":
        return {"allowed": True, "watermark": False, "priority": True, "bulk": True, "api": True}

    return {"allowed": False, "reason": "Unknown plan."}


# -----------------------------
# 5. Log Usage (SAFE)
# -----------------------------
def log_usage(user_id: str, org_id: str, action: str, bytes_in: int, bytes_out: int):
    sb = supabase()

    sb.table("usage_logs").insert({
        "user_id": user_id,
        "org_id": org_id,
        "action": action,
        "bytes_in": bytes_in,
        "bytes_out": bytes_out,
    }).execute()
