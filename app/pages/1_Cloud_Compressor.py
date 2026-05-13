import streamlit as st
import uuid
import os
import tempfile
import gc
import time

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
ORG_ID=None
#ORG_ID = ""   # Reserved for future org support

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

            # Release Streamlit's file handle and force GC (Windows lock fix)
            file = None
            gc.collect()

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
                    # Best-effort cleanup
                    if os.path.exists(input_path):
                        try:
                            os.remove(input_path)
                        except PermissionError:
                            time.sleep(0.2)
                            try:
                                os.remove(input_path)
                            except:
                                pass
                    continue

            if output_path is None:
                st.error("Cloud engine returned no output.")
                # Cleanup input file
                if os.path.exists(input_path):
                    try:
                        os.remove(input_path)
                    except PermissionError:
                        time.sleep(0.2)
                        try:
                            os.remove(input_path)
                        except:
                            pass
                continue

            # Show result
            st.success(f"Compressed Size: {size_mb:.2f} MB ({mode})")

            # Download button
            with open(output_path, "rb") as f_out:
                st.download_button(
                    label=f"⬇ Download {file.name if file else 'compressed.pdf'}",
                    data=f_out.read(),
                    file_name=f"crunched_{unique_name.split('_', 1)[-1]}",
                    mime="application/pdf"
                )

            # Log usage
            try:
                log_usage(
                    user_id=USER_ID,
                    org_id=ORG_ID,
                    action="compress",
                    bytes_in=os.path.getsize(input_path),
                    bytes_out=os.path.getsize(output_path),
                )
            except Exception as e:
                st.warning(f"Usage logging failed: {e}")

            # Cleanup input/output files with Windows-safe handling
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except PermissionError:
                    time.sleep(0.2)
                    try:
                        os.remove(input_path)
                    except:
                        pass

            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass


# ---------------- FOOTER ----------------
render_footer()

# import streamlit as st
# import uuid
# import os
# import tempfile
# import gc
# import time

# from components.sidebar import render_sidebar
# from components.footer import render_footer

# from engines.cruncher_cloud import compress_to_target


# # ---------------- UI ----------------
# render_sidebar()
# st.title("💻 Local Compressor")


# # ---------------- FILE UPLOAD ----------------
# uploaded_files = st.file_uploader(
#     "Upload PDFs",
#     type=["pdf"],
#     accept_multiple_files=True
# )


# # ---------------- PROCESSING ----------------
# if uploaded_files:
#     if st.button("Start Local Compression"):

#         for file in uploaded_files:
#             st.write(f"📄 Processing: **{file.name}**")

#             # Save uploaded file to temp
#             temp_dir = tempfile.gettempdir()
#             unique_name = f"{uuid.uuid4()}_{file.name}"
#             input_path = os.path.join(temp_dir, unique_name)

#             with open(input_path, "wb") as f:
#                 f.write(file.getvalue())

#             # Release Streamlit's file handle and force GC (Windows lock fix)
#             file = None
#             gc.collect()

#             # Run local engine
#             with st.spinner("Compressing locally..."):
#                 try:
#                     output_path, size_mb, mode = compress_to_target_local(
#                         input_path,
#                         target_mb=7
#                     )
#                 except Exception as e:
#                     st.error(f"Local compression failed: {e}")
#                     # Best-effort cleanup
#                     if os.path.exists(input_path):
#                         try:
#                             os.remove(input_path)
#                         except PermissionError:
#                             time.sleep(0.2)
#                             try:
#                                 os.remove(input_path)
#                             except:
#                                 pass
#                     continue

#             if output_path is None:
#                 st.error("Local engine returned no output.")
#                 # Cleanup input file
#                 if os.path.exists(input_path):
#                     try:
#                         os.remove(input_path)
#                     except PermissionError:
#                         time.sleep(0.2)
#                         try:
#                             os.remove(input_path)
#                         except:
#                             pass
#                 continue

#             # Show result
#             st.success(f"Compressed Size: {size_mb:.2f} MB ({mode})")

#             # Download button
#             with open(output_path, "rb") as f_out:
#                 st.download_button(
#                     label=f"⬇ Download {unique_name.split('_', 1)[-1]}",
#                     data=f_out.read(),
#                     file_name=f"local_{unique_name.split('_', 1)[-1]}",
#                     mime="application/pdf"
#                 )

#             # Cleanup input/output files with Windows-safe handling
#             if os.path.exists(input_path):
#                 try:
#                     os.remove(input_path)
#                 except PermissionError:
#                     time.sleep(0.2)
#                     try:
#                         os.remove(input_path)
#                     except:
#                         pass

#             if os.path.exists(output_path):
#                 try:
#                     os.remove(output_path)
#                 except:
#                     pass


# # ---------------- FOOTER ----------------
# render_footer()
