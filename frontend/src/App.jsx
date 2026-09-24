import { useState } from "react";
import { Route, Routes } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Sidebar from "./components/Sidebar.jsx";
import Navbar from "./components/Navbar.jsx";
import { ResultsProvider } from "./context/ResultsContext.jsx";

import Dashboard from "./pages/Dashboard.jsx";
import IceDetection from "./pages/IceDetection.jsx";
import IceVolume from "./pages/IceVolume.jsx";
import LandingSite from "./pages/LandingSite.jsx";
import PathPlanning from "./pages/PathPlanning.jsx";
import AIConfidence from "./pages/AIConfidence.jsx";
import Results from "./pages/Results.jsx";
import Settings from "./pages/Settings.jsx";

export default function App() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <ResultsProvider>
      <div className="flex min-h-screen text-slate-100">
        <Sidebar collapsed={collapsed} />
        <div className="flex min-h-screen flex-1 flex-col">
          <Navbar onToggleSidebar={() => setCollapsed((c) => !c)} />
          <main className="flex-1 overflow-y-auto p-4 md:p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/ice-detection" element={<IceDetection />} />
              <Route path="/ice-volume" element={<IceVolume />} />
              <Route path="/landing-site" element={<LandingSite />} />
              <Route path="/path-planning" element={<PathPlanning />} />
              <Route path="/ai-confidence" element={<AIConfidence />} />
              <Route path="/results" element={<Results />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "#121a33",
              color: "#e2e8f0",
              border: "1px solid rgba(148,163,184,0.2)",
            },
          }}
        />
      </div>
    </ResultsProvider>
  );
}
