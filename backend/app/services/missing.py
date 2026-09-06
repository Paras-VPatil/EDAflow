import pandas as pd
import numpy as np
from typing import Dict, Any, List

def analyze_missingness(df: pd.DataFrame) -> Dict[str, Any]:
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols
    
    if total_rows == 0 or total_cols == 0:
        return {
            "total_missing_cells": 0,
            "total_cells": total_cells,
            "overall_missing_percentage": 0.0,
            "columns_with_missing_count": 0,
            "columns": [],
            "missingness_correlations": [],
            "has_systematic_missingness": False
        }

    null_counts = df.isnull().sum()
    total_missing_cells = int(null_counts.sum())
    overall_missing_percentage = round((total_missing_cells / total_cells) * 100, 2)

    columns = []
    cols_with_missing = []

    for col in df.columns:
        m_count = int(null_counts[col])
        m_pct = round((m_count / total_rows) * 100, 2)
        columns.append({
            "column": str(col),
            "missing_count": m_count,
            "missing_percentage": m_pct,
            "total_rows": total_rows
        })
        if 0 < m_count < total_rows:
            cols_with_missing.append(col)

    # Sort columns by missing percentage descending
    columns.sort(key=lambda x: x["missing_percentage"], reverse=True)

    # Systematic missingness: correlate boolean indicators of missingness
    missingness_correlations = []
    has_systematic = False

    if len(cols_with_missing) >= 2:
        null_df = df[cols_with_missing].isnull().astype(float)
        corr_matrix = null_df.corr()
        
        seen_pairs = set()
        for c1 in cols_with_missing:
            for c2 in cols_with_missing:
                if c1 != c2:
                    pair_key = tuple(sorted([str(c1), str(c2)]))
                    if pair_key not in seen_pairs:
                        seen_pairs.add(pair_key)
                        val = corr_matrix.loc[c1, c2]
                        if not np.isnan(val):
                            r_val = float(val)
                            if abs(r_val) >= 0.4:
                                has_systematic = True
                                missingness_correlations.append({
                                    "col1": str(c1),
                                    "col2": str(c2),
                                    "correlation": round(r_val, 3)
                                })

    # Sort correlations by magnitude descending
    missingness_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

    return {
        "total_missing_cells": total_missing_cells,
        "total_cells": total_cells,
        "overall_missing_percentage": overall_missing_percentage,
        "columns_with_missing_count": len([c for c in columns if c["missing_count"] > 0]),
        "columns": columns,
        "missingness_correlations": missingness_correlations,
        "has_systematic_missingness": has_systematic
    }
