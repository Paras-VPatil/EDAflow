import React, { useState } from 'react';
import { InsightsResult } from '../../types/eda';
import {
  Lightbulb,
  AlertCircle,
  AlertTriangle,
  Info,
  CheckCircle2,
  Filter,
} from 'lucide-react';
import { Badge } from '../common/Badge';

interface InsightsSectionProps {
  insightsResult: InsightsResult;
}

export const InsightsSection: React.FC<InsightsSectionProps> = ({
  insightsResult,
}) => {
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const { insights, high_severity_count, medium_severity_count, low_severity_count } =
    insightsResult;

  const filteredInsights = insights.filter((item) => {
    const matchesSev = severityFilter === 'all' || item.severity === severityFilter;
    const matchesCat = categoryFilter === 'all' || item.category === categoryFilter;
    return matchesSev && matchesCat;
  });

  const getSeverityIcon = (sev: string) => {
    switch (sev) {
      case 'high':
        return <AlertCircle className="w-4 h-4 text-rose-500 dark:text-rose-400" />;
      case 'medium':
        return <AlertTriangle className="w-4 h-4 text-amber-500 dark:text-amber-400" />;
      case 'low':
      default:
        return <Info className="w-4 h-4 text-blue-500 dark:text-blue-400" />;
    }
  };

  const getSeverityCardBorder = (sev: string) => {
    switch (sev) {
      case 'high':
        return 'border-l-4 border-l-rose-500 bg-rose-50/50 dark:bg-rose-950/10 border-slate-200 dark:border-slate-800';
      case 'medium':
        return 'border-l-4 border-l-amber-500 bg-amber-50/50 dark:bg-amber-950/10 border-slate-200 dark:border-slate-800';
      case 'low':
      default:
        return 'border-l-4 border-l-blue-500 bg-blue-50/50 dark:bg-blue-950/10 border-slate-200 dark:border-slate-800';
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* 1. Header & Severity Stats Banner */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-amber-500 dark:text-amber-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                Prioritized Findings & Recommendations Engine
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Rule-based statistical reasoning engine synthesizing issues into actionable ML-prep steps.
            </p>
          </div>

          {/* Quick Severity Counters */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSeverityFilter('high')}
              className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-all ${
                severityFilter === 'high'
                  ? 'bg-rose-500/20 border-rose-500/50 text-rose-700 dark:text-rose-300 ring-2 ring-rose-500/30'
                  : 'bg-white dark:bg-dark-900 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-rose-500" />
              <span>{high_severity_count} High</span>
            </button>

            <button
              onClick={() => setSeverityFilter('medium')}
              className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-all ${
                severityFilter === 'medium'
                  ? 'bg-amber-500/20 border-amber-500/50 text-amber-700 dark:text-amber-300 ring-2 ring-amber-500/30'
                  : 'bg-white dark:bg-dark-900 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              <span>{medium_severity_count} Medium</span>
            </button>

            <button
              onClick={() => setSeverityFilter('low')}
              className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-all ${
                severityFilter === 'low'
                  ? 'bg-blue-500/20 border-blue-500/50 text-blue-700 dark:text-blue-300 ring-2 ring-blue-500/30'
                  : 'bg-white dark:bg-dark-900 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              <span>{low_severity_count} Low</span>
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-slate-200 dark:border-slate-800/80">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 font-medium">
            <Filter className="w-3.5 h-3.5" />
            <span>Filter Category:</span>
          </div>

          {['all', 'quality', 'distribution', 'outlier', 'correlation', 'categorical', 'target'].map(
            (cat) => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium capitalize transition-colors ${
                  categoryFilter === cat
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-slate-100 dark:bg-dark-900 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 border border-slate-200 dark:border-slate-800'
                }`}
              >
                {cat}
              </button>
            )
          )}

          {severityFilter !== 'all' && (
            <button
              onClick={() => setSeverityFilter('all')}
              className="text-xs text-brand-600 dark:text-brand-400 hover:underline ml-auto"
            >
              Reset Severity Filter
            </button>
          )}
        </div>
      </div>

      {/* 2. Insight Cards Feed */}
      <div className="space-y-3.5">
        {filteredInsights.length > 0 ? (
          filteredInsights.map((item, idx) => (
            <div
              key={idx}
              className={`glass-panel rounded-xl p-5 border transition-all ${getSeverityCardBorder(
                item.severity
              )}`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  {getSeverityIcon(item.severity)}
                  <h4 className="font-bold text-sm text-slate-900 dark:text-white tracking-tight">
                    {item.title}
                  </h4>
                </div>

                <div className="flex items-center gap-2">
                  <Badge
                    variant={
                      item.severity === 'high'
                        ? 'danger'
                        : item.severity === 'medium'
                        ? 'warning'
                        : 'info'
                    }
                  >
                    {item.severity.toUpperCase()}
                  </Badge>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400">
                    {item.category}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed mb-3">
                {item.description}
              </p>

              <div className="p-3 rounded-lg bg-white dark:bg-dark-950/80 border border-slate-200 dark:border-slate-800/90 text-xs text-slate-800 dark:text-slate-200 flex items-start gap-2 shadow-sm">
                <span className="font-bold text-brand-600 dark:text-brand-400 flex-shrink-0">
                  Recommendation:
                </span>
                <span className="text-slate-700 dark:text-slate-300 leading-relaxed">
                  {item.recommendation}
                </span>
              </div>

              {item.affected_columns.length > 0 && (
                <div className="mt-3 flex items-center gap-1.5 flex-wrap">
                  <span className="text-[10px] text-slate-500 font-medium">
                    Affected Features:
                  </span>
                  {item.affected_columns.map((col) => (
                    <span
                      key={col}
                      className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 text-[10px] font-mono text-slate-600 dark:text-slate-400"
                    >
                      {col}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="py-12 text-center glass-panel rounded-2xl">
            <CheckCircle2 className="w-8 h-8 text-emerald-600 dark:text-emerald-400 mx-auto mb-2" />
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">No Issues Found</h4>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              No findings matched the selected severity or category filter.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
