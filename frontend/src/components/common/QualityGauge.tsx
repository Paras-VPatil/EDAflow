import React from 'react';
import { QualityScoreBreakdown } from '../../types/eda';
import { ShieldCheck } from 'lucide-react';

interface QualityGaugeProps {
  score: QualityScoreBreakdown;
}

export const QualityGauge: React.FC<QualityGaugeProps> = ({ score }) => {
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A':
        return 'text-emerald-600 dark:text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
      case 'B':
        return 'text-brand-600 dark:text-brand-400 border-brand-500/30 bg-brand-500/10';
      case 'C':
        return 'text-amber-600 dark:text-amber-400 border-amber-500/30 bg-amber-500/10';
      case 'D':
        return 'text-orange-600 dark:text-orange-400 border-orange-500/30 bg-orange-500/10';
      case 'F':
      default:
        return 'text-rose-600 dark:text-rose-400 border-rose-500/30 bg-rose-500/10';
    }
  };

  const getScoreStroke = (finalScore: number) => {
    if (finalScore >= 90) return '#10b981';
    if (finalScore >= 80) return '#3b82f6';
    if (finalScore >= 70) return '#f59e0b';
    if (finalScore >= 55) return '#f97316';
    return '#ef4444';
  };

  const radius = 56;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score.final_score / 100) * circumference;

  return (
    <div className="glass-panel rounded-2xl p-6 relative overflow-hidden transition-colors">
      <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
        {/* Gauge Visual & Grade */}
        <div className="flex items-center gap-6">
          <div className="relative flex items-center justify-center">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle
                cx="64"
                cy="64"
                r={radius}
                className="text-slate-200 dark:text-slate-800"
                strokeWidth={strokeWidth}
                stroke="currentColor"
                fill="transparent"
              />
              <circle
                cx="64"
                cy="64"
                r={radius}
                stroke={getScoreStroke(score.final_score)}
                strokeWidth={strokeWidth}
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                {score.final_score}
              </span>
              <span className="text-[10px] uppercase font-bold text-slate-400 dark:text-slate-500 tracking-wider">
                out of 100
              </span>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Data Quality Score
              </span>
              <span
                className={`px-2 py-0.5 rounded-md border text-xs font-bold ${getGradeColor(
                  score.grade
                )}`}
              >
                Grade {score.grade}
              </span>
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
              {score.final_score >= 80 ? 'Production Ready' : score.final_score >= 60 ? 'Requires Remediation' : 'Critical Noise'}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mt-1 leading-relaxed">
              {score.summary}
            </p>
          </div>
        </div>

        {/* Transparent Penalty Breakdown */}
        <div className="w-full lg:w-auto bg-slate-100/80 dark:bg-dark-900/60 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex-1 max-w-xl transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
              Formula & Penalty Breakdown
            </span>
            <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">Base: 100 pts</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center text-xs">
            <div className="bg-white dark:bg-dark-950/70 rounded-lg p-2 border border-slate-200 dark:border-slate-800/80 shadow-sm">
              <div className="text-[10px] text-slate-500 dark:text-slate-400">Missingness</div>
              <div className="font-mono font-bold text-rose-500 dark:text-rose-400 mt-0.5">
                -{score.missingness_penalty}
              </div>
            </div>
            <div className="bg-white dark:bg-dark-950/70 rounded-lg p-2 border border-slate-200 dark:border-slate-800/80 shadow-sm">
              <div className="text-[10px] text-slate-500 dark:text-slate-400">Duplicates</div>
              <div className="font-mono font-bold text-amber-500 dark:text-amber-400 mt-0.5">
                -{score.duplicate_penalty}
              </div>
            </div>
            <div className="bg-white dark:bg-dark-950/70 rounded-lg p-2 border border-slate-200 dark:border-slate-800/80 shadow-sm">
              <div className="text-[10px] text-slate-500 dark:text-slate-400">Outliers</div>
              <div className="font-mono font-bold text-orange-500 dark:text-orange-400 mt-0.5">
                -{score.outlier_penalty}
              </div>
            </div>
            <div className="bg-white dark:bg-dark-950/70 rounded-lg p-2 border border-slate-200 dark:border-slate-800/80 shadow-sm">
              <div className="text-[10px] text-slate-500 dark:text-slate-400">Invalid Types</div>
              <div className="font-mono font-bold text-cyan-600 dark:text-cyan-400 mt-0.5">
                -{score.invalid_type_penalty}
              </div>
            </div>
            <div className="bg-white dark:bg-dark-950/70 rounded-lg p-2 border border-slate-200 dark:border-slate-800/80 shadow-sm col-span-2 sm:col-span-1">
              <div className="text-[10px] text-slate-500 dark:text-slate-400">Cardinality</div>
              <div className="font-mono font-bold text-purple-600 dark:text-purple-400 mt-0.5">
                -{score.high_cardinality_penalty}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
