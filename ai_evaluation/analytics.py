import json
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def generate_analytics(results_path=None) -> None:
    # Resolve paths relative to the project root
    base_dir = Path(__file__).parent.parent if "__file__" in locals() else Path.cwd()
    
    if results_path is None:
        results_file = base_dir / "ai_evaluation" / "results" / "latest_results.json"
    else:
        results_file = Path(results_path)

    if not results_file.exists():
        print(f"Error: {results_file} not found. Ensure you have run an evaluation first.")
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

    # 1. Average score by model
    model_scores = df.groupby("model_type")["judge_score"].mean().reset_index()
    sns.barplot(
        x="model_type",
        y="judge_score",
        data=model_scores,
        ax=axes[0, 0],
        hue="model_type",  # Added hue to avoid future warnings
        palette=model_color_map,
        legend=False
    )
    axes[0, 0].set_title("Average Judge Score by Model", fontweight='bold')
    axes[0, 0].set_ylim(0, 1.1)
    axes[0, 0].set_ylabel("Average Score (0.0 - 1.0)")

    # 2. Latency vs score
    sns.scatterplot(
        x="duration_seconds",
        y="judge_score",
        hue="model_type",
        style="model_type",
        data=df,
        ax=axes[0, 1],
        s=150,
        palette=model_color_map
    )
    axes[0, 1].set_title("Latency vs. Judge Score", fontweight='bold')
    axes[0, 1].set_xlabel("Duration (seconds)")

    # 3. Category performance
    sns.boxplot(
        x="category",
        y="judge_score",
        data=df,
        ax=axes[1, 0],
        palette="Set2"
    )
    axes[1, 0].set_title("Performance Distribution by Category", fontweight='bold')
    axes[1, 0].tick_params(axis="x", rotation=30)

    # 4. Total cost by model
    cost_df = df.groupby("model_type")["estimated_cost"].sum().reset_index()
    sns.barplot(
        x="model_type",
        y="estimated_cost",
        data=cost_df,
        ax=axes[1, 1],
        hue="model_type",
        palette=model_color_map,
        legend=False
    )
    axes[1, 1].set_title("Total Cumulative Cost ($)", fontweight='bold')
    axes[1, 1].set_ylabel("USD ($)")

    plt.tight_layout()
    
    # Save Output
    output_path = results_file.parent / "benchmark_report.png"
    plt.savefig(output_path, dpi=300) # Higher DPI for "publication-ready" charts
    plt.close(fig)
    print(f"✅ Analytics report saved to: {output_path}")

if __name__ == "__main__":
    generate_analytics()
