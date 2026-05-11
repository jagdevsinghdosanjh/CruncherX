import streamlit as st
from backend.supabase_client import get_supabase_client
from engines.cruncher_local import compress_to_target

def run():
    st.header("💻 Local Compressor (Bulldozer)")

    supabase = get_supabase_client()

    user = st.session_state.get("user")
    user_id = user["id"] if user else None
    org_id = user.get("org_id") if user else None

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        input_path = f"/tmp/{uploaded_file.name}"
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("Running Bulldozer Engine…")

        output_path, size_mb, status = compress_to_target(
            input_path=input_path,
            supabase=supabase,
            user_id=user_id,
            org_id=org_id
        )

        if status == "LocalError":
            st.error("Compression failed.")
            return

        st.success(f"Done — {size_mb:.2f} MB")

        with open(output_path, "rb") as f:
            st.download_button(
                label="Download Compressed PDF",
                data=f.read(),
                file_name=output_path,
                mime="application/pdf"
            )
