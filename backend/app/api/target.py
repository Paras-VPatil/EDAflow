import time
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from ..utils.storage import storage
from ..services.target import analyze_target

router = APIRouter(tags=["Target Intelligence"])

class TargetRequest(BaseModel):
    dataset_id: str
    target_column: str

@router.post("/target-analysis")
async def run_target_analysis(payload: TargetRequest):
    start_time = time.time()

    df = storage.get_dataframe(payload.dataset_id)
    if df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{payload.dataset_id}' not found."
        )

    if payload.target_column not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Column '{payload.target_column}' does not exist in dataset."
        )

    try:
        result = analyze_target(df, payload.target_column)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Target analysis failed: {str(e)}"
        )

    duration_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": "ok",
        "data": result,
        "warnings": [],
        "meta": {
            "duration_ms": duration_ms
        }
    }
