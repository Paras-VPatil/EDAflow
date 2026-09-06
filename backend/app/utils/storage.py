import uuid
import pandas as pd
import io
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List
from ..config import STORAGE_DIR, SAMPLE_DATA_DIR
from .sample_generator import generate_sample_datasets

class DatasetStorage:
    def __init__(self):
        self._memory_cache: Dict[str, pd.DataFrame] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._initialize_samples()

    def _initialize_samples(self):
        samples = generate_sample_datasets()
        for filename, df in samples.items():
            dataset_id = f"sample_{filename.replace('.csv', '')}"
            self._memory_cache[dataset_id] = df
            
            # Also write sample CSV to sample_data dir
            csv_path = SAMPLE_DATA_DIR / filename
            df.to_csv(csv_path, index=False)

            self._metadata[dataset_id] = {
                "dataset_id": dataset_id,
                "filename": filename,
                "rows": len(df),
                "columns": len(df.columns),
                "is_sample": True,
                "description": self._get_sample_description(filename)
            }

    def _get_sample_description(self, filename: str) -> str:
        desc_map = {
            "customer_churn.csv": "Telecom customer retention data with churn target, missing charges, and contract categories.",
            "titanic_survival.csv": "Historical passenger survival dataset with cabin missingness, fare outliers, and demographic features.",
            "california_housing.csv": "Regression dataset predicting median house value based on location, income, and room metrics.",
            "employee_attrition.csv": "HR analytics dataset evaluating factors predicting employee resignation vs retention."
        }
        return desc_map.get(filename, "Sample tabular dataset for automated exploratory data analysis.")

    def save_dataframe(self, df: pd.DataFrame, filename: str) -> str:
        dataset_id = str(uuid.uuid4())[:8]
        self._memory_cache[dataset_id] = df
        
        # Save to disk as well
        csv_path = STORAGE_DIR / f"{dataset_id}_{filename}"
        df.to_csv(csv_path, index=False)

        self._metadata[dataset_id] = {
            "dataset_id": dataset_id,
            "filename": filename,
            "rows": len(df),
            "columns": len(df.columns),
            "is_sample": False,
            "description": f"Uploaded file: {filename}"
        }
        return dataset_id

    def parse_file(self, content_bytes: bytes, filename: str) -> Tuple[pd.DataFrame, str]:
        ext = Path(filename).suffix.lower()
        if ext in [".csv", ".tsv", ".txt"]:
            sep = "\t" if ext == ".tsv" else ","
            try:
                df = pd.read_csv(io.BytesIO(content_bytes), sep=sep)
            except Exception:
                # Fallback to python engine with auto-separator detection
                df = pd.read_csv(io.BytesIO(content_bytes), sep=None, engine='python')
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(io.BytesIO(content_bytes))
        elif ext == ".json":
            df = pd.read_json(io.BytesIO(content_bytes))
        elif ext == ".parquet":
            df = pd.read_parquet(io.BytesIO(content_bytes))
        else:
            raise ValueError(f"Unsupported file format: '{ext}'. Supported formats: CSV, TSV, Excel, JSON, Parquet.")

        dataset_id = self.save_dataframe(df, filename)
        return df, dataset_id

    def get_dataframe(self, dataset_id: str) -> Optional[pd.DataFrame]:
        return self._memory_cache.get(dataset_id)

    def get_metadata(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        return self._metadata.get(dataset_id)

    def list_samples(self) -> List[Dict[str, Any]]:
        return [meta for meta in self._metadata.values() if meta.get("is_sample", False)]

# Singleton instance
storage = DatasetStorage()
