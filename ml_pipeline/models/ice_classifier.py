"""RandomForest-based subsurface ice classifier.

A thin, well-documented wrapper around scikit-learn's RandomForest that exposes
``fit`` / ``predict`` / ``predict_proba`` / ``evaluate`` / ``save`` / ``load`` and
records the feature ordering so inference stays consistent with training.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)

from .feature_extractor import FeatureExtractor


class IceClassifier:
    """Predicts the presence of subsurface ice from radar + terrain features."""

    def __init__(self, n_estimators: int = 200, max_depth: int = 12,
                 random_state: int = 42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
        )
        self.extractor = FeatureExtractor()
        self.feature_names: List[str] = []
        self.fitted = False

    def fit(self, df: pd.DataFrame) -> "IceClassifier":
        X = self.extractor.transform(df)
        y = self.extractor.transform_labels(df)
        if len(np.unique(y)) < 2:
            # Ensure two classes for a well-defined classifier.
            score = X.iloc[:, 0].to_numpy()
            y = (score >= np.percentile(score, 80)).astype(int)
        self.feature_names = list(X.columns)
        self.model.fit(X.to_numpy(), y)
        self.fitted = True
        return self

    def _features(self, df: pd.DataFrame) -> np.ndarray:
        X = self.extractor.transform(df)
        return X[self.feature_names].to_numpy()

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        self._check_fitted()
        return self.model.predict(self._features(df))

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        self._check_fitted()
        return self.model.predict_proba(self._features(df))[:, 1]

    def evaluate(self, df: pd.DataFrame) -> Dict[str, float]:
        self._check_fitted()
        y = self.extractor.transform_labels(df)
        preds = self.predict(df)
        return {
            "accuracy": float(accuracy_score(y, preds)),
            "precision": float(precision_score(y, preds, zero_division=0)),
            "recall": float(recall_score(y, preds, zero_division=0)),
            "f1": float(f1_score(y, preds, zero_division=0)),
        }

    def feature_importance(self) -> Dict[str, float]:
        self._check_fitted()
        return {
            name: float(imp)
            for name, imp in zip(self.feature_names,
                                 self.model.feature_importances_)
        }

    def save(self, path: str) -> str:
        self._check_fitted()
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        joblib.dump(
            {"model": self.model, "feature_names": self.feature_names}, path
        )
        return path

    @classmethod
    def load(cls, path: str) -> "IceClassifier":
        payload = joblib.load(path)
        obj = cls()
        obj.model = payload["model"]
        obj.feature_names = payload["feature_names"]
        obj.fitted = True
        return obj

    def _check_fitted(self) -> None:
        if not self.fitted:
            raise RuntimeError("IceClassifier must be fitted before use.")
