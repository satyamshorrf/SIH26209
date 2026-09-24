"""Generate physically-plausible sample datasets for the lunar pipeline.

Produces:
  * ``sample_dfsar.csv`` - DFSAR radar + terrain point table with Stokes params.
  * ``sample_ohrc.csv``  - OHRC optical pixel intensity table (gridded tile).

The data is synthetic but follows the expected statistical structure of the
Chandrayaan-2 south-polar products so every backend module produces meaningful
results out of the box.  Run with::

    python ml_pipeline/datasets/generate_samples.py
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(42)


def generate_dfsar(n: int = 2000) -> pd.DataFrame:
    """Generate a DFSAR point table over a lunar south-polar tile."""
    lat = RNG.uniform(-90.0, -85.0, n)
    lon = RNG.uniform(0.0, 360.0, n)

    # Elevation: crater-like basins via a couple of Gaussian depressions.
    base = -1500 + RNG.normal(0, 250, n)
    for cx, cy, depth, spread in [(-88.5, 120, 1800, 4.0),
                                  (-87.0, 240, 1200, 6.0)]:
        d2 = (lat - cx) ** 2 + ((lon - cy) / 10.0) ** 2
        base -= depth * np.exp(-d2 / (2 * spread ** 2))
    elevation = base

    # Slope correlates with elevation gradient magnitude.
    slope = np.clip(np.abs(RNG.normal(8, 5, n)) +
                    (elevation.std() - np.abs(elevation - elevation.mean())) * 0,
                    0, 35)
    slope = np.clip(slope + (np.abs(elevation) / np.abs(elevation).max()) * 6,
                    0, 40)

    # Illumination: lower in deep basins (permanent shadow).
    illum = np.clip(300 + elevation / 10.0 + RNG.normal(0, 30, n), 0, 400)

    # Temperature: colder in shadowed traps.
    temperature = np.clip(170 + illum / 8.0 + RNG.normal(0, 8, n), 40, 260)

    # Ice tends to sit in cold, shadowed, deep traps.
    ice_drivers = (
        (1 - illum / 400.0) * 0.5
        + (1 - (temperature - 40) / 220.0) * 0.3
        + (np.abs(elevation) / np.abs(elevation).max()) * 0.2
    )
    ice_prob = np.clip(ice_drivers + RNG.normal(0, 0.08, n), 0, 1)

    # Radar backscatter rises with ice content.
    radar = np.clip(0.1 + ice_prob * 0.6 + RNG.normal(0, 0.06, n), 0, 1)

    # Radar polarimetry derived products.
    # CPR (sigma_SC / sigma_OC style ratio) rises with ice; DOP falls with ice.
    cpr = np.clip(0.4 + ice_prob * 1.6 + RNG.normal(0, 0.05, n), 0.1, 3.0)
    dop = np.clip(0.4 - ice_prob * 0.34 + RNG.normal(0, 0.02, n), 0.02, 0.6)

    # Stokes vector consistent with the DOP magnitude: total power S1 and a
    # polarised part S2,S3,S4 whose quadrature equals DOP * S1.
    s1 = 1.0 + radar
    pol_power = dop * s1
    a = RNG.uniform(0.2, 0.6, n)
    b = RNG.uniform(0.2, 0.6, n)
    c = np.sqrt(np.clip(1.0 - a ** 2 - b ** 2, 1e-6, None))
    norm = np.sqrt(a ** 2 + b ** 2 + c ** 2)
    s2 = pol_power * (a / norm) * RNG.choice([-1, 1], n)
    s3 = pol_power * (b / norm) * RNG.choice([-1, 1], n)
    s4 = pol_power * (c / norm) * RNG.choice([-1, 1], n)

    hazard = np.clip(slope * 1.5 + (1 - illum / 400.0) * 30 +
                     RNG.normal(0, 5, n), 0, 100)

    return pd.DataFrame({
        "Latitude": np.round(lat, 5),
        "Longitude": np.round(lon, 5),
        "Elevation": np.round(elevation, 2),
        "Slope": np.round(slope, 3),
        "Temperature": np.round(temperature, 2),
        "Radar": np.round(radar, 4),
        "Illumination": np.round(illum, 2),
        "Hazard_Score": np.round(hazard, 2),
        "Ice_Probability": np.round(ice_prob, 4),
        "CPR": np.round(cpr, 4),
        "DOP": np.round(dop, 4),
        "S1": np.round(s1, 4),
        "S2": np.round(s2, 4),
        "S3": np.round(s3, 4),
        "S4": np.round(s4, 4),
    })


def generate_ohrc(size: int = 96) -> pd.DataFrame:
    """Generate an OHRC optical tile as a long pixel table (x, y, intensity)."""
    yy, xx = np.mgrid[0:size, 0:size]
    # Smooth regolith gradient.
    img = 0.5 + 0.25 * np.sin(xx / 12.0) * np.cos(yy / 15.0)
    # A central shadowed crater (dark disc).
    cx, cy, r = size * 0.55, size * 0.45, size * 0.22
    crater = ((xx - cx) ** 2 + (yy - cy) ** 2) < r ** 2
    img[crater] *= 0.25
    # Scattered boulders (bright speckle).
    boulders = RNG.random((size, size)) > 0.985
    img[boulders] = 1.0
    img = np.clip(img + RNG.normal(0, 0.03, (size, size)), 0, 1)

    return pd.DataFrame({
        "x": xx.ravel(),
        "y": yy.ravel(),
        "intensity": np.round(img.ravel(), 4),
    })


def main() -> None:
    dfsar = generate_dfsar()
    dfsar.to_csv(os.path.join(HERE, "sample_dfsar.csv"), index=False)
    print(f"Wrote sample_dfsar.csv ({len(dfsar)} rows)")

    ohrc = generate_ohrc()
    ohrc.to_csv(os.path.join(HERE, "sample_ohrc.csv"), index=False)
    print(f"Wrote sample_ohrc.csv ({len(ohrc)} rows)")


if __name__ == "__main__":
    main()
