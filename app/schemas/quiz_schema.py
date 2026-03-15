from pydantic import BaseModel
from typing import List

class GenerateQuizRequest(BaseModel):
    source_id: str

class GenerateQuizResponse(BaseModel):
    questions_generated: int

class QuestionResponse(BaseModel):
    question_id: str
    question: str
    options: List[str] | None
    type: str
    difficulty: str
    topic: str | None = None
