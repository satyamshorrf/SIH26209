"""OHRC (Orbiter High Resolution Camera) image processing.

Provides classical computer-vision preprocessing for the high resolution optical
imagery: grayscale loading, denoising, contrast enhancement (CLAHE), edge /
boulder detection and shadow segmentation.  OpenCV is used when available with a
NumPy/Pillow fallback so the module works in minimal environments.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np

from .utils import load_image_gray, save_heatmap

try:  # OpenCV is optional - degrade gracefully if unavailable.
    import cv2

    _HAS_CV2 = True
except Exception:  # pragma: no cover
    cv2 = None
    _HAS_CV2 = False


def load_ohrc(path: str) -> np.ndarray:
    """Load an OHRC image as a normalised float32 grayscale array.

    Raises ``ValueError`` if the image cannot be decoded.
    """
    img = load_image_gray(path)
    if img is None:
        raise ValueError(f"Could not decode OHRC image at '{path}'.")
    return img


def enhance_contrast(img: np.ndarray) -> np.ndarray:
    """Apply CLAHE contrast enhancement (or histogram stretch fallback)."""
    if _HAS_CV2:
        u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        return clahe.apply(u8).astype(np.float32) / 255.0
    # Simple percentile contrast stretch.
    lo, hi = np.percentile(img, [2, 98])
    if hi - lo < 1e-6:
        return img
    return np.clip((img - lo) / (hi - lo), 0, 1)


def denoise(img: np.ndarray) -> np.ndarray:
    """Gaussian denoise the image."""
    if _HAS_CV2:
        u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        blurred = cv2.GaussianBlur(u8, (5, 5), 0)
        return blurred.astype(np.float32) / 255.0
    # Separable box blur fallback.
    from scipy.ndimage import gaussian_filter

    return gaussian_filter(img, sigma=1.2)


def detect_edges(img: np.ndarray) -> np.ndarray:
    """Edge / boulder rim map via Canny (OpenCV) or Sobel gradient fallback."""
    if _HAS_CV2:
        u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        edges = cv2.Canny(u8, 50, 150)
        return edges.astype(np.float32) / 255.0
    from scipy.ndimage import sobel

    gx = sobel(img, axis=0)
    gy = sobel(img, axis=1)
    mag = np.hypot(gx, gy)
    mx = float(mag.max())
    return mag / mx if mx > 1e-9 else mag


def shadow_mask(img: np.ndarray, percentile: float = 25.0) -> np.ndarray:
    """Binary mask of permanently shadowed (dark) pixels."""
    thr = np.percentile(img, percentile)
    return (img <= thr).astype(np.float32)


def boulder_density(edges: np.ndarray, block: int = 32) -> float:
    """Estimate fractional boulder density from the edge map."""
    return float(np.mean(edges > 0.5))


def process_ohrc(path: str, render: bool = True) -> Dict[str, object]:
    """Full OHRC pipeline returning summary statistics and optional artefacts."""
    img = load_ohrc(path)
    enhanced = enhance_contrast(denoise(img))
    edges = detect_edges(enhanced)
    shadows = shadow_mask(enhanced)

    result: Dict[str, object] = {
        "width": int(img.shape[1]),
        "height": int(img.shape[0]),
        "mean_intensity": float(np.mean(img)),
        "std_intensity": float(np.std(img)),
        "shadow_fraction": float(np.mean(shadows)),
        "boulder_density": boulder_density(edges),
        "edge_density": float(np.mean(edges)),
    }

    if render:
        result["edge_map"] = save_heatmap(edges, "OHRC Edge / Boulder Map",
                                          "ohrc_edges", cmap="magma")
        result["shadow_map"] = save_heatmap(shadows, "OHRC Shadow Segmentation",
                                            "ohrc_shadow", cmap="gray")
    return result
