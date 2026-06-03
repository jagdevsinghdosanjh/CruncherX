import streamlit as st

def render_footer():
    st.markdown(
    """
    <div style='
        text-align:center;
        color:#39FF14;
        font-size:13px;
        padding:12px 0;
        background-color:#000000;
        border-top:1px solid #39FF14;
    '>
        Made in Punjab 🇮🇳 by <b>Jagdev Singh Dosanjh</b> — GHS Chananke<br>
        <span style='opacity:0.85;'>CruncherX — Black & Neon Green Edition</span>
    </div>
    """,
    unsafe_allow_html=True
)


# # import streamlit as st

# # def render_footer():
# #     st.markdown(\"\"\"
# #     <hr>
# #     <div style='text-align:center; color:#888888; font-size:13px;'>
# #         Made in Punjab 🇮🇳 | CruncherX — Black & Neon Green Edition
# #     </div>
# #     \"\"\", unsafe_allow_html=True)
# import streamlit as st

# def render_footer():
#     st.markdown("""
#     <hr>
#     <div style='text-align:center; color:#888888; font-size:13px;'>
#         Made in Punjab 🇮🇳 | CruncherX — Black & Neon Green Edition
#         With Care by - Jagdev Singh Dosanjh GHS Chananke Amritsar. 
#     </div>
#     """, unsafe_allow_html=True)
