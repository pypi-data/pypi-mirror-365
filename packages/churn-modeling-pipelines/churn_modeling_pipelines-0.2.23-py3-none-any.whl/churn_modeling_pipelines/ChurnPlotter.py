# =====================================================
# churn_modeling_pipelines/ChurnPlotter.py
# -----------------------------------------------------
# Visualization utility for churn model diagnostics.
# Includes confusion matrix, ROC curves, radar charts,
# and cost comparisons for base and ensemble models.
# =====================================================

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
from IPython.display import display, Markdown


class ChurnPlotter:
    """
    ChurnPlotter — Clean, Modular Visualization Utility

    Provides tools for visualizing:
    - Confusion matrices with annotations
    - ROC curves for single or multiple models
    - Radial performance charts per variant or group
    - Cost and metric comparison charts for ensembles and base models
    """

    @staticmethod
    def plot_confusion_matrix(y_true, y_pred, model_name, dataset="Test Set"):
        """
        Plots a standard confusion matrix heatmap with counts.

        Parameters:
            y_true (array-like): Ground truth labels.
            y_pred (array-like): Predicted labels from model.
            model_name (str): Model name for title annotation.
            dataset (str): Optional label for dataset (e.g., "Test Set").
        """
        cm = confusion_matrix(y_true, y_pred)
        labels = ["Not Churn", "Churn"]

        # Plot confusion matrix using seaborn heatmap
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.title(f"{model_name} – Confusion Matrix ({dataset})")
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_ensemble_confusion_matrix(model, X, y, dataset_name="Test Set"):
        """
        Plots an annotated confusion matrix for ensemble models (e.g., Voting, Bagging).

        Adds TP, FP, FN, TN tags along with percentages.

        Parameters:
            model: Trained ensemble model with .predict method.
            X (array-like): Feature data (e.g., X_test).
            y (array-like): True labels.
            dataset_name (str): Label to display on plot title.
        """
        y_pred = model.predict(X)  # Predict with ensemble model

        cm = confusion_matrix(y, y_pred)                        # Raw counts
        cm_percentage = cm / cm.sum(axis=1, keepdims=True)      # Row-wise percentage

        labels = np.array([['TN', 'FP'], ['FN', 'TP']])         # Matrix labels
        annot = np.empty_like(cm).astype(str)                   # Annotated matrix

        # Fill annotations with label, count, and percentage
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                count = cm[i, j]
                percent = cm_percentage[i, j]
                annot[i, j] = f"{labels[i, j]}\n{count}\n{percent:.1%}"

        # Plot heatmap with detailed annotations
        plt.figure(figsize=(6, 4))
        sns.heatmap(
            cm,
            annot=annot,
            fmt='',
            cmap='Blues',
            cbar=False,
            xticklabels=['Pred: No Churn', 'Pred: Churn'],
            yticklabels=['Actual: No Churn', 'Actual: Churn']
        )
        plt.title(f"Confusion Matrix – {dataset_name}")
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.tight_layout()
        plt.show()

    @staticmethod
    def show_clean_evaluation(title, df):
        """
        Display a styled evaluation summary with decimal formatting.

        Parameters:
            title (str): Section title to display.
            df (pd.DataFrame): Evaluation results DataFrame.
        """
        display(Markdown(f"## {title}"))
        display(
            df.style.format({
                "Accuracy": "{:.6f}",
                "Precision": "{:.6f}",
                "Recall": "{:.6f}",
                "F1-Score": "{:.6f}",
                "Cost ($)": "${:,.0f}"
            })
        )

    @staticmethod
    def plot_roc_curve(model, X_test, y_test, model_name):
        """
        Plot the ROC curve and AUC for a single model.

        Parameters:
            model: Trained classifier with predict_proba method.
            X_test (array-like): Test features.
            y_test (array-like): True labels.
            model_name (str): Name to annotate plot.
        """
        y_prob = model.predict_proba(X_test)[:, 1]             # Probability for class 1
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)

        # Plot ROC curve
        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.2f}')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f"{model_name} – ROC Curve")
        plt.legend(loc='lower right')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_all_roc_curves(variant_list, X_test, y_test, model_name):
        """
        Plot ROC curves for all model variants in a single figure.

        Parameters:
            variant_list (list): List of (params, model) tuples.
            X_test (array-like): Test feature data.
            y_test (array-like): True target labels.
            model_name (str): Family name to label figure.
        """
        plt.figure(figsize=(8, 6))

        # Iterate over each variant
        for idx, (params, model) in enumerate(variant_list):
            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_test)[:, 1]
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                roc_auc = auc(fpr, tpr)
                plt.plot(fpr, tpr, label=f"Variant {idx+1} (AUC = {roc_auc:.2f})")

        plt.plot([0, 1], [0, 1], 'k--', color='gray')
        plt.title(f"ROC Curves – {model_name} Variants")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.legend(loc="lower right")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_radial_chart(metrics_dict, model_name):
        """
        Plot a radar chart for a single model's performance metrics.

        Parameters:
            metrics_dict (dict): Dictionary with keys ['Accuracy', 'Precision', 'Recall', 'F1-Score'].
            model_name (str): Name of the model to display in the chart title.
        """
        # Metrics to plot and loop around
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        values = [metrics_dict[m] for m in metrics]
        values += values[:1]  # Loop back to the first for closure

        # Compute radar chart angles
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]

        # Create radar chart
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, values, marker='o')
        ax.fill(angles, values, alpha=0.3)

        ax.set_yticklabels([])  # Hide y-axis ticks
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_title(f"{model_name} – Radial Performance Chart", y=1.08)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_composite_radial_chart(evaluation_df, model_name):
        """
        Plot a composite radar chart comparing all model variants.

        Parameters:
            evaluation_df (pd.DataFrame): DataFrame with metrics per model variant.
            model_name (str): Family name to display in the chart title.
        """
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
        for i in range(len(evaluation_df)):
            row = evaluation_df.iloc[i]
            values = [row[m] for m in metrics]
            values += values[:1]
            ax.plot(angles, values, marker='o', label=f"Variant {i+1}")
            ax.fill(angles, values, alpha=0.1)

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_title(f"Radial Chart – {model_name} Variants", y=1.08)
        plt.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))
        plt.tight_layout()
        plt.show()

    def plot_ensemble_comparison(self, results_df, metric='F1 Score', top_n=5):
        """
        Compare top N ensemble models using radar and cost charts.

        Parameters:
            results_df (DataFrame): DataFrame of ensemble model results.
            metric (str): Metric used to rank top models (default: 'F1 Score').
            top_n (int): Number of top models to visualize (default: 5).
        """
        from math import pi

        # Step 1: Filter ensemble models using name patterns
        ensemble_mask = results_df['Model'].str.contains("Voting|Stacking|AdaBoost|Bagging|Boosting|CatBoost|LightGBM", case=False)
        ensemble_df = results_df[ensemble_mask].copy()

        # Step 2: Sort by selected metric
        top_ensembles = ensemble_df.sort_values(by=metric, ascending=False).head(top_n)

        # Step 3: Normalize metrics for radar chart
        radar_metrics = ['Accuracy', 'Recall', 'Precision', 'F1 Score']
        normalized = top_ensembles.copy()
        for col in radar_metrics:
            max_val = normalized[col].max()
            min_val = normalized[col].min()
            normalized[col] = (normalized[col] - min_val) / (max_val - min_val + 1e-8)

        # Step 4: Plot radar chart
        labels = radar_metrics
        angles = [n / float(len(labels)) * 2 * pi for n in range(len(labels))]
        angles += angles[:1]

        plt.figure(figsize=(10, 6))
        for i, row in normalized.iterrows():
            values = row[labels].tolist()
            values += values[:1]
            plt.polar(angles, values, label=row['Model'])
        plt.xticks(angles[:-1], labels)
        plt.title(f"Radar Chart Comparison: Top {top_n} Ensemble Models by {metric}", fontsize=12)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.tight_layout()
        plt.show()

        # Step 5: Plot cost comparison
        plt.figure(figsize=(10, 4))
        sns.barplot(data=top_ensembles, x='Model', y='Cost ($)', palette='Blues_d')
        plt.xticks(rotation=45, ha='right')
        plt.title("Cost Comparison of Top Ensemble Models")
        plt.ylabel("Cost ($)")
        plt.tight_layout()
        plt.show()

    def plot_selected_base_models(self, results_df, selected_models, metric='F1 Score'):
        """
        Compare selected base (non-ensemble) models using radar and cost charts.

        Parameters:
            results_df (DataFrame): Evaluation results containing base models.
            selected_models (list): Model names to compare.
            metric (str): Metric to normalize radar values (default: 'F1 Score').
        """
        from math import pi

        # Validation: no models passed
        if not selected_models:
            print("No model names provided.")
            return

        # Filter for selected models
        selected_df = results_df[results_df['Model'].isin(selected_models)].copy()
        if selected_df.empty:
            print("No matching base models found in the evaluation results.")
            return

        # Normalize metric values
        radar_metrics = ['Accuracy', 'Recall', 'Precision', 'F1 Score']
        normalized_df = selected_df.copy()
        for col in radar_metrics:
            min_val = normalized_df[col].min()
            max_val = normalized_df[col].max()
            normalized_df[col] = (normalized_df[col] - min_val) / (max_val - min_val + 1e-8)

        # Radar chart setup
        labels = radar_metrics
        angles = [n / float(len(labels)) * 2 * pi for n in range(len(labels))]
        angles += angles[:1]

        plt.figure(figsize=(10, 6))
        for _, row in normalized_df.iterrows():
            values = row[labels].tolist()
            values += values[:1]
            plt.polar(angles, values, label=row['Model'])
        plt.xticks(angles[:-1], labels)
        plt.title(f"Radar Comparison of Selected Base Models by {metric}", fontsize=12)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.tight_layout()
        plt.show()

        # Plot cost comparison
        plt.figure(figsize=(10, 4))
        sns.barplot(data=selected_df, x='Model', y='Cost ($)', palette='Greens_d')
        plt.xticks(rotation=45, ha='right')
        plt.title("Cost Comparison of Selected Base Models")
        plt.ylabel("Cost ($)")
        plt.tight_layout()
        plt.show()
