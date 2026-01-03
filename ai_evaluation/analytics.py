import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def generate_analytics(results_path="ai_evaluation/results/latest_results.json"):
    if not Path(results_path).exists():
        print(f"Error: {results_path} not found.")
        return

    with open(results_path, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    if df.empty:
        print("No data to analyze.")
        return

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # 1. Score by Model
    sns.barplot(
        x="model_type", y="judge_score", data=df, ax=axes[0, 0], palette="viridis"
    )
    axes[0, 0].set_title("Average Judge Score by Model")
    axes[0, 0].set_ylim(0, 1.1)

    # 2. Latency vs Score
    sns.scatterplot(
        x="duration_seconds",
        y="judge_score",
        hue="model_type",
        data=df,
        ax=axes[0, 1],
        s=100,
    )
    axes[0, 1].set_title("Latency vs. Judge Score")

    # 3. Category Performance
    sns.boxplot(x="category", y="judge_score", data=df, ax=axes[1, 0], palette="Set2")
    axes[1, 0].set_title("Performance by Category")
    axes[1, 0].tick_params(axis="x", rotation=45)

    # 4. Total Cost
    cost_df = df.groupby("model_type")["estimated_cost"].sum().reset_index()
    sns.barplot(
        x="model_type", y="estimated_cost", data=cost_df, ax=axes[1, 1], palette="magma"
    )
    axes[1, 1].set_title("Total Estimated Cost ($)")

    plt.tight_layout()
    output_path = "ai_evaluation/results/benchmark_report.png"
    plt.savefig(output_path)
    print(f"✅ Analytics report saved to: {output_path}")


if __name__ == "__main__":
    generate_analytics()
