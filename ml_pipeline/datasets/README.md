# Sample Datasets

Synthetic but physically-plausible datasets for the Lunar AI Ice Detection
System. They follow the structure of the Chandrayaan-2 south-polar products so
every backend module and ML model produces meaningful output out of the box.

Regenerate them at any time with:

```bash
python ml_pipeline/datasets/generate_samples.py
```

## `sample_dfsar.csv`

DFSAR radar + terrain point table (2,000 rows). Columns:

| Column | Description |
| --- | --- |
| `Latitude`, `Longitude` | South-polar coordinates (degrees) |
| `Elevation` | DEM elevation (metres, negative = below datum) |
| `Slope` | Terrain slope (degrees) |
| `Temperature` | Surface temperature (Kelvin) |
| `Radar` | Normalised radar backscatter (0–1) |
| `Illumination` | Solar illumination proxy (hours-equivalent) |
| `Hazard_Score` | Composite terrain hazard (0–100) |
| `Ice_Probability` | Ground-truth ice likelihood (0–1) |
| `CPR` | Circular Polarisation Ratio (ice indicator, >1 ≈ ice) |
| `DOP` | Degree Of Polarisation (ice indicator, <0.13 ≈ ice) |
| `S1`–`S4` | Stokes parameters (hybrid-polarimetry); `DOP = √(S2²+S3²+S4²)/S1` |

## `sample_ohrc.csv`

OHRC optical tile flattened to a pixel table (96×96 = 9,216 rows): columns
`x`, `y`, `intensity` (0–1). Contains a central shadowed crater and scattered
bright boulders so the OpenCV preprocessing (edge/shadow/boulder detection)
returns realistic statistics.

> The CPR/DOP and Stokes columns are internally consistent: the degree of
> polarisation recomputed from `S1..S4` matches the `DOP` column. `CPR` is
> provided as an independent σ_SC/σ_OC-style product, as in real DFSAR releases.
