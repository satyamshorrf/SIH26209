import axios from "axios";

// Base URL: in development requests are proxied by Vite to the FastAPI backend.
// Override with VITE_API_BASE_URL when deploying frontend and backend separately.
const baseURL = import.meta.env.VITE_API_BASE_URL || "";

export const api = axios.create({
  baseURL,
  timeout: 120000,
});

/** Absolute URL for a generated output artefact (PNG/CSV/JSON). */
export function outputUrl(filename) {
  if (!filename) return null;
  return `${baseURL}/outputs/${filename}`;
}

/** Absolute URL for the download endpoint of a generated artefact. */
export function downloadUrl(filename) {
  if (!filename) return null;
  return `${baseURL}/api/download/${filename}`;
}

/** Build a multipart FormData body from a plain object. */
function toFormData(fields) {
  const fd = new FormData();
  Object.entries(fields).forEach(([key, value]) => {
    if (value !== undefined && value !== null) fd.append(key, value);
  });
  return fd;
}

/** Generic upload helper used by every module. */
async function uploadFile(endpoint, fields) {
  const { data } = await api.post(endpoint, toFormData(fields), {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

/** Generic process helper used by every module. */
async function process(endpoint, fields) {
  const { data } = await api.post(endpoint, toFormData(fields), {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export const DashboardAPI = {
  get: async () => (await api.get("/api/dashboard")).data,
  health: async () => (await api.get("/api/health")).data,
};

/** Fetch a bundled sample dataset and return it as a File for the uploader. */
export async function fetchSampleFile(name = "sample_dfsar.csv") {
  const { data } = await api.get(`/api/sample/${name}`, {
    responseType: "blob",
  });
  return new File([data], name, { type: "text/csv" });
}

export const IceAPI = {
  upload: (dfsarFile, ohrcFile) =>
    uploadFile("/api/ice/upload", { dfsar_file: dfsarFile, ohrc_file: ohrcFile }),
  process: (dfsarStored, ohrcStored) =>
    process("/api/ice/process", {
      dfsar_file: dfsarStored,
      ohrc_file: ohrcStored,
    }),
};

export const VolumeAPI = {
  upload: (file) => uploadFile("/api/volume/upload", { dataset_file: file }),
  process: (stored, depth = 5.0) =>
    process("/api/volume/process", { dataset_file: stored, depth_m: depth }),
};

export const LandingAPI = {
  upload: (file) => uploadFile("/api/landing/upload", { dataset_file: file }),
  process: (stored) =>
    process("/api/landing/process", { dataset_file: stored }),
};

export const PathAPI = {
  upload: (file) => uploadFile("/api/path/upload", { dataset_file: file }),
  process: (stored, algorithm = "astar", gridSize = 40) =>
    process("/api/path/process", {
      dataset_file: stored,
      algorithm,
      grid_size: gridSize,
    }),
};

export const ConfidenceAPI = {
  upload: (file) => uploadFile("/api/confidence/upload", { dataset_file: file }),
  process: (stored) =>
    process("/api/confidence/process", { dataset_file: stored }),
};
