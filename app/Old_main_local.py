import streamlit as st
from components.sidebar import render_sidebar
from components.footer import render_footer
from engines.cruncher_local import compress_to_target
import os

st.set_page_config(page_title="CruncherX Local Bulldozer", layout="centered")

render_sidebar()
st.title("💻 CruncherX Local Bulldozer Mode")

uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Start Bulldozer Compression"):
        for file in uploaded_files:
            st.write(f"Processing: {file.name}")
            input_path = file.name
            with open(input_path, "wb") as f:
                f.write(file.getvalue())

            output_path, size_mb, mode = compress_to_target(input_path, target_mb=7)

            st.write(f"Compressed Size: {size_mb:.2f} MB ({mode})")

            with open(output_path, "rb") as f:
                st.download_button(
                    label=f"Download {file.name}",
                    data=f.read(),
                    file_name=f"bulldozer_{file.name}",
                    mime="application/pdf"
                )

render_footer()
