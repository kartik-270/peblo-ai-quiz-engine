from typing import List

def chunk_text(text: str, target_word_count: int = 400) -> List[str]:
    """
    Splits text into chunks of approximately `target_word_count` words.
    Prefers splitting on sentence boundaries ('. ', '! ', '? ') when near the target size.
    """
    if not text:
        return []

    words = text.split()
    chunks = []
    current_chunk_words = []
    
    for word in words:
        current_chunk_words.append(word)
        
        # Check if we have reached the target word count
        if len(current_chunk_words) >= target_word_count:
            # Try to push to the next sentence boundary to avoid cutting mid-sentence
            if word.endswith('.') or word.endswith('!') or word.endswith('?'):
                chunks.append(" ".join(current_chunk_words))
                current_chunk_words = []
                
    # Add any remaining words as a final chunk
    if current_chunk_words:
        chunks.append(" ".join(current_chunk_words))
        
    return chunks
