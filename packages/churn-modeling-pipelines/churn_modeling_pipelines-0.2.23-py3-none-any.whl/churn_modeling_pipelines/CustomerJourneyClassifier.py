# ==========================================================
# churn_modeling_pipelines/CustomerJourneyClassifier.py
# ----------------------------------------------------------
# Classifies customers into journey stages and visualizes
# churn risk across those stages using tenure and contact binning.
# ==========================================================

import pandas as pd

class CustomerJourneyClassifier:
    """
    CustomerJourneyClassifier — Labels customer journey stages
    based on 'Tenurebin' and 'Cccontactedlybin' columns.

    Features:
    ----------
    - Assigns customers to one of five journey stages:
      ['Awareness', 'Consideration', 'Acquisition', 'Engagement', 'Loyalty']
    - Adds a 'JourneyStage' column to the DataFrame.
    - Computes churn rate by journey stage.
    - Visualizes churn risk across stages with a line plot.
    """

    @staticmethod
    def assign_journey_stage(df):
        """
        Classify each customer into a journey stage.

        Uses 'Tenurebin' (e.g., New, Recent, Established, Loyal)
        and 'Cccontactedlybin' (e.g., Rare, Occasional, Frequent) to assign a label.

        Parameters:
            df (pd.DataFrame): Input DataFrame containing Tenurebin and Cccontactedlybin.

        Returns:
            pd.DataFrame: DataFrame with a new 'JourneyStage' column.
        """

        def classify(row):
            # Define journey stage rules
            if row['Tenurebin'] == 'New' and row['Cccontactedlybin'] == 'Rare':
                return 'Awareness'
            elif row['Tenurebin'] == 'New' and row['Cccontactedlybin'] == 'Occasional':
                return 'Consideration'
            elif row['Tenurebin'] == 'New' and row['Cccontactedlybin'] == 'Frequent':
                return 'Acquisition'
            elif row['Tenurebin'] in ['Recent', 'Established']:
                return 'Engagement'
            elif row['Tenurebin'] == 'Loyal':
                return 'Loyalty'
            else:
                return 'Other'

        # Apply classification row-wise
        df['JourneyStage'] = df.apply(classify, axis=1)
        return df

    @staticmethod
    def compute_churn_by_stage(df):
        """
        Compute churn rate (as %) for each customer journey stage.

        Parameters:
            df (pd.DataFrame): DataFrame that includes 'JourneyStage' and 'Churn'.

        Returns:
            pd.Series: Churn rate by stage, sorted alphabetically by stage.
        """
        return (
            df[df['JourneyStage'] != 'Other']                      # Exclude undefined classifications
            .groupby('JourneyStage')['Churn']                      # Group by stage
            .mean()                                                # Average churn
            .multiply(100)                                         # Convert to %
            .round(2)                                              # Round to 2 decimals
            .sort_index()                                          # Sort alphabetically by stage
        )

    @staticmethod
    def plot_churn_journey(churn_rate_by_stage):
        """
        Plot churn rate by customer journey stage.

        Parameters:
            churn_rate_by_stage (pd.Series): Output from compute_churn_by_stage()

        Visual:
            Line chart with annotated churn percentages.
        """
        import matplotlib.pyplot as plt

        # Extract index and values
        stages = churn_rate_by_stage.index.tolist()
        rates = churn_rate_by_stage.values

        # Create plot
        plt.figure(figsize=(10, 6))
        plt.plot(stages, rates, marker='o', linewidth=2, color='royalblue')

        # Add labels and formatting
        plt.title("Customer Churn Risk Across the Journey (Derived from Customer_churn_dataset)", fontsize=14)
        plt.xlabel("Customer Journey Stage", fontsize=12)
        plt.ylabel("Churn Risk (%)", fontsize=12)
        plt.ylim(0, max(rates) + 10)
        plt.grid(True)

        # Annotate each point
        for i, value in enumerate(rates):
            plt.text(i, value + 1, f"{value:.2f}%", ha='center', fontsize=10)

        plt.tight_layout()
        plt.show()
