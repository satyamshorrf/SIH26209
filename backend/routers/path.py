"""Module 4 - Rover Path Planning router.

Endpoints:
    POST /api/path/upload   - upload a terrain dataset
    POST /api/path/process  - plan a safe rover route (A* / Dijkstra)
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services import path_planner
from services.utils import save_scatter_map, to_native, write_csv

from ._common import load_uploaded_csv, store_upload

router = APIRouter(prefix="/api/path", tags=["Path Planning"])


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
    algorithm: str = Form(default="astar"),
    grid_size: int = Form(default=40),
):
    """Plan the shortest safe rover route across the hazard-weighted grid."""
    df = load_uploaded_csv(dataset_file)
    grid_size = int(max(10, min(grid_size, 120)))
    result = path_planner.plan_route(df, algorithm=algorithm, grid_size=grid_size)

    waypoints = result["waypoints"]

    # Build a route map overlay on the candidate scatter.
    import pandas as pd

    map_name = None
    if "Latitude" in df.columns and "Longitude" in df.columns:
        path_lat = [w["lat"] for w in waypoints]
        path_lon = [w["lon"] for w in waypoints]
        cols = {c.lower(): c for c in df.columns}
        color_col = cols.get("hazard_score") or cols.get("slope")
        colors = (df[color_col].to_numpy() if color_col else
                  np.zeros(len(df)))
        map_name = save_scatter_map(
            df[cols.get("longitude", "Longitude")],
            df[cols.get("latitude", "Latitude")],
            colors, f"Rover Route ({result['algorithm']})", "rover_route",
            cmap="cividis", path_x=path_lon, path_y=path_lat,
        )

    route_df = pd.DataFrame(waypoints)
    csv_name = write_csv(route_df, "rover_route")

    payload = {k: v for k, v in result.items() if not k.startswith("_")}
    payload.update({
        "artifacts": {
            "route_csv": csv_name,
            "route_map_png": map_name,
        },
    })
    return to_native(payload)
