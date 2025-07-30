from .EDAReports import EDAReports
from .EDAPlots import EDAPlots
from .ChurnHypothesisTester import ChurnHypothesisTester

class EDAHelper:
    """
    EDAHelper — Unified wrapper class for exploratory data analysis (EDA).

    This high-level interface wraps three core EDA modules:
    - EDAReports: Data summaries and profiling
    - EDAPlots: Visualizations for numerical and categorical insights
    - ChurnHypothesisTester: Basic hypothesis testing related to churn

    It offers shortcut methods to access commonly used functionality.
    """

    def __init__(self, df):
        """
        Initialize the EDAHelper with a DataFrame.

        Parameters:
        -----------
        df : pd.DataFrame
            The input dataset for analysis.
        """
        self.df = df
        self.reports = EDAReports(df)                 # Summary tables
        self.plots = EDAPlots(df)                     # Charts and visuals
        self.hypothesis = ChurnHypothesisTester(df)   # Statistical hypothesis testing

    # ================================
    # Report & Profiling Shortcuts
    # ================================

    def generate_report(self):
        """
        Run all report modules: profile, data types, and missing values.

        Returns:
        --------
        dict: Contains three dataframes with structured EDA outputs.
        """
        return self.reports.generate_report()

    def data_profile(self):
        """
        Generate column-level summaries, including:
        - Dtype, missing count, unique values, and samples.

        Returns:
        --------
        pd.DataFrame: Column-level profiling information.
        """
        return self.reports.data_profile()

    def dtype_info(self):
        """
        Return data types for all columns in the DataFrame.

        Returns:
        --------
        pd.DataFrame: Column names and their respective data types.
        """
        return self.reports.dtype_info()

    def value_counts_summary(self, column):
        """
        Get value counts and percentages for a given column.

        Parameters:
        -----------
        column : str
            Column to analyze.

        Returns:
        --------
        pd.DataFrame: Count and percentage breakdown of values.
        """
        return self.reports.value_counts_summary(column)

    # ================================
    # Plotting Shortcuts
    # ================================

    def univariate_categorical(self, column):
        """
        Plot a bar chart showing counts and percentages for a categorical column.

        Parameters:
        -----------
        column : str
            Name of the categorical column.
        """
        return self.plots.univariate_categorical(column)

    def univariate_numeric(self, column):
        """
        Plot a histogram and KDE for a numeric column.

        Parameters:
        -----------
        column : str
            Name of the numerical column.
        """
        return self.plots.univariate_numeric(column)

    def plot_correlation_heatmap(self):
        """
        Plot a heatmap of correlation among numeric columns.

        Returns:
        --------
        matplotlib figure showing correlations.
        """
        return self.plots.plot_correlation_heatmap()

    def categorical_vs_categorical(self, x, hue):
        """
        Plot a grouped bar chart comparing two categorical variables.

        Parameters:
        -----------
        x : str
            Base category on the x-axis.

        hue : str
            Grouping category used for hue coloring.
        """
        return self.plots.categorical_vs_categorical(x, hue)

    def numeric_vs_numeric(self, x, y):
        """
        Create a scatter plot to show the relationship between two numeric columns.

        Parameters:
        -----------
        x : str
            Feature for x-axis.

        y : str
            Feature for y-axis.
        """
        return self.plots.numeric_vs_numeric(x, y)

    def categorical_vs_numeric(self, cat_col, num_col):
        """
        Create a boxplot of a numeric column grouped by a categorical column.

        Parameters:
        -----------
        cat_col : str
            Categorical feature for grouping.

        num_col : str
            Numerical feature to analyze distribution.
        """
        return self.plots.categorical_vs_numeric(cat_col, num_col)

    def multivariate_pairplot(self, columns):
        """
        Create a pairplot for a list of columns.

        Parameters:
        -----------
        columns : list
            List of column names to include in the pairplot.
        """
        return self.plots.multivariate_pairplot(columns)

    def correlation_matrix(self):
        """
        Plot the full correlation matrix of numeric features.
        """
        return self.plots.correlation_matrix()

    def violin_plot(self, cat_col, num_col):
        """
        Plot a violin plot showing distribution of a numerical column
        split by categories.

        Parameters:
        -----------
        cat_col : str
            Categorical feature for x-axis.

        num_col : str
            Numeric feature for y-axis.
        """
        return self.plots.violin_plot(cat_col, num_col)

    def bar_mean_plot(self, cat_col, num_col):
        """
        Plot average of a numeric column for each category in a categorical column.

        Parameters:
        -----------
        cat_col : str
            Categorical column.

        num_col : str
            Numeric column to average.
        """
        return self.plots.bar_mean_plot(cat_col, num_col)

    def missing_heatmap(self):
        """
        Display a heatmap of missing values across the DataFrame.
        """
        return self.plots.missing_heatmap()

    # ================================
    # Hypothesis Testing Shortcut
    # ================================

    def test_churn_hypotheses_stats(self):
        """
        Run statistical tests to evaluate churn-related hypotheses.

        Returns:
        --------
        pd.DataFrame: Hypothesis test results including p-values.
        """
        return self.hypothesis.test_churn_hypotheses_stats()
