import argparse
import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

CATEGORIES = ["chat", "coding", "refactoring", "documenting"]
ALL_CATEGORIES = CATEGORIES + ["unknown"]


def plot_accuracy_table(metrics_list: list[dict], output_path: str):
    """Plot Routing Accuracy by Model & Category as a table image."""
    if not metrics_list:
        return

    df = pd.DataFrame(metrics_list)
    # Pivot to wide format: rows are Models, columns are Metrics
    pivot_df = df.pivot(index="Model", columns="Metric", values="Accuracy (%)").reset_index()
    
    # Enforce column order matching the console print
    cols = ["Model", "Overall", "Strict", "Chat", "Coding", "Refactoring", "Documenting"]
    # Only keep columns that exist (in case dataset lacked some)
    cols = [c for c in cols if c in pivot_df.columns]
    pivot_df = pivot_df[cols]

    # Format values as percentages
    for c in cols[1:]:
        pivot_df[c] = pivot_df[c].apply(lambda x: f"{x:.1f}%")

    # Create figure
    fig_width = max(8, len(cols) * 1.5)
    fig_height = max(3, len(pivot_df) * 0.5 + 1.5)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')

    table = ax.table(
        cellText=pivot_df.values,
        colLabels=cols,
        loc='center',
        cellLoc='center',
        bbox=[0, 0, 1, 1]
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    
    # Style the table
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#e0e0e0')
        cell.set_edgecolor('#cccccc')
        
    plt.title("Routing Accuracy by Model & Category", fontsize=16, pad=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved accuracy table to: {output_path}")


def plot_confusion_matrix(cm_df: pd.DataFrame, model_name: str, output_path: str):
    """Plot the confusion matrix using seaborn and save it."""
    # Ensure rows and columns are properly ordered
    cm_df = cm_df.reindex(index=CATEGORIES, columns=ALL_CATEGORIES, fill_value=0)

    plt.figure(figsize=(8, 6))
    
    # Use a custom colormap that makes zeros light and higher numbers darker
    ax = sns.heatmap(
        cm_df,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        linewidths=1,
        linecolor="white",
        annot_kws={"size": 14}
    )

    ax.set_title(model_name, fontsize=16, pad=20, fontweight='bold')
    ax.set_xlabel("Routed Category", fontsize=12, labelpad=10)
    ax.set_ylabel("Expected Category", fontsize=12, labelpad=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved visualization to: {output_path}")


def process_json(filepath: Path):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    models = data.get("models", {})
    if not models:
        print("No models found in JSON file.", file=sys.stderr)
        return

    accuracy_metrics = []

    for model_name, metrics in models.items():
        # 1. Confusion Matrix Plot
        cm_dict = metrics.get("confusion_matrix", {})
        cm_df = pd.DataFrame(cm_dict).T
        safe_model_name = model_name.replace("/", "_").replace(":", "_")
        output_path = filepath.parent / f"{filepath.stem}_{safe_model_name}.png"
        plot_confusion_matrix(cm_df, model_name, str(output_path))
        
        # 2. Collect Accuracy Metrics
        summary = metrics.get("summary", {})
        accuracy_metrics.append({"Model": model_name, "Metric": "Overall", "Accuracy (%)": summary.get("accuracy", 0) * 100})
        accuracy_metrics.append({"Model": model_name, "Metric": "Strict", "Accuracy (%)": summary.get("strict_accuracy", 0) * 100})
        
        cat_acc = metrics.get("category_accuracy", {})
        for cat in CATEGORIES:
            acc = cat_acc.get(cat, {}).get("accuracy", 0) * 100
            accuracy_metrics.append({"Model": model_name, "Metric": cat.capitalize(), "Accuracy (%)": acc})

    if accuracy_metrics:
        acc_output_path = filepath.parent / f"{filepath.stem}_accuracy.png"
        plot_accuracy_table(accuracy_metrics, str(acc_output_path))


def process_csv(filepath: Path):
    df = pd.read_csv(filepath)
    if "model" not in df.columns:
        print("CSV file missing 'model' column.", file=sys.stderr)
        return

    accuracy_metrics = []
    models = df["model"].unique()
    
    for model_name in models:
        model_df = df[df["model"] == model_name]
        
        # Compute confusion matrix
        cm_df = pd.crosstab(model_df["expected_category"], model_df["routed_category"])
        safe_model_name = model_name.replace("/", "_").replace(":", "_")
        output_path = filepath.parent / f"{filepath.stem}_{safe_model_name}.png"
        plot_confusion_matrix(cm_df, model_name, str(output_path))
        
        # Compute Accuracy
        overall_acc = (model_df["correct"] == True).mean() * 100
        strict_df = model_df[model_df["is_ambiguous"] == False]
        strict_acc = (strict_df["correct"] == True).mean() * 100 if len(strict_df) else 0.0
        
        accuracy_metrics.append({"Model": model_name, "Metric": "Overall", "Accuracy (%)": overall_acc})
        accuracy_metrics.append({"Model": model_name, "Metric": "Strict", "Accuracy (%)": strict_acc})
        
        for cat in CATEGORIES:
            cat_df = model_df[model_df["expected_category"] == cat]
            cat_acc = (cat_df["correct"] == True).mean() * 100 if len(cat_df) else 0.0
            accuracy_metrics.append({"Model": model_name, "Metric": cat.capitalize(), "Accuracy (%)": cat_acc})

    if accuracy_metrics:
        acc_output_path = filepath.parent / f"{filepath.stem}_accuracy.png"
        plot_accuracy_table(accuracy_metrics, str(acc_output_path))


def main():
    parser = argparse.ArgumentParser(
        description="Visualize benchmark confusion matrices from JSON or CSV results."
    )
    parser.add_argument(
        "results_file",
        type=str,
        help="Path to the JSON or CSV results file (e.g. results/..._results.json)"
    )

    args = parser.parse_args()
    filepath = Path(args.results_file)

    if not filepath.exists():
        print(f"Error: File '{filepath}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {filepath}...")
    if filepath.suffix.lower() == ".json":
        process_json(filepath)
    elif filepath.suffix.lower() == ".csv":
        process_csv(filepath)
    else:
        print(f"Error: Unsupported file extension '{filepath.suffix}'. Please provide a .json or .csv file.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
