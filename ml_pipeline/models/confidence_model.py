"""Mission confidence model.

Wraps the ice classifier with a full evaluation harness (train/test split + ROC,
AUC, confusion matrix and an aggregated mission-confidence score) used to report
how much trust to place in the autonomous detections.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from .feature_extractor import FeatureExtractor
from .ice_classifier import IceClassifier


class ConfidenceModel:
    """Evaluates detection reliability and produces a mission confidence score."""

    def __init__(self):
        self.extractor = FeatureExtractor()

    def evaluate(self, df: pd.DataFrame) -> Dict[str, object]:
        X = self.extractor.transform(df)
        y = self.extractor.transform_labels(df)
        if len(np.unique(y)) < 2:
            score = X.iloc[:, 0].to_numpy()
            y = (score >= np.percentile(score, 80)).astype(int)

        idx = np.arange(len(df))
        train_idx, test_idx = train_test_split(
            idx, test_size=0.3, random_state=42, stratify=y
        )
        clf = IceClassifier().fit(df.iloc[train_idx].reset_index(drop=True))

        test_df = df.iloc[test_idx].reset_index(drop=True)
        proba = clf.predict_proba(test_df)
        preds = clf.predict(test_df)
        y_test = y[test_idx]

        try:
            auc = float(roc_auc_score(y_test, proba))
        except ValueError:
            auc = 0.0

        accuracy = float(accuracy_score(y_test, preds))
        precision = float(precision_score(y_test, preds, zero_division=0))
        recall = float(recall_score(y_test, preds, zero_division=0))
        f1 = float(f1_score(y_test, preds, zero_division=0))
        mean_conf = float(np.mean(np.maximum(proba, 1 - proba)))

        mission_confidence = round(
            100.0 * (0.3 * accuracy + 0.2 * f1 + 0.2 * auc +
                     0.2 * mean_conf + 0.1 * recall), 2
        )

        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "mean_prediction_confidence": round(mean_conf, 4),
            "mission_confidence_percent": mission_confidence,
            "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
            "feature_importance": clf.feature_importance(),
        }
