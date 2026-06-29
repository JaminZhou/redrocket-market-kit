# Release Process

1. Confirm `CHANGELOG.md` has the release entry.
2. Run local verification:

   ```bash
   python -m pytest
   ruff check .
   python .github/scripts/validate_skill.py
   python -m build
   ```

3. Verify a wheel install in a clean environment:

   ```bash
   python -m venv /tmp/redrocket-release-check
   /tmp/redrocket-release-check/bin/python -m pip install dist/redrocket_market_kit-*.whl
   /tmp/redrocket-release-check/bin/redrocket init --dest /tmp/redrocket-skills --force
   ```

4. Tag and push:

   ```bash
   git tag v0.1.0
   git push origin main --tags
   ```

5. GitHub Actions builds and uploads distributions. PyPI publishing requires trusted publishing to be configured for this repository.

