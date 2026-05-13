import streamlit as st
import uuid
import os
import tempfile

from components.sidebar import render_sidebar
from components.footer import render_footer

from engines.cruncher_cloud import compress_to_target
from backend.subscriptions import (
    get_user_plan,
    enforce_plan_rules,
    log_usage,
)
from backend.supabase_client import get_supabase_client
from auth import get_current_user


# ---------------- UI ----------------
render_sidebar()
st.title("☁ Cloud Compressor")


# ---------------- AUTH ----------------
user = get_current_user()
if user is None:
    st.switch_page("Home.py")

USER_ID = user["id"]
ORG_ID = ""   # You can fill this later if orgs are enabled

sb = get_supabase_client()


# ---------------- PLAN LOADING ----------------
plan = get_user_plan(USER_ID)

if plan is None:
    st.error("No active plan found.")
    st.stop()

st.info(f"Your Plan: **{plan['plan']['name']}**")


# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True
)


# ---------------- PROCESSING ----------------
if uploaded_files:
    if st.button("Start Cloud Compression"):

        for file in uploaded_files:
            st.write(f"📄 Processing: **{file.name}**")

            # Enforce plan rules
            rules = enforce_plan_rules(plan)
            if not rules.get("allowed", False):
                st.error(rules.get("reason"))
                continue

            # Save uploaded file to temp
            temp_dir = tempfile.gettempdir()
            unique_name = f"{uuid.uuid4()}_{file.name}"
            input_path = os.path.join(temp_dir, unique_name)

            with open(input_path, "wb") as f:
                f.write(file.getvalue())

            # Run cloud engine
            with st.spinner("Compressing in cloud..."):
                try:
                    output_path, size_mb, mode = compress_to_target(
                        input_path,
                        sb,
                        USER_ID,
                        ORG_ID,
                    )
                except Exception as e:
                    st.error(f"Cloud compression failed: {e}")
                    if os.path.exists(input_path):
                        os.remove(input_path)
                    continue

            if output_path is None:
                st.error("Cloud engine returned no output.")
                continue

            # Show result
            st.success(f"Compressed Size: {size_mb:.2f} MB ({mode})")

            # Download button
            with open(output_path, "rb") as f:
                st.download_button(
                    label=f"⬇ Download {file.name}",
                    data=f.read(),
                    file_name=f"crunched_{file.name}",
                    mime="application/pdf"
                )

            # Log usage
            log_usage(
                user_id=USER_ID,
                org_id=ORG_ID,
                action="compress",
                bytes_in=os.path.getsize(input_path),
                bytes_out=os.path.getsize(output_path),
            )

            # Cleanup
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)


# ---------------- FOOTER ----------------
render_footer()
