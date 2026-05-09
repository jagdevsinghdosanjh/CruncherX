import streamlit as st

def render_sidebar():
    st.sidebar.markdown(\"\"\"
    <div style='text-align:center; padding:15px'>
        <h1 style='color:#39FF14; margin-bottom:0;'>CruncherX</h1>
        <p style='color:#AAAAAA; margin-top:4px;'>PDF Compression Suite</p>
        <hr style='border-color:#39FF14;'>
    </div>
    \"\"\", unsafe_allow_html=True)
