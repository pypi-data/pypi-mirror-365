# =====================================================
# churn_modeling_pipelines/__init__.py
# -----------------------------------------------------
# Central package initializer for churn_modeling_pipelines
# This file enables clean import of all core classes, tools,
# and utilities for end-to-end churn modeling workflows.
# =====================================================

# -----------------------------------------------------
# CORE MODEL BUILDERS AND EVALUATORS
# -----------------------------------------------------
from .ChurnPreprocessor import ChurnPreprocessor               # Handles end-to-end preprocessing for churn datasets
from .ChurnModelBuilder import ChurnModelBuilder               # Builds model variants for base classifiers
from .ChurnEvaluator import ChurnEvaluator                     # Evaluates model variants using cost-sensitive metrics
from .ChurnPlotter import ChurnPlotter                         # Generates performance plots (confusion, ROC, radial)
from .ModelComparator import ModelComparator                   # Compares multiple best models across types
from .CustomerJourneyClassifier import CustomerJourneyClassifier  # Labels customer journeys based on behavioral rules
from .DataPreprocessor import DataPreprocessor                 # Modular data cleaning and transformation utility

# -----------------------------------------------------
# EDA AND HYPOTHESIS TESTING MODULES
# -----------------------------------------------------
from .EDAReports import EDAReports                             # Generates structured reports (dtypes, missing, value counts)
from .EDAPlots import EDAPlots                                 # Produces univariate and bivariate plots
from .ChurnHypothesisTester import ChurnHypothesisTester       # Performs chi-square tests for churn-related features
from .EDAHelper import EDAHelper                               # Unified wrapper combining EDAReports, EDAPlots, and Hypothesis tests

# -----------------------------------------------------
# ENSEMBLE MODEL BUILDER
# -----------------------------------------------------
from .EnsembleBuilder import EnsembleBuilder                   # Builds and evaluates advanced ensemble models (Voting, Boosting, etc.)

# -----------------------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------------------
from .utils import set_random_seed                             # Ensures global reproducibility across pipelines

# -----------------------------------------------------
# NEURAL NETWORK EVALUATION WRAPPER
# -----------------------------------------------------
from .NeuralNetWrapper import build_and_evaluate_neural_net    # Helper to train and evaluate a basic neural net model

# -----------------------------------------------------
# EXPORTED INTERFACE
# This defines the full public API of the package.
# Ensures users can do:
# `from churn_modeling_pipelines import *`
# -----------------------------------------------------
__all__ = [
    "ChurnPreprocessor",
    "ChurnModelBuilder",
    "ChurnEvaluator",
    "ChurnPlotter",
    "ModelComparator",
    "CustomerJourneyClassifier",
    "DataPreprocessor",
    "EDAReports",
    "EDAPlots",
    "ChurnHypothesisTester",
    "EDAHelper",
    "EnsembleBuilder",
    "set_random_seed",
    "build_and_evaluate_neural_net"
]
