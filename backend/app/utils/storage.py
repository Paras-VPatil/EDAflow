import uuid
import re
import time
import os
import io
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List
import pandas as pd
from charset_normalizer import from_bytes

from ..config import (
    STORAGE_DIR,
    SAMPLE_DATA_DIR,
    STORAGE_RETENTION_HOURS,
    DEFAULT_MAX_ROWS_FOR_SYNC,
    settings
)
from .sample_generator import generate_sample_datasets

logger = logging.getLogger("edaflow.storage")

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and remove risky characters."""
    base_name = Path(filename).name
    cleaned = re.sub(r'[^a-zA-Z0-9_.-]', '_', base_name)
    if not cleaned or cleaned.startswith('.'):
        cleaned = f"dataset_{uuid.uuid4().hex[:6]}.csv"
    return cleaned

class DatasetStorage:
    def __init__(self):
        self._memory_cache: Dict[str, pd.DataFrame] = {}
        self._raw_frames: Dict[str, pd.DataFrame] = {} # Unsampled version if sampled
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._initialize_samples()

    def _initialize_samples(self):
        try:
            samples = generate_sample_datasets()
            for filename, df in samples.items():
                dataset_id = f"sample_{filename.replace('.csv', '')}"
                self._memory_cache[dataset_id] = df
                
                # Write sample CSV to sample_data dir
                csv_path = SAMPLE_DATA_DIR / filename
                df.to_csv(csv_path, index=False)

                self._metadata[dataset_id] = {
                    "dataset_id": dataset_id,
                    "filename": filename,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "is_sample": True,
                    "is_sampled": False,
                    "sample_rate": 1.0,
                    "created_at": time.time(),
                    "description": self._get_sample_description(filename)
                }
        except Exception as e:
            logger.error(f"Error initializing sample datasets: {e}")

    def _get_sample_description(self, filename: str) -> str:
        desc_map = {
            "customer_churn.csv": "Telecom customer retention data with churn target, missing charges, and contract categories.",
            "titanic_survival.csv": "Historical passenger survival dataset with cabin missingness, fare outliers, and demographic features.",
            "california_housing.csv": "Regression dataset predicting median house value based on location, income, and room metrics.",
            "employee_attrition.csv": "HR analytics dataset evaluating factors predicting employee resignation vs retention."
        }
        return desc_map.get(filename, "Sample tabular dataset for automated exploratory data analysis.")

    def save_dataframe(
        self,
        df: pd.DataFrame,
        filename: str,
        is_sampled: bool = False,
        original_rows: Optional[int] = None,
        warnings: Optional[List[str]] = None
    ) -> str:
        dataset_id = str(uuid.uuid4())[:8]
        clean_name = sanitize_filename(filename)
        
        self._memory_cache[dataset_id] = df
        
        # Save to disk as clean CSV
        csv_path = STORAGE_DIR / f"{dataset_id}_{clean_name}"
        df.to_csv(csv_path, index=False)

        orig_rows = original_rows or len(df)
        sample_rate = round(len(df) / orig_rows, 4) if orig_rows > 0 else 1.0

        self._metadata[dataset_id] = {
            "dataset_id": dataset_id,
            "filename": clean_name,
            "original_filename": filename,
            "rows": len(df),
            "columns": len(df.columns),
            "is_sample": False,
            "is_sampled": is_sampled,
            "original_rows": orig_rows,
            "sample_rate": sample_rate,
            "warnings": warnings or [],
            "created_at": time.time(),
            "description": f"Uploaded dataset: {clean_name}"
        }
        return dataset_id

    def inspect_excel_sheets(self, content_bytes: bytes) -> List[str]:
        """Return list of sheet names in an Excel file without loading all sheets."""
        try:
            excel_file = pd.ExcelFile(io.BytesIO(content_bytes))
            return excel_file.sheet_names
        except Exception as e:
            logger.warning(f"Could not inspect Excel sheets: {e}")
            return ["Sheet1"]

    def parse_file(
        self,
        content_bytes: bytes,
        filename: str,
        sheet_name: Optional[str] = None
    ) -> Tuple[pd.DataFrame, str, List[str]]:
        warnings: List[str] = []
        clean_name = sanitize_filename(filename)
        ext = Path(clean_name).suffix.lower()

        df: Optional[pd.DataFrame] = None

        if ext in [".csv", ".tsv", ".txt"]:
            # 1. Auto-detect encoding using charset-normalizer
            encoding = "utf-8"
            try:
                detection = from_bytes(content_bytes).best()
                if detection and detection.encoding:
                    encoding = detection.encoding
            except Exception as enc_err:
                logger.debug(f"Encoding detection fallback: {enc_err}")
                encoding = "utf-8"

            # 2. Try standard parsing, fallback with auto-delimiter and bad-line skipping
            try:
                # Fast path
                sep = "\t" if ext == ".tsv" else ","
                df = pd.read_csv(
                    io.BytesIO(content_bytes),
                    sep=sep,
                    encoding=encoding,
                    on_bad_lines='skip'
                )
            except Exception:
                try:
                    # Sniff delimiter using python engine
                    df = pd.read_csv(
                        io.BytesIO(content_bytes),
                        sep=None,
                        engine='python',
                        encoding=encoding,
                        on_bad_lines='skip'
                    )
                    warnings.append(f"Auto-detected delimiter for {clean_name} using fallback parser.")
                except Exception as fallback_err:
                    # Final attempt with latin-1
                    df = pd.read_csv(
                        io.BytesIO(content_bytes),
                        sep=None,
                        engine='python',
                        encoding='latin-1',
                        on_bad_lines='skip'
                    )
                    warnings.append("Decoded file using latin-1 encoding fallback.")

        elif ext in [".xlsx", ".xls"]:
            excel_target_sheet = sheet_name if sheet_name else 0
            df = pd.read_excel(io.BytesIO(content_bytes), sheet_name=excel_target_sheet)
        elif ext == ".json":
            df = pd.read_json(io.BytesIO(content_bytes))
        elif ext == ".parquet":
            df = pd.read_parquet(io.BytesIO(content_bytes))
        else:
            raise ValueError(f"Unsupported file format: '{ext}'. Supported: CSV, TSV, Excel, JSON, Parquet.")

        if df is None or df.empty:
            raise ValueError("The parsed dataset contains no rows or valid data.")

        # Ensure string column names
        df.columns = [str(c).strip() for c in df.columns]

        original_rows = len(df)
        is_sampled = False

        # Apply sampling strategy if dataset is extremely large
        if original_rows > settings.SAMPLING_THRESHOLD:
            sample_size = min(settings.SAMPLE_SIZE, original_rows)
            df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
            is_sampled = True
            warnings.append(
                f"Dataset contains {original_rows:,} rows. A statistically representative sample of {sample_size:,} rows was taken for high-velocity analysis."
            )

        dataset_id = self.save_dataframe(
            df=df,
            filename=clean_name,
            is_sampled=is_sampled,
            original_rows=original_rows,
            warnings=warnings
        )

        return df, dataset_id, warnings

    def get_dataframe(self, dataset_id: str) -> Optional[pd.DataFrame]:
        if dataset_id in self._memory_cache:
            return self._memory_cache[dataset_id]
        
        # Check disk if not in memory
        for file_path in STORAGE_DIR.glob(f"{dataset_id}_*"):
            try:
                df = pd.read_csv(file_path)
                self._memory_cache[dataset_id] = df
                return df
            except Exception as e:
                logger.error(f"Failed to read dataset {dataset_id} from disk: {e}")
        return None

    def get_metadata(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        return self._metadata.get(dataset_id)

    def list_samples(self) -> List[Dict[str, Any]]:
        return [meta for meta in self._metadata.values() if meta.get("is_sample", False)]

    def list_all_datasets(self) -> List[Dict[str, Any]]:
        return list(self._metadata.values())

    def cleanup_old_files(self, max_age_hours: Optional[int] = None) -> int:
        """Purge temporary files older than retention hours."""
        retention = max_age_hours or STORAGE_RETENTION_HOURS
        cutoff = time.time() - (retention * 3600)
        removed_count = 0

        try:
            for file_path in STORAGE_DIR.glob("*_*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    if stat.st_mtime < cutoff:
                        file_path.unlink()
                        removed_count += 1
                        # Remove from memory cache if present
                        prefix = file_path.name.split("_")[0]
                        self._memory_cache.pop(prefix, None)
                        self._metadata.pop(prefix, None)
        except Exception as err:
            logger.error(f"Error cleaning up old storage files: {err}")

        return removed_count

# Singleton instance
storage = DatasetStorage()
