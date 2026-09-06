import React, { useState } from 'react';
import { TargetAnalysisResult, ProfilerResult } from '../../types/eda';
import {
  Target,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';
import { Badge } from '../common/Badge';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface TargetSectionProps {
  targetResult: TargetAnalysisResult | null;
  profiler: ProfilerResult;
  onSelectTarget: (columnName: string) => void;
  isLoading: boolean;
}

export const TargetSection: React.FC<TargetSectionProps> = ({
  targetResult,
  profiler,
  onSelectTarget,
  isLoading,
}) => {
  const [selectedCol, setSelectedCol] = useState<string>(
    targetResult?.target_column || profiler.columns[profiler.columns.length - 1]?.name || ''
  );

  const handleRunTarget = () => {
    if (selectedCol) {
      onSelectTarget(selectedCol);
    }
  };

  const getTargetTypeBadge = (type: string) => {
    switch (type) {
      case 'binary_classification':
        return <Badge variant="primary">Binary Classification</Badge>;
      case 'multiclass_classification':
        return <Badge variant="info">Multiclass Classification</Badge>;
      case 'regression':
        return <Badge variant="success">Continuous Regression</Badge>;
      default:
        return <Badge variant="neutral">{type}</Badge>;
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* 1. Target Selector Header */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                Target Intelligence & ML Preparation
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Select your predictive target variable to evaluate class balance, feature importance proxies, and ML mitigations.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={selectedCol}
              onChange={(e) => setSelectedCol(e.target.value)}
              className="bg-white dark:bg-dark-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-900 dark:text-white focus:outline-none focus:border-brand-500 transition-colors"
            >
              <option value="" disabled>Select Target Column</option>
              {profiler.columns.map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name} ({c.inferred_type})
                </option>
              ))}
            </select>

            <button
              onClick={handleRunTarget}
              disabled={isLoading || !selectedCol}
              className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all disabled:opacity-50"
            >
              {isLoading ? 'Analyzing...' : 'Analyze Target'}
            </button>
          </div>
        </div>

        {targetResult ? (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800/80">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Target Variable:
                </span>
                <span className="text-base font-bold text-slate-900 dark:text-white">
                  {targetResult.target_column}
                </span>
                {getTargetTypeBadge(targetResult.target_type)}
              </div>

              {targetResult.imbalance_ratio !== null && targetResult.imbalance_ratio !== undefined && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-500 dark:text-slate-400">Class Imbalance Ratio:</span>
                  <span
                    className={`font-mono font-bold text-xs px-2.5 py-1 rounded-md border ${
                      targetResult.is_imbalanced
                        ? 'bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/30'
                        : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30'
                    }`}
                  >
                    {targetResult.imbalance_ratio}:1 ({targetResult.is_imbalanced ? 'Imbalanced' : 'Balanced'})
                  </span>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="mt-4 p-4 rounded-xl bg-slate-50 dark:bg-dark-900/50 border border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400 text-center">
            Select a target feature above and click "Analyze Target" to generate ML-readiness diagnostics.
          </div>
        )}
      </div>

      {targetResult && (
        <>
          {/* 2. Class Distribution / Regression Stats & Mitigations */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Visual Distribution */}
            <div className="lg:col-span-2 glass-panel rounded-2xl p-6">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight mb-4">
                {targetResult.target_type === 'regression'
                  ? 'Regression Target Distribution'
                  : 'Target Class Distribution & Frequency'}
              </h4>

              {targetResult.class_distribution ? (
                <div className="h-60 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={targetResult.class_distribution}
                      margin={{ top: 10, right: 30, left: 10, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis
                        dataKey="label"
                        tick={{ fill: '#64748b', fontSize: 11 }}
                      />
                      <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                      <Tooltip
                        formatter={(val: any, _, item: any) => [
                          `${val.toLocaleString()} records (${item.payload.percentage}%)`,
                          'Frequency',
                        ]}
                      />
                      <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                        {targetResult.class_distribution.map((_, idx) => (
                          <Cell
                            key={`cls-${idx}`}
                            fill={idx === 0 ? '#6366f1' : '#3b82f6'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : targetResult.regression_stats ? (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">Mean</span>
                    <div className="text-base font-mono font-bold text-slate-900 dark:text-white mt-1">
                      {targetResult.regression_stats.mean.toLocaleString()}
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">Median</span>
                    <div className="text-base font-mono font-bold text-slate-900 dark:text-white mt-1">
                      {targetResult.regression_stats.median.toLocaleString()}
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">Skewness</span>
                    <div className="text-base font-mono font-bold text-indigo-600 dark:text-indigo-400 mt-1">
                      {targetResult.regression_stats.skewness}
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">Std Dev</span>
                    <div className="text-base font-mono font-bold text-slate-900 dark:text-white mt-1">
                      {targetResult.regression_stats.std.toLocaleString()}
                    </div>
                  </div>
                </div>
              ) : null}
            </div>

            {/* Right: Mitigations & Guidelines */}
            <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="w-4 h-4 text-amber-500 dark:text-amber-400" />
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight">
                    ML-Readiness Action Plan
                  </h4>
                </div>

                <div className="space-y-2.5">
                  {targetResult.mitigations.map((mit, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-50 dark:bg-dark-900/80 border border-slate-200 dark:border-slate-800/80 text-xs text-slate-700 dark:text-slate-300 leading-relaxed flex items-start gap-2"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 flex-shrink-0 mt-0.5" />
                      <span>{mit}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4 p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-[11px] text-indigo-700 dark:text-indigo-300">
                🚀 <strong>Modeling Tip:</strong> Verify baseline benchmark performance against a Dummy / Zero-Rule Classifier before complex models.
              </div>
            </div>
          </div>

          {/* 3. Cross-Feature Breakdown */}
          {targetResult.feature_correlations.length > 0 && (
            <div className="glass-panel rounded-2xl p-6">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight mb-4">
                Feature Association with Target (Linear Correlation Proxy)
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {targetResult.feature_correlations.slice(0, 9).map((fc, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-slate-50 dark:bg-dark-900/60 border border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs"
                  >
                    <span className="font-semibold text-slate-800 dark:text-slate-200">
                      {fc.feature}
                    </span>
                    <span
                      className={`font-mono font-bold px-2 py-0.5 rounded ${
                        fc.correlation > 0
                          ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/30'
                          : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30'
                      }`}
                    >
                      r = {fc.correlation > 0 ? `+${fc.correlation}` : fc.correlation}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
