import streamlit as st
from supabase import create_client

@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]   # ✔ correct key name
    return create_client(url, key)