import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class ContentChunk(Base):
    __tablename__ = "content_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String, unique=True, index=True, default=lambda: f"CH_{uuid.uuid4().hex[:8].upper()}")
    source_id = Column(String, ForeignKey("source_documents.source_id"), index=True)
    topic = Column(String, index=True, nullable=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships can be added if needed
    # source = relationship("SourceDocument", back_populates="chunks")
