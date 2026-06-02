from fastapi import APIRouter
from fastapi import Depends

from app.auth.dependencies import require_admin
from app.db import SessionLocal
from app.models.audit_event import AuditEvent


router = APIRouter()


@router.get("/audit-events")
def list_audit_events(
    admin=Depends(require_admin),
):
    db = SessionLocal()

    events = db.query(AuditEvent).order_by(
        AuditEvent.created_at.desc()
    ).limit(100).all()

    response = [
        {
            "id": event.id,
            "actor": event.actor,
            "action": event.action,
            "object_type": event.object_type,
            "object_id": event.object_id,
            "details": event.details,
            "created_at": event.created_at,
        }
        for event in events
    ]

    db.close()

    return response
