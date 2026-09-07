import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

def analyze_timeseries(df: pd.DataFrame, datetime_col: Optional[str] = None) -> Dict[str, Any]:
    """Detect datetime columns and perform temporal regularity, trend, and autocorrelation analysis."""
    dt_cols = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            dt_cols.append(col)
        elif df[col].dtype == "object":
            sample = df[col].dropna().head(30)
            if not sample.empty and sample.nunique() > 2:
                try:
                    converted = pd.to_datetime(sample, errors='coerce')
                    if converted.notnull().mean() > 0.8:
                        dt_cols.append(col)
                except Exception:
                    pass

    if not dt_cols and not datetime_col:
        return {
            "has_timeseries": False,
            "datetime_columns": [],
            "message": "No datetime column detected in dataset."
        }

    target_col = datetime_col if (datetime_col and datetime_col in df.columns) else dt_cols[0]
    
    # Parse series to datetime
    try:
        dt_series = pd.to_datetime(df[target_col], errors='coerce').dropna().sort_values()
    except Exception as e:
        return {
            "has_timeseries": False,
            "datetime_columns": dt_cols,
            "error": f"Failed to parse datetime column '{target_col}': {str(e)}"
        }

    if len(dt_series) < 5:
        return {
            "has_timeseries": True,
            "datetime_columns": dt_cols,
            "selected_column": target_col,
            "message": "Insufficient timestamps for temporal analysis."
        }

    min_date = dt_series.min()
    max_date = dt_series.max()
    time_span_days = (max_date - min_date).total_seconds() / (24 * 3600)

    # Calculate intervals
    diffs = dt_series.diff().dropna()
    median_interval_seconds = diffs.dt.total_seconds().median() if not diffs.empty else 0

    inferred_frequency = "irregular"
    if median_interval_seconds > 0:
        if 50 <= median_interval_seconds <= 70:
            inferred_frequency = "1 minute"
        elif 3500 <= median_interval_seconds <= 3700:
            inferred_frequency = "1 hour"
        elif 82000 <= median_interval_seconds <= 90000:
            inferred_frequency = "1 day"
        elif 6 * 86400 <= median_interval_seconds <= 8 * 86400:
            inferred_frequency = "1 week"
        elif 27 * 86400 <= median_interval_seconds <= 32 * 86400:
            inferred_frequency = "1 month"
        elif 360 * 86400 <= median_interval_seconds <= 370 * 86400:
            inferred_frequency = "1 year"
        else:
            inferred_frequency = f"~{round(median_interval_seconds / 3600, 1)} hours"

    # Numeric metrics over time
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c != target_col]
    
    autocorrelations = {}
    trends = []
    
    if numeric_cols:
        sorted_df = df.copy()
        sorted_df[target_col] = pd.to_datetime(sorted_df[target_col], errors='coerce')
        sorted_df = sorted_df.dropna(subset=[target_col]).sort_values(by=target_col)

        for col in numeric_cols[:5]:
            clean_series = sorted_df[col].dropna()
            if len(clean_series) >= 10:
                # Lag-1 Autocorrelation
                lag1 = clean_series.autocorr(lag=1)
                lag7 = clean_series.autocorr(lag=7) if len(clean_series) > 14 else None
                
                autocorrelations[col] = {
                    "lag_1": round(float(lag1), 3) if not np.isnan(lag1) else 0.0,
                    "lag_7": round(float(lag7), 3) if lag7 is not None and not np.isnan(lag7) else None
                }

                # Simple linear trend check
                y = clean_series.values
                x = np.arange(len(y))
                if np.std(y) > 1e-6:
                    slope, _ = np.polyfit(x, y, 1)
                    norm_slope = slope / (np.std(y) + 1e-9)
                    direction = "upward" if norm_slope > 0.05 else ("downward" if norm_slope < -0.05 else "stable")
                    trends.append({
                        "column": col,
                        "direction": direction,
                        "normalized_slope": round(float(norm_slope), 4)
                    })

    return {
        "has_timeseries": True,
        "datetime_columns": dt_cols,
        "selected_column": target_col,
        "start_date": str(min_date),
        "end_date": str(max_date),
        "time_span_days": round(time_span_days, 1),
        "inferred_frequency": inferred_frequency,
        "autocorrelations": autocorrelations,
        "trends": trends
    }
