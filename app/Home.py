import streamlit as st
from components.sidebar import render_sidebar

render_sidebar()

st.title("🏠 CruncherX Dashboard")
st.write("Smaller PDFs. Bigger Productivity.")

st.subheader("Choose a Mode:")
st.page_link("pages/1_Cloud_Compressor.py", label="☁ Cloud Compressor")
st.page_link("pages/2_Local_Compressor.py", label="💻 Local Bulldozer Mode")
st.page_link("pages/3_OCR_Coming_Soon.py", label="🔍 OCR (Coming Soon)")
st.page_link("pages/4_About_CruncherX.py", label="ℹ About CruncherX")
st.page_link("pages/5_Contact_Support.py", label="📞 Contact Support")
