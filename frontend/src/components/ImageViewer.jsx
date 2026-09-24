import { useState } from "react";
import { ImageOff, ZoomIn, X } from "lucide-react";
import { outputUrl } from "../services/api.js";

/**
 * Displays a generated PNG artefact (heatmap / map) with a click-to-zoom modal.
 * Accepts either a bare backend filename or an absolute URL.
 */
export default function ImageViewer({ filename, url, alt = "Generated map", caption }) {
  const [zoom, setZoom] = useState(false);
  const src = url || outputUrl(filename);

  if (!src) {
    return (
      <div className="flex h-48 flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-slate-700/50 text-slate-500">
        <ImageOff className="h-8 w-8" />
        <p className="text-xs">No image available</p>
      </div>
    );
  }

  return (
    <>
      <figure className="group relative overflow-hidden rounded-xl border border-slate-700/40">
        <img src={src} alt={alt} className="w-full bg-space-800 object-contain" />
        <button
          onClick={() => setZoom(true)}
          className="absolute right-2 top-2 rounded-lg bg-space-900/70 p-1.5 text-slate-200 opacity-0 transition group-hover:opacity-100"
          aria-label="Zoom image"
        >
          <ZoomIn className="h-4 w-4" />
        </button>
        {caption && (
          <figcaption className="bg-space-900/60 px-3 py-1.5 text-xs text-slate-400">
            {caption}
          </figcaption>
        )}
      </figure>

      {zoom && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-6"
          onClick={() => setZoom(false)}
        >
          <button
            className="absolute right-6 top-6 rounded-lg bg-space-700 p-2 text-white"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
          <img
            src={src}
            alt={alt}
            className="max-h-[90vh] max-w-[90vw] rounded-xl object-contain"
          />
        </div>
      )}
    </>
  );
}
