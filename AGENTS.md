# Agent Instructions

## Communication

- Use Chinese by default when working with Chinese project docs or Chinese user requests.
- Keep `README.md` and `README.en.md` conceptually aligned when changing public-facing behavior.

## Safety Boundaries

- This project is read-only. Do not add code paths that execute, automate, or confirm trades, subscriptions, redemptions, conversions, transfers, order placement, order cancellation, payments, or account actions.
- Do not persist personal holdings, account identifiers, bank or brokerage screenshots, credentials, cookies, tokens, verification codes, or identity documents.
- Treat Red Rocket data as auxiliary valuation and product-discovery context, not as a primary real-time quote source, official fund limit source, or standalone investment signal.
- Decision-sensitive outputs must label source limits and say what still needs verification from exchange data, fund company announcements, sales channel rules, or local investment policy.

## Development Checks

Before submitting changes that touch Python code, CLI behavior, package metadata, skills, or release flow, run:

```bash
python -m pytest
ruff check .
python .github/scripts/validate_skill.py
python -m build
```

For skill changes, also run the local skill validator when available:

```bash
python /Users/JaminZhou/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/redrocket-market
```

## Documentation Rules

- Keep the skill positioning agent-neutral: Agent/Codex/Claude, not Codex-only.
- Keep financial disclaimers visible in README and skill-facing docs.
- Do not add badges, templates, or docs that imply official Red Rocket affiliation, regulated investment advice, or execution capability.
