import streamlit as st
import uuid
import os
import tempfile
import gc
import time

from components.sidebar import render_sidebar
from components.footer import render_footer

from engines.cruncher_local import compress_to_target_local


# ---------------- UI ----------------
render_sidebar()
st.title("💻 Local Compressor")


# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True
)


# ---------------- PROCESSING ----------------
if uploaded_files:
    if st.button("Start Local Compression"):

        for file in uploaded_files:
            st.write(f"📄 Processing: **{file.name}**")

            # Save uploaded file to temp
            temp_dir = tempfile.gettempdir()
            unique_name = f"{uuid.uuid4()}_{file.name}"
            input_path = os.path.join(temp_dir, unique_name)

            with open(input_path, "wb") as f:
                f.write(file.getvalue())

            # Release Streamlit's file handle and force GC (Windows lock fix)
            file = None
            gc.collect()

            # Run local engine
            with st.spinner("Compressing locally..."):
                try:
                    output_path, size_mb, mode = compress_to_target_local(
                        input_path,
                        target_mb=7
                    )
                except Exception as e:
                    st.error(f"Local compression failed: {e}")
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
                st.error("Local engine returned no output.")
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
                    label=f"⬇ Download {unique_name.split('_', 1)[-1]}",
                    data=f_out.read(),
                    file_name=f"local_{unique_name.split('_', 1)[-1]}",
                    mime="application/pdf"
                )

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
