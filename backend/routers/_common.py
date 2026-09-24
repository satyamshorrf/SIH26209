"""Shared helpers for the module routers (upload handling & previews)."""

from __future__ import annotations

from typing import Dict

from fastapi import HTTPException, UploadFile

from services.utils import dataframe_preview, load_csv, resolve_upload, save_upload


async def store_upload(file: UploadFile) -> Dict[str, object]:
    """Persist an uploaded file and, for CSVs, return a small preview.

    The returned ``stored_name`` is what subsequent ``/process`` calls reference.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    meta = save_upload(contents, file.filename or "upload.dat")

    response: Dict[str, object] = {
        "token": meta["token"],
        "stored_name": meta["stored_name"],
        "original_name": meta["original_name"],
        "size_bytes": len(contents),
    }

    if meta["stored_name"].lower().endswith(".csv"):
        try:
            df = load_csv(meta["path"])
            response["preview"] = dataframe_preview(df)
        except Exception as exc:  # noqa: BLE001 - surface parse issues to client
            response["preview_error"] = str(exc)
    return response


def load_uploaded_csv(stored_name: str):
    """Resolve a stored CSV upload to a DataFrame, raising HTTP 404 if missing."""
    try:
        path = resolve_upload(stored_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return load_csv(path)
