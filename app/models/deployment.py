from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db import Base


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)

    server_id = Column(
        Integer,
        ForeignKey("license_servers.id"),
        nullable=False,
    )

    artifact_path = Column(String, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="generated",
    )

    generated_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    content_backend = Column(String)
    content_ref = Column(String)
    content_path = Column(String)

    published_at = Column(DateTime)
    publish_status = Column(String)
    publish_message = Column(String)
