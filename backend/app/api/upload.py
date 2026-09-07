import time
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from ..config import MAX_UPLOAD_SIZE_BYTES, ALLOWED_EXTENSIONS
from ..utils.storage import storage, sanitize_filename
from ..services.profiler import profile_dataset

router = APIRouter(tags=["Upload"])

@router.post("/excel-sheets")
async def get_excel_sheets(file: UploadFile = File(...)):
    """Inspect sheet names in an uploaded Excel workbook."""
    filename = file.filename or "workbook.xlsx"
    ext = Path(filename).suffix.lower()
    if ext not in [".xlsx", ".xls"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel spreadsheet (.xlsx, .xls)."
        )
    content = await file.read()
    sheets = storage.inspect_excel_sheets(content)
    return {"filename": sanitize_filename(filename), "sheets": sheets}

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(None)
):
    start_time = time.time()
    
    raw_filename = file.filename or "uploaded_dataset.csv"
    ext = Path(raw_filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

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
        df, dataset_id, parse_warnings = storage.parse_file(content, raw_filename, sheet_name=sheet_name)
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
            "filename": meta_info.get("filename", raw_filename),
            "rows": len(df),
            "columns": len(df.columns),
            "is_sampled": meta_info.get("is_sampled", False),
            "original_rows": meta_info.get("original_rows", len(df)),
            "sample_rate": meta_info.get("sample_rate", 1.0),
            "profile": profile,
            "metadata": meta_info
        },
        "warnings": parse_warnings,
        "meta": {
            "duration_ms": duration_ms
        }
    }
