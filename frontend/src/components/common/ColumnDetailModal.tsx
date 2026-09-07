import React from 'react';
import { X, Layers, BarChart2 } from 'lucide-react';
import { ColumnProfile, FullEDAReport } from '../../types/eda';

interface ColumnDetailModalProps {
  column: ColumnProfile | null;
  report: FullEDAReport;
  onClose: () => void;
}

export const ColumnDetailModal: React.FC<ColumnDetailModalProps> = ({ column, report, onClose }) => {
  if (!column) return null;

  const numStats = report.distributions.columns[column.name];
  const catStats = report.categorical.columns.find((c) => c.column === column.name);
  const outlierStats = report.outliers.columns.find((o) => o.column === column.name);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-surface-card border border-surface-border rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl animate-scale-up">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-surface-border bg-surface-muted/30">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary-500/10 text-primary-400 border border-primary-500/20">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                {column.name}
                <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-surface-border text-primary-300">
                  {column.inferred_type}
                </span>
              </h3>
              <p className="text-xs text-text-muted">Storage Dtype: {column.dtype}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-text-muted hover:text-white hover:bg-surface-border/50 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto custom-scrollbar">
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-surface-muted/40 p-3.5 rounded-xl border border-surface-border/50">
              <span className="text-[11px] font-semibold text-text-muted uppercase tracking-wider">Unique Values</span>
              <p className="text-lg font-bold text-white mt-1">
                {column.unique_count.toLocaleString()}
              </p>
              <span className="text-xs text-text-muted">{(column.unique_ratio * 100).toFixed(1)}% of rows</span>
            </div>

            <div className="bg-surface-muted/40 p-3.5 rounded-xl border border-surface-border/50">
              <span className="text-[11px] font-semibold text-text-muted uppercase tracking-wider">Missing Count</span>
              <p className="text-lg font-bold text-white mt-1">
                {column.null_count.toLocaleString()}
              </p>
              <span className="text-xs text-text-muted">{(column.null_ratio * 100).toFixed(1)}% missing</span>
            </div>

            <div className="bg-surface-muted/40 p-3.5 rounded-xl border border-surface-border/50">
              <span className="text-[11px] font-semibold text-text-muted uppercase tracking-wider">Memory Size</span>
              <p className="text-lg font-bold text-white mt-1">
                {(column.memory_bytes / 1024).toFixed(1)} KB
              </p>
              <span className="text-xs text-text-muted">Deep footprint</span>
            </div>

            <div className="bg-surface-muted/40 p-3.5 rounded-xl border border-surface-border/50">
              <span className="text-[11px] font-semibold text-text-muted uppercase tracking-wider">Outliers (IQR)</span>
              <p className="text-lg font-bold text-white mt-1">
                {outlierStats ? outlierStats.iqr_outliers_count.toLocaleString() : 'N/A'}
              </p>
              <span className="text-xs text-text-muted">
                {outlierStats ? `${outlierStats.iqr_percentage}%` : 'Categorical / Non-numeric'}
              </span>
            </div>
          </div>

          {/* Numerical Statistics (if numeric) */}
          {numStats && (
            <div className="bg-surface-muted/20 border border-surface-border rounded-xl p-4 space-y-3">
              <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-accent-blue" />
                Distribution Metrics
              </h4>
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 text-xs">
                <div className="p-2 bg-surface-card rounded-lg border border-surface-border/40">
                  <span className="text-text-muted block">Mean</span>
                  <span className="font-mono font-medium text-white">{numStats.mean.toFixed(2)}</span>
                </div>
                <div className="p-2 bg-surface-card rounded-lg border border-surface-border/40">
                  <span className="text-text-muted block">Median</span>
                  <span className="font-mono font-medium text-white">{numStats.median.toFixed(2)}</span>
                </div>
                <div className="p-2 bg-surface-card rounded-lg border border-surface-border/40">
                  <span className="text-text-muted block">Std Dev</span>
                  <span className="font-mono font-medium text-white">{numStats.std.toFixed(2)}</span>
                </div>
                <div className="p-2 bg-surface-card rounded-lg border border-surface-border/40">
                  <span className="text-text-muted block">Min</span>
                  <span className="font-mono font-medium text-white">{numStats.min}</span>
                </div>
                <div className="p-2 bg-surface-card rounded-lg border border-surface-border/40">
                  <span className="text-text-muted block">Max</span>
                  <span className="font-mono font-medium text-white">{numStats.max}</span>
                </div>
                <div className="p-2 bg-surface-card rounded-lg border border-surface-border/40">
                  <span className="text-text-muted block">Skewness</span>
                  <span className="font-mono font-medium text-white">{numStats.skewness.toFixed(2)}</span>
                </div>
              </div>
            </div>
          )}

          {/* Top Categories Breakdown (if categorical) */}
          {catStats && catStats.frequencies.length > 0 && (
            <div className="bg-surface-muted/20 border border-surface-border rounded-xl p-4 space-y-3">
              <h4 className="text-sm font-semibold text-white">Top Frequency Distribution</h4>
              <div className="space-y-2">
                {catStats.frequencies.slice(0, 6).map((freq) => (
                  <div key={freq.category} className="space-y-1">
                    <div className="flex justify-between text-xs text-text-muted">
                      <span className="text-white font-medium truncate max-w-[200px]">{freq.category}</span>
                      <span>{freq.count.toLocaleString()} ({freq.percentage}%)</span>
                    </div>
                    <div className="w-full h-1.5 bg-surface-border rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-500 rounded-full"
                        style={{ width: `${Math.min(freq.percentage, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sample Values */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              Sample Distinct Values
            </h4>
            <div className="flex flex-wrap gap-2">
              {column.sample_values.map((val, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 rounded-lg bg-surface-muted border border-surface-border text-xs font-mono text-text-secondary"
                >
                  {String(val)}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-surface-border bg-surface-muted/30 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-surface-card border border-surface-border text-sm font-medium text-white hover:bg-surface-border/50 transition-colors"
          >
            Close Drill-down
          </button>
        </div>
      </div>
    </div>
  );
};
