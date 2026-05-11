import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def supabase_sign_in(email: str, password: str):
    supabase = get_supabase_client()
    return supabase.auth.sign_in_with_password({"email": email, "password": password})


def supabase_sign_up(email: str, password: str):
    supabase = get_supabase_client()
    return supabase.auth.sign_up({"email": email, "password": password})


def supabase_sign_out():
    supabase = get_supabase_client()
    supabase.auth.sign_out()


# ---------------- SESSION HELPERS ----------------

def set_current_user(user_dict: dict | None):
    st.session_state["current_user"] = user_dict


def get_current_user():
    return st.session_state.get("current_user")


def logout():
    set_current_user(None)
    supabase_sign_out()
