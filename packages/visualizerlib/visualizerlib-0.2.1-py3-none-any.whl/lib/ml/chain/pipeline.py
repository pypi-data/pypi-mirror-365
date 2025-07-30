import os,sys

class VlibPipeline:
    def __init__(self, steps, output="numpy"):
        self.steps = steps
        self.output = output

    def fit(self, X, y=None, override_cols=None):
        self.input_columns = list(X.columns)
        for step in self.steps:
            X = step.fit_transform(X, y, override_cols=override_cols)
        self.output_columns = self.get_feature_names(
            self.input_columns if override_cols is None else override_cols
        )
        return self

    def transform(self, X, override_cols=None):
        for step in self.steps:
            X = step.transform(X, override_cols=override_cols)
        if self.output == "pandas":
            return X
        else:
            return X.values

    def fit_transform(self, X, y=None, override_cols=None):
        self.fit(X, y, override_cols)
        return self.transform(X, override_cols)

    def __or__(self, other):
        if isinstance(other, VlibPipeline):
            return VlibPipeline(self.steps + other.steps, output=self.output)
        else:
            return VlibPipeline(self.steps + [other], output=self.output)

    def get_feature_names(self, input_cols):
        cols = input_cols
        for step in self.steps:
            cols = step.get_feature_names(cols)
        return cols
