import streamlit as st
from supabase import create_client

@st.cache_resource
def supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def log_engine_run(user_id, org_id, engine_type, input_bytes, output_bytes, status):
    sb = supabase()

    compression_ratio = None
    if input_bytes and output_bytes:
        compression_ratio = output_bytes / input_bytes

    sb.table("engine_logs").insert({
        "user_id": user_id,
        "org_id": org_id,
        "engine_type": engine_type,
        "input_bytes": input_bytes,
        "output_bytes": output_bytes,
        "compression_ratio": compression_ratio,
        "status": status
    }).execute()
