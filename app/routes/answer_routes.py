from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.question import Question
from app.models.student_answer import StudentAnswer
from app.schemas.answer_schema import StudentAnswerRequest, StudentAnswerResponse
from app.services.adaptive_service import update_student_difficulty
import logging

router = APIRouter(prefix="/submit-answer", tags=["Answer"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=StudentAnswerResponse)
async def submit_answer(
    request: StudentAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Submits a student's answer, checks correctness, and returns the next adaptive difficulty.
    """
    # 1. Fetch question
    question = db.query(Question).filter(Question.question_id == request.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    # 2. Check correctness
    is_correct = str(request.selected_answer).strip().lower() == str(question.correct_answer).strip().lower()
    
    # 3. Store answer
    new_answer = StudentAnswer(
        student_id=request.student_id,
        question_id=request.question_id,
        selected_answer=request.selected_answer,
        is_correct=is_correct
    )
    db.add(new_answer)
    db.commit() # Commit to ensure update_student_difficulty can see the latest answer

    # 4. Trigger Adaptive Engine
    next_diff = update_student_difficulty(db, request.student_id, question.difficulty)

    logger.info(f"Student {request.student_id} answered question {request.question_id}. Correct: {is_correct}. Next Difficulty: {next_diff}")

    return StudentAnswerResponse(
        correct=is_correct,
        next_difficulty=next_diff
    )
