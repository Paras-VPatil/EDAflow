import time
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from ..utils.storage import storage
from ..services.timeseries import analyze_timeseries

router = APIRouter(tags=["Time Series"])

class TimeseriesRequest(BaseModel):
    dataset_id: str
    datetime_column: Optional[str] = None

@router.post("/timeseries-analysis")
async def run_timeseries_analysis(payload: TimeseriesRequest):
    start_time = time.time()

    df = storage.get_dataframe(payload.dataset_id)
    if df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{payload.dataset_id}' not found."
        )

    try:
        report = analyze_timeseries(df, payload.datetime_column)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Time-series analysis failed: {str(e)}"
        )

    duration_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": "ok",
        "data": report,
        "warnings": [],
        "meta": {
            "duration_ms": duration_ms
        }
    }
