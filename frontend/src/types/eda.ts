export interface ColumnProfile {
  name: string;
  dtype: string;
  inferred_type: 'numeric' | 'categorical' | 'boolean' | 'datetime' | 'constant' | 'id_like';
  is_numeric: boolean;
  is_categorical: boolean;
  is_datetime: boolean;
  is_boolean: boolean;
  is_constant: boolean;
  is_id_like: boolean;
  unique_count: number;
  unique_ratio: number;
  null_count: number;
  null_ratio: number;
  memory_bytes: number;
  sample_values: (string | number | boolean)[];
}

export interface ProfilerResult {
  rows_count: number;
  columns_count: number;
  total_memory_bytes: number;
  total_memory_formatted: string;
  columns: ColumnProfile[];
  numeric_columns: string[];
  categorical_columns: string[];
  datetime_columns: string[];
  boolean_columns: string[];
  constant_columns: string[];
  id_like_columns: string[];
}

export interface ColumnMissing {
  column: string;
  missing_count: number;
  missing_percentage: number;
  total_rows: number;
}

export interface MissingCorrelationPair {
  col1: string;
  col2: string;
  correlation: number;
}

export interface MissingnessResult {
  total_missing_cells: number;
  total_cells: number;
  overall_missing_percentage: number;
  columns_with_missing_count: number;
  columns: ColumnMissing[];
  missingness_correlations: MissingCorrelationPair[];
  has_systematic_missingness: boolean;
}

export interface DuplicatesResult {
  duplicate_rows_count: number;
  total_rows: number;
  duplicate_percentage: number;
  has_duplicates: boolean;
  sample_duplicates: Record<string, any>[];
}

export interface HistogramData {
  bin_edges: number[];
  counts: number[];
  bin_labels: string[];
}

export interface NumericStats {
  column: string;
  count: number;
  mean: number;
  std: number;
  median: number;
  min: number;
  max: number;
  q25: number;
  q75: number;
  iqr: number;
  skewness: number;
  kurtosis: number;
  histogram: HistogramData;
  is_skewed: boolean;
  skew_direction: 'right' | 'left' | 'symmetric';
}

export interface DistributionsResult {
  columns: Record<string, NumericStats>;
}

export interface ColumnOutliers {
  column: string;
  iqr_outliers_count: number;
  iqr_percentage: number;
  iqr_lower_bound: number;
  iqr_upper_bound: number;
  zscore_outliers_count: number;
  zscore_percentage: number;
  isolation_forest_count: number;
  isolation_forest_percentage: number;
  consensus_count: number;
  consensus_percentage: number;
}

export interface OutliersResult {
  total_flagged_rows: number;
  columns: ColumnOutliers[];
  multivariate_anomaly_count: number;
  multivariate_anomaly_percentage: number;
}

export interface CorrelationPair {
  feature1: string;
  feature2: string;
  correlation: number;
  strength: 'very strong' | 'strong' | 'moderate' | 'weak';
  direction: 'positive' | 'negative';
}

export interface CorrelationsResult {
  numeric_columns: string[];
  pearson_matrix: Record<string, Record<string, number | null>>;
  spearman_matrix: Record<string, Record<string, number | null>>;
  top_positive_pairs: CorrelationPair[];
  top_negative_pairs: CorrelationPair[];
  strong_pairs_count: number;
}

export interface CategoryFrequency {
  category: string;
  count: number;
  percentage: number;
}

export interface ColumnCategorical {
  column: string;
  unique_count: number;
  is_high_cardinality: boolean;
  cardinality_threshold: number;
  frequencies: CategoryFrequency[];
  other_bucket_count: number;
  other_bucket_percentage: number;
}

export interface CategoricalResult {
  columns: ColumnCategorical[];
}

export interface TargetClassInfo {
  label: string;
  count: number;
  percentage: number;
}

export interface TargetCrossStats {
  feature: string;
  grouped_stats: Record<string, { mean: number; median: number; std: number; min: number; max: number }>;
}

export interface TargetCrossCatRate {
  feature: string;
  cross_tab: Record<string, Record<string, number>>;
}

export interface TargetAnalysisResult {
  target_column: string;
  target_type: 'binary_classification' | 'multiclass_classification' | 'regression';
  class_distribution?: TargetClassInfo[];
  imbalance_ratio?: number;
  is_imbalanced?: boolean;
  mitigations: string[];
  regression_stats?: NumericStats;
  feature_correlations: { feature: string; correlation: number; abs_correlation: number }[];
  numeric_cross_breakdown: TargetCrossStats[];
  categorical_cross_breakdown: TargetCrossCatRate[];
}

export interface InsightFinding {
  category: 'quality' | 'distribution' | 'outlier' | 'correlation' | 'categorical' | 'target';
  severity: 'high' | 'medium' | 'low' | 'info';
  title: string;
  description: string;
  recommendation: string;
  affected_columns: string[];
}

export interface QualityScoreBreakdown {
  base_score: number;
  missingness_penalty: number;
  duplicate_penalty: number;
  outlier_penalty: number;
  invalid_type_penalty: number;
  high_cardinality_penalty: number;
  final_score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  summary: string;
}

export interface InsightsResult {
  quality_score: QualityScoreBreakdown;
  insights: InsightFinding[];
  high_severity_count: number;
  medium_severity_count: number;
  low_severity_count: number;
}

export interface FullEDAReport {
  dataset_id: string;
  filename: string;
  profiler: ProfilerResult;
  missing: MissingnessResult;
  duplicates: DuplicatesResult;
  distributions: DistributionsResult;
  outliers: OutliersResult;
  correlations: CorrelationsResult;
  categorical: CategoricalResult;
  insights: InsightsResult;
  target?: TargetAnalysisResult | null;
}

export interface SampleDatasetMeta {
  dataset_id: string;
  filename: string;
  rows: number;
  columns: number;
  is_sample: boolean;
  description: string;
}
