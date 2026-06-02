from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from app.db import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)

    actor = Column(String)

    action = Column(String, nullable=False)

    object_type = Column(String)
    object_id = Column(String)

    details = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
