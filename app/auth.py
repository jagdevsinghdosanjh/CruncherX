import streamlit as st
from supabase import create_client, Client

# ---------------------------------------------------------
# SUPABASE CLIENT (must use ANON KEY, not service key)
# ---------------------------------------------------------
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]  # MUST be anon key
    return create_client(url, key)


# ---------------------------------------------------------
# AUTH FUNCTIONS
# ---------------------------------------------------------
def supabase_sign_in(email: str, password: str):
    sb = get_supabase_client()
    return sb.auth.sign_in_with_password({"email": email, "password": password})


def supabase_sign_up(email: str, password: str):
    sb = get_supabase_client()
    return sb.auth.sign_up({"email": email, "password": password})


def supabase_sign_out():
    sb = get_supabase_client()
    sb.auth.sign_out()


# ---------------------------------------------------------
# SESSION STATE HELPERS
# ---------------------------------------------------------
def set_current_user(user_dict: dict | None):
    st.session_state["current_user"] = user_dict


def get_current_user():
    return st.session_state.get("current_user")


def logout():
    supabase_sign_out()
    st.session_state.pop("current_user", None)
