"""Module 2 - Ice Volume estimation router.

Endpoints:
    POST /api/volume/upload   - upload a DFSAR/OHRC dataset
    POST /api/volume/process  - estimate subsurface ice volume
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services import ice_volume
from services.utils import save_bar, to_native, write_csv

from ._common import load_uploaded_csv, store_upload

router = APIRouter(prefix="/api/volume", tags=["Ice Volume"])


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
async def process(
    dataset_file: str = Form(...),
    depth_m: float = Form(default=5.0),
):
    """Estimate subsurface ice volume from an uploaded dataset."""
    df = load_uploaded_csv(dataset_file)
    result = ice_volume.estimate_volume(df, depth_m=depth_m)
    summary = result["summary"]
    table = result["table"]

    csv_name = write_csv(table, "ice_volume")

    # Pie / bar chart of PSR vs DSPR vs non-shadowed contributions.
    psr_pct = summary["psr_percent"]
    dspr_pct = summary["dspr_percent"]
    other_pct = round(max(0.0, 100.0 - psr_pct), 2)
    chart_name = save_bar(
        ["PSR", "DSPR", "Illuminated"],
        [psr_pct, dspr_pct, other_pct],
        "Shadowed Region Distribution (%)",
        "volume_regions",
    )

    return to_native({
        "summary": summary,
        "estimated_ice_volume_m3": summary["total_volume_m3"],
        "estimated_ice_volume_million_m3": summary["total_volume_million_m3"],
        "estimated_mass_million_tonnes": summary["total_mass_million_tonnes"],
        "psr_percent": summary["psr_percent"],
        "dspr_percent": summary["dspr_percent"],
        "charts": {
            "region_distribution": [
                {"name": "PSR", "value": psr_pct},
                {"name": "DSPR", "value": dspr_pct},
                {"name": "Illuminated", "value": other_pct},
            ],
        },
        "artifacts": {
            "volume_csv": csv_name,
            "region_chart_png": chart_name,
        },
        "preview": to_native(table.head(15).to_dict(orient="records")),
    })
