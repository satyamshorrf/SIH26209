"""Shared helper utilities for the Lunar AI Ice Detection backend.

This module centralises the small, dependency-light helpers that every router
and service relies on: filesystem management for uploads/outputs, safe CSV and
image loading, JSON sanitisation for NumPy/pandas types and lightweight matplotlib
chart rendering.  Keeping these here avoids circular imports between the service
modules.
"""

from __future__ import annotations

import io
import json
import math
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

# matplotlib must use a non-interactive backend on a headless server.
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (import after backend selection)

# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Directory holding the bundled sample datasets shipped with the repository.
SAMPLE_DATA_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "ml_pipeline", "datasets")
)


def ensure_dirs() -> None:
    """Create the upload and output directories if they do not yet exist."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def new_token() -> str:
    """Return a short unique token used to namespace uploaded/generated files."""
    return uuid.uuid4().hex[:12]


def timestamp() -> str:
    """Return an ISO-8601 UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()


def upload_path(filename: str) -> str:
    ensure_dirs()
    return os.path.join(UPLOAD_DIR, filename)


def output_path(filename: str) -> str:
    ensure_dirs()
    return os.path.join(OUTPUT_DIR, filename)


def save_upload(file_bytes: bytes, original_name: str) -> Dict[str, str]:
    """Persist an uploaded file to disk under a unique name.

    Returns a dict containing the generated ``token``, the ``stored_name`` and
    the absolute ``path`` on disk.
    """
    ensure_dirs()
    token = new_token()
    ext = os.path.splitext(original_name)[1].lower() or ".dat"
    stored_name = f"{token}{ext}"
    path = os.path.join(UPLOAD_DIR, stored_name)
    with open(path, "wb") as fh:
        fh.write(file_bytes)
    return {
        "token": token,
        "original_name": original_name,
        "stored_name": stored_name,
        "path": path,
    }


def resolve_upload(stored_name: str) -> str:
    """Resolve a previously stored upload name to its absolute path."""
    path = os.path.join(UPLOAD_DIR, stored_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Uploaded file '{stored_name}' was not found.")
    return path


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------


def load_csv(path: str) -> pd.DataFrame:
    """Read a CSV file into a DataFrame, raising a clear error on failure."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV file '{path}' does not exist.")
    try:
        return pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"Failed to parse CSV '{path}': {exc}") from exc


def load_image_gray(path: str) -> Optional[np.ndarray]:
    """Load an image as a normalised float32 grayscale array in ``[0, 1]``.

    Uses OpenCV when available and falls back to Pillow otherwise.  Returns
    ``None`` if no image library can decode the file.
    """
    try:
        import cv2

        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            return img.astype(np.float32) / 255.0
    except Exception:
        pass

    try:
        from PIL import Image

        with Image.open(path) as im:
            arr = np.asarray(im.convert("L"), dtype=np.float32)
        return arr / 255.0
    except Exception:
        return None


def sample_dataset_path(name: str) -> Optional[str]:
    """Return the path to a bundled sample dataset if it exists."""
    candidate = os.path.join(SAMPLE_DATA_DIR, name)
    return candidate if os.path.exists(candidate) else None


# ---------------------------------------------------------------------------
# JSON sanitisation
# ---------------------------------------------------------------------------


def to_native(value: Any) -> Any:
    """Recursively convert NumPy/pandas scalar & container types to native Python.

    FastAPI serialises with the standard ``json`` encoder which does not know how
    to handle ``np.float32``, ``np.int64`` or ``NaN`` values.  This helper makes
    any analysis result safe to return directly from an endpoint.
    """
    if isinstance(value, dict):
        return {str(k): to_native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_native(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        f = float(value)
        return None if (math.isnan(f) or math.isinf(f)) else f
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, np.ndarray):
        return [to_native(v) for v in value.tolist()]
    if isinstance(value, float):
        return None if (math.isnan(value) or math.isinf(value)) else value
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    return value


def dataframe_preview(df: pd.DataFrame, rows: int = 10) -> Dict[str, Any]:
    """Return a JSON-safe preview (columns + first ``rows`` records) of a frame."""
    head = df.head(rows).copy()
    head = head.replace({np.nan: None})
    return {
        "columns": [str(c) for c in df.columns],
        "row_count": int(len(df)),
        "rows": to_native(head.to_dict(orient="records")),
    }


def write_csv(df: pd.DataFrame, prefix: str) -> str:
    """Write ``df`` to the outputs directory and return the stored file name."""
    ensure_dirs()
    name = f"{prefix}_{new_token()}.csv"
    df.to_csv(os.path.join(OUTPUT_DIR, name), index=False)
    return name


def write_json(payload: Dict[str, Any], prefix: str) -> str:
    """Write a JSON document to the outputs directory; return the file name."""
    ensure_dirs()
    name = f"{prefix}_{new_token()}.json"
    with open(os.path.join(OUTPUT_DIR, name), "w", encoding="utf-8") as fh:
        json.dump(to_native(payload), fh, indent=2)
    return name


# ---------------------------------------------------------------------------
# Chart rendering helpers (matplotlib -> PNG on disk)
# ---------------------------------------------------------------------------

_DARK_BG = "#0b1020"
_PANEL_BG = "#121a33"
_ACCENT = "#4f8cff"
_ACCENT2 = "#a855f7"


def _style_axes(ax) -> None:
    ax.set_facecolor(_PANEL_BG)
    ax.tick_params(colors="#c7d2fe")
    for spine in ax.spines.values():
        spine.set_color("#334155")
    ax.title.set_color("#e2e8f0")
    ax.xaxis.label.set_color("#c7d2fe")
    ax.yaxis.label.set_color("#c7d2fe")


def save_heatmap(matrix: np.ndarray, title: str, prefix: str,
                 cmap: str = "viridis") -> str:
    """Render a 2D matrix as a heatmap PNG and return the stored file name."""
    ensure_dirs()
    name = f"{prefix}_{new_token()}.png"
    fig, ax = plt.subplots(figsize=(6, 5), dpi=120)
    fig.patch.set_facecolor(_DARK_BG)
    _style_axes(ax)
    im = ax.imshow(matrix, cmap=cmap, aspect="auto")
    ax.set_title(title)
    cbar = fig.colorbar(im, ax=ax)
    cbar.ax.yaxis.set_tick_params(color="#c7d2fe")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="#c7d2fe")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, name), facecolor=fig.get_facecolor())
    plt.close(fig)
    return name


def save_scatter_map(x: Iterable[float], y: Iterable[float],
                     values: Iterable[float], title: str, prefix: str,
                     cmap: str = "viridis",
                     path_x: Optional[Iterable[float]] = None,
                     path_y: Optional[Iterable[float]] = None) -> str:
    """Render a coloured scatter plot (optionally overlaying a route) to PNG."""
    ensure_dirs()
    name = f"{prefix}_{new_token()}.png"
    fig, ax = plt.subplots(figsize=(7, 5), dpi=120)
    fig.patch.set_facecolor(_DARK_BG)
    _style_axes(ax)
    sc = ax.scatter(list(x), list(y), c=list(values), cmap=cmap, s=14,
                    edgecolors="none")
    if path_x is not None and path_y is not None:
        ax.plot(list(path_x), list(path_y), color="#f97316", linewidth=2.2,
                marker="o", markersize=4, label="Planned route")
        ax.legend(facecolor=_PANEL_BG, edgecolor="#334155", labelcolor="#e2e8f0")
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    fig.colorbar(sc, ax=ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, name), facecolor=fig.get_facecolor())
    plt.close(fig)
    return name


def save_bar(labels: List[str], values: List[float], title: str,
             prefix: str) -> str:
    """Render a simple bar chart to PNG and return the stored file name."""
    ensure_dirs()
    name = f"{prefix}_{new_token()}.png"
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=120)
    fig.patch.set_facecolor(_DARK_BG)
    _style_axes(ax)
    ax.bar(labels, values, color=_ACCENT)
    ax.set_title(title)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, name), facecolor=fig.get_facecolor())
    plt.close(fig)
    return name


def safe_float(value: Any, default: float = 0.0) -> float:
    """Coerce a value to float, returning ``default`` on failure or NaN."""
    try:
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (TypeError, ValueError):
        return default
