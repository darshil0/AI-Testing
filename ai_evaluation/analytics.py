import json
from pathlib import Path

# Optional analytics imports guarded at import time
try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    ANALYTICS_AVAILABLE = True
except ImportError:
    plt = None  # type: ignore
    pd = None  # type: ignore
    sns = None  # type: ignore
    ANALYTICS_AVAILABLE = False


def _check_analytics_dependencies():
    if not ANALYTICS_AVAILABLE:
        raise RuntimeError(
            "Analytics dependencies (matplotlib, seaborn, pandas, numpy) are not installed.\n"
            "Install with: pip install 'ai-evaluation-framework[dashboard]' or pip install -e '.[dev,dashboard]'"
        )


def generate_analytics(results_path=None, config_path=None) -> None:
    _check_analytics_dependencies()

    if results_path is None:
        try:
            from .run_evaluation import resolve_config_path, safe_yaml_load

            resolved_config_path = resolve_config_path(config_path)
            with resolved_config_path.open("r", encoding="utf-8") as f:
                config = safe_yaml_load(f) or {}
                results_dir_name = (
                    config.get("directories", {}).get("results", "results")
                    if isinstance(config, dict)
                    else "results"
                )
        except Exception as e:
            resolved_config_path = Path(__file__).parent / "config.yaml"
            results_dir_name = "results"
            print(f"Warning: Could not read config file: {e}")

        results_dir = Path(results_dir_name)
        if not results_dir.is_absolute():
            results_dir = resolved_config_path.parent / results_dir
        results_file = results_dir / "latest_results.json"
    else:
        results_file = Path(results_path)

    if not results_file.exists():
        print(
            f"Error: {results_file} not found. Ensure you have run an evaluation first."
        )
        return

    with results_file.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {results_file} contains invalid JSON.")
            return

    df = pd.DataFrame(data)
    if df.empty:
        print("No data to analyze.")
        return

    # Standardize legacy/current column aliases
    if "cost" in df.columns and "estimated_cost" not in df.columns:
        df["estimated_cost"] = df["cost"]
    elif "estimated_cost" in df.columns and "cost" not in df.columns:
        df["cost"] = df["estimated_cost"]

    if "score" in df.columns and "judge_score" not in df.columns:
        df["judge_score"] = df["score"]
    elif "judge_score" in df.columns and "score" not in df.columns:
        df["score"] = df["judge_score"]

    # Supply default values for optional/missing columns
    defaults = {
        "model_type": "Unknown",
        "category": "General",
        "status": "success",
        "duration_seconds": None,
        "estimated_cost": 0.0,
        "score": None,
        "judge_score": None,
    }
    for col, default_val in defaults.items():
        if col not in df.columns:
            df[col] = default_val

    # Coerce numeric columns safely
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df.loc[df["score"] < 0, "score"] = None

    df["judge_score"] = pd.to_numeric(df["judge_score"], errors="coerce")
    df.loc[df["judge_score"] < 0, "judge_score"] = None

    df["duration_seconds"] = pd.to_numeric(df["duration_seconds"], errors="coerce")
    df["estimated_cost"] = pd.to_numeric(df["estimated_cost"], errors="coerce").fillna(0.0)

    required_columns = {
        "model_type",
        "judge_score",
        "duration_seconds",
        "category",
        "estimated_cost",
    }

    missing = required_columns - set(df.columns)
    if missing:
        print(f"Missing required columns in results: {', '.join(sorted(missing))}")
        return

    # Visual Setup
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # Define a consistent color mapping for models to keep colors the same across plots
    unique_models = df["model_type"].unique()
    palette = sns.color_palette("viridis", n_colors=len(unique_models))
    model_color_map = dict(zip(unique_models, palette))

    valid_score_df = df[df["status"].isin(["success"]) & df["score"].notna()]
    valid_dur_df = df[df["duration_seconds"].notna()]

    # 1. Average score by model
    if not valid_score_df.empty:
        model_scores = (
            valid_score_df.groupby("model_type")["score"].mean().reset_index()
        )
        sns.barplot(
            x="model_type",
            y="score",
            data=model_scores,
            ax=axes[0, 0],
            hue="model_type",
            palette=model_color_map,
            legend=False,
        )
        axes[0, 0].set_title(
            "Average Judge Score by Model (Valid Successes Only)", fontweight="bold"
        )
        axes[0, 0].set_ylim(0, 1.1)
        axes[0, 0].set_ylabel("Average Score (0.0 - 1.0)")
    else:
        axes[0, 0].text(0.5, 0.5, "No Valid Scores Available", ha="center", va="center")
        axes[0, 0].set_title("Average Judge Score by Model", fontweight="bold")

    # 2. Latency vs score
    if not valid_score_df.empty and not valid_dur_df.empty:
        plot_df = valid_score_df[valid_score_df["duration_seconds"].notna()]
        if not plot_df.empty:
            sns.scatterplot(
                x="duration_seconds",
                y="score",
                hue="model_type",
                style="model_type",
                data=plot_df,
                ax=axes[0, 1],
                s=150,
                palette=model_color_map,
            )
        axes[0, 1].set_title("Latency vs. Judge Score", fontweight="bold")
        axes[0, 1].set_xlabel("Duration (seconds)")
        axes[0, 1].set_ylabel("Score (0.0 - 1.0)")
    else:
        axes[0, 1].text(0.5, 0.5, "No Latency vs Score Data", ha="center", va="center")
        axes[0, 1].set_title("Latency vs. Judge Score", fontweight="bold")

    # 3. Category performance
    if not valid_score_df.empty:
        sns.boxplot(
            x="category",
            y="score",
            data=valid_score_df,
            ax=axes[1, 0],
            hue="category",
            palette="Set2",
            legend=False,
        )
        axes[1, 0].set_title("Performance Distribution by Category", fontweight="bold")
        axes[1, 0].tick_params(axis="x", rotation=30)
    else:
        axes[1, 0].text(0.5, 0.5, "No Valid Category Scores", ha="center", va="center")
        axes[1, 0].set_title("Performance Distribution by Category", fontweight="bold")

    # 4. Total cost by model
    cost_df = df.groupby("model_type")["estimated_cost"].sum().reset_index()
    sns.barplot(
        x="model_type",
        y="estimated_cost",
        data=cost_df,
        ax=axes[1, 1],
        hue="model_type",
        palette=model_color_map,
        legend=False,
    )
    axes[1, 1].set_title("Total Cumulative Cost ($)", fontweight="bold")
    axes[1, 1].set_ylabel("USD ($)")

    plt.tight_layout()

    # Save Output
    output_path = results_file.parent / "benchmark_report.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)  # Higher DPI for "publication-ready" charts
    plt.close(fig)
    print(f"✅ Analytics report saved to: {output_path}")


if __name__ == "__main__":
    generate_analytics()
