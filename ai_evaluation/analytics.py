import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def generate_analytics(results_path="ai_evaluation/results/latest_results.json") -> None:
    results_file = Path(results_path)
    if not results_file.exists():
        print(f"Error: {results_file} not found.")
        return

    with results_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

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

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # 1. Average score by model
    model_scores = df.groupby("model_type")["judge_score"].mean().reset_index()
    sns.barplot(
        x="model_type",
        y="judge_score",
        data=model_scores,
        ax=axes[0, 0],
        palette="viridis",
    )
    axes[0, 0].set_title("Average Judge Score by Model")
    axes[0, 0].set_ylim(0, 1.1)
    axes[0, 0].set_xlabel("Model")
    axes[0, 0].set_ylabel("Average judge score")

    # 2. Latency vs score
    sns.scatterplot(
        x="duration_seconds",
        y="judge_score",
        hue="model_type",
        data=df,
        ax=axes[0, 1],
        s=100,
    )
    axes[0, 1].set_title("Latency vs. Judge Score")
    axes[0, 1].set_xlabel("Duration (seconds)")
    axes[0, 1].set_ylabel("Judge score")

    # 3. Category performance
    sns.boxplot(
        x="category",
        y="judge_score",
        data=df,
        ax=axes[1, 0],
        palette="Set2",
    )
    axes[1, 0].set_title("Performance by Category")
    axes[1, 0].tick_params(axis="x", rotation=45)
    axes[1, 0].set_xlabel("Category")
    axes[1, 0].set_ylabel("Judge score")

    # 4. Total cost by model
    cost_df = df.groupby("model_type")["estimated_cost"].sum().reset_index()
    sns.barplot(
        x="model_type",
        y="estimated_cost",
        data=cost_df,
        ax=axes[1, 1],
        palette="magma",
    )
    axes[1, 1].set_title("Total Estimated Cost ($)")
    axes[1, 1].set_xlabel("Model")
    axes[1, 1].set_ylabel("Total estimated cost ($)")

    plt.tight_layout()
    output_path = Path("ai_evaluation/results/benchmark_report.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close(fig)
    print(f"✅ Analytics report saved to: {output_path}")


if __name__ == "__main__":
    generate_analytics()
