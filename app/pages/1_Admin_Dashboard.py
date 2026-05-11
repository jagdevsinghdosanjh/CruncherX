import streamlit as st
from backend.monitoring.stats import get_basic_stats
from backend.supabase_client import get_supabase

def main():
    st.title("Admin Dashboard")

    # -----------------------------
    # Summary Metrics
    # -----------------------------
    stats = get_basic_stats()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", stats.get("users", 0))
    col2.metric("Organizations", stats.get("orgs", 0))
    col3.metric("Total Jobs", stats.get("jobs", 0))

    st.markdown("---")

    # -----------------------------
    # Recent Usage Logs
    # -----------------------------
    st.subheader("Recent Usage Logs")

    supabase = get_supabase()
    logs = (
        supabase.table("usage_logs")
        .select("*")
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )

    if logs.data:
        for log in logs.data:
            st.write(
                f"**{log['created_at']}** — `{log['action']}` — "
                f"{log['bytes_in']} bytes → {log['bytes_out']} bytes"
            )
    else:
        st.info("No usage logs found yet.")
