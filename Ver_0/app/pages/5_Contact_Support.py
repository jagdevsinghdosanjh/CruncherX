import streamlit as st
from Ver_0.app.components.sidebar import render_sidebar
from Ver_0.app.components.footer import render_footer

render_sidebar()
st.title("📞 Contact Support")

st.write("**Email:** jagdevsinghdosanjh@gmail.com")
st.write("**WhatsApp:** +91-8146553307")

render_footer()
