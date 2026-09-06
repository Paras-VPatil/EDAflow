import pytest
import pandas as pd
import numpy as np
from app.services.profiler import profile_dataset, infer_column_type
from app.services.missing import analyze_missingness
from app.services.duplicates import analyze_duplicates, deduplicate_dataframe
from app.services.distributions import analyze_distributions
from app.services.outliers import analyze_outliers
from app.services.correlations import analyze_correlations
from app.services.categorical import analyze_categorical
from app.services.target import analyze_target
from app.services.insights import generate_insights_and_quality

@pytest.fixture
def sample_df():
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "id": [f"ID_{i}" for i in range(n)],
        "age": np.random.normal(35, 10, size=n),
        "income": np.random.exponential(50000, size=n),
        "department": np.random.choice(["Sales", "Engineering", "HR"], size=n),
        "is_active": np.random.choice([0, 1], size=n),
        "constant_col": ["Fixed"] * n,
        "missing_col": [np.nan if i < 30 else float(i) for i in range(n)],
        "missing_col_correlated": [np.nan if i < 28 else float(i*2) for i in range(n)],
        "churn": np.random.choice(["Yes", "No"], size=n, p=[0.2, 0.8])
    })

def test_profiler(sample_df):
    profile = profile_dataset(sample_df)
    assert profile["rows_count"] == 100
    assert profile["columns_count"] == 9
    assert "constant_col" in profile["constant_columns"]
    assert "id" in profile["id_like_columns"]
    assert "is_active" in profile["boolean_columns"]
    assert "age" in profile["numeric_columns"]

def test_missingness(sample_df):
    missing = analyze_missingness(sample_df)
    assert missing["total_missing_cells"] == 58
    assert missing["has_systematic_missingness"] is True
    assert len(missing["missingness_correlations"]) > 0

def test_duplicates():
    df = pd.DataFrame({
        "a": [1, 2, 2, 3],
        "b": ["x", "y", "y", "z"]
    })
    dups = analyze_duplicates(df)
    assert dups["duplicate_rows_count"] == 1
    assert dups["has_duplicates"] is True
    
    deduped = deduplicate_dataframe(df)
    assert len(deduped) == 3

def test_distributions(sample_df):
    dists = analyze_distributions(sample_df, numeric_columns=["age", "income"])
    assert "age" in dists["columns"]
    assert "income" in dists["columns"]
    
    income_stat = dists["columns"]["income"]
    assert income_stat["skewness"] > 0
    assert len(income_stat["histogram"]["counts"]) > 0
    assert len(income_stat["histogram"]["bin_edges"]) == len(income_stat["histogram"]["counts"]) + 1

def test_outliers(sample_df):
    outliers = analyze_outliers(sample_df, numeric_columns=["age", "income"])
    assert "columns" in outliers
    assert outliers["multivariate_anomaly_count"] >= 0
    for col_info in outliers["columns"]:
        assert "iqr_outliers_count" in col_info
        assert "zscore_outliers_count" in col_info
        assert "consensus_count" in col_info

def test_correlations():
    np.random.seed(42)
    x = np.linspace(0, 10, 50)
    y = x * 2.5 + np.random.normal(0, 0.1, 50)
    z = -x * 3.0 + np.random.normal(0, 0.1, 50)
    df = pd.DataFrame({"x": x, "y": y, "z": z})
    
    corrs = analyze_correlations(df, numeric_columns=["x", "y", "z"])
    assert len(corrs["top_positive_pairs"]) >= 1
    assert corrs["top_positive_pairs"][0]["correlation"] > 0.95
    assert len(corrs["top_negative_pairs"]) >= 1
    assert corrs["top_negative_pairs"][0]["correlation"] < -0.95

def test_categorical(sample_df):
    cats = analyze_categorical(sample_df, categorical_columns=["department"])
    assert len(cats["columns"]) == 1
    dept_info = cats["columns"][0]
    assert dept_info["unique_count"] == 3
    assert len(dept_info["frequencies"]) == 3

def test_target_classification(sample_df):
    target_info = analyze_target(sample_df, "churn")
    assert target_info["target_type"] == "binary_classification"
    assert target_info["imbalance_ratio"] >= 2.0
    assert len(target_info["mitigations"]) > 0
    assert len(target_info["numeric_cross_breakdown"]) > 0

def test_target_regression(sample_df):
    target_info = analyze_target(sample_df, "income")
    assert target_info["target_type"] == "regression"
    assert target_info["regression_stats"] is not None
    assert len(target_info["feature_correlations"]) > 0

def test_insights_and_quality(sample_df):
    profile = profile_dataset(sample_df)
    missing = analyze_missingness(sample_df)
    dups = analyze_duplicates(sample_df)
    dists = analyze_distributions(sample_df, profile["numeric_columns"])
    outliers = analyze_outliers(sample_df, profile["numeric_columns"])
    corrs = analyze_correlations(sample_df, profile["numeric_columns"])
    cats = analyze_categorical(sample_df, profile["categorical_columns"])
    target = analyze_target(sample_df, "churn")

    insights = generate_insights_and_quality(profile, missing, dups, dists, outliers, corrs, cats, target)
    
    q_score = insights["quality_score"]
    assert 0 <= q_score["final_score"] <= 100
    assert q_score["grade"] in ["A", "B", "C", "D", "F"]
    assert len(insights["insights"]) > 0
