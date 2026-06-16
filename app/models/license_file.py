from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base

class LicenseFile(Base):
    __tablename__ = "license_files"

    id = Column(Integer, primary_key=True, index=True)

    server_id = Column(
        Integer,
        ForeignKey("license_servers.id"),
        nullable=True,
    )

    filename = Column(String, nullable=False)

    vendor = Column(String)

    server_hostname = Column(String)
    server_hostid = Column(String)

    storage_path = Column(String)

    imported_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    content_backend = Column(String)
    content_ref = Column(String)
    content_path = Column(String)

    published_at = Column(DateTime)
    publish_status = Column(String)
    publish_message = Column(String)

    deleted_at = Column(DateTime)
    deleted_by = Column(String)

    features = relationship(
        "Feature",
        back_populates="license_file",
        cascade="all, delete-orphan",
    )

    matching_warning = Column(String)


class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)

    license_file_id = Column(
        Integer,
        ForeignKey("license_files.id"),
    )

    name = Column(String)
    vendor = Column(String)
    version = Column(String)
    expiry = Column(String)
    count = Column(String)

    license_file = relationship(
        "LicenseFile",
        back_populates="features",
    )
