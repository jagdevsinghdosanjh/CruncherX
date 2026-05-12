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

render_sidebar()
st.title("☁ Cloud Compressor")

# Require login
user = get_current_user()
if user is None:
    st.switch_page("Home.py")

USER_ID = user["id"]
ORG_ID = ""

sb = get_supabase_client()

# Load plan
plan = get_user_plan(USER_ID)
if plan is None:
    st.error("No active plan found.")
    st.stop()

st.info(f"Your Plan: **{plan['plan']['name']}**")

uploaded_files = st.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Start Cloud Compression"):

        for file in uploaded_files:
            st.write(f"📄 Processing: **{file.name}**")

            rules = enforce_plan_rules(plan)
            if not rules.get("allowed", False):
                st.error(rules.get("reason"))
                continue

            temp_dir = tempfile.gettempdir()
            unique_name = f"{uuid.uuid4()}_{file.name}"
            input_path = os.path.join(temp_dir, unique_name)

            with open(input_path, "wb") as f:
                f.write(file.getvalue())

            output_path = None
            size_mb = None
            mode = None

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

            st.success(f"Compressed Size: {size_mb:.2f} MB ({mode})")

            with open(output_path, "rb") as f:
                st.download_button(
                    label=f"⬇ Download {file.name}",
                    data=f.read(),
                    file_name=f"crunched_{file.name}",
                    mime="application/pdf"
                )

            log_usage(
                user_id=USER_ID,
                org_id=ORG_ID,
                action="compress",
                bytes_in=os.path.getsize(input_path),
                bytes_out=os.path.getsize(output_path),
            )

            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

render_footer()


# import streamlit as st
# import uuid
# import os
# import tempfile
# from typing import Optional

# from components.sidebar import render_sidebar
# from components.footer import render_footer

# from engines.cruncher_cloud import compress_to_target
# from backend.subscriptions import (
#     get_user_plan,
#     enforce_plan_rules,
#     log_usage,
# )
# from backend.supabase_client import get_supabase_client


# # -----------------------------
# # Layout
# # -----------------------------
# render_sidebar()
# st.title("☁ Cloud Compressor")


# # -----------------------------
# # Simulated auth (replace later)
# # -----------------------------
# USER_ID: str = "demo-user-123"
# ORG_ID: str = ""  # keep as empty string instead of None to satisfy type hints


# # -----------------------------
# # Load user + plan
# # -----------------------------
# user = get_user_plan(USER_ID)

# if user is None:
#     st.error("User not found or no active plan. Please sign in or subscribe.")
#     st.stop()

# plan_name = user["plan"].get("name", "Unknown")
# st.info(f"Your Plan: **{plan_name}**")


# # -----------------------------
# # File upload
# # -----------------------------
# uploaded_files = st.file_uploader(
#     "Upload PDFs",
#     type=["pdf"],
#     accept_multiple_files=True
# )

# # Supabase client (for engine + logs)
# sb = get_supabase_client()


# # -----------------------------
# # Main action
# # -----------------------------
# if uploaded_files:
#     if st.button("Start Cloud Compression"):

#         for file in uploaded_files:
#             st.write(f"📄 Processing: **{file.name}**")

#             # 1. Enforce plan rules (includes expiry + daily limit)
#             rules = enforce_plan_rules(user)
#             if not rules.get("allowed", False):
#                 st.error(rules.get("reason", "Not allowed by plan."))
#                 continue

#             # 2. Save to temp file
#             temp_dir = tempfile.gettempdir()
#             unique_name = f"{uuid.uuid4()}_{file.name}"
#             input_path: str = os.path.join(temp_dir, unique_name)

#             with open(input_path, "wb") as f:
#                 f.write(file.getvalue())

#             output_path: Optional[str] = None
#             size_mb: Optional[float] = None
#             mode: Optional[str] = None

#             # 3. Cloud compression
#             with st.spinner("Compressing in cloud..."):
#                 try:
#                     # Expected signature:
#                     # compress_to_target(input_path, supabase, user_id, org_id)
#                     result = compress_to_target(
#                         input_path,
#                         sb,
#                         USER_ID,
#                         ORG_ID,
#                     )
#                     # Be explicit in case the engine returns a tuple with Optional types
#                     output_path, size_mb, mode = result
#                 except Exception as e:
#                     st.error(f"Cloud compression failed: {e}")
#                     # Cleanup input file even on failure
#                     if os.path.exists(input_path):
#                         os.remove(input_path)
#                     continue

#             # Guard against None for type checker and safety
#             if output_path is None or size_mb is None or mode is None:
#                 st.error("Cloud compression returned invalid result.")
#                 if os.path.exists(input_path):
#                     os.remove(input_path)
#                 continue

#             # 4. Show result
#             st.success(f"Compressed Size: {size_mb:.2f} MB ({mode})")

#             # 5. Download button
#             with open(output_path, "rb") as f:
#                 st.download_button(
#                     label=f"⬇ Download {file.name}",
#                     data=f.read(),
#                     file_name=f"crunched_{file.name}",
#                     mime="application/pdf"
#                 )

#             # 6. Log usage (for daily limit + analytics)
#             try:
#                 bytes_in = os.path.getsize(input_path)
#                 bytes_out = os.path.getsize(output_path)

#                 log_usage(
#                     user_id=USER_ID,
#                     org_id=ORG_ID,  # now always a str
#                     action="compress",
#                     bytes_in=bytes_in,
#                     bytes_out=bytes_out,
#                 )
#             except Exception as e:
#                 st.warning(f"Usage logging failed: {e}")

#             # 7. Cleanup temp files
#             try:
#                 if os.path.exists(input_path):
#                     os.remove(input_path)
#                 if os.path.exists(output_path):
#                     os.remove(output_path)
#             except Exception:
#                 pass

# render_footer()

# # import streamlit as st
# # import uuid
# # import os
# # import tempfile

# # from components.sidebar import render_sidebar
# # from components.footer import render_footer

# # from engines.cruncher_cloud import compress_to_target
# # from backend.subscriptions import (
# #     get_user_plan,
# #     enforce_plan_rules,
# #     log_usage,
# # )
# # from backend.supabase_client import get_supabase_client


# # # -----------------------------
# # # Layout
# # # -----------------------------
# # render_sidebar()
# # st.title("☁ Cloud Compressor")


# # # -----------------------------
# # # Simulated auth (replace later)
# # # -----------------------------
# # USER_ID = "demo-user-123"
# # ORG_ID = None


# # # -----------------------------
# # # Load user + plan
# # # -----------------------------
# # user = get_user_plan(USER_ID)

# # if user is None:
# #     st.error("User not found or no active plan. Please sign in or subscribe.")
# #     st.stop()

# # plan_name = user["plan"].get("name", "Unknown")
# # st.info(f"Your Plan: **{plan_name}**")


# # # -----------------------------
# # # File upload
# # # -----------------------------
# # uploaded_files = st.file_uploader(
# #     "Upload PDFs",
# #     type=["pdf"],
# #     accept_multiple_files=True
# # )

# # # Supabase client (for engine + logs)
# # sb = get_supabase_client()


# # # -----------------------------
# # # Main action
# # # -----------------------------
# # if uploaded_files:
# #     if st.button("Start Cloud Compression"):

# #         for file in uploaded_files:
# #             st.write(f"📄 Processing: **{file.name}**")

# #             # 1. Enforce plan rules (includes expiry + daily limit)
# #             rules = enforce_plan_rules(user)
# #             if not rules.get("allowed", False):
# #                 st.error(rules.get("reason", "Not allowed by plan."))
# #                 continue

# #             # 2. Save to temp file
# #             temp_dir = tempfile.gettempdir()
# #             unique_name = f"{uuid.uuid4()}_{file.name}"
# #             input_path = os.path.join(temp_dir, unique_name)

# #             with open(input_path, "wb") as f:
# #                 f.write(file.getvalue())

# #             # 3. Cloud compression
# #             with st.spinner("Compressing in cloud..."):
# #                 try:
# #                     # Cloud engine signature:
# #                     # compress_to_target(input_path, supabase, user_id, org_id)
# #                     output_path, size_mb, mode = compress_to_target(
# #                         input_path,
# #                         sb,
# #                         USER_ID,
# #                         ORG_ID,
# #                     )
# #                 except Exception as e:
# #                     st.error(f"Cloud compression failed: {e}")
# #                     # Cleanup input file even on failure
# #                     if os.path.exists(input_path):
# #                         os.remove(input_path)
# #                     continue

# #             # 4. Show result
# #             st.success(f"Compressed Size: {size_mb:.2f} MB ({mode})")

# #             # 5. Download button
# #             with open(output_path, "rb") as f:
# #                 st.download_button(
# #                     label=f"⬇ Download {file.name}",
# #                     data=f.read(),
# #                     file_name=f"crunched_{file.name}",
# #                     mime="application/pdf"
# #                 )

# #             # 6. Log usage (for daily limit + analytics)
# #             try:
# #                 log_usage(
# #                     user_id=USER_ID,
# #                     org_id=ORG_ID,
# #                     action="compress",
# #                     bytes_in=os.path.getsize(input_path),
# #                     bytes_out=os.path.getsize(output_path),
# #                 )
# #             except Exception as e:
# #                 st.warning(f"Usage logging failed: {e}")

# #             # 7. Cleanup temp files
# #             try:
# #                 if os.path.exists(input_path):
# #                     os.remove(input_path)
# #                 if os.path.exists(output_path):
# #                     os.remove(output_path)
# #             except Exception:
# #                 pass

# # render_footer()
