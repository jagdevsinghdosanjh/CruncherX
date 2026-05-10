import streamlit as st
from components.sidebar import render_sidebar
from components.footer import render_footer
from auth import get_current_user, set_current_user, logout

# ---------------------------------------------------------
# LOGIN VIEW
# ---------------------------------------------------------

def login_view():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "123":
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")


def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_view()
        st.stop()

    st.title("Welcome to PDF CruncherX")
    st.write("You are logged in!")


if __name__ == "__main__":
    main()

# def login_view():
#     st.set_page_config(page_title="CruncherX Login", layout="centered")
#     st.title("🔐 CruncherX Login")

#     email = st.text_input("Email")
#     name = st.text_input("Name")

#     if st.button("Continue"):
#         if email:
#             set_current_user({"email": email, "name": name or email})
#             st.experimental_rerun()
#         else:
#             st.error("Please enter an email")


# ---------------------------------------------------------
# MAIN DASHBOARD (AFTER LOGIN)
# ---------------------------------------------------------
def dashboard_view():
    st.set_page_config(page_title="CruncherX Dashboard", layout="centered")

    render_sidebar()

    user = get_current_user()
    st.title("🏠 CruncherX Dashboard")
    st.write(f"Welcome, **{user['name']}** ({user['email']})")
    st.write("Smaller PDFs. Bigger Productivity.")

    # Logout button (top-right)
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Logout"):
            logout()
            st.experimental_rerun()

    # Navigation
    st.subheader("Choose a Mode:")
    st.page_link("pages/1_Cloud_Compressor.py", label="☁ Cloud Compressor")
    st.page_link("pages/2_Local_Compressor.py", label="💻 Local Bulldozer Mode")
    st.page_link("pages/3_OCR_Coming_Soon.py", label="🔍 OCR (Coming Soon)")
    st.page_link("pages/4_About_CruncherX.py", label="ℹ About CruncherX")
    st.page_link("pages/5_Contact_Support.py", label="📞 Contact Support")

    render_footer()


# ---------------------------------------------------------
# APP ENTRY POINT
# ---------------------------------------------------------
def main():
    user = get_current_user()

    if user is None:
        login_view()
    else:
        dashboard_view()


if __name__ == "__main__":
    main()
