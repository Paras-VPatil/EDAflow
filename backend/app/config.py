import os
from pathlib import Path
from typing import Set, List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "EDAflow"
    APP_VERSION: str = "1.0.0"
    ENV: str = "production"
    DEBUG: bool = False
    
    # Server / Network
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Storage & Upload Limits
    STORAGE_DIR: Path = BASE_DIR / "storage"
    SAMPLE_DATA_DIR: Path = BASE_DIR / "sample_data"
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: Set[str] = {".csv", ".tsv", ".json", ".xlsx", ".xls", ".parquet"}
    
    # Analysis & Sampling Limits
    DEFAULT_MAX_ROWS_FOR_SYNC: int = 250_000
    SAMPLING_THRESHOLD: int = 100_000
    SAMPLE_SIZE: int = 50_000
    MAX_COLUMNS_FOR_CORRELATION: int = 100
    
    # Statistical Thresholds
    HISTOGRAM_DEFAULT_BINS: int = 20
    TOP_N_CATEGORIES: int = 10
    HIGH_CARDINALITY_THRESHOLD: int = 30
    CORRELATION_STRONG_THRESHOLD: float = 0.60
    OUTLIER_ZSCORE_THRESHOLD: float = 3.0
    
    # Cleanup TTL (Hours before temporary storage files are purged)
    STORAGE_RETENTION_HOURS: int = 24
    
    # Rate Limiting
    RATE_LIMIT_UPLOAD: str = "30/minute"
    RATE_LIMIT_ANALYZE: str = "60/minute"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()

# Ensure directories exist
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Backward-compatible module-level exports
APP_NAME = settings.APP_NAME
APP_VERSION = settings.APP_VERSION
STORAGE_DIR = settings.STORAGE_DIR
SAMPLE_DATA_DIR = settings.SAMPLE_DATA_DIR
MAX_UPLOAD_SIZE_MB = settings.MAX_UPLOAD_SIZE_MB
MAX_UPLOAD_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = settings.ALLOWED_EXTENSIONS
DEFAULT_MAX_ROWS_FOR_SYNC = settings.DEFAULT_MAX_ROWS_FOR_SYNC
HISTOGRAM_DEFAULT_BINS = settings.HISTOGRAM_DEFAULT_BINS
TOP_N_CATEGORIES = settings.TOP_N_CATEGORIES
HIGH_CARDINALITY_THRESHOLD = settings.HIGH_CARDINALITY_THRESHOLD
CORRELATION_STRONG_THRESHOLD = settings.CORRELATION_STRONG_THRESHOLD
OUTLIER_ZSCORE_THRESHOLD = settings.OUTLIER_ZSCORE_THRESHOLD
STORAGE_RETENTION_HOURS = settings.STORAGE_RETENTION_HOURS
