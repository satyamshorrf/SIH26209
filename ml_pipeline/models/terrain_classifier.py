"""Terrain safety classifier.

Classifies each location into one of three landing categories - ``Safe``,
``Risk`` or ``Unsafe`` - from slope, roughness and illumination using a gradient
boosting model.  Labels for training are generated with the same weighted
multi-criteria rule the backend uses, giving a self-consistent target.
"""

from __future__ import annotations

import os
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score

from . import preprocessing as pp

CLASSES = ["Unsafe", "Risk", "Safe"]


def _terrain_features(df: pd.DataFrame) -> pd.DataFrame:
    feats = pp.engineer_features(df)
    keep = [c for c in ["Slope", "Roughness", "Illumination", "Texture"]
            if c in feats.columns]
    return feats[keep]


def _terrain_labels(df: pd.DataFrame) -> np.ndarray:
    """Generate Safe/Risk/Unsafe labels via a weighted suitability score."""
    feats = pp.engineer_features(df)
    slope = pp.normalise(feats["Slope"].to_numpy())
    rough = feats["Roughness"].to_numpy()
    illum = feats["Illumination"].to_numpy()
    lsi = 0.45 * (1 - slope) + 0.30 * (1 - rough) + 0.25 * illum
    labels = np.where(lsi >= 0.70, 2, np.where(lsi >= 0.45, 1, 0))
    return labels.astype(int)


class TerrainClassifier:
    """Three-class terrain safety model for landing-site selection."""

    def __init__(self, random_state: int = 42):
        self.model = GradientBoostingClassifier(random_state=random_state)
        self.feature_names: List[str] = []
        self.fitted = False

    def fit(self, df: pd.DataFrame) -> "TerrainClassifier":
        X = _terrain_features(df)
        y = _terrain_labels(df)
        if len(np.unique(y)) < 2:
            y = (X.iloc[:, 0].to_numpy()
                 >= np.median(X.iloc[:, 0].to_numpy())).astype(int)
        self.feature_names = list(X.columns)
        self.model.fit(X.to_numpy(), y)
        self.fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if not self.fitted:
            raise RuntimeError("TerrainClassifier must be fitted before use.")
        X = _terrain_features(df)[self.feature_names].to_numpy()
        return self.model.predict(X)

    def predict_labels(self, df: pd.DataFrame) -> List[str]:
        return [CLASSES[int(min(p, len(CLASSES) - 1))] for p in self.predict(df)]

    def evaluate(self, df: pd.DataFrame) -> Dict[str, float]:
        y = _terrain_labels(df)
        preds = self.predict(df)
        return {"accuracy": float(accuracy_score(y, preds))}

    def save(self, path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        joblib.dump(
            {"model": self.model, "feature_names": self.feature_names}, path
        )
        return path

    @classmethod
    def load(cls, path: str) -> "TerrainClassifier":
        payload = joblib.load(path)
        obj = cls()
        obj.model = payload["model"]
        obj.feature_names = payload["feature_names"]
        obj.fitted = True
        return obj
