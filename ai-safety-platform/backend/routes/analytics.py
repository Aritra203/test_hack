from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from backend.config.database import db_manager
from backend.models.schemas import AnalyticsResponse


router = APIRouter(tags=["analytics"])


@router.get("/analytics", response_model=AnalyticsResponse)
async def analytics() -> AnalyticsResponse:
    db = db_manager.get_database()
    total = await db["analyses"].count_documents({})

    risk_pipeline = [
        {"$group": {"_id": "$result.risk_level", "count": {"$sum": 1}}},
    ]
    label_pipeline = [
        {"$unwind": "$result.labels"},
        {"$group": {"_id": "$result.labels.label", "count": {"$sum": 1}}},
    ]

    risk_rows = await db["analyses"].aggregate(risk_pipeline).to_list(length=100)
    label_rows = await db["analyses"].aggregate(label_pipeline).to_list(length=100)

    since = datetime.now(timezone.utc) - timedelta(days=7)
    recent = await db["analyses"].count_documents({"created_at": {"$gte": since}})

    return AnalyticsResponse(
        total_analyses=total,
        by_risk={row["_id"] or "UNKNOWN": int(row["count"]) for row in risk_rows},
        by_label={row["_id"] or "unknown": int(row["count"]) for row in label_rows},
        recent_incidents=recent,
    )

