import streamlit as st
import json
import pandas as pd
import glob
from pathlib import Path

st.set_page_config(page_title="AI Benchmark Dashboard", layout="wide")

st.title("🤖 AI-Testing Benchmark Dashboard")
st.markdown("Interactive analysis of your model evaluation runs.")

# Load available runs
run_files = glob.glob("ai_evaluation/results/run_*.json")
run_files.sort(reverse=True)

if not run_files:
    st.warning("No evaluation runs found. Run an evaluation first!")
else:
    selected_run = st.sidebar.selectbox("Select Evaluation Run", run_files)
    
    with open(selected_run, 'r') as f:
        data = json.load(f)
        df = pd.DataFrame(data)

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Tests", len(df))
    m2.metric("Avg Score", round(df["judge_score"].mean(), 2))
    m3.metric("Avg Latency", f"{round(df['duration_seconds'].mean(), 2)}s")
    m4.metric("Total Cost", f"${round(df['estimated_cost'].sum(), 4)}")

    # PII Warning
    pii_count = df["pii_found"].sum()
    if pii_count > 0:
        st.error(f"⚠️ Security Alert: {pii_count} responses contained potential PII leaks!")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Detailed Results", "📈 Model Comparisons", "🛡️ Security & PII"])

    with tab1:
        st.dataframe(df[["test_case_name", "model_type", "category", "judge_score", "duration_seconds", "estimated_cost"]].style.background_gradient(subset=['judge_score'], cmap='RdYlGn'))
        
        st.subheader("Individual Response View")
        case = st.selectbox("Select a test case to inspect", df["test_case_name"].unique())
        case_data = df[df["test_case_name"] == case].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            st.info("**Prompt:**")
            st.text(case_data["prompt"])
        with c2:
            st.success("**Model Response:**")
            st.text(case_data["response"])
            st.markdown(f"**Judge Reasoning:** {case_data['judge_reasoning']}")

    with tab2:
        st.subheader("Performance by Model")
        chart_type = st.radio("Chart Type", ["Avg Score", "Avg Latency", "Cost"], horizontal=True)
        
        if chart_type == "Avg Score":
            st.bar_chart(df.groupby("model_type")["judge_score"].mean())
        elif chart_type == "Avg Latency":
            st.bar_chart(df.groupby("model_type")["duration_seconds"].mean())
        else:
            st.bar_chart(df.groupby("model_type")["estimated_cost"].sum())

    with tab3:
        if pii_count > 0:
            st.write("The following cases triggered PII warnings:")
            st.table(df[df["pii_found"] == True][["test_case_name", "model_type", "pii_types"]])
        else:
            st.success("No PII leaks detected in this run.")

st.sidebar.markdown("---")
st.sidebar.info("V1.1.0 - Production Ready")
