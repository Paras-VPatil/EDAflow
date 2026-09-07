import React, { useState } from 'react';
import { GitCompare, AlertTriangle, CheckCircle2, Activity, TrendingUp } from 'lucide-react';
import { SampleDatasetMeta, DriftReport } from '../../types/eda';
import { runDriftAnalysis } from '../../api/client';

interface DriftSectionProps {
  currentDatasetId: string;
  currentDatasetName: string;
  sampleDatasets: SampleDatasetMeta[];
}

export const DriftSection: React.FC<DriftSectionProps> = ({
  currentDatasetId,
  currentDatasetName,
  sampleDatasets,
}) => {
  const [comparisonDatasetId, setComparisonDatasetId] = useState<string>('');
  const [driftReport, setDriftReport] = useState<DriftReport | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunDrift = async () => {
    if (!comparisonDatasetId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await runDriftAnalysis(currentDatasetId, comparisonDatasetId);
      setDriftReport(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to calculate dataset drift.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="bg-surface-card border border-surface-border rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <GitCompare className="w-3.5 h-3.5" />
              Dataset Comparison & Statistical Drift
            </div>
            <h2 className="text-xl font-bold text-white">Compare Against Another Dataset</h2>
            <p className="text-sm text-text-muted mt-1">
              Compare <strong className="text-primary-400">{currentDatasetName}</strong> (Baseline) with another dataset to detect schema mismatches, missingness shifts, and Kolmogorov-Smirnov distribution drift.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={comparisonDatasetId}
              onChange={(e) => setComparisonDatasetId(e.target.value)}
              className="bg-surface-muted border border-surface-border rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-primary-500"
            >
              <option value="">Select comparison dataset...</option>
              {sampleDatasets
                .filter((s) => s.dataset_id !== currentDatasetId)
                .map((s) => (
                  <option key={s.dataset_id} value={s.dataset_id}>
                    {s.filename} ({s.rows} rows)
                  </option>
                ))}
            </select>

            <button
              onClick={handleRunDrift}
              disabled={!comparisonDatasetId || isLoading}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-primary-500 to-accent-indigo text-white text-sm font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-primary-500/20 flex items-center gap-2 whitespace-nowrap"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Calculating Drift...
                </>
              ) : (
                <>
                  <Activity className="w-4 h-4" />
                  Run Drift Analysis
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-4 rounded-xl bg-status-danger/10 border border-status-danger/20 text-status-danger text-sm flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}
      </div>

      {/* Results */}
      {driftReport && (
        <div className="space-y-6 animate-fade-in">
          {/* Top Drift Score Banner */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-surface-card border border-surface-border rounded-2xl p-5">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Overall Drift Status</span>
              <p className={`text-xl font-bold mt-1 ${driftReport.drift_summary.drift_score_pct > 20 ? 'text-status-danger' : 'text-status-success'}`}>
                {driftReport.drift_summary.overall_status}
              </p>
              <span className="text-xs text-text-muted">
                {driftReport.drift_summary.drifted_features_count} of {driftReport.drift_summary.total_numeric_evaluated} features drifted ({driftReport.drift_summary.drift_score_pct}%)
              </span>
            </div>

            <div className="bg-surface-card border border-surface-border rounded-2xl p-5">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Baseline Rows</span>
              <p className="text-2xl font-bold text-white mt-1">
                {driftReport.baseline_summary.rows.toLocaleString()}
              </p>
              <span className="text-xs text-text-muted">{driftReport.baseline_summary.columns} columns</span>
            </div>

            <div className="bg-surface-card border border-surface-border rounded-2xl p-5">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Comparison Rows</span>
              <p className="text-2xl font-bold text-white mt-1">
                {driftReport.comparison_summary.rows.toLocaleString()}
              </p>
              <span className="text-xs text-text-muted">{driftReport.comparison_summary.columns} columns</span>
            </div>

            <div className="bg-surface-card border border-surface-border rounded-2xl p-5">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Common Features</span>
              <p className="text-2xl font-bold text-primary-400 mt-1">
                {driftReport.schema_drift.common_columns_count}
              </p>
              <span className="text-xs text-text-muted">Evaluated across both sets</span>
            </div>
          </div>

          {/* Numerical Drift Table */}
          {driftReport.numeric_drift.length > 0 && (
            <div className="bg-surface-card border border-surface-border rounded-2xl p-6">
              <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-primary-400" />
                Kolmogorov-Smirnov & Population Stability Index (PSI) Drift
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-surface-border text-text-muted bg-surface-muted/30">
                      <th className="p-3 font-semibold">Feature</th>
                      <th className="p-3 font-semibold">Baseline Mean ± Std</th>
                      <th className="p-3 font-semibold">Comparison Mean ± Std</th>
                      <th className="p-3 font-semibold">KS Statistic (p-val)</th>
                      <th className="p-3 font-semibold">PSI Score</th>
                      <th className="p-3 font-semibold">Drift Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {driftReport.numeric_drift.map((num) => (
                      <tr key={num.column} className="border-b border-surface-border/40 hover:bg-surface-muted/20">
                        <td className="p-3 font-bold text-white">{num.column}</td>
                        <td className="p-3 font-mono text-text-secondary">{num.baseline_mean} ± {num.baseline_std}</td>
                        <td className="p-3 font-mono text-text-secondary">{num.comparison_mean} ± {num.comparison_std}</td>
                        <td className="p-3 font-mono text-text-muted">{num.ks_statistic} (p={num.p_value.toFixed(4)})</td>
                        <td className="p-3 font-mono text-text-muted">{num.psi.toFixed(4)}</td>
                        <td className="p-3">
                          {num.has_drift ? (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full font-semibold bg-status-danger/10 text-status-danger border border-status-danger/20">
                              <AlertTriangle className="w-3 h-3" />
                              Drift Detected ({num.severity})
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full font-semibold bg-status-success/10 text-status-success border border-status-success/20">
                              <CheckCircle2 className="w-3 h-3" />
                              Stable
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
