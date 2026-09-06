import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List, Optional

def analyze_outliers(df: pd.DataFrame, numeric_columns: Optional[List[str]] = None) -> Dict[str, Any]:
    total_rows = len(df)
    if total_rows == 0:
        return {
            "total_flagged_rows": 0,
            "columns": [],
            "multivariate_anomaly_count": 0,
            "multivariate_anomaly_percentage": 0.0
        }

    if numeric_columns is None:
        numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col])]

    # Keep columns that have variation and aren't all null
    valid_num_cols = [c for c in numeric_columns if df[c].dropna().nunique() > 1]
    
    col_results = []
    
    # Track per-row outlier indicators for consensus
    iqr_row_flags = {c: set() for c in valid_num_cols}
    zscore_row_flags = {c: set() for c in valid_num_cols}

    for col in valid_num_cols:
        series = df[col]
        non_null = series.dropna()
        if len(non_null) < 4:
            continue

        arr = non_null.to_numpy(dtype=float)
        q25 = float(np.percentile(arr, 25))
        q75 = float(np.percentile(arr, 75))
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr

        # 1. IQR outliers
        iqr_mask = (series < lower_bound) | (series > upper_bound)
        iqr_indices = set(series[iqr_mask].index)
        iqr_row_flags[col] = iqr_indices
        iqr_count = len(iqr_indices)
        iqr_pct = round((iqr_count / total_rows) * 100, 2)

        # 2. Z-Score outliers
        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
        if std_val > 0:
            z_scores = (series - mean_val) / std_val
            z_mask = z_scores.abs() > 3.0
            z_indices = set(series[z_mask].index)
        else:
            z_indices = set()
        
        zscore_row_flags[col] = z_indices
        z_count = len(z_indices)
        z_pct = round((z_count / total_rows) * 100, 2)

        # Univariate Consensus (IQR and Z-score agreement on this column)
        uni_consensus = iqr_indices.intersection(z_indices)
        
        col_results.append({
            "column": str(col),
            "iqr_outliers_count": iqr_count,
            "iqr_percentage": iqr_pct,
            "iqr_lower_bound": round(lower_bound, 3),
            "iqr_upper_bound": round(upper_bound, 3),
            "zscore_outliers_count": z_count,
            "zscore_percentage": z_pct,
            "isolation_forest_count": 0,  # will populate after multivariate step
            "isolation_forest_percentage": 0.0,
            "consensus_count": len(uni_consensus),
            "consensus_percentage": round((len(uni_consensus) / total_rows) * 100, 2)
        })

    # 3. Multivariate Anomaly Detection with Isolation Forest
    iso_anomalies_set = set()
    if len(valid_num_cols) >= 1 and total_rows >= 10:
        try:
            # Impute median for multivariate model without changing original df
            imputed_df = df[valid_num_cols].fillna(df[valid_num_cols].median())
            # Run IsolationForest
            iso = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
            preds = iso.fit_predict(imputed_df)
            iso_anomalies_indices = set(df.index[preds == -1])
            iso_anomalies_set = iso_anomalies_indices
        except Exception:
            iso_anomalies_set = set()

    multivariate_count = len(iso_anomalies_set)
    multivariate_pct = round((multivariate_count / total_rows) * 100, 2)

    # Update column results with isolation forest breakdown
    for col_info in col_results:
        col = col_info["column"]
        iqr_set = iqr_row_flags.get(col, set())
        z_set = zscore_row_flags.get(col, set())
        
        # Isolation forest overlaps
        iso_overlap = iso_anomalies_set.intersection(iqr_set.union(z_set))
        col_info["isolation_forest_count"] = len(iso_overlap)
        col_info["isolation_forest_percentage"] = round((len(iso_overlap) / total_rows) * 100, 2)
        
        # 2+ methods agreement on this feature
        # row in (iqr & z) OR (iqr & iso) OR (z & iso)
        agree_2plus = (iqr_set & z_set) | (iqr_set & iso_anomalies_set) | (z_set & iso_anomalies_set)
        col_info["consensus_count"] = len(agree_2plus)
        col_info["consensus_percentage"] = round((len(agree_2plus) / total_rows) * 100, 2)

    # Sort columns by consensus count descending
    col_results.sort(key=lambda x: x["consensus_count"], reverse=True)

    # Total unique rows flagged by any method
    all_flagged_rows = set(iso_anomalies_set)
    for c in valid_num_cols:
        all_flagged_rows.update(iqr_row_flags.get(c, set()))
        all_flagged_rows.update(zscore_row_flags.get(c, set()))

    return {
        "total_flagged_rows": len(all_flagged_rows),
        "columns": col_results,
        "multivariate_anomaly_count": multivariate_count,
        "multivariate_anomaly_percentage": multivariate_pct
    }
