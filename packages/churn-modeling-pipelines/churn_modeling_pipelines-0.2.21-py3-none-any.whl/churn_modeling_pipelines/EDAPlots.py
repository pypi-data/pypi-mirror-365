# EDAPlots.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")  # Set global Seaborn style

class EDAPlots:
    """
    EDAPlots — Visualization methods for EDA.
    """

    def __init__(self, df):
        self.df = df

    def univariate_categorical(self, column, color='skyblue'):
        value_counts = self.df[column].dropna().value_counts()
        total = value_counts.sum()
        percentages = (value_counts / total * 100).round(1)

        plt.figure(figsize=(8, 4))
        bars = plt.bar(value_counts.index.astype(str), value_counts.values, color=color)
        for bar, count, pct in zip(bars, value_counts.values, percentages.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                     f'{count}\n({pct}%)', ha='center', va='bottom', fontsize=10)
        plt.title(f'Categorical Distribution: {column}')
        plt.tight_layout()
        plt.show()

    def univariate_numeric(self, column, bins=20, color='skyblue'):
        data = self.df[column].dropna()
        total = len(data)

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
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
        sns.kdeplot(data=data, ax=axes[1], fill=True, color=color)
        axes[1].set_title(f'KDE Plot of {column}')
        plt.tight_layout()
        plt.show()

    def categorical_vs_categorical(self, x, hue):
        data = self.df[[x, hue]].dropna()
        plt.figure(figsize=(8, 5))
        ax = sns.countplot(data=data, x=x, hue=hue, palette='Set2')
        plt.title(f"Count Plot: {x} vs {hue}")
        for container in ax.containers:
            ax.bar_label(container, fmt='%d', label_type='edge', fontsize=9, padding=3)
        plt.tight_layout()
        plt.show()

    def numeric_vs_numeric(self, x, y):
        plt.figure(figsize=(8, 5))
        sns.scatterplot(data=self.df, x=x, y=y)
        plt.title(f"Scatter Plot: {x} vs {y}")
        plt.tight_layout()
        plt.show()

    def categorical_vs_numeric(self, cat_col, num_col):
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=self.df, x=cat_col, y=num_col)
        plt.title(f"Box Plot: {num_col} by {cat_col}")
        plt.tight_layout()
        plt.show()

    def multivariate_pairplot(self, columns):
        sns.pairplot(self.df[columns].dropna())
        plt.suptitle("Multivariate Pairplot", y=1.02)
        plt.show()

    def correlation_matrix(self, figsize=(8, 6), cmap='YlGnBu'):
        corr = self.df.select_dtypes(include=['float64', 'int64']).corr()
        plt.figure(figsize=figsize)
        sns.heatmap(corr, annot=True, fmt=".2f", cmap=cmap)
        plt.title("Correlation Matrix")
        plt.tight_layout()
        plt.show()

    def violin_plot(self, cat_col, num_col):
        plt.figure(figsize=(8, 5))
        sns.violinplot(data=self.df, x=cat_col, y=num_col)
        plt.title(f"Violin Plot: {num_col} by {cat_col}")
        plt.tight_layout()
        plt.show()

    def bar_mean_plot(self, cat_col, num_col):
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
        plt.figure(figsize=(10, 5))
        sns.heatmap(self.df.isnull(), cbar=False, cmap='Reds')
        plt.title("Missing Value Heatmap")
        plt.tight_layout()
        plt.show()
