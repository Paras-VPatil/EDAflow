# EDAflow — Automated Dataset Intelligence Platform

> **A production-grade automated EDA & dataset-intelligence platform** that transforms raw tabular datasets into structured statistical insights, multi-method anomaly profiles, target-aware machine learning preparation reports, and actionable recommendations.

---

## 🌟 Key Architecture & Highlights

```text
                               EDAflow Platform
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            │                                                   │
        FRONTEND                                             BACKEND
 React 18 + TypeScript                                   FastAPI + Python
 Tailwind CSS + Recharts                                Pure Analytical Services
            │                                                   │
            └─────────────────────────┬─────────────────────────┘
                                      │
                               ANALYSIS ENGINE
                                      │
       ┌───────────────┬──────────────┼───────────────┬───────────────┐
       ↓               ↓              ↓               ↓               ↓
   Profiler       Missingness    Distributions     Outliers      Correlations
       │               │              │               │               │
       └───────────────┴──────────────┼───────────────┴───────────────┘
                                      ↓
                               INSIGHT ENGINE
                          (Rule-Based Reasoning)
                                      ↓
                         Transparent Quality Score
                                      ↓
                           ML-Readiness Action Plan
                                      ↓
                          HTML / PDF / JSON Report
```

---

## 🔬 Analytical Service Engine (`backend/app/services/`)

1. **`profiler.py`**: Shape calculation, deep memory consumption, and rich semantic type inference (`numeric`, `categorical`, `datetime`, `boolean`, `constant`, `id_like`).
2. **`missing.py`**: Per-column null counts & percentages, overall missingness rate, and pairwise **Systematic Missingness Correlation Matrix** (detecting MAR / MNAR patterns).
3. **`duplicates.py`**: Exact duplicate row count, duplicate percentage, sampling, and 1-click dataset deduplication.
4. **`distributions.py`**: Parametric and non-parametric statistics (Mean, Median, Std Dev, Min, Max, Q1, Q3, IQR), Skewness (`scipy.stats.skew`), Kurtosis (`scipy.stats.kurtosis`), and **server-side histogram binning** (`numpy.histogram`).
5. **`outliers.py`**: Multi-method statistical anomaly detection combining:
   - Non-parametric IQR fences (`[Q1 - 1.5×IQR, Q3 + 1.5×IQR]`)
   - Parametric Z-Score (`|z| > 3.0`)
   - Multivariate Anomaly Detection with **Isolation Forest** (`sklearn.ensemble.IsolationForest`)
   - **Consensus Scoring** (rows flagged by 2+ methods)
6. **`correlations.py`**: Pearson (linear) and Spearman (rank) correlation matrices with programmatic ranking of strong collinear pairs above customizable thresholds.
7. **`categorical.py`**: Value counts, frequencies, proportions, and automatic **Top-10 + "Other" bucket aggregation** for high-cardinality features.
8. **`target.py`**: Automated Target Intelligence detecting **Binary Classification**, **Multiclass Classification**, or **Regression**, class imbalance ratios, SMOTE/weighting mitigations, and target-vs-feature cross-tab breakdowns.
9. **`insights.py`**: Rule-based intelligence engine emitting structured findings categorized with severity (🔴 High, 🟠 Medium, 🟡 Low), actionable ML preprocessing recommendations, and a transparent **Data Quality Score** (`100 - missingness_penalty - duplicate_penalty - outlier_penalty - invalid_type_penalty - cardinality_penalty`).

---

## 🚀 Quickstart Guide

### 1. Start Backend (FastAPI)
```bash
# From project root
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --port 8000 --reload
```
API Documentation will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Start Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Dashboard will be live at: [http://localhost:3000](http://localhost:3000)

### 3. Run Backend Test Suite
```bash
pytest backend/tests -v
```

---

## 📦 Built-In Demonstration Datasets
EDAflow includes 4 pre-loaded datasets for instant 1-click exploration:
- **Customer Churn (`customer_churn.csv`)**: Telecom churn with numerical metrics, missing total charges, and binary target.
- **Titanic Survival (`titanic_survival.csv`)**: Passenger survival data with cabin missingness, extreme fare outliers, and demographic categories.
- **California Housing (`california_housing.csv`)**: Continuous regression dataset predicting median house values.
- **Employee Attrition (`employee_attrition.csv`)**: HR analytics evaluating job satisfaction and employee retention.

---

## 🛠️ REST API Specification

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Ingest CSV, Excel, Parquet, or JSON with MIME/size validation |
| `POST` | `/api/analyze` | Execute complete EDA statistical and insight pipeline |
| `POST` | `/api/target-analysis` | Deep ML-readiness analysis for a selected target column |
| `GET` | `/api/sample-datasets` | List pre-packaged demo datasets |
| `GET` | `/api/download-deduplicated/{dataset_id}` | Export cleaned CSV with duplicates removed |
| `GET` | `/api/export-report/{dataset_id}` | Standalone responsive HTML executive report |
| `GET` | `/api/health` | Service health status check |
