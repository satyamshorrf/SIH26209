"""Training entrypoint for the lunar ML pipeline.

Run with::

    python -m ml_pipeline.models.training \
        --data ml_pipeline/datasets/sample_dfsar.csv \
        --out ml_pipeline/models/artifacts

Trains the ice and terrain classifiers, prints evaluation metrics and persists
the fitted models with joblib.
"""

from __future__ import annotations

import argparse
import os

import pandas as pd

from .confidence_model import ConfidenceModel
from .ice_classifier import IceClassifier
from .terrain_classifier import TerrainClassifier


def train(data_path: str, out_dir: str) -> None:
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training data not found: {data_path}")
    df = pd.read_csv(data_path)
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loaded {len(df)} rows from {data_path}")

    print("\n== Training IceClassifier ==")
    ice = IceClassifier().fit(df)
    print("Ice metrics:", ice.evaluate(df))
    print("Feature importance:", ice.feature_importance())
    ice.save(os.path.join(out_dir, "ice_classifier.joblib"))

    print("\n== Training TerrainClassifier ==")
    terrain = TerrainClassifier().fit(df)
    print("Terrain metrics:", terrain.evaluate(df))
    terrain.save(os.path.join(out_dir, "terrain_classifier.joblib"))

    print("\n== Mission Confidence Evaluation ==")
    report = ConfidenceModel().evaluate(df)
    for key, value in report.items():
        if key not in ("confusion_matrix", "feature_importance"):
            print(f"  {key}: {value}")

    print(f"\nArtifacts saved to: {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train lunar ice/terrain models")
    parser.add_argument(
        "--data",
        default=os.path.join(os.path.dirname(__file__), "..", "datasets",
                             "sample_dfsar.csv"),
        help="Path to the training CSV.",
    )
    parser.add_argument(
        "--out",
        default=os.path.join(os.path.dirname(__file__), "artifacts"),
        help="Directory to write fitted model artefacts.",
    )
    args = parser.parse_args()
    train(os.path.abspath(args.data), os.path.abspath(args.out))


if __name__ == "__main__":
    main()
