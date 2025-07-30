# =====================================================
# EDAReports.py — Exploratory Data Analysis Summarizer
# =====================================================
# Purpose: Provides structured summaries of a dataset for quick understanding.
# Includes profiling of columns, missing values, data types, and category counts.
# =====================================================

import pandas as pd


class EDAReports:
    """
    EDAReports — Generates structured summaries of the dataset.

    Attributes:
    -----------
    df : pd.DataFrame
        The input DataFrame to analyze.

    Methods:
    --------
    data_profile() :
        Returns a high-level profile for each column (dtype, nulls, unique values, sample).
    
    dtype_info() :
        Lists the data types of all columns.
    
    missing_summary() :
        Summarizes missing values for each column.
    
    value_counts_summary(column) :
        Returns count and percentage breakdown of values for a specific column.
    
    generate_report() :
        Returns a combined summary as a dictionary (profile, types, nulls).
    """

    def __init__(self, df):
        """
        Initialize the EDAReports class with a pandas DataFrame.

        Parameters:
        -----------
        df : pd.DataFrame
            The dataset to be analyzed.
        """
        self.df = df

    def data_profile(self):
        """
        Create a basic profile for each column including:
        - Data type
        - Number of non-null and null entries
        - Number of unique values
        - Sample values (up to 3 examples)

        Returns:
        --------
        pd.DataFrame :
            Tabular summary of column-wise data profile.
        """
        profile_data = []

        # Loop through each column to extract summary statistics
        for col in self.df.columns:
            profile_data.append({
                "Column": col,
                "Data Type": self.df[col].dtype,
                "Non-Null Count": self.df[col].notnull().sum(),
                "Missing Count": self.df[col].isnull().sum(),
                "Unique Values": self.df[col].nunique(),
                "Sample Values": self.df[col].dropna().unique()[:3]  # Up to 3 sample non-null values
            })

        return pd.DataFrame(profile_data)

    def dtype_info(self):
        """
        List the data types of each column.

        Returns:
        --------
        pd.DataFrame :
            Two-column DataFrame with column names and their data types.
        """
        return self.df.dtypes.reset_index().rename(
            columns={"index": "Column", 0: "Data Type"}
        )

    def missing_summary(self):
        """
        Summarize the number of missing values per column.

        Returns:
        --------
        pd.DataFrame :
            Summary of missing value counts by column.
        """
        return self.df.isnull().sum().reset_index(name='Missing Count').rename(
            columns={'index': 'Column'}
        )

    def value_counts_summary(self, column):
        """
        Compute value counts and corresponding percentage for a single column.

        Parameters:
        -----------
        column : str
            Column name for which the value counts are computed.

        Returns:
        --------
        pd.DataFrame :
            Value count and percentage table for the selected column.
        """
        data = self.df[column].value_counts(dropna=False)  # Includes NaNs
        percent = (data / data.sum() * 100).round(2)       # Convert to percentage

        return pd.DataFrame({
            'Count': data,
            'Percentage': percent
        })

    def generate_report(self):
        """
        Generate a complete summary report consisting of:
        - Data profile
        - Data types
        - Missing value summary

        Returns:
        --------
        dict :
            Dictionary with keys 'Data Profile', 'Data Types', and 'Missing Summary',
            each containing their respective DataFrame.
        """
        return {
            "Data Profile": self.data_profile(),
            "Data Types": self.dtype_info(),
            "Missing Summary": self.missing_summary()
        }
