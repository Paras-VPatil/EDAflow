import React from 'react';
import { OutliersResult } from '../../types/eda';
import { ShieldAlert } from 'lucide-react';
import { Badge } from '../common/Badge';

interface OutliersSectionProps {
  outliers: OutliersResult;
}

export const OutliersSection: React.FC<OutliersSectionProps> = ({ outliers }) => {
  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* 1. Header & Multi-Method Explanation */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                Outlier Lab & Multi-Method Consensus
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 max-w-2xl">
              Cross-validates anomalies using three complementary paradigms: Non-parametric IQR, Parametric Z-Score, and Multivariate Isolation Forest.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2 text-right">
              <span className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">
                Multivariate Anomalies
              </span>
              <div className="text-lg font-mono font-bold text-purple-600 dark:text-purple-400">
                {outliers.multivariate_anomaly_count.toLocaleString()}{' '}
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  ({outliers.multivariate_anomaly_percentage}%)
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Multi-Method Method Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-dark-900/60 border border-slate-200 dark:border-slate-800/80">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-bold text-slate-900 dark:text-white">1. IQR Method</span>
              <Badge variant="primary">Non-Parametric</Badge>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
              Flags values outside Tukey's fences: <code className="text-indigo-600 dark:text-indigo-300 font-mono">[Q1 - 1.5×IQR, Q3 + 1.5×IQR]</code>. Robust to heavy tails.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 dark:bg-dark-900/60 border border-slate-200 dark:border-slate-800/80">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-bold text-slate-900 dark:text-white">2. Z-Score Method</span>
              <Badge variant="info">Parametric</Badge>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
              Flags values with standardized distance <code className="text-cyan-600 dark:text-cyan-300 font-mono">|z| &gt; 3.0</code> standard deviations from the mean.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 dark:bg-dark-900/60 border border-slate-200 dark:border-slate-800/80">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-bold text-slate-900 dark:text-white">3. Isolation Forest</span>
              <Badge variant="warning">Multivariate Ensemble</Badge>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
              Random tree partitioning isolating multidimensional structural anomalies across all numeric features jointly.
            </p>
          </div>
        </div>

        {/* Multi-Method Comparison Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold">
                <th className="pb-3 px-3">Numeric Column</th>
                <th className="pb-3 px-3 text-right">IQR Outliers (Count / %)</th>
                <th className="pb-3 px-3 text-right">Z-Score (|z|&gt;3)</th>
                <th className="pb-3 px-3 text-right">Isolation Forest</th>
                <th className="pb-3 px-3 text-right">2+ Methods Consensus</th>
                <th className="pb-3 px-3">IQR Clean Bounds</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-sans">
              {outliers.columns.map((col) => (
                <tr
                  key={col.column}
                  className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                >
                  <td className="py-3 px-3 font-semibold text-slate-900 dark:text-white">
                    {col.column}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-700 dark:text-slate-300">
                    {col.iqr_outliers_count.toLocaleString()}{' '}
                    <span className="text-[10px] text-slate-400 dark:text-slate-500">
                      ({col.iqr_percentage}%)
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-700 dark:text-slate-300">
                    {col.zscore_outliers_count.toLocaleString()}{' '}
                    <span className="text-[10px] text-slate-400 dark:text-slate-500">
                      ({col.zscore_percentage}%)
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-700 dark:text-slate-300">
                    {col.isolation_forest_count.toLocaleString()}{' '}
                    <span className="text-[10px] text-slate-400 dark:text-slate-500">
                      ({col.isolation_forest_percentage}%)
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right">
                    <Badge
                      variant={
                        col.consensus_percentage >= 3.0
                          ? 'danger'
                          : col.consensus_count > 0
                          ? 'warning'
                          : 'success'
                      }
                    >
                      {col.consensus_count.toLocaleString()} (
                      {col.consensus_percentage}%)
                    </Badge>
                  </td>
                  <td className="py-3 px-3 font-mono text-[11px] text-slate-500 dark:text-slate-400">
                    [{col.iqr_lower_bound} to {col.iqr_upper_bound}]
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
