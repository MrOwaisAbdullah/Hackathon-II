# ChatKit Protocol Reference

This document details the communication protocol between the ChatKit JS frontend and the Custom Backend.

## Streaming Format

ChatKit uses **NDJSON** (Newline Delimited JSON) over a standard HTTP stream (SSE-like but sent as standard POST response).

Each line in the stream is a JSON object representing an event.

## Event Types

### 1. `text`
Used to stream text chunks to the UI.

```json
{"type": "text", "content": "Hello"}
{"type": "text", "content": " world!"}
```

### 2. `widget`
Used to render complex UI elements (cards, forms, etc.).

```json
{
  "type": "widget",
  "widget": {
    "type": "card",
    "title": "Search Result",
    "content": "This is a summary retrieved via RAG."
  }
}
```

### 3. `status`
Updates the status indicator in the chat UI.

```json
{"type": "status", "status": "Searching documentation..."}
```

## Backend API Endpoints

### `POST /chatkit/sessions`
**Request**: Optional user metadata or auth headers.
**Response**:
```json
{
  "sessionId": "string",
  "clientToken": "string"
}
```

### `POST /chatkit/respond`
**Request**:
```json
{
  "message_id": "string",
  "thread_id": "string",
  "session_id": "string"
}
```
**Response**: A stream of NDJSON events.

## Message Store Schema (Internal)

If using the default `Store` from `chatkit.store`:
- `sessions`: `id`, `user_id`, `created_at`
- `threads`: `id`, `session_id`, `created_at`
- `messages`: `id`, `thread_id`, `role`, `content`, `created_at`
