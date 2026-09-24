"""DFSAR (Dual Frequency Synthetic Aperture Radar) CSV processing.

Loads a DFSAR point/pixel table and engineers the radar features used by the ice
classifier: CPR, DOP, normalised backscatter and a local backscatter texture
(standard deviation of the backscatter signal in a sliding window).
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from . import cpr as cpr_mod
from . import dop as dop_mod


def _normalise(arr: np.ndarray) -> np.ndarray:
    lo = float(np.nanmin(arr))
    hi = float(np.nanmax(arr))
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def _coordinate_columns(df: pd.DataFrame) -> Dict[str, str]:
    cols = {c.lower(): c for c in df.columns}
    out = {}
    for key in ("latitude", "lat"):
        if key in cols:
            out["lat"] = cols[key]
            break
    for key in ("longitude", "lon", "lng"):
        if key in cols:
            out["lon"] = cols[key]
            break
    return out


def backscatter_series(df: pd.DataFrame) -> np.ndarray:
    """Return a normalised radar backscatter series for the dataset."""
    cols = {c.lower(): c for c in df.columns}
    for key in ("radar", "backscatter", "sigma0", "s1"):
        if key in cols:
            return _normalise(df[cols[key]].to_numpy(dtype=np.float64))
    # As a last resort synthesise backscatter from CPR.
    return _normalise(cpr_mod.compute_cpr(df))


def backscatter_texture(backscatter: np.ndarray, window: int = 9) -> np.ndarray:
    """Local texture = rolling standard deviation of the backscatter signal.

    Texture captures terrain roughness; smooth icy traps exhibit low texture
    while boulder fields and crater rims show high texture.
    """
    series = pd.Series(backscatter)
    texture = series.rolling(window=window, center=True, min_periods=1).std()
    texture = texture.fillna(0.0).to_numpy()
    return _normalise(texture)


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer the full radar feature table from a raw DFSAR frame.

    Returns a new DataFrame containing the original coordinates (when present)
    plus ``CPR``, ``DOP``, ``Backscatter`` and ``Texture`` columns.
    """
    coords = _coordinate_columns(df)
    cpr = cpr_mod.compute_cpr(df)
    dop = dop_mod.compute_dop(df)
    backscatter = backscatter_series(df)
    texture = backscatter_texture(backscatter)

    out = pd.DataFrame()
    if "lat" in coords:
        out["Latitude"] = df[coords["lat"]].to_numpy(dtype=np.float64)
    if "lon" in coords:
        out["Longitude"] = df[coords["lon"]].to_numpy(dtype=np.float64)

    # Carry temperature / illumination through when available - they help the
    # downstream ice classifier.
    cols = {c.lower(): c for c in df.columns}
    if "temperature" in cols:
        out["Temperature"] = df[cols["temperature"]].to_numpy(dtype=np.float64)
    if "illumination" in cols:
        out["Illumination"] = df[cols["illumination"]].to_numpy(dtype=np.float64)

    out["CPR"] = cpr
    out["DOP"] = dop
    out["Backscatter"] = backscatter
    out["Texture"] = texture
    return out


def ice_probability(features: pd.DataFrame) -> np.ndarray:
    """Compute a per-point ice probability from the engineered features.

    Combines the normalised CPR (positive indicator), inverse DOP (low DOP is
    indicative of volume scattering) and a mild cold-trap temperature bonus.
    """
    cpr = features["CPR"].to_numpy()
    dop = features["DOP"].to_numpy()
    cpr_score = np.clip(cpr / 2.0, 0.0, 1.0)
    dop_score = np.clip(1.0 - dop / 0.4, 0.0, 1.0)
    prob = 0.55 * cpr_score + 0.45 * dop_score
    if "Temperature" in features.columns:
        temp = features["Temperature"].to_numpy()
        temp_n = _normalise(temp)
        prob = prob * (0.85 + 0.15 * (1.0 - temp_n))  # colder -> slight boost
    return np.clip(prob, 0.0, 1.0)


def detect_ice(df: pd.DataFrame) -> pd.DataFrame:
    """Return a per-point ice-detection table with CPR/DOP, probability & mask."""
    features = extract_features(df)
    prob = ice_probability(features)
    cpr = features["CPR"].to_numpy()
    dop = features["DOP"].to_numpy()
    mask = ((cpr > cpr_mod.CPR_ICE_THRESHOLD) &
            (dop < dop_mod.DOP_ICE_THRESHOLD)).astype(int)
    out = features.copy()
    out["IceProbability"] = np.round(prob, 4)
    out["IceMask"] = mask
    return out


def feature_summary(features: pd.DataFrame) -> Dict[str, float]:
    """Return descriptive statistics over the engineered feature table."""
    summary = {
        "rows": int(len(features)),
        "cpr": cpr_mod.cpr_summary(features["CPR"].to_numpy()),
        "dop": dop_mod.dop_summary(features["DOP"].to_numpy()),
        "mean_backscatter": float(np.nanmean(features["Backscatter"])),
        "mean_texture": float(np.nanmean(features["Texture"])),
    }
    return summary
