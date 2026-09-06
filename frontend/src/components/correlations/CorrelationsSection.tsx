import React, { useState } from 'react';
import { CorrelationsResult } from '../../types/eda';
import { GitCommit, ArrowUpRight, ArrowDownRight, AlertTriangle } from 'lucide-react';
import { Badge } from '../common/Badge';

interface CorrelationsSectionProps {
  correlations: CorrelationsResult;
}

export const CorrelationsSection: React.FC<CorrelationsSectionProps> = ({
  correlations,
}) => {
  const [method, setMethod] = useState<'pearson' | 'spearman'>('pearson');
  const [threshold, setThreshold] = useState<number>(0.5);

  const activeMatrix =
    method === 'pearson'
      ? correlations.pearson_matrix
      : correlations.spearman_matrix;

  const cols = correlations.numeric_columns;

  const getHeatmapColor = (val: number | null) => {
    if (val === null || val === undefined) return 'bg-slate-100 dark:bg-slate-900 text-slate-400 dark:text-slate-600';
    if (val === 1.0) return 'bg-indigo-600 text-white font-bold';
    if (val >= 0.7) return 'bg-blue-600 text-white font-semibold';
    if (val >= 0.4) return 'bg-blue-500/30 text-blue-800 dark:text-blue-200';
    if (val >= 0.1) return 'bg-blue-500/10 text-slate-700 dark:text-slate-300';
    if (val > -0.1) return 'bg-slate-100 dark:bg-dark-900 text-slate-500 dark:text-slate-400';
    if (val > -0.4) return 'bg-rose-500/10 text-slate-700 dark:text-slate-300';
    if (val > -0.7) return 'bg-rose-500/30 text-rose-800 dark:text-rose-200';
    return 'bg-rose-600 text-white font-semibold';
  };

  const filteredPositivePairs = correlations.top_positive_pairs.filter(
    (p) => Math.abs(p.correlation) >= threshold
  );

  const filteredNegativePairs = correlations.top_negative_pairs.filter(
    (p) => Math.abs(p.correlation) >= threshold
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* 1. Header & Controls */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2">
              <GitCommit className="w-5 h-5 text-brand-600 dark:text-brand-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                Correlation Matrix & Multicollinearity
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Evaluates linear (Pearson) and monotonic rank (Spearman) relationships between numeric features.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Method Toggle */}
            <div className="flex rounded-xl bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 p-0.5 text-xs">
              <button
                onClick={() => setMethod('pearson')}
                className={`px-3 py-1 rounded-lg font-semibold transition-all ${
                  method === 'pearson'
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Pearson (Linear)
              </button>
              <button
                onClick={() => setMethod('spearman')}
                className={`px-3 py-1 rounded-lg font-semibold transition-all ${
                  method === 'spearman'
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Spearman (Rank)
              </button>
            </div>

            {/* Threshold Slider */}
            <div className="flex items-center gap-2 bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-1.5 text-xs">
              <span className="text-slate-600 dark:text-slate-400">Filter |r| ≥</span>
              <input
                type="range"
                min="0.2"
                max="0.9"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-20 accent-brand-500 cursor-pointer"
              />
              <span className="font-mono font-bold text-brand-600 dark:text-brand-400">{threshold.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Statistical Best Practice Banner */}
        <div className="mb-6 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-start gap-2 text-xs text-amber-700 dark:text-amber-300">
          <AlertTriangle className="w-4 h-4 text-amber-500 dark:text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <strong>Statistical Best Practice:</strong> Correlation does not imply causation. High collinearity (|r| &gt; 0.80) inflates parameter variance in linear models and can indicate redundant feature engineering.
          </div>
        </div>

        {/* Correlation Heatmap Grid */}
        {cols.length > 0 ? (
          <div className="overflow-x-auto pb-2">
            <div className="inline-block min-w-full">
              <table className="border-collapse text-xs">
                <thead>
                  <tr>
                    <th className="p-2 text-left font-semibold text-slate-500 dark:text-slate-400 w-32 truncate"></th>
                    {cols.map((col) => (
                      <th
                        key={col}
                        className="p-2 text-center font-mono font-semibold text-slate-700 dark:text-slate-300 max-w-[90px] truncate"
                        title={col}
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {cols.map((rowCol) => (
                    <tr key={rowCol}>
                      <td
                        className="p-2 font-mono font-semibold text-slate-700 dark:text-slate-300 truncate max-w-[120px]"
                        title={rowCol}
                      >
                        {rowCol}
                      </td>
                      {cols.map((col) => {
                        const val = activeMatrix[rowCol]?.[col];
                        return (
                          <td key={col} className="p-1">
                            <div
                              className={`h-9 w-16 rounded-md flex items-center justify-center font-mono text-[11px] transition-all hover:scale-105 ${getHeatmapColor(
                                val
                              )}`}
                              title={`${rowCol} ↔ ${col}: ${val !== null && val !== undefined ? val : 'N/A'}`}
                            >
                              {val !== null && val !== undefined ? val.toFixed(2) : '-'}
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-slate-500 dark:text-slate-400">
            Fewer than 2 numeric features available for correlation analysis.
          </div>
        )}
      </div>

      {/* 2. Top Ranked Collinear Pairs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Positive Pairs */}
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <ArrowUpRight className="w-4 h-4 text-blue-500 dark:text-blue-400" />
            <h4 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight">
              Strong Positive Relationships (|r| ≥ {threshold.toFixed(2)})
            </h4>
          </div>

          <div className="space-y-2">
            {filteredPositivePairs.length > 0 ? (
              filteredPositivePairs.map((pair, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-50 dark:bg-dark-900/70 border border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs"
                >
                  <div className="font-semibold text-slate-800 dark:text-slate-200">
                    {pair.feature1} <span className="text-slate-400 dark:text-slate-500">↔</span> {pair.feature2}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="primary">{pair.strength.toUpperCase()}</Badge>
                    <span className="font-mono font-bold text-blue-600 dark:text-blue-400">
                      +{pair.correlation.toFixed(2)}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 dark:text-slate-400 py-4 text-center">
                No positive pairs above current threshold.
              </p>
            )}
          </div>
        </div>

        {/* Negative Pairs */}
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <ArrowDownRight className="w-4 h-4 text-rose-500 dark:text-rose-400" />
            <h4 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight">
              Strong Inverse Relationships (|r| ≥ {threshold.toFixed(2)})
            </h4>
          </div>

          <div className="space-y-2">
            {filteredNegativePairs.length > 0 ? (
              filteredNegativePairs.map((pair, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-50 dark:bg-dark-900/70 border border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs"
                >
                  <div className="font-semibold text-slate-800 dark:text-slate-200">
                    {pair.feature1} <span className="text-slate-400 dark:text-slate-500">↔</span> {pair.feature2}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="danger">{pair.strength.toUpperCase()}</Badge>
                    <span className="font-mono font-bold text-rose-600 dark:text-rose-400">
                      {pair.correlation.toFixed(2)}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 dark:text-slate-400 py-4 text-center">
                No inverse pairs above current threshold.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
