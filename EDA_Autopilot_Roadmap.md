# EDA Autopilot — Implementation Roadmap

**A production-oriented plan for building an automated dataset-intelligence platform**

---

## 1. High-Level Architecture & Decision Tree

Before writing code, lock in the shape of the system. Everything downstream depends on these four decisions.

```
                        ┌─────────────────────────┐
                        │   Decision Tree          │
                        └─────────────────────────┘

Q1: Sync or async processing?
    Small files (<50MB, MVP)  → Synchronous FastAPI endpoint
    Large files (production)  → Background job (Celery/RQ) + polling/websocket

Q2: Store the raw file or just results?
    Portfolio/demo            → Ephemeral storage, delete after N hours
    Production                → Object storage (S3/local disk) + metadata in Postgres

Q3: Compute engine?
    <1M rows                  → Pandas (simplicity wins)
    >1M rows / wide files     → Polars or DuckDB (add later, don't over-engineer MVP)

Q4: Report delivery?
    Interactive first          → JSON API + React dashboard (recommended)
    Static export second       → HTML/PDF generated from same JSON
```

**Recommended default path:** synchronous processing for MVP → background jobs in Phase 5, Pandas as the only engine until Phase 6, JSON-first API with a React dashboard, static exports as a later convenience feature.

### System Data Flow

```
┌──────────┐   1. Upload    ┌──────────────┐   2. Validate    ┌───────────────┐
│  React   │ ─────────────► │   FastAPI     │ ───────────────► │  File checks  │
│ Frontend │                │  /upload      │                  │ size/type/MIME│
└──────────┘                └───────┬───────┘                  └───────┬───────┘
      ▲                             │                                  │
      │                             ▼                                  ▼
      │                     ┌───────────────┐                 ┌────────────────┐
      │                     │ Persist file  │ ◄────────────── │  Sanitize name │
      │                     │ + dataset row │                 │  reject exec   │
      │                     │ in Postgres   │                 └────────────────┘
      │                             │
      │                             ▼
      │                     ┌───────────────────────┐
      │   3. Poll/GET       │  Analysis Engine        │
      │◄────────────────────│  (services/*.py)        │
      │                     │  profiler → quality →   │
      │                     │  stats → outliers →      │
      │                     │  correlations → target   │
      │                     └───────────┬─────────────┘
      │                                 ▼
      │                     ┌───────────────────────┐
      │   4. Render          │  Insight + Recommend   │
      │◄────────────────────│  Engine (rule-based)    │
      │                     └───────────┬─────────────┘
      │                                 ▼
      │                     ┌───────────────────────┐
      └────────────────────►│  Report JSON persisted │
        5. Export HTML/PDF   │  + served via REST      │
                             └───────────────────────┘
```

Every analysis module returns a **plain JSON-serializable dict**. This is the single most important design decision: it decouples computation from presentation, lets you build the frontend independently, and gives you the JSON export feature for free.

---

## 2. Technology Stack — With Rationale

| Layer | Choice | Why this over alternatives |
|---|---|---|
| Frontend | **React + TypeScript** | Type safety catches malformed API responses early; huge charting ecosystem; directly resume-relevant since most DS job postings expect familiarity with a modern frontend for internal tools. |
| Styling | **Tailwind CSS** | Fast to build a clean dashboard without fighting a component library; pairs well with a design system for the "polished, stakeholder-ready" report requirement. |
| Charts | **Recharts** (primary), **Plotly** (for anything needing zoom/pan, e.g. large scatter/correlation matrices) | Recharts is lightweight and composable for standard bar/histogram/line needs; Plotly covers interactive statistical plots (box, violin) without you hand-rolling SVG math. |
| Backend | **Python + FastAPI** | Async-native, automatic OpenAPI docs (useful for the "API-friendly" requirement), Pydantic gives you free request/response validation — critical when users upload arbitrary CSVs. |
| Data processing | **Pandas + NumPy + SciPy** | Industry-standard for tabular EDA; SciPy gives you proper stats (skew, kurtosis, Shapiro-Wilk) without reimplementing formulas. |
| ML utilities | **Scikit-learn** | IsolationForest for multivariate outliers, `train_test_split` stratification checks, preprocessing utilities — reused later for a possible "auto-modeling" Phase 6/7. |
| Large-data engine (later) | **Polars or DuckDB** | Only added once you hit real memory pressure; DuckDB is attractive because it can run SQL-style aggregations directly over a CSV/Parquet without full in-memory load. |
| Database | **PostgreSQL** | Relational integrity for `users → datasets → analysis_runs → reports`; JSONB columns let you store the flexible analysis-result payloads without schema churn. |
| File storage | **Local disk (dev) → S3-compatible bucket (prod)** | Keep an abstraction layer (`StorageBackend` interface) from day one so swapping is a config change, not a rewrite. |
| Background jobs | **Celery + Redis** (or RQ for simpler setup) | Needed once files get large enough that synchronous processing blocks the request thread. |
| Testing | **pytest** (backend), **Vitest + React Testing Library** (frontend) | Standard, well-documented, integrates cleanly with CI. |
| Containerization | **Docker + docker-compose** | Reproducible local dev, and a straightforward path to any cloud (Fly.io, Render, AWS ECS). |
| CI/CD | **GitHub Actions** | Free for public repos, trivial to wire up lint + test + build on every PR — a strong signal in a portfolio project. |

**Rationale summary for a reviewer:** every choice is justified by a concrete requirement in the spec (validation → Pydantic, large files → DuckDB/Polars later, stakeholder-ready report → charting library split), not by trend-following. Be ready to explain *why not* Streamlit/Dash: those are excellent for prototyping but conflate frontend and backend in a way that undersells full-stack engineering skill, which is explicitly part of what this project should demonstrate.

---

## 3. Architecture Overview

### 3.1 Project Structure

```
eda-autopilot/
├── frontend/                  # React + TS + Tailwind
│   ├── src/
│   │   ├── components/        # Charts, tables, cards
│   │   ├── pages/              # Overview, Quality, Distributions, ...
│   │   ├── api/                # typed fetch wrappers
│   │   └── types/               # mirrors backend Pydantic schemas
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/                 # thin route handlers
│   │   │   ├── upload.py
│   │   │   ├── analysis.py
│   │   │   └── reports.py
│   │   ├── services/            # pure analysis logic, framework-agnostic
│   │   │   ├── profiler.py
│   │   │   ├── missing.py
│   │   │   ├── duplicates.py
│   │   │   ├── distributions.py
│   │   │   ├── outliers.py
│   │   │   ├── correlations.py
│   │   │   ├── categorical.py
│   │   │   ├── target.py
│   │   │   └── insights.py
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/               # Pydantic request/response models
│   │   └── utils/                  # storage backend, sanitization, chunking
│   └── requirements.txt
├── tests/
├── sample_data/
├── docs/
├── Dockerfile
├── docker-compose.yml
└── README.md
```

**Key principle:** `services/` never imports FastAPI. Each service function takes a DataFrame (or path) and returns a dict. This makes every analysis function independently unit-testable and reusable in a notebook, a CLI, or a batch job — a detail worth calling out in interviews as evidence of separation-of-concerns thinking.

### 3.2 Data Flow Contract

Define the shape early. Every service returns something like:

```python
{
  "status": "ok",
  "data": { ... },       # the actual metrics
  "warnings": [ ... ],   # e.g. "column has 100% missing values"
  "meta": { "computed_at": ..., "duration_ms": ... }
}
```

This uniform envelope means the Insight Engine can iterate over all service outputs without special-casing each one.

### 3.3 Database Schema (minimum viable)

```sql
users            (id, email, created_at)
datasets         (id, user_id, filename, storage_path, rows, columns, uploaded_at)
analysis_runs    (id, dataset_id, status, started_at, completed_at)
reports          (id, analysis_run_id, section, result_json, created_at)
```

Storing each section (`overview`, `missing`, `outliers`, ...) as its own row with a JSONB `result_json` lets the frontend fetch sections independently and lets you re-run a single section without recomputing everything.

---

## 4. Development Roadmap

Effort estimates assume solo development, evenings/weekends pace, moderate FastAPI/React familiarity. Adjust down if working full-time on it.

### Phase 1 — Core EDA Engine (MVP) — ~2 weeks

**Goal:** a working pipeline from CSV to basic report, end to end, even if ugly.

Deliverables:
- CSV upload endpoint with size/type/MIME validation
- `profiler.py`: shape, dtypes, memory usage, auto feature-type inference (numeric/categorical/datetime/boolean/constant/ID-like)
- `missing.py`: per-column missing count/percentage
- `duplicates.py`: duplicate row detection and rate
- `distributions.py`: mean/median/std/min/max/quartiles for numeric columns
- Minimal React page rendering these four sections as tables (no charts yet)

**Why this order:** profiling must exist before anything else can reason about the data (you can't detect outliers in a column you haven't typed correctly). Missing/duplicates are the cheapest wins and immediately make the tool feel useful.

**Milestone check:** upload a messy CSV (mixed types, some empty columns) and get correct numbers back without a crash.

---

### Phase 2 — Advanced Analytics — ~2–3 weeks

**Goal:** move from "descriptive statistics" to "statistical reasoning," which is what differentiates this from `df.describe()`.

Deliverables:
- `distributions.py` extended: skewness, kurtosis, histogram bin data for frontend rendering
- `outliers.py`: IQR method, Z-score method, IsolationForest — return all three plus a simple agreement/confidence heuristic
- `correlations.py`: Pearson matrix for numeric columns, automatic extraction of "strong" pairs above a threshold (e.g. |r| > 0.6)
- `categorical.py`: value counts, proportions, high-cardinality detection with automatic "top-N + Other" grouping
- Frontend: real charts (histogram, correlation heatmap, bar charts for categoricals) via Recharts/Plotly

**Why this order:** these features depend on correct type inference from Phase 1, and they're independent of each other, so they can be built and tested in parallel.

**Milestone check:** a dataset with a genuinely skewed column and a genuinely high-cardinality column produces the correct warnings.

---

### Phase 3 — Target Intelligence — ~1.5–2 weeks

**Goal:** turn the tool from generic EDA into an ML-prep assistant.

Deliverables:
- Target column selector in the UI
- `target.py`: automatic target-type detection (binary/multiclass/regression) based on dtype + unique-value heuristics
- Class distribution and imbalance ratio calculation for classification targets
- Target-vs-numerical breakdowns (grouped means, boxplot data)
- Target-vs-categorical breakdowns (per-category rate, e.g. churn rate by occupation)

**Why this order:** target analysis is meaningless without correlations and categorical analysis already in place (you need to know which features to cross against the target).

**Milestone check:** selecting a binary target correctly reports imbalance ratio and produces sensible per-category rates.

---

### Phase 4 — Insight & Recommendation Engine — ~1–1.5 weeks

**Goal:** the differentiating feature. Convert raw statistics into prioritized, human-readable findings.

Deliverables:
- `insights.py`: rule engine that scans all prior service outputs and emits structured findings, e.g.
  ```python
  if skewness > 1: emit("distribution", "high", f"{col} is right-skewed (skew={skewness:.2f})")
  if missing_pct > 0.2: emit("quality", "high", f"{col} has {missing_pct:.1%} missing values")
  if abs(corr) > 0.7: emit("relationship", "medium", f"{a} and {b} are strongly correlated (r={corr:.2f})")
  ```
- Severity tagging (🔴/🟠/🟡) and simple prioritization (sort by severity, then by how many rows/columns affected)
- Recommendation text paired with each insight (e.g. skew → suggest log1p/RobustScaler, never auto-transform)
- Data Quality Score: a transparent weighted formula (`100 - missingness_penalty - duplicate_penalty - outlier_penalty - invalid_type_penalty`), with the breakdown shown to the user, not just the final number
- Dashboard home page summarizing rows/columns/quality score/top issues

**Why this order:** the insight engine is a pure function of everything computed in Phases 1–3, so it must come last among analysis features. Building it earlier would mean constantly rewriting it as new service outputs are added.

**Milestone check:** insights read naturally, never claim causation, and match manual inspection of the same dataset.

---

### Phase 5 — Productionization — ~2–3 weeks

**Goal:** move from "runs on my machine" to something you'd trust with a stranger's file.

Deliverables:
- Authentication (JWT-based, simple email/password or OAuth)
- Persist datasets/analysis runs/reports in PostgreSQL (schema in §3.3)
- Background job processing (Celery + Redis) so large uploads don't block the request thread; frontend polls a status endpoint or subscribes via websocket
- HTML and PDF report export (server-rendered from the same JSON payload — do not duplicate calculation logic in a templating layer)
- Dockerfile + docker-compose for one-command local spin-up
- CI pipeline: lint (ruff/eslint) + test (pytest/vitest) + build on every PR

**Why this order:** productionization features (auth, persistence, background jobs) are infrastructure concerns that are far easier to bolt onto a stable, feature-complete analysis engine than to build in parallel with it.

**Milestone check:** two concurrent users can each upload a file, log out, log back in, and see their analysis history.

---

### Phase 6 — Scale & Deployment — ~1.5–2 weeks (optional but high-value)

**Goal:** handle files that don't fit comfortably in memory, and put the app somewhere real.

Deliverables:
- Chunked/streaming processing path for files above a size threshold; swap to Polars or DuckDB for aggregation-heavy computations on those files
- File security hardening: extension allowlist, MIME sniffing (not just extension trust), filename sanitization, automatic temp-file cleanup, execution isolation (never `eval`/`exec` on file content)
- Cloud deployment (Render/Fly.io for simplicity, or AWS ECS + RDS + S3 for a more "enterprise" story)
- Basic monitoring/logging (structured logs, request IDs, error tracking via Sentry)

**Milestone check:** a 2GB CSV completes analysis without OOM-killing the process, and the deployed instance survives a restart without losing existing users' data.

---

### Roadmap Summary Table

| Phase | Focus | Est. Time | Key Risk if Skipped |
|---|---|---|---|
| 1 | Core EDA | 2 wks | No working product to iterate on |
| 2 | Advanced analytics | 2–3 wks | Project looks like a `describe()` wrapper |
| 3 | Target intelligence | 1.5–2 wks | No ML-relevance story |
| 4 | Insight engine | 1–1.5 wks | No differentiation from existing EDA libraries |
| 5 | Productionization | 2–3 wks | Can't demo to real users or on real infra |
| 6 | Scale & deploy | 1.5–2 wks | Breaks on any dataset bigger than a toy example |

**Total: ~11–15 weeks part-time.** Phases 1–4 alone (≈7–9 weeks) already produce a strong, demoable portfolio artifact; treat Phases 5–6 as the difference between "project" and "product."

---

## 5. Feature Implementation Guide

Concrete calculation + visualization + integration notes for each required report section.

### 5.1 Dataset Overview
- **Calculate:** `df.shape`, `df.dtypes`, `df.memory_usage(deep=True).sum()`, per-column `nunique()`, sample value.
- **Infer types beyond pandas dtypes:** flag a numeric column as ID-like if `nunique() / len(df) > 0.95`; flag as constant if `nunique() == 1`; flag boolean-like integer columns (only 0/1).
- **Visualize:** summary cards (rows/columns/memory/missing%) + a schema table.
- **Integrate:** this runs first and its output (`feature_types` dict) is passed into every subsequent service so they don't each re-infer types.

### 5.2 Missing Values
- **Calculate:** `df.isnull().sum()`, percentage, and — the differentiator — missingness correlation: build a boolean "is-missing" matrix and correlate it against other columns to detect systematic (not random) missingness.
- **Visualize:** horizontal bar chart sorted descending by missing %.
- **Integrate:** feed the missingness-correlation result directly into the Insight Engine as a "structural missingness" finding.

### 5.3 Duplicates
- **Calculate:** `df.duplicated().sum()`, rate = duplicates / total rows.
- **Visualize:** simple stat cards; provide a "view duplicate samples" table endpoint (paginated, don't load all duplicates into one response).
- **Integrate:** offer a `/download-deduplicated` endpoint that returns `df.drop_duplicates()` as a new CSV — a genuinely useful feature, not just a report line.

### 5.4 Distributions
- **Calculate:** for each numeric column — mean, median, std, min/max, Q1/Q3, IQR, skewness (`scipy.stats.skew`), kurtosis (`scipy.stats.kurtosis`).
- **Visualize:** histogram (compute bins server-side with `numpy.histogram`, send bin edges + counts to frontend rather than raw data — keeps payloads small and avoids shipping full columns over the wire).
- **Integrate:** skewness > 1 (or < -1) triggers a recommendation (log1p/Box-Cox/RobustScaler) in the Insight Engine — clearly labeled as a suggestion, never auto-applied.

### 5.5 Outliers
- **Calculate:** run all three methods per numeric column:
  - IQR: flag values outside `[Q1 - 1.5*IQR, Q3 + 1.5*IQR]`
  - Z-score: flag `|z| > 3`
  - IsolationForest (`sklearn.ensemble.IsolationForest`) for multivariate anomalies across all numeric columns jointly
- **Combine:** report each method's count and a simple agreement heuristic ("high confidence" if ≥2 methods agree on a large fraction of the same rows).
- **Visualize:** table of outlier counts/percentages per column; optionally a scatter plot with outliers highlighted for the top 1–2 flagged columns.
- **Integrate:** never auto-remove outliers; only flag and let the user export flagged rows for review.

### 5.6 Correlations
- **Calculate:** `df.corr()` (Pearson) for numeric columns; consider adding Spearman for non-linear monotonic relationships as a Phase 2 stretch.
- **Extract:** programmatically pull pairs above a threshold (e.g. |r| > 0.6) into a ranked list — this is what feeds the Insight Engine, not the raw matrix.
- **Visualize:** heatmap (Plotly handles this well natively) plus a ranked list of top correlated pairs.
- **Integrate:** always render the "correlation does not imply causation" caveat next to this section — both a statistical best practice and a nice interview talking point about responsible reporting.

### 5.7 Categorical Analysis
- **Calculate:** `value_counts(normalize=True)` per categorical column; cardinality = `nunique()`.
- **High-cardinality handling:** if `nunique() > threshold` (e.g. 50), show only top 10 categories + "Other" bucket to avoid unusable charts.
- **Visualize:** bar charts for low-cardinality columns; a flagged warning card for high-cardinality ones.
- **Integrate:** high-cardinality columns get flagged as "consider target encoding / hashing / grouping" in the Insight Engine's ML-prep recommendations.

### 5.8 Target Analysis
- **Detect target type:** dtype + unique-value-count heuristics — `nunique() <= ~10` and non-numeric or low-cardinality integer → classification; continuous float with high cardinality → regression.
- **Classification path:** class distribution, imbalance ratio (`majority_count / minority_count`), suggested mitigations (stratified split, class weights, SMOTE) — presented as options, not automatically applied.
- **Regression path:** target distribution stats (reuse `distributions.py` logic), skewness check on the target itself.
- **Cross-analysis:** grouped means/medians of numeric features by target class (classification) or correlation of numeric features with target (regression); category-wise rate tables for categorical features vs. classification target.
- **Visualize:** boxplots/violin plots (numeric vs. target), grouped bar charts (categorical vs. target).
- **Integrate:** this is the last analysis stage — it consumes outputs from correlations, categorical, and distributions modules rather than recomputing from scratch.

---

## 6. Testing, Documentation & Deployment Considerations

**Testing priorities (in order of ROI):**
1. Service-layer unit tests with deliberately ugly fixtures: empty dataframe, all-null column, constant column, single row, mixed-type column, 100%-missing column, duplicate column names.
2. API-level integration tests for the upload → analyze → report round trip.
3. Frontend component tests for chart rendering with edge-case data (empty series, single data point).

**Documentation:**
- README with architecture diagram, setup instructions, and a GIF/screenshot of the dashboard (screenshots do more for portfolio credibility than paragraphs).
- API docs are free via FastAPI's auto-generated OpenAPI/Swagger — link to it prominently.
- A short `docs/insight-rules.md` explaining every rule in the Insight Engine in plain language — this doubles as a design document that's easy to walk through in an interview.

**Deployment:**
- Start with a single Docker Compose stack (FastAPI + Postgres + Redis + frontend build) on a low-cost host (Render, Fly.io, Railway).
- Add a `/health` endpoint and basic uptime monitoring before calling it "deployed."
- Set explicit resource limits (max upload size, max processing time) so one bad file can't take the service down — this is worth calling out explicitly as a security/reliability consideration in any writeup.

---

## 7. Resume-Ready Project Summary

> **EDA Autopilot — Automated Dataset Intelligence Platform.** Built a full-stack application (React/TypeScript, FastAPI, PostgreSQL) that ingests raw CSV data and automatically profiles data quality, detects statistical anomalies (missingness patterns, skewness, multi-method outlier detection via IQR/Z-score/Isolation Forest), computes feature correlations, and performs target-aware analysis including automatic classification/regression detection and class-imbalance diagnosis. Implemented a rule-based insight and recommendation engine that translates raw statistics into prioritized, human-readable findings, alongside a transparent data-quality scoring system. The project demonstrates end-to-end ownership across data science (statistical methods, feature engineering heuristics) and software engineering (modular service architecture, REST API design, containerized deployment, automated test coverage on adversarial datasets) — spanning the full lifecycle from raw data to a stakeholder-ready report.

---

## Immediate Next Steps

1. Scaffold the repo structure from §3.1.
2. Stand up FastAPI with a single `/upload` endpoint that validates and stores a file — get the CI pipeline running against this trivial baseline immediately, before any analysis logic exists.
3. Build `profiler.py` and its unit tests first; every other service depends on its output contract.
4. Build the frontend against a hardcoded/mocked JSON response before the real backend is finished — this parallelizes frontend and backend work and forces you to nail the API contract early.
