import { useEffect } from "react";
import { BrainCircuit, Gauge, Target, Activity, Grid3x3 } from "lucide-react";
import PageHeader from "../components/common/PageHeader.jsx";
import DatasetUploader from "../components/DatasetUploader.jsx";
import RunButton from "../components/common/RunButton.jsx";
import SampleLoader from "../components/common/SampleLoader.jsx";
import ProgressBar from "../components/common/ProgressBar.jsx";
import ResultCard from "../components/ResultCard.jsx";
import StatCard from "../components/Cards/StatCard.jsx";
import ChartCard from "../components/ChartCard.jsx";
import BarChartView from "../components/Charts/BarChartView.jsx";
import LineChartView from "../components/Charts/LineChartView.jsx";
import GaugeView from "../components/Charts/GaugeView.jsx";
import ConfusionMatrix from "../components/Charts/ConfusionMatrix.jsx";
import DownloadButton from "../components/DownloadButton.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import { useModuleProcessor } from "../hooks/useModuleProcessor.js";
import { useResults } from "../context/ResultsContext.jsx";
import { ConfidenceAPI } from "../services/api.js";
import { formatPercent, formatNumber } from "../utils/format.js";

export default function AIConfidence() {
  const proc = useModuleProcessor(ConfidenceAPI);
  const { saveResult } = useResults();

  useEffect(() => {
    if (proc.result) saveResult("confidence", proc.result);
  }, [proc.result, saveResult]);

  const r = proc.result;
  const m = r?.metrics;

  const importanceData = (r?.feature_importance || []).map((f) => ({
    name: f.feature,
    value: Number((f.importance * 100).toFixed(2)),
  }));

  const rocData = (r?.roc_curve || []).map((p) => ({
    x: Number(p.fpr.toFixed(3)),
    tpr: Number(p.tpr.toFixed(3)),
    diagonal: Number(p.fpr.toFixed(3)),
  }));

  return (
    <div>
      <PageHeader
        icon={BrainCircuit}
        title="Module 5 · AI Confidence"
        subtitle="Classifier evaluation: accuracy, precision/recall, F1, ROC-AUC & mission confidence"
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <ResultCard title="Upload & Process">
          <DatasetUploader
            file={proc.file}
            onFile={proc.setFile}
            label="Dataset CSV"
          />
          <div className="mt-3">
            <SampleLoader onLoaded={proc.setFile} />
          </div>
          <RunButton
            onRun={() => proc.run()}
            onReset={proc.reset}
            isBusy={proc.isBusy}
            disabled={!proc.file}
            label="Evaluate Model"
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
              icon={BrainCircuit}
              title="No evaluation yet"
              message="Upload a dataset (or load the sample) and evaluate the classifier."
            />
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <StatCard
                  icon={Target}
                  label="Accuracy"
                  value={formatPercent(m.accuracy)}
                  accent="blue"
                />
                <StatCard
                  icon={Activity}
                  label="F1 Score"
                  value={formatPercent(m.f1_score)}
                  accent="purple"
                />
                <StatCard
                  icon={Activity}
                  label="ROC-AUC"
                  value={formatPercent(m.roc_auc)}
                  accent="cyan"
                />
                <StatCard
                  icon={Gauge}
                  label="Mission Conf."
                  value={formatNumber(m.mission_confidence_percent, 1)}
                  unit="%"
                  accent="green"
                />
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <ChartCard title="Mission Confidence" height={220}>
                  <GaugeView
                    value={m.mission_confidence_percent}
                    label="Confidence %"
                  />
                </ChartCard>
                <ChartCard title="Feature Importance (%)" icon={BrainCircuit}>
                  <BarChartView data={importanceData} colorful />
                </ChartCard>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <ChartCard title="ROC Curve" icon={Activity}>
                  <LineChartView
                    data={rocData}
                    xKey="x"
                    lines={[
                      { key: "tpr", color: "#4f8cff", name: "ROC" },
                      { key: "diagonal", color: "#64748b", name: "Chance" },
                    ]}
                  />
                </ChartCard>
                <ResultCard title="Confusion Matrix" icon={Grid3x3}>
                  <ConfusionMatrix
                    matrix={r.confusion_matrix}
                    labels={r.confusion_matrix_labels}
                  />
                  <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-300">
                    <span>Precision: {formatPercent(m.precision)}</span>
                    <span>· Recall: {formatPercent(m.recall)}</span>
                  </div>
                  <div className="mt-3">
                    <DownloadButton
                      filename={r.artifacts?.report_json}
                      label="Report JSON"
                    />
                  </div>
                </ResultCard>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
