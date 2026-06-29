# redrocket-market-kit

Read-only Red Rocket market data toolkit for China index, ETF, fund, and valuation context.

This project is a connector and decision-support utility. It does not trade, submit orders, redeem funds, or store personal holdings.

## Status

Alpha. Public Red Rocket endpoints may change without notice. Treat output as auxiliary market context, not investment advice.

## Install

### Local development

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -e '.[dev]'
```

### From Git

```bash
pipx install git+https://github.com/JaminZhou/redrocket-market-kit.git
```

## CLI

```bash
redrocket scan --preset wide --limit 5
redrocket scan --preset tech --order desc --limit 5
redrocket etf --preset cross_border --limit 10
redrocket search 110020
redrocket related 000300.SH --security-type etf --limit 10
redrocket fund 110020 --limit 10
redrocket quote 000300.SH,000688.SH
```

### Install the bundled Codex/agent skill

```bash
redrocket init                       # installs to ~/.agents/skills/redrocket-market
redrocket init --client codex
redrocket init --dest ~/.agents/skills
redrocket init --print
redrocket init --uninstall
```

Use Red Rocket for valuation context, fund/ETF discovery, related product lookup, and read-only fund profiles. Do not use it as the primary real-time price source or as a single trading signal.

## Codex Skill

The skill lives in `skills/redrocket-market/`. Install or symlink it into your Codex skills folder when you want Codex to use this toolkit as a reusable capability.

## Development

```bash
./.venv/bin/python -m pytest
./.venv/bin/ruff check .
./.venv/bin/python -m build
```

## Release checklist

1. Update `CHANGELOG.md`.
2. Run tests, lint, skill validation, and package build.
3. Tag the release, for example `git tag v0.1.0`.
4. Publish from CI or upload the built distribution.

See [docs/release.md](docs/release.md) for the full release process.
