"""Module 3 - Safe Landing Site router.

Endpoints:
    POST /api/landing/upload   - upload a terrain/DEM dataset
    POST /api/landing/process  - compute landing suitability & zones
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services import landing_analysis
from services.utils import save_scatter_map, to_native, write_csv

from ._common import load_uploaded_csv, store_upload

router = APIRouter(prefix="/api/landing", tags=["Safe Landing"])


@router.post("/upload")
async def upload(
    dataset_file: Optional[UploadFile] = File(default=None),
    file: Optional[UploadFile] = File(default=None),
):
    primary = dataset_file or file
    if primary is None:
        raise HTTPException(status_code=400, detail="No file provided.")
    return {"dataset": await store_upload(primary)}


@router.post("/process")
async def process(dataset_file: str = Form(...)):
    """Score landing candidates and return the recommended touchdown site."""
    df = load_uploaded_csv(dataset_file)
    scored = landing_analysis.landing_suitability(df)
    summary = landing_analysis.landing_summary(scored)

    csv_name = write_csv(scored, "landing_sites")

    map_name = None
    if "Latitude" in scored.columns and "Longitude" in scored.columns:
        map_name = save_scatter_map(
            scored["Longitude"], scored["Latitude"], scored["LSI"],
            "Landing Suitability Index", "landing_map", cmap="RdYlGn",
        )

    return to_native({
        "summary": summary,
        "best_site": summary["best_site"],
        "safe_zones": summary["safe_zones"],
        "risk_zones": summary["risk_zones"],
        "unsafe_zones": summary["unsafe_zones"],
        "charts": {
            "zone_distribution": [
                {"name": "Safe", "value": summary["safe_zones"]},
                {"name": "Risk", "value": summary["risk_zones"]},
                {"name": "Unsafe", "value": summary["unsafe_zones"]},
            ],
        },
        "artifacts": {
            "landing_csv": csv_name,
            "landing_map_png": map_name,
        },
        "preview": to_native(scored.head(15).to_dict(orient="records")),
    })
