import streamlit as st
from components.sidebar import render_sidebar
from components.footer import render_footer
from auth import (
    get_current_user,
    set_current_user,
    logout,
    supabase_sign_in,
    supabase_sign_up,
)
from backend.supabase_client import get_supabase_client

# ---------------------------------------------------------
# MUST BE FIRST STREAMLIT COMMAND
# ---------------------------------------------------------
st.set_page_config(page_title="CruncherX", layout="wide")

# ---------------------------------------------------------
# INIT SUPABASE CLIENT
# ---------------------------------------------------------
sb = get_supabase_client()

if sb is None:
    st.error("Supabase client failed to initialize. Check secrets.toml.")
    st.stop()

FREE_PLAN_ID = "a32d6731-8622-42df-b375-7309f478eab1"


# ---------------------------------------------------------
# CREATE USER ROW IN public.profiles
# ---------------------------------------------------------
def ensure_user_row(user):
    """Ensure a profile row exists for this user."""

    res = (
        sb.table("profiles")
        .select("id")
        .eq("id", user.id)
        .execute()
    )

    data = getattr(res, "data", res)

    if not data:
        sb.table("profiles").insert({
            "id": user.id,
            "email": user.email,
            "name": user.email.split("@")[0],
            "plan_id": FREE_PLAN_ID,
            "plan_expiry": None
        }).execute()


# ---------------------------------------------------------
# HANDLE EMAIL CONFIRMATION REDIRECT
# ---------------------------------------------------------
query_params = st.query_params

if "access_token" in query_params:
    token = query_params["access_token"]
    refresh = query_params.get("refresh_token", "")

    # Set Supabase session
    sb.auth.set_session(token, refresh)

    auth_user = sb.auth.get_user()
    user = getattr(auth_user, "user", None)

    if user:
        ensure_user_row(user)

        set_current_user({
            "email": user.email,
            "id": user.id,
            "name": user.email.split("@")[0],
        })

        st.success("Email confirmed! You are now logged in.")
        st.rerun()


# ---------------------------------------------------------
# LOGIN / SIGNUP VIEW
# ---------------------------------------------------------
def login_view():
    st.title("🔐 CruncherX Login")

    tab_login, tab_signup = st.tabs(["Login", "Sign up"])

    # ---------------- LOGIN TAB ----------------
    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                try:
                    res = supabase_sign_in(email, password)
                    user = getattr(res, "user", None)

                    if user is None:
                        st.error("Invalid credentials.")
                    else:
                        # Set session
                        sb.auth.set_session(
                            res.session.access_token,
                            res.session.refresh_token
                        )

                        ensure_user_row(user)

                        set_current_user({
                            "email": user.email,
                            "id": user.id,
                            "name": user.email.split("@")[0],
                        })
                        st.rerun()

                except Exception as e:
                    st.error(f"Login failed: {e}")

    # ---------------- SIGNUP TAB ----------------
    with tab_signup:
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Create account"):
            if not new_email or not new_password:
                st.error("Please enter email and password.")
            else:
                try:
                    supabase_sign_up(new_email, new_password)
                    st.success("Account created. Check your email to confirm.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")


# ---------------------------------------------------------
# DASHBOARD VIEW
# ---------------------------------------------------------
def dashboard_view():
    render_sidebar()

    user = get_current_user()

    if user is None:
        st.error("Session expired. Please log in again.")
        st.rerun()

    st.title("🏠 CruncherX Dashboard")
    st.write(f"Welcome, **{user['name']}** ({user['email']})")
    st.write("Smaller PDFs. Bigger Productivity.")

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Logout"):
            logout()
            st.rerun()

    st.subheader("Choose a Mode:")
    st.page_link("pages/1_Cloud_Compressor.py", label="☁ Cloud Compressor")
    st.page_link("pages/2_Local_Compressor.py", label="💻 Local Bulldozer Mode")
    st.page_link("pages/3_OCR_Coming_Soon.py", label="🔍 OCR (Coming Soon)")
    st.page_link("pages/4_About_CruncherX.py", label="ℹ About CruncherX")
    st.page_link("pages/5_Contact_Support.py", label="📞 Contact Support")

    render_footer()


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
def main():
    user = get_current_user()

    if user is None:
        login_view()
        return

    dashboard_view()


if __name__ == "__main__":
    main()
