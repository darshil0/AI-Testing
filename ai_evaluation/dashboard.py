import glob
import json
import subprocess
import sys
from pathlib import Path

# Optional dashboard imports guarded at import time
try:
    import pandas as pd
    import streamlit as st

    DASHBOARD_AVAILABLE = True
except ImportError:
    pd = None  # type: ignore
    st = None  # type: ignore
    DASHBOARD_AVAILABLE = False

# Reconfigure sys.stdout and sys.stderr to use utf-8 on Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def _check_dashboard_dependencies():
    if not DASHBOARD_AVAILABLE:
        raise RuntimeError(
            "Dashboard dependencies (streamlit, pandas, matplotlib, seaborn, numpy) are not installed.\n"
            "Install them with: pip install 'ai-evaluation-framework[dashboard]'"
        )


def _normalize_results_dataframe(df):
    """Normalize legacy and current result data for dashboard rendering."""
    if df.empty:
        return df

    if "score" not in df.columns and "judge_score" in df.columns:
        df["score"] = pd.to_numeric(df["judge_score"], errors="coerce")

    if "judge_score" not in df.columns and "score" in df.columns:
        df["judge_score"] = df["score"]

    if "estimated_cost" not in df.columns and "cost" in df.columns:
        df["estimated_cost"] = pd.to_numeric(df["cost"], errors="coerce").fillna(0.0)

    if "duration_seconds" not in df.columns and "duration" in df.columns:
        df["duration_seconds"] = pd.to_numeric(df["duration"], errors="coerce")

    if "pii_found" not in df.columns:
        df["pii_found"] = False
    if "pii_types" not in df.columns:
        df["pii_types"] = [[] for _ in range(len(df))]

    if "status" not in df.columns:
        df["status"] = "success"

    if "score" in df.columns:
        df["score"] = pd.to_numeric(df["score"], errors="coerce")
        df.loc[df["score"] < 0, "score"] = None

    if "estimated_cost" in df.columns:
        df["estimated_cost"] = pd.to_numeric(df["estimated_cost"], errors="coerce").fillna(0.0)

    if "duration_seconds" in df.columns:
        df["duration_seconds"] = pd.to_numeric(df["duration_seconds"], errors="coerce")

    return df


def show_dashboard():
    _check_dashboard_dependencies()
    st.set_page_config(page_title="AI Benchmark Dashboard", layout="wide")

    st.title("🤖 AI-Testing Benchmark Dashboard")
    st.markdown("Interactive analysis of your model evaluation runs.")

    script_dir = Path(__file__).parent

    custom_config_arg = st.sidebar.text_input(
        "Config File Path", value="ai_evaluation/config.yaml"
    )
    results_dir_name = "results"
    try:
        from .run_evaluation import resolve_config_path, safe_yaml_load

        config_path = resolve_config_path(
            custom_config_arg if custom_config_arg.strip() else None
        )
        with open(config_path, "r", encoding="utf-8") as f:
            config = safe_yaml_load(f) or {}
            results_dir_name = (
                config.get("directories", {}).get("results", "results")
                if isinstance(config, dict)
                else "results"
            )
    except Exception as e:
        config_path = script_dir / "config.yaml"
        st.sidebar.warning(f"Could not load config: {e}")

    results_dir = Path(results_dir_name)
    if not results_dir.is_absolute():
        results_dir = config_path.parent / results_dir

    run_files = glob.glob(str(results_dir / "run_*.json"))
    run_files.sort(reverse=True)

    if not run_files:
        st.warning(
            f"No evaluation runs found in {results_dir}. Run an evaluation first!"
        )
        st.stop()

    st.sidebar.header("Settings")
    selected_run = st.sidebar.selectbox(
        "Select Evaluation Run", run_files, format_func=lambda x: Path(x).name
    )

    try:
        with open(selected_run, "r", encoding="utf-8") as f:
            data = json.load(f)
            df = _normalize_results_dataframe(pd.DataFrame(data))
    except json.JSONDecodeError as e:
        st.error(f"Failed to load run file due to invalid JSON: {e}")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred while loading the run: {e}")
        st.stop()

    if df.empty:
        st.warning("Selected evaluation run contains no data.")
        st.stop()

    # Standardize legacy/current column aliases
    if "cost" in df.columns and "estimated_cost" not in df.columns:
        df["estimated_cost"] = df["cost"]
    elif "estimated_cost" in df.columns and "cost" not in df.columns:
        df["cost"] = df["estimated_cost"]

    if "score" in df.columns and "judge_score" not in df.columns:
        df["judge_score"] = df["score"]
    elif "judge_score" in df.columns and "score" not in df.columns:
        df["score"] = df["judge_score"]

    # Ensure required columns exist with fallback defaults
    required_defaults = {
        "test_case_name": "Unknown",
        "model_type": "Unknown",
        "category": "General",
        "status": "success",
        "score": None,
        "judge_score": None,
        "duration_seconds": None,
        "estimated_cost": 0.0,
        "prompt": "",
        "response": "",
        "judge_reasoning": "",
        "pii_found": False,
        "pii_types": [],
    }
    for col, default_val in required_defaults.items():
        if col not in df.columns:
            df[col] = default_val

    # Standardize score column from score or judge_score
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df.loc[df["score"] < 0, "score"] = None

    df["judge_score"] = pd.to_numeric(df["judge_score"], errors="coerce")
    df.loc[df["judge_score"] < 0, "judge_score"] = None

    df["estimated_cost"] = pd.to_numeric(df["estimated_cost"], errors="coerce").fillna(0.0)
    df["duration_seconds"] = pd.to_numeric(df["duration_seconds"], errors="coerce")

    valid_score_df = df[df["status"].isin(["success"]) & df["score"].notna()].copy()
    valid_dur_df = df[df["duration_seconds"].notna()].copy()

    avg_score_str = (
        f"{valid_score_df['score'].mean():.2f}"
        if not valid_score_df.empty
        else "No valid scores"
    )
    avg_lat_str = (
        f"{valid_dur_df['duration_seconds'].mean():.2f}s"
        if not valid_dur_df.empty
        else "N/A"
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Tests", len(df))
    m2.metric("Avg Score (Valid Successes)", avg_score_str)
    m3.metric("Avg Latency", avg_lat_str)
    m4.metric("Total Cost", f"${df['estimated_cost'].sum():.4f}")

    non_success_df = df[df["status"] != "success"]
    if not non_success_df.empty:
        st.warning(
            f"⚠️ {len(non_success_df)} test case(s) failed, errored, or were invalid in this run."
        )

    pii_count = df["pii_found"].sum()
    if pii_count > 0:
        st.error(
            f"⚠️ Security Alert: {pii_count} responses contained potential PII leaks!"
        )

    tab1, tab2, tab3 = st.tabs(
        ["📊 Detailed Results", "📈 Model Comparisons", "🛡️ Security & PII"]
    )

    with tab1:
        st.subheader("Run Overview")
        display_cols = [
            "test_case_name",
            "model_type",
            "category",
            "status",
            "score",
            "duration_seconds",
            "estimated_cost",
        ]
        st.dataframe(
            df[display_cols],
            use_container_width=True,
        )

        st.divider()

        st.subheader("Individual Response View")
        case = st.selectbox(
            "Select a test case to inspect", df["test_case_name"].unique()
        )

        case_df = df[df["test_case_name"] == case]
        filtered_models = case_df["model_type"].unique()
        selected_model = st.selectbox("Select model to view response", filtered_models)

        matched_rows = case_df[case_df["model_type"] == selected_model]
        if matched_rows.empty:
            st.warning("No data found for selected model.")
        else:
            case_data = matched_rows.iloc[0]
            c1, c2 = st.columns(2)
            with c1:
                st.info("**Prompt:**")
                st.code(str(case_data["prompt"]), language="text")
            with c2:
                st.success("**Model Response:**")
                st.code(str(case_data["response"]), language="text")
                st.warning(
                    f"**Judge Reasoning / Error:**\n\n{case_data['judge_reasoning']}"
                )

    with tab2:
        st.subheader("Performance by Model")
        chart_type = st.radio(
            "Metric to Compare",
            ["Avg Score", "Avg Latency", "Total Cost"],
            horizontal=True,
        )

        if chart_type == "Avg Score":
            if valid_score_df.empty:
                st.warning("No valid scores available to chart.")
                chart_data = pd.Series(dtype=float)
            else:
                chart_data = valid_score_df.groupby("model_type")["score"].mean()
        elif chart_type == "Avg Latency":
            chart_data = valid_dur_df.groupby("model_type")["duration_seconds"].mean()
        else:
            chart_data = df.groupby("model_type")["estimated_cost"].sum()

        if not chart_data.empty:
            st.bar_chart(chart_data)

    with tab3:
        if pii_count > 0:
            st.write("The following cases triggered PII warnings:")
            st.table(df[df["pii_found"]][["test_case_name", "model_type", "pii_types"]])
        else:
            st.success("No PII leaks detected in this run.")

    st.sidebar.markdown("---")
    st.sidebar.info("V2.1.9 - Production Ready")


def main():
    """
    Entry point for launching the Streamlit dashboard.
    If run within a Streamlit context, it calls show_dashboard().
    Otherwise, it invokes Streamlit subprocess to run itself.
    """
    try:
        _check_dashboard_dependencies()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if st.runtime.exists():
        show_dashboard()
    else:
        script_path = Path(__file__).resolve()
        try:
            subprocess.run(
                [sys.executable, "-m", "streamlit", "run", str(script_path)], check=True
            )
        except Exception as e:
            print(f"Error launching Streamlit dashboard: {e}")


if __name__ == "__main__":
    main()




























































































































































































































































































































































































































































































































































































n



a


















n














































n





































n
















































n








n




n




n




n



n


n




