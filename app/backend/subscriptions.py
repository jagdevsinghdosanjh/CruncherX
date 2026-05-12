from datetime import datetime
from supabase import create_client
import streamlit as st


@st.cache_resource
def supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])


def get_user_plan(user_id):
    sb = supabase()

    user = sb.table("users").select("*").eq("id", user_id).single().execute().data
    if not user:
        return None

    plan = sb.table("subscription_plans").select("*").eq("id", user["plan_id"]).single().execute().data
    return {**user, "plan": plan}


def is_plan_expired(user):
    expiry = user.get("plan_expiry")
    if expiry is None:
        return True

    expiry_dt = datetime.fromisoformat(expiry.replace("Z", ""))
    return expiry_dt < datetime.utcnow()


def check_daily_limit(user_id):
    sb = supabase()

    today = datetime.utcnow().date().isoformat()

    result = (
        sb.table("usage_logs")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .eq("action", "compress")
        .gte("created_at", today)
        .execute()
    )

    return result.count


def enforce_plan_rules(user):
    plan = user["plan"]["name"]

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


def log_usage(user_id, org_id, action, bytes_in, bytes_out):
    sb = supabase()
    sb.table("usage_logs").insert({
        "user_id": user_id,
        "org_id": org_id,
        "action": action,
        "bytes_in": bytes_in,
        "bytes_out": bytes_out
    }).execute()

# from datetime import datetime, timedelta
# from supabase import create_client
# import streamlit as st


# # -----------------------------
# # Supabase Client
# # -----------------------------
# @st.cache_resource
# def supabase():
#     return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])


# # -----------------------------
# # 1. Get User Plan
# # -----------------------------
# def get_user_plan(user_id):
#     sb = supabase()

#     user = sb.table("users").select("*").eq("id", user_id).single().execute().data
#     if not user:
#         return None

#     plan = sb.table("subscription_plans").select("*").eq("id", user["plan_id"]).single().execute().data
#     return {**user, "plan": plan}


# # -----------------------------
# # 2. Check if plan expired
# # -----------------------------
# def is_plan_expired(user):
#     expiry = user.get("plan_expiry")
#     if expiry is None:
#         return True

#     expiry_dt = datetime.fromisoformat(expiry.replace("Z", ""))
#     return expiry_dt < datetime.utcnow()


# # -----------------------------
# # 3. Daily Limit Check (Free Plan)
# # -----------------------------
# def check_daily_limit(user_id):
#     sb = supabase()

#     today_count = (
#         sb.table("usage_logs")
#         .select("id", count="exact")
#         .eq("user_id", user_id)
#         .eq("action", "compress")
#         .gte("created_at", datetime.utcnow().date().isoformat())
#         .execute()
#     )

#     return today_count.count


# # -----------------------------
# # 4. Enforce Plan Rules
# # -----------------------------
# def enforce_plan_rules(user, job_type="compress"):
#     plan = user["plan"]["name"]

#     # 1. Expired plan → downgrade to Free
#     if is_plan_expired(user):
#         return {"allowed": False, "reason": "Plan expired. Please renew."}

#     # 2. Free Plan Rules
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

#     # 3. Basic Plan
#     if plan == "Basic":
#         return {
#             "allowed": True,
#             "watermark": False,
#             "priority": False,
#             "bulk": True,
#             "api": False,
#         }

#     # 4. Pro Plan
#     if plan == "Pro":
#         return {
#             "allowed": True,
#             "watermark": False,
#             "priority": True,
#             "bulk": True,
#             "api": False,
#         }

#     # 5. Business Plan
#     if plan == "Business":
#         return {
#             "allowed": True,
#             "watermark": False,
#             "priority": True,
#             "bulk": True,
#             "api": True,
#         }

#     return {"allowed": False, "reason": "Unknown plan."}


# # -----------------------------
# # 5. Log Usage
# # -----------------------------
# def log_usage(user_id, org_id, action, bytes_in, bytes_out):
#     sb = supabase()
#     sb.table("usage_logs").insert({
#         "user_id": user_id,
#         "org_id": org_id,
#         "action": action,
#         "bytes_in": bytes_in,
#         "bytes_out": bytes_out
#     }).execute()
