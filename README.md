# redrocket-market-kit

Read-only Red Rocket market data toolkit for China index, ETF, fund, and valuation context.

This project is a connector and decision-support utility. It does not trade, submit orders, redeem funds, or store personal holdings.

## Install

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -e '.[dev]'
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

Use Red Rocket for valuation context, fund/ETF discovery, related product lookup, and read-only fund profiles. Do not use it as the primary real-time price source or as a single trading signal.

## Codex Skill

The skill lives in `skills/redrocket-market/`. Install or symlink it into your Codex skills folder when you want Codex to use this toolkit as a reusable capability.

