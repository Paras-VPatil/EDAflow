import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "EDAflow"

def test_get_samples():
    response = client.get("/api/sample-datasets")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert len(data["data"]) >= 4

def test_analyze_sample():
    # Load first sample
    samples_res = client.get("/api/sample-datasets")
    sample_id = samples_res.json()["data"][0]["dataset_id"]
    
    # Run analysis
    res = client.post("/api/analyze", json={"dataset_id": sample_id})
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "ok"
    data = payload["data"]
    assert "profiler" in data
    assert "missing" in data
    assert "duplicates" in data
    assert "distributions" in data
    assert "outliers" in data
    assert "correlations" in data
    assert "categorical" in data
    assert "insights" in data

def test_target_analysis_api():
    samples_res = client.get("/api/sample-datasets")
    # Find customer churn sample
    churn_sample = next(s for s in samples_res.json()["data"] if "churn" in s["filename"])
    
    res = client.post("/api/target-analysis", json={
        "dataset_id": churn_sample["dataset_id"],
        "target_column": "Churn"
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["target_column"] == "Churn"
    assert data["target_type"] == "binary_classification"

def test_export_report():
    samples_res = client.get("/api/sample-datasets")
    sample_id = samples_res.json()["data"][0]["dataset_id"]

    res = client.get(f"/api/export-report/{sample_id}")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "EDAflow" in res.text

def test_download_deduplicated():
    samples_res = client.get("/api/sample-datasets")
    sample_id = samples_res.json()["data"][0]["dataset_id"]

    res = client.get(f"/api/download-deduplicated/{sample_id}")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
