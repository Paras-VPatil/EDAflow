import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

def analyze_categorical(df: pd.DataFrame, categorical_columns: Optional[List[str]] = None, top_n: int = 10, cardinality_threshold: int = 30) -> Dict[str, Any]:
    if categorical_columns is None:
        # Include object, category, and string dtypes or low-cardinality discrete columns
        categorical_columns = []
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].dtype.name == 'category' or df[col].dtype == 'string':
                categorical_columns.append(col)
            elif not pd.api.types.is_numeric_dtype(df[col]):
                categorical_columns.append(col)

    results = []

    for col in categorical_columns:
        series = df[col].dropna()
        total_non_null = len(series)
        if total_non_null == 0:
            continue

        unique_count = int(series.nunique())
        is_high_card = unique_count > cardinality_threshold
        val_counts = series.value_counts()

        frequencies = []
        other_count = 0
        other_pct = 0.0

        if unique_count <= top_n:
            for cat_name, cnt in val_counts.items():
                cnt_int = int(cnt)
                frequencies.append({
                    "category": str(cat_name),
                    "count": cnt_int,
                    "percentage": round((cnt_int / total_non_null) * 100, 2)
                })
        else:
            # Top N categories
            top_items = val_counts.iloc[:top_n]
            for cat_name, cnt in top_items.items():
                cnt_int = int(cnt)
                frequencies.append({
                    "category": str(cat_name),
                    "count": cnt_int,
                    "percentage": round((cnt_int / total_non_null) * 100, 2)
                })
            
            # Aggregate remaining as "Other"
            other_series = val_counts.iloc[top_n:]
            other_count = int(other_series.sum())
            other_pct = round((other_count / total_non_null) * 100, 2)
            if other_count > 0:
                frequencies.append({
                    "category": "Other (Combined)",
                    "count": other_count,
                    "percentage": other_pct
                })

        results.append({
            "column": str(col),
            "unique_count": unique_count,
            "is_high_cardinality": is_high_card,
            "cardinality_threshold": cardinality_threshold,
            "frequencies": frequencies,
            "other_bucket_count": other_count,
            "other_bucket_percentage": other_pct
        })

    # Sort columns by unique count ascending
    results.sort(key=lambda x: x["unique_count"])

    return {
        "columns": results
    }
