import time
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from ..utils.storage import storage
from ..services.profiler import profile_dataset
from ..services.missing import analyze_missingness
from ..services.duplicates import analyze_duplicates
from ..services.distributions import analyze_distributions
from ..services.outliers import analyze_outliers
from ..services.correlations import analyze_correlations
from ..services.categorical import analyze_categorical
from ..services.target import analyze_target
from ..services.insights import generate_insights_and_quality

router = APIRouter(tags=["Analysis"])

class AnalyzeRequest(BaseModel):
    dataset_id: str
    target_column: Optional[str] = None
    correlation_threshold: float = 0.5

@router.post("/analyze")
async def analyze_dataset_endpoint(payload: AnalyzeRequest):
    start_time = time.time()

    df = storage.get_dataframe(payload.dataset_id)
    if df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID '{payload.dataset_id}' not found. Please upload or select a valid dataset."
        )

    meta = storage.get_metadata(payload.dataset_id) or {}
    filename = meta.get("filename", "dataset.csv")

    warnings = []

    # 1. Profile
    profile = profile_dataset(df)

    # 2. Missingness
    missing = analyze_missingness(df)

    # 3. Duplicates
    duplicates = analyze_duplicates(df)

    # 4. Distributions
    distributions = analyze_distributions(df, numeric_columns=profile["numeric_columns"])

    # 5. Outliers
    outliers = analyze_outliers(df, numeric_columns=profile["numeric_columns"])

    # 6. Correlations
    correlations = analyze_correlations(df, numeric_columns=profile["numeric_columns"], threshold=payload.correlation_threshold)

    # 7. Categorical
    categorical = analyze_categorical(df, categorical_columns=profile["categorical_columns"])

    # 8. Target Intelligence (if requested or auto-guess if present)
    target_result = None
    if payload.target_column and payload.target_column in df.columns:
        try:
            target_result = analyze_target(df, payload.target_column)
        except Exception as e:
            warnings.append(f"Target analysis failed: {str(e)}")

    # 9. Rule-based Insight Engine + Data Quality Score
    insights = generate_insights_and_quality(
        profiler_data=profile,
        missing_data=missing,
        duplicates_data=duplicates,
        distributions_data=distributions,
        outliers_data=outliers,
        correlations_data=correlations,
        categorical_data=categorical,
        target_data=target_result
    )

    duration_ms = round((time.time() - start_time) * 1000, 2)

    report_data = {
        "dataset_id": payload.dataset_id,
        "filename": filename,
        "profiler": profile,
        "missing": missing,
        "duplicates": duplicates,
        "distributions": distributions,
        "outliers": outliers,
        "correlations": correlations,
        "categorical": categorical,
        "insights": insights,
        "target": target_result
    }

    return {
        "status": "ok",
        "data": report_data,
        "warnings": warnings,
        "meta": {
            "computed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "duration_ms": duration_ms,
            "rows": len(df),
            "columns": len(df.columns)
        }
    }
