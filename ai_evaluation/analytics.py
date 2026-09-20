import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def generate_analytics(results_path=None, config_path=None) -> None:
    base_dir = Path(__file__).parent.parent

    if results_path is None:
        c_path = (
            Path(config_path)
            if config_path
            else base_dir / "ai_evaluation" / "config.yaml"
        )
        if not c_path.exists():
            c_path = Path(__file__).parent / "config.yaml"

        results_dir_name = "results"
        if c_path.exists():
            try:
                from .run_evaluation import safe_yaml_load

                with c_path.open("r", encoding="utf-8") as f:
                    config = safe_yaml_load(f)
                    results_dir_name = config.get("directories", {}).get(
                        "results", "results"
                    )
            except Exception as e:
                print(f"Warning: Could not read config file {c_path}: {e}")

        results_dir = Path(results_dir_name)
        if not results_dir.is_absolute():
            results_dir = c_path.parent / results_dir
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

    # Standardize score column if missing
    if "score" not in df.columns:
        if "judge_score" in df.columns:
            df["score"] = pd.to_numeric(df["judge_score"], errors="coerce")
            df.loc[df["score"] < 0, "score"] = None
        else:
            df["score"] = None

    if "status" not in df.columns:
        df["status"] = "success"

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
