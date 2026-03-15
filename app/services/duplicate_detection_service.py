import logging
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

# Initialize model (downloads on first run)
try:
    logger.info("Loading sentence-transformers model (this might take a while on first run)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Sentence-transformers model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load sentence-transformers model: {e}")
    model = None

def is_duplicate_question(new_question_text: str, existing_questions: list[str], threshold: float = 0.9) -> bool:
    """
    Checks if `new_question_text` is too similar to any strings in `existing_questions`.
    Uses cosine similarity of sentence embeddings.
    Returns True if similarity > threshold.
    """
    if not model or not existing_questions:
        return False

    try:
        new_embedding = model.encode(new_question_text, convert_to_tensor=True)
        existing_embeddings = model.encode(existing_questions, convert_to_tensor=True)
        
        # Compute cosine similarities
        cosine_scores = util.cos_sim(new_embedding, existing_embeddings)[0]
        
        # Check if any score exceeds the threshold
        if max(cosine_scores).item() > threshold:
            logger.info(f"Duplicate detected! Score: {max(cosine_scores).item()}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error during duplicate detection: {e}")
        return False
