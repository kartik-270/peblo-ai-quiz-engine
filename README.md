# Peblo AI: Backend Engineer Challenge - Adaptive Quiz Engine

A robust, AI-driven backend system designed to ingest educational PDFs and convert them into interactive, adaptive quiz experiences with full data traceability.

## 🚀 Backend Engineering Highlights

This project focuses on building a production-ready pipeline that bridges static educational content with dynamic AI assessments.

### 1. Ingestion & Data Pipeline
- **Clean Extraction**: Uses `PyMuPDF` with a custom post-extraction cleaning phase to remove noise, normalize whitespace, and preserve document structure.
- **Traceable Chunking**: Content is split into logical chunks, each stored with a unique ID to ensure every generated question can be traced back to its specific source text.

### 2. AI Quiz Generation Service
- **Structured LLM Orchestration**: Integrates with **Llama 3.3 (via Hugging Face)** using a specialized "system-user" prompt pattern for high-fidelity educational output.
- **Strict Validation**: Implemented **Pydantic Schemas** (`AIQuizResponseSchema`) to validate LLM JSON outputs before database ingestion, ensuring zero schema drift.
- **Duplicate Detection**: Uses `sentence-transformers` (cosine similarity) to prevent semantic overlap between generated questions, maintaining a high-quality question bank.
- **Efficiency Sampling**: Implements a chunk-sampling strategy to efficiently generate diverse questions from large textbooks without overloading the LLM.

### 3. Adaptive Difficulty Engine
- **Historical Analysis**: Uses a sliding-window algorithm (window size of 3) to analyze student performance.
- **RSA (Rolling Success Accuracy)**: Calculates real-time accuracy thresholds (>80% for level up, <40% for level down) to adjust the student's difficulty level dynamically.
- **Relative Difficulty Logic**: The prompt engineering ensures that "Easy", "Medium", and "Hard" are interpreted relative to the specific grade level detected in the PDF.

### 4. Observability & Stability
- **Request Middleware**: Custom FastAPI middleware logs every request method, path, status, and duration for production monitoring.
- **Robust Error Handling**: Multi-stage retries and fallback mechanisms for LLM calls and database transactions.

---

## 🛠️ Technology Stack
- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy (PostgreSQL)
- **AI/ML**: Hugging Face Inference API, Sentence-Transformers
- **PDF Core**: PyMuPDF (fitz)

---

## ⚙️ Setup & Installation

### 1. Clone & Environment
```bash
git clone <repository-url>
cd peblo-ai-quiz-engine
python -m venv venv
# Windows: .\venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration (`.env`)
```env
HF_TOKEN=your_huggingface_token
DATABASE_URL=your_postgresql_url
```

---

## 🖥️ Running the Engine

The system is designed for **Zero-Configuration Start**. Running the application will automatically:
1. Initialize all database tables and schema.
2. Prepare the synchronous generation pipeline.
3. Serve the interactive portal.

```bash
python -m app.main
```
- **Web Portal**: [http://localhost:8000](http://localhost:8000)
- **Interactive docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📂 Backend Architecture
```text
├── app/
│   ├── core/      # Database config, Logging, Settings
│   ├── models/    # Source, Chunk, Question, StudentAnswer (SQLAlchemy)
│   ├── routes/    # REST API Layer (Ingest, Quiz, Answer)
│   ├── schemas/   # Strict Pydantic Validation Schemas
│   └── services/  # Core logic: LLM, PDF, Adaptive Engine, Duplicates
└── static/        # Frontend assets (served via FastAPI)
```
