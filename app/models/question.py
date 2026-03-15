import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Enum
import enum
from app.core.database import Base

class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    TRUE_FALSE = "TRUE_FALSE"
    FILL_BLANK = "FILL_BLANK"

class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String, unique=True, index=True, default=lambda: f"Q_{uuid.uuid4().hex[:8].upper()}")
    question_text = Column(String, nullable=False)
    type = Column(Enum(QuestionType), nullable=False)
    options = Column(JSON, nullable=True) # JSON list of options for MCQ, else null or empty
    correct_answer = Column(String, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    source_chunk_id = Column(String, ForeignKey("content_chunks.chunk_id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
