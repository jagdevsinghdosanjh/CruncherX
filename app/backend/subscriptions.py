from datetime import datetime, date
from typing import Optional, Dict, Any
import streamlit as st
from backend.supabase_client import get_supabase_client


# ---------------------------------------------------------
# Supabase Client (cached)
# ---------------------------------------------------------
sb = get_supabase_client()


# ---------------------------------------------------------
# 1. Get User + Plan (matches your actual schema)
# ---------------------------------------------------------
def get_user_plan(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Loads the user's active subscription plan based on:
    - profiles.plan_id
    - subscription_plans table
    """

    # Fetch profile
    profile_res = (
        sb.table("profiles")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    if profile_res is None:
        return None

    profile = getattr(profile_res, "data", profile_res)
    if not isinstance(profile, dict):
        return None

    plan_id = profile.get("plan_id")
    if not plan_id:
        return None

    # Fetch plan details
    plan_res = (
        sb.table("subscription_plans")
        .select("*")
        .eq("id", plan_id)
        .maybe_single()
        .execute()
    )

    if plan_res is None:
        return None

    plan = getattr(plan_res, "data", plan_res)
    if not isinstance(plan, dict):
        return None

    return {
        "id": profile.get("id"),
        "email": profile.get("email"),
        "plan_id": plan_id,
        "plan_expiry": profile.get("plan_expiry"),
        "plan": plan,
    }


# ---------------------------------------------------------
# 2. Check if plan expired
# ---------------------------------------------------------
def is_plan_expired(user: Dict[str, Any]) -> bool:
    expiry = user.get("plan_expiry")
    if not expiry:
        return True

    try:
        expiry_dt = datetime.fromisoformat(expiry.replace("Z", ""))
    except Exception:
        return True

    return expiry_dt < datetime.utcnow()


# ---------------------------------------------------------
# 3. Daily Limit Check (usage_logs table)
# ---------------------------------------------------------
def check_daily_limit(user_id: str) -> int:
    today_str = date.today().isoformat()

    res = (
        sb.table("usage_logs")
        .select("id")
        .eq("user_id", user_id)
        .eq("action", "compress")
        .gte("created_at", today_str)
        .execute()
    )

    data = getattr(res, "data", res)
    if not isinstance(data, list):
        return 0

    return len(data)


# ---------------------------------------------------------
# 4. Enforce Plan Rules (Free / Basic / Pro / Business)
# ---------------------------------------------------------
def enforce_plan_rules(user: Dict[str, Any]) -> Dict[str, Any]:
    plan_name = user["plan"].get("name")

    if not plan_name:
        return {"allowed": False, "reason": "Invalid plan."}

    if is_plan_expired(user):
        return {"allowed": False, "reason": "Plan expired. Please renew."}

    # ---------------- FREE PLAN ----------------
    if plan_name == "Free":
        if check_daily_limit(user["id"]) >= 5:
            return {"allowed": False, "reason": "Daily limit reached (5/day)."}
        return {
            "allowed": True,
            "watermark": True,
            "priority": False,
            "bulk": False,
            "api": False,
        }

    # ---------------- BASIC PLAN ----------------
    if plan_name == "Basic":
        return {
            "allowed": True,
            "watermark": False,
            "priority": False,
            "bulk": True,
            "api": False,
        }

    # ---------------- PRO PLAN ----------------
    if plan_name == "Pro":
        return {
            "allowed": True,
            "watermark": False,
            "priority": True,
            "bulk": True,
            "api": False,
        }

    # ---------------- BUSINESS PLAN ----------------
    if plan_name == "Business":
        return {
            "allowed": True,
            "watermark": False,
            "priority": True,
            "bulk": True,
            "api": True,
        }

    return {"allowed": False, "reason": "Unknown plan."}


# ---------------------------------------------------------
# 5. Log Usage (matches usage_logs table)
# ---------------------------------------------------------
def log_usage(user_id: str, org_id: str, action: str, bytes_in: int, bytes_out: int):
    sb.table("usage_logs").insert({
        "user_id": user_id,
        "org_id": org_id,
        "action": action,
        "bytes_in": bytes_in,
        "bytes_out": bytes_out,
    }).execute()
