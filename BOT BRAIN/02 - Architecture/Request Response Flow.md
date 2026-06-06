---
type: system
status: current
source: code
---

# Request Response Flow

The main runtime path is `POST /chat/message`.

## Flow

1. FastAPI validates `ChatMessageRequest`.
2. [[Chat Router]] resolves the session ID.
3. [[Assistant Intent Classifier]] classifies policy-level intent.
4. [[Financial Intent Parser]] classifies executable financial intent.
5. [[Parameter Extractor]] extracts amount, currency, and months.
6. [[Dialogue Layer]] resolves whether this is a new turn, continuation, or new-topic override.
7. Unsupported or non-executable assistant intents go through [[Assistant Response Policy]] and [[Answer Plan]].
8. Executable intents with complete parameters call [[Financial Tool Executor]].
9. [[Financial Decision Engine]] returns structured decisions.
10. [[Hebrew Response Builder]] returns the typed response.

## Important Branches

Policy-only branch: privacy questions, unsupported advice, and future-feature requests are answered through policy and answer planning. They should not call financial tools.

Missing-data branch: purchase and installment requests with missing parameters save temporary dialogue state and return `needs_more_info`.

Executable branch: complete cashflow, purchase, and installment requests execute structured demo tools and pass the result into the decision engine.

Unknown branch: unsupported unknown messages return a safe fallback and do not execute tools.

## What Can Go Wrong

If intent classification is too broad, unsafe requests can execute tools. If parameter extraction is too permissive, negative or malformed amounts can be treated as valid. If dialogue continuation is too aggressive, a new topic can be forced into the old pending intent. Each risk has tests and should stay covered.

## Non-Execution Rules

Unknown, missing-field, privacy, unsupported-advice, and future-feature requests do not execute financial tools.

## Related Notes

- [[System Map]]
- [[Debug Metadata]]
- [[Financial Contracts]]
