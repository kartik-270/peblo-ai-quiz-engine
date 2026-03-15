import json
import logging
import requests
from typing import List, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Hugging Face OpenAI-compatible API URL
API_URL = "https://router.huggingface.co/v1/chat/completions"

def generate_quiz_questions(text: str, target_difficulty: str = "medium", max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Calls Hugging Face Inference API (OpenAI compatible) to generate quiz questions.
    Requires a valid HF_TOKEN in settings.
    """
    headers = {
        "Authorization": f"Bearer {settings.HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Generate exactly 3 quiz questions from the following educational content.
    Target difficulty: {target_difficulty}
    Required question types: MCQ, TRUE_FALSE, FILL_BLANK.
    
    IMPORTANT CONTEXT:
    This content is for young children (e.g., Grade 1-4). 
    Difficulty levels (easy, medium, hard) MUST be RELATIVE to this age group.
    - "Hard" should mean "challenging for a child at this grade level" (e.g., multi-step, requiring more thought).
    - Do NOT skip generating "Hard" questions just because the subject is simple.
    
    Rules:
    - Questions must match the content.
    - Set difficulty to exactly "{target_difficulty}".
    - Provide the correct answer.
    
    Content:
    {text}
    
    Return strict JSON ONLY as an object containing a "questions" key with an array of objects.
    Example format:
    {{
      "questions": [
        {{
          "question": "Question text here",
          "type": "MCQ", 
          "options": ["A", "B", "C", "D"], 
          "answer": "Correct A",
          "difficulty": "{target_difficulty}"
        }}
      ]
    }}"""

    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.1
    }

    for attempt in range(max_retries):
        try:
            logger.info(f"Hugging Face API Attempt {attempt + 1}...")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"HF API Error: {response.status_code} - {response.text}")
                continue

            result = response.json()
            # result is OpenAI format
            content = result['choices'][0]['message']['content'].strip()

            logger.info("HF response received.")
            
            # Clean possible markdown formatting
            clean_content = content.replace("```json", "").replace("```", "").strip()
            
            try:
                data = json.loads(clean_content)
            except json.JSONDecodeError:
                # Attempt to find JSON block in text
                start = clean_content.find('{')
                end = clean_content.rfind('}') + 1
                if start != -1 and end != 0:
                    data = json.loads(clean_content[start:end])
                else:
                    raise ValueError("No valid JSON found in HF response.")

            if isinstance(data, dict):
                if "questions" in data:
                    data = data["questions"]
                else:
                    for key, value in data.items():
                        if isinstance(value, list):
                            data = value
                            break

            if not isinstance(data, list):
                raise ValueError("HF did not return a JSON array of questions.")

            # Validation
            validated_questions = []
            for item in data:
                q_text = item.get("question") or item.get("text") or ""
                if q_text:
                    validated_questions.append({
                        "question": q_text,
                        "type": str(item.get("type", "MCQ")).upper(),
                        "options": item.get("options", []),
                        "answer": str(item.get("answer", "") or item.get("correct_answer", "")),
                        "difficulty": str(item.get("difficulty", "medium")).lower()
                    })

            return validated_questions

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} error with HF: {str(e)}")
            if attempt == max_retries - 1:
                return []
    
    return []
