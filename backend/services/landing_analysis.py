"""Safe landing site analysis.

Combines the terrain metrics into a single Landing Suitability Index (LSI) using
a weighted multi-criteria decision model, then classifies each candidate into
Safe / Risk / Unsafe zones and identifies the optimal touchdown coordinate.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from . import terrain as terrain_mod

# Weights for the multi-criteria suitability model.  They sum to 1.0.
WEIGHTS = {
    "slope": 0.30,
    "roughness": 0.20,
    "crater": 0.20,
    "boulder": 0.15,
    "illumination": 0.15,
}

SAFE_THRESHOLD = 0.70
RISK_THRESHOLD = 0.45


def _normalise(arr: np.ndarray) -> np.ndarray:
    lo = float(np.nanmin(arr))
    hi = float(np.nanmax(arr))
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def landing_suitability(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the Landing Suitability Index and zone label per candidate."""
    terrain = terrain_mod.terrain_features(df)

    # Convert each metric into a "goodness" score in [0,1] (higher = safer).
    slope_score = 1.0 - _normalise(terrain["Slope"].to_numpy())
    rough_score = 1.0 - terrain["Roughness"].to_numpy()
    crater_score = terrain["CraterDistance"].to_numpy()
    boulder_score = 1.0 - terrain["BoulderDensity"].to_numpy()
    illum_score = terrain["Illumination"].to_numpy()

    lsi = (
        WEIGHTS["slope"] * slope_score
        + WEIGHTS["roughness"] * rough_score
        + WEIGHTS["crater"] * crater_score
        + WEIGHTS["boulder"] * boulder_score
        + WEIGHTS["illumination"] * illum_score
    )
    lsi = np.clip(lsi, 0.0, 1.0)

    zones = np.where(
        lsi >= SAFE_THRESHOLD,
        "Safe",
        np.where(lsi >= RISK_THRESHOLD, "Risk", "Unsafe"),
    )

    out = terrain.copy()
    out["LSI"] = lsi
    out["SafetyPercent"] = np.round(lsi * 100.0, 2)
    out["Zone"] = zones
    return out


def best_landing_site(scored: pd.DataFrame) -> Dict[str, float]:
    """Return the highest-scoring candidate as the recommended landing site."""
    idx = int(scored["LSI"].to_numpy().argmax())
    row = scored.iloc[idx]
    site = {
        "lsi": float(row["LSI"]),
        "safety_percent": float(row["SafetyPercent"]),
        "zone": str(row["Zone"]),
        "slope": float(row.get("Slope", 0.0)),
        "illumination": float(row.get("Illumination", 0.0)),
    }
    if "Latitude" in scored.columns:
        site["latitude"] = float(row["Latitude"])
    if "Longitude" in scored.columns:
        site["longitude"] = float(row["Longitude"])
    return site


def landing_summary(scored: pd.DataFrame) -> Dict[str, object]:
    counts = scored["Zone"].value_counts().to_dict()
    total = int(len(scored))
    return {
        "total_candidates": total,
        "safe_zones": int(counts.get("Safe", 0)),
        "risk_zones": int(counts.get("Risk", 0)),
        "unsafe_zones": int(counts.get("Unsafe", 0)),
        "safe_fraction": float(counts.get("Safe", 0) / total) if total else 0.0,
        "mean_safety_percent": float(scored["SafetyPercent"].mean()),
        "best_site": best_landing_site(scored),
    }
