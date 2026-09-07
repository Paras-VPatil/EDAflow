import axios from 'axios';
import { FullEDAReport, SampleDatasetMeta, TargetAnalysisResult, DriftReport } from '../types/eda';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getSampleDatasets = async (): Promise<SampleDatasetMeta[]> => {
  const response = await api.get('/sample-datasets');
  return response.data.data;
};

export const inspectExcelSheets = async (file: File): Promise<string[]> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/excel-sheets', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data.sheets || [];
};

export const uploadDataset = async (file: File, sheetName?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  if (sheetName) {
    formData.append('sheet_name', sheetName);
  }
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const runAnalysis = async (
  datasetId: string,
  targetColumn?: string,
  correlationThreshold: number = 0.5
): Promise<FullEDAReport> => {
  const response = await api.post('/analyze', {
    dataset_id: datasetId,
    target_column: targetColumn || undefined,
    correlation_threshold: correlationThreshold,
  });
  return response.data.data;
};

export const runTargetAnalysis = async (
  datasetId: string,
  targetColumn: string
): Promise<TargetAnalysisResult> => {
  const response = await api.post('/target-analysis', {
    dataset_id: datasetId,
    target_column: targetColumn,
  });
  return response.data.data;
};

export const runDriftAnalysis = async (
  baselineDatasetId: string,
  comparisonDatasetId: string
): Promise<DriftReport> => {
  const response = await api.post('/drift-analysis', {
    baseline_dataset_id: baselineDatasetId,
    comparison_dataset_id: comparisonDatasetId,
  });
  return response.data.data;
};

export const getDeduplicatedDownloadUrl = (datasetId: string): string => {
  return `/api/download-deduplicated/${datasetId}`;
};

export const getHtmlReportUrl = (datasetId: string): string => {
  return `/api/export-report/${datasetId}`;
};

export const getNotebookReportUrl = (datasetId: string): string => {
  return `/api/export-notebook/${datasetId}`;
};

export const getMarkdownReportUrl = (datasetId: string): string => {
  return `/api/export-markdown/${datasetId}`;
};
