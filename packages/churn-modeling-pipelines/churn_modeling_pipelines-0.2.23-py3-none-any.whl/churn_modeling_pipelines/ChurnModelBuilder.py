# =====================================================
# churn_modeling_pipelines/ChurnModelBuilder.py
# -----------------------------------------------------
# Builds multiple model variants for churn prediction.
# Supports Logistic Regression, KNN, SVM, Naive Bayes,
# Decision Tree, and many more ML algorithms.
# =====================================================

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.neural_network import MLPClassifier

from .utils import set_random_seed  # Ensures reproducibility


class ChurnModelBuilder:
    """
    ChurnModelBuilder — Builds and trains multiple model variants
    for churn prediction tasks using different algorithm families.

    Features:
    - Accepts preprocessed training and test datasets.
    - Supports 10 model types including tree-based, boosting, and neural networks.
    - For each model, builds 5 tuned variants with parameter diversity.
    - Integrates centralized random seed for reproducibility.

    Returns:
        A list of (parameters_dict, trained_model) pairs for evaluation.
    """

    def __init__(self, X_train, X_test, y_train, seed: int = 42):
        """
        Initialize the builder with dataset and reproducibility seed.

        Parameters:
            X_train (DataFrame): Feature matrix for training.
            X_test (DataFrame): Feature matrix for testing.
            y_train (Series): Labels for training set.
            seed (int): Seed for reproducibility.
        """
        set_random_seed(seed)               # Set random seed globally
        self.X_train = X_train              # Store training features
        self.X_test = X_test                # Store testing features
        self.y_train = y_train              # Store training labels
        self.seed = seed                    # Save seed for internal use

    def build_logistic_regression(self):
        """
        Builds 5 Logistic Regression models with varied C and class_weight.

        Returns:
            List of (params_dict, trained_model)
        """
        combinations = [
            {'C': 0.01, 'class_weight': None},
            {'C': 0.1, 'class_weight': 'balanced'},
            {'C': 1.0, 'class_weight': None},
            {'C': 10.0, 'class_weight': 'balanced'},
            {'C': 100.0, 'class_weight': {0: 1, 1: 2}},
        ]
        models = []
        for params in combinations:
            model = LogisticRegression(**params, max_iter=1000, random_state=self.seed)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models

    def build_decision_tree(self):
        """
        Builds 5 Decision Tree models with varied max_depth and class_weight.

        Returns:
            List of (params_dict, trained_model)
        """
        combinations = [
            {'max_depth': 3, 'class_weight': None},
            {'max_depth': 5, 'class_weight': 'balanced'},
            {'max_depth': 7, 'class_weight': None},
            {'max_depth': 9, 'class_weight': 'balanced'},
            {'max_depth': None, 'class_weight': {0: 1, 1: 2}},
        ]
        models = []
        for params in combinations:
            model = DecisionTreeClassifier(**params, random_state=self.seed)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models

    def build_knn(self):
        """
        Builds 5 K-Nearest Neighbors models with different values of k.

        Returns:
            List of (params_dict, trained_model)
        """
        models = []
        for k in [3, 5, 7, 9, 11]:
            model = KNeighborsClassifier(n_neighbors=k)
            model.fit(self.X_train, self.y_train)
            models.append(({'n_neighbors': k}, model))
        return models

    def build_naive_bayes(self):
        """
        Builds 5 Naive Bayes models with different var_smoothing values.

        Returns:
            List of (params_dict, trained_model)
        """
        models = []
        for smoothing in [1e-9, 1e-8, 1e-7, 1e-6, 1e-5]:
            model = GaussianNB(var_smoothing=smoothing)
            model.fit(self.X_train, self.y_train)
            models.append(({'var_smoothing': smoothing}, model))
        return models

    def build_svm(self):
        """
        Builds 5 Support Vector Machine (SVM) models with different
        combinations of C, gamma, and class_weight.

        Returns:
            List of (params_dict, trained_model)
        """
        combinations = [
            {'C': 0.1, 'gamma': 'scale', 'class_weight': None},
            {'C': 1.0, 'gamma': 'scale', 'class_weight': 'balanced'},
            {'C': 10.0, 'gamma': 'auto', 'class_weight': 'balanced'},
            {'C': 0.5, 'gamma': 'auto', 'class_weight': None},
            {'C': 5.0, 'gamma': 'scale', 'class_weight': {0: 1, 1: 2}},
        ]
        models = []
        for params in combinations:
            model = SVC(**params, probability=True, random_state=self.seed)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models

    def build_random_forest(self):
        """
        Builds 5 Random Forest models with varying max_depth and n_estimators.

        Returns:
            List of (params_dict, trained_model)
        """
        combinations = [
            {'n_estimators': 100, 'max_depth': 3},
            {'n_estimators': 200, 'max_depth': 5},
            {'n_estimators': 300, 'max_depth': 7},
            {'n_estimators': 100, 'max_depth': None},
            {'n_estimators': 200, 'max_depth': 10},
        ]
        models = []
        for params in combinations:
            model = RandomForestClassifier(**params, random_state=self.seed)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models

    def build_xgboost(self):
        """
        Builds 5 XGBoost models with diverse learning rates, depth, and trees.

        Returns:
            List of (params_dict, trained_model)
        """
        combinations = [
            {'n_estimators': 100, 'max_depth': 3, 'learning_rate': 0.1},
            {'n_estimators': 200, 'max_depth': 4, 'learning_rate': 0.1},
            {'n_estimators': 150, 'max_depth': 5, 'learning_rate': 0.05},
            {'n_estimators': 300, 'max_depth': 3, 'learning_rate': 0.01},
            {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.2},
        ]
        models = []
        for params in combinations:
            model = XGBClassifier(**params, use_label_encoder=False, eval_metric='logloss', random_state=self.seed)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models

    def build_lightgbm(self):
        """
        Builds 5 LightGBM models with different depths, learning rates, and trees.

        Returns:
            List of (params_dict, trained_model)
        """
        combinations = [
            {'n_estimators': 100, 'learning_rate': 0.1, 'max_depth': 3},
            {'n_estimators': 150, 'learning_rate': 0.05, 'max_depth': 4},
            {'n_estimators': 200, 'learning_rate': 0.01, 'max_depth': 5},
            {'n_estimators': 250, 'learning_rate': 0.1, 'max_depth': -1},
            {'n_estimators': 300, 'learning_rate': 0.2, 'max_depth': 6},
        ]
        models = []
        for params in combinations:
            model = LGBMClassifier(**params, random_state=self.seed)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models

    def build_catboost(self):
        """
        Builds 5 CatBoost models with varied iteration counts, learning rates, and depths.

        Returns:
            List of (params_dict, trained_model)
        """
        combinations = [
            {'iterations': 100, 'learning_rate': 0.1, 'depth': 4},
            {'iterations': 150, 'learning_rate': 0.05, 'depth': 5},
            {'iterations': 200, 'learning_rate': 0.01, 'depth': 6},
            {'iterations': 250, 'learning_rate': 0.1, 'depth': 7},
            {'iterations': 300, 'learning_rate': 0.2, 'depth': 8},
        ]
        models = []
        for params in combinations:
            model = CatBoostClassifier(**params, verbose=0, random_state=self.seed)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models

    def build_keras_neural_net(self):
        """
        Builds 5 Neural Network variants using Scikeras and Keras.

        Architecture:
        - Fully connected feed-forward networks.
        - Hidden layers, dropout, batch normalization configurable.
        - Tuned across layer depth, activation, dropout, and learning rate.

        Returns:
            List of (params_dict, trained_model)
        """
        # Internal model builder passed to KerasClassifier
        def create_model(hidden_layers=[64, 32], dropout_rate=0.2, learning_rate=0.001, activation='relu'):
            """
            Creates a compiled Keras binary classification model.

            Parameters:
                hidden_layers (list): List of integers for hidden layer sizes
                dropout_rate (float): Dropout rate for regularization
                learning_rate (float): Learning rate for the Adam optimizer
                activation (str): Activation function for hidden layers

            Returns:
                Compiled Keras model
            """
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
            from tensorflow.keras.optimizers import Adam

            model = Sequential()
            model.add(Dense(hidden_layers[0], activation=activation, input_shape=(self.X_train.shape[1],)))
            model.add(BatchNormalization())
            model.add(Dropout(dropout_rate))

            for units in hidden_layers[1:]:
                model.add(Dense(units, activation=activation))
                model.add(BatchNormalization())
                model.add(Dropout(dropout_rate))

            model.add(Dense(1, activation='sigmoid'))  # Output layer for binary classification

            optimizer = Adam(learning_rate=learning_rate)
            model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
            return model

        # Define 5 variant configurations
        combinations = [
            {'hidden_layers': [64, 32], 'dropout_rate': 0.2, 'learning_rate': 0.001, 'activation': 'relu'},
            {'hidden_layers': [128, 64], 'dropout_rate': 0.3, 'learning_rate': 0.0005, 'activation': 'relu'},
            {'hidden_layers': [32, 16], 'dropout_rate': 0.1, 'learning_rate': 0.001, 'activation': 'tanh'},
            {'hidden_layers': [64, 32, 16], 'dropout_rate': 0.25, 'learning_rate': 0.0008, 'activation': 'relu'},
            {'hidden_layers': [128, 64, 32], 'dropout_rate': 0.3, 'learning_rate': 0.0003, 'activation': 'relu'},
        ]

        from scikeras.wrappers import KerasClassifier  # Import here to avoid issues if TensorFlow not needed elsewhere
        models = []
        for params in combinations:
            model = KerasClassifier(
                model=create_model,
                **params,
                epochs=50,
                batch_size=32,
                verbose=0,
                random_state=self.seed
            )
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models
