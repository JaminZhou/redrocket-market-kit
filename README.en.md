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
redrocket index 000300.SH --limit 10
redrocket components 000300.SH --limit 20
redrocket index-detail-plus 000300.SH --limit 10
redrocket etf-detail 510300.SH --limit 10
redrocket etf-flow 510300.SH --period 3M --limit 10
redrocket fund 110020 --limit 10
redrocket fund-notices 110020 --limit 5
redrocket manager 110020 --limit 5
redrocket quote 000300.SH,000688.SH
redrocket heat --limit 10
redrocket hot-timeline --limit 8
redrocket news --page 1 --limit 8
redrocket classes --search-value AI --limit 10
redrocket focus-news --limit 8
redrocket knowledge follw_valuation_tips fund_details_page_asset_allocation
redrocket article N2607011526280455070 --content-limit 240
redrocket must-read 000300.SH --limit 5
redrocket wind --limit 10
redrocket signal-detail 000300.SH --limit 5
redrocket compare --limit 8
redrocket index-compare 000300.SH:沪深300 000905.SH:中证500 --limit 10
```

Common commands:

- `scan`: scan valuation tables by presets such as broad market, consumer, technology, strategy, and cross-border.
- `etf`: scan ETF candidates.
- `search`: search indexes, ETFs, funds, stocks, and other securities by code or name.
- `related`: find ETFs or mutual funds related to an index.
- `index`: read an index profile, valuation labels, and recent ROE series.
- `components`: read full component-stock and weight snapshots for an index or tracked security.
- `index-detail-plus`: read index valuation series, components, industry distribution, revenue/profit, risk/return, and main related funds.
- `etf-detail`: read an ETF profile, quote snapshot, performance, and share-flow context.
- `etf-flow`: read ETF net subscription, share changes, margin data, linked fund, and tracking-index context.
- `fund`: read a mutual fund profile, sale status, and asset allocation.
- `fund-notices`: read recent mutual-fund announcements; use `--detail-id` for one announcement's attachment links.
- `manager`: read fund-manager detail rows and managed-security summaries.
- `quote`: read Red Rocket quote snapshots as auxiliary context only, not as the primary real-time market data source.
- `heat`: read the home market heat list and major index snapshots.
- `hot-timeline`: read compact H5 hot-market event timeline rows for intraday or post-close market context.
- `news`: read the worth-looking news/opportunity list.
- `classes`: read index-browser classification trees for industry/theme filter codes.
- `focus-news`: read compact focus-news metadata and the latest Shanghai Composite intraday point as auxiliary context.
- `knowledge`: read Red Rocket knowledge-base methodology/help text for labels such as valuation notes.
- `article`: read a compact article-detail excerpt by `statusId` returned from `news` or `must-read`; output is capped by default and is not a long-form article mirror.
- `must-read`: read must-read title/tag/related-security metadata for one security, without long article bodies.
- `wind`: read Red Rocket index wind-vane signal rows as methodology-specific auxiliary context.
- `signal-detail`: read compact wind-vane detail for one security, including scores, score details, and related product summary without huge strategy internals.
- `compare`: read recommended index comparison groups; deeper comparison detail endpoints still need stable parameter handling.
- `index-compare`: read stable explicit index comparison details such as archives, similarity, top holdings, market value, performance correlation, and PEG comparison.

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
- Index profiles, valuation series, full components, industry distribution, risk/return, and related-fund context.
- ETF profiles, net subscription, share changes, margin data, linked funds, and tracking-index context.
- Mutual-fund announcements and fund-manager background context.
- Red Rocket methodology-specific classification, focus-news, H5 hot-market timeline, knowledge-base notes, article excerpts, must-read title metadata, wind-vane detail, and index comparison context.

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
4. Create a tag, for example `git tag v0.1.1`.
5. Push the tag and let GitHub Actions build the release artifacts.

See [docs/release.md](docs/release.md) for the full process.
