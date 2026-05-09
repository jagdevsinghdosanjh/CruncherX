import streamlit as st

def render_sidebar():
    st.sidebar.markdown(\"\"\"
    <div style='text-align:center; padding:15px'>
        <h1 style='color:#5A4FF3;'>CruncherX</h1>
        <p style='color:gray;'>PDF Compression Suite</p>
    </div>
    \"\"\", unsafe_allow_html=True)
