import React from 'react';
import { SampleDatasetMeta } from '../../types/eda';
import { Sparkles, Users, Ship, Home, Briefcase, ArrowRight } from 'lucide-react';

interface SampleDatasetSelectorProps {
  samples: SampleDatasetMeta[];
  onSelectSample: (sampleId: string) => void;
  isLoading: boolean;
}

export const SampleDatasetSelector: React.FC<SampleDatasetSelectorProps> = ({
  samples,
  onSelectSample,
  isLoading,
}) => {
  const getIcon = (filename: string) => {
    if (filename.includes('churn')) return Users;
    if (filename.includes('titanic')) return Ship;
    if (filename.includes('housing')) return Home;
    return Briefcase;
  };

  const getTag = (filename: string) => {
    if (filename.includes('churn')) return { label: 'Binary Classification', color: 'text-indigo-600 dark:text-indigo-400 bg-indigo-500/10 border-indigo-500/30' };
    if (filename.includes('titanic')) return { label: 'Missingness & Outliers', color: 'text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/30' };
    if (filename.includes('housing')) return { label: 'Regression & Skew', color: 'text-amber-600 dark:text-amber-400 bg-amber-500/10 border-amber-500/30' };
    return { label: 'HR Analytics', color: 'text-cyan-600 dark:text-cyan-400 bg-cyan-500/10 border-cyan-500/30' };
  };

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-500 dark:text-amber-400" />
          <h4 className="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
            Or Explore Instantly with Curated Sample Datasets
          </h4>
        </div>
        <span className="text-xs text-slate-500 dark:text-slate-400">1-click instant analysis</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {samples.map((sample) => {
          const Icon = getIcon(sample.filename);
          const tag = getTag(sample.filename);

          return (
            <button
              key={sample.dataset_id}
              onClick={() => onSelectSample(sample.dataset_id)}
              disabled={isLoading}
              className="glass-card text-left p-4 rounded-xl group hover:border-brand-500/40 transition-all duration-200 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2.5">
                  <div className="p-2 rounded-lg bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 text-brand-600 dark:text-brand-400 group-hover:text-brand-500 group-hover:border-brand-500/30 transition-colors">
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${tag.color}`}>
                    {tag.label}
                  </span>
                </div>

                <h5 className="font-bold text-sm text-slate-900 dark:text-white group-hover:text-brand-600 dark:group-hover:text-brand-300 transition-colors">
                  {sample.filename}
                </h5>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                  {sample.description}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                <span className="font-mono text-[11px]">
                  {sample.rows.toLocaleString()} rows • {sample.columns} cols
                </span>
                <span className="text-brand-600 dark:text-brand-400 font-semibold flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                  Load <ArrowRight className="w-3 h-3" />
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
