# redrocket-market-kit

Language: [中文](README.md) | English

A read-only toolkit for Red Rocket public market data, focused on China index valuation, ETF and fund candidate discovery, related product lookup, and read-only fund profile context.

This project is a data connector and investment research helper. It does not trade, subscribe, redeem, convert, transfer money, or store personal holdings or account data.

## Status

Alpha. Red Rocket public endpoints may change. Outputs are only auxiliary context for valuation and product research; they are not investment advice and do not replace exchange quotes, fund company announcements, or sales platform rules.

## Installation

### Local Development

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -e '.[dev]'
```

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

## Install The Codex/Agent Skill

The CLI includes the `redrocket-market` skill and can install it into a local Agent/Codex skill directory:

```bash
redrocket init                       # installs to ~/.agents/skills/redrocket-market by default
redrocket init --client codex
redrocket init --dest ~/.agents/skills
redrocket init --print
redrocket init --uninstall
```

After installation, Codex can automatically use the skill when it needs valuation scans, ETF or fund candidate discovery, or Red Rocket data interpretation.

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
./.venv/bin/python -m pytest
./.venv/bin/ruff check .
./.venv/bin/python .github/scripts/validate_skill.py
./.venv/bin/python -m build
```

## Release Checklist

1. Update `CHANGELOG.md`.
2. Run tests, lint, skill validation, and package build.
3. Install the wheel in a clean environment and verify `redrocket init` installs the bundled skill.
4. Create a tag, for example `git tag v0.1.0`.
5. Push the tag and let GitHub Actions build the release artifacts.

See [docs/release.md](docs/release.md) for the full process.
