import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Optional

def analyze_distributions(df: pd.DataFrame, numeric_columns: Optional[List[str]] = None, bins_count: int = 15) -> Dict[str, Any]:
    if numeric_columns is None:
        numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col])]

    results: Dict[str, Any] = {}

    for col in numeric_columns:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if len(series) == 0:
            continue

        try:
            arr = series.to_numpy(dtype=float)
            arr = arr[~np.isnan(arr)]
            if len(arr) == 0:
                continue

            mean_val = float(np.mean(arr))
            std_val = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
            if np.isnan(std_val):
                std_val = 0.0

            median_val = float(np.median(arr))
            min_val = float(np.min(arr))
            max_val = float(np.max(arr))
            q25 = float(np.percentile(arr, 25)) if len(arr) >= 4 else min_val
            q75 = float(np.percentile(arr, 75)) if len(arr) >= 4 else max_val
            iqr_val = max(0.0, q75 - q25)

            # Skewness & Kurtosis
            skew_val = float(stats.skew(arr)) if len(arr) >= 3 else 0.0
            if np.isnan(skew_val):
                skew_val = 0.0
            kurt_val = float(stats.kurtosis(arr)) if len(arr) >= 4 else 0.0
            if np.isnan(kurt_val):
                kurt_val = 0.0

            is_skewed = abs(skew_val) >= 1.0
            if skew_val > 0.5:
                skew_dir = "right"
            elif skew_val < -0.5:
                skew_dir = "left"
            else:
                skew_dir = "symmetric"

            # Server-side histogram binning
            if min_val == max_val or len(arr) <= 2:
                counts = [len(arr)]
                bin_edges = [min_val - 0.5, max_val + 0.5]
                bin_labels = [f"{min_val:.1f}"]
            else:
                num_bins = min(bins_count, max(3, int(np.sqrt(len(arr)))))
                counts_np, edges_np = np.histogram(arr, bins=num_bins)
                counts = [int(c) for c in counts_np]
                bin_edges = [round(float(e), 3) for e in edges_np]
                bin_labels = [f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}" for i in range(len(bin_edges) - 1)]

            results[str(col)] = {
                "column": str(col),
                "count": len(arr),
                "mean": round(mean_val, 3),
                "std": round(std_val, 3),
                "median": round(median_val, 3),
                "min": round(min_val, 3),
                "max": round(max_val, 3),
                "q25": round(q25, 3),
                "q75": round(q75, 3),
                "iqr": round(iqr_val, 3),
                "skewness": round(skew_val, 3),
                "kurtosis": round(kurt_val, 3),
                "histogram": {
                    "bin_edges": bin_edges,
                    "counts": counts,
                    "bin_labels": bin_labels
                },
                "is_skewed": is_skewed,
                "skew_direction": skew_dir
            }
        except Exception:
            continue

    return {
        "columns": results
    }
