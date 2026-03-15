from pydantic import BaseModel
from typing import List

class IngestRequest(BaseModel):
    subject: str | None = None
    grade: int | None = None

class IngestResponse(BaseModel):
    source_id: str
    chunks_created: int
