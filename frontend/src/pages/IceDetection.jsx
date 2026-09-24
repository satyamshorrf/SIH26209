import { useEffect } from "react";
import { Snowflake, Image as ImageIcon, Percent, Gauge, Table2 } from "lucide-react";
import PageHeader from "../components/common/PageHeader.jsx";
import DatasetUploader from "../components/DatasetUploader.jsx";
import RunButton from "../components/common/RunButton.jsx";
import SampleLoader from "../components/common/SampleLoader.jsx";
import ProgressBar from "../components/common/ProgressBar.jsx";
import ResultCard from "../components/ResultCard.jsx";
import StatCard from "../components/Cards/StatCard.jsx";
import ImageViewer from "../components/ImageViewer.jsx";
import DownloadButton from "../components/DownloadButton.jsx";
import DataTable from "../components/common/DataTable.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import { useModuleProcessor } from "../hooks/useModuleProcessor.js";
import { useResults } from "../context/ResultsContext.jsx";
import { IceAPI } from "../services/api.js";
import { formatNumber, formatPercent } from "../utils/format.js";

export default function IceDetection() {
  const proc = useModuleProcessor(IceAPI);
  const { saveResult } = useResults();

  useEffect(() => {
    if (proc.result) saveResult("ice", proc.result);
  }, [proc.result, saveResult]);

  const r = proc.result;

  return (
    <div>
      <PageHeader
        icon={Snowflake}
        title="Module 1 · Ice Detection"
        subtitle="CPR / DOP radar polarimetry + ML classification of subsurface water-ice"
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <ResultCard title="Upload & Process" className="lg:col-span-1">
          <DatasetUploader
            file={proc.file}
            onFile={proc.setFile}
            label="DFSAR CSV dataset"
          />
          <div className="mt-4">
            <DatasetUploader
              file={proc.secondaryFile}
              onFile={proc.setSecondaryFile}
              accept={{ "image/*": [".png", ".jpg", ".jpeg", ".tif", ".tiff"] }}
              label="OHRC image (optional)"
              hint="Drag & drop a PNG / TIF / JPEG, or click to browse"
              icon={ImageIcon}
            />
          </div>
          <div className="mt-3">
            <SampleLoader onLoaded={proc.setFile} />
          </div>
          <RunButton
            onRun={() => proc.run()}
            onReset={proc.reset}
            isBusy={proc.isBusy}
            disabled={!proc.file}
            label="Detect Ice"
          />
          <ProgressBar progress={proc.progress} status={proc.status} />
          {proc.error && (
            <p className="mt-3 rounded-lg border border-red-500/30 bg-red-500/10 p-2 text-xs text-red-300">
              {proc.error}
            </p>
          )}
        </ResultCard>

        <div className="lg:col-span-2">
          {!r ? (
            <EmptyState
              icon={Snowflake}
              title="No detection yet"
              message="Upload a DFSAR CSV (or load the sample) and run ice detection."
            />
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <StatCard
                  icon={Percent}
                  label="Ice Detected"
                  value={formatNumber(r.ice_detection_percent, 2)}
                  unit="%"
                  accent="blue"
                />
                <StatCard
                  icon={Snowflake}
                  label="Ice Points"
                  value={formatNumber(r.detected_points, 0)}
                  accent="cyan"
                />
                <StatCard
                  icon={Table2}
                  label="Total Points"
                  value={formatNumber(r.total_points, 0)}
                  accent="purple"
                />
                <StatCard
                  icon={Gauge}
                  label="Mean Probability"
                  value={formatPercent(r.mean_ice_probability)}
                  accent="green"
                />
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <ResultCard title="Ice Probability Heatmap" icon={Snowflake}>
                  <ImageViewer
                    filename={r.artifacts?.heatmap_png}
                    alt="Ice probability heatmap"
                  />
                </ResultCard>
                <ResultCard title="Confidence & Downloads" icon={Gauge}>
                  {r.confidence && (
                    <ul className="space-y-1 text-sm text-slate-300">
                      <li>
                        Accuracy: {formatPercent(r.confidence.accuracy)}
                      </li>
                      <li>F1 Score: {formatPercent(r.confidence.f1_score)}</li>
                      <li>ROC-AUC: {formatPercent(r.confidence.roc_auc)}</li>
                      <li>
                        Mission Confidence:{" "}
                        {formatNumber(
                          r.confidence.mission_confidence_percent,
                          1
                        )}
                        %
                      </li>
                    </ul>
                  )}
                  <div className="mt-4 flex flex-wrap gap-2">
                    <DownloadButton
                      filename={r.artifacts?.detection_csv}
                      label="Detection CSV"
                    />
                    <DownloadButton
                      filename={r.artifacts?.mask_csv}
                      label="Mask CSV"
                      variant="ghost"
                    />
                  </div>
                  {r.ohrc && !r.ohrc.error && (
                    <div className="mt-4 rounded-lg border border-slate-700/40 bg-space-700/30 p-3 text-xs text-slate-300">
                      <p className="font-semibold text-slate-200">OHRC analysis</p>
                      <p>
                        Shadow fraction:{" "}
                        {formatPercent(r.ohrc.shadow_fraction)} · Boulder density:{" "}
                        {formatPercent(r.ohrc.boulder_density)}
                      </p>
                    </div>
                  )}
                </ResultCard>
              </div>

              <ResultCard title="Detection Preview" icon={Table2}>
                <DataTable rows={r.preview} />
              </ResultCard>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
