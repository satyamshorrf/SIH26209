import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, Image as ImageIcon, X } from "lucide-react";
import { formatBytes } from "../utils/format.js";

/**
 * Drag-and-drop dataset uploader supporting a primary file (CSV) and an optional
 * secondary file (e.g. OHRC image).  Selection is controlled by the parent.
 */
export default function DatasetUploader({
  file,
  onFile,
  accept = { "text/csv": [".csv"] },
  label = "DFSAR CSV dataset",
  hint = "Drag & drop a .csv file here, or click to browse",
  icon: Icon = FileText,
}) {
  const onDrop = useCallback(
    (accepted) => {
      if (accepted && accepted.length > 0) onFile(accepted[0]);
    },
    [onFile]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple: false,
  });

  return (
    <div>
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </p>

      {file ? (
        <div className="flex items-center justify-between rounded-xl border border-slate-700/50 bg-space-700/40 p-3">
          <div className="flex items-center gap-3">
            <Icon className="h-5 w-5 text-accent-blue" />
            <div className="leading-tight">
              <p className="text-sm font-medium text-white">{file.name}</p>
              <p className="text-xs text-slate-400">{formatBytes(file.size)}</p>
            </div>
          </div>
          <button
            onClick={() => onFile(null)}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-600/40 hover:text-white"
            aria-label="Remove file"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <div
          {...getRootProps()}
          className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed p-6 text-center transition ${
            isDragActive
              ? "border-accent-blue bg-accent-blue/10"
              : "border-slate-700/60 hover:border-accent-blue/60 hover:bg-space-700/30"
          }`}
        >
          <input {...getInputProps()} />
          <UploadCloud className="h-8 w-8 text-accent-blue" />
          <p className="text-sm text-slate-300">{hint}</p>
        </div>
      )}
    </div>
  );
}

export { ImageIcon };
