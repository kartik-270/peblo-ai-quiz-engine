import logging
from sqlalchemy.orm import Session
from typing import List

from app.models.chunk import ContentChunk
from app.models.question import Question, QuestionType, DifficultyLevel
from app.services.llm_service import generate_quiz_questions
from app.services.duplicate_detection_service import is_duplicate_question

logger = logging.getLogger(__name__)

def generate_questions_for_source(db: Session, source_id: str, target_difficulty: str = "medium") -> int:
    """
    Fetch all chunks for a given source, generate questions via LLM,
    filter out duplicates, and store them in the database.
    Returns the number of generated questions.
    """
    chunks = db.query(ContentChunk).filter(ContentChunk.source_id == source_id).all()
    if not chunks:
        logger.warning(f"No chunks found for source {source_id}.")
        return 0

    # Retrieve all existing question texts from the DB for duplicate checking
    # (In a huge DB, we'd limit this to recent or relevant questions)
    existing_questions_query = db.query(Question.question_text).all()
    existing_questions = [q[0] for q in existing_questions_query]

    total_created = 0

    for chunk in chunks:
        logger.info(f"Generating questions for chunk {chunk.chunk_id}...")
        
        # Call LLM with target difficulty
        generated_list = generate_quiz_questions(chunk.text, target_difficulty=target_difficulty)
        
        for q_data in generated_list:
            question_text = q_data.get("question", "").strip()
            if not question_text:
                continue
                
            # Filter duplicates
            if is_duplicate_question(question_text, existing_questions):
                logger.info(f"Skipping duplicate question: {question_text}")
                continue

            # Map enums safely
            try:
                q_type = QuestionType(q_data.get("type", "MCQ").upper())
            except ValueError:
                q_type = QuestionType.MCQ
                
            # Force the requested difficulty to ensure strict adherence
            q_diff = DifficultyLevel(target_difficulty.lower())

            # Build model
            new_question = Question(
                question_text=question_text,
                type=q_type,
                options=q_data.get("options"),
                correct_answer=q_data.get("answer", ""),
                difficulty=q_diff,
                source_chunk_id=chunk.chunk_id
            )
            
            db.add(new_question)
            existing_questions.append(question_text) # add to in-memory list for next iterations
            total_created += 1

    db.commit()
    return total_created
