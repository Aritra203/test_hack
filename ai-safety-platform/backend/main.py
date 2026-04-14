from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.cloudinary_config import init_cloudinary
from backend.config.database import db_manager
from backend.config.settings import settings
from backend.routes.analysis import router as analysis_router
from backend.routes.analytics import router as analytics_router
from backend.routes.fir import router as fir_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_cloudinary()
    await db_manager.connect()
    yield
    await db_manager.disconnect()


app = FastAPI(
    title=settings.project_name,
    version=settings.api_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)
app.include_router(fir_router)
app.include_router(analytics_router)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": settings.project_name, "version": settings.api_version}

