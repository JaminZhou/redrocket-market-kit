# Security Policy

## Supported Versions

Only the latest released version is supported during the alpha phase.

## Reporting a Vulnerability

Open a private security advisory or contact the maintainer privately. Do not include secrets, account identifiers, screenshots, cookies, or personal financial records in public issues.

## Data Boundary

This project should only call public read-only endpoints. It must not:

- Store personal holdings or account data.
- Persist bank or broker screenshots.
- Execute trades, subscriptions, redemptions, conversions, transfers, or confirmations.
- Ask users for credentials, cookies, verification codes, or identity documents.

