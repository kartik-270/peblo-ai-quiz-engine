import re

def clean_extracted_text(text: str) -> str:
    """
    Cleans raw text extracted from PDF.
    - Removes extra whitespace
    - Removes isolated numbers (like page numbers)
    - Joins broken lines
    """
    if not text:
        return ""

    # Replace newlines with spaces to join broken lines
    text = text.replace("\n", " ")
    
    # Remove isolated numbers (often page numbers at the bottom/top)
    text = re.sub(r'\b\d+\b(?![\w\-\.])', '', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()
