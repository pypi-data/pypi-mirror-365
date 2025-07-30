import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

from statsmodels.tools.tools import add_constant
from statsmodels.stats.outliers_influence import variance_inflation_factor

from sklearn.impute import SimpleImputer

class DataExplorer:
    def __init__(self, df, target_col):
        self.df = df
        self.target_col = target_col
        self.task_type = 'classification' if self.df[target_col].nunique() <= 10 else 'regression'

    def summary(self):
        print("Dataset Shape:", self.df.shape)
        print("\n data types:\n", self.df.dtypes)
        print("\n Missing Values:\n", self.df.isnull().sum().sort_values(ascending=False))
        display(self.df.head())

    def plot_target(self):
        if self.task_type == 'regression':
            sns.histplot(self.df[self.target_col], kde=True)
        else:
            self.df[self.target_col].value_counts().plot(kind='bar')
        plt.title(f"Target Distribution: {self.target_col}")
        plt.show()

    def get_imputed_numeric_df(self):
        """Returns median-imputed numeric-only DataFrame for EDA/VIF."""
        X = self.df.drop(columns=[self.target_col], errors='ignore')
        X_numeric = X.select_dtypes(include=np.number)
        imputer = SimpleImputer(strategy='median')
        X_imputed = pd.DataFrame(imputer.fit_transform(X_numeric), columns=X_numeric.columns)
        return X_imputed


    #Need to add categorical visualizations






    def correlation_heatmap(self, exclude_cols=None):
        data = self.df.drop(columns=exclude_cols, errors='ignore') if exclude_cols else self.df
        corr = data.select_dtypes(include='number').corr()
        sns.heatmap(
            corr,
            annot=True,
            fmt=".3f",              # Round to 3 decimal places
            cmap='coolwarm',
            annot_kws={"size": 8}   # Make text smaller
        )
        plt.title("Correlation Heatmap")
        plt.show()

    def calculate_vif(self):
        X_imputed = self.get_imputed_numeric_df()
        X_imputed = add_constant(X_imputed)

        vif = pd.DataFrame()
        vif["Feature"] = X_imputed.columns
        vif["VIF"] = [variance_inflation_factor(X_imputed.values, i) for i in range(X_imputed.shape[1])]
        return vif[vif["Feature"] != "const"]
