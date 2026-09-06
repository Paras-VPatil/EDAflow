import React from 'react';
import {
  Layers,
  FileSpreadsheet,
  Download,
  UploadCloud,
  ChevronDown,
  Sparkles,
} from 'lucide-react';
import { SampleDatasetMeta } from '../../types/eda';
import { ThemeToggle } from './ThemeToggle';

interface NavbarProps {
  currentDatasetId?: string;
  currentFilename?: string;
  rowsCount?: number;
  colsCount?: number;
  sampleDatasets: SampleDatasetMeta[];
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
  onSelectSample: (sampleId: string) => void;
  onOpenUpload: () => void;
  onOpenExportModal: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentDatasetId,
  currentFilename,
  rowsCount,
  colsCount,
  sampleDatasets,
  theme,
  onToggleTheme,
  onSelectSample,
  onOpenUpload,
  onOpenExportModal,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 dark:border-slate-800/80 bg-white/85 dark:bg-dark-950/80 backdrop-blur-md transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Logo & Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center shadow-glow-sm shadow-brand-500/20 text-white">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg tracking-tight text-slate-900 dark:text-white">
                EDAflow
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-1.5 py-0.5 rounded bg-brand-500/15 text-brand-600 dark:text-brand-300 border border-brand-500/30">
                PRO
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium hidden sm:block">
              Automated Dataset Intelligence Platform
            </p>
          </div>
        </div>

        {/* Center: Current Dataset Pill if loaded */}
        {currentFilename && (
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300">
            <FileSpreadsheet className="w-3.5 h-3.5 text-brand-500 dark:text-brand-400" />
            <span className="font-semibold text-slate-900 dark:text-white max-w-[160px] truncate">
              {currentFilename}
            </span>
            <span className="text-slate-400 dark:text-slate-600">•</span>
            <span className="text-slate-600 dark:text-slate-400">
              {rowsCount?.toLocaleString()} rows
            </span>
            <span className="text-slate-400 dark:text-slate-600">•</span>
            <span className="text-slate-600 dark:text-slate-400">{colsCount} cols</span>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2.5">
          {/* Theme Toggle */}
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />

          {/* Sample Dataset Selector dropdown */}
          <div className="relative group">
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-800 dark:text-slate-200 transition-colors">
              <Sparkles className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" />
              <span>Samples</span>
              <ChevronDown className="w-3 h-3 text-slate-400 group-hover:rotate-180 transition-transform" />
            </button>

            <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-dark-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-2xl py-2 hidden group-hover:block z-50 animate-in fade-in slide-in-from-top-1 duration-150">
              <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Select Demonstration Dataset
              </div>
              {sampleDatasets.map((s) => (
                <button
                  key={s.dataset_id}
                  onClick={() => onSelectSample(s.dataset_id)}
                  className="w-full text-left px-3 py-2 hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors flex flex-col gap-0.5"
                >
                  <div className="text-xs font-semibold text-slate-900 dark:text-white flex items-center justify-between">
                    <span>{s.filename}</span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">
                      {s.rows} rows
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-1">
                    {s.description}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Upload New Dataset */}
          <button
            onClick={onOpenUpload}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-sm transition-all"
          >
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Upload</span>
          </button>

          {/* Export Center Trigger */}
          {currentDatasetId && (
            <button
              onClick={onOpenExportModal}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-800 dark:text-slate-200 transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
              <span className="hidden sm:inline">Export</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
