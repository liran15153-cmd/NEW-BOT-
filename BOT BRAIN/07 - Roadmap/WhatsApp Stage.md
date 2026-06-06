---
type: roadmap
status: future
source: docs
---

# WhatsApp Stage

WhatsApp is a delivery channel, not the bot brain.

## Prerequisites

- stable `/chat/message` contract
- strong Hebrew manual QA
- clear privacy copy
- safe error handling
- decision on session mapping
- production-ready webhook verification
- no secrets exposed client-side

## Integration Shape

WhatsApp should be an adapter around the existing bot brain. It should translate WhatsApp webhook payloads into the internal chat request shape and translate the response back into WhatsApp messages. It should not contain business logic.

## Main Risks

- webhook retry behavior
- session mapping from phone numbers
- secret handling
- message formatting differences
- production observability
- user consent and privacy copy

## Recommended Approach

Use WhatsApp Cloud API when this stage becomes active. Avoid unofficial WhatsApp Web automation for a product that needs reliability.

## Related Notes

- [[Current Product Behavior]]
- [[Privacy Model]]
- [[Do Not Build Yet]]
