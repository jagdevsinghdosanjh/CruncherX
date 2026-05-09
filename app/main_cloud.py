import streamlit as st
from components.sidebar import render_sidebar
from engines.cruncher_cloud import compress_to_target

render_sidebar()
st.title("☁ CruncherX Cloud Compressor (<7MB)")

uploaded = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded:
    if st.button("Start Compression"):
        for file in uploaded:
            st.write(f"Processing: {file.name}")
            with open(file.name, "wb") as f:
                f.write(file.getvalue())

            out, size, mode = compress_to_target(file.name, 7)

            with open(out, "rb") as f:
                st.download_button(f"Download {file.name}", f.read(), file_name=f"crunched_{file.name}")
