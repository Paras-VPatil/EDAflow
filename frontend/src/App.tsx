import React, { useState, useEffect, useRef } from 'react';
import {
  getSampleDatasets,
  uploadDataset,
  runAnalysis,
  runTargetAnalysis,
} from './api/client';
import {
  parseCSV,
  profileDatasetClient,
  FALLBACK_SAMPLE_DATASETS,
} from './services/clientProfiler';
import {
  CHURN_CSV_SAMPLE,
  TITANIC_CSV_SAMPLE,
  HOUSING_CSV_SAMPLE,
} from './services/demoDatasets';
import { FullEDAReport, SampleDatasetMeta, ColumnProfile } from './types/eda';
import { Navbar } from './components/common/Navbar';
import { Dropzone } from './components/upload/Dropzone';
import { SampleDatasetSelector } from './components/upload/SampleDatasetSelector';
import { OverviewSection } from './components/overview/OverviewSection';
import { MissingSection } from './components/missing/MissingSection';
import { DistributionsSection } from './components/distributions/DistributionsSection';
import { OutliersSection } from './components/outliers/OutliersSection';
import { CorrelationsSection } from './components/correlations/CorrelationsSection';
import { CategoricalSection } from './components/categorical/CategoricalSection';
import { TargetSection } from './components/target/TargetSection';
import { InsightsSection } from './components/insights/InsightsSection';
import { DriftSection } from './components/drift/DriftSection';
import { ExportModal } from './components/export/ExportModal';
import { ColumnDetailModal } from './components/common/ColumnDetailModal';
import {
  LayoutDashboard,
  AlertCircle,
  BarChart3,
  ShieldAlert,
  GitCommit,
  Type,
  Target,
  Lightbulb,
  GitCompare,
  X,
  Sparkles
} from 'lucide-react';

type TabKey =
  | 'overview'
  | 'missing'
  | 'distributions'
  | 'outliers'
  | 'correlations'
  | 'categorical'
  | 'target'
  | 'insights'
  | 'drift';

export const App: React.FC = () => {
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    const saved = localStorage.getItem('edaflow_theme');
    return saved === 'light' ? 'light' : 'dark';
  });

  const [samples, setSamples] = useState<SampleDatasetMeta[]>(FALLBACK_SAMPLE_DATASETS);
  const [report, setReport] = useState<FullEDAReport | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingMsg, setLoadingMsg] = useState<string>('Initializing...');
  const [isUploadOpen, setIsUploadOpen] = useState<boolean>(false);
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedColumn, setSelectedColumn] = useState<ColumnProfile | null>(null);
  const clientRowsRef = useRef<{ headers: string[]; rows: Record<string, any>[] } | null>(null);

  // Apply theme class to <html>
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }
    localStorage.setItem('edaflow_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Helper to load client sample
  const loadClientSample = (sampleId: string) => {
    let csvText = CHURN_CSV_SAMPLE;
    let filename = 'customer_churn.csv';
    let target = 'Churn';

    if (sampleId.includes('titanic')) {
      csvText = TITANIC_CSV_SAMPLE;
      filename = 'titanic_survival.csv';
      target = 'Survived';
    } else if (sampleId.includes('housing')) {
      csvText = HOUSING_CSV_SAMPLE;
      filename = 'california_housing.csv';
      target = 'MedianHouseValue';
    }

    const { headers, rows } = parseCSV(csvText);
    clientRowsRef.current = { headers, rows };
    const clientReport = profileDatasetClient(filename, headers, rows, target);
    setReport(clientReport);
  };

  // 1. Initial Load: Fetch sample datasets from backend, or fallback to instant client-side profile
  useEffect(() => {
    const initApp = async () => {
      try {
        setIsLoading(true);
        setLoadingMsg('Loading demonstration datasets...');
        const sampleList = await getSampleDatasets();
        if (sampleList && sampleList.length > 0) {
          setSamples(sampleList);
          const firstSample = sampleList[0];
          setLoadingMsg(`Running statistical analysis on ${firstSample.filename}...`);
          const initialReport = await runAnalysis(firstSample.dataset_id, 'Churn');
          setReport(initialReport);
          return;
        }
      } catch (err: any) {
        console.warn('Backend unavailable, activating in-browser client analytics engine:', err);
      } finally {
        setIsLoading(false);
      }

      // Seamless fallback to built-in client engine if backend is not linked or cold-starting
      loadClientSample('sample_churn');
    };

    initApp();
  }, []);

  // 2. Select Sample Dataset
  const handleSelectSample = async (sampleId: string) => {
    try {
      setIsLoading(true);
      const sample = samples.find((s) => s.dataset_id === sampleId);
      setLoadingMsg(`Analyzing ${sample?.filename || 'dataset'} with EDA engine...`);
      setIsUploadOpen(false);

      let targetGuess: string | undefined = undefined;
      if (sample?.filename.includes('churn')) targetGuess = 'Churn';
      else if (sample?.filename.includes('titanic')) targetGuess = 'Survived';
      else if (sample?.filename.includes('housing')) targetGuess = 'MedianHouseValue';
      else if (sample?.filename.includes('attrition')) targetGuess = 'Attrition';

      const res = await runAnalysis(sampleId, targetGuess);
      setReport(res);
      setActiveTab('overview');
    } catch (err: any) {
      console.warn('Backend sample load failed, using client engine:', err);
      loadClientSample(sampleId);
      setActiveTab('overview');
    } finally {
      setIsLoading(false);
    }
  };

  // 3. Handle File Upload
  const handleFileUpload = async (file: File) => {
    try {
      setIsLoading(true);
      setLoadingMsg(`Uploading and parsing ${file.name}...`);
      const uploadRes = await uploadDataset(file);
      const datasetId = uploadRes.data.dataset_id;

      setLoadingMsg('Computing statistical distributions, multi-method outliers, and insights...');
      const fullReport = await runAnalysis(datasetId);
      setReport(fullReport);
      clientRowsRef.current = null;
      setIsUploadOpen(false);
      setActiveTab('overview');
    } catch (err: any) {
      console.warn('Backend upload failed, parsing client-side:', err);
      try {
        setLoadingMsg(`Parsing ${file.name} directly in browser...`);
        const text = await file.text();
        const { headers, rows } = parseCSV(text);
        if (headers.length === 0 || rows.length === 0) {
          throw new Error('Unable to parse tabular columns from file.');
        }
        clientRowsRef.current = { headers, rows };
        const clientReport = profileDatasetClient(file.name, headers, rows);
        setReport(clientReport);
        setIsUploadOpen(false);
        setActiveTab('overview');
        setErrorMessage(null);
      } catch (parseErr: any) {
        setErrorMessage(
          parseErr?.message || 'Failed to parse tabular file format. Please upload a valid CSV.'
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  // 4. Handle Target Selection
  const handleSelectTarget = async (targetColumn: string) => {
    if (!report) return;
    try {
      setIsLoading(true);
      setLoadingMsg(`Computing Target Intelligence and Baseline Model for '${targetColumn}'...`);
      
      if (clientRowsRef.current) {
        const { headers, rows } = clientRowsRef.current;
        const updatedReport = profileDatasetClient(report.filename, headers, rows, targetColumn);
        setReport(updatedReport);
      } else {
        const targetRes = await runTargetAnalysis(report.dataset_id, targetColumn);
        setReport({
          ...report,
          target: targetRes,
        });
      }
    } catch (err: any) {
      if (clientRowsRef.current) {
        const { headers, rows } = clientRowsRef.current;
        const updatedReport = profileDatasetClient(report.filename, headers, rows, targetColumn);
        setReport(updatedReport);
      } else {
        setErrorMessage(
          err?.response?.data?.detail || `Target analysis failed for '${targetColumn}'.`
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  const navTabs: { key: TabKey; label: string; icon: React.ComponentType<{ className?: string }>; badge?: number | string; badgeColor?: string }[] = [
    { key: 'overview', label: 'Overview & Score', icon: LayoutDashboard },
    { key: 'missing', label: 'Data Health & Missingness', icon: AlertCircle, badge: report?.missing.columns_with_missing_count ? `${report.missing.columns_with_missing_count} null cols` : undefined },
    { key: 'distributions', label: 'Distributions & Skew', icon: BarChart3 },
    { key: 'outliers', label: 'Outlier Lab', icon: ShieldAlert, badge: report?.outliers.multivariate_anomaly_count ? `${report.outliers.multivariate_anomaly_count}` : undefined },
    { key: 'correlations', label: 'Correlations', icon: GitCommit, badge: report?.correlations.strong_pairs_count ? `${report.correlations.strong_pairs_count} pairs` : undefined },
    { key: 'categorical', label: 'Categorical Intelligence', icon: Type },
    { key: 'target', label: 'Target & ML Prep', icon: Target, badge: report?.target ? report.target.target_type.replace('_', ' ') : undefined },
    { key: 'drift', label: 'Dataset Drift', icon: GitCompare, badge: 'New', badgeColor: 'bg-primary-500/20 text-primary-400 border-primary-500/30' },
    {
      key: 'insights',
      label: 'Smart Insights',
      icon: Lightbulb,
      badge: report?.insights.high_severity_count ? `${report.insights.high_severity_count} High` : `${report?.insights.insights.length || 0}`,
      badgeColor: report?.insights.high_severity_count ? 'bg-rose-500/20 text-rose-500 dark:text-rose-300 border-rose-500/30' : undefined
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-dark-950 text-slate-900 dark:text-slate-100 flex flex-col selection:bg-brand-500 selection:text-white font-sans transition-colors duration-200">
      {/* 1. Global Navigation Bar */}
      <Navbar
        currentDatasetId={report?.dataset_id}
        currentFilename={report?.filename}
        rowsCount={report?.profiler.rows_count}
        colsCount={report?.profiler.columns_count}
        sampleDatasets={samples}
        theme={theme}
        onToggleTheme={toggleTheme}
        onSelectSample={handleSelectSample}
        onOpenUpload={() => setIsUploadOpen(true)}
        onOpenExportModal={() => setIsExportOpen(true)}
      />

      {/* 2. Error Toast if applicable */}
      {errorMessage && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4 w-full">
          <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/80 border border-rose-200 dark:border-rose-500/40 text-rose-800 dark:text-rose-200 text-xs flex items-center justify-between shadow-lg">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-500 dark:text-rose-400 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="p-1 rounded text-rose-500 dark:text-rose-400 hover:text-rose-900 dark:hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* 3. Sampling Notice if dataset was sampled */}
      {report?.is_sampled && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-3 w-full">
          <div className="p-3 rounded-xl bg-primary-500/10 border border-primary-500/30 text-primary-300 text-xs flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-primary-400 shrink-0" />
            <span>
              <strong>Large Dataset Sampled:</strong> Analysis was performed on a statistically representative sample of {report.profiler.rows_count.toLocaleString()} rows (from {report.original_rows?.toLocaleString() || 'all'} total rows) to deliver instant sub-second response times.
            </span>
          </div>
        </div>
      )}

      {/* 4. Main Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Upload Modal / Overlay if open or if no report */}
        {(isUploadOpen || !report) && (
          <div className="glass-panel rounded-2xl p-8 mb-6 border border-brand-500/20 shadow-2xl relative animate-in fade-in duration-200">
            {report && (
              <button
                onClick={() => setIsUploadOpen(false)}
                className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            )}

            <div className="max-w-2xl mx-auto text-center mb-6">
              <span className="text-xs font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 inline-block mb-2">
                Automated Ingestion
              </span>
              <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                Upload Any Tabular Dataset for Instant Intelligence
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Drop CSV, TSV, Excel, Parquet, or JSON. Features auto-encoding detection, delimiter sniffing, bad-line tolerance, and anomaly scoring.
              </p>
            </div>

            <Dropzone
              onFileSelected={handleFileUpload}
              isLoading={isLoading}
              loadingMessage={loadingMsg}
            />

            <SampleDatasetSelector
              samples={samples}
              onSelectSample={handleSelectSample}
              isLoading={isLoading}
            />
          </div>
        )}

        {/* Loaded Dataset Tabbed Analysis Dashboard */}
        {report && (
          <>
            {/* Tab Navigation Pill Strip */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar border-b border-slate-200 dark:border-slate-800/80">
              {navTabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.key;

                return (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={`flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                      isActive
                        ? 'bg-brand-600 text-white shadow-glow-sm shadow-brand-500/30'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-900/80'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    <span>{tab.label}</span>
                    {tab.badge && (
                      <span
                        className={`text-[10px] font-mono px-1.5 py-0.5 rounded-md border ${
                          tab.badgeColor ||
                          (isActive
                            ? 'bg-white/20 text-white border-white/30'
                            : 'bg-slate-100 dark:bg-dark-900 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-800')
                        }`}
                      >
                        {tab.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Active Tab View Content */}
            <div className="mt-6">
              {activeTab === 'overview' && (
                <OverviewSection
                  report={report}
                  onColumnClick={(col) => setSelectedColumn(col)}
                />
              )}
              {activeTab === 'missing' && (
                <MissingSection
                  missing={report.missing}
                  duplicates={report.duplicates}
                  datasetId={report.dataset_id}
                />
              )}
              {activeTab === 'distributions' && (
                <DistributionsSection distributions={report.distributions} />
              )}
              {activeTab === 'outliers' && (
                <OutliersSection outliers={report.outliers} />
              )}
              {activeTab === 'correlations' && (
                <CorrelationsSection correlations={report.correlations} />
              )}
              {activeTab === 'categorical' && (
                <CategoricalSection categorical={report.categorical} />
              )}
              {activeTab === 'target' && (
                <TargetSection
                  targetResult={report.target || null}
                  profiler={report.profiler}
                  onSelectTarget={handleSelectTarget}
                  isLoading={isLoading}
                />
              )}
              {activeTab === 'drift' && (
                <DriftSection
                  currentDatasetId={report.dataset_id}
                  currentDatasetName={report.filename}
                  sampleDatasets={samples}
                />
              )}
              {activeTab === 'insights' && (
                <InsightsSection insightsResult={report.insights} />
              )}
            </div>
          </>
        )}
      </main>

      {/* 5. Column Drill-down Modal */}
      {report && (
        <ColumnDetailModal
          column={selectedColumn}
          report={report}
          onClose={() => setSelectedColumn(null)}
        />
      )}

      {/* 6. Export Artifact Modal */}
      {report && (
        <ExportModal
          isOpen={isExportOpen}
          onClose={() => setIsExportOpen(false)}
          report={report}
        />
      )}

      {/* 7. Clean Footer */}
      <footer className="w-full border-t border-slate-200 dark:border-slate-800/60 bg-white/60 dark:bg-dark-950/60 py-6 mt-12 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 dark:text-slate-400">
          <div>
            <span className="font-bold text-slate-700 dark:text-slate-300">EDAflow</span> — Production-grade Automated Dataset Intelligence Platform
          </div>
          <div className="flex items-center gap-4">
            <span>FastAPI + Python Engine</span>
            <span>•</span>
            <span>React + TypeScript</span>
            <span>•</span>
            <span>Statistical & ML Reasoning</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
export default App;
