import os, sys
from lib.ml.base import BaseTransformer



class VlibSimpleImputer(BaseTransformer):
    def __init__(self, strategy="mean", columns=None):
        super().__init__(columns)
        self.strategy = strategy

    def fit(self, X, y=None, override_cols=None):
        cols = self._get_columns(X, override_cols)
        self.fill_values = {}
        for col in cols:
            if self.strategy == "mean":
                self.fill_values[col] = X[col].mean()
            elif self.strategy == "median":
                self.fill_values[col] = X[col].median()
            else:
                self.fill_values[col] = X[col].mode()[0]
        return self

    def transform(self, X, override_cols=None):
        X = X.copy()
        cols = self._get_columns(X, override_cols)
        for col in cols:
            X[col] = X[col].fillna(self.fill_values[col])
        return X[cols]  # ✅ return only processed columns

    def get_feature_names(self, input_cols):
        return input_cols