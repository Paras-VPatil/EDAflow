import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
import pandas as pd

client = TestClient(app)
TEST_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "test_datasets"

def test_clean_dataset_pipeline():
    file_path = TEST_DATA_DIR / "01_clean.csv"
    with open(file_path, "rb") as f:
        res = client.post("/api/upload", files={"file": ("01_clean.csv", f, "text/csv")})
    assert res.status_code == 200
    dataset_id = res.json()["data"]["dataset_id"]

    res_ana = client.post("/api/analyze", json={"dataset_id": dataset_id})
    assert res_ana.status_code == 200
    data = res_ana.json()["data"]
    assert len(data["profiler"]["numeric_columns"]) == 3
    assert data["missing"]["total_missing_cells"] == 0

def test_empty_and_header_only_rejection():
    # 03_empty.csv
    file_path = TEST_DATA_DIR / "03_empty.csv"
    with open(file_path, "rb") as f:
        res = client.post("/api/upload", files={"file": ("03_empty.csv", f, "text/csv")})
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()

    # 04_header_only.csv
    file_path_h = TEST_DATA_DIR / "04_header_only.csv"
    with open(file_path_h, "rb") as f:
        res = client.post("/api/upload", files={"file": ("04_header_only.csv", f, "text/csv")})
    # Should either succeed profile with 0 rows or reject gracefully
    assert res.status_code in [200, 400, 422]

def test_single_row_dataset():
    file_path = TEST_DATA_DIR / "05_one_row.csv"
    with open(file_path, "rb") as f:
        res = client.post("/api/upload", files={"file": ("05_one_row.csv", f, "text/csv")})
    assert res.status_code == 200
    dataset_id = res.json()["data"]["dataset_id"]

    res_ana = client.post("/api/analyze", json={"dataset_id": dataset_id})
    assert res_ana.status_code == 200
    data = res_ana.json()["data"]
    assert data["profiler"]["rows_count"] == 1

def test_all_missing_column_dataset():
    file_path = TEST_DATA_DIR / "08_all_missing_column.csv"
    with open(file_path, "rb") as f:
        res = client.post("/api/upload", files={"file": ("08_all_missing_column.csv", f, "text/csv")})
    assert res.status_code == 200
    dataset_id = res.json()["data"]["dataset_id"]

    res_ana = client.post("/api/analyze", json={"dataset_id": dataset_id})
    assert res_ana.status_code == 200
    data = res_ana.json()["data"]
    occ_col = next(c for c in data["missing"]["columns"] if c["column"] == "occupation")
    assert occ_col["missing_percentage"] == 100.0

def test_constant_column_dataset():
    file_path = TEST_DATA_DIR / "12_constant.csv"
    with open(file_path, "rb") as f:
        res = client.post("/api/upload", files={"file": ("12_constant.csv", f, "text/csv")})
    assert res.status_code == 200
    dataset_id = res.json()["data"]["dataset_id"]

    res_ana = client.post("/api/analyze", json={"dataset_id": dataset_id})
    assert res_ana.status_code == 200
    data = res_ana.json()["data"]
    assert "constant" in data["profiler"]["constant_columns"]

def test_high_cardinality_dataset():
    file_path = TEST_DATA_DIR / "13_high_cardinality.csv"
    with open(file_path, "rb") as f:
        res = client.post("/api/upload", files={"file": ("13_high_cardinality.csv", f, "text/csv")})
    assert res.status_code == 200
    dataset_id = res.json()["data"]["dataset_id"]

    res_ana = client.post("/api/analyze", json={"dataset_id": dataset_id})
    assert res_ana.status_code == 200
    data = res_ana.json()["data"]
    city_cat = next(c for c in data["categorical"]["columns"] if c["column"] == "city")
    assert city_cat["is_high_cardinality"] is True
    assert city_cat["other_bucket_count"] > 0

def test_outlier_multivariate_dataset():
    file_path = TEST_DATA_DIR / "20_multivariate_anomaly.csv"
    with open(file_path, "rb") as f:
        res = client.post("/api/upload", files={"file": ("20_multivariate_anomaly.csv", f, "text/csv")})
    assert res.status_code == 200
    dataset_id = res.json()["data"]["dataset_id"]

    res_ana = client.post("/api/analyze", json={"dataset_id": dataset_id})
    assert res_ana.status_code == 200
    data = res_ana.json()["data"]
    assert data["outliers"]["multivariate_anomaly_count"] > 0

def test_single_class_target_resilience():
    file_path = TEST_DATA_DIR / "29_single_class_target.csv"
    with open(file_path, "rb") as f:
        res = client.post("/api/upload", files={"file": ("29_single_class_target.csv", f, "text/csv")})
    assert res.status_code == 200
    dataset_id = res.json()["data"]["dataset_id"]

    res_target = client.post("/api/target-analysis", json={"dataset_id": dataset_id, "target_column": "target"})
    assert res_target.status_code == 200
    data = res_target.json()["data"]
    assert data["target_type"] == "single_class_trivial"
    assert len(data["mitigations"]) > 0

def test_disaster_dataset_resilience():
    """Ultimate stress test combining missingness, duplicates, outliers, skewness, constant, all-null, and imbalanced target."""
    file_path = TEST_DATA_DIR / "30_disaster_dataset.csv"
    with open(file_path, "rb") as f:
        res = client.post("/api/upload", files={"file": ("30_disaster_dataset.csv", f, "text/csv")})
    assert res.status_code == 200
    dataset_id = res.json()["data"]["dataset_id"]

    res_ana = client.post("/api/analyze", json={"dataset_id": dataset_id, "target_column": "churn"})
    assert res_ana.status_code == 200
    data = res_ana.json()["data"]
    
    # Assertions on disaster dataset
    assert data["duplicates"]["duplicate_rows_count"] >= 4
    assert data["missing"]["total_missing_cells"] > 0
    assert "constant_col" in data["profiler"]["constant_columns"]
    assert data["insights"]["quality_score"]["final_score"] < 90
    assert len(data["insights"]["insights"]) > 0

def test_security_file_rejections():
    # Attempt uploading .exe
    file_path_exe = TEST_DATA_DIR / "invalid" / "malicious.exe"
    with open(file_path_exe, "rb") as f:
        res_exe = client.post("/api/upload", files={"file": ("malicious.exe", f, "application/octet-stream")})
    assert res_exe.status_code == 400
    assert "unsupported" in res_exe.json()["detail"].lower()

    # Attempt uploading .py
    file_path_py = TEST_DATA_DIR / "invalid" / "test.py"
    with open(file_path_py, "rb") as f:
        res_py = client.post("/api/upload", files={"file": ("test.py", f, "text/x-python")})
    assert res_py.status_code == 400
    assert "unsupported" in res_py.json()["detail"].lower()
