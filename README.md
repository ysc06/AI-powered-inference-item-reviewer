# 🧑‍🏫👩‍🏫 IntelFlux 

IntelFlux is an AI-Powered Exam Item Builder and Reviewer with Prompt Workflow. 
A major limitation of current NLP systems and large language models is their difficulty with inference and other higher-level reasoning tasks.
Most models can summarize or rewrite text, but they struggle to generate questions that require multi-step reasoning or logic across multiple passages. Because of this, they provide limited support for teachers preparing instructional materials or for students who need practice with deeper comprehension skills. 

This app provides a workflow that uses AI for generation while relying on structured prompts, validation checks, and human review to produce higher-quality inference-based exam items. It is a full-stack system built with OpenAI, Hugging Face embeddings, FastAPI, and React.



## Overview

This system showcases how **AI + backend orchestration + workflow automation** can transform exam content creation.  
It provides a complete pipeline:
- Generate exam items from `.docx` or text prompts using OpenAI GPT-4.1  
- Validate structure and enforce guardrails  
- Compute semantic embeddings for similarity detection  
- Enable human reviewers to approve/reject items  
- Commit approved items and export them to CSV

---

## Features

| Category | Description |
|-----------|-------------|
| **AI Generation** | Uses OpenAI API to generate exam items in JSON format from `.docx` or prompt text |
| **Validation Guardrails** | Enforces choice length limits and ensures valid structure |
| **Duplicate Detection** | Embeds each item using Hugging Face Sentence Transformers for semantic similarity search |
| **Review Workflow** | Supports `approve`, `reject`, and `commit` actions |
| **Frontend** | React-based dashboard for item viewing, approval, and similarity display |

🍕Secret Sauce: Prompts engineered through a developer’s analytical mindset, enabling systematic examination and transformation of exam content.


## Architecture

```
+------------------------------------------------------+
|                    Frontend (React)                 |
|  - Reviewer Dashboard                               |
|  - Approve / Reject / Commit Workflow               |
+---------------------------▲--------------------------+
                            |
                            ▼
+---------------------------+--------------------------+
|             FastAPI Backend (Python)                 |
|  - /api/items CRUD routes                            |
|  - /api/items/generate (OpenAI prompt generation)     |
|  - /api/items/similar (embedding search)              |
|  - /api/items/approve, /reject, /commit               |
|  - SQLite via SQLAlchemy ORM                          |
+---------------------------▲--------------------------+
                            |
                            ▼
+---------------------------+--------------------------+
|                AI & Embedding Services               |
|  - OpenAI GPT-4.1 / GPT-4o for generation            |
|  - Hugging Face Sentence Transformers embeddings      |
+------------------------------------------------------+
```

---

## Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/exam-item-reviewer.git
cd exam-item-reviewer
```

### 2️⃣ Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Add your API key in `.env`
```
OPENAI_API_KEY=your_api_key_here
```

### 4️⃣ Initialize the database
```bash
python -m backend.app.db_init
```

### 5️⃣ Run the backend server
```bash
uvicorn backend.app.main:app --reload
```
Visit: http://127.0.0.1:8000/docs

### 6️⃣ (Optional) Run with Docker Compose
```bash
docker-compose up --build
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| `POST` | `/api/items/` | Create new item |
| `GET` | `/api/items/` | List all items |
| `POST` | `/api/items/generate` | Generate item from OpenAI prompt |
| `GET` | `/api/items/{id}/similar` | Find top-K similar items |
| `POST` | `/api/items/{id}/approve` | Approve item |
| `POST` | `/api/items/{id}/reject` | Reject item |
| `POST` | `/api/items/commit` | Commit approved items |
| `GET` | `/api/export` | Export items to CSV |


---

## Roadmap

- [x] FastAPI backend + SQLite ORM  
- [x] CRUD & similarity routes  
- [x] Review workflow (approve/reject/commit)  
- [x] OpenAI generation from `.docx` prompt  
- [x] React frontend integration  


---

## Tech Stack

| Layer | Tools |
|--------|--------|
| **Backend** | FastAPI, SQLAlchemy, SQLite |
| **AI** | OpenAI API, Hugging Face Sentence Transformers |
| **Frontend** | React, JavaScript, HTML, CSS |
| **Utilities** | dotenv, Pydantic, JSON Validation |

---
## Challenges
**1. Making AI output predictable** 
- The OpenAI model sometimes returned incomplete or messy results (missing choices, too-long stems, wrong formats).I had to add validation rules and cleanup logic to make sure every generated item met the required structure. <br>

**2. Handling different item states** 
- Each item can be pending, approved, rejected, or committed. Keeping these states consistent across the database, API, and frontend UI was harder than expected. I had to build a clean mapping so the backend and frontend always spoke the same “language.”
**3. Building similarity search with embeddings** 
The system detects duplicate or similar items using embeddings.This required: 
-- caching embeddings so we don’t recompute them
-- managing model downloads
-- handling performance when comparing many items
**4. Dockerizing the whole project**

- Running the backend, frontend, and database inside Docker introduced issues like:
- fixing Python import paths
- passing environment variables to Vite
- setting up CORS correctly
- making sure the SQLite database stays persistent
**5. Showing long stimuli and text correctly in the UI**
Some stimuli are long paragraphs.I had to handle:
- formatting
- escaping characters
- avoiding broken layouts in the React frontend
**6. Building a reviewer-friendly interface**
- The UI needed clear status tabs, search, and clean item display.
- Handling loading states, errors, and async API calls added complexity.
**7. Ensuring the system is stable end-to-end**
Because this is a full-stack + AI project, small issues in one layer often affected others.
I learned to:
- test each part separately
- check API responses
- keep a clean contract between backend and frontend
---

## Author
**Naomi (Yu-Shan) Cheng**  
Master of Computer Science (AI Specialization), University of Illinois Urbana–Champaign  


---
