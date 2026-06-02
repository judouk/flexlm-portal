from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.db import Base

class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True)

    deployment_id = Column(
        Integer,
        ForeignKey("deployments.id"),
        nullable=False,
    )

    severity = Column(
        String,
        nullable=False,
    )

    code = Column(
        String,
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
