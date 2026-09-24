"""Subsurface ice volume estimation.

Estimates the volume of water-ice in the surveyed region using the classic
reservoir formula::

    Volume = Area x Depth x Ice_Fraction

Permanently Shadowed Regions (PSR) and Doubly-Shadowed Permanently-shadowed
Regions (DSPR) are derived from illumination and temperature, the ice fraction
from the joint CPR/DOP radar signature, and the depth defaults to the top 5 m of
regolith that DFSAR is sensitive to.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from . import dfsar_processing as dfsar

# Physical constants.
ICE_DENSITY_KG_M3 = 917.0       # density of water ice
DEFAULT_DEPTH_M = 5.0           # DFSAR subsurface sensing depth
# Approximate ground area represented by a single sample point (m^2).  At the
# lunar south pole one degree ~= 30.3 km; a 5000-point survey over ~1deg^2
# yields cells of the order of 1.8e5 m^2 each.
DEFAULT_CELL_AREA_M2 = 180_000.0


def _normalise(arr: np.ndarray) -> np.ndarray:
    lo = float(np.nanmin(arr))
    hi = float(np.nanmax(arr))
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def _col(df: pd.DataFrame, *names: str):
    cols = {c.lower(): c for c in df.columns}
    for n in names:
        if n in cols:
            return df[cols[n]].to_numpy(dtype=np.float64)
    return None


def ice_fraction(df: pd.DataFrame) -> np.ndarray:
    """Per-point ice fraction in [0,1] from the radar signature."""
    prob = _col(df, "ice_probability", "ice_prob")
    if prob is not None:
        return np.clip(prob, 0.0, 1.0)

    features = dfsar.extract_features(df)
    cpr = features["CPR"].to_numpy()
    dop = features["DOP"].to_numpy()
    # High CPR + low DOP -> high ice fraction.
    cpr_score = np.clip(cpr / 2.0, 0.0, 1.0)
    dop_score = np.clip(1.0 - dop / 0.4, 0.0, 1.0)
    return np.clip(0.6 * cpr_score + 0.4 * dop_score, 0.0, 1.0)


def shadow_regions(df: pd.DataFrame) -> Dict[str, np.ndarray]:
    """Return boolean masks for PSR and DSPR cells."""
    illum = _col(df, "illumination")
    temp = _col(df, "temperature")

    if illum is not None:
        illum_n = _normalise(illum)
    else:
        illum_n = np.full(len(df), 0.5)

    psr = illum_n < 0.25  # permanently shadowed: very low illumination
    if temp is not None:
        # Doubly shadowed traps are the coldest within PSRs.
        dspr = psr & (temp < np.percentile(temp, 15))
    else:
        dspr = psr & (illum_n < 0.1)
    return {"psr": psr, "dspr": dspr}


def estimate_volume(df: pd.DataFrame, depth_m: float = DEFAULT_DEPTH_M,
                    cell_area_m2: float = DEFAULT_CELL_AREA_M2) -> Dict[str, object]:
    """Estimate total subsurface ice volume and a per-cell breakdown table."""
    frac = ice_fraction(df)
    regions = shadow_regions(df)
    psr = regions["psr"]
    dspr = regions["dspr"]
    n = len(df)

    # Only PSR cells are assumed to retain stable subsurface ice.
    cell_volume = cell_area_m2 * depth_m * frac
    cell_volume = np.where(psr, cell_volume, cell_volume * 0.15)

    total_volume_m3 = float(np.sum(cell_volume))
    total_mass_kg = total_volume_m3 * ICE_DENSITY_KG_M3

    out = pd.DataFrame()
    lat = _col(df, "latitude", "lat")
    lon = _col(df, "longitude", "lon")
    if lat is not None:
        out["Latitude"] = lat
    if lon is not None:
        out["Longitude"] = lon
    out["IceFraction"] = np.round(frac, 4)
    out["IsPSR"] = psr
    out["IsDSPR"] = dspr
    out["CellVolume_m3"] = np.round(cell_volume, 2)

    summary = {
        "total_points": int(n),
        "depth_m": depth_m,
        "cell_area_m2": cell_area_m2,
        "psr_fraction": float(np.mean(psr)),
        "dspr_fraction": float(np.mean(dspr)),
        "psr_percent": round(float(np.mean(psr)) * 100, 2),
        "dspr_percent": round(float(np.mean(dspr)) * 100, 2),
        "mean_ice_fraction": float(np.mean(frac)),
        "total_volume_m3": round(total_volume_m3, 2),
        "total_volume_million_m3": round(total_volume_m3 / 1e6, 4),
        "total_mass_tonnes": round(total_mass_kg / 1000.0, 2),
        "total_mass_million_tonnes": round(total_mass_kg / 1e9, 4),
    }
    return {"summary": summary, "table": out}
