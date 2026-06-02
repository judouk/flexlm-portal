from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base

class LicenseDaemon(Base):
    __tablename__ = "license_daemons"

    id = Column(Integer, primary_key=True, index=True)

    server_id = Column(
        Integer,
        ForeignKey("license_servers.id"),
        nullable=False,
    )

    name = Column(String, nullable=False)
    daemon_path = Column(String)
    options_file_path = Column(String)
    port = Column(Integer)

    server = relationship(
        "LicenseServer",
        back_populates="daemons"
    )
