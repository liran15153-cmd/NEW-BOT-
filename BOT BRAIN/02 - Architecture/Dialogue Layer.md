---
type: system
status: current
source: code
---

# Dialogue Layer

The dialogue layer supports short clarification flows only.

## Current Behavior

- Stores pending intent state in memory.
- Uses `user_id` and `session_id`.
- Defaults missing `session_id` to `default:{user_id}`.
- Continues a pending intent when the next message provides missing parameters.
- Starts a new topic when a different supported intent is clear.
- Clears state after completion or when stale.

## Not Long-Term Memory

Conversation state is not user memory, financial history, or analytics storage. It is only a temporary mechanism for flows like:

`Can I buy this?` -> `What amount?` -> `400 shekels`.

## Continuation Rules

Continue state only when the new message provides missing information or clearly continues the same intent. If the new message clearly matches a different supported intent, the system should treat it as a new topic and clear or override the old pending state.

This matters because financial conversations are short and context-sensitive. A user might ask "Can I buy this?", then immediately ask "How much is left until salary?" The second message should not be forced into the purchase flow.

## State Safety

State should not store full answer text, raw financial histories, or long-term user facts. It stores only enough to continue the current clarification flow.

## Related Notes

- [[Request Response Flow]]
- [[Current Product Behavior]]
- [[Privacy Model]]
