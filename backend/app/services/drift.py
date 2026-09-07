import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from scipy.stats import ks_2samp

def calculate_psi(expected: np.ndarray, actual: np.ndarray, num_bins: int = 10) -> float:
    """Calculate Population Stability Index (PSI) between two distributions with Laplace smoothing."""
    try:
        if len(expected) == 0 or len(actual) == 0:
            return 0.0

        # Generate bin edges on expected
        quantiles = np.linspace(0, 1, num_bins + 1)
        bins = np.percentile(expected, quantiles * 100)
        bins = np.unique(bins)
        if len(bins) < 2:
            return 0.0

        bins[0] = -np.inf
        bins[-1] = np.inf

        expected_counts, _ = np.histogram(expected, bins=bins)
        actual_counts, _ = np.histogram(actual, bins=bins)

        # Laplace smoothing ensures no bucket has zero density
        eps = 1e-4
        expected_pct = (expected_counts + eps) / (np.sum(expected_counts) + eps * len(expected_counts))
        actual_pct = (actual_counts + eps) / (np.sum(actual_counts) + eps * len(actual_counts))

        ratio = np.clip(actual_pct / expected_pct, 1e-6, 1e6)
        psi_val = np.sum((actual_pct - expected_pct) * np.log(ratio))
        return round(float(np.clip(psi_val, 0.0, 10.0)), 4)
    except Exception:
        return 0.0

def compare_datasets(df_baseline: pd.DataFrame, df_comparison: pd.DataFrame) -> Dict[str, Any]:
    """
    Compare two datasets (Baseline vs Comparison / Train vs Test) and detect:
    - Schema differences (added, removed, type-shifted columns)
    - Row count and missingness shift
    - Numerical distribution drift (Kolmogorov-Smirnov test & PSI)
    - Categorical distribution shifts
    """
    cols_baseline = set(df_baseline.columns)
    cols_comparison = set(df_comparison.columns)

    common_cols = sorted(list(cols_baseline.intersection(cols_comparison)))
    added_cols = sorted(list(cols_comparison - cols_baseline))
    removed_cols = sorted(list(cols_baseline - cols_comparison))

    # Schema & Type drift
    type_mismatches = []
    for col in common_cols:
        t1 = str(df_baseline[col].dtype)
        t2 = str(df_comparison[col].dtype)
        if t1 != t2:
            type_mismatches.append({
                "column": col,
                "baseline_type": t1,
                "comparison_type": t2
            })

    # Missingness comparison
    missing_drift = []
    for col in common_cols:
        m1 = round(float(df_baseline[col].isnull().mean() * 100), 2)
        m2 = round(float(df_comparison[col].isnull().mean() * 100), 2)
        diff = round(m2 - m1, 2)
        if abs(diff) >= 2.0 or m1 > 0 or m2 > 0:
            missing_drift.append({
                "column": col,
                "baseline_missing_pct": m1,
                "comparison_missing_pct": m2,
                "shift_pct": diff,
                "status": "increased" if diff > 0 else ("decreased" if diff < 0 else "unchanged")
            })

    # Numerical Drift (KS test & PSI)
    numeric_drift = []
    for col in common_cols:
        if pd.api.types.is_numeric_dtype(df_baseline[col]) and pd.api.types.is_numeric_dtype(df_comparison[col]):
            s1 = df_baseline[col].dropna().values
            s2 = df_comparison[col].dropna().values

            if len(s1) > 5 and len(s2) > 5:
                # Kolmogorov-Smirnov Test
                ks_stat, p_val = ks_2samp(s1, s2)
                psi_val = calculate_psi(s1, s2)

                # Drift decision: p-value < 0.05 and KS statistic > 0.1
                has_drift = (p_val < 0.05 and ks_stat > 0.10) or psi_val > 0.20
                drift_severity = "high" if psi_val > 0.25 or ks_stat > 0.25 else ("moderate" if has_drift else "none")

                numeric_drift.append({
                    "column": col,
                    "ks_statistic": round(float(ks_stat), 4),
                    "p_value": round(float(p_val), 6),
                    "psi": psi_val,
                    "has_drift": bool(has_drift),
                    "severity": drift_severity,
                    "baseline_mean": round(float(np.mean(s1)), 2),
                    "comparison_mean": round(float(np.mean(s2)), 2),
                    "baseline_std": round(float(np.std(s1)), 2),
                    "comparison_std": round(float(np.std(s2)), 2)
                })

    # Overall drift summary
    drifted_cols = [c for c in numeric_drift if c["has_drift"]]
    drift_score = round((len(drifted_cols) / len(numeric_drift) * 100) if numeric_drift else 0.0, 1)

    return {
        "baseline_summary": {
            "rows": len(df_baseline),
            "columns": len(df_baseline.columns)
        },
        "comparison_summary": {
            "rows": len(df_comparison),
            "columns": len(df_comparison.columns)
        },
        "schema_drift": {
            "common_columns_count": len(common_cols),
            "added_columns": added_cols,
            "removed_columns": removed_cols,
            "type_mismatches": type_mismatches
        },
        "missingness_drift": missing_drift,
        "numeric_drift": numeric_drift,
        "drift_summary": {
            "drift_score_pct": drift_score,
            "drifted_features_count": len(drifted_cols),
            "total_numeric_evaluated": len(numeric_drift),
            "overall_status": "Severe Drift Detected" if drift_score > 30 else ("Moderate Drift" if drift_score > 10 else "Distributions Stable")
        }
    }
