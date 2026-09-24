"""Feature extraction for radar (DFSAR) and optical (OHRC) inputs.

Wraps the preprocessing helpers into a small reusable class so notebooks and the
training script can request a consistent feature matrix.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd

from . import preprocessing as pp


@dataclass
class FeatureExtractor:
    """Builds model-ready feature matrices from raw lunar datasets."""

    feature_names: List[str] = field(
        default_factory=lambda: pp.RADAR_FEATURES + pp.TERRAIN_FEATURES
    )

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return the engineered feature frame restricted to known features."""
        feats = pp.engineer_features(df)
        available = [c for c in self.feature_names if c in feats.columns]
        return feats[available]

    def transform_labels(self, df: pd.DataFrame) -> np.ndarray:
        return pp.make_labels(df)

    def image_features(self, image: np.ndarray) -> np.ndarray:
        """Extract simple statistical descriptors from an OHRC grayscale tile.

        Returns ``[mean, std, p25, p75, edge_density]`` which the terrain model
        can use as a compact texture fingerprint.
        """
        image = np.asarray(image, dtype=np.float64)
        gx = np.abs(np.gradient(image, axis=0))
        gy = np.abs(np.gradient(image, axis=1))
        edges = np.hypot(gx, gy)
        return np.array([
            float(np.mean(image)),
            float(np.std(image)),
            float(np.percentile(image, 25)),
            float(np.percentile(image, 75)),
            float(np.mean(edges)),
        ])
