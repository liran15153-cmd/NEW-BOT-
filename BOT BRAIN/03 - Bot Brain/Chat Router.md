---
type: system
status: current
source: code
---

# Chat Router

`app/ai/chat_router.py` is the orchestration center for `POST /chat/message`.

## Responsibilities

- resolve session ID
- run assistant-level and financial intent classifiers
- extract parameters
- load and update short-lived dialogue state
- route non-executable intents through policy responses
- execute financial tools only when required fields are present
- clear pending state after completion

## Router Decision Order

The router first checks the assistant-level intent because policy and safety may override normal financial execution. If the assistant intent is non-executable, the router builds a policy response and clears existing pending state when appropriate. Only executable intents continue into dialogue resolution and possible tool execution.

This order is important. If financial parsing ran the show, unsafe messages that contain purchase language could accidentally execute a purchase simulation.

## What To Watch When Editing

The router is tempting to use as a shortcut because every request passes through it. Resist that. If a change adds new keyword rules, edit the classifier or parser. If it changes wording, edit the response builder. If it changes risk, edit the decision engine.

## Forbidden Responsibilities

- regex parsing rules
- user-facing Hebrew answer text
- direct financial calculations
- external API calls
- database access
- long-term memory

## Related Notes

- [[Request Response Flow]]
- [[Assistant Intent Classifier]]
- [[Financial Tool Executor]]
- [[Dialogue Layer]]
