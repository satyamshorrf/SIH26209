# Lunar AI Ice Detection System

**Smart India Hackathon 2026 · Problem Statement **
Detection and Characterization of Subsurface Ice in Lunar South Polar Regions
using Chandrayaan-2 **DFSAR** and **OHRC** datasets — with safe-landing analysis
and autonomous rover path planning.

An enterprise-grade, full-stack web application:

- **Frontend** — React 19 + Vite + Tailwind CSS v4 dark ISRO mission-control
  dashboard (Recharts, Framer Motion, Leaflet, React Dropzone, React Hot Toast).
- **Backend** — Python FastAPI exposing five analysis modules, each with an
  `upload` and `process` endpoint, plus dashboard aggregation and artefact
  downloads.
- **ML pipeline** — scikit-learn ice / terrain classifiers, feature engineering,
  a confidence/evaluation harness and reproducible sample datasets.

---

## Modules

| # | Module | What it does |
| - | ------ | ------------ |
| 1 | **Ice Detection** | CPR / DOP radar polarimetry + ML classifier → ice %, probability heatmap, binary mask, CSV |
| 2 | **Ice Volume** | PSR / DSPR mapping, `Volume = Area × Depth × Ice Fraction`, volume report + pie chart |
| 3 | **Safe Landing Site** | Slope, roughness, crater distance, boulder density, illumination → Landing Suitability Index + Safe/Risk/Unsafe zones |
| 4 | **Path Planning** | Hazard-weighted grid + **A\*** / **Dijkstra** with solar & terrain constraints → route, distance, travel time |
| 5 | **AI Confidence** | Accuracy, precision, recall, F1, ROC-AUC, confusion matrix, feature importance, mission confidence |

---

## Project Structure

```text
.
├── README.md
├── .gitignore
├── frontend/                 # React 19 + Vite + Tailwind v4 dashboard
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── components/        # Sidebar, Navbar, DatasetUploader, Charts/, MapViewer/, Cards/, common/
│       ├── pages/             # Dashboard, IceDetection, IceVolume, LandingSite, PathPlanning, AIConfidence, Results, Settings
│       ├── services/          # axios API client
│       ├── hooks/             # useModuleProcessor
│       ├── context/           # ResultsContext
│       ├── utils/             # formatting helpers
│       ├── App.jsx
│       └── main.jsx
├── backend/                  # FastAPI service
│   ├── main.py
│   ├── requirements.txt
│   ├── routers/              # ice, volume, landing, path, confidence
│   ├── services/             # dfsar_processing, ohrc_processing, cpr, dop, terrain,
│   │                         #   landing_analysis, path_planner, ice_volume, confidence_score, utils
│   ├── uploads/              # uploaded files (gitignored)
│   └── outputs/              # generated PNG/CSV/JSON artefacts (gitignored)
└── ml_pipeline/
    ├── datasets/             # sample_dfsar.csv, sample_ohrc.csv, generator, README
    └── models/               # feature_extractor, ice_classifier, terrain_classifier,
                              #   confidence_model, preprocessing, training
```

---

## Quick Start

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at <http://127.0.0.1:8000> — interactive docs at
<http://127.0.0.1:8000/docs>.

> The heavy geoscience / deep-learning packages (`torch`, `transformers`,
> `rasterio`, `pds4_tools`) are listed but commented out in
> `backend/requirements.txt`. The backend runs fully without them via built-in
> fallbacks; uncomment to enable richer raster / transformer processing.

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

The dashboard runs at <http://127.0.0.1:5173> and proxies `/api` and `/outputs`
to the backend on port 8000 (see `vite.config.js`). To point at a different
backend, set `VITE_API_BASE_URL`.

### 3. ML pipeline (optional)

```bash
# Regenerate sample datasets
python ml_pipeline/datasets/generate_samples.py

# Train + evaluate the ice / terrain classifiers
python -m ml_pipeline.models.training
```

---

## Using the App

1. Open the dashboard — headline cards/charts load from the bundled sample survey.
2. Open any module, click **Load sample dataset** (or drag in your own DFSAR CSV
   / OHRC image), then run the analysis.
3. View result cards, charts, heatmaps and the interactive lunar viewer; download
   the generated CSV / PNG / JSON artefacts.
4. The **Results** page consolidates the latest output from every module.

---

## API

All process endpoints accept `multipart/form-data` referencing a previously
uploaded file's `stored_name`.

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| POST | `/api/ice/upload` · `/api/ice/process` | Ice detection |
| POST | `/api/volume/upload` · `/api/volume/process` | Ice volume |
| POST | `/api/landing/upload` · `/api/landing/process` | Safe landing |
| POST | `/api/path/upload` · `/api/path/process` | Path planning |
| POST | `/api/confidence/upload` · `/api/confidence/process` | AI confidence |
| GET | `/api/dashboard` | Aggregated dashboard metrics |
| GET | `/api/sample/{name}` | Download a bundled sample dataset |
| GET | `/api/download/{filename}` | Download a generated artefact |

---

## Tech Stack

**Frontend:** React 19, Vite, Tailwind CSS v4, React Router, Recharts,
Framer Motion, Leaflet, React Dropzone, React Hook Form, React Hot Toast,
Lucide React, React Icons, Axios.

**Backend / ML:** FastAPI, Uvicorn, NumPy, pandas, SciPy, scikit-learn,
NetworkX, Matplotlib, OpenCV, Pillow, Joblib, Pydantic (optional: PyTorch,
Transformers, Rasterio, pds4_tools).

No database required — everything is processed locally.
