import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

def analyze_correlations(df: pd.DataFrame, numeric_columns: Optional[List[str]] = None, threshold: float = 0.5) -> Dict[str, Any]:
    if numeric_columns is None:
        numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col])]

    # Filter out columns that have 0 variance
    valid_cols = [c for c in numeric_columns if df[c].dropna().nunique() > 1]

    if len(valid_cols) < 2:
        return {
            "numeric_columns": [str(c) for c in valid_cols],
            "pearson_matrix": {},
            "spearman_matrix": {},
            "top_positive_pairs": [],
            "top_negative_pairs": [],
            "strong_pairs_count": 0
        }

    sub_df = df[valid_cols]
    pearson_df = sub_df.corr(method="pearson")
    spearman_df = sub_df.corr(method="spearman")

    pearson_matrix: Dict[str, Dict[str, Optional[float]]] = {}
    spearman_matrix: Dict[str, Dict[str, Optional[float]]] = {}

    for c1 in valid_cols:
        pearson_matrix[str(c1)] = {}
        spearman_matrix[str(c1)] = {}
        for c2 in valid_cols:
            p_val = pearson_df.loc[c1, c2]
            s_val = spearman_df.loc[c1, c2]
            pearson_matrix[str(c1)][str(c2)] = None if np.isnan(p_val) else round(float(p_val), 3)
            spearman_matrix[str(c1)][str(c2)] = None if np.isnan(s_val) else round(float(s_val), 3)

    # Extract ranked pairs
    positive_pairs = []
    negative_pairs = []
    seen = set()

    for i in range(len(valid_cols)):
        for j in range(i + 1, len(valid_cols)):
            c1 = valid_cols[i]
            c2 = valid_cols[j]
            r = pearson_df.loc[c1, c2]
            if np.isnan(r):
                continue
            r_val = float(r)
            abs_r = abs(r_val)

            if abs_r >= 0.8:
                strength = "very strong"
            elif abs_r >= 0.6:
                strength = "strong"
            elif abs_r >= 0.4:
                strength = "moderate"
            else:
                strength = "weak"

            pair_item = {
                "feature1": str(c1),
                "feature2": str(c2),
                "correlation": round(r_val, 3),
                "strength": strength,
                "direction": "positive" if r_val >= 0 else "negative"
            }

            if r_val > 0 and r_val >= 0.4:
                positive_pairs.append(pair_item)
            elif r_val < 0 and r_val <= -0.4:
                negative_pairs.append(pair_item)

    positive_pairs.sort(key=lambda x: x["correlation"], reverse=True)
    negative_pairs.sort(key=lambda x: x["correlation"])  # Most negative first

    strong_pairs_count = len([p for p in positive_pairs + negative_pairs if abs(p["correlation"]) >= threshold])

    return {
        "numeric_columns": [str(c) for c in valid_cols],
        "pearson_matrix": pearson_matrix,
        "spearman_matrix": spearman_matrix,
        "top_positive_pairs": positive_pairs,
        "top_negative_pairs": negative_pairs,
        "strong_pairs_count": strong_pairs_count
    }
