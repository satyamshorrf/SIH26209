import { useEffect, useState } from "react";
import { Menu, Satellite, Activity } from "lucide-react";
import { DashboardAPI } from "../services/api.js";

export default function Navbar({ onToggleSidebar }) {
  const [online, setOnline] = useState(null);

  useEffect(() => {
    let mounted = true;
    DashboardAPI.health()
      .then(() => mounted && setOnline(true))
      .catch(() => mounted && setOnline(false));
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <header className="glass sticky top-0 z-20 flex items-center justify-between border-b border-slate-700/40 px-4 py-3">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="rounded-lg p-2 text-slate-300 transition-colors hover:bg-slate-700/40 hover:text-white"
          aria-label="Toggle sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div className="flex items-center gap-2">
          <Satellite className="h-5 w-5 text-accent-blue" />
          <h1 className="text-base font-semibold text-white md:text-lg">
            Lunar Subsurface Ice Detection &amp; Rover Planning
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <span
          className={`flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${
            online === false
              ? "bg-red-500/15 text-red-300"
              : "bg-emerald-500/15 text-emerald-300"
          }`}
        >
          <Activity className="h-3.5 w-3.5" />
          {online === null
            ? "Connecting…"
            : online
            ? "Telemetry Online"
            : "Backend Offline"}
        </span>
      </div>
    </header>
  );
}
