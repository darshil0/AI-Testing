import streamlit as st
import json
import pandas as pd
import glob
from pathlib import Path
import subprocess
import sys


def show_dashboard():
    st.set_page_config(page_title="AI Benchmark Dashboard", layout="wide")

    st.title("🤖 AI-Testing Benchmark Dashboard")
    st.markdown("Interactive analysis of your model evaluation runs.")

    # Get the directory of the currently running script
    script_dir = Path(__file__).parent
    results_dir = script_dir / "results"

    # Load available runs
    run_files = glob.glob(str(results_dir / "run_*.json"))
    run_files.sort(reverse=True)

    if not run_files:
        st.warning(f"No evaluation runs found in {results_dir}. Run an evaluation first!")
        st.stop()

    # Sidebar for run selection
    st.sidebar.header("Settings")
    selected_run = st.sidebar.selectbox(
        "Select Evaluation Run", 
        run_files, 
        format_func=lambda x: Path(x).name
    )

    with open(selected_run, "r") as f:
        data = json.load(f)
        df = pd.DataFrame(data)

    # Metrics Layout
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Tests", len(df))
    m2.metric("Avg Score", f"{df['judge_score'].mean():.2f}")
    m3.metric("Avg Latency", f"{df['duration_seconds'].mean():.2f}s")
    m4.metric("Total Cost", f"${df['estimated_cost'].sum():.4f}")

    # PII Warning
    pii_count = df["pii_found"].sum()
    if pii_count > 0:
        st.error(
            f"⚠️ Security Alert: {pii_count} responses contained potential PII leaks!"
        )

    # Tabs
    tab1, tab2, tab3 = st.tabs(
        ["📊 Detailed Results", "📈 Model Comparisons", "🛡️ Security & PII"]
    )

    with tab1:
        st.subheader("Run Overview")
        # Display styled dataframe
        display_cols = [
            "test_case_name", "model_type", "category", 
            "judge_score", "duration_seconds", "estimated_cost"
        ]
        st.dataframe(
            df[display_cols].style.background_gradient(subset=["judge_score"], cmap="RdYlGn"),
            use_container_width=True
        )

        st.divider()
        
        st.subheader("Individual Response View")
        case = st.selectbox(
            "Select a test case to inspect", df["test_case_name"].unique()
        )
        case_data = df[df["test_case_name"] == case].iloc[0]

        c1, c2 = st.columns(2)
        with c1:
            st.info("**Prompt:**")
            st.markdown(f"```text\n{case_data['prompt']}\n```")
        with c2:
            st.success("**Model Response:**")
            st.markdown(f"```text\n{case_data['response']}\n```")
            st.warning(f"**Judge Reasoning:**\n\n{case_data['judge_reasoning']}")

    with tab2:
        st.subheader("Performance by Model")
        chart_type = st.radio(
            "Metric to Compare", ["Avg Score", "Avg Latency", "Total Cost"], horizontal=True
        )

        # Prepare Aggregated Data
        if chart_type == "Avg Score":
            chart_data = df.groupby("model_type")["judge_score"].mean()
        elif chart_type == "Avg Latency":
            chart_data = df.groupby("model_type")["duration_seconds"].mean()
        else:
            chart_data = df.groupby("model_type")["estimated_cost"].sum()
        
        st.bar_chart(chart_data)

    with tab3:
        if pii_count > 0:
            st.write("The following cases triggered PII warnings:")
            st.table(
                df[df["pii_found"] == True][
                    ["test_case_name", "model_type", "pii_types"]
                ]
            )
        else:
            st.success("No PII leaks detected in this run.")

    st.sidebar.markdown("---")
    st.sidebar.info("V2.1.0 - Production Ready")


if __name__ == "__main__":
    # Check if the script is being run directly via 'python dashboard.py'
    # If so, it will launch the Streamlit process properly.
    if st.runtime.exists():
        show_dashboard()
    else:
        script_path = Path(__file__).resolve()
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(script_path)])
