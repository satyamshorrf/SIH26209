import { Download } from "lucide-react";
import { downloadUrl } from "../services/api.js";

/**
 * Button that downloads a generated backend artefact by filename.
 */
export default function DownloadButton({ filename, label, variant = "solid" }) {
  if (!filename) return null;
  const href = downloadUrl(filename);

  const styles =
    variant === "ghost"
      ? "border border-slate-600/60 text-slate-200 hover:bg-slate-700/40"
      : "bg-gradient-to-r from-accent-blue to-accent-purple text-white hover:opacity-90";

  return (
    <a
      href={href}
      download
      className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition ${styles}`}
    >
      <Download className="h-4 w-4" />
      {label || "Download"}
    </a>
  );
}
