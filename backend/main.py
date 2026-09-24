"""Lunar AI Ice Detection System - FastAPI application entrypoint.

Run locally with::

    uvicorn main:app --reload

The API exposes five analysis modules (ice detection, ice volume, safe landing,
path planning and AI confidence), each with an ``/upload`` and ``/process``
endpoint, plus dashboard aggregation and static file serving for generated
artefacts (heatmaps, route maps, CSV/JSON downloads).
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from routers import confidence, ice, landing, path, volume
from services.utils import (
    OUTPUT_DIR,
    UPLOAD_DIR,
    ensure_dirs,
    output_path,
    sample_dataset_path,
)

ensure_dirs()

app = FastAPI(
    title="Lunar AI Ice Detection System",
    description=(
        "Detection and characterisation of subsurface ice in lunar south "
        "polar regions using Chandrayaan-2 DFSAR and OHRC datasets, with safe "
        "landing analysis and autonomous rover path planning."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register module routers.
app.include_router(ice.router)
app.include_router(volume.router)
app.include_router(landing.router)
app.include_router(path.router)
app.include_router(confidence.router)

# Serve generated artefacts (PNG heatmaps, route maps, CSV/JSON exports).
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


@app.get("/")
def root():
    """Service banner / health summary."""
    return {
        "service": "Lunar AI Ice Detection System",
        "version": "1.0.0",
        "status": "online",
        "modules": ["ice", "volume", "landing", "path", "confidence"],
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/dashboard")
def dashboard():
    """Aggregate headline metrics across modules using the bundled sample data.

    Powers the frontend dashboard cards/charts even before the user uploads
    their own datasets.
    """
    from services import (
        confidence_score,
        ice_volume,
        landing_analysis,
    )
    from services.dfsar_processing import extract_features, feature_summary
    from services.utils import load_csv

    sample = sample_dataset_path("sample_dfsar.csv")
    if not sample:
        return JSONResponse(
            status_code=200,
            content={
                "available": False,
                "message": "No sample dataset bundled.",
            },
        )

    df = load_csv(sample)
    features = extract_features(df)
    fsum = feature_summary(features)

    # Ice detection headline.
    cpr = features["CPR"].to_numpy()
    dop = features["DOP"].to_numpy()
    ice_mask = (cpr > 1.0) & (dop < 0.13)
    detected_ice_percent = round(float(ice_mask.mean()) * 100, 2)

    # Landing + volume + confidence headlines.
    scored = landing_analysis.landing_suitability(df)
    lsum = landing_analysis.landing_summary(scored)
    vol = ice_volume.estimate_volume(df)
    conf = confidence_score.evaluate(df)

    return {
        "available": True,
        "cards": {
            "dfsar_points": int(len(df)),
            "ohrc_points": int(len(df)),
            "detected_ice_percent": detected_ice_percent,
            "landing_safety_score": round(lsum["mean_safety_percent"], 2),
            "mission_confidence": conf["metrics"]["mission_confidence_percent"],
        },
        "feature_summary": fsum,
        "landing_summary": lsum,
        "volume_summary": vol["summary"],
        "confidence_metrics": conf["metrics"],
    }


@app.get("/api/sample/{name}")
def download_sample(name: str):
    """Serve a bundled sample dataset (e.g. ``sample_dfsar.csv``).

    Lets the frontend offer a one-click "load sample" action so the full
    upload -> process workflow can be exercised without external data.
    """
    if "/" in name or "\\" in name or ".." in name:
        return JSONResponse(status_code=400, content={"detail": "Invalid name"})
    path = sample_dataset_path(name)
    if not path:
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return FileResponse(path, filename=name, media_type="text/csv")


@app.get("/api/download/{filename}")
def download_output(filename: str):
    """Download a generated artefact (CSV/PNG/JSON) by filename."""
    path = output_path(filename)
    if not os.path.exists(path):
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return FileResponse(path, filename=filename)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
