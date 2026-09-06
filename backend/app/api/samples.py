from fastapi import APIRouter, HTTPException, status
from ..utils.storage import storage

router = APIRouter(tags=["Sample Datasets"])

@router.get("/sample-datasets")
async def get_sample_datasets():
    samples = storage.list_samples()
    return {
        "status": "ok",
        "data": samples,
        "warnings": [],
        "meta": {"count": len(samples)}
    }

@router.get("/sample-datasets/{dataset_id}")
async def get_sample_dataset_info(dataset_id: str):
    df = storage.get_dataframe(dataset_id)
    if df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample dataset '{dataset_id}' not found."
        )
    meta = storage.get_metadata(dataset_id)
    return {
        "status": "ok",
        "data": {
            "metadata": meta,
            "preview_rows": df.head(5).to_dict(orient="records"),
            "columns": list(df.columns)
        }
    }
