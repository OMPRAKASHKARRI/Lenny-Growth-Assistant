# Product Requirements Document (PRD)
# The Lenny Growth Assistant

## 1. Product Overview

The Lenny Growth Assistant is a full-stack AI assistant that turns Lenny's Podcast transcripts into a searchable, grounded knowledge system for product managers and growth leaders.

The product allows users to ask product and growth questions, receive answers grounded in podcast transcripts with source citations, continue conversations through independent sessions, generate Ship 30 for 30-style written content, and create Markdown or HTML artifacts that can be viewed directly inside the application.

The product is designed as a small forward-deployment engagement: it should be understandable, runnable, testable, and easy for another engineer to operate.

## 2. User and Problem

### Primary User

The primary persona is a product manager or growth leader who wants actionable product and growth knowledge without spending hours searching or listening through a large podcast archive.

### Problem

Lenny's Podcast contains a large amount of practical knowledge from experienced product and growth leaders. Finding the relevant insight for a specific question can require listening to long episodes, searching transcripts manually, and synthesizing information across sources.

### Product Solution

The assistant provides a conversational interface over the transcript knowledge base. It retrieves relevant transcript context, asks the configured language model to answer from that context, and exposes the supporting source information so users can understand where an answer came from.

## 3. Goals

1. Provide grounded answers based on Lenny's Podcast transcripts.
2. Clearly identify the sources supporting each answer.
3. Preserve independent chat sessions and conversation context.
4. Support local Ollama inference for evaluation and demonstration.
5. Support a cloud LLM provider through the same provider abstraction.
6. Generate approximately 1,250-word Ship 30 for 30-style content.
7. Generate Markdown and HTML artifacts from the conversation.
8. Render generated artifacts inside the application.
9. Provide a reproducible and operationally understandable system.
10. Provide clear documentation and tests for handoff.

## 4. Success Metrics

The assignment defines the following target outcomes:

- Retrieval citation accuracy: >= 90%.
- Local inference latency: < 4 seconds to first token where hardware/model performance permits.
- Artifact render safety: 0 known XSS vulnerabilities in the implemented rendering path.

Additional practical success indicators:

- Users can complete a grounded question-answer flow without understanding RAG or model infrastructure.
- A local Ollama demo can be completed successfully.
- A generated HTML artifact renders inside the product rather than requiring an external application.
- Another engineer can start and troubleshoot the application using the README.

## 5. Core User Flows

### Flow A — Grounded Question

1. User creates or selects a chat session.
2. User submits a product/growth question.
3. Backend creates an embedding for the query.
4. Relevant transcript chunks are retrieved from the vector knowledge base.
5. The selected LLM receives the question and retrieved context.
6. The response is streamed to the frontend.
7. Source citations are displayed with the answer.
8. The message and source information are persisted.

### Flow B — Follow-up Question

1. User continues an existing session.
2. Previous conversation context is included.
3. The new question is retrieved against the transcript knowledge base.
4. The assistant responds using the retrieved transcript context and session context.

### Flow C — Insufficient Context

1. User asks a question that is not adequately supported by the transcript archive.
2. Retrieval returns no sufficiently relevant context.
3. The assistant does not fabricate an answer or citation.
4. The user is told that the available Lenny podcast archive does not contain sufficient information.

### Flow D — Ship 30 for 30 Content

1. User asks for an article or essay based on the current knowledge.
2. Relevant transcript context is retrieved.
3. The dedicated Ship 30 for 30 skill structures the response.
4. The output targets approximately 1,250 words.
5. The content uses a strong hook, skimmable structure, headings, bullets, selective emphasis, and an actionable takeaway.
6. Claims remain grounded in transcript context.

### Flow E — Artifact Generation

1. User asks for an artifact.
2. The assistant generates Markdown or HTML/CSS content.
3. The application detects the artifact.
4. The artifact is persisted.
5. The right-side Artifact Viewer renders the result.
6. HTML is treated as untrusted content and isolated in a sandboxed iframe.

## 6. Scope

### Included

- FastAPI backend
- PostgreSQL/Supabase persistence
- pgvector retrieval
- Transcript ingestion and embeddings
- Grounded conversational RAG
- Source citations
- Independent sessions
- Streaming responses
- Ollama local provider
- Cloud provider abstraction
- Provider selection
- Ship 30 for 30 skill
- Markdown and HTML artifacts
- In-app Artifact Viewer
- HTML isolation/sanitization
- Health checks
- Error handling
- Docker Compose
- Environment example
- Tests
- PRD, architecture, design, and README documentation

### Intentionally Excluded / Deferred

- User authentication and enterprise identity management
- Complex multi-tenant authorization
- Advanced analytics dashboards
- Full production observability infrastructure
- Fine-tuning a custom LLM
- Audio transcription itself
- A complex agent planning framework beyond the required product workflow

These are outside the highest-value MVP scope for the assignment.

## 7. Assumptions

- The supplied Lenny Podcast transcript repository is the knowledge source.
- Transcript files may have different metadata formats, so ingestion should tolerate reasonable variation.
- Ollama is available locally for the required evaluation demonstration.
- PostgreSQL with pgvector is available through Supabase.
- Generated HTML is untrusted and must be isolated from the parent application.
- The evaluator values a working, understandable system over unnecessary enterprise complexity.

## 8. Risks and Trade-offs

### Hallucination

Risk: the language model may produce information not present in the transcripts.

Mitigation: retrieve transcript context, enforce grounded prompting, use a similarity threshold, and explicitly handle insufficient retrieval.

### Local Model Quality

Risk: a local 3B/7B/8B model may have weaker reasoning and writing quality than a cloud model.

Trade-off: Ollama provides a zero/low-cost local evaluation path and satisfies the required local demonstration, while the provider abstraction allows cloud models when higher quality is needed.

### Latency

Risk: local inference can be slower depending on hardware.

Mitigation: stream responses and provide status feedback.

### Artifact Security

Risk: generated HTML can contain unsafe scripts or markup.

Mitigation: sanitize where appropriate and render HTML inside a sandboxed iframe without `allow-same-origin`.

### Data Availability

Risk: the transcript archive may change or ingestion may be incomplete.

Mitigation: keep ingestion reproducible and preserve source metadata for traceability.

### Provider Availability

Risk: Ollama or a cloud API can be unavailable.

Mitigation: provider health checks, timeouts, structured errors, and explicit provider status.

## 9. Acceptance Criteria

The MVP is acceptable when:

- A user can create an independent session.
- A user can ask a question and receive a streamed answer.
- The answer is grounded in transcript retrieval and includes source information.
- Unsupported questions are handled without fabricated citations.
- Ollama can serve the local demo.
- The provider abstraction can select the cloud provider.
- Ship 30 for 30 content can be generated.
- HTML artifacts can be generated, persisted, and rendered in the Artifact Viewer.
- HTML rendering uses sandbox isolation.
- PostgreSQL/Supabase persistence works.
- Health checks report core dependency status.
- Backend tests pass and the frontend production build succeeds.
- The system has documented setup, architecture, design, troubleshooting, and deployment information.

## 10. Implementation Plan

1. Establish the backend and database foundation.
2. Load and index transcript knowledge.
3. Implement retrieval and grounded generation.
4. Implement provider abstraction and Ollama/cloud routing.
5. Implement session persistence and streaming.
6. Implement Ship 30 skill.
7. Implement artifact generation and secure rendering.
8. Build and polish the chat interface.
9. Add tests, health checks, logging, and resilience.
10. Validate Docker startup and documentation.
11. Demonstrate the local Ollama workflow.

## 11. Definition of Done

The product is considered ready for evaluation when the complete user journey works locally, the required deliverables are present, secrets are excluded from source control, and the documented verification steps can be followed by another engineer.
