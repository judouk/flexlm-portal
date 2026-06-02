from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    role = Column(String, nullable=False, default="user")

    active = Column(Boolean, default=True)
