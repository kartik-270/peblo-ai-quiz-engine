import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base

class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, unique=True, index=True, default=lambda: f"SRC_{uuid.uuid4().hex[:8].upper()}")
    subject = Column(String, index=True, nullable=True)
    grade = Column(Integer, index=True, nullable=True)
    filename = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
