# ==========================================================
# churn_modeling_pipelines/DataPreprocessor.py
# ----------------------------------------------------------
# Modular preprocessing pipeline for customer churn datasets.
# Handles cleaning, encoding, binning, imputation, outliers,
# normalization, validation, and city tier encoding.
# ==========================================================


import pandas as pd
import numpy as np
import re
import warnings
from typing import List

# ==========================================================
# DEFINE CUSTOM DATAPREPROCESSOR CLASS
# ==========================================================

class DataPreprocessor:
    """
    A modular preprocessing pipeline for customer churn datasets.

    This class encapsulates methods to:
    - Clean and standardize raw data
    - Handle invalid entries and missing values
    - Transform features (e.g., binning, encoding)
    - Normalize string formats
    - Perform validation and outlier clipping

    Attributes:
    -----------
    df : pd.DataFrame
        Internal copy of the input DataFrame (original preserved).

    transform_log : list
        Log of all transformation steps applied (for traceability).
    """

    def __init__(self, df: pd.DataFrame):
        """
        Constructor for the DataPreprocessor.

        Parameters:
        -----------
        df : pd.DataFrame
            The raw input data to be cleaned and preprocessed.
        """
        self.df = df.copy()                                # Work with a copy to preserve original dataset
        self.transform_log = []                            # Log all transformations for traceability

    # ==========================================================
    # STEP 1: STANDARDIZE COLUMN NAMES TO CAMELCASE
    # ==========================================================

    def standardize_column_names(self):
        """
        Standardize all column names to CamelCase format by:
        - Replacing special characters and spaces with underscores
        - Capitalizing each component
        - Removing extra characters

        Returns:
        --------
        self : DataPreprocessor
            Returns the updated object to allow method chaining.
        """
        def camel_case(s):
            s = re.sub(r'[\s\W]+', '_', s)  # Replace special characters with underscores
            parts = s.split('_')            # Split into parts
            return ''.join(p.capitalize() for p in parts if p)  # Capitalize and join

        old_names = self.df.columns.tolist()
        self.df.columns = [camel_case(col) for col in self.df.columns]
        self.transform_log.append("Standardized column names to CamelCase")

        print("Column names standardized.\nBefore:", old_names, "\nAfter:", self.df.columns.tolist())
        return self

    # ==========================================================
    # STEP 2: REPLACE INVALID ENTRIES (e.g., '#', 'Nan', '*')
    # ==========================================================

    def replace_invalid_entries(self):
        """
        Replace a predefined list of invalid symbols or placeholders 
        (e.g., '#', 'Nan', '*', etc.) with NumPy NaN.

        Returns:
        --------
        self : DataPreprocessor
            Updated object for method chaining.
        """
        invalid_entries = ['#', '$', '@', 'Nan', 'nan', '*', '&&&&', '+']

        # Count invalid values before replacement
        pre_invalid_counts = {
            col: self.df[col].isin(invalid_entries).sum() for col in self.df.columns
        }

        # Replace and coerce types
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            self.df = self.df.replace(invalid_entries, np.nan).infer_objects()

        post_missing_counts = self.df.isna().sum()
        self.transform_log.append("Replaced invalid entries with NaN")

        print("Invalid entries replaced:\n", {k: v for k, v in pre_invalid_counts.items() if v > 0})
        print("Missing after replacement (Top 10):", post_missing_counts.sort_values(ascending=False).head(10))
        return self

    # ==========================================================
    # STEP 3: CORRECT DATA TYPES FOR KEY COLUMNS
    # ==========================================================

    def correct_data_types(self):
        """
        Coerce key columns to appropriate data types (Int64, float64, category).

        Uses explicit type mapping and handles exceptions.
        Skips any missing or error-prone columns.

        Returns:
        --------
        self : DataPreprocessor
            Updated object for method chaining.
        """
        col_type_map = {
            'CcAgentScore': 'Int64',
            'AccountUserCount': 'Int64',
            'ServiceScore': 'Int64',
            'RevPerMonth': 'float64',
            'Cashback': 'float64',
            'DaySinceCcConnect': 'Int64',
            'ComplainLy': 'category'
        }

        converted, skipped = [], []
        print("Beginning data type corrections...\n")

        for col, dtype in col_type_map.items():
            if col in self.df.columns:
                try:
                    if dtype.startswith('Int'):
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce').round().astype('Int64')
                    elif dtype == 'float64':
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    elif dtype == 'category':
                        self.df[col] = self.df[col].astype('category')
                    converted.append((col, dtype))
                except Exception as e:
                    skipped.append((col, dtype, str(e)))
            else:
                skipped.append((col, dtype, 'Missing'))

        print("Converted:", converted, "\Skipped:", skipped)
        self.transform_log.append("Corrected data types")
        return self

    # ==========================================================
    # STEP 4: IMPUTE MISSING VALUES (COLUMN-WISE STRATEGIES)
    # ==========================================================

    def impute_missing_values(self):
        """
        Imputes missing values using column-specific logic:
        - Special columns use mode or median strategies
        - Numeric columns use skew-aware mean/median
        - Categorical columns use mode
        
        Returns:
        --------
        self : DataPreprocessor
            Updated object for method chaining.
        """
        special_cols = ['AccountUserCount', 'DaySinceCcConnect', 'ServiceScore', 'ComplainLy']
        log = []

        # Handle special columns first with custom logic
        for col in special_cols:
            if col in self.df.columns and self.df[col].isnull().sum() > 0:
                if col == 'AccountUserCount':
                    val = int(round(self.df[col].median()))
                    self.df[col] = self.df[col].fillna(val).astype('Int64')
                    log.append(f"Filled {col} with median: {val}")
                elif col == 'DaySinceCcConnect':
                    val = self.df[col].median()
                    self.df[col] = self.df[col].fillna(val).astype('Int64')
                    log.append(f"Filled {col} with median: {val}")
                elif col == 'ServiceScore':
                    val = int(round(self.df[col].mode().iloc[0]))
                    self.df[col] = self.df[col].fillna(val).astype('Int64')
                    log.append(f"Filled {col} with mode: {val}")
                elif col == 'ComplainLy':
                    val = self.df[col].mode().iloc[0]
                    self.df[col] = self.df[col].fillna(val).astype('category')
                    log.append(f"Filled {col} with mode: {val}")

        # Handle other numeric columns
        for col in self.df.select_dtypes(include=['float64', 'Int64']).columns:
            if self.df[col].isnull().sum() > 0 and col not in special_cols:
                strategy = 'median' if abs(self.df[col].skew()) > 1 else 'mean'
                fill_val = self.df[col].median() if strategy == 'median' else self.df[col].mean()
                if str(self.df[col].dtype) == 'Int64':
                    fill_val = pd.NA if pd.isna(fill_val) else int(round(fill_val))
                self.df[col] = self.df[col].fillna(fill_val)
                log.append(f"Filled {col} with {strategy}: {fill_val}")

        # Handle categorical/object columns using mode
        for col in self.df.select_dtypes(include=['object', 'category']).columns:
            if self.df[col].isnull().sum() > 0:
                mode = self.df[col].mode().iloc[0]
                self.df[col] = self.df[col].fillna(mode)
                log.append(f"Filled {col} with mode: {mode}")

        print("Imputation Log:", log)
        self.transform_log.append("Imputed missing values")
        return self

    # ==========================================================
    # STEP 5: FEATURE BINNING — GROUP CONTINUOUS VALUES
    # ==========================================================

    def bin_features(self):
        """
        Bins select numeric columns into categorical bins.

        Features binned:
        - Tenure → New, Recent, Established, Loyal
        - CcContactedLy → Occasional, Rare, Frequent
        - CouponUsedForPayment → Occasionally, Frequently, Heavily
        - DaySinceCcConnect → Recent, Weekly, Older

        Returns:
        --------
        self : DataPreprocessor
            Updated object for method chaining.
        """
        if 'Tenure' in self.df.columns:
            self.df['TenureBin'] = self.df['Tenure'].apply(
                lambda x: 'New' if pd.isna(x) or x <= 6 else
                          'Recent' if x <= 12 else
                          'Established' if x <= 24 else 'Loyal'
            ).astype('category')

        if 'CcContactedLy' in self.df.columns:
            self.df['CcContactedLYBin'] = self.df['CcContactedLy'].apply(
                lambda x: 'Occasional' if pd.isna(x) or x <= 11 else
                          'Rare' if x <= 17 else 'Frequent'
            ).astype('category')

        if 'CouponUsedForPayment' in self.df.columns:
            self.df['CouponUsageBin'] = self.df['CouponUsedForPayment'].apply(
                lambda x: 'Occasionally' if pd.isna(x) or x <= 2 else
                          'Frequently' if x <= 5 else 'Heavily'
            ).astype('category')

        if 'DaySinceCcConnect' in self.df.columns:
            self.df['CcConnectBin'] = self.df['DaySinceCcConnect'].apply(
                lambda x: 'Recent' if pd.isna(x) or x <= 2 else
                          'Weekly' if x <= 7 else 'Older'
            ).astype('category')

        self.transform_log.append("Binned features")
        return self

    # ==========================================================
    # STEP 6: OUTLIER DETECTION AND CLIPPING (IQR METHOD)
    # ==========================================================

    def clip_outliers(self):
        """
        Clips outliers using the IQR method for select numeric columns.

        Formula:
        - Lower Bound = Q1 - 1.5 * IQR
        - Upper Bound = Q3 + 1.5 * IQR

        Affected features:
        - RevPerMonth
        - Cashback
        - Tenure
        - CcContactedLy

        Returns:
        --------
        self : DataPreprocessor
            Updated object for method chaining.
        """
        features = ['RevPerMonth', 'Cashback', 'Tenure', 'CcContactedLy']

        for col in features:
            if col in self.df.columns:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outliers = ((self.df[col] < lower) | (self.df[col] > upper)).sum()
                self.df[col] = self.df[col].clip(lower, upper)
                print(f"{col}: Clipped {outliers} outliers using IQR [{lower:.2f}, {upper:.2f}]")

        self.transform_log.append("Clipped outliers using IQR")
        return self

    # ==========================================================
    # STEP 7: CLEAN & NORMALIZE STRING COLUMNS
    # ==========================================================

    def normalize_strings(self):
        """
        Cleans and standardizes string-based categorical columns:
        - Strips leading/trailing whitespace
        - Title-cases all strings
        - Replaces known abbreviations (e.g., 'M' → 'Male')

        Returns:
        --------
        self : DataPreprocessor
            Updated object for method chaining.
        """
        gender_map = {'M': 'Male', 'F': 'Female'}                # Map gender abbreviations
        plan_map = {'Regular +': 'Regular Plus', 'Super +': 'Super Plus'}  # Fix naming inconsistencies

        for col in self.df.select_dtypes(include=['object', 'category']):
            self.df[col] = self.df[col].astype(str).str.strip().str.title()  # Strip & title case strings
            if col == 'Gender':
                self.df[col] = self.df[col].replace(gender_map)
            if col == 'AccountSegment':
                self.df[col] = self.df[col].replace(plan_map)

        print("String normalization applied.")
        self.transform_log.append("Normalized string values")
        return self

    # ==========================================================
    # STEP 8: VALIDATE CHURN LABEL FORMAT
    # ==========================================================

    def verify_class_label(self):
        """
        Confirms that the 'Churn' column contains valid binary labels.
        - Accepted: 0, 1, 'Yes', 'No', 'True', 'False'

        Raises:
        -------
        AssertionError : if unexpected labels are found.

        Returns:
        --------
        self : DataPreprocessor
            Updated object for method chaining.
        """
        if 'Churn' in self.df.columns:
            allowed = {0, 1, '0', '1', 'Yes', 'No', 'True', 'False'}
            labels = self.df['Churn'].dropna().unique()
            assert set(labels).issubset(allowed), f"Unexpected churn labels: {labels}"
            print("Churn label valid. Distribution:\n", self.df['Churn'].value_counts())
            self.transform_log.append("Verified churn as binary label")
        else:
            print("Churn column missing.")
        return self

    # ==========================================================
    # STEP 9: DROP COLUMNS THAT SHOULD BE REMOVED
    # ==========================================================

    def drop_columns(self, cols: List[str]):
        """
        Drops user-specified columns from the DataFrame.

        Parameters:
        -----------
        cols : list of str
            List of column names to remove.

        Returns:
        --------
        self : DataPreprocessor
            Updated object for method chaining.
        """
        self.df.drop(columns=cols, inplace=True, errors='ignore')  # Ignore if column not found
        print(f"Dropped columns: {cols}")
        self.transform_log.append(f"Dropped columns: {cols}")
        return self

    # ==========================================================
    # STEP 10: ENCODE CITY TIER LABELS
    # ==========================================================

    def encode_city_tier(self):
        """
        Maps numeric CityTier values to descriptive labels:
        - 3 → Metro
        - 2 → Semi_Urban
        - 1 → Rural

        If CityTier is missing, prints a warning.

        Returns:
        --------
        self : DataPreprocessor
            Updated object for method chaining.
        """
        if 'CityTier' in self.df.columns:
            tier_map = {
                3: 'Metro', 2: 'Semi_Urban', 1: 'Rural',
                '3': 'Metro', '2': 'Semi_Urban', '1': 'Rural'
            }
            self.df['CityTier'] = self.df['CityTier'].map(tier_map).astype('category')
            print("Encoded City_Tier:\n", self.df['CityTier'].value_counts())
            self.transform_log.append("Encoded CityTier")
        else:
            print("CityTier column missing.")
        return self

    # ==========================================================
    # MASTER RUNNER — FULL PIPELINE EXECUTION
    # ==========================================================

    def run_full_pipeline(self, drop_cols: List[str]):
        """
        Executes all preprocessing steps in sequence:
        1. Standardize column names
        2. Replace invalid entries
        3. Correct data types
        4. Impute missing values
        5. Bin features
        6. Clip outliers
        7. Normalize string columns
        8. Validate churn label
        9. Drop irrelevant columns
        10. Encode city tier

        Parameters:
        -----------
        drop_cols : list of str
            Columns to be removed from the dataset.

        Returns:
        --------
        self : DataPreprocessor
            Fully processed object ready for modeling.
        """
        return self.standardize_column_names()\
                   .replace_invalid_entries()\
                   .correct_data_types()\
                   .impute_missing_values()\
                   .bin_features()\
                   .clip_outliers()\
                   .normalize_strings()\
                   .verify_class_label()\
                   .drop_columns(drop_cols)\
                   .encode_city_tier()

    # ==========================================================
    # UTILITY: RETURN THE CLEANED DATAFRAME
    # ==========================================================

    def get_clean_data(self) -> pd.DataFrame:
        """
        Returns the processed and cleaned DataFrame after all transformations.

        Returns:
        --------
        pd.DataFrame
            The cleaned DataFrame with all preprocessing steps applied.
        """
        return self.df

    # ==========================================================
    # UTILITY: DISPLAY ALL TRANSFORMATIONS APPLIED
    # ==========================================================

    def print_transform_log(self):
        """
        Prints a chronological log of all transformations applied to the data.
        Useful for tracking and auditing preprocessing actions.

        Returns:
        --------
        None
        """
        print("\Transformation Log:")
        for i, step in enumerate(self.transform_log, 1):
            print(f"{i}. {step}")
