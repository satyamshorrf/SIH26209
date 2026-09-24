"""Module 5 - AI Confidence router.

Endpoints:
    POST /api/confidence/upload   - upload a dataset
    POST /api/confidence/process  - evaluate the ice classifier
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services import confidence_score
from services.utils import save_heatmap, to_native, write_json

from ._common import load_uploaded_csv, store_upload

router = APIRouter(prefix="/api/confidence", tags=["AI Confidence"])


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
    """Train + evaluate the ice classifier and return all confidence metrics."""
    df = load_uploaded_csv(dataset_file)
    report = confidence_score.evaluate(df)

    # Render the confusion matrix as a heatmap.
    cm = np.array(report["confusion_matrix"], dtype=float)
    cm_png = save_heatmap(cm, "Confusion Matrix", "confusion_matrix",
                          cmap="Blues") if cm.size else None

    json_name = write_json(report, "confidence_report")

    payload = dict(report)
    payload["artifacts"] = {
        "confusion_matrix_png": cm_png,
        "report_json": json_name,
    }
    return to_native(payload)
