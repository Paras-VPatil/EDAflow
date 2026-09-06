import React, { useState } from 'react';
import { DistributionsResult } from '../../types/eda';
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
import { Badge } from '../common/Badge';
import { BarChart3 } from 'lucide-react';

interface DistributionsSectionProps {
  distributions: DistributionsResult;
}

export const DistributionsSection: React.FC<DistributionsSectionProps> = ({
  distributions,
}) => {
  const numericColumns = Object.keys(distributions.columns);
  const [selectedColumn, setSelectedColumn] = useState<string>(
    numericColumns[0] || ''
  );

  const activeStats = selectedColumn
    ? distributions.columns[selectedColumn]
    : null;

  const chartData =
    activeStats?.histogram.counts.map((cnt, idx) => ({
      bin: activeStats.histogram.bin_labels[idx] || `Bin ${idx + 1}`,
      count: cnt,
    })) || [];

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* 1. Interactive Single Column Deep-Dive */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-brand-600 dark:text-brand-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                Distribution & Histogram Explorer
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Server-binned histogram modeling with skewness and kurtosis diagnostics.
            </p>
          </div>

          {/* Column Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Feature:</span>
            <select
              value={selectedColumn}
              onChange={(e) => setSelectedColumn(e.target.value)}
              className="bg-white dark:bg-dark-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-900 dark:text-white focus:outline-none focus:border-brand-500 transition-colors"
            >
              {numericColumns.map((col) => (
                <option key={col} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>
        </div>

        {activeStats && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Histogram Visual */}
            <div className="lg:col-span-2 bg-slate-50/80 dark:bg-dark-900/60 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3 text-xs">
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  Frequency Histogram: <span className="text-brand-600 dark:text-brand-400">{selectedColumn}</span>
                </span>
                <Badge
                  variant={
                    activeStats.is_skewed
                      ? 'warning'
                      : 'success'
                  }
                >
                  {activeStats.skew_direction.toUpperCase()} SKEW (skew={activeStats.skewness})
                </Badge>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis
                      dataKey="bin"
                      tick={{ fill: '#64748b', fontSize: 10 }}
                      angle={-30}
                      textAnchor="end"
                      height={45}
                    />
                    <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                    <Tooltip
                      formatter={(val: any) => [`${val.toLocaleString()} records`, 'Frequency']}
                    />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {chartData.map((_, index) => (
                        <Cell
                          key={`bar-${index}`}
                          fill={activeStats.is_skewed ? '#6366f1' : '#3b82f6'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Statistical Metrics Sidebar */}
            <div className="bg-slate-50/80 dark:bg-dark-900/60 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3">
                  Summary Statistics
                </h4>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2 rounded-lg bg-white dark:bg-dark-950 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">Mean</span>
                    <div className="font-mono font-bold text-slate-900 dark:text-white mt-0.5">
                      {activeStats.mean.toLocaleString()}
                    </div>
                  </div>
                  <div className="p-2 rounded-lg bg-white dark:bg-dark-950 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">Median</span>
                    <div className="font-mono font-bold text-slate-900 dark:text-white mt-0.5">
                      {activeStats.median.toLocaleString()}
                    </div>
                  </div>
                  <div className="p-2 rounded-lg bg-white dark:bg-dark-950 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">Std Dev</span>
                    <div className="font-mono font-bold text-slate-900 dark:text-white mt-0.5">
                      {activeStats.std.toLocaleString()}
                    </div>
                  </div>
                  <div className="p-2 rounded-lg bg-white dark:bg-dark-950 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">IQR</span>
                    <div className="font-mono font-bold text-slate-900 dark:text-white mt-0.5">
                      {activeStats.iqr.toLocaleString()}
                    </div>
                  </div>
                  <div className="p-2 rounded-lg bg-white dark:bg-dark-950 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">Min</span>
                    <div className="font-mono font-bold text-slate-900 dark:text-white mt-0.5">
                      {activeStats.min.toLocaleString()}
                    </div>
                  </div>
                  <div className="p-2 rounded-lg bg-white dark:bg-dark-950 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">Max</span>
                    <div className="font-mono font-bold text-slate-900 dark:text-white mt-0.5">
                      {activeStats.max.toLocaleString()}
                    </div>
                  </div>
                  <div className="p-2 rounded-lg bg-white dark:bg-dark-950 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">Skewness</span>
                    <div className="font-mono font-bold text-indigo-600 dark:text-indigo-400 mt-0.5">
                      {activeStats.skewness}
                    </div>
                  </div>
                  <div className="p-2 rounded-lg bg-white dark:bg-dark-950 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">Kurtosis</span>
                    <div className="font-mono font-bold text-indigo-600 dark:text-indigo-400 mt-0.5">
                      {activeStats.kurtosis}
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommendation Note */}
              <div className="mt-4 p-3 rounded-lg bg-brand-500/10 border border-brand-500/20 text-[11px] text-brand-700 dark:text-brand-300">
                {activeStats.is_skewed ? (
                  <span>
                    ⚠️ <strong>Skewed Feature:</strong> Non-tree ML models benefit from power transform (`np.log1p` or Box-Cox) or `RobustScaler`.
                  </span>
                ) : (
                  <span>
                    ✅ <strong>Normal Shape:</strong> Symmetrically distributed; suitable for standard Z-score standardization.
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 2. Full Numeric Statistics Table */}
      <div className="glass-panel rounded-2xl p-6">
        <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight mb-4">
          All Numeric Features Comparison Table
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold">
                <th className="pb-3 px-3">Column</th>
                <th className="pb-3 px-3 text-right">Mean</th>
                <th className="pb-3 px-3 text-right">Median</th>
                <th className="pb-3 px-3 text-right">Std Dev</th>
                <th className="pb-3 px-3 text-right">Min - Max</th>
                <th className="pb-3 px-3 text-right">IQR</th>
                <th className="pb-3 px-3 text-center">Skewness</th>
                <th className="pb-3 px-3 text-center">Kurtosis</th>
                <th className="pb-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-sans">
              {Object.values(distributions.columns).map((colStat) => (
                <tr
                  key={colStat.column}
                  className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                >
                  <td className="py-3 px-3 font-semibold text-slate-900 dark:text-white">
                    {colStat.column}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-700 dark:text-slate-300">
                    {colStat.mean.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-700 dark:text-slate-300">
                    {colStat.median.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-500 dark:text-slate-400">
                    {colStat.std.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-500 dark:text-slate-400">
                    {colStat.min} → {colStat.max}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-500 dark:text-slate-400">
                    {colStat.iqr}
                  </td>
                  <td className="py-3 px-3 text-center">
                    <Badge
                      variant={colStat.is_skewed ? 'warning' : 'neutral'}
                    >
                      {colStat.skewness} ({colStat.skew_direction})
                    </Badge>
                  </td>
                  <td className="py-3 px-3 text-center font-mono text-slate-500 dark:text-slate-400">
                    {colStat.kurtosis}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => setSelectedColumn(colStat.column)}
                      className="px-2.5 py-1 rounded bg-slate-100 dark:bg-dark-900 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-[11px] font-semibold text-brand-600 dark:text-brand-400 transition-colors"
                    >
                      Inspect
                    </button>
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
