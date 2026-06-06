---
type: system
status: current
source: code
---

# AI Layer

The AI layer is deterministic. It does not call an LLM.

## Current Modules

- `chat_router.py`: orchestration
- `assistant_intent_classifier.py`: policy-level intent classification
- `financial_intent_parser.py`: executable financial intent parsing
- `financial_parameter_extractor.py`: amount and installment extraction
- `assistant_response_policy.py`: safety and response-type decisions
- `assistant_answer_plan.py`: structured answer planning
- `hebrew_response_builder.py`: final Hebrew answer text
- `financial_tool_executor.py`: safe tool execution boundary
- `chat_message_schemas.py`: request, response, and debug schemas

## Core Boundary

The AI layer may decide how to route and phrase answers, but it must not invent financial numbers. Numbers must come from [[Financial Layer]].

## Naming Clarification

This layer is called `ai` because it owns assistant behavior, not because it currently calls an AI provider. Today it is deterministic and local. That is intentional. The goal is to establish safe assistant behavior before adding an LLM.

## Change Guidance

When adding behavior, first decide whether it is a policy concern, parsing concern, parameter concern, dialogue concern, or response wording concern. Then edit the smallest module that owns that concern. Avoid routing new behavior through one giant if-statement in `chat_router.py`.

## Current Internal Contract

The AI layer passes structured objects between modules: intent parse result, extracted parameters, policy decision, answer plan, tool execution result, and final chat response. Preserve that structured boundary.

## Related Notes

- [[Chat Router]]
- [[Assistant Response Policy]]
- [[Hebrew Response Builder]]
