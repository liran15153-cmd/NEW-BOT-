---
type: map
status: current
source: code
---

# System Map

The system is a deterministic bot-brain backend. A request enters through FastAPI, is routed through the AI orchestration layer, optionally continues short-lived dialogue state, executes financial tools only when safe, and returns a structured response with Hebrew user-facing text plus internal debug metadata.

## Primary Flow

`POST /chat/message` -> [[API Layer]] -> [[Chat Router]] -> [[Assistant Intent Classifier]] -> [[Financial Intent Parser]] -> [[Parameter Extractor]] -> [[Dialogue Layer]] -> [[Assistant Response Policy]] or [[Financial Tool Executor]] -> [[Financial Decision Engine]] -> [[Answer Plan]] -> [[Hebrew Response Builder]] -> response.

## Why The Flow Is Split

The system intentionally separates policy, parsing, state, financial facts, financial decisions, and final wording. This prevents one central module from quietly doing everything. A purchase question and a loan question may both contain the word "buy"; the assistant intent layer catches the loan-risk category before the executable financial path can accidentally run `simulate_purchase`.

The flow also keeps missing data safe. The bot should ask for an amount, installment count, or transaction history instead of making up a number. This matters more in financial wellness than in a casual chatbot because fake confidence can create real harm.

## Runtime Examples

For `Can I buy headphones for 400 shekels?`, the system classifies affordability, extracts `amount_minor = 40000`, executes the demo purchase tool, passes facts into the decision engine, and returns a Hebrew answer with `debug.tool_executed = true`.

For `Am I likely to enter overdraft before payday?`, the system classifies overdraft risk, executes the demo overdraft-risk tool, projects balance before salary, passes the facts into the decision engine, and returns a Hebrew answer with no invented live-bank data.

For `Should I take a loan to buy this?`, the system classifies unsupported loan advice, skips financial tools, and returns a safe policy response with `debug.tool_executed = false`.

## Hard Boundaries

- Missing-field requests do not execute financial tools.
- Unknown requests do not execute financial tools.
- Privacy and unsupported-advice requests do not execute financial tools.
- Financial tools return structured facts, not final wording.
- Final user-facing Hebrew copy belongs in [[Hebrew Response Builder]].

## Related Notes

- [[Request Response Flow]]
- [[Debug Metadata]]
- [[Safety Boundaries]]
- [[Testing Map]]
