"""Degree Of Polarisation (DOP / m) computation.

The degree of polarisation describes how strongly the backscattered wave retains
a deterministic polarisation state.  From the Stokes vector it is:

    DOP = sqrt(S2^2 + S3^2 + S4^2) / S1

Low DOP (typically < 0.13 in the lunar ice literature) combined with high CPR is
a strong joint indicator of randomly-oriented volume scattering from subsurface
ice rather than surface roughness, which tends to preserve polarisation.

A radar-backscatter fallback is provided for datasets lacking Stokes parameters.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DOP_ICE_THRESHOLD = 0.13


def compute_dop(df: pd.DataFrame) -> np.ndarray:
    """Return a per-row DOP array for ``df``.

    Priority order mirrors :func:`cpr.compute_cpr`:

    1. Existing ``DOP`` column.
    2. Full Stokes vector ``S1..S4``.
    3. ``Radar`` backscatter proxy (inverse relationship: rough/icy volume
       scattering depolarises the return, lowering DOP).
    """
    cols = {c.lower(): c for c in df.columns}

    if "dop" in cols:
        return np.clip(df[cols["dop"]].to_numpy(dtype=np.float64), 0.0, 1.0)

    if all(k in cols for k in ("s1", "s2", "s3", "s4")):
        s1 = df[cols["s1"]].to_numpy(dtype=np.float64)
        s2 = df[cols["s2"]].to_numpy(dtype=np.float64)
        s3 = df[cols["s3"]].to_numpy(dtype=np.float64)
        s4 = df[cols["s4"]].to_numpy(dtype=np.float64)
        s1_safe = np.where(np.abs(s1) < 1e-9, 1e-9, s1)
        dop = np.sqrt(s2 ** 2 + s3 ** 2 + s4 ** 2) / s1_safe
        return np.clip(dop, 0.0, 1.0)

    if "radar" in cols:
        radar = df[cols["radar"]].to_numpy(dtype=np.float64)
        radar = _normalise(radar)
        # Strong volume scattering (high radar proxy) -> lower DOP.
        return np.clip(0.45 - radar * 0.4, 0.02, 0.9)

    raise ValueError(
        "Cannot compute DOP: dataset needs a 'DOP', full Stokes ('S1'..'S4') "
        "or 'Radar' column."
    )


def dop_ice_mask(dop: np.ndarray, threshold: float = DOP_ICE_THRESHOLD) -> np.ndarray:
    """Boolean mask of points whose DOP falls below the ice threshold."""
    return dop < threshold


def _normalise(arr: np.ndarray) -> np.ndarray:
    lo = float(np.nanmin(arr))
    hi = float(np.nanmax(arr))
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def dop_summary(dop: np.ndarray) -> dict:
    """Return descriptive statistics for a DOP array."""
    mask = dop_ice_mask(dop)
    return {
        "mean_dop": float(np.nanmean(dop)),
        "max_dop": float(np.nanmax(dop)),
        "min_dop": float(np.nanmin(dop)),
        "low_dop_fraction": float(np.mean(mask)),
        "threshold": DOP_ICE_THRESHOLD,
    }
