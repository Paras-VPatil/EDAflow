from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import APP_NAME, APP_VERSION
from .api import (
    upload_router,
    analysis_router,
    target_router,
    samples_router,
    export_router
)

app = FastAPI(
    title=f"{APP_NAME} — Automated Dataset Intelligence Platform API",
    version=APP_VERSION,
    description="High-performance backend engine for automated profiling, statistical analysis, multi-method anomaly detection, target intelligence, and insight generation."
)

# Enable CORS for local Vite dev and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(upload_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(target_router, prefix="/api")
app.include_router(samples_router, prefix="/api")
app.include_router(export_router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": APP_NAME,
        "version": APP_VERSION,
        "message": "EDAflow engine is operational and ready to process datasets."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
