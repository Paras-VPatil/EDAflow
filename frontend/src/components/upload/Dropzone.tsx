import React, { useState, useRef } from 'react';
import { UploadCloud, Loader2 } from 'lucide-react';

interface DropzoneProps {
  onFileSelected: (file: File) => void;
  isLoading: boolean;
  loadingMessage?: string;
}

export const Dropzone: React.FC<DropzoneProps> = ({
  onFileSelected,
  isLoading,
  loadingMessage = 'Processing and profiling dataset with statistical engine...',
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelected(e.target.files[0]);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => !isLoading && fileInputRef.current?.click()}
      className={`relative cursor-pointer group rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-300 ${
        isDragOver
          ? 'border-brand-500 bg-brand-500/10 scale-[1.01]'
          : 'border-slate-300 dark:border-slate-800 hover:border-brand-400 dark:hover:border-slate-700 bg-white/60 dark:bg-dark-900/40 hover:bg-white dark:hover:bg-dark-900/70'
      }`}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.tsv,.json,.xlsx,.xls,.parquet"
        onChange={handleFileChange}
        className="hidden"
        disabled={isLoading}
      />

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-6">
          <div className="w-16 h-16 rounded-2xl bg-brand-500/10 border border-brand-500/30 flex items-center justify-center mb-4">
            <Loader2 className="w-8 h-8 text-brand-600 dark:text-brand-400 animate-spin" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
            Ingesting & Analyzing Dataset
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-sm">
            {loadingMessage}
          </p>
          <div className="mt-4 flex items-center gap-2 text-xs font-mono text-brand-600 dark:text-brand-400">
            <span className="w-2 h-2 rounded-full bg-brand-500 animate-ping" />
            Running statistical profiling & anomaly heuristics
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600/10 to-indigo-500/10 dark:from-brand-600/20 dark:to-indigo-500/20 border border-brand-500/30 flex items-center justify-center mb-4 group-hover:scale-110 group-hover:border-brand-500/50 transition-all duration-300">
            <UploadCloud className="w-8 h-8 text-brand-600 dark:text-brand-400" />
          </div>

          <h3 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight group-hover:text-brand-600 dark:group-hover:text-brand-300 transition-colors">
            Drop your dataset here, or <span className="text-brand-600 dark:text-brand-400 underline decoration-brand-500/50 underline-offset-4">browse files</span>
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1.5 max-w-md">
            Automated profiling, distribution modeling, multi-method outlier consensus, target intelligence, and insight generation.
          </p>

          <div className="mt-5 flex flex-wrap items-center justify-center gap-2 text-xs font-medium text-slate-600 dark:text-slate-400">
            <span className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-dark-950 border border-slate-200 dark:border-slate-800">
              CSV / TSV
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-dark-950 border border-slate-200 dark:border-slate-800">
              Excel (.xlsx)
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-dark-950 border border-slate-200 dark:border-slate-800">
              JSON
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-dark-950 border border-slate-200 dark:border-slate-800">
              Parquet
            </span>
            <span className="text-slate-400 dark:text-slate-500">• Up to 100MB</span>
          </div>
        </div>
      )}
    </div>
  );
};
