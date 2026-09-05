# Design Specification
# The Lenny Growth Assistant

## 1. Design Goal

The product should feel like a focused professional knowledge workspace rather than a generic chatbot.

The primary design objective is to let a product manager move from:

```text
Question → Grounded Insight → Reusable Content → Artifact
```

with minimal cognitive overhead.

The interface should make the AI system understandable without requiring users to understand RAG, embeddings, models, or infrastructure.

## 2. Design Principles

### Grounding First

Sources should be visible and understandable. The interface should make it clear that answers come from the transcript knowledge base.

### Minimal Cognitive Load

Users should be able to ask questions naturally without configuring prompts or retrieval settings.

### Professional Simplicity

Use clear hierarchy, restrained visual decoration, readable typography, consistent spacing, and subtle borders.

### Progressive Disclosure

Advanced information such as source excerpts, provider details, and artifact content should be available without overwhelming the initial chat experience.

### Trust Through State

Loading, retrieval, generation, errors, and provider state should be visible rather than hidden.

### Accessibility

Controls should have labels, focus states, meaningful button names, and appropriate live regions for streaming content.

## 3. Information Architecture

The application is organized around three primary areas:

```text
Application
│
├── Header
│   ├── Product name
│   ├── Session controls
│   └── Provider selector
│
├── Main Workspace
│   ├── Chat Pane
│   │   ├── Conversation history
│   │   ├── Source citations
│   │   └── Composer
│   │
│   └── Artifact Viewer
│       ├── Artifact title
│       ├── Markdown preview
│       └── HTML preview
│
└── Status / Feedback
```

## 4. Primary Layout

Desktop:

```text
┌──────────────────────────────────────────────────────────────┐
│ Lenny Growth Assistant       Session        Ollama ▼         │
├──────────────────────────────┬───────────────────────────────┤
│                              │                               │
│          CHAT                │       ARTIFACT VIEWER         │
│                              │                               │
│ User message                │ Artifact title                │
│ Assistant response          │                               │
│ Source citations             │ Markdown / HTML preview       │
│                              │                               │
│                              │                               │
├──────────────────────────────┴───────────────────────────────┤
│ Ask Lenny's Podcast anything...                         Send │
└──────────────────────────────────────────────────────────────┘
```

The artifact panel can be collapsed when the user wants a larger chat area.

## 5. Initial Empty State

The first screen should immediately communicate the product value.

Suggested content:

```text
Lenny Growth Assistant

Turn Lenny's Podcast into actionable product and growth knowledge.

Ask questions like:

“How should an early-stage startup prioritize growth experiments?”

“What makes a great product manager?”

“Create a growth experimentation framework.”
```

The empty state should avoid unnecessary technical terminology.

## 6. Chat Experience

### User Message

User messages should be visually distinct and compact.

### Assistant Message

Assistant messages should support:

- Markdown
- Headings
- Lists
- Bold emphasis
- Code when relevant
- Source citations

### Streaming State

While generating:

```text
Retrieving transcripts...
Generating response...
```

The response should progressively appear rather than waiting for the entire completion.

### Source Citations

Citations should be visually separated from the main answer.

Example:

```text
Sources
[Episode: Example Episode, Guest: Example Guest, Topic/Timestamp]
```

Where supported, the UI can allow users to expand supporting context.

## 7. Session UX

Users should be able to:

- Start a new chat
- Continue an existing chat
- See the current session
- Keep sessions independent

A new session should clearly reset the conversational context.

## 8. Provider Selector

The provider selector should clearly communicate which model path is active.

Example:

```text
Provider: Ollama ▼
```

Possible options:

```text
Ollama
Cloud
```

The selected value must represent the actual backend provider, not merely a visual toggle.

## 9. Artifact Viewer

The Artifact Viewer occupies the right side of the desktop workspace.

It should include:

- Artifact title
- Artifact type
- Preview
- Clear visual distinction from chat
- A visible indication that HTML is sandboxed

Example:

```text
┌──────────────────────────────────┐
│ Artifact: Growth Canvas          │
│ Sandboxed Preview                │
├──────────────────────────────────┤
│                                  │
│       Rendered Artifact          │
│                                  │
└──────────────────────────────────┘
```

The viewer should not redirect the user to another application.

## 10. Artifact States

### No Artifact

The viewer can remain collapsed or show a lightweight empty state.

### Loading

Show that an artifact is being generated.

### Markdown

Render formatted Markdown with readable typography.

### HTML

Render the HTML inside the sandboxed iframe.

### Error

If rendering fails, show an understandable error instead of breaking the entire chat interface.

## 11. Responsive Behavior

### Desktop

Use the two-pane layout.

### Tablet

Allow the artifact pane to become narrower or collapsible.

### Mobile

Prioritize the chat experience.

The artifact viewer should become a drawer, tab, or collapsible section so that the user does not have to scroll through a permanently split layout.

Avoid horizontal overflow.

## 12. Accessibility

The interface should include:

- Semantic buttons
- Accessible form labels
- Descriptive iframe titles
- Keyboard-accessible controls
- Visible focus states
- `aria-live` for streaming assistant content where appropriate
- Sufficiently descriptive error messages
- Meaningful empty states
- No information conveyed by color alone

## 13. Interaction States

The design should explicitly account for:

```text
Initial
↓
Typing
↓
Submitting
↓
Retrieving
↓
Streaming
↓
Completed
```

Error branches:

```text
Submitting
   ├── Invalid input
   ├── Database unavailable
   ├── Ollama unavailable
   ├── Cloud provider unavailable
   └── Generation timeout
```

Retrieval branch:

```text
Retrieving
   ├── Relevant context found
   └── Insufficient context
```

Artifact branch:

```text
Artifact request
   ├── Markdown generated
   ├── HTML generated
   └── Artifact error
```

## 14. Visual Hierarchy

Prioritize:

1. User's current question
2. Assistant answer
3. Supporting sources
4. Artifact content
5. Provider/status information
6. Secondary technical information

The interface should not make infrastructure details more prominent than the user's work.

## 15. Content Design

Use direct language.

Good:

> I couldn't find enough information in the Lenny podcast archive to answer that confidently.

Avoid:

> RAG retrieval threshold failure: no documents found.

Technical details belong in logs or developer documentation, not in normal user-facing copy.

## 16. Error UX

Errors should explain:

- What happened
- Whether the user's message was saved
- What they can try next

Example:

> Ollama is unavailable. Make sure Ollama is running and try again.

For cloud provider configuration:

> The cloud provider is not configured. Select Ollama or configure the required cloud API key.

## 17. Artifact Security UX

The UI should communicate that generated HTML is isolated.

A small indicator such as:

```text
Sandboxed Preview
```

helps users understand that the preview is deliberately separated from the main application.

Avoid exposing unnecessary security implementation details to normal users.

## 18. Design Trade-offs

### Two-Pane Workspace

Chosen because the assignment requires an in-product artifact experience and side-by-side interaction is efficient for comparing the conversation with generated work.

### Collapsible Artifact Pane

Chosen because not every question creates an artifact and chat should remain the primary workspace.

### Provider Badge

Chosen because provider selection is part of the evaluation and users need to know whether the local or cloud path is active.

### Source Visibility

Chosen because grounded answers are a central product promise and users should be able to understand why they can trust an answer.

## 19. Design Quality Checklist

Before release, verify:

- [ ] Empty state communicates value
- [ ] Chat is readable
- [ ] Streaming state is clear
- [ ] Sources are visible
- [ ] Provider is visible
- [ ] New session is easy to find
- [ ] Artifact viewer is discoverable
- [ ] Artifact viewer can collapse
- [ ] HTML preview is sandboxed
- [ ] Errors are understandable
- [ ] Keyboard interactions work
- [ ] Mobile layout does not overflow
- [ ] Buttons have accessible labels
- [ ] iframe has a meaningful title
