from datetime import datetime, date
from typing import Optional, Dict, Any
import streamlit as st
from supabase import create_client

FREE_PLAN_ID = "a32d6731-8622-42df-b375-7309f478eab1"


# ---------------------------------------------------------
# Supabase Client (cached)
# ---------------------------------------------------------
@st.cache_resource
def supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


# ---------------------------------------------------------
# 1. Get User + Plan (SDK‑SAFE)
# ---------------------------------------------------------
def get_user_plan(user_id: str) -> Optional[Dict[str, Any]]:
    sb = supabase()

    user_res = (
        sb.table("profiles")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    # New SDK returns None instead of response object
    if user_res is None:
        return None

    # Some SDK versions return dict, some return object with .data
    user = getattr(user_res, "data", user_res)

    if not isinstance(user, dict):
        return None

    plan_id = user.get("plan_id")
    if not plan_id:
        return None

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
        "id": user.get("id"),
        "email": user.get("email"),
        "plan_id": plan_id,
        "plan_expiry": user.get("plan_expiry"),
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
# 3. Daily Limit Check
# ---------------------------------------------------------
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

    data = getattr(res, "data", res)
    if not isinstance(data, list):
        return 0

    return len(data)


# ---------------------------------------------------------
# 4. Enforce Plan Rules
# ---------------------------------------------------------
def enforce_plan_rules(user: Dict[str, Any]) -> Dict[str, Any]:
    plan = user["plan"].get("name")

    if not plan:
        return {"allowed": False, "reason": "Invalid plan."}

    if is_plan_expired(user):
        return {"allowed": False, "reason": "Plan expired. Please renew."}

    if plan == "Free":
        if check_daily_limit(user["id"]) >= 5:
            return {"allowed": False, "reason": "Daily limit reached (5/day)."}
        return {
            "allowed": True,
            "watermark": True,
            "priority": False,
            "bulk": False,
            "api": False,
        }

    if plan == "Basic":
        return {"allowed": True, "watermark": False, "priority": False, "bulk": True, "api": False}

    if plan == "Pro":
        return {"allowed": True, "watermark": False, "priority": True, "bulk": True, "api": False}

    if plan == "Business":
        return {"allowed": True, "watermark": False, "priority": True, "bulk": True, "api": True}

    return {"allowed": False, "reason": "Unknown plan."}


# ---------------------------------------------------------
# 5. Log Usage
# ---------------------------------------------------------
def log_usage(user_id: str, org_id: str, action: str, bytes_in: int, bytes_out: int):
    sb = supabase()

    sb.table("usage_logs").insert({
        "user_id": user_id,
        "org_id": org_id,
        "action": action,
        "bytes_in": bytes_in,
        "bytes_out": bytes_out,
    }).execute()



# from datetime import datetime, date
# from typing import Optional, Dict, Any
# import streamlit as st
# from supabase import create_client

# FREE_PLAN_ID = "a32d6731-8622-42df-b375-7309f478eab1"


# # ---------------------------------------------------------
# # Supabase Client (cached)
# # ---------------------------------------------------------
# @st.cache_resource
# def supabase():
#     return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


# # ---------------------------------------------------------
# # 1. Get User + Plan (SDK‑SAFE)
# # ---------------------------------------------------------
# def get_user_plan(user_id: str) -> Optional[Dict[str, Any]]:
#     sb = supabase()

#     # profiles table (correct)
#     user_res = (
#         sb.table("profiles")
#         .select("*")
#         .eq("id", user_id)
#         .maybe_single()
#         .execute()
#     )

#     # New SDK returns None instead of response object
#     if user_res is None:
#         return None

#     # Some SDK versions return dict, some return object with .data
#     user = getattr(user_res, "data", user_res)

#     if not isinstance(user, dict):
#         return None

#     plan_id = user.get("plan_id")
#     if not plan_id:
#         return None

#     # subscription_plans table
#     plan_res = (
#         sb.table("subscription_plans")
#         .select("*")
#         .eq("id", plan_id)
#         .maybe_single()
#         .execute()
#     )

#     if plan_res is None:
#         return None

#     plan = getattr(plan_res, "data", plan_res)

#     if not isinstance(plan, dict):
#         return None

#     return {
#         "id": user.get("id"),
#         "email": user.get("email"),
#         "plan_id": plan_id,
#         "plan_expiry": user.get("plan_expiry"),
#         "plan": plan,
#     }


# # ---------------------------------------------------------
# # 2. Check if plan expired
# # ---------------------------------------------------------
# def is_plan_expired(user: Dict[str, Any]) -> bool:
#     expiry = user.get("plan_expiry")
#     if not expiry:
#         return True

#     try:
#         expiry_dt = datetime.fromisoformat(expiry.replace("Z", ""))
#     except Exception:
#         return True

#     return expiry_dt < datetime.utcnow()


# # ---------------------------------------------------------
# # 3. Daily Limit Check
# # ---------------------------------------------------------
# def check_daily_limit(user_id: str) -> int:
#     sb = supabase()

#     today_str = date.today().isoformat()

#     res = (
#         sb.table("usage_logs")
#         .select("id")
#         .eq("user_id", user_id)
#         .eq("action", "compress")
#         .gte("created_at", today_str)
#         .execute()
#     )

#     data = getattr(res, "data", res)
#     if not isinstance(data, list):
#         return 0

#     return len(data)


# # ---------------------------------------------------------
# # 4. Enforce Plan Rules
# # ---------------------------------------------------------
# def enforce_plan_rules(user: Dict[str, Any]) -> Dict[str, Any]:
#     plan = user["plan"].get("name")

#     if not plan:
#         return {"allowed": False, "reason": "Invalid plan."}

#     if is_plan_expired(user):
#         return {"allowed": False, "reason": "Plan expired. Please renew."}

#     if plan == "Free":
#         if check_daily_limit(user["id"]) >= 5:
#             return {"allowed": False, "reason": "Daily limit reached (5/day)."}
#         return {
#             "allowed": True,
#             "watermark": True,
#             "priority": False,
#             "bulk": False,
#             "api": False,
#         }

#     if plan == "Basic":
#         return {"allowed": True, "watermark": False, "priority": False, "bulk": True, "api": False}

#     if plan == "Pro":
#         return {"allowed": True, "watermark": False, "priority": True, "bulk": True, "api": False}

#     if plan == "Business":
#         return {"allowed": True, "watermark": False, "priority": True, "bulk": True, "api": True}

#     return {"allowed": False, "reason": "Unknown plan."}


# # ---------------------------------------------------------
# # 5. Log Usage
# # ---------------------------------------------------------
# def log_usage(user_id: str, org_id: str, action: str, bytes_in: int, bytes_out: int):
#     sb = supabase()

#     sb.table("usage_logs").insert({
#         "user_id": user_id,
#         "org_id": org_id,
#         "action": action,
#         "bytes_in": bytes_in,
#         "bytes_out": bytes_out,
#     }).execute()
