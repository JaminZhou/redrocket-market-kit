# redrocket-market-kit

[![CI](https://github.com/JaminZhou/redrocket-market-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/JaminZhou/redrocket-market-kit/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/JaminZhou/redrocket-market-kit?sort=semver)](https://github.com/JaminZhou/redrocket-market-kit/releases)
[![Python](https://img.shields.io/badge/python-3.9--3.12-blue.svg)](pyproject.toml)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](CHANGELOG.md)
[![Agent Skill](https://img.shields.io/badge/Agent%20skill-Codex%20%2F%20Claude-111827.svg)](skills/redrocket-market/SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Language: [中文](README.md) | English

A read-only toolkit for Red Rocket public market data, focused on China index valuation, ETF and fund candidate discovery, related product lookup, and read-only fund profile context.

This project is a data connector and investment research helper. It does not trade, subscribe, redeem, convert, transfer money, or store personal holdings or account data.

> Important boundary: this is not an official Red Rocket project, does not provide a primary real-time quote source, is not investment advice, and will not execute any trade, subscription, redemption, conversion, transfer, or confirmation action.

## Status

Alpha. Red Rocket public endpoints may change. Outputs are only auxiliary context for valuation and product research; they are not investment advice and do not replace exchange quotes, fund company announcements, or sales platform rules.

## Installation

### Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

For scripts or CI, you can skip activation and call `./.venv/bin/python` directly.

### Install From Git

```bash
pipx install git+https://github.com/JaminZhou/redrocket-market-kit.git
```

## CLI Usage

```bash
redrocket scan --preset wide --limit 5
redrocket scan --preset tech --order desc --limit 5
redrocket etf --preset cross_border --limit 10
redrocket search 110020
redrocket related 000300.SH --security-type etf --limit 10
redrocket fund 110020 --limit 10
redrocket quote 000300.SH,000688.SH
```

Common commands:

- `scan`: scan valuation tables by presets such as broad market, consumer, technology, strategy, and cross-border.
- `etf`: scan ETF candidates.
- `search`: search indexes, ETFs, funds, stocks, and other securities by code or name.
- `related`: find ETFs or mutual funds related to an index.
- `fund`: read a mutual fund profile.
- `quote`: read Red Rocket quote snapshots as auxiliary context only, not as the primary real-time market data source.

## Install The Agent Skill

The CLI includes the `redrocket-market` skill and can install it into a local Agent, Codex, or Claude skill directory:

```bash
redrocket init                       # installs to $CODEX_HOME/skills or ~/.codex/skills by default
redrocket init --client agents       # installs to ~/.agents/skills
redrocket init --client claude       # installs to $CLAUDE_CONFIG_DIR/skills or ~/.claude/skills
redrocket init --dest ~/.agents/skills
redrocket init --print
redrocket init --uninstall
```

Use `--client codex` for Codex-native installs that follow `CODEX_HOME`, use
`--client agents` for the open Agent Skills user directory, and use
`--client claude` for Claude Code installs that follow `CLAUDE_CONFIG_DIR` when
it is set.

After installation, Agent, Codex, or Claude environments that support `SKILL.md` can use the skill for valuation scans, ETF or fund candidate discovery, or Red Rocket data interpretation.

## Data Boundaries

Red Rocket is useful for:

- Valuation percentile and valuation ranking context.
- Related index, ETF, and mutual fund lookup.
- Product candidate lists and low-valuation leads.
- Read-only fund profile enrichment.

Red Rocket is not suitable as:

- The primary source for intraday real-time prices.
- The sole source for fund subscription or redemption limits.
- A standalone buy, sell, subscribe, or redeem signal.
- A tool for executing any real trading action.

Decision-sensitive workflows must still verify exchange quotes, fund company announcements, sales channel rules, and local investment discipline.

## Development

```bash
python -m pytest
ruff check .
python .github/scripts/validate_skill.py
python -m build
```

## Release Checklist

1. Update `CHANGELOG.md`.
2. Run tests, lint, skill validation, and package build.
3. Install the wheel in a clean environment and verify `redrocket init` installs the bundled skill.
4. Create a tag, for example `git tag v0.1.0`.
5. Push the tag and let GitHub Actions build the release artifacts.

See [docs/release.md](docs/release.md) for the full process.
