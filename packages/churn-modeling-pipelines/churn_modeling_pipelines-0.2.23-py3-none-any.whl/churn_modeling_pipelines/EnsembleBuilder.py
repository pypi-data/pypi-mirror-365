# EnsembleBuilder.py
# ===================
# Contains reusable builder functions for training ensemble models in churn modeling

# =========================
# IMPORT REQUIRED LIBRARIES
# =========================
import warnings
import numpy as np
from .utils import set_random_seed  # ✅ Import the centralized seed setter

from sklearn.ensemble import (
    VotingClassifier, StackingClassifier, AdaBoostClassifier, BaggingClassifier,
    GradientBoostingClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier


class EnsembleBuilder:
    """
    EnsembleBuilder – A class to train and return multiple ensemble learning model variants.

    This builder supports a variety of ensemble methods:
    - Voting Classifier (soft/hard/weighted)
    - Stacking
    - AdaBoost
    - Bagging
    - Boosting methods (Gradient, CatBoost, LightGBM, Hist)
    - Custom Blending logic

    Parameters
    ----------
    X_train : pd.DataFrame
        Feature matrix used for training all ensemble models.
    y_train : pd.Series
        Target variable associated with the training set.
    seed : int, optional
        Random seed used to enforce reproducibility (default is 42).
    """

    def __init__(self, X_train, y_train, seed: int = 42):
        """
        Initialize the ensemble builder with training data and seed.
        Applies centralized seed setting for reproducibility.
        """
        set_random_seed(seed)  # ✅ Ensure consistent randomness across classifiers
        self.X_train = X_train
        self.y_train = y_train
        self.seed = seed

    def build_voting_classifier(self):
        """
        Build and train multiple VotingClassifier variants using different combinations
        of base learners and voting strategies (soft, hard, weighted).

        Returns
        -------
        list of tuples:
            Each tuple contains (metadata dict, trained VotingClassifier instance)
        """
        # Define common base learners to be reused across variants
        lr = LogisticRegression(max_iter=1000, random_state=self.seed)
        dt = DecisionTreeClassifier(max_depth=5, random_state=self.seed)
        knn = KNeighborsClassifier(n_neighbors=5)
        svm = SVC(probability=True, kernel='rbf', random_state=self.seed)
        xgb = XGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric='logloss',
            random_state=self.seed
        )

        # Define 5 voting classifier variants with different strategies
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

        # Build and train each voting classifier variant
        models = []
        for v in variants:
            model = VotingClassifier(
                estimators=v['estimators'],
                voting=v['voting'],
                weights=v.get('weights', None)  # Optional weighting
            )
            model.fit(self.X_train, self.y_train)
            models.append(({"name": v["name"]}, model))  # Append with metadata

        return models

    def build_stacking_classifier(self):
        """
        Build and train multiple StackingClassifier variants.
        Each variant uses a different combination of base learners and meta learners.

        Returns
        -------
        list of tuples:
            Each tuple contains (metadata dict, trained StackingClassifier instance)
        """
        # Define 5 stacking configurations with different base/meta learners
        variants = [
            {
                "name": "Stacking_LR_Meta_LR_DT",
                "base": [
                    ('lr', LogisticRegression(random_state=self.seed)),
                    ('dt', DecisionTreeClassifier(random_state=self.seed))
                ],
                "meta": LogisticRegression(random_state=self.seed),
                "passthrough": False
            },
            {
                "name": "Stacking_SVM_Meta_DT_KNN",
                "base": [
                    ('dt', DecisionTreeClassifier(random_state=self.seed)),
                    ('knn', KNeighborsClassifier())
                ],
                "meta": SVC(probability=True, random_state=self.seed),
                "passthrough": False
            },
            {
                "name": "Stacking_XGB_Meta_DT_KNN",
                "base": [
                    ('dt', DecisionTreeClassifier(random_state=self.seed)),
                    ('knn', KNeighborsClassifier())
                ],
                "meta": XGBClassifier(
                    use_label_encoder=False,
                    eval_metric='logloss',
                    random_state=self.seed
                ),
                "passthrough": True
            },
            {
                "name": "Stacking_LR_Meta_KNN_SVM",
                "base": [
                    ('knn', KNeighborsClassifier()),
                    ('svm', SVC(probability=True, random_state=self.seed))
                ],
                "meta": LogisticRegression(random_state=self.seed),
                "passthrough": False
            },
            {
                "name": "Stacking_LR_Meta_All_3",
                "base": [
                    ('lr', LogisticRegression(random_state=self.seed)),
                    ('knn', KNeighborsClassifier()),
                    ('dt', DecisionTreeClassifier(random_state=self.seed))
                ],
                "meta": LogisticRegression(random_state=self.seed),
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
        Build and train multiple AdaBoostClassifier variants using different base learners
        and hyperparameter settings for number of estimators and learning rate.

        Returns
        -------
        list of tuples:
            Each tuple contains (metadata dict, trained AdaBoostClassifier instance)
        """
        configs = [
            {
                "name": "AdaBoost_DT_50_0.1",
                "base": DecisionTreeClassifier(max_depth=1, random_state=self.seed),
                "n_estimators": 50,
                "learning_rate": 0.1
            },
            {
                "name": "AdaBoost_DT_100_0.05",
                "base": DecisionTreeClassifier(max_depth=2, random_state=self.seed),
                "n_estimators": 100,
                "learning_rate": 0.05
            },
            {
                "name": "AdaBoost_LR_50_1.0",
                "base": LogisticRegression(max_iter=1000, random_state=self.seed),
                "n_estimators": 50,
                "learning_rate": 1.0
            },
            {
                "name": "AdaBoost_DT_200_0.1",
                "base": DecisionTreeClassifier(max_depth=3, random_state=self.seed),
                "n_estimators": 200,
                "learning_rate": 0.1
            },
            {
                "name": "AdaBoost_LR_100_0.5",
                "base": LogisticRegression(max_iter=1000, random_state=self.seed),
                "n_estimators": 100,
                "learning_rate": 0.5
            }
        ]

        models = []
        for config in configs:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # Suppress convergence warnings
                model = AdaBoostClassifier(
                    estimator=config["base"],
                    n_estimators=config["n_estimators"],
                    learning_rate=config["learning_rate"],
                    random_state=self.seed
                )
                model.fit(self.X_train, self.y_train)
                models.append(({"name": config["name"]}, model))
        return models

    def build_bagging_classifier(self):
        """
        Build and train multiple BaggingClassifier variants using different base estimators
        and sampling strategies for bootstrapping.

        Returns
        -------
        list of tuples:
            Each tuple contains (metadata dict, trained BaggingClassifier instance)
        """
        configs = [
            {
                "name": "Bagging_DT_10_0.8",
                "base": DecisionTreeClassifier(max_depth=3, random_state=self.seed),
                "n_estimators": 10,
                "max_samples": 0.8,
                "max_features": 0.8,
                "bootstrap": True
            },
            {
                "name": "Bagging_DT_50_0.5",
                "base": DecisionTreeClassifier(max_depth=5, random_state=self.seed),
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
                "base": LogisticRegression(max_iter=1000, random_state=self.seed),
                "n_estimators": 20,
                "max_samples": 1.0,
                "max_features": 1.0,
                "bootstrap": True
            },
            {
                "name": "Bagging_DT_100_0.6",
                "base": DecisionTreeClassifier(max_depth=4, random_state=self.seed),
                "n_estimators": 100,
                "max_samples": 0.6,
                "max_features": 0.6,
                "bootstrap": False
            }
        ]

        models = []
        for config in configs:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # Avoid warnings for unstable estimators
                model = BaggingClassifier(
                    estimator=config["base"],
                    n_estimators=config["n_estimators"],
                    max_samples=config["max_samples"],
                    max_features=config["max_features"],
                    bootstrap=config["bootstrap"],
                    random_state=self.seed
                )
                model.fit(self.X_train, self.y_train)
                models.append(({"name": config["name"]}, model))
        return models

    def build_lightgbm_classifier(self):
        """
        Build and train multiple LightGBM (LGBMClassifier) variants with different 
        combinations of depth, estimators, and learning rate.

        Returns
        -------
        list of tuples:
            Each tuple contains (metadata dict with hyperparameters, trained LGBMClassifier)
        """
        configs = [
            {'n_estimators': 100, 'max_depth': 3, 'learning_rate': 0.1},
            {'n_estimators': 200, 'max_depth': 4, 'learning_rate': 0.1},
            {'n_estimators': 150, 'max_depth': 5, 'learning_rate': 0.05},
            {'n_estimators': 300, 'max_depth': 3, 'learning_rate': 0.01},
            {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.2},
        ]

        models = []
        for i, params in enumerate(configs):
            model = LGBMClassifier(**params, random_state=self.seed)
            model.fit(self.X_train, self.y_train)
            models.append(({"name": f"LGBM_{i+1}", **params}, model))
        return models

    def build_catboost_classifier(self):
        """
        Build and train multiple CatBoostClassifier variants with different iterations,
        depths, and learning rates. Verbose output is suppressed.

        Returns
        -------
        list of tuples:
            Each tuple contains (metadata dict with hyperparameters, trained CatBoostClassifier)
        """
        configs = [
            {'iterations': 100, 'depth': 3, 'learning_rate': 0.1},
            {'iterations': 200, 'depth': 4, 'learning_rate': 0.1},
            {'iterations': 150, 'depth': 5, 'learning_rate': 0.05},
            {'iterations': 300, 'depth': 3, 'learning_rate': 0.01},
            {'iterations': 100, 'depth': 6, 'learning_rate': 0.2},
        ]

        models = []
        for i, params in enumerate(configs):
            model = CatBoostClassifier(**params, verbose=0, random_state=self.seed)
            model.fit(self.X_train, self.y_train)
            models.append(({"name": f"CatBoost_{i+1}", **params}, model))
        return models

    def build_gradient_boosting_classifier(self):
        """
        Build and train multiple GradientBoostingClassifier variants with varied 
        n_estimators, max_depth, and learning_rate settings.

        Returns
        -------
        list of tuples:
            Each tuple contains (metadata dict, trained GradientBoostingClassifier)
        """
        configs = [
            {'n_estimators': 100, 'max_depth': 3, 'learning_rate': 0.1},
            {'n_estimators': 200, 'max_depth': 4, 'learning_rate': 0.1},
            {'n_estimators': 150, 'max_depth': 5, 'learning_rate': 0.05},
            {'n_estimators': 300, 'max_depth': 3, 'learning_rate': 0.01},
            {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.2},
        ]

        models = []
        for i, params in enumerate(configs):
            # Instantiate and fit the model with provided configuration
            model = GradientBoostingClassifier(**params, random_state=self.seed)
            model.fit(self.X_train, self.y_train)

            # Append metadata and model to the result list
            models.append(({"name": f"GBoost_{i+1}", **params}, model))
        return models

    def build_extra_trees_classifier(self):
        """
        Build and train multiple ExtraTreesClassifier variants. Although named Extra Trees, 
        this implementation mistakenly uses RandomForestClassifier, which should be corrected if necessary.

        Returns
        -------
        list of tuples:
            Each tuple contains (metadata dict, trained ExtraTreesClassifier model)
        """
        configs = [
            {'n_estimators': 100, 'max_depth': 3},
            {'n_estimators': 200, 'max_depth': 5},
            {'n_estimators': 150, 'max_depth': 7},
            {'n_estimators': 300, 'max_depth': None},
            {'n_estimators': 100, 'max_depth': 10},
        ]

        models = []
        for i, params in enumerate(configs):
            # WARNING: This currently uses RandomForestClassifier instead of ExtraTreesClassifier
            model = RandomForestClassifier(**params, random_state=self.seed)
            model.fit(self.X_train, self.y_train)

            models.append(({"name": f"ExtraTrees_{i+1}", **params}, model))
        return models

    def build_hist_gradient_boosting_classifier(self):
        """
        Build and train multiple HistGradientBoostingClassifier variants using different combinations
        of max_iter (trees), max_depth, and learning_rate.

        Returns
        -------
        list of tuples:
            Each tuple contains (metadata dict, trained HistGradientBoostingClassifier)
        """
        configs = [
            {'max_iter': 100, 'max_depth': 3, 'learning_rate': 0.1},
            {'max_iter': 200, 'max_depth': 4, 'learning_rate': 0.1},
            {'max_iter': 150, 'max_depth': 5, 'learning_rate': 0.05},
            {'max_iter': 300, 'max_depth': 3, 'learning_rate': 0.01},
            {'max_iter': 100, 'max_depth': 6, 'learning_rate': 0.2},
        ]

        models = []
        for i, params in enumerate(configs):
            model = HistGradientBoostingClassifier(**params, random_state=self.seed)
            model.fit(self.X_train, self.y_train)

            models.append(({"name": f"HistGB_{i+1}", **params}, model))
        return models

    def build_custom_voting_classifier(self):
        """
        Build and train multiple customized VotingClassifier variants combining diverse
        base models (XGBoost, CatBoost, SVM, Logistic Regression, Random Forest).

        Returns
        -------
        list of tuples:
            Each tuple contains (metadata dict, trained VotingClassifier)
        """
        # Define diverse base classifiers
        xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=self.seed)
        cat = CatBoostClassifier(verbose=0, random_state=self.seed)
        rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=self.seed)
        lr = LogisticRegression(max_iter=1000, random_state=self.seed)
        svm = SVC(probability=True, random_state=self.seed)

        # Define ensemble combinations
        variants = [
            {"name": "CustomVoting_XGB_RF_LR_Hard", "estimators": [('xgb', xgb), ('rf', rf), ('lr', lr)], "voting": 'hard'},
            {"name": "CustomVoting_XGB_RF_Cat_Soft", "estimators": [('xgb', xgb), ('rf', rf), ('cat', cat)], "voting": 'soft'},
            {"name": "CustomVoting_RF_LR_SVM_Soft", "estimators": [('rf', rf), ('lr', lr), ('svm', svm)], "voting": 'soft'},
            {"name": "CustomVoting_Weighted_XGB_Cat_LR", "estimators": [('xgb', xgb), ('cat', cat), ('lr', lr)], "voting": 'soft', "weights": [3, 2, 1]},
            {"name": "CustomVoting_XGB_SVM_RF_Hard", "estimators": [('xgb', xgb), ('svm', svm), ('rf', rf)], "voting": 'hard'}
        ]

        models = []
        for config in variants:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # Suppress any warnings
                model = VotingClassifier(
                    estimators=config['estimators'],
                    voting=config['voting'],
                    weights=config.get('weights', None)  # Optional weighting
                )
                model.fit(self.X_train, self.y_train)
                models.append(({"name": config["name"]}, model))
        return models

    def build_blending_classifier(self):
        """
        Build a simple Blending Ensemble manually using Decision Tree and KNN as base models,
        and Logistic Regression as the meta-learner trained on their predicted probabilities.

        Returns
        -------
        list:
            A list with one tuple containing metadata and a custom blending model.
        """
        from sklearn.model_selection import train_test_split

        # Split training data into base and validation sets for manual blending
        X_base, X_val, y_base, y_val = train_test_split(
            self.X_train, self.y_train, test_size=0.2, random_state=self.seed
        )

        # Train base models
        dt = DecisionTreeClassifier(max_depth=5, random_state=self.seed)
        knn = KNeighborsClassifier(n_neighbors=5)
        dt.fit(X_base, y_base)
        knn.fit(X_base, y_base)

        # Generate base model predictions (probabilities) on validation set
        dt_preds = dt.predict_proba(X_val)[:, 1].reshape(-1, 1)
        knn_preds = knn.predict_proba(X_val)[:, 1].reshape(-1, 1)

        # Stack the predictions horizontally to form meta-features
        stacked_preds = np.hstack([dt_preds, knn_preds])

        # Train meta-model on stacked predictions
        meta_model = LogisticRegression(max_iter=1000, random_state=self.seed)
        meta_model.fit(stacked_preds, y_val)

        # Define a simple wrapper class to mimic scikit-learn's API
        class BlendingEnsemble:
            """
            A lightweight custom blending class combining base models and a meta-model.
            """
            def __init__(self, base_models, meta_model):
                self.base_models = base_models
                self.meta_model = meta_model

            def predict(self, X):
                # Stack base model predictions to feed into meta-model
                base_outputs = np.hstack([model.predict_proba(X)[:, 1].reshape(-1, 1) for model in self.base_models])
                return self.meta_model.predict(base_outputs)

            def predict_proba(self, X):
                base_outputs = np.hstack([model.predict_proba(X)[:, 1].reshape(-1, 1) for model in self.base_models])
                return self.meta_model.predict_proba(base_outputs)

        # Instantiate and return the custom blending ensemble
        blending_model = BlendingEnsemble(base_models=[dt, knn], meta_model=meta_model)
        return [({"name": "Blending"}, blending_model)]
