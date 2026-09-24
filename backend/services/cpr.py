"""Circular Polarisation Ratio (CPR) computation.

The CPR is the primary radar discriminator used to flag water-ice in
permanently shadowed regions.  For a circularly-polarised SAR system (such as
Chandrayaan-2 DFSAR operating in hybrid-polarimetry mode) it is derived from the
four Stokes parameters ``S1..S4``:

    CPR = (S1 - S4) / (S1 + S4)

where ``S1`` is total power and ``S4`` is the fourth Stokes parameter (the
circular polarisation component).  High CPR (> 1) indicates strong
same-sense circular backscatter which, in the absence of rough terrain, is a
classic signature of volume scattering from buried ice.

When raw Stokes parameters are unavailable we fall back to a physically-motivated
estimate driven by the normalised radar backscatter coefficient.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

CPR_ICE_THRESHOLD = 1.0


def compute_cpr(df: pd.DataFrame) -> np.ndarray:
    """Return a per-row CPR array for ``df``.

    The function looks for, in priority order:

    1. An existing ``CPR`` column (already computed upstream).
    2. Stokes parameters ``S1`` and ``S4``.
    3. A normalised ``Radar`` backscatter column (0-1) used as a proxy.
    """
    cols = {c.lower(): c for c in df.columns}

    if "cpr" in cols:
        return df[cols["cpr"]].to_numpy(dtype=np.float64)

    if "s1" in cols and "s4" in cols:
        s1 = df[cols["s1"]].to_numpy(dtype=np.float64)
        s4 = df[cols["s4"]].to_numpy(dtype=np.float64)
        denom = s1 + s4
        # Guard against division by zero.
        denom = np.where(np.abs(denom) < 1e-9, 1e-9, denom)
        cpr = (s1 - s4) / denom
        return np.clip(cpr, 0.0, 5.0)

    # Fallback: derive CPR from radar backscatter.  Stronger backscatter in the
    # cold shadowed traps maps to higher CPR via an empirically scaled curve.
    if "radar" in cols:
        radar = df[cols["radar"]].to_numpy(dtype=np.float64)
        radar = _normalise(radar)
        # Map [0,1] backscatter to a plausible CPR range of roughly [0.2, 2.2].
        return 0.2 + radar * 2.0

    raise ValueError(
        "Cannot compute CPR: dataset needs a 'CPR', Stokes ('S1','S4') or "
        "'Radar' column."
    )


def cpr_ice_mask(cpr: np.ndarray, threshold: float = CPR_ICE_THRESHOLD) -> np.ndarray:
    """Boolean mask of pixels/points whose CPR exceeds the ice threshold."""
    return cpr > threshold


def _normalise(arr: np.ndarray) -> np.ndarray:
    lo = float(np.nanmin(arr))
    hi = float(np.nanmax(arr))
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def cpr_summary(cpr: np.ndarray) -> dict:
    """Return descriptive statistics for a CPR array."""
    mask = cpr_ice_mask(cpr)
    return {
        "mean_cpr": float(np.nanmean(cpr)),
        "max_cpr": float(np.nanmax(cpr)),
        "min_cpr": float(np.nanmin(cpr)),
        "high_cpr_fraction": float(np.mean(mask)),
        "threshold": CPR_ICE_THRESHOLD,
    }
