from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base

class LicenseServer(Base):
    __tablename__ = "license_servers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    hostname = Column(String, nullable=False)
    hostid = Column(String, nullable=False)

    lmgrd_port = Column(Integer)

    daemons = relationship(
        "LicenseDaemon",
        back_populates="server",
        cascade="all, delete-orphan",
    )

    merge_policy = Column(
        String,
        nullable=False,
        default="additive",
    )
