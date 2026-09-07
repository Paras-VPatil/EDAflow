# EDAflow — Automated Dataset Intelligence Platform

> **A production-grade automated EDA & dataset-intelligence platform** that transforms raw tabular datasets into structured statistical insights, multi-method anomaly profiles, target-aware machine learning preparation reports, dataset drift analysis, and exportable artifacts (HTML, Jupyter Notebook `.ipynb`, Markdown, Clean CSV).

---

## 🌟 Key Architecture & Highlights

```text
                               EDAflow Platform
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            │                                                   │
        FRONTEND                                             BACKEND
 React 18 + TypeScript                                   FastAPI + Python
 Tailwind CSS + Recharts                             Pure Analytical Services
            │                                                   │
            └─────────────────────────┬─────────────────────────┘
                                      │
                              ANALYSIS ENGINE
                                      │
   ┌───────────────┬──────────────┼──────────────┬──────────────┬──────────────┐
   ↓               ↓              ↓              ↓              ↓              ↓
Profiler      Missingness   Distributions     Outliers    Correlations    Drift / Timeseries
   │               │              │              │              │              │
   └───────────────┴──────────────┼──────────────┴──────────────┴──────────────┘
                                  ↓
                            INSIGHT ENGINE
                        (Rule-Based Reasoning)
                                  ↓
                       Transparent Quality Score
                                  ↓
                     Baseline Model "Score to Beat"
                                  ↓
              Artifact Exports (HTML, .ipynb, .md, Clean CSV)
```

---

## 🔬 Analytical Service Engine (`backend/app/services/`)

1. **`profiler.py`**: Shape calculation, deep memory consumption, and rich semantic type inference (`numeric`, `categorical`, `datetime`, `boolean`, `constant`, `id_like`, `free_text`, `geo`).
2. **`storage.py`**: Resilient ingestion with auto-charset detection (`charset-normalizer`), delimiter auto-sniffing, bad-line skipping, multi-sheet Excel inspection, filename sanitization, and automated sampling for large datasets.
3. **`missing.py`**: Per-column null counts & percentages, overall missingness rate, and pairwise **Systematic Missingness Correlation Matrix** (detecting MAR / MNAR patterns).
4. **`duplicates.py`**: Exact duplicate row count, duplicate percentage, sampling, and 1-click dataset deduplication.
5. **`distributions.py`**: Parametric and non-parametric statistics (Mean, Median, Std Dev, Min, Max, Q1, Q3, IQR), Skewness, Kurtosis, and **server-side histogram binning**.
6. **`outliers.py`**: Multi-method statistical anomaly detection combining:
   - Non-parametric IQR fences (`[Q1 - 1.5×IQR, Q3 + 1.5×IQR]`)
   - Parametric Z-Score (`|z| > 3.0`)
   - Multivariate Anomaly Detection with **Isolation Forest**
   - **Consensus Scoring** (rows flagged by 2+ methods)
7. **`correlations.py`**: Pearson (linear) and Spearman (rank) correlation matrices with ranking of strong collinear pairs and protection against wide-dataset slowdowns.
8. **`categorical.py`**: Value counts, frequencies, proportions, and automatic **Top-10 + "Other" bucket aggregation** for high-cardinality features.
9. **`target.py` & `baseline.py`**: Automated Target Intelligence with 5-Fold Cross-Validated **Baseline Model Benchmark ("Score to Beat")** and **Mutual Information Feature Importance Ranking**.
10. **`drift.py`**: Two-dataset drift comparison engine evaluating schema shift, missingness drift, and **Kolmogorov-Smirnov / PSI** distribution drift.
11. **`timeseries.py`**: Temporal regularity, frequency inference, trend slopes, and lag-1 / lag-7 autocorrelation.
12. **`notebook_generator.py`**: Dynamic generation of executable Jupyter Notebooks (`.ipynb`) reproducing the analysis in pure Python.
13. **`insights.py`**: Rule-based intelligence engine emitting structured findings categorized with severity (🔴 High, 🟠 Medium, 🟡 Low), actionable ML preprocessing recommendations, and a transparent **Data Quality Score**.

---

## 🐳 Docker Quickstart (One-Command Deployment)

Run the full stack (FastAPI Backend + Nginx/React Frontend) with Docker Compose:

```bash
docker compose up --build
```
- **Web Dashboard**: [http://localhost:3000](http://localhost:3000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🚀 Local Development Setup

### 1. Start Backend (FastAPI)
```bash
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --port 8000 --reload
```

### 2. Start Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

### 3. Run Backend Test Suite
```bash
pytest backend/tests -v
```

### 4. Build Frontend for Production
```bash
cd frontend
npm run build
```

---

## 📦 Built-In Demonstration Datasets
EDAflow includes 4 pre-loaded datasets for instant 1-click exploration:
- **Customer Churn (`customer_churn.csv`)**: Telecom churn with numerical metrics, missing total charges, and binary target.
- **Titanic Survival (`titanic_survival.csv`)**: Passenger survival data with cabin missingness, extreme fare outliers, and demographic categories.
- **California Housing (`california_housing.csv`)**: Continuous regression dataset predicting median house values.
- **Employee Attrition (`employee_attrition.csv`)**: HR analytics evaluating factors predicting employee resignation vs retention.

---

## 🛠️ REST API Specification

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Ingest CSV, Excel, Parquet, or JSON with charset detection and delimiter sniffing |
| `POST` | `/api/excel-sheets` | List available sheet names in an Excel workbook |
| `POST` | `/api/analyze` | Execute complete statistical profiling and insight pipeline |
| `POST` | `/api/target-analysis` | Target diagnostics, baseline model fitting ("Score to Beat"), and feature importance |
| `POST` | `/api/drift-analysis` | Compare two datasets for schema mismatch and distribution drift (KS / PSI) |
| `POST` | `/api/timeseries-analysis` | Temporal frequency inference, autocorrelation, and trend analysis |
| `GET` | `/api/sample-datasets` | List pre-packaged demo datasets |
| `GET` | `/api/download-deduplicated/{id}` | Export cleaned CSV with duplicates removed |
| `GET` | `/api/export-report/{id}` | Standalone responsive HTML executive report |
| `GET` | `/api/export-notebook/{id}` | Download executable Jupyter Notebook (`.ipynb`) reproducing the analysis |
| `GET` | `/api/export-markdown/{id}` | Download GitHub-ready Markdown report (`.md`) |
| `GET` | `/api/health` | Deep health check (storage writability and disk capacity probe) |
