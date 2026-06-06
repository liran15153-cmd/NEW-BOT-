---
type: concept
status: current
source: code
---

# Answer Plan

`assistant_answer_plan.py` builds a structured bridge between policy decisions and final answer wording.

## Purpose

The plan tells the response builder what kind of message to produce without embedding final Hebrew copy inside policy modules.

## Why Not Write The Answer Directly

Directly writing final copy in the policy layer would make safety behavior hard to audit and localize. The answer plan keeps policy structured while still giving the response builder enough direction to write the correct Hebrew message.

## Contents

- response type
- main message key
- structured numbers to include
- assumptions
- warnings
- missing fields
- forbidden claims
- required disclaimer keys
- tone

## Examples

Unsupported loan advice may produce a plan with `response_type = unsupported_request`, a main message key for unsupported financial advice, and forbidden claims such as `recommend_loan`.

Recurring expenses without transaction history may produce a plan with `response_type = ask_for_missing_data` and `missing_fields = ["transactions"]`.

## Boundary

The answer plan is not the answer. Final user-facing text belongs in [[Hebrew Response Builder]].

## Related Notes

- [[Assistant Response Policy]]
- [[Hebrew Response Builder]]
- [[Debug Metadata]]
