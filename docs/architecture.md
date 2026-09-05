# Architecture Specification
# The Lenny Growth Assistant

## 1. Architecture Overview

The Lenny Growth Assistant uses a full-stack architecture with a React-based frontend, FastAPI backend, PostgreSQL/Supabase persistence, pgvector retrieval, and a provider abstraction supporting local Ollama and a cloud LLM.

```text
                         ┌─────────────────────────┐
                         │       React UI           │
                         │ Chat + Sessions          │
                         │ Provider Selector        │
                         │ Artifact Viewer          │
                         └────────────┬────────────┘
                                      │ HTTP / SSE
                                      ▼
                         ┌─────────────────────────┐
                         │       FastAPI API        │
                         │ Sessions / Chat / Health │
                         └───────┬─────────┬─────────┘
                                 │         │
                      ┌──────────┘         └─────────────┐
                      ▼                                  ▼
             ┌──────────────────┐             ┌──────────────────┐
             │   RAG Pipeline   │             │ LLM Provider     │
             │ Query Embedding  │             │    Factory       │
             │ Vector Retrieval │             ├──────────────────┤
             │ Context Builder  │             │ Ollama           │
             └────────┬─────────┘             │ Cloud Provider   │
                      │                       └──────────────────┘
                      ▼
             ┌────────────────────┐
             │ PostgreSQL         │
             │ + pgvector         │
             │ Sessions           │
             │ Messages           │
             │ Artifacts          │
             │ Transcript Chunks  │
             └────────────────────┘
```

## 2. Main Components

### Frontend

Responsibilities:

- Chat interface
- Session selection/new session
- Streaming response rendering
- Provider selection
- Citation display
- Artifact detection/display
- Responsive layout
- Loading and error states
- Accessible controls

### FastAPI Backend

Responsibilities:

- API routing
- Request validation
- Session management
- Message persistence
- Retrieval orchestration
- Provider selection
- Streaming responses
- Artifact persistence
- Health checks
- Error handling and logging

### RAG Layer

Responsibilities:

- Generate query embeddings
- Search transcript chunks using vector similarity
- Apply similarity threshold
- Select top relevant chunks
- Build grounded model context
- Preserve source metadata

### Provider Layer

A common provider interface keeps the application independent of a specific LLM vendor.

```text
BaseLLMProvider
       │
       ├── OllamaProvider
       │
       └── CloudProvider
```

The application requests a provider through a factory/configuration layer rather than directly coupling business logic to a specific model.

## 3. Data Model

### Session

```text
id          UUID
title       string
created_at  timestamp
updated_at  timestamp
```

A session represents an independent conversation.

### Message

```text
id          UUID
session_id  UUID
role        string
content     text
sources     JSONB
created_at  timestamp
```

Messages belong to exactly one session.

### Artifact

```text
id            UUID
message_id    UUID
artifact_type markdown | html
content       text
created_at    timestamp
```

Artifacts are associated with the message that generated them.

### Transcript Chunk

```text
id               UUID
episode_title    string
guest_name       string
publication_date date/timestamp
timestamp_ref    string
chunk_text       text
embedding        vector
metadata         JSON/JSONB
created_at       timestamp
```

The vector field stores the embedding used for similarity retrieval.

## 4. Knowledge Ingestion

The ingestion pipeline is:

```text
Transcript Repository
        ↓
Download / Load
        ↓
Parse Markdown/TXT
        ↓
Extract Metadata
        ↓
Chunk Transcript
        ↓
Generate Embeddings
        ↓
Store in PostgreSQL + pgvector
        ↓
Create Vector Index
```

Target chunking behavior:

- Approximately 500–800 tokens per chunk
- Approximately 100-token overlap
- Preserve episode and guest metadata
- Preserve timestamp/topic information when available

The ingestion process should be repeatable and avoid unnecessary duplication.

## 5. Retrieval

For a user query:

```text
Question
   ↓
Embedding Model
   ↓
pgvector cosine similarity
   ↓
Similarity threshold
   ↓
Top 4–6 chunks
   ↓
Grounded context
```

The retrieval layer returns both text and source metadata.

The model receives only the relevant transcript context needed for the response.

If retrieval does not meet the configured relevance threshold, the system should acknowledge insufficient information rather than fabricate an answer.

## 6. Grounded Generation

The grounded prompt establishes the transcript context as the knowledge source.

The model is instructed to:

- Answer using retrieved transcript context.
- Avoid unsupported claims.
- Attribute information to the appropriate episode/guest.
- Use the supplied source metadata for citations.
- Admit when the context is insufficient.

The response pipeline is:

```text
User Question
      ↓
Retrieve
      ↓
Build Grounded Prompt
      ↓
Select LLM Provider
      ↓
Stream Tokens
      ↓
Attach Sources
      ↓
Persist Message
      ↓
Frontend
```

## 7. Session Context

Each session maintains its own message history.

A follow-up question uses the current session's context while retrieving new transcript evidence for the new question.

Session IDs prevent unrelated conversations from sharing message history.

## 8. LLM Provider Routing

Configuration determines the default provider, while the UI can expose provider selection.

Example:

```env
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=
```

Provider behavior:

### Ollama

- Local inference
- Used for the required demonstration
- Streaming through the local Ollama API

### Cloud Provider

- Used when configured
- Accessed through the same provider interface
- Requires the appropriate API credential

The provider abstraction means the RAG and API layers do not need to know provider-specific implementation details.

## 9. Streaming

The chat API uses a streaming response mechanism such as Server-Sent Events.

Conceptual event flow:

```text
status → retrieving transcripts
status → generating response
token  → partial response
source → citation metadata
done
```

Streaming reduces perceived latency and allows users to see generation progress.

## 10. Ship 30 for 30 Skill

The Ship 30 capability is isolated as a dedicated skill rather than being embedded as unrelated prompt text throughout the application.

Expected structure:

- Strong hook
- Curiosity gap or meaningful tension
- Clear narrative progression
- Short paragraphs
- H2/H3 headings
- Bullets
- Selective bold emphasis
- Approximately 1,250 words
- Concrete operational takeaway
- Grounded attribution

The skill receives retrieved transcript context and the user's request.

## 11. Artifact Architecture

Supported artifact types:

```text
markdown
html
```

Artifact flow:

```text
User Request
    ↓
LLM Generation
    ↓
Artifact Detection
    ↓
Artifact Persistence
    ↓
Artifact Viewer
```

Markdown is rendered as formatted content.

HTML/CSS is rendered inside an isolated iframe.

## 12. Artifact Security

Generated HTML is treated as untrusted.

The viewer uses:

```html
sandbox="allow-scripts"
```

`allow-same-origin` is intentionally omitted.

The goal is to prevent generated content from gaining normal access to the parent application's:

- DOM
- cookies
- localStorage
- application state

Sanitization is also applied where appropriate before rendering.

This provides defense in depth: sanitization reduces dangerous markup while iframe sandboxing isolates the rendered document.

## 13. API Contracts

### Create Session

```text
POST /api/sessions
```

Creates a new independent chat session.

### Get Session

```text
GET /api/sessions/{session_id}
```

Returns session information and message history.

### Chat

```text
POST /api/chat
```

Accepts a session, message, mode, and provider selection and returns a streamed response.

### Health

```text
GET /api/health
```

Reports application and dependency health, including database, Ollama, and knowledge-base status.

## 14. Persistence Strategy

PostgreSQL/Supabase provides relational persistence.

pgvector stores transcript embeddings alongside source metadata, allowing relational records and vector search to remain in the same database.

This avoids introducing a separate vector database for the MVP.

## 15. Resilience

The application handles:

- Database connection failures
- Missing cloud API credentials
- Ollama unavailability
- Provider timeouts
- Empty retrieval results
- Invalid requests
- Artifact rendering failures

Errors should be returned in a structured and user-understandable way.

## 16. Observability

Important events should be logged, including:

- Requests
- Retrieval completion
- Retrieval latency
- Provider selection
- Provider latency
- Provider errors
- Artifact generation
- Database errors

Secrets must never be written to logs.

## 17. Deployment Topology

The application supports a reproducible local workflow using Docker Compose.

Conceptually:

```text
Docker Compose
 ├── PostgreSQL + pgvector
 ├── FastAPI backend
 └── Frontend
```

For the evaluation workflow, Supabase can provide PostgreSQL persistence and Ollama can run locally on the developer/evaluator machine.

Environment-specific values are supplied through `.env`.

## 18. Security Considerations

Primary security controls:

- No secrets in source code
- `.env` excluded from source control
- Pydantic input validation
- Parameterized/database ORM queries
- Restricted CORS
- Structured error handling
- Safe logging
- Untrusted artifact treatment
- Sandboxed HTML iframe
- No `allow-same-origin` on artifact iframe

## 19. Known Trade-offs

### Supabase vs Local PostgreSQL

Supabase reduces local database setup time and provides managed PostgreSQL while retaining PostgreSQL/pgvector semantics.

### Local vs Cloud LLM

Ollama provides a local, controllable evaluation path. Cloud models can provide stronger quality but introduce API credentials, cost, and network dependency.

### Single Database for Relational + Vector Data

Using PostgreSQL + pgvector keeps the MVP architecture simple and reduces operational complexity compared with introducing a separate vector database.

### Streaming vs Batch Responses

Streaming improves perceived responsiveness even when local model generation takes time.

## 20. Extension Points

The architecture can later support:

- Additional LLM providers
- More embedding models
- Authentication
- Multi-tenant data isolation
- Advanced retrieval/reranking
- Conversation analytics
- Background ingestion jobs
- Production tracing/metrics
- More artifact types
