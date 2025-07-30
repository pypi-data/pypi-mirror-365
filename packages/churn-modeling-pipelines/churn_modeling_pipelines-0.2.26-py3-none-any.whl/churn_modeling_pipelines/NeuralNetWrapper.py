# =============================================
# NeuralNetWrapper.py — Keras Evaluation Wrapper
# =============================================

# Import core components of the churn modeling pipeline
from churn_modeling_pipelines import ChurnModelBuilder, ChurnEvaluator, ChurnPlotter
from churn_modeling_pipelines.utils import set_random_seed

def build_and_evaluate_neural_net(X_train, X_test, y_train, y_test, seed=42, verbose=True):
    """
    Wrapper function to build, evaluate, and visualize Keras Neural Network variants.

    This function serves as a reusable evaluation pipeline for neural network models
    built using Keras (via SciKeras). It integrates training, evaluation, and
    optional visualization into a single callable workflow.

    Parameters:
    -----------
    X_train : pd.DataFrame
        Feature matrix for training the neural network.

    X_test : pd.DataFrame
        Feature matrix for evaluating the model on unseen data.

    y_train : pd.Series
        Binary labels corresponding to X_train (0 = No Churn, 1 = Churn).

    y_test : pd.Series
        Binary labels corresponding to X_test for final evaluation.

    seed : int, optional (default=42)
        Random seed used to enforce reproducibility in training and evaluation.

    verbose : bool, optional (default=True)
        Whether to display evaluation summary and performance plots (confusion matrix and ROC).

    Returns:
    --------
    results_df : pd.DataFrame
        Tabular summary of evaluation metrics for all neural network variants.

    variant_list : list of tuples
        List containing (params_dict, trained_model) for each neural net configuration.
    """

    # Step 1: Set the global random seed to ensure consistent results across runs
    set_random_seed(seed)

    # Step 2: Use ChurnModelBuilder to construct neural network model variants
    # The method build_keras_neural_net() should return a list of (params, model) tuples
    builder = ChurnModelBuilder(X_train, X_test, y_train)
    nn_variants = builder.build_keras_neural_net()

    # Step 3: Evaluate the performance of each trained variant on the test dataset
    evaluator = ChurnEvaluator(X_test, y_test)
    results_df = evaluator.evaluate_variants(nn_variants, model_name="NeuralNet")

    # Step 4: Append a clear model label to each row of the results DataFrame
    results_df["Model"] = [f"NeuralNet_Variant{i+1}" for i in range(len(results_df))]

    # Step 5: If enabled, print the evaluation and generate confusion matrix and ROC plots
    if verbose:
        # Show formatted evaluation results
        ChurnPlotter.show_clean_evaluation("Neural Network Evaluation", results_df)

        # Plot confusion matrix for the first neural network variant
        ChurnPlotter.plot_confusion_matrix(
            y_test, nn_variants[0][1].predict(X_test), "NeuralNet", dataset="Test Set"
        )

        # Plot ROC curves for all neural network variants
        ChurnPlotter.plot_all_roc_curves(nn_variants, X_test, y_test, "NeuralNet")

    # Return both raw model objects and their evaluation summary
    return results_df, nn_variants
