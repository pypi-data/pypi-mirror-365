import pandas as pd
import matplotlib.pyplot as plt
import shap
import numpy as np
from sklearn.pipeline import Pipeline

class ModelInterpreter:
    """
    Interpret trained machine learning models for regression or classification.

    Supports:
        - Tree-based models: Feature importances
        - Linear models: Coefficients
        - SHAP values: Works for both regression and classification
        - Pipelines: Automatically extracts final model & transformed feature names
    """

    def __init__(self, model, X_train, task='regression'):
        """
        Initialize the interpreter.

        Args:
            model: Trained scikit-learn compatible model or Pipeline.
            X_train (pd.DataFrame): Training features used to fit the model.
            task (str): 'regression' or 'classification'.
        """
        self.task = task
        self.X_train = X_train

        if isinstance(model, Pipeline):
            self.pipeline = model
            self.model = model.steps[-1][1]

            preprocessor = model.named_steps.get('preprocessing')
            if preprocessor is not None and hasattr(preprocessor, "get_feature_names_out"):
                self.feature_names = preprocessor.get_feature_names_out()
            else:
                self.feature_names = X_train.columns
        else:
            # ✅ FIX: Handle normal (non-pipeline) models
            self.pipeline = None
            self.model = model
            self.feature_names = X_train.columns

    def feature_importance(self):
        """
        Plot and return feature importances (tree-based models only).

        Returns:
            pd.Series or None: Feature importances sorted ascending, or None if unavailable.
        """
        if hasattr(self.model, "feature_importances_"):
            feature_names = (
                self.feature_names
                if len(self.model.feature_importances_) == len(self.feature_names)
                else [f"feature_{i}" for i in range(len(self.model.feature_importances_))]
            )

            importances = pd.Series(
                self.model.feature_importances_, index=feature_names
            ).sort_values(ascending=True)

            importances.plot(kind="barh", figsize=(8, 6))
            plt.title("Feature Importance")
            plt.show()
            return importances
        else:
            print("⚠️ Feature importances not available for this model.")
            return None

    def coefficients(self, plot=True):
        """
        Plot and return model coefficients (linear models only).
        """
        if hasattr(self.model, "coef_"):
            coefs = self.model.coef_

            # Handle multi-class classification
            if self.task == "classification" and coefs.ndim > 1:
                coefs = np.mean(np.abs(coefs), axis=0)

            feature_names = (
                self.feature_names
                if len(coefs) == len(self.feature_names)
                else [f"feature_{i}" for i in range(len(coefs))]
            )

            coefs_series = pd.Series(coefs, index=feature_names).sort_values()

            if plot:
                coefs_series.plot(kind="barh", figsize=(8, 6))
                plt.title("Model Coefficients")
                plt.show()

            return coefs_series
        else:
            print("⚠️ Coefficients not available for this model.")
            return None


    def shap_summary(self, sample_size=500):
        """
        Plot SHAP summary (works for both regression and classification).

        Args:
            sample_size (int, optional): Number of samples to use for SHAP calculation.

        Notes:
            - Automatically handles pipelines (applies preprocessing before SHAP).
            - For classification, SHAP explains predicted probabilities.
            - Works best with tree-based models, but also supports linear models.

        Returns:
            shap.Explanation or None: SHAP values object for further analysis.
        """
        # ✅ Automatically transform data if pipeline is provided
        if self.pipeline is not None and hasattr(self.pipeline, "named_steps"):
            try:
                preprocessor = self.pipeline.named_steps.get("preprocessing")
                if preprocessor is not None:
                    X_transformed = preprocessor.transform(self.X_train)
                    feature_names = preprocessor.get_feature_names_out()
                    X_transformed = pd.DataFrame(X_transformed, columns=feature_names)
                else:
                    X_transformed = self.X_train
            except Exception as e:
                print(f"⚠️ Failed to transform data with pipeline preprocessing: {e}")
                X_transformed = self.X_train
        else:
            X_transformed = self.X_train

        # ✅ Take sample for SHAP
        X_sample = X_transformed.sample(min(sample_size, len(X_transformed)), random_state=42)

        try:
            explainer = shap.Explainer(self.model, X_sample)
            shap_values = explainer(X_sample)
            shap.summary_plot(shap_values, X_sample)
            return shap_values
        except Exception as e:
            print(f"⚠️ SHAP interpretation failed: {e}")
            return None
