from typing import Dict, Any, List, Optional

def generate_insights_and_quality(
    profiler_data: Dict[str, Any],
    missing_data: Dict[str, Any],
    duplicates_data: Dict[str, Any],
    distributions_data: Dict[str, Any],
    outliers_data: Dict[str, Any],
    correlations_data: Dict[str, Any],
    categorical_data: Dict[str, Any],
    target_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    insights: List[Dict[str, Any]] = []

    total_rows = profiler_data.get("rows_count", 0)
    total_cols = profiler_data.get("columns_count", 0)
    
    # --- 1. DATA QUALITY PENALTY CALCULATION ---
    # Missingness penalty
    overall_missing_pct = missing_data.get("overall_missing_percentage", 0.0)
    high_missing_cols = [c for c in missing_data.get("columns", []) if c.get("missing_percentage", 0.0) >= 20.0]
    missingness_penalty = min(35.0, (overall_missing_pct * 0.8) + (len(high_missing_cols) * 2.5))

    # Duplicate penalty
    dup_pct = duplicates_data.get("duplicate_percentage", 0.0)
    duplicate_penalty = min(25.0, dup_pct * 1.5)

    # Outlier penalty
    outlier_pct = 0.0
    if total_rows > 0:
        total_flagged = outliers_data.get("total_flagged_rows", 0)
        outlier_pct = (total_flagged / total_rows) * 100.0
    outlier_penalty = min(15.0, outlier_pct * 0.35)

    # Constant & ID-like penalty
    constant_cols = profiler_data.get("constant_columns", [])
    id_cols = profiler_data.get("id_like_columns", [])
    invalid_type_penalty = min(15.0, (len(constant_cols) * 4.0) + (1.0 if len(id_cols) > 2 else 0.0))

    # High cardinality penalty
    high_card_cols = [c for c in categorical_data.get("columns", []) if c.get("is_high_cardinality", False)]
    high_card_penalty = min(10.0, len(high_card_cols) * 1.5)

    # Final score
    raw_score = 100.0 - missingness_penalty - duplicate_penalty - outlier_penalty - invalid_type_penalty - high_card_penalty
    final_score = round(max(0.0, min(100.0, raw_score)), 1)

    if final_score >= 90:
        grade = "A"
        summary = "Exceptional data health with minimal noise, suitable for modeling with minimal preprocessing."
    elif final_score >= 80:
        grade = "B"
        summary = "Solid dataset quality with minor anomalies or missingness that can be readily addressed."
    elif final_score >= 70:
        grade = "C"
        summary = "Moderate data health issues detected; requires standard cleaning, imputation, and outlier treatment."
    elif final_score >= 55:
        grade = "D"
        summary = "Significant noise, missingness, or structural issues detected. Careful feature hygiene recommended."
    else:
        grade = "F"
        summary = "Critical data quality deficiencies detected. Requires extensive remediation before ML ingestion."

    quality_score = {
        "base_score": 100.0,
        "missingness_penalty": round(missingness_penalty, 1),
        "duplicate_penalty": round(duplicate_penalty, 1),
        "outlier_penalty": round(outlier_penalty, 1),
        "invalid_type_penalty": round(invalid_type_penalty, 1),
        "high_cardinality_penalty": round(high_card_penalty, 1),
        "final_score": final_score,
        "grade": grade,
        "summary": summary
    }

    # --- 2. RULE-BASED INSIGHT GENERATION ---

    # Rule: Missingness
    for col_info in missing_data.get("columns", []):
        col_name = col_info["column"]
        m_pct = col_info["missing_percentage"]
        m_cnt = col_info["missing_count"]
        if m_pct >= 40.0:
            insights.append({
                "category": "quality",
                "severity": "high",
                "title": f"Critical Missingness in '{col_name}'",
                "description": f"Column '{col_name}' has {m_pct}% missing values ({m_cnt:,} rows null).",
                "recommendation": "Columns with >40% missingness often dilute model signals. Consider dropping or creating an explicit missingness indicator feature (`is_missing`).",
                "affected_columns": [col_name]
            })
        elif m_pct >= 10.0:
            insights.append({
                "category": "quality",
                "severity": "medium",
                "title": f"Moderate Missingness in '{col_name}'",
                "description": f"Column '{col_name}' is missing {m_pct}% of values ({m_cnt:,} rows).",
                "recommendation": "Use KNN/Iterative imputation for continuous data or median/mode imputation depending on distribution skew.",
                "affected_columns": [col_name]
            })

    # Rule: Systematic Missingness
    if missing_data.get("has_systematic_missingness", False):
        top_corr = missing_data.get("missingness_correlations", [])[0]
        insights.append({
            "category": "quality",
            "severity": "medium",
            "title": "Systematic Missingness Pattern Detected",
            "description": f"Missingness in '{top_corr['col1']}' is strongly correlated with '{top_corr['col2']}' (r = {top_corr['correlation']:.2f}).",
            "recommendation": "Missing Not At Random (MNAR) or Missing At Random (MAR) is likely. Simple mean imputation will introduce bias; model the missingness mechanism or use pattern-aware algorithms (e.g. LightGBM/XGBoost native null handling).",
            "affected_columns": [top_corr["col1"], top_corr["col2"]]
        })

    # Rule: Duplicates
    if duplicates_data.get("duplicate_rows_count", 0) > 0:
        d_cnt = duplicates_data["duplicate_rows_count"]
        d_pct = duplicates_data["duplicate_percentage"]
        sev = "high" if d_pct > 5.0 else "medium"
        insights.append({
            "category": "quality",
            "severity": sev,
            "title": f"{d_cnt:,} Duplicate Rows Detected ({d_pct}%)",
            "description": f"The dataset contains {d_cnt:,} exact duplicate records ({d_pct}% of total dataset).",
            "recommendation": "Duplicates can lead to data leakage and artificially inflated cross-validation scores. Remove duplicates before splitting training and test sets.",
            "affected_columns": []
        })

    # Rule: Constant Columns
    for c_col in constant_cols:
        insights.append({
            "category": "quality",
            "severity": "high",
            "title": f"Zero-Variance Constant Column '{c_col}'",
            "description": f"Column '{c_col}' has identical values across all rows (0 variance).",
            "recommendation": "Drop this feature immediately as it provides zero discriminatory information to ML models and wastes memory.",
            "affected_columns": [c_col]
        })

    # Rule: ID-like Columns
    for id_col in id_cols:
        insights.append({
            "category": "quality",
            "severity": "low",
            "title": f"High Cardinality Identifier '{id_col}'",
            "description": f"Column '{id_col}' contains almost entirely unique values (>95% unique ratio).",
            "recommendation": "Ensure this column is excluded from ML feature matrix to avoid spurious memorization or overfitting.",
            "affected_columns": [id_col]
        })

    # Rule: Skewness & Distributions
    dist_cols = distributions_data.get("columns", {})
    for col_name, stats_info in dist_cols.items():
        skew = stats_info.get("skewness", 0.0)
        direction = stats_info.get("skew_direction", "symmetric")
        if abs(skew) >= 2.0:
            insights.append({
                "category": "distribution",
                "severity": "high",
                "title": f"Severe {direction.capitalize()} Skewness in '{col_name}'",
                "description": f"Column '{col_name}' exhibits extreme skewness (skew={skew:.2f}, kurtosis={stats_info.get('kurtosis'):.2f}).",
                "recommendation": "Apply non-linear power transformations like Log (`np.log1p`), Yeo-Johnson, or use tree-based ensembles that are invariant to monotonic scale.",
                "affected_columns": [col_name]
            })
        elif abs(skew) >= 1.0:
            insights.append({
                "category": "distribution",
                "severity": "medium",
                "title": f"Moderate {direction.capitalize()} Skewness in '{col_name}'",
                "description": f"Column '{col_name}' has noticeable distributional asymmetry (skew={skew:.2f}).",
                "recommendation": "Consider RobustScaler or Box-Cox transformation if training linear models or neural networks.",
                "affected_columns": [col_name]
            })

    # Rule: Outlier Multi-Method Consensus
    for col_outlier in outliers_data.get("columns", []):
        cons_cnt = col_outlier.get("consensus_count", 0)
        cons_pct = col_outlier.get("consensus_percentage", 0.0)
        col_name = col_outlier.get("column", "")
        if cons_pct >= 3.0 and cons_cnt >= 5:
            insights.append({
                "category": "outlier",
                "severity": "medium",
                "title": f"High Outlier Consensus in '{col_name}'",
                "description": f"{cons_cnt:,} records ({cons_pct}%) confirmed as statistical anomalies by 2+ detection methods (IQR / Z-Score / Isolation Forest).",
                "recommendation": "Inspect flagged records for measurement errors. Consider winsorizing (clipping at 1st/99th percentiles) or using robust loss functions (Huber loss).",
                "affected_columns": [col_name]
            })

    # Rule: Correlations & Multicollinearity
    top_pos = correlations_data.get("top_positive_pairs", [])
    top_neg = correlations_data.get("top_negative_pairs", [])
    
    for pair in top_pos:
        corr = pair.get("correlation", 0.0)
        if corr >= 0.85:
            insights.append({
                "category": "correlation",
                "severity": "high",
                "title": f"High Multicollinearity: '{pair['feature1']}' ↔ '{pair['feature2']}'",
                "description": f"Strong positive correlation (r = {corr:.2f}) between features. Redundant information present.",
                "recommendation": "Drop one of the collinear features or use PCA/Regularized models (Ridge/Lasso) to prevent variance inflation in linear models. Note: correlation does not imply causation.",
                "affected_columns": [pair["feature1"], pair["feature2"]]
            })
        elif corr >= 0.70:
            insights.append({
                "category": "correlation",
                "severity": "medium",
                "title": f"Substantial Correlation: '{pair['feature1']}' ↔ '{pair['feature2']}'",
                "description": f"Noticeable collinear relationship (r = {corr:.2f}).",
                "recommendation": "Check Variance Inflation Factor (VIF) if deploying regression models.",
                "affected_columns": [pair["feature1"], pair["feature2"]]
            })

    for pair in top_neg:
        corr = pair.get("correlation", 0.0)
        if corr <= -0.80:
            insights.append({
                "category": "correlation",
                "severity": "medium",
                "title": f"Strong Inverse Correlation: '{pair['feature1']}' ↔ '{pair['feature2']}'",
                "description": f"Strong negative association (r = {corr:.2f}).",
                "recommendation": "Investigate underlying business logic driving this trade-off relationship.",
                "affected_columns": [pair["feature1"], pair["feature2"]]
            })

    # Rule: High Cardinality Categoricals
    for card_info in high_card_cols:
        col_name = card_info["column"]
        u_cnt = card_info["unique_count"]
        insights.append({
            "category": "categorical",
            "severity": "medium",
            "title": f"High Cardinality Feature '{col_name}'",
            "description": f"Column '{col_name}' contains {u_cnt:,} unique categorical levels.",
            "recommendation": "Avoid naive One-Hot Encoding which creates excessive sparsity. Utilize Target Encoding, Frequency Encoding, or Embedding layers.",
            "affected_columns": [col_name]
        })

    # Rule: Target Intelligence (if supplied)
    if target_data:
        t_type = target_data.get("target_type")
        t_col = target_data.get("target_column")
        if target_data.get("is_imbalanced"):
            ratio = target_data.get("imbalance_ratio", 1.0)
            insights.append({
                "category": "target",
                "severity": "high",
                "title": f"Target Class Imbalance ({ratio:.1f}:1)",
                "description": f"Target '{t_col}' has a {ratio:.1f}:1 ratio between majority and minority classes.",
                "recommendation": "Use stratified splitting, threshold tuning, and optimize PR-AUC / Balanced Accuracy rather than overall accuracy.",
                "affected_columns": [t_col]
            })
        elif t_type in ["binary_classification", "multiclass_classification"]:
            insights.append({
                "category": "target",
                "severity": "low",
                "title": f"Target '{t_col}' is Well-Balanced",
                "description": "Class frequencies are evenly distributed across categories.",
                "recommendation": "Standard evaluation metrics like Accuracy and Cross-Entropy loss are well-suited.",
                "affected_columns": [t_col]
            })

    # Priority ordering: high -> medium -> low -> info
    sev_map = {"high": 0, "medium": 1, "low": 2, "info": 3}
    insights.sort(key=lambda x: sev_map.get(x["severity"], 99))

    high_count = len([i for i in insights if i["severity"] == "high"])
    med_count = len([i for i in insights if i["severity"] == "medium"])
    low_count = len([i for i in insights if i["severity"] == "low"])

    return {
        "quality_score": quality_score,
        "insights": insights,
        "high_severity_count": high_count,
        "medium_severity_count": med_count,
        "low_severity_count": low_count
    }
