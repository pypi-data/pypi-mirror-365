import pandas as pd
import numpy as np
import os, sys
from lib.ml.base import BaseTransformer



class VlibStandardScaler(BaseTransformer):
    def fit(self, X, y=None, override_cols=None):
        cols = self._get_columns(X, override_cols)
        self.means = X[cols].mean()
        self.stds = X[cols].std(ddof=0)
        self.cols = cols
        return self

    def transform(self, X, override_cols=None):
        X = X.copy()
        cols = self._get_columns(X, override_cols)
        X_scaled = (X[cols] - self.means) / self.stds
        return X_scaled  # ✅ return only scaled columns

    def get_feature_names(self, input_cols):
        return input_cols


class VlibOneHotEncoder(BaseTransformer):
    def fit(self, X, y=None, override_cols=None):
        cols = self._get_columns(X, override_cols)
        self.categories_ = {}
        for col in cols:
            self.categories_[col] = list(pd.Series(X[col]).dropna().unique())
        return self

    def transform(self, X, override_cols=None):
        cols = self._get_columns(X, override_cols)
        new_data = pd.DataFrame(index=X.index)
        for col in cols:
            for cat in self.categories_[col]:
                new_data[f"{col}_{cat}"] = (X[col] == cat).astype(int)
        return new_data  # ✅ returns only encoded columns

    def get_feature_names(self, input_cols):
        names = []
        for col in input_cols:
            for cat in self.categories_[col]:
                names.append(f"{col}_{cat}")
        return names


class VlibOrdinalEncoder(BaseTransformer):
    def fit(self, X, y=None, override_cols=None):
        cols = self._get_columns(X, override_cols)
        self.category_mapping = {}
        for col in cols:
            unique_vals = list(pd.Series(X[col]).dropna().unique())
            self.category_mapping[col] = {cat: idx for idx, cat in enumerate(unique_vals)}
        return self

    def transform(self, X, override_cols=None):
        cols = self._get_columns(X, override_cols)
        encoded = pd.DataFrame(index=X.index)
        for col in cols:
            encoded[col] = X[col].map(self.category_mapping[col]).fillna(-1).astype(int)
        return encoded  # ✅ only encoded columns

    def get_feature_names(self, input_cols):
        return input_cols


class VlibLabelEncoder:
    def fit(self, y):
        self.classes_ = np.unique(y)
        self.class_to_int = {cls: idx for idx, cls in enumerate(self.classes_)}
        self.int_to_class = {idx: cls for cls, idx in self.class_to_int.items()}
        return self

    def transform(self, y):
        return np.array([self.class_to_int[val] for val in y])

    def inverse_transform(self, y_int):
        return np.array([self.int_to_class[val] for val in y_int])

    def fit_transform(self, y):
        return self.fit(y).transform(y)