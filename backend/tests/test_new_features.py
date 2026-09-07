import pytest
import pandas as pd
import numpy as np
import io
import json
from fastapi.testclient import TestClient

from app.main import app
from app.utils.storage import storage, sanitize_filename
from app.services.timeseries import analyze_timeseries
from app.services.baseline import fit_baseline_model
from app.services.drift import compare_datasets
from app.services.notebook_generator import generate_eda_notebook
from app.services.profiler import profile_dataset, infer_column_type

client = TestClient(app)

def test_sanitize_filename():
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("my data (1).csv") == "my_data__1_.csv"
    assert sanitize_filename("test.parquet").endswith(".parquet")

def test_semantic_types_free_text_and_geo():
    # Free text test
    text_data = pd.Series([
        "This is an extensive customer review explaining all the issues with product delivery.",
        "Another long detailed feedback paragraph describing performance and usability aspects.",
        "A third extensive comment submitted by an enterprise user requesting custom dashboard features.",
        "Detailed review number four giving four stars because of excellent support response time."
    ] * 5, name="review_text")
    
    prof_text = infer_column_type(text_data, len(text_data))
    assert prof_text["inferred_type"] == "free_text"
    assert prof_text["is_free_text"] is True

    # Geo lat test
    lat_data = pd.Series([37.7749, 34.0522, 40.7128, 51.5074, -33.8688], name="latitude")
    prof_lat = infer_column_type(lat_data, len(lat_data))
    assert prof_lat["inferred_type"] == "geo"
    assert prof_lat["is_geo"] is True

def test_timeseries_analysis():
    dates = pd.date_range(start="2023-01-01", periods=30, freq="D")
    values = np.linspace(10, 50, 30) + np.random.normal(0, 1, 30)
    df = pd.DataFrame({"timestamp": dates, "value": values})
    
    res = analyze_timeseries(df, "timestamp")
    assert res["has_timeseries"] is True
    assert res["inferred_frequency"] == "1 day"
    assert "value" in res["autocorrelations"]

def test_baseline_model_classification():
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "age": np.random.randint(18, 70, n),
        "income": np.random.uniform(20000, 100000, n),
        "department": np.random.choice(["Sales", "Engineering", "HR"], n),
        "target": np.random.choice([0, 1], n)
    })
    
    res = fit_baseline_model(df, "target", task_type="classification")
    assert "error" not in res
    assert res["task_type"] == "classification"
    assert "mean_accuracy" in res["metrics"]
    assert len(res["feature_importance"]) > 0

def test_baseline_model_regression():
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "feature_a": np.random.randn(n),
        "feature_b": np.random.randn(n),
        "price": np.random.uniform(100, 500, n)
    })
    
    res = fit_baseline_model(df, "price", task_type="regression")
    assert "error" not in res
    assert res["task_type"] == "regression"
    assert "mean_r2" in res["metrics"]
    assert len(res["feature_importance"]) > 0

def test_drift_analysis():
    df_train = pd.DataFrame({
        "feature_1": np.random.normal(10, 2, 200),
        "feature_2": np.random.normal(50, 5, 200),
        "cat_1": np.random.choice(["A", "B"], 200)
    })
    # Shifted test dataset
    df_test = pd.DataFrame({
        "feature_1": np.random.normal(25, 2, 200), # Severe drift
        "feature_2": np.random.normal(50, 5, 200), # No drift
        "cat_1": np.random.choice(["A", "B"], 200)
    })
    
    drift = compare_datasets(df_train, df_test)
    assert drift["baseline_summary"]["rows"] == 200
    assert len(drift["numeric_drift"]) == 2
    f1_drift = next(d for d in drift["numeric_drift"] if d["column"] == "feature_1")
    assert f1_drift["has_drift"] is True

def test_notebook_generator():
    df = pd.DataFrame({"col_a": [1, 2, 3, 4, 5], "col_b": [10, 20, 30, 40, 50]})
    prof = profile_dataset(df)
    nb_json = generate_eda_notebook("test_data.csv", prof, "col_b")
    parsed = json.loads(nb_json)
    assert "cells" in parsed
    assert len(parsed["cells"]) >= 4

def test_api_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["storage"]["writable"] is True
    assert data["loaded_samples_count"] >= 4

def test_api_excel_sheets_and_multi_sheet_upload():
    # Create an in-memory excel file with two sheets
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        pd.DataFrame({"a": [1, 2, 3]}).to_excel(writer, sheet_name="Customers", index=False)
        pd.DataFrame({"x": [10, 20], "y": [30, 40]}).to_excel(writer, sheet_name="Orders", index=False)
    buffer.seek(0)
    
    # Check sheet inspection
    resp_sheets = client.post(
        "/api/excel-sheets",
        files={"file": ("multi_sheet.xlsx", buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert resp_sheets.status_code == 200
    assert resp_sheets.json()["sheets"] == ["Customers", "Orders"]

    # Upload specific sheet
    resp_upload = client.post(
        "/api/upload",
        files={"file": ("multi_sheet.xlsx", buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"sheet_name": "Orders"}
    )
    assert resp_upload.status_code == 200
    assert resp_upload.json()["data"]["columns"] == 2

def test_api_exports():
    # Use existing sample
    sample_id = "sample_customer_churn"
    
    # Test notebook export
    res_nb = client.get(f"/api/export-notebook/{sample_id}")
    assert res_nb.status_code == 200
    assert "application/x-ipynb+json" in res_nb.headers.get("content-type", "")

    # Test markdown export
    res_md = client.get(f"/api/export-markdown/{sample_id}")
    assert res_md.status_code == 200
    assert "text/markdown" in res_md.headers.get("content-type", "")
    assert b"EDAflow Intelligence Report" in res_md.content

def test_baseline_single_class_target_fails_gracefully():
    df = pd.DataFrame({
        "feature_1": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "feature_2": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
        "target": ["constant_class"] * 10
    })
    res = fit_baseline_model(df, "target")
    assert "error" in res
    assert "only 1 unique" in res["error"]

def test_baseline_pure_categorical_predictors():
    df = pd.DataFrame({
        "cat_1": ["Low", "Med", "High", "Low", "Med", "High", "Low", "Med", "High", "Low"] * 3,
        "cat_2": ["Red", "Blue", "Green", "Red", "Blue", "Green", "Red", "Blue", "Green", "Red"] * 3,
        "target": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1] * 3
    })
    res = fit_baseline_model(df, "target", task_type="classification")
    assert "error" not in res
    assert res["task_type"] == "classification"
    assert "mean_accuracy" in res["metrics"]
    assert len(res["feature_importance"]) > 0

def test_baseline_pure_numeric_predictors():
    df = pd.DataFrame({
        "num_1": np.linspace(1, 100, 30),
        "num_2": np.linspace(100, 1, 30),
        "target": [0 if x < 15 else 1 for x in range(30)]
    })
    res = fit_baseline_model(df, "target", task_type="classification")
    assert "error" not in res
    assert res["task_type"] == "classification"
    assert "mean_accuracy" in res["metrics"]

def test_calculate_psi_edge_cases():
    from app.services.drift import calculate_psi
    # Disjoint arrays
    exp = np.array([1, 2, 3, 4, 5] * 10)
    act = np.array([100, 200, 300, 400, 500] * 10)
    psi = calculate_psi(exp, act)
    assert psi >= 0.0
    assert not np.isnan(psi)
    assert not np.isinf(psi)

