import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    FLOAT,
    ForeignKey,
    JSON,
    String,
    UUID,
)

from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True)
    username = Column(String(50), unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    hashed_password = Column(String)
    is_admin = Column(Boolean)


class Receipts(Base):
    __tablename__ = "receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    products = Column(JSON)
    payment = Column(JSON)
    total = Column(FLOAT)
    rest = Column(FLOAT)
    created_at = Column(DateTime, default=datetime.utcnow())
    owner_id = Column(Integer, ForeignKey("users.id"))
