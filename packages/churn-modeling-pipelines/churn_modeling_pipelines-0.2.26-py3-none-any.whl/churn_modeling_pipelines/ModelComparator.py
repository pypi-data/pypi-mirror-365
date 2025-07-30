import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

class ModelComparator:
    """
    ModelComparator – Compare Best Variants Across Multiple Models

    This class helps identify, compare, and visualize the best-performing model variants
    across different machine learning models based on prioritized evaluation metrics.

    Features:
    ---------
    - Cost-sensitive model selection
    - Composite score ranking using custom metric weights
    - Identification of overall best model
    - Comparative visualizations for base and ensemble models
    """

    @staticmethod
    def generate_model_summary(all_model_results):
        """
        Selects the best variant from each model result table using a prioritized rule:
        1. Highest Recall
        2. Then Lowest Cost
        3. Then Highest F1-Score

        Parameters:
        -----------
        all_model_results : list of pd.DataFrame
            A list where each element is a DataFrame of model variants with evaluation metrics.

        Returns:
        --------
        summary_df : pd.DataFrame
            DataFrame showing the best variant from each model with a cost flag column.
        """
        best_variants = []

        for df in all_model_results:
            df = df.copy()

            # Sort by prioritized rule: Recall → Cost ($) → F1-Score
            df_sorted = df.sort_values(by=["Recall", "Cost ($)", "F1-Score"], ascending=[False, True, False])

            # Select the best performing variant
            best_variant = df_sorted.iloc[0]
            best_variants.append(best_variant)

        # Combine top variants into a single DataFrame
        summary_df = pd.DataFrame(best_variants).reset_index(drop=True)

        # Highlight the model with the lowest cost
        min_cost = summary_df["Cost ($)"].min()
        summary_df["is_best_cost"] = summary_df["Cost ($)"].apply(
            lambda x: "🟩 True" if x == min_cost else "🟥 False"
        )

        return summary_df

    @staticmethod
    def identify_overall_best_model(summary_df, plot=True):
        """
        Identifies the overall best model using a composite score with metric weights.

        Composite Score = Weighted sum of normalized values of:
        - Accuracy, Precision, Recall, F1-Score (higher is better)
        - Cost ($) (lower is better)

        Parameters:
        -----------
        summary_df : pd.DataFrame
            Output from generate_model_summary – each row is a top variant per model.

        plot : bool, optional (default=True)
            Whether to display visual charts for comparison.

        Returns:
        --------
        df : pd.DataFrame
            Ranked summary with composite scores and best model flags.
        """
        df = summary_df.copy()

        # Define metric weights (Cost has the highest influence)
        weights = {
            'Accuracy': 1.0,
            'Precision': 1.0,
            'Recall': 1.5,
            'F1-Score': 1.5,
            'Cost ($)': 2.0
        }

        # Normalize performance metrics: higher is better
        for metric in ['Accuracy', 'Precision', 'Recall', 'F1-Score']:
            df[f'n_{metric}'] = (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min())

        # Normalize Cost: lower is better → invert score
        df['n_Cost ($)'] = 1 - (df['Cost ($)'] - df['Cost ($)'].min()) / (df['Cost ($)'].max() - df['Cost ($)'].min())

        # Compute weighted composite score
        df['Composite Score'] = (
            df['n_Accuracy'] * weights['Accuracy'] +
            df['n_Precision'] * weights['Precision'] +
            df['n_Recall'] * weights['Recall'] +
            df['n_F1-Score'] * weights['F1-Score'] +
            df['n_Cost ($)'] * weights['Cost ($)']
        )

        # Identify the best overall model
        max_score = df['Composite Score'].max()
        df['is_overall_best'] = df['Composite Score'].apply(lambda x: "✅ Best" if x == max_score else "")

        # Drop intermediate normalization columns
        df.drop(columns=[col for col in df.columns if col.startswith('n_')], inplace=True)

        # Sort by composite score in descending order
        df.sort_values(by="Composite Score", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Display comparative charts if requested
        if plot:
            display(Markdown("## Composite Score by Model"))
            plt.figure(figsize=(10, 5))
            sns.barplot(data=df, x='Model', y='Composite Score', hue='is_overall_best', dodge=False)
            plt.title("Composite Score per Model")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

            display(Markdown("<hr style='border-top: 3px double #bbb;'>"))

            display(Markdown("## Accuracy vs Cost ($)"))
            plt.figure(figsize=(10, 6))
            sns.scatterplot(
                data=df,
                x='Cost ($)',
                y='Accuracy',
                hue='Model',
                style='is_overall_best',
                s=150
            )
            plt.title("Accuracy vs Cost for Best Variants")
            plt.tight_layout()
            plt.show()

        return df

    @staticmethod
    def plot_ensemble_model_comparison(summary_df):
        """
        Visual comparison of ensemble model performance using Composite Score and Cost.

        Parameters:
        -----------
        summary_df : pd.DataFrame
            Output from generate_model_summary containing the best variant from all models.

        Charts Displayed:
        -----------------
        - Composite Score Bar Chart for Ensemble Models
        - Cost Impact Chart for Ensemble Models
        """
        # Filter ensemble models using common keywords
        ensemble_keywords = [
            "Voting", "Stacking", "Bagging", "AdaBoost", "LightGBM",
            "CatBoost", "GradientBoosting", "ExtraTrees", "HistGradientBoosting", "Blending"
        ]
        ensemble_df = summary_df[summary_df["Model"].str.contains('|'.join(ensemble_keywords), case=False)]

        if ensemble_df.empty:
            print("No ensemble models found in the summary.")
            return

        df_sorted = ensemble_df.sort_values(by="Composite Score", ascending=False)

        # Composite Score Chart
        display(Markdown("## Ensemble Models: Composite Score Comparison"))
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_sorted, x='Model', y='Composite Score', hue='is_overall_best', dodge=False)
        plt.title("Ensemble Models – Composite Score Comparison", fontsize=14)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # Cost Comparison Chart
        display(Markdown("## Cost Comparison Among Ensembles"))
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_sorted, x='Model', y='Cost ($)', palette='coolwarm')
        plt.title("Ensemble Models – Cost Impact", fontsize=14)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_selected_ensemble_comparison(summary_df, selected_models):
        """
        Display comparative charts for a manually selected list of ensemble models.

        Parameters:
        -----------
        summary_df : pd.DataFrame
            Output from generate_model_summary

        selected_models : list of str
            List of specific model names to include in the comparison.

        Charts Displayed:
        -----------------
        - Composite Score Bar Chart
        - Cost Impact Bar Chart
        """
        df_selected = summary_df[summary_df["Model"].isin(selected_models)]

        if df_selected.empty:
            print("No matching models found in selection.")
            return

        df_sorted = df_selected.sort_values(by="Composite Score", ascending=False)

        # Composite Score Chart
        display(Markdown("### Composite Score – Selected Ensemble Models"))
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_sorted, x="Model", y="Composite Score", hue="is_overall_best", dodge=False)
        plt.title("Composite Score – Selected Ensembles")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # Cost Impact Chart
        display(Markdown("### Cost Impact – Selected Ensemble Models"))
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_sorted, x="Model", y="Cost ($)", palette="coolwarm")
        plt.title("Cost Impact – Selected Ensembles")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
