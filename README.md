# The Lenny Growth Assistant 🚀

A full-stack AI-powered conversational assistant that turns **Lenny's Podcast transcripts** into grounded, actionable product and growth knowledge.

The application combines **RAG, PostgreSQL/pgvector, Ollama, cloud LLM support, streaming chat, Ship 30 for 30 content generation, and a secure in-app Artifact Viewer**.

---

## ✨ Features

- 💬 Conversational product and growth assistant
- 🔎 Transcript-based RAG retrieval
- 📚 Source-grounded answers with citations
- 🧠 Session-aware follow-up conversations
- 🦙 Local Ollama LLM support
- ☁️ Cloud LLM provider abstraction
- 🔄 Runtime provider switching
- ⚡ Streaming chat responses
- ✍️ Dedicated Ship 30 for 30 writing skill
- 📝 Markdown artifact generation
- 🌐 HTML/CSS artifact generation
- 🖼️ Claude-style side-by-side Artifact Viewer
- 🔒 Sandboxed HTML rendering
- 🗄️ Supabase PostgreSQL persistence
- 🔢 pgvector embeddings and similarity search
- ❤️ Health checks for backend, database, Ollama, and knowledge base
- 🐳 Docker Compose support
- 🧪 Automated backend tests
- 📱 Responsive frontend
- ♿ Accessibility-focused UI states

---

# 🏗️ Architecture

```text
┌───────────────────────────────────────────────────────────────┐
│                         React Frontend                        │
│                                                               │
│  Chat │ Sessions │ Provider Selector │ Citations │ Artifacts │
└──────────────────────────────┬────────────────────────────────┘
                               │ HTTP / SSE
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                        │
│                                                               │
│ Sessions │ Chat │ RAG │ Ship 30 │ Artifacts │ Health │ Logs  │
└───────────────┬───────────────────────┬───────────────────────┘
                │                       │
                ▼                       ▼
┌────────────────────────┐   ┌──────────────────────────────────┐
│ PostgreSQL + pgvector  │   │          LLM Providers           │
│                        │   │                                  │
│ Sessions               │   │  Ollama          Cloud Provider  │
│ Messages               │   │  (Local)         (Optional)      │
│ Artifacts              │   │                                  │
│ Transcript Chunks      │   └──────────────────────────────────┘
│ Embeddings             │
└────────────────────────┘
```

### RAG Flow

```text
User Question
      ↓
Query Embedding
      ↓
pgvector Similarity Search
      ↓
Top Relevant Transcript Chunks
      ↓
Similarity Threshold
      ↓
Grounded Prompt
      ↓
Selected LLM Provider
      ↓
Streaming Response
      ↓
Citations + Persistence
```

---

# 🛠️ Tech Stack

## Frontend

- React
- Vite
- JavaScript
- CSS
- Markdown rendering
- DOMPurify
- Sandboxed iframe

## Backend

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- asyncpg
- httpx

## Database

- PostgreSQL
- Supabase
- pgvector

## AI

- Ollama
- `llama3.2:3b`
- Cloud LLM provider
- Sentence-transformers embeddings

## Deployment

- Docker
- Docker Compose
- Supabase

---

# 📁 Project Structure

```text
Lenny Growth Assistant/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
│
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   └── design.md
│
├── agent_transcripts/
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── scripts/
│   │   ├── download_transcripts.py
│   │   └── ingest.py
│   │
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── providers/
│   │   ├── rag/
│   │   └── skills/
│   │
│   └── tests/
│
└── frontend/
    ├── package.json
    └── src/
        ├── main.jsx
        └── styles.css
```

---

# ⚙️ Prerequisites

Recommended environment:

- Python 3.11+
- Node.js 18+ or 20 LTS
- Docker Desktop
- Ollama
- Supabase account
- Git

The assignment targets a local environment capable of running a small local model through Ollama.

---

# 🗄️ Supabase Setup

This project uses Supabase as the PostgreSQL database.

## 1. Create a Supabase project

Create a new PostgreSQL project in Supabase.

## 2. Enable pgvector

In the Supabase dashboard:

```text
Database
  → Extensions
  → vector
  → Enable
```

## 3. Get the database connection string

Use the Supabase connection/pooler string appropriate for your environment.

The backend uses SQLAlchemy's async PostgreSQL driver, so the URL should use:

```text
postgresql+asyncpg://
```

Example format:

```env
DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@HOST:5432/DATABASE
```

**Never commit your real database password.**

---

# 🔐 Environment Variables

Create a local `.env` file based on `.env.example`.

Example:

```env
DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@HOST:5432/postgres

DEFAULT_LLM_PROVIDER=ollama

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

CORS_ORIGINS=http://localhost:5173
```

### Important

Do not commit:

```text
.env
```

Only commit:

```text
.env.example
```

---

# 🦙 Ollama Setup

Install Ollama and make sure it is running.

Pull the model:

```bash
ollama pull llama3.2:3b
```

Verify:

```bash
ollama list
```

The application defaults to:

```env
DEFAULT_LLM_PROVIDER=ollama
```

The local Ollama workflow is the required demonstration path for the assignment.

---

# 🚀 Running the Backend

From the project root:

### Create/activate your Python environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r backend/requirements.txt
```

### Start FastAPI

Windows:

```powershell
$env:PYTHONPATH="backend"
uvicorn backend.app.main:app --reload --port 8000
```

If the project's existing configuration uses a different module path, use the command documented by the current backend configuration.

Backend:

```text
http://localhost:8000
```

Health endpoint:

```text
http://localhost:8000/api/health
```

---

# 💾 Transcript Ingestion

The project includes transcript download and ingestion scripts.

```text
backend/scripts/download_transcripts.py
backend/scripts/ingest.py
```

The ingestion pipeline:

```text
Transcript Files
      ↓
Parse
      ↓
Extract Episode / Guest Metadata
      ↓
Chunk Transcript
      ↓
Generate Embeddings
      ↓
Store in PostgreSQL + pgvector
```

Target chunking strategy:

- Approximately 500–800 tokens
- Approximately 100-token overlap
- Preserve episode/guest metadata
- Preserve timestamp/topic references where available

Run the appropriate ingestion command from the project root after configuring the database and embedding dependencies.

---

# 💬 Running the Frontend

Go to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start development server:

```bash
npm run dev
```

The frontend is typically available at:

```text
http://localhost:5173
```

---

# 🐳 Docker Compose

The project includes Docker Compose configuration for reproducible application startup.

Run:

```bash
docker compose up --build
```

Expected services include:

```text
db
backend
frontend
```

If Supabase is being used as the active database, configure the backend environment accordingly rather than using a local database service.

Ollama can run on the host machine for the local model demonstration.

---

# 🔌 API

## Create Session

```http
POST /api/sessions
```

Creates an independent chat session.

## Get Session

```http
GET /api/sessions/{session_id}
```

Returns session information and message history.

## Chat

```http
POST /api/chat
```

Streams the assistant response.

The chat flow includes:

```text
Retrieving transcripts
        ↓
Generating response
        ↓
Streaming tokens
        ↓
Sources
        ↓
Done
```

## Health

```http
GET /api/health
```

Checks:

- API
- Database
- Ollama
- Knowledge base

---

# 🔎 Grounded RAG

The assistant is designed to answer using retrieved Lenny's Podcast transcript context.

For each query:

1. Generate query embedding.
2. Search transcript vectors.
3. Select relevant chunks.
4. Apply similarity threshold.
5. Build grounded context.
6. Send context to the selected LLM.
7. Stream the response.
8. Preserve source metadata.

If the transcript archive does not contain sufficient information, the assistant should acknowledge the limitation rather than inventing facts or citations.

Example:

```text
I do not have sufficient information in Lenny's podcast archive to answer this.
```

---

# 📚 Citations

Responses identify supporting transcript sources.

Example:

```text
[Episode: Example Episode, Guest: Example Guest, Topic/Timestamp]
```

Source information is persisted with the message where applicable.

---

# ✍️ Ship 30 for 30 Skill

The project includes a dedicated Ship 30 for 30 writing skill.

It targets approximately:

```text
1,250 words
```

The generated content emphasizes:

- Strong opening hook
- Curiosity gap or meaningful tension
- Clear narrative progression
- Short paragraphs
- Headings
- Bullets
- Selective bold emphasis
- Concrete actionable takeaway
- Transcript-grounded claims

Implementation:

```text
backend/app/skills/ship30_writer.py
```

---

# 🖼️ Artifact Viewer

The application supports two artifact types:

```text
Markdown
HTML/CSS
```

Generated artifacts can be displayed in the application's right-side viewer.

### Markdown

Markdown is rendered as formatted content.

### HTML

Generated HTML is treated as untrusted content and rendered inside a sandboxed iframe.

The iframe uses:

```html
sandbox="allow-scripts"
```

and intentionally does not use:

```text
allow-same-origin
```

This reduces the ability of generated content to access the parent application's cookies, storage, DOM, and application state.

DOMPurify is used where appropriate as an additional sanitization layer.

---

# 🔒 Security

Important security practices include:

- No API keys in source code
- `.env` excluded from Git
- Input validation
- Parameterized database access
- Restricted CORS
- Structured error handling
- Safe logging
- Generated HTML treated as untrusted
- Sandboxed iframe
- No `allow-same-origin`
- No secrets in logs

---

# ❤️ Health Check

A successful health check should report the major application dependencies.

Example:

```json
{
  "api": "ok",
  "database": "ok",
  "ollama": "ok",
  "knowledge_base": "ready"
}
```

A degraded dependency should be reported rather than silently hidden.

---

# 🧪 Testing

Backend tests:

```bash
pytest backend/tests -q
```

The project includes tests covering important areas such as:

- API behavior
- Embeddings
- Retrieval
- Provider behavior
- Session/persistence behavior where implemented

Frontend production build:

```bash
cd frontend
npm run build
```

Docker Compose validation:

```bash
docker compose config
```

---

# 🩺 Troubleshooting

## Ollama unavailable

Check:

```bash
ollama list
```

Then make sure Ollama is running and the configured model exists:

```bash
ollama pull llama3.2:3b
```

Verify:

```env
OLLAMA_BASE_URL=http://localhost:11434
```

## Database connection failure

Check:

- Supabase project is active.
- `DATABASE_URL` is correct.
- Password is correct.
- The URL uses `postgresql+asyncpg://` for the async backend.
- pgvector is enabled.

## Empty retrieval

Check:

- Transcript ingestion completed.
- Embeddings exist.
- Database connection is healthy.
- pgvector is enabled.
- The query is relevant to the transcript archive.

## Cloud provider failure

Check:

- Cloud API key is configured.
- Provider/model configuration is correct.
- Network access is available.

If the cloud provider is not configured, use Ollama for the local evaluation workflow.

## Frontend cannot reach backend

Check:

```env
CORS_ORIGINS=http://localhost:5173
```

and verify the backend is running on the configured API port.

---

# 📊 Operational Readiness

The application includes:

- Health checks
- Structured logging
- Provider error handling
- Database error handling
- Ollama timeout/unavailable handling
- Empty retrieval handling
- Artifact rendering isolation
- Environment-based configuration
- Docker Compose support

The goal is for another engineer to be able to run, test, troubleshoot, and extend the system without needing to understand the implementation from scratch.

---

# 📖 Documentation

Additional project documentation:

```text
docs/PRD.md
docs/architecture.md
docs/design.md
```

### PRD

Describes:

- User
- Problem
- Goals
- Success metrics
- Assumptions
- Scope
- Risks
- Trade-offs
- Acceptance criteria

### Architecture

Describes:

- System components
- RAG pipeline
- Database schema
- API contracts
- Provider abstraction
- Streaming
- Artifact security
- Deployment
- Resilience

### Design

Describes:

- UI/UX principles
- Information architecture
- Chat states
- Artifact viewer
- Responsive behavior
- Accessibility
- Design trade-offs

---

# 🎥 Demo Flow

For the assignment demonstration:

1. Open the Lenny Growth Assistant.
2. Show the initial chat interface.
3. Ask a product/growth question.
4. Show the grounded answer.
5. Show transcript citations.
6. Show that **Ollama** is the active local provider.
7. Ask for a reusable content artifact.
8. Generate an HTML artifact.
9. Show it rendering inside the Artifact Viewer.
10. Briefly explain:
   - RAG + pgvector
   - local Ollama
   - provider abstraction
   - artifact sandboxing
11. Explain one engineering trade-off.

The assignment requires a 2–3 minute demo with camera enabled.

---

# 🚧 Known Limitations

- Local model quality depends on available hardware and the selected Ollama model.
- Ship 30 output targets approximately 1,250 words rather than enforcing an exact word count.
- Artifact content is generated by the selected model and should remain grounded in the current context.
- Full production authentication/multi-tenancy is outside the MVP scope.
- Production-scale observability can be added in a future iteration.

---

# 🎯 Assignment Alignment

This project is designed around the assignment's primary evaluation areas:

- Customer and product judgment
- Technical execution
- Agentic/RAG architecture
- Source grounding
- Local/cloud model configuration
- Deployment and operability
- Code quality
- UI/UX
- Security
- Documentation
- Communication

---

# 👨‍💻 Development Philosophy

The implementation prioritizes:

```text
Working functionality
        ↓
Reliable grounding
        ↓
Clear architecture
        ↓
Security
        ↓
Operational readiness
        ↓
UI polish
```

The system favors simple, explainable components over unnecessary infrastructure complexity.

---

## License

Created as a take-home engineering assignment for the Forward Deployed Engineer evaluation.
