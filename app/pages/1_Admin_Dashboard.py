import streamlit as st
from backend.monitoring.stats import get_basic_stats
from backend.supabase_client import get_supabase_client

st.set_page_config(page_title="Admin Dashboard", layout="wide")

def main():
    st.title("🛠 Admin Dashboard")

    supabase = get_supabase_client()
    stats = get_basic_stats()

    st.markdown("### 🔍 System Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Jobs", stats.get("total_jobs", 0))
    c2.metric("Cloud Jobs", stats.get("cloud_jobs", 0))
    c3.metric("Local Jobs", stats.get("local_jobs", 0))
    c4.metric("Total Errors", stats.get("total_errors", 0))

    st.markdown("---")

    st.markdown("### 📦 Raw Tables")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Engine Logs")
        try:
            logs = supabase.table("engine_logs").select("*").order("created_at", desc=True).limit(50).execute()
            st.dataframe(logs.data or [], width="stretch", height=300)
        except Exception as e:
            st.error(f"Error loading engine_logs: {e}")

    with col_right:
        st.subheader("Error Logs")
        try:
            errors = supabase.table("error_logs").select("*").order("created_at", desc=True).limit(50).execute()
            st.dataframe(errors.data or [], width="stretch", height=300)
        except Exception as e:
            st.error(f"Error loading error_logs: {e}")

if __name__ == "__main__":
    main()

# import streamlit as st
# from backend.monitoring.stats import get_basic_stats
# from backend.supabase_client import get_supabase_client

# st.set_page_config(page_title="Admin Dashboard", layout="wide")

# def main():
#     st.title("🛠 Admin Dashboard")

#     # Ensure Supabase is reachable (will raise if secrets missing)
#     supabase = get_supabase_client()

#     # High‑level stats from monitoring.stats
#     stats = get_basic_stats()

#     st.markdown("### 🔍 System Overview")

#     c1, c2, c3, c4 = st.columns(4)
#     c1.metric("Total Jobs", stats.get("total_jobs", 0))
#     c2.metric("Cloud Jobs", stats.get("cloud_jobs", 0))
#     c3.metric("Local Jobs", stats.get("local_jobs", 0))
#     c4.metric("Total Errors", stats.get("total_errors", 0))

#     st.markdown("---")

#     st.markdown("### 📦 Raw Tables (Quick Admin Peek)")

#     col_left, col_right = st.columns(2)

#     with col_left:
#         st.subheader("Engine Logs")
#         try:
#             engine_logs = supabase.table("engine_logs").select("*").order("created_at", desc=True).limit(50).execute()
#             if engine_logs.data:
#                 st.dataframe(engine_logs.data, width="stretch", height=300)
#             else:
#                 st.info("No engine logs yet.")
#         except Exception as e:
#             st.error(f"Error loading engine_logs: {e}")

#     with col_right:
#         st.subheader("Error Logs")
#         try:
#             error_logs = supabase.table("error_logs").select("*").order("created_at", desc=True).limit(50).execute()
#             if error_logs.data:
#                 st.dataframe(error_logs.data, width="stretch", height=300)
#             else:
#                 st.success("No errors recorded.")
#         except Exception as e:
#             st.error(f"Error loading error_logs: {e}")

#     st.markdown("---")
#     st.caption("CruncherX Admin Dashboard — Org‑level view over engines, jobs, and failures.")

# if __name__ == "__main__":
#     main()

# # import streamlit as st
# # from backend.monitoring.stats import get_basic_stats
# # from backend.supabase_client import get_supabase

# # def main():
# #     st.title("Admin Dashboard")

# #     # -----------------------------
# #     # Summary Metrics
# #     # -----------------------------
# #     stats = get_basic_stats()

# #     col1, col2, col3 = st.columns(3)
# #     col1.metric("Total Users", stats.get("users", 0))
# #     col2.metric("Organizations", stats.get("orgs", 0))
# #     col3.metric("Total Jobs", stats.get("jobs", 0))

# #     st.markdown("---")

# #     # -----------------------------
# #     # Recent Usage Logs
# #     # -----------------------------
# #     st.subheader("Recent Usage Logs")

# #     supabase = get_supabase()
# #     logs = (
# #         supabase.table("usage_logs")
# #         .select("*")
# #         .order("created_at", desc=True)
# #         .limit(10)
# #         .execute()
# #     )

# #     if logs.data:
# #         for log in logs.data:
# #             st.write(
# #                 f"**{log['created_at']}** — `{log['action']}` — "
# #                 f"{log['bytes_in']} bytes → {log['bytes_out']} bytes"
# #             )
# #     else:
# #         st.info("No usage logs found yet.")

# # main()
