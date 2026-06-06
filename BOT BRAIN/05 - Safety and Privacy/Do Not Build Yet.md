---
type: checklist
status: current
source: docs
---

# Do Not Build Yet

These systems are explicitly deferred. Do not add them just because they appear in roadmap notes.

## Deferred Infrastructure

- Supabase
- database models
- repositories
- CSV upload
- Open Banking
- WhatsApp
- real LLM provider
- provider adapters
- authentication
- frontend
- admin dashboard
- background jobs
- employer analytics
- long-term memory

## Why This List Exists

These features are not bad ideas. They are simply not the next bottleneck. The current bottleneck is whether the bot-brain behavior is clear, safe, and useful. Adding infrastructure too early would increase code surface, privacy risk, and debugging complexity before the product loop is proven.

## When Something Can Leave This List

A deferred item can become active only when there is a focused plan, explicit product behavior, privacy review where relevant, tests, and a clear integration boundary. "We will need it eventually" is not enough.

## Rule

Each deferred area needs its own plan, tests, privacy review, and architecture boundary before implementation.

## Related Notes

- [[Next Best Steps]]
- [[Future Data Sources]]
- [[WhatsApp Stage]]
- [[Real LLM Stage]]
