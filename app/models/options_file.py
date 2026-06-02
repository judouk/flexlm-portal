from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.db import Base


class OptionsFile(Base):
    __tablename__ = "options_files"

    id = Column(Integer, primary_key=True, index=True)

    server_id = Column(
        Integer,
        ForeignKey("license_servers.id"),
        nullable=False,
    )

    filename = Column(String, nullable=False)

    storage_path = Column(String)

    content = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    content_backend = Column(String)
    content_ref = Column(String)
    content_path = Column(String)

    published_at = Column(DateTime)
    publish_status = Column(String)
    publish_message = Column(String)
