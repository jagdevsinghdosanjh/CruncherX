import streamlit as st
import uuid
import os
import tempfile
from components.sidebar import render_sidebar
from components.footer import render_footer
from engines.cruncher_local import compress_to_target
from backend.subscription import (
    get_user_plan,
    check_daily_limit,
    enforce_plan_rules,
    log_usage
)

render_sidebar()
st.title("💻 Local Compressor")

# Simulated user_id (replace with real auth)
USER_ID = "demo-user-123"
ORG_ID = None

# Load user plan
plan = get_user_plan(USER_ID)
st.info(f"Your Plan: **{plan['name']}**")

uploaded_files = st.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Start Local Compression"):

        for file in uploaded_files:

            st.write(f"📄 Processing: **{file.name}**")

            # 1. Enforce subscription rules
            allowed, reason = enforce_plan_rules(plan, job_type="compression")
            if not allowed:
                st.error(reason)
                continue

            # 2. Daily limit check
            if not check_daily_limit(USER_ID):
                st.error("❌ Daily limit reached for Free plan.")
                continue

            # 3. Save file safely
            temp_dir = tempfile.gettempdir()
            unique_name = f"{uuid.uuid4()}_{file.name}"
            input_path = os.path.join(temp_dir, unique_name)

            with open(input_path, "wb") as f:
                f.write(file.getvalue())

            # 4. Compress with spinner
            with st.spinner("Compressing..."):
                try:
                    output_path, size_mb, mode = compress_to_target(
                        input_path,
                        target_mb=7,
                        user_plan=plan,
                        user_id=USER_ID,
                        org_id=ORG_ID
                    )
                except Exception as e:
                    st.error(f"Compression failed: {e}")
                    continue

            # 5. Show results
            st.success(f"Compressed Size: {size_mb:.2f} MB ({mode})")

            # 6. Download button
            with open(output_path, "rb") as f:
                st.download_button(
                    label=f"⬇ Download {file.name}",
                    data=f.read(),
                    file_name=f"crunched_{file.name}",
                    mime="application/pdf"
                )

            # 7. Log usage
            log_usage(
                user_id=USER_ID,
                org_id=ORG_ID,
                action="local_compression",
                bytes_in=os.path.getsize(input_path),
                bytes_out=os.path.getsize(output_path)
            )

            # 8. Cleanup
            os.remove(input_path)
            os.remove(output_path)

render_footer()

# import streamlit as st
# from components.sidebar import render_sidebar
# from components.footer import render_footer
# from engines.cruncher_cloud import compress_to_target
# import os

# render_sidebar()
# st.title("☁ Cloud Compressor")

# uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

# if uploaded_files:
#     if st.button("Start Cloud Compression"):
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
#                     file_name=f"crunched_{file.name}",
#                     mime="application/pdf"
#                 )

# render_footer()
