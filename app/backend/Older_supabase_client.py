import streamlit as st
from supabase import create_client

@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]   # ✔ correct key name
    return create_client(url, key)




# from supabase import create_client
# import streamlit as st

# def get_supabase_client():
#     url = st.secrets["SUPABASE_URL"]
#     key = st.secrets["SUPABASE_KEY"]
#     return create_client(url, key)

# def log_engine_run(supabase, user_id, org_id, engine_type, input_bytes, output_bytes, status):
#     compression_ratio = None
#     if input_bytes and output_bytes:
#         compression_ratio = output_bytes / input_bytes

#     supabase.table("engine_logs").insert({
#         "user_id": user_id,
#         "org_id": org_id,
#         "engine_type": engine_type,
#         "input_bytes": input_bytes,
#         "output_bytes": output_bytes,
#         "compression_ratio": compression_ratio,
#         "status": status
#     }).execute()

# from supabase import create_client
# import streamlit as st
# import time

# def get_supabase():
#     url = st.secrets["SUPABASE_URL"]
#     key = st.secrets["SUPABASE_KEY"]
#     return create_client(url, key)



# def log_engine_run(supabase, user_id, org_id, engine_type, input_bytes, output_bytes, status):
#     compression_ratio = None
#     if input_bytes and output_bytes:
#         compression_ratio = output_bytes / input_bytes

#     supabase.table("engine_logs").insert({
#         "user_id": user_id,
#         "org_id": org_id,
#         "engine_type": engine_type,
#         "input_bytes": input_bytes,
#         "output_bytes": output_bytes,
#         "compression_ratio": compression_ratio,
#         "status": status
#     }).execute()
