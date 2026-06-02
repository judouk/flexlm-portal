from fastapi import APIRouter
from fastapi import Depends

from app.audit import write_audit_event
from app.auth.dependencies import require_manager
from app.db import SessionLocal
from app.services.content_publish_service import publish_content


router = APIRouter()


@router.post("/content/publish")
def publish(
    user=Depends(require_manager),
):

    db = SessionLocal()

    result = publish_content(db)

    write_audit_event(
        db,
        actor=user["sub"],
        action="content.published",
        object_type="content_backend",
        object_id=result.get("backend"),
        details=result,
    )

    db.commit()
    db.close()

    return result
