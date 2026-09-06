import time
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from ..config import MAX_UPLOAD_SIZE_BYTES, ALLOWED_EXTENSIONS
from ..utils.storage import storage
from ..services.profiler import profile_dataset

router = APIRouter(tags=["Upload"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    start_time = time.time()
    
    filename = file.filename or "uploaded_dataset.csv"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Read content with size check
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_UPLOAD_SIZE_BYTES / (1024*1024):.0f} MB."
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )

    try:
        df, dataset_id = storage.parse_file(content, filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse file: {str(e)}"
        )

    # Run initial dataset profile
    profile = profile_dataset(df)
    meta_info = storage.get_metadata(dataset_id)

    duration_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": "ok",
        "data": {
            "dataset_id": dataset_id,
            "filename": filename,
            "rows": len(df),
            "columns": len(df.columns),
            "profile": profile,
            "metadata": meta_info
        },
        "warnings": [],
        "meta": {
            "duration_ms": duration_ms
        }
    }
