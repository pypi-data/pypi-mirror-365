# ChurnHypothesisTester.py

import pandas as pd
from scipy import stats


class ChurnHypothesisTester:
    """
    ChurnHypothesisTester — Statistical hypothesis testing for churn-related patterns.
    """

    def __init__(self, df):
        self.df = df.copy()

    def test_churn_hypotheses_stats(self):
        """
        Performs chi-square tests for key churn-related hypotheses.
        Returns: DataFrame of hypothesis, p-values, and statistical decisions.
        """
        results = []

        # --- Hypothesis 1: Account User Count ---
        self.df['UserCountGroup'] = self.df['AccountUserCount'].apply(
            lambda x: '>3 Users' if x > 3 else '≤3 Users'
        )
        ct1 = pd.crosstab(self.df['UserCountGroup'], self.df['Churn'])
        _, p1, _, _ = stats.chi2_contingency(ct1)
        results.append(['H₁: Account User Count', p1, self._decision(p1)])

        # --- Hypothesis 2: Support Contact Frequency ---
        ct2 = pd.crosstab(self.df['CcContactedLYBin'], self.df['Churn'])
        _, p2, _, _ = stats.chi2_contingency(ct2)
        results.append(['H₂: Support Contact Frequency', p2, self._decision(p2)])

        # --- Hypothesis 3: Payment Method ---
        ct3 = pd.crosstab(self.df['Payment'], self.df['Churn'])
        _, p3, _, _ = stats.chi2_contingency(ct3)
        results.append(['H₃: Payment Method', p3, self._decision(p3)])

        # --- Hypothesis 4: Revenue Growth (YoY) ---
        self.df['RevGrowthYoy'] = pd.to_numeric(self.df['RevGrowthYoy'], errors='coerce')
        self.df['RevGrowthGroup'] = pd.cut(
            self.df['RevGrowthYoy'],
            bins=[-float('inf'), -0.1, 0.1, float('inf')],
            labels=['Decline', 'Stable', 'Growth']
        )
        ct4 = pd.crosstab(self.df['RevGrowthGroup'], self.df['Churn'])
        _, p4, _, _ = stats.chi2_contingency(ct4)
        results.append(['H₄: Revenue Growth (YoY)', p4, self._decision(p4)])

        # --- Hypothesis 5: Loyalty and Satisfaction ---
        self.df['LoyaltyGroup'] = self.df['TenureBin'].astype(str) + " | " + self.df['ServiceScore'].astype(str)
        ct5 = pd.crosstab(self.df['LoyaltyGroup'], self.df['Churn'])
        _, p5, _, _ = stats.chi2_contingency(ct5)
        results.append(['H₅: Loyalty & Satisfaction', p5, self._decision(p5)])

        # Compile and return results
        df_results = pd.DataFrame(results, columns=['Hypothesis', 'p-value', 'Decision'])
        df_results['p-value'] = df_results['p-value'].apply(lambda x: f"{x:.2e}")
        return df_results

    def _decision(self, p):
        return "Reject H₀" if p < 0.05 else "Fail to reject H₀"
