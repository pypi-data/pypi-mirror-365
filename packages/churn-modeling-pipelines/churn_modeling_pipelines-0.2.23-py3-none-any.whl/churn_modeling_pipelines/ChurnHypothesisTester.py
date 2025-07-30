import pandas as pd
from scipy import stats


class ChurnHypothesisTester:
    """
    ChurnHypothesisTester — Performs statistical tests to explore hypotheses related to churn.

    This class applies Chi-square tests on categorical groupings to identify significant
    relationships between customer features and churn behavior.

    Parameters:
        df (pd.DataFrame): The dataset containing churn-related fields.

    Methods:
        test_churn_hypotheses_stats(): Returns a DataFrame with p-values and decisions
        for key churn hypotheses.
    """

    def __init__(self, df):
        """
        Initialize the tester with a copy of the input DataFrame.

        Args:
            df (pd.DataFrame): Preprocessed dataset with required columns.
        """
        self.df = df.copy()  # Work on a safe copy to avoid modifying the original DataFrame

    def test_churn_hypotheses_stats(self):
        """
        Conducts statistical hypothesis tests related to churn behavior.

        Hypotheses tested:
        H₁: Customers with more than 3 users have different churn behavior.
        H₂: Customers who frequently contact support show churn differences.
        H₃: Churn behavior varies by payment method.
        H₄: Revenue growth influences churn rate.
        H₅: Loyalty (tenure) and satisfaction (service score) jointly impact churn.

        Returns:
            pd.DataFrame: Table of hypotheses, p-values (scientific notation), and decisions.
        """
        results = []  # Store tuples of (hypothesis, p-value, decision)

        # -----------------------------------------------
        # H₁: Account User Count – Grouped into ≤3 vs >3
        # -----------------------------------------------
        self.df['UserCountGroup'] = self.df['AccountUserCount'].apply(
            lambda x: '>3 Users' if x > 3 else '≤3 Users'
        )
        ct1 = pd.crosstab(self.df['UserCountGroup'], self.df['Churn'])
        _, p1, _, _ = stats.chi2_contingency(ct1)
        results.append(['H₁: Account User Count', p1, self._decision(p1)])

        # -----------------------------------------------
        # H₂: Support Contact Frequency
        # (e.g. Contacted customer care last year: Yes/No bin)
        # -----------------------------------------------
        ct2 = pd.crosstab(self.df['CcContactedLYBin'], self.df['Churn'])
        _, p2, _, _ = stats.chi2_contingency(ct2)
        results.append(['H₂: Support Contact Frequency', p2, self._decision(p2)])

        # -----------------------------------------------
        # H₃: Payment Method vs Churn
        # -----------------------------------------------
        ct3 = pd.crosstab(self.df['Payment'], self.df['Churn'])
        _, p3, _, _ = stats.chi2_contingency(ct3)
        results.append(['H₃: Payment Method', p3, self._decision(p3)])

        # -----------------------------------------------
        # H₄: Revenue Growth (YoY) – Grouped into Decline, Stable, Growth
        # -----------------------------------------------
        self.df['RevGrowthYoy'] = pd.to_numeric(self.df['RevGrowthYoy'], errors='coerce')  # Ensure numeric format
        self.df['RevGrowthGroup'] = pd.cut(
            self.df['RevGrowthYoy'],
            bins=[-float('inf'), -0.1, 0.1, float('inf')],
            labels=['Decline', 'Stable', 'Growth']
        )
        ct4 = pd.crosstab(self.df['RevGrowthGroup'], self.df['Churn'])
        _, p4, _, _ = stats.chi2_contingency(ct4)
        results.append(['H₄: Revenue Growth (YoY)', p4, self._decision(p4)])

        # -----------------------------------------------
        # H₅: Loyalty & Satisfaction (TenureBin + ServiceScore)
        # -----------------------------------------------
        self.df['LoyaltyGroup'] = self.df['TenureBin'].astype(str) + " | " + self.df['ServiceScore'].astype(str)
        ct5 = pd.crosstab(self.df['LoyaltyGroup'], self.df['Churn'])
        _, p5, _, _ = stats.chi2_contingency(ct5)
        results.append(['H₅: Loyalty & Satisfaction', p5, self._decision(p5)])

        # -----------------------------------------------
        # Compile results into a clean DataFrame
        # -----------------------------------------------
        df_results = pd.DataFrame(results, columns=['Hypothesis', 'p-value', 'Decision'])

        # Format p-values in scientific notation (e.g., 3.45e-05)
        df_results['p-value'] = df_results['p-value'].apply(lambda x: f"{x:.2e}")

        return df_results

    def _decision(self, p):
        """
        Internal helper to determine statistical significance.

        Args:
            p (float): p-value from test

        Returns:
            str: "Reject H₀" if p < 0.05, else "Fail to reject H₀"
        """
        return "Reject H₀" if p < 0.05 else "Fail to reject H₀"
