from sqlalchemy.orm import Session
from app.models.student_answer import StudentAnswer
from app.models.question import DifficultyLevel
import logging

logger = logging.getLogger(__name__)

def update_student_difficulty(db: Session, student_id: str, current_difficulty: DifficultyLevel) -> str:
    """
    Evaluates the last 3 answers for the student.
    - If all 3 correct -> increase difficulty (if possible)
    - If all 3 incorrect -> decrease difficulty (if possible)
    - Else keep the same.
    Returns the next difficulty level as a string.
    """
    recent_answers = db.query(StudentAnswer).filter(
        StudentAnswer.student_id == student_id
    ).order_by(StudentAnswer.created_at.desc()).limit(2).all()

    if len(recent_answers) < 2:
        # Not enough data to adapt
        return current_difficulty.value

    all_correct = all(ans.is_correct for ans in recent_answers)
    all_incorrect = all(not ans.is_correct for ans in recent_answers)

    next_diff = current_difficulty

    if all_correct:
        if current_difficulty == DifficultyLevel.EASY:
            next_diff = DifficultyLevel.MEDIUM
        elif current_difficulty == DifficultyLevel.MEDIUM:
            next_diff = DifficultyLevel.HARD
        elif current_difficulty == DifficultyLevel.HARD:
            next_diff = DifficultyLevel.HARD # Already max
        logger.info(f"Student {student_id} got 3 correct in a row. Increasing difficulty to {next_diff.value}.")
            
    elif all_incorrect:
        if current_difficulty == DifficultyLevel.HARD:
            next_diff = DifficultyLevel.MEDIUM
        elif current_difficulty == DifficultyLevel.MEDIUM:
            next_diff = DifficultyLevel.EASY
        elif current_difficulty == DifficultyLevel.EASY:
            next_diff = DifficultyLevel.EASY # Already min
        logger.info(f"Student {student_id} got 3 incorrect in a row. Decreasing difficulty to {next_diff.value}.")

    return next_diff.value
