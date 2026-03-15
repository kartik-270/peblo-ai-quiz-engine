from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.question import Question, DifficultyLevel
from app.schemas.quiz_schema import GenerateQuizRequest, GenerateQuizResponse, QuestionResponse
from app.services.quiz_generation_service import generate_questions_for_source
import logging

router = APIRouter(prefix="/quiz", tags=["Quiz"])
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=GenerateQuizResponse)
async def generate_quiz(
    request: GenerateQuizRequest,
    db: Session = Depends(get_db)
):
    """
    Triggers the generation of quiz questions from chunks associated with a source_id.
    """
    logger.info(f"Triggering quiz generation for source_id: {request.source_id}")
    count = generate_questions_for_source(db, request.source_id)
    return GenerateQuizResponse(questions_generated=count)

@router.get("/", response_model=List[QuestionResponse])
async def get_quiz(
    topic: str = Query(None),
    difficulty: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Fetches questions based on topic and difficulty.
    """
    query = db.query(Question)
    
    if topic:
        from app.models.chunk import ContentChunk
        # Case-insensitive topic matching using ILIKE
        query = query.join(ContentChunk, Question.source_chunk_id == ContentChunk.chunk_id).filter(ContentChunk.topic.ilike(f"%{topic}%"))

    if difficulty:
        try:
            # Map input to enum safely (case-insensitive)
            diff_enum = DifficultyLevel(difficulty.lower())
            query = query.filter(Question.difficulty == diff_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid difficulty level '{difficulty}'. Use easy, medium, or hard.")

    questions = query.all()
    
    # Auto-generate if no questions exist for this topic (Synchronous)
    if not questions and topic:
        logger.info(f"No questions found for topic '{topic}'. Attempting synchronous auto-generation...")
        from app.models.chunk import ContentChunk
        # Find any chunk for this topic to use as source
        chunk = db.query(ContentChunk).filter(ContentChunk.topic.ilike(f"%{topic}%")).first()
        if chunk:
            from app.services.quiz_generation_service import generate_questions_for_source
            generate_questions_for_source(db, chunk.source_id, target_difficulty=difficulty or "medium")
            # Re-query
            questions = query.all()
    
    return [
        QuestionResponse(
            question_id=q.question_id,
            question=q.question_text,
            options=q.options,
            type=q.type.value,
            difficulty=q.difficulty.value,
            topic=topic or "General"
        ) for q in questions
    ]
