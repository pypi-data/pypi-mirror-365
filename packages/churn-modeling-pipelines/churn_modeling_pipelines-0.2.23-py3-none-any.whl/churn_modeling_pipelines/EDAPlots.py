# ===============================================
# EDAPlots.py — Visualization Suite for EDA
# ===============================================
# Purpose: Contains reusable plotting methods to visualize
# various distributions and relationships in your dataset.
# ===============================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set consistent style for seaborn plots
sns.set(style="whitegrid")


class EDAPlots:
    """
    EDAPlots — Provides visual exploration of the dataset.

    Attributes:
    -----------
    df : pd.DataFrame
        The DataFrame to visualize.

    Methods:
    --------
    univariate_categorical(column, color) :
        Bar plot showing frequency & % for categorical column.

    univariate_numeric(column, bins, color) :
        Histogram + KDE plot for numerical distribution.

    categorical_vs_categorical(x, hue) :
        Count plot comparing two categorical variables.

    numeric_vs_numeric(x, y) :
        Scatter plot between two numerical columns.

    categorical_vs_numeric(cat_col, num_col) :
        Boxplot comparing numeric distribution across categories.

    multivariate_pairplot(columns) :
        Pairplot for exploring interactions among multiple features.

    correlation_matrix(figsize, cmap) :
        Heatmap showing Pearson correlation of numerical variables.

    violin_plot(cat_col, num_col) :
        Violin plot of numeric distribution across categories.

    bar_mean_plot(cat_col, num_col) :
        Bar chart showing average values grouped by categories.

    missing_heatmap() :
        Heatmap to visually inspect missing values.
    """

    def __init__(self, df):
        """
        Initialize the visualizer with a dataset.

        Parameters:
        -----------
        df : pd.DataFrame
            The input DataFrame to be plotted.
        """
        self.df = df

    def univariate_categorical(self, column, color='skyblue'):
        """
        Plot a bar chart of frequency and percentage for a categorical variable.

        Parameters:
        -----------
        column : str
            The name of the categorical column.
        color : str
            The bar color (default is skyblue).
        """
        value_counts = self.df[column].dropna().value_counts()
        total = value_counts.sum()
        percentages = (value_counts / total * 100).round(1)

        # Create bar plot
        plt.figure(figsize=(8, 4))
        bars = plt.bar(value_counts.index.astype(str), value_counts.values, color=color)

        # Add text labels for count and percentage
        for bar, count, pct in zip(bars, value_counts.values, percentages.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                     f'{count}\n({pct}%)', ha='center', va='bottom', fontsize=10)

        plt.title(f'Categorical Distribution: {column}')
        plt.tight_layout()
        plt.show()

    def univariate_numeric(self, column, bins=20, color='skyblue'):
        """
        Plot a histogram and KDE curve for a numerical variable.

        Parameters:
        -----------
        column : str
            The name of the numerical column.
        bins : int
            Number of histogram bins.
        color : str
            Color for the histogram and KDE.
        """
        data = self.df[column].dropna()
        total = len(data)

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # Histogram subplot
        counts, bin_edges, patches = axes[0].hist(data, bins=bins, color=color, edgecolor='white')
        for i in range(len(patches)):
            height = patches[i].get_height()
            if height > 0:
                percentage = f"({height / total * 100:.1f}%)"
                axes[0].text(patches[i].get_x() + patches[i].get_width() / 2,
                             height + total * 0.01,
                             f"{int(height)}\n{percentage}",
                             ha='center', va='bottom', fontsize=8)
        axes[0].set_title(f'Histogram of {column}')

        # KDE subplot
        sns.kdeplot(data=data, ax=axes[1], fill=True, color=color)
        axes[1].set_title(f'KDE Plot of {column}')

        plt.tight_layout()
        plt.show()

    def categorical_vs_categorical(self, x, hue):
        """
        Plot a count plot showing interaction between two categorical columns.

        Parameters:
        -----------
        x : str
            Column for x-axis (base category).
        hue : str
            Column used to split the bars (sub-category).
        """
        data = self.df[[x, hue]].dropna()
        plt.figure(figsize=(8, 5))
        ax = sns.countplot(data=data, x=x, hue=hue, palette='Set2')
        plt.title(f"Count Plot: {x} vs {hue}")

        # Add bar labels
        for container in ax.containers:
            ax.bar_label(container, fmt='%d', label_type='edge', fontsize=9, padding=3)

        plt.tight_layout()
        plt.show()

    def numeric_vs_numeric(self, x, y):
        """
        Scatter plot for two numeric columns to show their relationship.

        Parameters:
        -----------
        x : str
            Column for x-axis.
        y : str
            Column for y-axis.
        """
        plt.figure(figsize=(8, 5))
        sns.scatterplot(data=self.df, x=x, y=y)
        plt.title(f"Scatter Plot: {x} vs {y}")
        plt.tight_layout()
        plt.show()

    def categorical_vs_numeric(self, cat_col, num_col):
        """
        Box plot to compare numeric distribution across categories.

        Parameters:
        -----------
        cat_col : str
            Categorical feature on x-axis.
        num_col : str
            Numerical feature on y-axis.
        """
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=self.df, x=cat_col, y=num_col)
        plt.title(f"Box Plot: {num_col} by {cat_col}")
        plt.tight_layout()
        plt.show()

    def multivariate_pairplot(self, columns):
        """
        Generate a Seaborn pairplot to explore interactions among multiple numeric features.

        Parameters:
        -----------
        columns : list of str
            List of column names to include in the pairplot.
        """
        sns.pairplot(self.df[columns].dropna())
        plt.suptitle("Multivariate Pairplot", y=1.02)
        plt.show()

    def correlation_matrix(self, figsize=(8, 6), cmap='YlGnBu'):
        """
        Plot a correlation heatmap of numerical features in the DataFrame.

        Parameters:
        -----------
        figsize : tuple
            Size of the figure (width, height).
        cmap : str
            Color map to use for the heatmap.
        """
        # Compute correlation only on numeric columns
        corr = self.df.select_dtypes(include=['float64', 'int64']).corr()

        plt.figure(figsize=figsize)
        sns.heatmap(corr, annot=True, fmt=".2f", cmap=cmap)
        plt.title("Correlation Matrix")
        plt.tight_layout()
        plt.show()

    def violin_plot(self, cat_col, num_col):
        """
        Create a violin plot showing numeric distribution per category.

        Parameters:
        -----------
        cat_col : str
            Categorical column for the x-axis.
        num_col : str
            Numerical column for the y-axis.
        """
        plt.figure(figsize=(8, 5))
        sns.violinplot(data=self.df, x=cat_col, y=num_col)
        plt.title(f"Violin Plot: {num_col} by {cat_col}")
        plt.tight_layout()
        plt.show()

    def bar_mean_plot(self, cat_col, num_col):
        """
        Bar chart showing average numeric values grouped by categorical values.

        Parameters:
        -----------
        cat_col : str
            Categorical feature used for grouping.
        num_col : str
            Numeric feature to compute mean values.
        """
        # Aggregate and sort data by mean
        agg_data = self.df.groupby(cat_col)[num_col].mean().sort_values()

        plt.figure(figsize=(10, 5))
        sns.barplot(
            x=agg_data.index,
            y=agg_data.values,
            hue=agg_data.index,
            palette='viridis',
            legend=False
        )
        plt.ylabel(f"Average {num_col}")
        plt.title(f"Average {num_col} by {cat_col}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def missing_heatmap(self):
        """
        Display a heatmap to visualize missing values across the DataFrame.
        """
        plt.figure(figsize=(10, 5))
        sns.heatmap(self.df.isnull(), cbar=False, cmap='Reds')
        plt.title("Missing Value Heatmap")
        plt.tight_layout()
        plt.show()
