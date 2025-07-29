import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc

class ChurnPlotter:
    """
    ChurnPlotter – Clean, Modular Visualization Utility

    Generates:
    - Confusion Matrix with annotations
    - ROC Curve for a single model
    - ROC Curve for all model variants
    - Radial Chart of performance metrics per model
    - Composite Radial Chart of all model variants
    """

    @staticmethod
    def plot_confusion_matrix(y_true, y_pred, model_name, dataset="Test Set"):
        cm = confusion_matrix(y_true, y_pred)
        labels = ["Not Churn", "Churn"]
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
        Plot a confusion matrix specifically for ensemble models (e.g., VotingClassifier, BaggingClassifier).
        Annotates each cell with the label (e.g., TP), count, and percentage.

        Parameters:
            model: Trained ensemble model (e.g., VotingClassifier or any model with .predict method)
            X (array-like): Feature data (e.g., X_test or X_train)
            y (array-like): True labels corresponding to X
            dataset_name (str): Descriptive label for the dataset (e.g., "Test Set", "Train Set")
        """
        # Predict labels using the ensemble model
        y_pred = model.predict(X)

        # Compute raw and percentage confusion matrix
        cm = confusion_matrix(y, y_pred)
        cm_percentage = cm / cm.sum(axis=1, keepdims=True)

        # Define annotation labels
        labels = np.array([['TN', 'FP'], ['FN', 'TP']])
        annot = np.empty_like(cm).astype(str)

        # Combine label, count, and percentage for each cell
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                count = cm[i, j]
                percent = cm_percentage[i, j]
                annot[i, j] = f"{labels[i, j]}\n{count}\n{percent:.1%}"

        # Create heatmap
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
        Display a clean, formatted model evaluation table using pandas styling.

        Parameters:
        - title (str): Section heading to display above the table.
        - df (pd.DataFrame): Evaluation summary DataFrame.
        """
        from IPython.display import display, Markdown

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
        y_prob = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)

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
        plt.figure(figsize=(8, 6))
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
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        values = [metrics_dict[m] for m in metrics]
        values += values[:1]

        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, values, marker='o')
        ax.fill(angles, values, alpha=0.3)

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_title(f"{model_name} – Radial Performance Chart", y=1.08)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_composite_radial_chart(evaluation_df, model_name):
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
        Visual comparison of ensemble models only, using radar chart and ROC curves.

        Parameters:
            results_df (pd.DataFrame): Evaluation DataFrame with model metrics.
            metric (str): Primary metric to sort and display (default: 'F1 Score').
            top_n (int): Number of top ensemble models to visualize.

        Notes:
            - Requires results_df to have a 'Model' column.
            - Assumes metrics: Accuracy, Recall, Precision, F1 Score, Cost ($)
        """
        import matplotlib.pyplot as plt
        import numpy as np
        import seaborn as sns
        from math import pi

        # Step 1: Filter ensemble models only
        ensemble_mask = results_df['Model'].str.contains("Voting|Stacking|AdaBoost|Bagging|Boosting|CatBoost|LightGBM", case=False)
        ensemble_df = results_df[ensemble_mask].copy()

        # Step 2: Sort by metric and select top_n
        top_ensembles = ensemble_df.sort_values(by=metric, ascending=False).head(top_n)

        # Step 3: Radar Chart — Normalize metrics between 0–1
        radar_metrics = ['Accuracy', 'Recall', 'Precision', 'F1 Score']
        normalized = top_ensembles.copy()
        for col in radar_metrics:
            max_val = normalized[col].max()
            min_val = normalized[col].min()
            normalized[col] = (normalized[col] - min_val) / (max_val - min_val + 1e-8)

        # Step 4: Plot Radar Chart
        labels = radar_metrics
        num_vars = len(labels)
        angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
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

        # Step 5: Cost Comparison Bar Plot
        plt.figure(figsize=(10, 4))
        sns.barplot(data=top_ensembles, x='Model', y='Cost ($)', palette='Blues_d')
        plt.xticks(rotation=45, ha='right')
        plt.title("Cost Comparison of Top Ensemble Models")
        plt.ylabel("Cost ($)")
        plt.tight_layout()
        plt.show()

    def plot_selected_base_models(self, results_df, selected_models, metric='F1 Score'):
        """
        Plot radar and cost charts to compare selected base (non-ensemble) models.

        Parameters:
        ----------
        results_df : pd.DataFrame
            Evaluation results containing performance metrics for all models.
        selected_models : list
            List of base model names (e.g., 'KNN_K3', 'Logistic_L2') to include in the comparison.
        metric : str
            Primary metric for radar chart normalization (default: 'F1 Score').

        Notes:
        ------
        Assumes results_df includes the following columns:
        ['Model', 'Accuracy', 'Recall', 'Precision', 'F1 Score', 'Cost ($)']
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        from math import pi

        # Validation
        if not selected_models:
            print("No model names provided.")
            return

        # Filter selected models
        selected_df = results_df[results_df['Model'].isin(selected_models)].copy()
        if selected_df.empty:
            print("No matching base models found in the evaluation results.")
            return

        # Normalize performance metrics for radar chart
        radar_metrics = ['Accuracy', 'Recall', 'Precision', 'F1 Score']
        normalized_df = selected_df.copy()
        for col in radar_metrics:
            min_val = normalized_df[col].min()
            max_val = normalized_df[col].max()
            normalized_df[col] = (normalized_df[col] - min_val) / (max_val - min_val + 1e-8)

        # Radar chart setup
        labels = radar_metrics
        angles = [n / float(len(labels)) * 2 * pi for n in range(len(labels))]
        angles += angles[:1]  # complete loop

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

        # Bar chart: cost comparison
        plt.figure(figsize=(10, 4))
        sns.barplot(data=selected_df, x='Model', y='Cost ($)', palette='Greens_d')
        plt.xticks(rotation=45, ha='right')
        plt.title("Cost Comparison of Selected Base Models")
        plt.ylabel("Cost ($)")
        plt.tight_layout()
        plt.show()
