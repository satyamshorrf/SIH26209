"""Terrain analysis for safe-landing and path-planning modules.

Derives geomorphological metrics from a DEM-style point table: slope, surface
roughness, crater proximity, boulder density and illumination.  When the input
already contains some of these columns they are used directly; otherwise they are
estimated from elevation and radar texture.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


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


def compute_slope(df: pd.DataFrame) -> np.ndarray:
    """Return per-point slope in degrees."""
    existing = _col(df, "slope")
    if existing is not None:
        return existing

    elev = _col(df, "elevation", "dem", "height")
    lat = _col(df, "latitude", "lat")
    lon = _col(df, "longitude", "lon")
    if elev is None or lat is None or lon is None:
        # Without elevation we cannot compute a true gradient.
        return np.zeros(len(df))

    coords = np.column_stack([lat, lon])
    tree = cKDTree(coords)
    # Use the local elevation gradient against nearest neighbours as a proxy.
    _, idx = tree.query(coords, k=min(6, len(df)))
    slopes = np.zeros(len(df))
    for i in range(len(df)):
        neigh = idx[i][1:] if idx.ndim > 1 else [idx[i]]
        if len(neigh) == 0:
            continue
        dz = np.abs(elev[neigh] - elev[i])
        # Approximate ground distance in metres (~30.3 km per degree on Moon).
        dd = np.linalg.norm(coords[neigh] - coords[i], axis=1) * 30300.0
        dd = np.where(dd < 1.0, 1.0, dd)
        slopes[i] = float(np.degrees(np.arctan(np.mean(dz / dd))))
    return slopes


def surface_roughness(df: pd.DataFrame) -> np.ndarray:
    """Local elevation roughness (normalised std-dev of neighbour elevations)."""
    elev = _col(df, "elevation", "dem", "height")
    texture = _col(df, "texture")
    if texture is not None:
        return _normalise(texture)
    if elev is None:
        return np.zeros(len(df))
    series = pd.Series(elev)
    rough = series.rolling(window=9, center=True, min_periods=1).std().fillna(0.0)
    return _normalise(rough.to_numpy())


def crater_distance(df: pd.DataFrame, hazard_percentile: float = 85.0) -> np.ndarray:
    """Distance (normalised, 0=on a crater, 1=far) to the nearest crater proxy.

    Craters are approximated as the points with the deepest elevation / highest
    hazard, and a KD-tree returns each point's distance to that set.
    """
    lat = _col(df, "latitude", "lat")
    lon = _col(df, "longitude", "lon")
    if lat is None or lon is None:
        return np.ones(len(df))

    hazard = _col(df, "hazard_score")
    elev = _col(df, "elevation")
    if hazard is not None:
        score = hazard
    elif elev is not None:
        score = -elev  # deeper = more crater-like
    else:
        return np.ones(len(df))

    thr = np.percentile(score, hazard_percentile)
    crater_pts = np.column_stack([lat, lon])[score >= thr]
    if len(crater_pts) == 0:
        return np.ones(len(df))
    tree = cKDTree(crater_pts)
    dists, _ = tree.query(np.column_stack([lat, lon]), k=1)
    return _normalise(dists)


def boulder_density(df: pd.DataFrame) -> np.ndarray:
    """Boulder density proxy from radar/elevation texture."""
    texture = _col(df, "texture")
    if texture is not None:
        return _normalise(texture)
    rough = surface_roughness(df)
    return rough


def illumination(df: pd.DataFrame) -> np.ndarray:
    """Return normalised illumination (solar visibility) per point."""
    illum = _col(df, "illumination")
    if illum is not None:
        return _normalise(illum)
    # Without measured illumination, derive from latitude proximity to pole.
    lat = _col(df, "latitude", "lat")
    if lat is None:
        return np.full(len(df), 0.5)
    return _normalise(np.abs(lat))


def terrain_features(df: pd.DataFrame) -> pd.DataFrame:
    """Assemble all terrain metrics into a single DataFrame."""
    out = pd.DataFrame()
    lat = _col(df, "latitude", "lat")
    lon = _col(df, "longitude", "lon")
    if lat is not None:
        out["Latitude"] = lat
    if lon is not None:
        out["Longitude"] = lon
    out["Slope"] = compute_slope(df)
    out["Roughness"] = surface_roughness(df)
    out["CraterDistance"] = crater_distance(df)
    out["BoulderDensity"] = boulder_density(df)
    out["Illumination"] = illumination(df)
    elev = _col(df, "elevation")
    if elev is not None:
        out["Elevation"] = elev
    return out


def terrain_summary(features: pd.DataFrame) -> Dict[str, float]:
    return {
        "mean_slope": float(np.nanmean(features["Slope"])),
        "max_slope": float(np.nanmax(features["Slope"])),
        "mean_roughness": float(np.nanmean(features["Roughness"])),
        "mean_boulder_density": float(np.nanmean(features["BoulderDensity"])),
        "mean_illumination": float(np.nanmean(features["Illumination"])),
    }
