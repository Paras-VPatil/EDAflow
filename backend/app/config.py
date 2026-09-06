import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Application settings
APP_NAME = "EDAflow"
APP_VERSION = "1.0.0"
MAX_UPLOAD_SIZE_MB = 100
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv", ".tsv", ".json", ".xlsx", ".xls", ".parquet"}
DEFAULT_MAX_ROWS_FOR_SYNC = 500_000
HISTOGRAM_DEFAULT_BINS = 20
TOP_N_CATEGORIES = 10
HIGH_CARDINALITY_THRESHOLD = 30
CORRELATION_STRONG_THRESHOLD = 0.60
OUTLIER_ZSCORE_THRESHOLD = 3.0
