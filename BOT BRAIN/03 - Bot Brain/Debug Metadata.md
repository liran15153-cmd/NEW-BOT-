---
type: concept
status: current
source: code
---

# Debug Metadata

Debug metadata helps tests and developers inspect the bot-brain path. It is not user-facing product behavior.

## Important Fields

- `session_id`
- `normalized_message`
- `matched_rule`
- `parameters`
- `active_intent_before`
- `active_intent_after`
- `state_continued`
- `state_cleared`
- `tool_executed`
- `risk_level`
- `reason_codes`
- assistant policy metadata such as assistant intent, response type, policy allowed, and blocked reason

## How To Use Debug Metadata

Debug metadata is the fastest way to understand why the bot answered the way it did. If `tool_executed` is false, inspect intent, response type, missing fields, and blocked reason. If `state_continued` is true, the answer came from a pending dialogue state. If risk level or reason codes are missing on an answered financial request, check tool execution and decision engine flow.

## What Not To Do

Do not expose raw debug output as product UI for end users. It may contain implementation details and internal classification labels. It belongs in tests, developer tools, and local tester panels.

## Rule

Product behavior must not depend on debug fields. Debug is observability for local testing and safety assertions.

## Related Notes

- [[Request Response Flow]]
- [[Testing Map]]
- [[Manual Tester QA]]
