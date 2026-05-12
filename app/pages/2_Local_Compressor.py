import streamlit as st
from backend.supabase_client import get_supabase_client
from engines.cruncher_local import compress_to_target
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
        if status not in ["Bulldozer", "success"]:
            st.error(status)  # status contains the reason (e.g., "Daily limit reached")
            return

        # -----------------------------
        # Success
        # -----------------------------
        st.success(f"Done — {size_mb:.2f} MB")

        with open(output_path, "rb") as f:
            st.download_button(
                label="Download Compressed PDF",
                data=f.read(),
                file_name=output_path,
                mime="application/pdf"
            )

    render_footer()

# import streamlit as st
# from components.sidebar import render_sidebar
# from components.footer import render_footer
# from engines.cruncher_local import compress_to_target
# import os

# render_sidebar()
# st.title("💻 Local Bulldozer Compressor")

# uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

# if uploaded_files:
#     if st.button("Start Bulldozer Compression"):
#         for file in uploaded_files:
#             st.write(f"Processing: {file.name}")
#             input_path = file.name
#             with open(input_path, "wb") as f:
#                 f.write(file.getvalue())

#             output_path, size_mb, mode = compress_to_target(input_path, target_mb=7)

#             st.write(f"Compressed Size: {size_mb:.2f} MB ({mode})")

#             with open(output_path, "rb") as f:
#                 st.download_button(
#                     label=f"Download {file.name}",
#                     data=f.read(),
#                     file_name=f"bulldozer_{file.name}",
#                     mime="application/pdf"
#                 )

# render_footer()
