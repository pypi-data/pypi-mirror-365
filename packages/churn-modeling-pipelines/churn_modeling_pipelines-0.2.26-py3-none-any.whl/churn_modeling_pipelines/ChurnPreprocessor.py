# =====================================================
# churn_modeling_pipelines/ChurnPreprocessor.py
# -----------------------------------------------------
# Handles preprocessing pipeline for churn datasets.
# Encodes categoricals, scales numerics, imputes nulls,
# and returns train/test split with fitted transformers.
# =====================================================

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split


class ChurnPreprocessor:
    """
    ChurnPreprocessor — Prepares churn data for modeling.

    Features:
    ----------
    - Identifies numeric and categorical features.
    - Imputes missing values with safe strategies.
    - Applies StandardScaler to numerics and OneHotEncoder to categoricals.
    - Stores fitted transformers for reuse downstream.
    - Splits data into train/test sets with reproducibility.
    """

    def __init__(self, df, target_column='Churn'):
        """
        Initialize the preprocessor with the raw DataFrame.

        Parameters:
            df (pd.DataFrame): Original dataset including target column.
            target_column (str): Name of the target column (default = 'Churn')
        """
        self.df = df.copy()                                      # Avoid mutating original input
        self.df.columns = self.df.columns.str.strip()            # Clean column names of trailing spaces
        self.target_column = target_column.strip()               # Strip spaces from target column name

        # Will be filled during preprocessing
        self.pipeline = None                                     # ColumnTransformer that holds pipelines
        self.scaler = None                                       # StandardScaler fitted on numeric columns
        self.ohe = None                                          # OneHotEncoder fitted on categorical columns

        # Placeholders for split datasets
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    def preprocess(self, test_size=0.2, random_state=42):
        """
        Run the complete preprocessing pipeline.

        Steps:
        - Detect numeric and categorical features
        - Impute missing values
        - Encode categoricals and scale numerics
        - Perform train-test split
        - Store fitted scaler and encoder

        Parameters:
            test_size (float): Proportion of the data to use for testing.
            random_state (int): Random seed for reproducibility.

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Split into features and label
        X = self.df.drop(columns=[self.target_column])           # Features (everything but target)
        y = self.df[self.target_column]                          # Target column

        # Identify types
        numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = X.select_dtypes(include=['object']).columns.tolist()

        # Force all categoricals to string (avoids mixed-type errors)
        for col in categorical_cols:
            X[col] = X[col].astype(str)

        # === NUMERIC PIPELINE: Imputation + Scaling ===
        numeric_pipeline = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),         # Fill missing numerics with mean
            ('scaler', StandardScaler())                         # Scale to 0 mean and unit variance
        ])

        # === CATEGORICAL PIPELINE: Imputation + OneHotEncoding ===
        categorical_pipeline = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),                   # Fill missing categoricals with most frequent
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))  # One-hot encode with unknown handling
        ])

        # Combine both pipelines into a column transformer
        self.pipeline = ColumnTransformer(transformers=[
            ('num', numeric_pipeline, numeric_cols),
            ('cat', categorical_pipeline, categorical_cols)
        ])

        # Split data into training and testing sets
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Fit transformer on training and apply to both sets
        self.X_train = self.pipeline.fit_transform(self.X_train)
        self.X_test = self.pipeline.transform(self.X_test)

        # Store fitted components for external use
        self.scaler = self.pipeline.named_transformers_['num'].named_steps['scaler']
        self.ohe = self.pipeline.named_transformers_['cat'].named_steps['encoder']

        return self.X_train, self.X_test, self.y_train, self.y_test

    def get_clean_dataframe(self):
        """
        Return a cleaned copy of the original DataFrame.

        Useful for journey classification or EDA before transformation.

        Returns:
            pd.DataFrame: Cleaned input DataFrame (pre-split).
        """
        return self.df.copy()
