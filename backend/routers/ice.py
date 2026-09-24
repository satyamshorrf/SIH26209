"""Module 1 - Ice Detection router.

Endpoints:
    POST /api/ice/upload   - upload a DFSAR CSV (and optionally an OHRC image)
    POST /api/ice/process  - run CPR/DOP + classifier ice detection
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services import confidence_score, ohrc_processing
from services.dfsar_processing import detect_ice, feature_summary
from services.utils import (
    resolve_upload,
    save_heatmap,
    to_native,
    write_csv,
)

from ._common import load_uploaded_csv, store_upload

router = APIRouter(prefix="/api/ice", tags=["Ice Detection"])


@router.post("/upload")
async def upload(
    dfsar_file: Optional[UploadFile] = File(default=None),
    ohrc_file: Optional[UploadFile] = File(default=None),
    file: Optional[UploadFile] = File(default=None),
):
    """Upload a DFSAR CSV and/or an OHRC image for ice detection."""
    primary = dfsar_file or file
    if primary is None and ohrc_file is None:
        raise HTTPException(status_code=400, detail="No file provided.")

    response = {}
    if primary is not None:
        response["dfsar"] = await store_upload(primary)
    if ohrc_file is not None:
        response["ohrc"] = await store_upload(ohrc_file)
    return response


@router.post("/process")
async def process(
    dfsar_file: str = Form(...),
    ohrc_file: Optional[str] = Form(default=None),
):
    """Run the full ice detection pipeline on a previously uploaded DFSAR CSV."""
    df = load_uploaded_csv(dfsar_file)
    detection = detect_ice(df)

    ice_mask = detection["IceMask"].to_numpy()
    ice_percent = round(float(ice_mask.mean()) * 100, 2)
    summary = feature_summary(detection)

    # Render an ice-probability heatmap (gridded if coordinates are present).
    heatmap_name = _render_heatmap(detection)

    # Persist outputs for download.
    csv_name = write_csv(detection, "ice_detection")
    mask_df = detection.copy()
    mask_only = mask_df[[c for c in ["Latitude", "Longitude", "IceMask",
                                     "IceProbability"] if c in mask_df.columns]]
    mask_csv = write_csv(mask_only, "ice_mask")

    # AI confidence for this detection.
    try:
        conf = confidence_score.evaluate(df)["metrics"]
    except Exception:  # noqa: BLE001
        conf = {}

    ohrc_result = None
    if ohrc_file:
        try:
            ohrc_path = resolve_upload(ohrc_file)
            ohrc_result = ohrc_processing.process_ohrc(ohrc_path)
        except Exception as exc:  # noqa: BLE001
            ohrc_result = {"error": str(exc)}

    return to_native({
        "ice_detection_percent": ice_percent,
        "detected_points": int(ice_mask.sum()),
        "total_points": int(len(detection)),
        "mean_ice_probability": float(detection["IceProbability"].mean()),
        "summary": summary,
        "confidence": conf,
        "ohrc": ohrc_result,
        "artifacts": {
            "heatmap_png": heatmap_name,
            "detection_csv": csv_name,
            "mask_csv": mask_csv,
        },
        "preview": to_native(detection.head(15).to_dict(orient="records")),
    })


def _render_heatmap(detection) -> str:
    """Render an ice-probability heatmap and return the stored PNG filename."""
    prob = detection["IceProbability"].to_numpy()
    if "Latitude" in detection.columns and "Longitude" in detection.columns:
        lat = detection["Latitude"].to_numpy()
        lon = detection["Longitude"].to_numpy()
        size = 50
        lat_edges = np.linspace(lat.min(), lat.max(), size + 1)
        lon_edges = np.linspace(lon.min(), lon.max(), size + 1)
        grid = np.full((size, size), np.nan)
        count = np.zeros((size, size))
        r = np.clip(np.digitize(lat, lat_edges) - 1, 0, size - 1)
        c = np.clip(np.digitize(lon, lon_edges) - 1, 0, size - 1)
        for ri, ci, p in zip(r, c, prob):
            grid[ri, ci] = (p if np.isnan(grid[ri, ci])
                            else (grid[ri, ci] + p) / 2)
            count[ri, ci] += 1
        grid = np.where(np.isnan(grid), 0.0, grid)
        return save_heatmap(grid, "Ice Probability Heatmap", "ice_heatmap",
                            cmap="viridis")
    # Fall back to a 1D reshaped strip.
    n = len(prob)
    side = int(np.ceil(np.sqrt(n)))
    padded = np.zeros(side * side)
    padded[:n] = prob
    return save_heatmap(padded.reshape(side, side), "Ice Probability Heatmap",
                        "ice_heatmap", cmap="viridis")
