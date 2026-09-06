from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

# Base envelope
class ResponseEnvelope(BaseModel):
    status: str = "ok"
    data: Any
    warnings: List[str] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)

# Profiler Models
class ColumnProfile(BaseModel):
    name: str
    dtype: str
    inferred_type: str  # numeric, categorical, boolean, datetime, constant, id_like
    is_numeric: bool
    is_categorical: bool
    is_datetime: bool
    is_boolean: bool
    is_constant: bool
    is_id_like: bool
    unique_count: int
    unique_ratio: float
    null_count: int
    null_ratio: float
    memory_bytes: int
    sample_values: List[Any] = Field(default_factory=list)

class ProfilerResult(BaseModel):
    rows_count: int
    columns_count: int
    total_memory_bytes: int
    total_memory_formatted: str
    columns: List[ColumnProfile]
    numeric_columns: List[str]
    categorical_columns: List[str]
    datetime_columns: List[str]
    boolean_columns: List[str]
    constant_columns: List[str]
    id_like_columns: List[str]

# Missing Models
class ColumnMissing(BaseModel):
    column: str
    missing_count: int
    missing_percentage: float
    total_rows: int

class MissingCorrelationPair(BaseModel):
    col1: str
    col2: str
    correlation: float

class MissingnessResult(BaseModel):
    total_missing_cells: int
    total_cells: int
    overall_missing_percentage: float
    columns_with_missing_count: int
    columns: List[ColumnMissing]
    missingness_correlations: List[MissingCorrelationPair] = Field(default_factory=list)
    has_systematic_missingness: bool = False

# Duplicates Models
class DuplicatesResult(BaseModel):
    duplicate_rows_count: int
    total_rows: int
    duplicate_percentage: float
    has_duplicates: bool
    sample_duplicates: List[Dict[str, Any]] = Field(default_factory=list)

# Distributions Models
class HistogramData(BaseModel):
    bin_edges: List[float]
    counts: List[int]
    bin_labels: List[str]

class NumericStats(BaseModel):
    column: str
    count: int
    mean: float
    std: float
    median: float
    min: float
    max: float
    q25: float
    q75: float
    iqr: float
    skewness: float
    kurtosis: float
    histogram: HistogramData
    is_skewed: bool
    skew_direction: str  # right, left, symmetric

class DistributionsResult(BaseModel):
    columns: Dict[str, NumericStats]

# Outliers Models
class ColumnOutliers(BaseModel):
    column: str
    iqr_outliers_count: int
    iqr_percentage: float
    iqr_lower_bound: float
    iqr_upper_bound: float
    zscore_outliers_count: int
    zscore_percentage: float
    isolation_forest_count: int
    isolation_forest_percentage: float
    consensus_count: int
    consensus_percentage: float

class OutliersResult(BaseModel):
    total_flagged_rows: int
    columns: List[ColumnOutliers]
    multivariate_anomaly_count: int
    multivariate_anomaly_percentage: float

# Correlations Models
class CorrelationPair(BaseModel):
    feature1: str
    feature2: str
    correlation: float
    strength: str  # very strong, strong, moderate, weak
    direction: str  # positive, negative

class CorrelationsResult(BaseModel):
    numeric_columns: List[str]
    pearson_matrix: Dict[str, Dict[str, Optional[float]]]
    spearman_matrix: Dict[str, Dict[str, Optional[float]]]
    top_positive_pairs: List[CorrelationPair]
    top_negative_pairs: List[CorrelationPair]
    strong_pairs_count: int

# Categorical Models
class CategoryFrequency(BaseModel):
    category: str
    count: int
    percentage: float

class ColumnCategorical(BaseModel):
    column: str
    unique_count: int
    is_high_cardinality: bool
    cardinality_threshold: int
    frequencies: List[CategoryFrequency]
    other_bucket_count: int = 0
    other_bucket_percentage: float = 0.0

class CategoricalResult(BaseModel):
    columns: List[ColumnCategorical]

# Target Intelligence Models
class TargetClassInfo(BaseModel):
    label: str
    count: int
    percentage: float

class TargetCrossStats(BaseModel):
    feature: str
    grouped_stats: Dict[str, Dict[str, float]]  # class -> {mean, median, std, min, max}

class TargetCrossCatRate(BaseModel):
    feature: str
    cross_tab: Dict[str, Dict[str, float]]  # category -> {class -> pct}

class TargetAnalysisResult(BaseModel):
    target_column: str
    target_type: str  # binary_classification, multiclass_classification, regression
    class_distribution: Optional[List[TargetClassInfo]] = None
    imbalance_ratio: Optional[float] = None
    is_imbalanced: Optional[bool] = None
    mitigations: List[str] = Field(default_factory=list)
    regression_stats: Optional[NumericStats] = None
    feature_correlations: List[Dict[str, Any]] = Field(default_factory=list)
    numeric_cross_breakdown: List[TargetCrossStats] = Field(default_factory=list)
    categorical_cross_breakdown: List[TargetCrossCatRate] = Field(default_factory=list)

# Insights & Quality Models
class InsightFinding(BaseModel):
    category: str  # quality, distribution, outlier, correlation, categorical, target
    severity: str  # high (🔴), medium (🟠), low (🟡), info (ℹ️)
    title: str
    description: str
    recommendation: str
    affected_columns: List[str] = Field(default_factory=list)

class QualityScoreBreakdown(BaseModel):
    base_score: float = 100.0
    missingness_penalty: float
    duplicate_penalty: float
    outlier_penalty: float
    invalid_type_penalty: float
    high_cardinality_penalty: float
    final_score: float
    grade: str  # A, B, C, D, F
    summary: str

class InsightsResult(BaseModel):
    quality_score: QualityScoreBreakdown
    insights: List[InsightFinding]
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int

# Full EDA Report payload
class FullEDAReport(BaseModel):
    dataset_id: str
    filename: str
    profiler: ProfilerResult
    missing: MissingnessResult
    duplicates: DuplicatesResult
    distributions: DistributionsResult
    outliers: OutliersResult
    correlations: CorrelationsResult
    categorical: CategoricalResult
    insights: InsightsResult
    target: Optional[TargetAnalysisResult] = None
