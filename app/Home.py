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

st.set_page_config(page_title="CruncherX", layout="wide")


# ---------------- LOGIN / SIGNUP VIEW ----------------

def login_view():
    st.title("🔐 CruncherX Login")

    tab_login, tab_signup = st.tabs(["Login", "Sign up"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                try:
                    res = supabase_sign_in(email, password)
                    user = res.user
                    if user is None:
                        st.error("Invalid credentials.")
                    else:
                        set_current_user(
                            {
                                "email": user.email,
                                "id": user.id,
                                "name": user.email.split("@")[0],
                            }
                        )
                        st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

    with tab_signup:
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Create account"):
            if not new_email or not new_password:
                st.error("Please enter email and password.")
            else:
                try:
                    res = supabase_sign_up(new_email, new_password)
                    user = res.user
                    if user is None:
                        st.info("Check your email to confirm your account.")
                    else:
                        st.success("Account created. You can now log in.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")


# ---------------- DASHBOARD VIEW ----------------

def dashboard_view():
    render_sidebar()

    user = get_current_user()

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


# ---------------- ENTRY POINT ----------------

def main():
    user = get_current_user()
    if user is None:
        login_view()
    else:
        dashboard_view()


if __name__ == "__main__":
    main()
