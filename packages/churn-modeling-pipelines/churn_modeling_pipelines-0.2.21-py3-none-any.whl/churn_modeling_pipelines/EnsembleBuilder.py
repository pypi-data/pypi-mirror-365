"""
EnsembleBuilder.py
------------------
This module contains reusable builder functions for training ensemble models
as part of the CHURNGUARD churn detection pipeline.

Supported ensemble methods:
1. Voting Classifier (Hard & Soft)
2. Stacking Classifier
3. AdaBoost Classifier
4. Bagging Classifier

Each method returns a dictionary of trained models using preselected base learners.
These models can be evaluated using the ChurnEvaluator class.
"""

# =========================
# IMPORT REQUIRED LIBRARIES
# =========================
import warnings                                  # Needed to suppress convergence and deprecation warnings
from sklearn.ensemble import VotingClassifier, StackingClassifier, AdaBoostClassifier, BaggingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


class EnsembleBuilder:
    def __init__(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train

    def build_voting_classifier(self):
        """
        Build 5 distinct VotingClassifier variants using different combinations of base models and weights.

        Returns:
            List of tuples: [({'name': 'Voting_X'}, model), ...]
        """
        from sklearn.ensemble import VotingClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.svm import SVC
        from xgboost import XGBClassifier

        # Define reusable base models
        lr = LogisticRegression(max_iter=1000, random_state=42)
        dt = DecisionTreeClassifier(max_depth=5, random_state=42)
        knn = KNeighborsClassifier(n_neighbors=5)
        svm = SVC(probability=True, kernel='rbf', random_state=42)
        xgb = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1,
                            use_label_encoder=False, eval_metric='logloss', random_state=42)

        variants = [
            {
                "name": "Voting_Hard_LR_DT_KNN",
                "estimators": [('lr', lr), ('dt', dt), ('knn', knn)],
                "voting": 'hard'
            },
            {
                "name": "Voting_Soft_LR_DT_KNN",
                "estimators": [('lr', lr), ('dt', dt), ('knn', knn)],
                "voting": 'soft'
            },
            {
                "name": "Voting_Soft_LR_SVM_XGB",
                "estimators": [('lr', lr), ('svm', svm), ('xgb', xgb)],
                "voting": 'soft'
            },
            {
                "name": "Voting_Soft_Weighted_XGB_SVM_DT",
                "estimators": [('xgb', xgb), ('svm', svm), ('dt', dt)],
                "voting": 'soft',
                "weights": [3, 2, 1]
            },
            {
                "name": "Voting_Hard_KNN_SVM_DT",
                "estimators": [('knn', knn), ('svm', svm), ('dt', dt)],
                "voting": 'hard'
            }
        ]

        models = []
        for v in variants:
            model = VotingClassifier(
                estimators=v['estimators'],
                voting=v['voting'],
                weights=v.get('weights', None)
            )
            model.fit(self.X_train, self.y_train)
            models.append(({"name": v["name"]}, model))

        return models


    def build_stacking_classifier(self):
        """
        Build 5 distinct StackingClassifier variants using different base learners and final estimators.

        Returns:
            List of tuples: [({'name': 'Stacking_X'}, model), ...]
        """
        from sklearn.ensemble import StackingClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.svm import SVC
        from xgboost import XGBClassifier

        variants = [
            {
                "name": "Stacking_LR_Meta_LR_DT",
                "base": [('lr', LogisticRegression()), ('dt', DecisionTreeClassifier())],
                "meta": LogisticRegression(),
                "passthrough": False
            },
            {
                "name": "Stacking_SVM_Meta_DT_KNN",
                "base": [('dt', DecisionTreeClassifier()), ('knn', KNeighborsClassifier())],
                "meta": SVC(probability=True),
                "passthrough": False
            },
            {
                "name": "Stacking_XGB_Meta_DT_KNN",
                "base": [('dt', DecisionTreeClassifier()), ('knn', KNeighborsClassifier())],
                "meta": XGBClassifier(use_label_encoder=False, eval_metric='logloss'),
                "passthrough": True
            },
            {
                "name": "Stacking_LR_Meta_KNN_SVM",
                "base": [('knn', KNeighborsClassifier()), ('svm', SVC(probability=True))],
                "meta": LogisticRegression(),
                "passthrough": False
            },
            {
                "name": "Stacking_LR_Meta_All_3",
                "base": [('lr', LogisticRegression()), ('knn', KNeighborsClassifier()), ('dt', DecisionTreeClassifier())],
                "meta": LogisticRegression(),
                "passthrough": True
            }
        ]

        models = []
        for v in variants:
            model = StackingClassifier(
                estimators=v["base"],
                final_estimator=v["meta"],
                passthrough=v["passthrough"]
            )
            model.fit(self.X_train, self.y_train)
            models.append(({"name": v["name"]}, model))

        return models


    def build_adaboost_classifier(self):
        """
        Build 5 AdaBoostClassifier variants using different base estimators and learning configurations.

        Returns:
            List of tuples: [({'name': 'AdaBoost_X'}, model), ...]
        """
        from sklearn.ensemble import AdaBoostClassifier
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.linear_model import LogisticRegression
        import warnings

        combinations = [
            {"name": "AdaBoost_DT_50_0.1", "base": DecisionTreeClassifier(max_depth=1), "n_estimators": 50, "learning_rate": 0.1},
            {"name": "AdaBoost_DT_100_0.05", "base": DecisionTreeClassifier(max_depth=2), "n_estimators": 100, "learning_rate": 0.05},
            {"name": "AdaBoost_LR_50_1.0", "base": LogisticRegression(max_iter=1000), "n_estimators": 50, "learning_rate": 1.0},
            {"name": "AdaBoost_DT_200_0.1", "base": DecisionTreeClassifier(max_depth=3), "n_estimators": 200, "learning_rate": 0.1},
            {"name": "AdaBoost_LR_100_0.5", "base": LogisticRegression(max_iter=1000), "n_estimators": 100, "learning_rate": 0.5},
        ]

        models = []
        for config in combinations:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = AdaBoostClassifier(
                    estimator=config["base"],
                    n_estimators=config["n_estimators"],
                    learning_rate=config["learning_rate"],
                    random_state=42
                )
                model.fit(self.X_train, self.y_train)
                models.append(({"name": config["name"]}, model))

        return models


    def build_bagging_classifier(self):
        """
        Build 5 BaggingClassifier variants using different base estimators and configurations.

        Returns:
            List of tuples: [({'name': 'Bagging_X'}, model), ...]
        """
        from sklearn.ensemble import BaggingClassifier
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.linear_model import LogisticRegression
        import warnings

        variants = [
            {
                "name": "Bagging_DT_10_0.8",
                "base": DecisionTreeClassifier(max_depth=3),
                "n_estimators": 10,
                "max_samples": 0.8,
                "max_features": 0.8,
                "bootstrap": True
            },
            {
                "name": "Bagging_DT_50_0.5",
                "base": DecisionTreeClassifier(max_depth=5),
                "n_estimators": 50,
                "max_samples": 0.5,
                "max_features": 0.7,
                "bootstrap": False
            },
            {
                "name": "Bagging_KNN_30_0.7",
                "base": KNeighborsClassifier(n_neighbors=5),
                "n_estimators": 30,
                "max_samples": 0.7,
                "max_features": 0.9,
                "bootstrap": True
            },
            {
                "name": "Bagging_LR_20_1.0",
                "base": LogisticRegression(max_iter=1000),
                "n_estimators": 20,
                "max_samples": 1.0,
                "max_features": 1.0,
                "bootstrap": True
            },
            {
                "name": "Bagging_DT_100_0.6",
                "base": DecisionTreeClassifier(max_depth=4),
                "n_estimators": 100,
                "max_samples": 0.6,
                "max_features": 0.6,
                "bootstrap": False
            }
        ]

        models = []
        for config in variants:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = BaggingClassifier(
                    estimator=config["base"],
                    n_estimators=config["n_estimators"],
                    max_samples=config["max_samples"],
                    max_features=config["max_features"],
                    bootstrap=config["bootstrap"],
                    random_state=42
                )
                model.fit(self.X_train, self.y_train)
                models.append(({"name": config["name"]}, model))

        return models


    def build_lightgbm_classifier(self):
        """
        Build LightGBM classifier variants using different boosting configurations.

        Returns:
            List of tuples: [({'name': 'LGBM_X'}, model), ...]
        """
        from lightgbm import LGBMClassifier

        combinations = [
            {'n_estimators': 100, 'max_depth': 3, 'learning_rate': 0.1},
            {'n_estimators': 200, 'max_depth': 4, 'learning_rate': 0.1},
            {'n_estimators': 150, 'max_depth': 5, 'learning_rate': 0.05},
            {'n_estimators': 300, 'max_depth': 3, 'learning_rate': 0.01},
            {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.2},
        ]

        models = []
        for i, params in enumerate(combinations):
            model = LGBMClassifier(**params, random_state=42)
            model.fit(self.X_train, self.y_train)
            models.append(({"name": f"LGBM_{i+1}", **params}, model))

        return models

    def build_catboost_classifier(self):
        """
        Build CatBoost classifier variants using tuned parameters.

        Returns:
            List of tuples: [({'name': 'CatBoost_X'}, model), ...]
        """
        from catboost import CatBoostClassifier

        combinations = [
            {'iterations': 100, 'depth': 3, 'learning_rate': 0.1},
            {'iterations': 200, 'depth': 4, 'learning_rate': 0.1},
            {'iterations': 150, 'depth': 5, 'learning_rate': 0.05},
            {'iterations': 300, 'depth': 3, 'learning_rate': 0.01},
            {'iterations': 100, 'depth': 6, 'learning_rate': 0.2},
        ]

        models = []
        for i, params in enumerate(combinations):
            model = CatBoostClassifier(**params, verbose=0, random_state=42)
            model.fit(self.X_train, self.y_train)
            models.append(({"name": f"CatBoost_{i+1}", **params}, model))

        return models

    def build_gradient_boosting_classifier(self):
        """
        Build GradientBoostingClassifier variants using different boosting parameters.

        Returns:
            List of tuples: [({'name': 'GBoost_X'}, model), ...]
        """
        from sklearn.ensemble import GradientBoostingClassifier

        combinations = [
            {'n_estimators': 100, 'max_depth': 3, 'learning_rate': 0.1},
            {'n_estimators': 200, 'max_depth': 4, 'learning_rate': 0.1},
            {'n_estimators': 150, 'max_depth': 5, 'learning_rate': 0.05},
            {'n_estimators': 300, 'max_depth': 3, 'learning_rate': 0.01},
            {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.2},
        ]

        models = []
        for i, params in enumerate(combinations):
            model = GradientBoostingClassifier(**params, random_state=42)
            model.fit(self.X_train, self.y_train)
            models.append(({"name": f"GBoost_{i+1}", **params}, model))

        return models

    def build_extra_trees_classifier(self):
        """
        Build ExtraTreesClassifier variants with varied tree depth and estimators.

        Returns:
            List of tuples: [({'name': 'ExtraTrees_X'}, model), ...]
        """
        from sklearn.ensemble import ExtraTreesClassifier

        combinations = [
            {'n_estimators': 100, 'max_depth': 3},
            {'n_estimators': 200, 'max_depth': 5},
            {'n_estimators': 150, 'max_depth': 7},
            {'n_estimators': 300, 'max_depth': None},
            {'n_estimators': 100, 'max_depth': 10},
        ]

        models = []
        for i, params in enumerate(combinations):
            model = ExtraTreesClassifier(**params, random_state=42)
            model.fit(self.X_train, self.y_train)
            models.append(({"name": f"ExtraTrees_{i+1}", **params}, model))

        return models

    def build_hist_gradient_boosting_classifier(self):
        """
        Build HistGradientBoostingClassifier variants with different boosting configurations.

        Returns:
            List of tuples: [({'name': 'HistGB_X'}, model), ...]
        """
        from sklearn.ensemble import HistGradientBoostingClassifier

        combinations = [
            {'max_iter': 100, 'max_depth': 3, 'learning_rate': 0.1},
            {'max_iter': 200, 'max_depth': 4, 'learning_rate': 0.1},
            {'max_iter': 150, 'max_depth': 5, 'learning_rate': 0.05},
            {'max_iter': 300, 'max_depth': 3, 'learning_rate': 0.01},
            {'max_iter': 100, 'max_depth': 6, 'learning_rate': 0.2},
        ]

        models = []
        for i, params in enumerate(combinations):
            model = HistGradientBoostingClassifier(**params, random_state=42)
            model.fit(self.X_train, self.y_train)
            models.append(({"name": f"HistGB_{i+1}", **params}, model))

        return models

    def build_custom_voting_classifier(self):
        """
        Build 5 custom VotingClassifier variants using advanced base models and strategic combinations.

        Returns:
            List of tuples: [({'name': 'CustomVoting_X'}, model), ...]
        """
        from sklearn.ensemble import VotingClassifier, RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from xgboost import XGBClassifier
        from catboost import CatBoostClassifier
        from sklearn.svm import SVC
        import warnings

        # Reusable advanced models
        xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
        cat = CatBoostClassifier(verbose=0, random_state=42)
        rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        lr = LogisticRegression(max_iter=1000)
        svm = SVC(probability=True)

        variants = [
            {
                "name": "CustomVoting_XGB_RF_LR_Hard",
                "estimators": [('xgb', xgb), ('rf', rf), ('lr', lr)],
                "voting": 'hard'
            },
            {
                "name": "CustomVoting_XGB_RF_Cat_Soft",
                "estimators": [('xgb', xgb), ('rf', rf), ('cat', cat)],
                "voting": 'soft'
            },
            {
                "name": "CustomVoting_RF_LR_SVM_Soft",
                "estimators": [('rf', rf), ('lr', lr), ('svm', svm)],
                "voting": 'soft'
            },
            {
                "name": "CustomVoting_Weighted_XGB_Cat_LR",
                "estimators": [('xgb', xgb), ('cat', cat), ('lr', lr)],
                "voting": 'soft',
                "weights": [3, 2, 1]
            },
            {
                "name": "CustomVoting_XGB_SVM_RF_Hard",
                "estimators": [('xgb', xgb), ('svm', svm), ('rf', rf)],
                "voting": 'hard'
            }
        ]

        models = []
        for config in variants:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = VotingClassifier(
                    estimators=config['estimators'],
                    voting=config['voting'],
                    weights=config.get('weights', None)
                )
                model.fit(self.X_train, self.y_train)
                models.append(({"name": config["name"]}, model))

        return models


    def build_blending_classifier(self):
        """
        Build a custom blending ensemble:
        - Train base models on train set
        - Train meta-model on base model predictions on holdout set

        Returns:
            List of one tuple: [({'name': 'Blending'}, blending_pipeline)]
        """
        from sklearn.linear_model import LogisticRegression
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.model_selection import train_test_split
        import numpy as np

        # Step 1: Split train set into base_train and holdout_val
        X_base, X_val, y_base, y_val = train_test_split(
            self.X_train, self.y_train, test_size=0.2, random_state=42
        )

        # Step 2: Train base models on base_train
        dt = DecisionTreeClassifier(max_depth=5, random_state=42)
        knn = KNeighborsClassifier(n_neighbors=5)
        dt.fit(X_base, y_base)
        knn.fit(X_base, y_base)

        # Step 3: Get predictions on holdout set
        dt_preds = dt.predict_proba(X_val)[:, 1].reshape(-1, 1)
        knn_preds = knn.predict_proba(X_val)[:, 1].reshape(-1, 1)
        stacked_preds = np.hstack([dt_preds, knn_preds])

        # Step 4: Train meta-model (Logistic Regression)
        meta_model = LogisticRegression(max_iter=1000)
        meta_model.fit(stacked_preds, y_val)

        # Step 5: Full pipeline for inference
        class BlendingEnsemble:
            def __init__(self, base_models, meta_model):
                self.base_models = base_models
                self.meta_model = meta_model

            def predict(self, X):
                base_outputs = np.hstack([
                    model.predict_proba(X)[:, 1].reshape(-1, 1)
                    for model in self.base_models
                ])
                return self.meta_model.predict(base_outputs)

            def predict_proba(self, X):
                base_outputs = np.hstack([
                    model.predict_proba(X)[:, 1].reshape(-1, 1)
                    for model in self.base_models
                ])
                return self.meta_model.predict_proba(base_outputs)

        blending_model = BlendingEnsemble(base_models=[dt, knn], meta_model=meta_model)
        return [({"name": "Blending"}, blending_model)]
