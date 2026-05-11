import streamlit as st
import pandas as pd
import altair as alt
from backend.supabase_client import get_supabase_client

st.set_page_config(page_title="Monitoring Dashboard", layout="wide")

def load_table(supabase, table):
    try:
        data = supabase.table(table).select("*").order("created_at", desc=True).execute()
        return pd.DataFrame(data.data) if data.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def safe_col(df, col):
    return col in df.columns and not df.empty

def main():
    st.title("📊 CruncherX Monitoring Dashboard")

    supabase = get_supabase_client()

    # Load all monitoring tables
    engine_logs = load_table(supabase, "engine_logs")
    latency_stats = load_table(supabase, "latency_stats")
    error_logs = load_table(supabase, "error_logs")
    job_metrics = load_table(supabase, "job_metrics")

    st.markdown("### 🔍 System Overview")

    col1, col2, col3, col4 = st.columns(4)

    # ===== SAFE METRICS =====
    total_jobs = len(engine_logs)

    cloud_jobs = (
        len(engine_logs[engine_logs["engine_type"] == "cloud"])
        if safe_col(engine_logs, "engine_type")
        else 0
    )

    local_jobs = (
        len(engine_logs[engine_logs["engine_type"] == "local"])
        if safe_col(engine_logs, "engine_type")
        else 0
    )

    total_errors = len(error_logs)

    col1.metric("Total Jobs", total_jobs)
    col2.metric("Cloud Jobs", cloud_jobs)
    col3.metric("Local Jobs", local_jobs)
    col4.metric("Errors", total_errors)

    st.markdown("---")

    # ============================
    # ENGINE PERFORMANCE CHART
    # ============================
    st.subheader("⚙️ Engine Performance (Compression Ratio Over Time)")

    if safe_col(engine_logs, "compression_ratio") and safe_col(engine_logs, "created_at"):
        engine_logs["created_at"] = pd.to_datetime(engine_logs["created_at"])

        chart = (
            alt.Chart(engine_logs)
            .mark_line(point=True)
            .encode(
                x="created_at:T",
                y="compression_ratio:Q",
                color="engine_type:N",
                tooltip=[
                    "engine_type",
                    "input_bytes",
                    "output_bytes",
                    "compression_ratio",
                    "created_at",
                ],
            )
            .properties(height=300)
        )

        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No engine logs yet.")

    st.markdown("---")

    # ============================
    # LATENCY CHART
    # ============================
    st.subheader("⏱ Latency Over Time")

    if safe_col(latency_stats, "duration_ms") and safe_col(latency_stats, "created_at"):
        latency_stats["created_at"] = pd.to_datetime(latency_stats["created_at"])

        chart = (
            alt.Chart(latency_stats)
            .mark_area(opacity=0.4)
            .encode(
                x="created_at:T",
                y="duration_ms:Q",
                color="engine_type:N",
                tooltip=["engine_type", "duration_ms", "stage", "created_at"],
            )
            .properties(height=300)
        )

        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No latency data yet.")

    st.markdown("---")

    # ============================
    # ERROR LOGS TABLE
    # ============================
    st.subheader("❌ Error Logs")

    if not error_logs.empty:
        st.dataframe(error_logs, use_container_width=True, height=250)
    else:
        st.success("No errors recorded.")

    st.markdown("---")

    # ============================
    # JOB METRICS (CPU + RAM)
    # ============================
    st.subheader("🖥 System Resource Usage (Local Engine)")

    if safe_col(job_metrics, "cpu_usage") and safe_col(job_metrics, "created_at"):
        job_metrics["created_at"] = pd.to_datetime(job_metrics["created_at"])

        cpu_chart = (
            alt.Chart(job_metrics)
            .mark_line(point=True)
            .encode(
                x="created_at:T",
                y="cpu_usage:Q",
                tooltip=["cpu_usage", "memory_usage", "created_at"],
            )
            .properties(title="CPU Usage (%)", height=250)
        )

        mem_chart = (
            alt.Chart(job_metrics)
            .mark_line(point=True, color="orange")
            .encode(
                x="created_at:T",
                y="memory_usage:Q",
                tooltip=["cpu_usage", "memory_usage", "created_at"],
            )
            .properties(title="Memory Usage (MB)", height=250)
        )

        st.altair_chart(cpu_chart, use_container_width=True)
        st.altair_chart(mem_chart, use_container_width=True)

    else:
        st.info("No job metrics yet.")

    st.markdown("---")

    st.caption("CruncherX Monitoring System — Powered by Supabase + Streamlit")

if __name__ == "__main__":
    main()
