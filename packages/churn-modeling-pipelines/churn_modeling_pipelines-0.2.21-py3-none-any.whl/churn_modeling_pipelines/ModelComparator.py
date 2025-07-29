import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

class ModelComparator:
    """
    ModelComparator – Compare Best Variants Across Multiple Models

    Features:
    - Cost-sensitive selection
    - Composite score ranking with printed weights
    - Cleanly separated visualizations
    - Single best model identification
    - Comparison of all ensemble models or selected ones
    """

    @staticmethod
    def generate_model_summary(all_model_results):
        """
        Extract best variant from each model based on prioritized ranking:
        - Highest Recall
        - Then Lowest Cost
        - Then Highest F1-Score

        Returns:
            summary_df (DataFrame): A combined table showing the top variant per model
        """
        best_variants = []

        for df in all_model_results:
            df = df.copy()
            df_sorted = df.sort_values(by=["Recall", "Cost ($)", "F1-Score"], ascending=[False, True, False])
            best_variant = df_sorted.iloc[0]
            best_variants.append(best_variant)

        summary_df = pd.DataFrame(best_variants).reset_index(drop=True)

        # Highlight lowest-cost model
        min_cost = summary_df["Cost ($)"].min()
        summary_df["is_best_cost"] = summary_df["Cost ($)"].apply(
            lambda x: "🟩 True" if x == min_cost else "🟥 False"
        )

        return summary_df

    @staticmethod
    def identify_overall_best_model(summary_df, plot=True):
        """
        Ranks models using a composite score based on weighted metrics:
        - Accuracy, Precision, Recall, F1-Score, and Cost ($)

        Args:
            summary_df (DataFrame): Top variant per model from generate_model_summary
            plot (bool): Whether to render comparative charts

        Returns:
            df (DataFrame): Ranked table with composite scores and visual flags
        """
        df = summary_df.copy()

        weights = {
            'Accuracy': 1.0,
            'Precision': 1.0,
            'Recall': 1.5,
            'F1-Score': 1.5,
            'Cost ($)': 2.0
        }

        for metric in ['Accuracy', 'Precision', 'Recall', 'F1-Score']:
            df[f'n_{metric}'] = (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min())

        df['n_Cost ($)'] = 1 - (df['Cost ($)'] - df['Cost ($)'].min()) / (df['Cost ($)'].max() - df['Cost ($)'].min())

        df['Composite Score'] = (
            df['n_Accuracy'] * weights['Accuracy'] +
            df['n_Precision'] * weights['Precision'] +
            df['n_Recall'] * weights['Recall'] +
            df['n_F1-Score'] * weights['F1-Score'] +
            df['n_Cost ($)'] * weights['Cost ($)']
        )

        max_score = df['Composite Score'].max()
        df['is_overall_best'] = df['Composite Score'].apply(lambda x: "✅ Best" if x == max_score else "")

        df.drop(columns=[col for col in df.columns if col.startswith('n_')], inplace=True)
        df.sort_values(by="Composite Score", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)

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
        Generate a bar chart comparing performance of ensemble models.

        Parameters:
            summary_df (DataFrame): Output from generate_model_summary()

        Shows:
            - Composite score comparison (primary)
            - Cost-sensitive ranking
        """
        # Filter known ensemble models
        ensemble_keywords = [
            "Voting", "Stacking", "Bagging", "AdaBoost", "LightGBM",
            "CatBoost", "GradientBoosting", "ExtraTrees", "HistGradientBoosting", "Blending"
        ]
        ensemble_df = summary_df[summary_df["Model"].str.contains('|'.join(ensemble_keywords), case=False)]

        if ensemble_df.empty:
            print("No ensemble models found in the summary.")
            return

        # Sort for clean plotting
        df_sorted = ensemble_df.sort_values(by="Composite Score", ascending=False)

        # Plot Composite Score
        display(Markdown("## Ensemble Models: Composite Score Comparison"))
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_sorted, x='Model', y='Composite Score', hue='is_overall_best', dodge=False)
        plt.title("Ensemble Models – Composite Score Comparison", fontsize=14)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # Plot Cost Comparison
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
        Plot visual comparison charts for only the selected ensemble models.

        Parameters:
            summary_df (DataFrame): Combined evaluation summary (e.g., from generate_model_summary)
            selected_models (list): List of model names to include in the plot

        Displays:
            - Composite Score Bar Chart
            - Cost Bar Chart
        """
        df_selected = summary_df[summary_df["Model"].isin(selected_models)]

        if df_selected.empty:
            print("No matching models found in selection.")
            return

        df_sorted = df_selected.sort_values(by="Composite Score", ascending=False)

        # Composite Score Bar Chart
        display(Markdown("### Composite Score – Selected Ensemble Models"))
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_sorted, x="Model", y="Composite Score", hue="is_overall_best", dodge=False)
        plt.title("Composite Score – Selected Ensembles")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # Cost Comparison Chart
        display(Markdown("### Cost Impact – Selected Ensemble Models"))
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_sorted, x="Model", y="Cost ($)", palette="coolwarm")
        plt.title("Cost Impact – Selected Ensembles")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
