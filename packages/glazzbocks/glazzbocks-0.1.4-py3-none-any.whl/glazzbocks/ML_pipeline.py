# === Required Imports ===
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score
)
from sklearn.metrics import (roc_curve, precision_recall_curve, auc, roc_auc_score, 
RocCurveDisplay, PrecisionRecallDisplay, confusion_matrix, ConfusionMatrixDisplay)

from sklearn.model_selection import cross_validate, KFold
from sklearn.base import is_classifier

# === MLPipeline Class ===
class MLPipeline:
    """
    A machine learning pipeline for regression and classification tasks.

    This class automates:
        - Data splitting (train/test)
        - Feature preprocessing (numeric scaling, categorical encoding)
        - Model training and prediction
        - Cross-validation (regression & classification)
        - Evaluation and diagnostic visualization

    Attributes:
        model: The ML model (default: LinearRegression).
        pipeline: Full scikit-learn Pipeline (preprocessing + model).
        numeric_cols (list): List of detected numeric column names.
        categorical_cols (list): List of detected categorical column names.
    """
    def __init__(self, model=None):
        self.model = model if model else LinearRegression()
        self.pipeline = None
        self.numeric_cols = []
        self.categorical_cols = []

    def set_model(self, model):
        """
        Set the ML model directly as an initialized scikit-learn instance.
        """
        self.model = model
        self.pipeline = None
        print(f"Model set to: {self.model}")


    def split_data(self, df, target_col, test_size=0.2, random_state=42):
        X = df.drop(columns=[target_col])
        y = df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        return X_train, X_test, y_train, y_test 

    def build_pipeline(self, X):
        """
        Build a preprocessing and modeling pipeline based on the input features.

        Args:
            X (pd.DataFrame): Input feature dataset used to determine numeric and 
                            categorical columns.

        Raises:
            ValueError: If no numeric or categorical columns are detected in `X`.

        Notes:
            - Automatically detects numeric and categorical columns:
                * Numeric columns: dtype `number` (int or float).
                * Categorical columns: dtype `object` (string-based).
            - For numeric features:
                * Missing values are imputed using the median.
                * Features are standardized using StandardScaler.
            - For categorical features:
                * Missing values are imputed with the most frequent value.
                * Features are one-hot encoded (unknown categories ignored at prediction time).
            - The final pipeline is stored in `self.pipeline` as:
                Pipeline([
                    ('preprocessing', ColumnTransformer),
                    ('model', self.model)
                ])
            - Call this method before `fit()` if the pipeline is not already built.
        """
        # Select only non-null column names
        self.numeric_cols = [col for col in X.select_dtypes(include='number').columns if col is not None]
        self.categorical_cols = [col for col in X.select_dtypes(include='object').columns if col is not None]

        numeric_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        transformers = []

        if self.numeric_cols:
            transformers.append(('num', numeric_pipeline, self.numeric_cols))

        if self.categorical_cols:
            categorical_pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(handle_unknown='ignore'))
            ])
            transformers.append(('cat', categorical_pipeline, self.categorical_cols))

        if not transformers:
            raise ValueError("No columns to transform. Check your input data.")

        preprocessor = ColumnTransformer(transformers)

        self.pipeline = Pipeline([
            ('preprocessing', preprocessor),
            ('model', self.model)
        ])

    def cross_validate(self, X_train, y_train):
        """
        Perform cross-validation for regression or classification tasks.

        Args:
            X_train (pd.DataFrame or np.ndarray): Training feature set.
            y_train (pd.Series or np.ndarray): Training target values.

        Returns:
            dict: A dictionary containing cross-validation results.

                - **For regression:**
                    {
                        'metrics': pd.DataFrame with per-fold metrics
                            (mse, rmse, mae, r2),
                        'roc_data': None,
                        'f1_threshold_data': None,
                        'X_test_folds': None,
                        'y_test_folds': None
                    }

                - **For classification:**
                    {
                        'metrics': pd.DataFrame with per-fold metrics
                            (accuracy, precision, recall, f1),
                        'roc_data': dict of {fold: {'fpr', 'tpr', 'thresholds'}},
                        'f1_threshold_data': pd.DataFrame with optimal thresholds and F1 scores,
                        'X_test_folds': dict of held-out test features per fold,
                        'y_test_folds': dict of held-out test targets per fold
                    }

        Raises:
            ValueError: If the pipeline is not built and no features are available.

        Notes:
            - Uses 10-fold cross-validation (KFold, shuffle=True, random_state=42).
            - For regression, negative error metrics are converted to positive values.
            - For classification, ROC and Precision-Recall thresholds are computed
            per fold, storing optimal F1-maximizing thresholds.
            - Pipelines are automatically built if not already initialized.
            - Ensure the model supports `predict_proba()` for ROC and F1 threshold plots.
        """
        if self.pipeline is None:
            self.build_pipeline(X_train)
        
        model = self.pipeline.steps[-1][1]
        is_classification = is_classifier(model)

        # === REGRESSION ===
        if not is_classification:
            scoring = {
                'neg_mean_squared_error': 'neg_mean_squared_error',
                'neg_mean_absolute_error': 'neg_mean_absolute_error',
                'r2': 'r2'
            }

            cv = KFold(n_splits=10, shuffle=True, random_state=42)
            cv_results = cross_validate(
                self.pipeline, X_train, y_train,
                cv=cv, scoring=scoring, return_train_score=False
            )

            fold_results = {
                f'fold_{i}': {
                    'mse': -cv_results['test_neg_mean_squared_error'][i],
                    'rmse': np.sqrt(-cv_results['test_neg_mean_squared_error'][i]),
                    'mae': -cv_results['test_neg_mean_absolute_error'][i],
                    'r2': cv_results['test_r2'][i]
                }
                for i in range(10)
            }

            metrics_df = pd.DataFrame(fold_results).T
            metrics_df.index.name = 'fold'

            print("\n=== Cross-Validation Metrics (Regression) ===")
            print(metrics_df)
            print("\nAverage Metrics Across Folds:")
            print(metrics_df.mean())

            return {
                'metrics': metrics_df,
                'roc_data': None,
                'f1_threshold_data': None,
                'X_test_folds': None,
                'y_test_folds': None
            }

        # === CLASSIFICATION ===
        scoring = {
            'accuracy': 'accuracy',
            'precision': 'precision_weighted',
            'recall': 'recall_weighted',
            'f1': 'f1_weighted'
        }

        cv = KFold(n_splits=10, shuffle=True, random_state=42)
        cv_results = cross_validate(
            self.pipeline, X_train, y_train,
            cv=cv, scoring=scoring, return_train_score=False, return_estimator=True
        )

        fold_results = {}
        roc_data = {}
        f1_threshold_data = {}
        X_test_folds = {}
        y_test_folds = {}

        for fold, (train_idx, test_idx) in enumerate(cv.split(X_train, y_train)):
            X_test_fold = X_train.iloc[test_idx] if isinstance(X_train, pd.DataFrame) else X_train[test_idx]
            y_test_fold = y_train.iloc[test_idx] if isinstance(y_train, pd.Series) else y_train[test_idx]

            X_test_folds[f'fold_{fold}'] = X_test_fold
            y_test_folds[f'fold_{fold}'] = y_test_fold

            estimator = cv_results['estimator'][fold]
            y_prob = estimator.predict_proba(X_test_fold)[:, 1]

            fpr, tpr, roc_thresholds = roc_curve(y_test_fold, y_prob)
            roc_data[f'fold_{fold}'] = {'fpr': fpr, 'tpr': tpr, 'thresholds': roc_thresholds}

            precision, recall, thresholds = precision_recall_curve(y_test_fold, y_prob)
            f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
            optimal_idx = np.argmax(f1_scores)
            f1_threshold_data[f'fold_{fold}'] = {
                'threshold': thresholds[optimal_idx],
                'f1': f1_scores[optimal_idx]
            }

            fold_results[f'fold_{fold}'] = {
                'accuracy': cv_results['test_accuracy'][fold],
                'precision': cv_results['test_precision'][fold],
                'recall': cv_results['test_recall'][fold],
                'f1': cv_results['test_f1'][fold]
            }

        metrics_df = pd.DataFrame(fold_results).T
        metrics_df.index.name = 'fold'

        print("\n=== Cross-Validation Metrics (Classification) ===")
        print(metrics_df)
        print("\nAverage Metrics Across Folds:")
        print(metrics_df.mean())

        return {
            'metrics': metrics_df,
            'roc_data': roc_data,
            'f1_threshold_data': pd.DataFrame(f1_threshold_data).T,
            'X_test_folds': X_test_folds,
            'y_test_folds': y_test_folds
        }

    def plot_roc_curve(self, X_test, y_test):
        """
        Plot ROC (Receiver Operating Characteristic) curve on the hold-out test set.

        Args:
            X_test (array-like or pd.DataFrame): Test feature set.
            y_test (array-like or pd.Series): True binary class labels for the test set.

        Raises:
            ValueError: If the pipeline is not fitted or the model is not a classifier.

        Notes:
            - This method uses the predicted probabilities (positive class) to plot the ROC curve.
            - The Area Under the Curve (AUC) score is displayed in the plot title.
            - Standard practice: ROC curve is computed on the hold-out test set, 
            not during cross-validation.

        Example:
            >>> pipeline.plot_roc_curve(X_test, y_test)
        """
        if not hasattr(self, 'pipeline') or self.pipeline is None or not is_classifier(self.pipeline.steps[-1][1]):
            raise ValueError("This method is only for classification tasks with a fitted pipeline.")

        y_prob = self.pipeline.predict_proba(X_test)[:, 1]
        auc_score = roc_auc_score(y_test, y_prob)

        RocCurveDisplay.from_predictions(y_test, y_prob)
        plt.title(f'ROC Curve - Test Set (AUC = {auc_score:.2f})')
        plt.show()

    def plot_f1_threshold(self, X_test, y_test):
        """
        Plot F1 score vs decision threshold on the hold-out test set.

        Args:
            X_test (array-like or pd.DataFrame): Test feature set.
            y_test (array-like or pd.Series): True binary class labels for the test set.

        Raises:
            ValueError: If the pipeline is not fitted or the model is not a classifier.

        Notes:
            - F1 scores are computed for different probability thresholds using the precision-recall curve.
            - The optimal threshold (maximizing F1 score) is marked with a red dot.
            - Standard practice: This plot is generated on the hold-out test set 
            after the final model is trained.

        Example:
            >>> pipeline.plot_f1_threshold(X_test, y_test)
        """
        if not hasattr(self, 'pipeline') or self.pipeline is None or not is_classifier(self.pipeline.steps[-1][1]):
            raise ValueError("This method is only for classification tasks with a fitted pipeline.")

        y_prob = self.pipeline.predict_proba(X_test)[:, 1]

        precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
        optimal_idx = np.argmax(f1_scores)

        plt.figure(figsize=(8, 6))
        plt.plot(thresholds, f1_scores[:-1], label='F1 Score')
        plt.plot(thresholds[optimal_idx], f1_scores[optimal_idx], 'ro',
                label=f'Optimal Threshold = {thresholds[optimal_idx]:.2f} (F1={f1_scores[optimal_idx]:.2f})')
        plt.xlabel('Threshold')
        plt.ylabel('F1 Score')
        plt.title('F1 Score vs Threshold - Test Set')
        plt.legend()
        plt.show()

    def plot_confusion_matrix(self, X_test, y_test, normalize='true'):
        """
        Plot confusion matrix for classification on the hold-out test set.

        Args:
            X_test: Test features.
            y_test: True labels.
            normalize: 'true' (default) shows percentages; set to None for raw counts.

        Raises:
            ValueError: If the pipeline is not fitted or the model is not a classifier.
        """
        if not hasattr(self, 'pipeline') or self.pipeline is None or not is_classifier(self.pipeline.steps[-1][1]):
            raise ValueError("This method is only for classification tasks with a fitted pipeline.")

        y_pred = self.pipeline.predict(X_test)

        cm = confusion_matrix(y_test, y_pred, normalize=normalize)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot(cmap='Blues', values_format='.2f' if normalize else 'd')

        plt.title('Confusion Matrix - Test Set')
        plt.show()
        
    def plot_predicted_vs_actual(self, X_test, y_test):
        """Plot predicted vs. actual values for regression on the test set.
        
        Args:
            X_test: Test features.
            y_test: True test labels.
        
        Raises:
            ValueError: If the pipeline is not fitted or the model is a classifier.
        
        Notes:
            - Plots predicted values (from pipeline.predict) against actual values.
            - Includes a 45-degree line for reference.
        """
        if not hasattr(self, 'pipeline') or self.pipeline is None or is_classifier(self.pipeline.steps[-1][1]):
            raise ValueError("This method is only for regression tasks with a fitted pipeline.")
        
        y_pred_test = self.pipeline.predict(X_test)
        
        plt.figure(figsize=(8, 6))
        plt.scatter(y_test, y_pred_test, alpha=0.5, color='#1f77b4')
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, label='Perfect Prediction')
        plt.xlabel('Actual Values')
        plt.ylabel('Predicted Values')
        plt.title('Predicted vs. Actual Values - Test Set')
        plt.legend()
        plt.grid(False)

    def plot_residuals(self, X_test, y_test):
        """Plot residuals vs. predicted values for regression on the test set.
        
        Args:
            X_test: Test features.
            y_test: True test labels.
        
        Raises:
            ValueError: If the pipeline is not fitted or the model is a classifier.
        
        Notes:
            - Residuals are (actual - predicted) values.
            - Helps identify patterns (e.g., heteroscedasticity) or bias.
        """
        if not hasattr(self, 'pipeline') or self.pipeline is None or is_classifier(self.pipeline.steps[-1][1]):
            raise ValueError("This method is only for regression tasks with a fitted pipeline.")
        
        y_pred_test = self.pipeline.predict(X_test)
        residuals = y_test - y_pred_test
        
        plt.figure(figsize=(8, 6))
        plt.scatter(y_pred_test, residuals, alpha=0.5, color='#ff7f0e')
        plt.axhline(y=0, color='r', linestyle='--', lw=2, label='Zero Residual')
        plt.xlabel('Predicted Values')
        plt.ylabel('Residuals')
        plt.title('Residuals vs. Predicted Values - Test Set')
        plt.legend()
        plt.grid(False)

    def plot_error_distribution(self, X_test, y_test):
        """Plot histogram of residuals for regression on the test set.
        
        Args:
            X_test: Test features.
            y_test: True test labels.
        
        Raises:
            ValueError: If the pipeline is not fitted or the model is a classifier.
        
        Notes:
            - Shows the distribution of residuals to assess normality and error spread.
        """
        if not hasattr(self, 'pipeline') or self.pipeline is None or is_classifier(self.pipeline.steps[-1][1]):
            raise ValueError("This method is only for regression tasks with a fitted pipeline.")
        
        y_pred_test = self.pipeline.predict(X_test)
        residuals = y_test - y_pred_test
        
        plt.figure(figsize=(8, 6))
        plt.hist(residuals, bins=30, color='#2ca02c', alpha=0.7)
        plt.xlabel('Residuals')
        plt.ylabel('Frequency')
        plt.title('Residuals Distribution - Test Set')
        plt.grid(False)

    
    def fit(self, X_train, y_train):
        self.build_pipeline(X_train)
        self.pipeline.fit(X_train, y_train)

        return self.pipeline

    def predict(self, X):
        return self.pipeline.predict(X)

    def evaluate(self, y_true, y_pred, task=None, verbose=True):
        """
        Evaluate model performance for regression or classification tasks.

        Args:
            y_true (array-like): True target values.
            y_pred (array-like): Predicted values from the model.
            task (str, optional): 'regression' or 'classification'. If None, inferred from model.
            verbose (bool): Whether to print metrics.

        Returns:
            dict: Evaluation metrics.
        """
        if task is None:
            if is_classifier(self.model):
                task = 'classification'
            else:
                task = 'regression'

        if task == 'regression':
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            if verbose:
                print("=== Regression Evaluation ===")
                print(f"RMSE: {rmse:.2f}")
                print(f"MAE:  {mae:.2f}")
                print(f"R²:   {r2:.3f}")
            return {'rmse': rmse, 'mae': mae, 'r2': r2}
        
        elif task == 'classification':
            acc = accuracy_score(y_true, y_pred)
            prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            rec = recall_score(y_true, y_pred, average='weighted')
            f1 = f1_score(y_true, y_pred, average='weighted')
            if verbose:
                print("=== Classification Evaluation ===")
                print(f"Accuracy:  {acc:.2f}")
                print(f"Precision: {prec:.2f}")
                print(f"Recall:    {rec:.2f}")
                print(f"F1 Score:  {f1:.2f}")
            return {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1}
        
        else:
            raise ValueError("Invalid task. Use 'regression' or 'classification'.")

