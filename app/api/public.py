from datetime import datetime

from fastapi import APIRouter

from app.db import SessionLocal
from app.services.license_summary_service import get_public_license_summary


router = APIRouter()


@router.get("/public/license-summary")
def public_license_summary():
    db = SessionLocal()

    try:
        items = get_public_license_summary(db)
    finally:
        db.close()

    return {
        "generated_at": datetime.utcnow(),
        "items": items,
    }
