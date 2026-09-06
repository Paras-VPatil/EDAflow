import React, { useState } from 'react';
import { CategoricalResult } from '../../types/eda';
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
import { Type } from 'lucide-react';
import { Badge } from '../common/Badge';

interface CategoricalSectionProps {
  categorical: CategoricalResult;
}

export const CategoricalSection: React.FC<CategoricalSectionProps> = ({
  categorical,
}) => {
  const [selectedColName, setSelectedColName] = useState<string>(
    categorical.columns[0]?.column || ''
  );

  const activeCol =
    categorical.columns.find((c) => c.column === selectedColName) ||
    categorical.columns[0];

  const chartData =
    activeCol?.frequencies.map((f) => ({
      category: f.category,
      count: f.count,
      percentage: f.percentage,
    })) || [];

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* 1. Explorer Header & Column Selector */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2">
              <Type className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                Categorical Intelligence & High-Cardinality Grouping
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Profiles category frequency distributions with automatic Top-10 + "Other" consolidation.
            </p>
          </div>

          {categorical.columns.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Categorical Feature:</span>
              <select
                value={selectedColName}
                onChange={(e) => setSelectedColName(e.target.value)}
                className="bg-white dark:bg-dark-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-900 dark:text-white focus:outline-none focus:border-brand-500 transition-colors"
              >
                {categorical.columns.map((c) => (
                  <option key={c.column} value={c.column}>
                    {c.column} ({c.unique_count} levels)
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {activeCol ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chart */}
            <div className="lg:col-span-2 bg-slate-50/80 dark:bg-dark-900/60 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3 text-xs">
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  Value Frequency Breakdown:{' '}
                  <span className="text-emerald-600 dark:text-emerald-400">{activeCol.column}</span>
                </span>
                <div className="flex items-center gap-2">
                  <Badge variant={activeCol.is_high_cardinality ? 'warning' : 'success'}>
                    {activeCol.unique_count} Unique Levels
                  </Badge>
                  {activeCol.is_high_cardinality && (
                    <span className="text-[10px] text-amber-600 dark:text-amber-400 font-medium">
                      (High Cardinality)
                    </span>
                  )}
                </div>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 70, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis
                      type="number"
                      domain={[0, 100]}
                      unit="%"
                      tick={{ fill: '#64748b', fontSize: 10 }}
                    />
                    <YAxis
                      type="category"
                      dataKey="category"
                      tick={{ fill: '#64748b', fontSize: 10 }}
                      width={90}
                    />
                    <Tooltip
                      formatter={(val: any, _, item: any) => [
                        `${val}% (${item.payload.count.toLocaleString()} rows)`,
                        'Frequency',
                      ]}
                    />
                    <Bar dataKey="percentage" radius={[0, 4, 4, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={
                            entry.category.includes('Other')
                              ? '#94a3b8'
                              : '#10b981'
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Level Breakdown List */}
            <div className="bg-slate-50/80 dark:bg-dark-900/60 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3">
                  Top Category Proportions
                </h4>

                <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
                  {activeCol.frequencies.map((freq, idx) => (
                    <div
                      key={idx}
                      className="p-2 rounded-lg bg-white dark:bg-dark-950 border border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs shadow-sm"
                    >
                      <div className="truncate font-medium text-slate-700 dark:text-slate-300 max-w-[140px]" title={freq.category}>
                        {freq.category}
                      </div>
                      <div className="flex items-center gap-2 font-mono text-[11px]">
                        <span className="text-slate-400">
                          {freq.count.toLocaleString()}
                        </span>
                        <span className="font-bold text-emerald-600 dark:text-emerald-400">
                          {freq.percentage}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Encoding Tip */}
              <div className="mt-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-[11px] text-emerald-700 dark:text-emerald-300">
                {activeCol.is_high_cardinality ? (
                  <span>
                    💡 <strong>High Cardinality Strategy:</strong> Use Target Encoding, Frequency Encoding, or entity embeddings. One-Hot encoding will cause dimensional explosion.
                  </span>
                ) : (
                  <span>
                    💡 <strong>Low Cardinality Strategy:</strong> Safe for Standard One-Hot Encoding (`pd.get_dummies` or `OneHotEncoder`).
                  </span>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="py-12 text-center text-xs text-slate-500 dark:text-slate-400">
            No categorical columns identified in this dataset.
          </div>
        )}
      </div>

      {/* 2. All Categoricals Summary */}
      <div className="glass-panel rounded-2xl p-6">
        <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight mb-4">
          Categorical Features Overview
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {categorical.columns.map((c) => (
            <div
              key={c.column}
              onClick={() => setSelectedColName(c.column)}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                selectedColName === c.column
                  ? 'bg-brand-500/10 border-brand-500/40 shadow-sm'
                  : 'bg-white dark:bg-dark-900/60 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-xs text-slate-900 dark:text-white truncate">
                  {c.column}
                </span>
                <Badge variant={c.is_high_cardinality ? 'warning' : 'neutral'}>
                  {c.unique_count} levels
                </Badge>
              </div>

              <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                Top level: <span className="text-slate-800 dark:text-slate-200 font-medium">{c.frequencies[0]?.category}</span> ({c.frequencies[0]?.percentage}%)
              </div>

              {c.other_bucket_count > 0 && (
                <div className="text-[10px] text-slate-400 dark:text-slate-500 mt-1">
                  Other aggregated: {c.other_bucket_percentage}%
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
