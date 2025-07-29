# =============================
# Imports
# =============================
from .EDAReports import EDAReports
from .EDAPlots import EDAPlots
from .ChurnHypothesisTester import ChurnHypothesisTester

# =============================
# Class Definition
# =============================

class EDAHelper:
    """
    EDAHelper — Unified wrapper class for exploratory data analysis.

    This class provides a modular and backward-compatible interface
    that delegates core responsibilities to specialized internal modules:
    
    - EDAReports:     For data profiling, types, missing values, etc.
    - EDAPlots:       For univariate, bivariate, multivariate visualizations.
    - ChurnHypothesisTester: For statistical hypothesis testing.

    Usage:
        eda = EDAHelper(df)

        # Access reports
        eda.reports.data_profile()
        eda.reports.generate_report()

        # Access plots
        eda.plots.univariate_numeric("RevPerMonth")
        eda.plots.plot_correlation_heatmap()

        # Run hypothesis testing
        eda.hypothesis.test_churn_hypotheses_stats()
    """

    def __init__(self, df):
        """
        Initialize the unified EDAHelper class.

        Parameters:
            df (pd.DataFrame): The input dataset to be profiled and analyzed.
        """
        self.df = df
        self.reports = EDAReports(df)
        self.plots = EDAPlots(df)
        self.hypothesis = ChurnHypothesisTester(df)

    # Optional convenience forwarding methods for commonly used functions
    def generate_report(self):
        """
        Shortcut to EDAReports.generate_report()
        """
        return self.reports.generate_report()

    def plot_correlation_heatmap(self):
        """
        Shortcut to EDAPlots.plot_correlation_heatmap()
        """
        return self.plots.plot_correlation_heatmap()

    def test_churn_hypotheses_stats(self):
        """
        Shortcut to ChurnHypothesisTester.test_churn_hypotheses_stats()
        """
        return self.hypothesis.test_churn_hypotheses_stats()
