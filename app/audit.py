import json

from app.models.audit_event import AuditEvent


def write_audit_event(
    db,
    actor,
    action,
    object_type=None,
    object_id=None,
    details=None,
):

    event = AuditEvent(
        actor=actor,
        action=action,
        object_type=object_type,
        object_id=str(object_id) if object_id else None,
        details=json.dumps(details) if details else None,
    )

    db.add(event)
