import time
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from ..utils.storage import storage
from ..services.drift import compare_datasets

router = APIRouter(tags=["Dataset Drift & Comparison"])

class DriftRequest(BaseModel):
    baseline_dataset_id: str
    comparison_dataset_id: str

@router.post("/drift-analysis")
async def run_drift_analysis(payload: DriftRequest):
    start_time = time.time()

    df_base = storage.get_dataframe(payload.baseline_dataset_id)
    if df_base is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Baseline dataset '{payload.baseline_dataset_id}' not found."
        )

    df_comp = storage.get_dataframe(payload.comparison_dataset_id)
    if df_comp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison dataset '{payload.comparison_dataset_id}' not found."
        )

    try:
        drift_report = compare_datasets(df_base, df_comp)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Drift analysis failed: {str(e)}"
        )

    duration_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": "ok",
        "data": drift_report,
        "warnings": [],
        "meta": {
            "duration_ms": duration_ms
        }
    }
