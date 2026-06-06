---
type: system
status: current
source: code
---

# API Layer

The API layer owns HTTP boundaries and should stay thin.

## Current Routes

- `app/api/chat_message_api.py`: `POST /chat/message`
- `app/api/health_check_api.py`: `GET /health`
- `app/api/local_tester_api.py`: `GET /tester`

## Responsibilities

- accept typed requests
- access app-level dependencies
- call the appropriate router or handler
- return typed responses or files

## Dependency Boundary

The app attaches replaceable dependencies to `app.state`: financial tools, conversation state store, and decision engine. This keeps tests isolated and avoids uncontrolled globals. API handlers should use these dependencies, not instantiate deep business logic themselves.

## Current API Contract

`POST /chat/message` accepts `user_id`, optional `session_id`, and `message`. It returns a structured response with answer, intent, status, tool execution metadata, missing fields, confidence, and debug metadata.

`GET /tester` serves the local tester. It is a manual QA surface, not a production frontend.

## Forbidden Responsibilities

- parsing intent
- extracting parameters
- calculating affordability
- managing dialogue state
- building user-facing financial answers

## Related Notes

- [[Chat Router]]
- [[Manual Tester QA]]
- [[Architecture Principles]]
