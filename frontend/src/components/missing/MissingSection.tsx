import React from 'react';
import { MissingnessResult, DuplicatesResult } from '../../types/eda';
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
import {
  CheckCircle2,
  Download,
  Copy,
  Network,
  Info,
} from 'lucide-react';
import { getDeduplicatedDownloadUrl } from '../../api/client';

interface MissingSectionProps {
  missing: MissingnessResult;
  duplicates: DuplicatesResult;
  datasetId: string;
}

export const MissingSection: React.FC<MissingSectionProps> = ({
  missing,
  duplicates,
  datasetId,
}) => {
  const missingChartData = missing.columns
    .filter((col) => col.missing_count > 0)
    .map((col) => ({
      column: col.column,
      percentage: col.missing_percentage,
      count: col.missing_count,
    }));

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* 1. Missing Values Overview Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                Missing Values Distribution by Column
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                {missing.columns_with_missing_count} of {missing.columns.length} columns contain null values.
              </p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded-md bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300">
              Overall: {missing.overall_missing_percentage}%
            </span>
          </div>

          {missingChartData.length > 0 ? (
            <div className="h-72 w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={missingChartData}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 60, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis
                    type="number"
                    domain={[0, 100]}
                    unit="%"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                  />
                  <YAxis
                    type="category"
                    dataKey="column"
                    tick={{ fill: '#64748b', fontSize: 11 }}
                    width={80}
                  />
                  <Tooltip
                    formatter={(value: any, _, item: any) => [
                      `${value}% (${item.payload.count.toLocaleString()} rows)`,
                      'Missing Rate',
                    ]}
                  />
                  <Bar dataKey="percentage" radius={[0, 4, 4, 0]}>
                    {missingChartData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={
                          entry.percentage >= 40
                            ? '#ef4444'
                            : entry.percentage >= 15
                            ? '#f59e0b'
                            : '#3b82f6'
                        }
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="py-16 text-center">
              <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto mb-3">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                Zero Missing Values Detected!
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-sm mx-auto">
                Every column in this dataset is 100% complete without empty cells.
              </p>
            </div>
          )}
        </div>

        {/* 2. Duplicates & Deduplication Action Card */}
        <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Copy className="w-4 h-4 text-amber-500 dark:text-amber-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                Duplicate Rows
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Exact identical records across all columns.
            </p>

            <div className="my-6 p-4 rounded-xl bg-slate-50 dark:bg-dark-900/80 border border-slate-200 dark:border-slate-800 text-center">
              <div className="text-3xl font-extrabold text-slate-900 dark:text-white">
                {duplicates.duplicate_rows_count.toLocaleString()}
              </div>
              <div className="text-xs font-semibold text-amber-600 dark:text-amber-400 mt-1">
                {duplicates.duplicate_percentage}% duplicate rate
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                {duplicates.has_duplicates
                  ? 'Duplicate records can cause data leakage and artificially skew model weights.'
                  : 'No duplicate observations found.'}
              </p>
            </div>
          </div>

          <div>
            <a
              href={getDeduplicatedDownloadUrl(datasetId)}
              download
              className={`w-full py-2.5 px-4 rounded-xl font-semibold text-xs flex items-center justify-center gap-2 transition-all ${
                duplicates.has_duplicates
                  ? 'bg-amber-600 hover:bg-amber-500 text-white shadow-sm'
                  : 'bg-slate-100 dark:bg-dark-900 text-slate-700 dark:text-slate-400 border border-slate-200 dark:border-slate-800 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Download className="w-4 h-4" />
              <span>
                {duplicates.has_duplicates
                  ? 'Download Deduplicated CSV'
                  : 'Export Clean Dataset CSV'}
              </span>
            </a>
          </div>
        </div>
      </div>

      {/* 3. Systematic Missingness Correlation Card */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-2">
          <Network className="w-4 h-4 text-brand-600 dark:text-brand-400" />
          <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
            Systematic Missingness Correlation Analysis
          </h3>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-2xl">
          Evaluates pairwise correlation between boolean missingness indicators to detect Missing Not At Random (MNAR) or Missing At Random (MAR) patterns.
        </p>

        {missing.missingness_correlations.length > 0 ? (
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {missing.missingness_correlations.map((pair, idx) => (
              <div
                key={idx}
                className="bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3.5 flex items-center justify-between"
              >
                <div>
                  <div className="text-xs font-bold text-slate-900 dark:text-white">
                    {pair.col1} ↔ {pair.col2}
                  </div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                    Co-missingness correlation
                  </div>
                </div>
                <span className="font-mono text-xs font-bold px-2 py-1 rounded bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/30">
                  r = {pair.correlation}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-4 p-4 rounded-xl bg-slate-50 dark:bg-dark-900/50 border border-slate-200 dark:border-slate-800/80 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
            <Info className="w-4 h-4 text-slate-400 flex-shrink-0" />
            <span>
              No strong systematic missingness correlations (|r| ≥ 0.40) detected. Missing values appear random or isolated.
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
