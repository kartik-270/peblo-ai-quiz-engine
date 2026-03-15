import fitz # PyMuPDF
from fastapi import UploadFile

def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Reads an uploaded PDF file and extracts raw text using PyMuPDF.
    """
    try:
        pdf_bytes = file.file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        full_text = []
        for page in doc:
            text = page.get_text()
            full_text.append(text)
            
        return "\n".join(full_text)
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
    finally:
        file.file.seek(0) # Reset file pointer for future reads if necessary
