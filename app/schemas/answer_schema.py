from pydantic import BaseModel

class StudentAnswerRequest(BaseModel):
    student_id: str
    question_id: str
    selected_answer: str

class StudentAnswerResponse(BaseModel):
    correct: bool
    next_difficulty: str
