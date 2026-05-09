import streamlit as st
from components.sidebar import render_sidebar
from components.footer import render_footer

render_sidebar()
st.title("ℹ About CruncherX")

st.markdown(\"\"\"
**CruncherX** is a dual-engine PDF compression suite:

- ☁ **Cloud Engine** for safe, online compression  
- 💻 **Local Bulldozer Engine** for maximum offline compression  

Built for educators, admins, and professionals who handle large scanned PDFs daily.
\"\"\")

render_footer()
