import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from .distributions import analyze_distributions

def analyze_target(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset.")

    series = df[target_column].dropna()
    total_non_null = len(series)
    unique_count = int(series.nunique())

    if total_non_null == 0:
        raise ValueError(f"Target column '{target_column}' contains only missing values.")

    # Edge Case: Target has only 1 unique class
    if unique_count == 1:
        single_val = str(series.iloc[0])
        return {
            "target_column": str(target_column),
            "target_type": "single_class_trivial",
            "class_distribution": [{"label": single_val, "count": total_non_null, "percentage": 100.0}],
            "imbalance_ratio": 1.0,
            "is_imbalanced": False,
            "mitigations": [
                "⚠️ Target contains only one class. Classification modeling cannot be performed because there is zero variance.",
                "Check data filtering or labeling pipeline before attempting ML training."
            ],
            "regression_stats": None,
            "feature_correlations": [],
            "numeric_cross_breakdown": [],
            "categorical_cross_breakdown": []
        }

    is_num = pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)
    
    # 1. Determine Target Type
    if unique_count == 2:
        target_type = "binary_classification"
    elif not is_num or unique_count <= 10:
        target_type = "multiclass_classification"
    else:
        target_type = "regression"

    class_distribution = None
    imbalance_ratio = None
    is_imbalanced = None
    mitigations = []
    regression_stats = None
    feature_correlations = []
    numeric_cross_breakdown = []
    categorical_cross_breakdown = []

    # 2. Classification Path
    if target_type in ["binary_classification", "multiclass_classification"]:
        val_counts = series.value_counts()
        class_dist_list = []
        for label, count in val_counts.items():
            cnt_int = int(count)
            class_dist_list.append({
                "label": str(label),
                "count": cnt_int,
                "percentage": round((cnt_int / total_non_null) * 100, 2)
            })
        class_distribution = class_dist_list

        counts_arr = val_counts.to_numpy()
        maj_cnt = float(np.max(counts_arr))
        min_cnt = float(np.min(counts_arr))
        imbalance_ratio = round(maj_cnt / min_cnt, 2) if min_cnt > 0 else 1.0
        is_imbalanced = (imbalance_ratio >= 2.0)

        # Mitigations recommendations
        if imbalance_ratio >= 5.0:
            mitigations = [
                "Severe class imbalance detected: Utilize Stratified K-Fold cross-validation.",
                "Apply algorithmic cost-weighting (e.g. `class_weight='balanced'` in sklearn / XGBoost scale_pos_weight).",
                "Evaluate Synthetic Minority Over-sampling (SMOTE) or ADASYN on training splits only.",
                "Avoid raw Accuracy metric — evaluate with PR-AUC, F1-Score (Macro/Weighted), or Balanced Accuracy."
            ]
        elif imbalance_ratio >= 2.0:
            mitigations = [
                "Moderate class imbalance: Use Stratified sampling across Train/Validation/Test splits.",
                "Consider setting `class_weight='balanced'` in tree-based or logistic models.",
                "Prioritize ROC-AUC / F1-Score over simple Accuracy."
            ]
        else:
            mitigations = [
                "Classes are well-balanced. Standard cross-validation and classification metrics are suitable."
            ]

        # Numeric features cross-breakdown (Grouped Stats by Class)
        numeric_cols = [c for c in df.columns if c != target_column and pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])]
        for num_col in numeric_cols[:10]:
            valid_sub = df[[num_col, target_column]].dropna()
            if valid_sub.empty:
                continue
            
            grouped = valid_sub.groupby(target_column)[num_col]
            grp_stats: Dict[str, Dict[str, float]] = {}
            for cls_name, grp in grouped:
                arr = grp.to_numpy(dtype=float)
                if len(arr) > 0:
                    grp_stats[str(cls_name)] = {
                        "mean": round(float(np.mean(arr)), 2),
                        "median": round(float(np.median(arr)), 2),
                        "std": round(float(np.std(arr, ddof=1)), 2) if len(arr) > 1 else 0.0,
                        "min": round(float(np.min(arr)), 2),
                        "max": round(float(np.max(arr)), 2)
                    }
            numeric_cross_breakdown.append({
                "feature": str(num_col),
                "grouped_stats": grp_stats
            })

        # Categorical features cross-breakdown (Crosstabs)
        cat_cols = [c for c in df.columns if c != target_column and (df[c].dtype == 'object' or df[c].dtype.name == 'category' or df[c].nunique() < 10)]
        for cat_col in cat_cols[:8]:
            valid_sub = df[[cat_col, target_column]].dropna()
            if valid_sub.empty:
                continue
            
            try:
                ct = pd.crosstab(valid_sub[cat_col], valid_sub[target_column], normalize='index') * 100
                ct_dict = {}
                for cat_val, row in ct.iterrows():
                    ct_dict[str(cat_val)] = {str(k): round(float(v), 2) for k, v in row.items()}

                categorical_cross_breakdown.append({
                    "feature": str(cat_col),
                    "cross_tab": ct_dict
                })
            except Exception:
                continue

    # 3. Regression Path
    elif target_type == "regression":
        reg_dist = analyze_distributions(df[[target_column]], numeric_columns=[target_column])
        regression_stats = reg_dist["columns"].get(target_column)

        # Correlation of numeric features with target
        numeric_cols = [c for c in df.columns if c != target_column and pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])]
        for num_col in numeric_cols:
            valid_sub = df[[num_col, target_column]].dropna()
            if len(valid_sub) > 3 and valid_sub[num_col].nunique() > 1:
                r = valid_sub[num_col].corr(valid_sub[target_column])
                if not np.isnan(r):
                    feature_correlations.append({
                        "feature": str(num_col),
                        "correlation": round(float(r), 3),
                        "abs_correlation": round(abs(float(r)), 3)
                    })

        feature_correlations.sort(key=lambda x: x["abs_correlation"], reverse=True)

        if regression_stats and regression_stats.get("is_skewed"):
            mitigations.append(f"Target is {regression_stats.get('skew_direction')}-skewed (skew={regression_stats.get('skewness'):.2f}): Consider Target Transformation (`np.log1p` or Box-Cox) during model training.")
        mitigations.append("Assess evaluation metrics: RMSE for penalizing large errors, MAE for robust baseline, and R² for variance explained.")

    return {
        "target_column": str(target_column),
        "target_type": target_type,
        "class_distribution": class_distribution,
        "imbalance_ratio": imbalance_ratio,
        "is_imbalanced": is_imbalanced,
        "mitigations": mitigations,
        "regression_stats": regression_stats,
        "feature_correlations": feature_correlations,
        "numeric_cross_breakdown": numeric_cross_breakdown,
        "categorical_cross_breakdown": categorical_cross_breakdown
    }
