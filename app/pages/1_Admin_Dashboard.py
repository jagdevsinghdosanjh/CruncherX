import streamlit as st
from backend.monitoring.stats import get_basic_stats
from backend.supabase_client import get_supabase_client

st.set_page_config(page_title="Admin Dashboard", layout="wide")

# ---------------------------------------------------------
# ADMIN ACCESS CONTROL
# ---------------------------------------------------------
ADMIN_EMAILS = ["jagdevsinghdosanjh@gmail.com"]

def require_admin():
    if "current_user" not in st.session_state:
        st.error("You must be logged in.")
        st.stop()

    user = st.session_state["current_user"]

    if user["email"] not in ADMIN_EMAILS:
        st.error("Access denied. Admins only.")
        st.stop()

# ---------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------
def main():
    require_admin()

    st.title("🛠 Admin Dashboard")

    supabase = get_supabase_client()

    # FIXED: get_basic_stats() takes NO arguments
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

    # ---------------- ENGINE LOGS ----------------
    with col_left:
        st.subheader("Engine Logs")
        try:
            logs = (
                supabase.table("engine_logs")
                .select("*")
                .order("created_at", desc=True)
                .limit(50)
                .execute()
            )
            st.dataframe(logs.data or [], height=300)
        except Exception as e:
            st.error(f"Error loading engine_logs: {e}")

    # ---------------- ERROR LOGS ----------------
    with col_right:
        st.subheader("Error Logs")
        try:
            errors = (
                supabase.table("error_logs")
                .select("*")
                .order("created_at", desc=True)
                .limit(50)
                .execute()
            )
            st.dataframe(errors.data or [], height=300)
        except Exception as e:
            st.error(f"Error loading error_logs: {e}")

if __name__ == "__main__":
    main()
