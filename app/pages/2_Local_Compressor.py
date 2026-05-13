import streamlit as st
from backend.supabase_client import get_supabase_client
from engines.cruncher_local import compress_to_target_local
from components.sidebar import render_sidebar
from components.footer import render_footer


def run():
    st.header("💻 Local Compressor (Bulldozer Mode)")

    render_sidebar()

    supabase = get_supabase_client()

    # -----------------------------
    # Load user session
    # -----------------------------
    user = st.session_state.get("user")

    if not user:
        st.error("You must be logged in to use the Local Compressor.")
        return

    user_id = user["id"]
    org_id = user.get("org_id")

    # -----------------------------
    # File upload
    # -----------------------------
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        input_path = f"/tmp/{uploaded_file.name}"
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("Running Bulldozer Engine…")

        # -----------------------------
        # Call subscription-aware engine
        # -----------------------------
        output_path, size_mb, status = compress_to_target(
            input_path=input_path,
            user_id=user_id,
            org_id=org_id,
            supabase=supabase,
            is_bulk=False
        )

        # -----------------------------
        # Handle subscription errors
        # -----------------------------
        if output_path is None:
            st.error(status)  # status contains the reason
            return

        # -----------------------------
        # Success
        # -----------------------------
        st.success(f"Done — {size_mb:.2f} MB")

        # Pylance-safe: output_path is guaranteed to be str here
        with open(output_path, "rb") as f:
            st.download_button(
                label="Download Compressed PDF",
                data=f.read(),
                file_name=output_path,
                mime="application/pdf"
            )

    render_footer()
