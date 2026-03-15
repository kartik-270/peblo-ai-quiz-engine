# Peblo AI Content Ingestion + Adaptive Quiz Engine

## Project Overview
This project is an AI-powered quiz generation platform. It ingests educational content from PDF files, processes the text into structured chunks, and utilizes LLMs (OpenAI) to generate interactive, traceable quiz questions. It includes an adaptive difficulty engine that updates recommendations based on student performance.

## Architecture & Design
The system follows a modular **FastAPI** architecture with a clear separation of concerns:
- **Core**: Configuration, database setup, and logging.
- **Models**: SQLAlchemy ORM definitions for Sources, Chunks, Questions, and Answers.
- **Routes**: RESTful API endpoints for ingestion, quiz management, and answer submission.
- **Services**: Business logic for PDF parsing, text cleaning, chunking, LLM orchestration, duplicate detection, and adaptive logic.

### Data Flow
1. **Ingest**: PDF -> Raw Text (PyMuPDF) -> Cleaned Text -> Chunks -> Database.
2. **Generate**: DB Chunks -> OpenAI GPT-4o -> Structured JSON Questions -> Duplicate Check (Sentence-Transformers) -> Database.
3. **Serve**: Filter questions by topic/difficulty -> API Response.
4. **Learn**: Student Answer -> Accuracy check -> Rule-based Adaptive Engine -> Next recommended difficulty.

## Tech Stack
- **Framework**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **AI**: OpenAI GPT-4o
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`) for duplicate detection.
- **PDF Parsing**: PyMuPDF
- **Validation**: Pydantic

## Setup Instructions

### Prerequisites
- Python 3.11+
- OpenAI API Key

### Installation

1. **Clone the repository** (or navigate to the project directory).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**:
   Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   Add your `OPENAI_API_KEY` to the `.env` file.

### Running the Backend
```bash
uvicorn app.main:app --reload
```
The server will be available at `http://localhost:8000`.
Swagger docs are available at `http://localhost:8000/docs`.

## API Endpoints

### 1. Ingest PDF
`POST /ingest/`
- **Body**: `multipart/form-data`
  - `file`: PDF file
  - `subject`: (Optional) Grade/Subject name

### 2. Generate Quiz
`POST /quiz/generate`
- **Body**:
  ```json
  { "source_id": "SRC_XXXX" }
  ```

### 3. Get Quiz Questions
`GET /quiz/`
- **Query Params**: `topic`, `difficulty`

### 4. Submit Answer
`POST /submit-answer/`
- **Body**:
  ```json
  {
    "student_id": "S001",
    "question_id": "Q_XXXX",
    "selected_answer": "Option 1"
  }
  ```

## Key Features
- **Traceability**: Every question is linked to the specific text chunk it was generated from.
- **Duplicate Detection**: Uses cosine similarity to prevent saving questions that are too similar (>0.9) to existing ones.
- **Adaptive Engine**: Automatically adjusts student difficulty after every 3 responses (increases after 3 correct, decreases after 3 incorrect).
- **Graceful Error Handling**: LLM retries and strict JSON validation ensure reliable quiz generation.
