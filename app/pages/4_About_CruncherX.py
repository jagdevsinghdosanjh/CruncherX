import streamlit as st
from components.sidebar import render_sidebar
from components.footer import render_footer

render_sidebar()

st.title("ℹ About CruncherX")

st.markdown("""
**CruncherX** is a dual-engine PDF compression suite designed for speed, clarity, and reliability.

### 🚀 What CruncherX Offers
- ☁ **Cloud Engine** — Safe, fast online compression  
- 💻 **Local Bulldozer Engine** — Maximum offline compression power  
- 📉 **Smart Size Targeting** — Automatically compresses PDFs under 7 MB  
- 🧾 **Perfect for Scanned PDFs** — Ideal for BLOs, schools, offices, and admins  

CruncherX is built for professionals who handle large scanned PDFs daily and need consistent, high-quality compression.
""")

render_footer()

# import streamlit as st
# from components.sidebar import render_sidebar
# from components.footer import render_footer

# render_sidebar()
# st.title("ℹ About CruncherX")

# st.markdown(\"\"\"
# **CruncherX** is a dual-engine PDF compression suite:

# - ☁ **Cloud Engine** for safe, online compression  
# - 💻 **Local Bulldozer Engine** for maximum offline compression  

# Built for educators, admins, and professionals who handle large scanned PDFs daily.
# \"\"\")

# render_footer()
