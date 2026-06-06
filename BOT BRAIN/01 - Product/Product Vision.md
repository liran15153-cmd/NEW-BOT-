---
type: concept
status: current
source: docs
---

# Product Vision

The current product is a deterministic Hebrew financial wellness assistant backend. Its purpose is to prove the conversational core before adding real financial data, WhatsApp delivery, Supabase, Open Banking, authentication, a dashboard, or a real LLM.

## What It Should Feel Like

- private
- practical
- calm
- clear
- non-judgmental
- honest about uncertainty
- grounded in structured financial data

## Strategic Focus

The product should win by reducing anxiety and confusion around small financial decisions. It does not need to solve the entire financial life of a user in the first version. The stronger path is to make one conversation loop feel trustworthy: a user asks a concrete question, the bot knows what data it needs, the answer is practical, and the bot refuses unsafe requests cleanly.

This is why the current local deterministic backend is a good foundation. It forces the team to define behavior before hiding ambiguity behind an LLM or external integration.

## Product Anti-Pattern

The dangerous path is building integrations before the conversation is good. WhatsApp can make a weak bot easier to reach, but it will not make it more useful. Open Banking can provide data, but it raises the stakes for privacy and accuracy. An LLM can sound fluent, but it can also invent financial facts unless deterministic policy and tool boundaries are strong.

## What It Must Not Become Yet

It must not become a generic financial platform before the bot brain is strong. The next useful work is better deterministic behavior, richer scenarios, and stronger QA, not infrastructure expansion.

## Related Notes

- [[Current Product Behavior]]
- [[User Experience Principles]]
- [[Do Not Build Yet]]
- [[Next Best Steps]]
