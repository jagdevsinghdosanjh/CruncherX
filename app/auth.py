import streamlit as st
from supabase import create_client, Client


# -----------------------------
# SUPABASE CLIENT (cached)
# -----------------------------
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# -----------------------------
# AUTH ACTIONS
# -----------------------------
def supabase_sign_in(email: str, password: str):
    sb = get_supabase_client()
    return sb.auth.sign_in_with_password({"email": email, "password": password})


def supabase_sign_up(email: str, password: str):
    sb = get_supabase_client()
    return sb.auth.sign_up({"email": email, "password": password})


def supabase_sign_out():
    sb = get_supabase_client()
    sb.auth.sign_out()


# -----------------------------
# USER ROW CREATION
# -----------------------------
def ensure_user_row(user):
    """
    Ensure a row exists in public.users for subscription + usage tracking.
    """
    sb = get_supabase_client()

    # Check if row exists
    res = (
        sb.table("users")
        .select("id")
        .eq("id", user.id)
        .execute()
    )

    if not res.data:
        # Create new row
        sb.table("users").insert({
            "id": user.id,
            "email": user.email,
            "plan_id": "free",
            "plan_expiry": None
        }).execute()


# -----------------------------
# SESSION HELPERS
# -----------------------------
def set_current_user(user_dict: dict | None):
    st.session_state["current_user"] = user_dict


def get_current_user():
    return st.session_state.get("current_user")


def logout():
    supabase_sign_out()
    st.session_state.pop("current_user", None)


def require_login():
    """
    Redirect user to login page if not authenticated.
    """
    if "current_user" not in st.session_state or st.session_state["current_user"] is None:
        st.switch_page("Home.py")
