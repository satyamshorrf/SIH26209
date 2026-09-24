"""Data preprocessing utilities for the lunar ML pipeline.

These helpers are deliberately framework-light (NumPy / pandas / scikit-learn) so
the pipeline trains quickly on CPU and mirrors the feature engineering performed
by the FastAPI backend.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Radar Stokes-derived / terrain features the models consume.
RADAR_FEATURES: List[str] = ["CPR", "DOP", "Backscatter", "Texture"]
TERRAIN_FEATURES: List[str] = ["Slope", "Roughness", "Illumination"]


def normalise(arr: np.ndarray) -> np.ndarray:
    """Min-max normalise an array to [0, 1]."""
    arr = np.asarray(arr, dtype=np.float64)
    lo, hi = float(np.nanmin(arr)), float(np.nanmax(arr))
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def compute_cpr(df: pd.DataFrame) -> np.ndarray:
    """CPR from Stokes parameters or a radar backscatter proxy."""
    cols = {c.lower(): c for c in df.columns}
    if "cpr" in cols:
        return df[cols["cpr"]].to_numpy(dtype=np.float64)
    if "s1" in cols and "s4" in cols:
        s1 = df[cols["s1"]].to_numpy(dtype=np.float64)
        s4 = df[cols["s4"]].to_numpy(dtype=np.float64)
        denom = np.where(np.abs(s1 + s4) < 1e-9, 1e-9, s1 + s4)
        return np.clip((s1 - s4) / denom, 0.0, 5.0)
    if "radar" in cols:
        return 0.2 + normalise(df[cols["radar"]].to_numpy()) * 2.0
    raise ValueError("Need CPR, Stokes (S1,S4) or Radar column for CPR.")


def compute_dop(df: pd.DataFrame) -> np.ndarray:
    """DOP from the full Stokes vector or a radar backscatter proxy."""
    cols = {c.lower(): c for c in df.columns}
    if "dop" in cols:
        return np.clip(df[cols["dop"]].to_numpy(dtype=np.float64), 0.0, 1.0)
    if all(k in cols for k in ("s1", "s2", "s3", "s4")):
        s1 = df[cols["s1"]].to_numpy(dtype=np.float64)
        s2 = df[cols["s2"]].to_numpy(dtype=np.float64)
        s3 = df[cols["s3"]].to_numpy(dtype=np.float64)
        s4 = df[cols["s4"]].to_numpy(dtype=np.float64)
        s1_safe = np.where(np.abs(s1) < 1e-9, 1e-9, s1)
        return np.clip(np.sqrt(s2 ** 2 + s3 ** 2 + s4 ** 2) / s1_safe, 0.0, 1.0)
    if "radar" in cols:
        return np.clip(0.45 - normalise(df[cols["radar"]].to_numpy()) * 0.4,
                       0.02, 0.9)
    raise ValueError("Need DOP, full Stokes or Radar column for DOP.")


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a feature frame containing radar + terrain features."""
    cols = {c.lower(): c for c in df.columns}
    out = pd.DataFrame()
    out["CPR"] = compute_cpr(df)
    out["DOP"] = compute_dop(df)

    if "radar" in cols:
        out["Backscatter"] = normalise(df[cols["radar"]].to_numpy())
    else:
        out["Backscatter"] = normalise(out["CPR"].to_numpy())
    out["Texture"] = (
        pd.Series(out["Backscatter"]).rolling(9, center=True, min_periods=1)
        .std().fillna(0.0).to_numpy()
    )

    if "slope" in cols:
        out["Slope"] = df[cols["slope"]].to_numpy(dtype=np.float64)
    else:
        out["Slope"] = np.zeros(len(df))
    out["Roughness"] = normalise(out["Texture"].to_numpy())
    if "illumination" in cols:
        out["Illumination"] = normalise(df[cols["illumination"]].to_numpy())
    else:
        out["Illumination"] = np.full(len(df), 0.5)
    if "temperature" in cols:
        out["Temperature"] = df[cols["temperature"]].to_numpy(dtype=np.float64)
    return out


def make_labels(df: pd.DataFrame) -> np.ndarray:
    """Binary ice labels from an explicit column or the CPR/DOP physics rule."""
    cols = {c.lower(): c for c in df.columns}
    if "label" in cols:
        return (df[cols["label"]].to_numpy() > 0).astype(int)
    if "ice_probability" in cols:
        return (df[cols["ice_probability"]].to_numpy() >= 0.5).astype(int)
    cpr = compute_cpr(df)
    dop = compute_dop(df)
    return ((cpr > 1.0) & (dop < 0.13)).astype(int)


def scale_features(X: pd.DataFrame) -> Tuple[np.ndarray, StandardScaler]:
    """Standard-scale a feature matrix, returning the array and fitted scaler."""
    scaler = StandardScaler()
    return scaler.fit_transform(X.to_numpy()), scaler
