import { useEffect, useState } from "react";
import { Settings as SettingsIcon, Server, CheckCircle2, XCircle } from "lucide-react";
import PageHeader from "../components/common/PageHeader.jsx";
import ResultCard from "../components/ResultCard.jsx";
import { DashboardAPI } from "../services/api.js";

export default function Settings() {
  const [online, setOnline] = useState(null);
  const apiBase = import.meta.env.VITE_API_BASE_URL || "(Vite dev proxy → :8000)";

  useEffect(() => {
    DashboardAPI.health()
      .then(() => setOnline(true))
      .catch(() => setOnline(false));
  }, []);

  return (
    <div>
      <PageHeader
        icon={SettingsIcon}
        title="Settings"
        subtitle="Application configuration and backend connectivity"
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <ResultCard title="Backend Connection" icon={Server}>
          <div className="space-y-3 text-sm text-slate-300">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">API base URL</span>
              <span className="font-mono text-xs text-white">{apiBase}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Status</span>
              <span
                className={`inline-flex items-center gap-1.5 font-medium ${
                  online ? "text-emerald-300" : "text-red-300"
                }`}
              >
                {online ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <XCircle className="h-4 w-4" />
                )}
                {online === null ? "Checking…" : online ? "Connected" : "Offline"}
              </span>
            </div>
          </div>
        </ResultCard>

        <ResultCard title="About" icon={SettingsIcon}>
          <div className="space-y-2 text-sm text-slate-300">
            <p>
              <span className="font-semibold text-white">
                Lunar AI Ice Detection System
              </span>{" "}
              v1.0.0
            </p>
            <p>
              Smart India Hackathon 2026 · Problem Statement-Student Innovation-Space technology refers to the application of engineering principles to the design, development, manufacture, and operation of devices and systems for space travel and exploration.
            </p>
            <p className="text-slate-400">
              Built with React 19, Vite, Tailwind CSS v4 and FastAPI. Datasets:
              Chandrayaan-2 DFSAR &amp; OHRC.
            </p>
          </div>
        </ResultCard>

       
      </div>
    </div>
  );
}
