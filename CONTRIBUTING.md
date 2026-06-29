# Contributing

This project is intentionally read-only. Contributions should preserve the boundary that the CLI never trades, redeems, subscribes, transfers, or confirms financial actions.

## Development

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -e '.[dev]'
./.venv/bin/python -m pytest
./.venv/bin/ruff check .
./.venv/bin/python -m build
```

## Pull Request Checklist

- Add tests for behavior changes.
- Keep output source-attributed with checked time and URL where decision-sensitive.
- Do not add personal holdings, account identifiers, screenshots, credentials, cookies, or tokens.
- Do not make Red Rocket the sole source for investment decisions.
- Run the full development command set before requesting review.

## Versioning

Use semantic versioning. Before tagging a release, update `CHANGELOG.md` and verify the bundled skill still installs with:

```bash
redrocket init --dest /tmp/redrocket-skills --force
```

