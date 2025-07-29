import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
from IPython.display import display, Markdown


class ChurnEvaluator:
    """
    ChurnEvaluator – Evaluates all variants of a model using consistent metrics.

    Features:
    - Evaluates both base and ensemble models with consistent metrics
    - Calculates Accuracy, Precision, Recall, F1-Score, and cost-sensitive score
    - Highlights best-performing variant using recall, cost, and F1-score
    - Optional inline visualization via ChurnPlotter (confusion matrix, ROC, radial chart)

    Returns:
        - best_variant_name (str)
        - best_model (fitted model)
        - result_df (pandas.DataFrame with metrics and annotations)
    """

    @staticmethod
    def _compute_metrics(y_true, y_pred):
        """
        Compute standard classification metrics and extract FP, FN for cost evaluation.
        """
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        confusion = confusion_matrix(y_true, y_pred)
        fp, fn = confusion[0][1], confusion[1][0]
        return accuracy, precision, recall, f1, fp, fn

    @staticmethod
    def evaluate_model(model_name, builder_method, X_train, X_test, y_train, y_test,
                       plot_variant_level_charts=True, fp_cost=100, fn_cost=500):
        """
        Evaluates multiple hyperparameter variants for a base model.
        """
        variants = builder_method()
        results = []
        model_objects = {}

        for i, (params, model) in enumerate(variants):
            y_pred = model.predict(X_test)
            accuracy, precision, recall, f1, fp, fn = ChurnEvaluator._compute_metrics(y_test, y_pred)
            cost = (fp * fp_cost) + (fn * fn_cost)

            variant_name = f"Variant {i+1}"
            model_objects[variant_name] = model

            results.append({
                "Model": model_name,
                "Variant": variant_name,
                "Accuracy": accuracy,
                "Precision": precision,
                "Recall": recall,
                "F1-Score": f1,
                "Cost ($)": cost,
                "Params": params
            })

        result_df = pd.DataFrame(results)
        best_cost = result_df["Cost ($)"].min()
        result_df["is_best_cost"] = result_df["Cost ($)"].apply(lambda x: "🟩 True" if x == best_cost else "🟥 False")

        best_idx = result_df.sort_values(
            by=["Recall", "Cost ($)", "F1-Score"],
            ascending=[False, True, False]
        ).index[0]

        result_df["is_best_variant"] = "❌"
        result_df.at[best_idx, "is_best_variant"] = "✅ Best"

        best_variant_name = result_df.loc[best_idx, "Variant"]
        best_model = model_objects[best_variant_name]

        if plot_variant_level_charts:
            display(Markdown(f"### Evaluation Summary – **{model_name}**"))
            display(result_df)

            try:
                from churn_modeling_pipelines import ChurnPlotter
                print(f"\nConfusion Matrix – {model_name}: {best_variant_name}")
                ChurnPlotter.plot_confusion_matrix(y_test, best_model.predict(X_test), model_name)

                print(f"\nROC Curve – All Variants: {model_name}")
                ChurnPlotter.plot_all_roc_curves(variants, X_test, y_test, model_name)

                print(f"\nRadial Chart – All Variants: {model_name}")
                ChurnPlotter.plot_composite_radial_chart(result_df, model_name)
            except ImportError:
                print("ChurnPlotter module not found. Skipping visualizations.")

        return best_variant_name, best_model, result_df

    @staticmethod
    def evaluate_ensemble_models(model_list, model_name, X_test, y_test,
                                 plot_variant_level_charts=True, fp_cost=100, fn_cost=500):
        """
        Evaluates a list of pre-built ensemble models.
        """
        results = []
        model_objects = {}

        for i, (params, model) in enumerate(model_list):
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

            accuracy, precision, recall, f1, fp, fn = ChurnEvaluator._compute_metrics(y_test, y_pred)
            cost = (fp * fp_cost) + (fn * fn_cost)

            variant_name = params.get("name", f"Variant {i+1}")
            model_objects[variant_name] = model

            results.append({
                "Model": model_name,
                "Variant": variant_name,
                "Accuracy": accuracy,
                "Precision": precision,
                "Recall": recall,
                "F1-Score": f1,
                "Cost ($)": cost,
                "Params": params
            })

        result_df = pd.DataFrame(results)
        best_cost = result_df["Cost ($)"].min()
        result_df["is_best_cost"] = result_df["Cost ($)"].apply(lambda x: "🟩 True" if x == best_cost else "🟥 False")

        best_idx = result_df.sort_values(
            by=["Recall", "Cost ($)", "F1-Score"],
            ascending=[False, True, False]
        ).index[0]

        result_df["is_best_variant"] = "❌"
        result_df.at[best_idx, "is_best_variant"] = "✅ Best"

        best_variant_name = result_df.loc[best_idx, "Variant"]
        best_model = model_objects[best_variant_name]

        if plot_variant_level_charts:
            display(Markdown(f"### Evaluation Summary – **{model_name}**"))
            display(result_df)

            try:
                from churn_modeling_pipelines import ChurnPlotter
                print(f"\nConfusion Matrix – {model_name}: {best_variant_name}")
                ChurnPlotter.plot_ensemble_confusion_matrix(best_model, X_test, y_test)

                print(f"\nROC Curve – {model_name}: {best_variant_name}")
                ChurnPlotter.plot_roc_curve(best_model, X_test, y_test, f"{model_name} – {best_variant_name}")

                print(f"\nRadial Chart – {model_name}: {best_variant_name}")
                ChurnPlotter.plot_radial_chart(result_df.loc[best_idx].to_dict(), f"{model_name} – {best_variant_name}")
            except ImportError:
                print("ChurnPlotter module not found. Skipping visualizations.")

        return best_variant_name, best_model, result_df
