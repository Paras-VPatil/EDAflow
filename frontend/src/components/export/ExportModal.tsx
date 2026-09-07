import React, { useState } from 'react';
import { FullEDAReport } from '../../types/eda';
import {
  X,
  FileCode,
  FileSpreadsheet,
  Download,
  Copy,
  Check,
  ExternalLink,
  BookOpen,
  FileText,
} from 'lucide-react';
import {
  getDeduplicatedDownloadUrl,
  getHtmlReportUrl,
  getNotebookReportUrl,
  getMarkdownReportUrl,
} from '../../api/client';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  report: FullEDAReport;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  report,
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(report, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJson = () => {
    const dataStr =
      'data:text/json;charset=utf-8,' +
      encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute(
      'download',
      `${report.filename}_edaflow_report.json`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 dark:bg-dark-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-xl bg-white dark:bg-dark-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl p-6 transition-colors">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
              Export Center & Report Artifacts
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Choose delivery format for {report.filename}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Options */}
        <div className="py-5 space-y-3">
          {/* Option 1: Jupyter Notebook (.ipynb) */}
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-dark-950/80 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                <BookOpen className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                  Jupyter Notebook (.ipynb)
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 font-semibold">New</span>
                </h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Executable Pandas, Matplotlib, and Seaborn code reproducing all analysis.
                </p>
              </div>
            </div>

            <a
              href={getNotebookReportUrl(report.dataset_id)}
              download
              className="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs flex items-center gap-1.5 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>.ipynb</span>
            </a>
          </div>

          {/* Option 2: Markdown Summary (.md) */}
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-dark-950/80 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                  GitHub Markdown Report (.md)
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400 font-semibold">New</span>
                </h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Formatted Markdown report ready for GitHub README or project documentation.
                </p>
              </div>
            </div>

            <a
              href={getMarkdownReportUrl(report.dataset_id)}
              download
              className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs flex items-center gap-1.5 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>.md</span>
            </a>
          </div>

          {/* Option 3: Standalone HTML Report */}
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-dark-950/80 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
                <FileCode className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                  Standalone Executive HTML Report
                </h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Self-contained HTML file ready for browser viewing or Print to PDF.
                </p>
              </div>
            </div>

            <a
              href={getHtmlReportUrl(report.dataset_id)}
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center gap-1.5 transition-colors"
            >
              <span>Open / Print</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

          {/* Option 4: Cleaned Deduplicated CSV */}
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-dark-950/80 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                  Cleaned Deduplicated Dataset (CSV)
                </h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Raw dataset with exact duplicate observations filtered out.
                </p>
              </div>
            </div>

            <a
              href={getDeduplicatedDownloadUrl(report.dataset_id)}
              download
              className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center gap-1.5 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download</span>
            </a>
          </div>

          {/* Option 5: Full JSON Report */}
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-dark-950/80 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/20">
                <Download className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                  Raw Statistical JSON Payload
                </h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Full programmatic schema containing all computed analytical metrics.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyJson}
                className="px-3 py-1.5 rounded-lg bg-white dark:bg-dark-900 border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
              <button
                onClick={handleDownloadJson}
                className="px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>JSON</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-200 dark:border-slate-800 text-right">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-semibold transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
