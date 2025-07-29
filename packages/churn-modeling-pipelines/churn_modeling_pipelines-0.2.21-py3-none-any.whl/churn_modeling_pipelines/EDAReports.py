# EDAReports.py

import pandas as pd

class EDAReports:
    """
    EDAReports — Generates structured summaries of the dataset.
    """

    def __init__(self, df):
        self.df = df

    def data_profile(self):
        """
        Returns basic profiling information for each column.
        """
        profile_data = []
        for col in self.df.columns:
            profile_data.append({
                "Column": col,
                "Data Type": self.df[col].dtype,
                "Non-Null Count": self.df[col].notnull().sum(),
                "Missing Count": self.df[col].isnull().sum(),
                "Unique Values": self.df[col].nunique(),
                "Sample Values": self.df[col].dropna().unique()[:3]
            })
        return pd.DataFrame(profile_data)

    def dtype_info(self):
        """
        Returns data types of each column.
        """
        return self.df.dtypes.reset_index().rename(columns={"index": "Column", 0: "Data Type"})

    def missing_summary(self):
        """
        Returns summary of missing values by column.
        """
        return self.df.isnull().sum().reset_index(name='Missing Count').rename(columns={'index': 'Column'})

    def value_counts_summary(self, column):
        """
        Returns counts and percentages for a specified column.
        """
        data = self.df[column].value_counts(dropna=False)
        percent = (data / data.sum() * 100).round(2)
        return pd.DataFrame({'Count': data, 'Percentage': percent})

    def generate_report(self):
        """
        Combines profile, types, and missing value summary into one dictionary.
        """
        return {
            "Data Profile": self.data_profile(),
            "Data Types": self.dtype_info(),
            "Missing Summary": self.missing_summary()
        }
