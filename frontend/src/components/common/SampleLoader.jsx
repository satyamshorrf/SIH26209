import { useState } from "react";
import { Database, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import { fetchSampleFile } from "../../services/api.js";

/**
 * Button that loads a bundled sample dataset into the module uploader so the
 * full workflow can be tested without external files.
 */
export default function SampleLoader({ onLoaded, name = "sample_dfsar.csv" }) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      const file = await fetchSampleFile(name);
      onLoaded(file);
      toast.success("Sample dataset loaded.");
    } catch {
      toast.error("Could not load sample dataset.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-slate-600/60 px-3 py-2 text-xs font-medium text-slate-300 transition hover:bg-slate-700/40 disabled:opacity-50"
    >
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <Database className="h-4 w-4" />
      )}
      Load sample dataset
    </button>
  );
}
