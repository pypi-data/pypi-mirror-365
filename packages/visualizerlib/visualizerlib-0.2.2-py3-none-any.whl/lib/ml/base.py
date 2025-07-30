import numpy as np
import pandas as pd
from lib.ml.chain.pipeline import VlibPipeline

class BaseTransformer:
    def __init__(self, columns=None):
        self.columns = columns

    def fit(self, X, y=None, override_cols=None):
        return self

    def transform(self, X, override_cols=None):
        return X

    def fit_transform(self, X, y=None, override_cols=None):
        return self.fit(X, y, override_cols).transform(X, override_cols)

    def _get_columns(self, X, override_cols):
        if self.columns is not None:
            return self.columns
        elif override_cols is not None:
            return override_cols
        else:
            return list(X.columns)

    def get_feature_names(self, input_cols):
        return input_cols

    def __or__(self, other):
        if isinstance(other, VlibPipeline):
            return VlibPipeline([self] + other.steps)
        else:
            return VlibPipeline([self, other])
