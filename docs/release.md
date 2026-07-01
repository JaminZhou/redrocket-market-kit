# 发布流程

## 本地发布前检查

1. 确认 `CHANGELOG.md` 已写入本次版本变化。
2. 运行完整校验：

   ```bash
   python -m pytest
   ruff check .
   python .github/scripts/validate_skill.py
   python -m build
   ```

3. 用干净环境验证 wheel 安装和内置 skill 安装：

   ```bash
   python -m venv /tmp/redrocket-release-check
   /tmp/redrocket-release-check/bin/python -m pip install dist/redrocket_market_kit-*.whl
   /tmp/redrocket-release-check/bin/redrocket init --dest /tmp/redrocket-skills --force
   test -f /tmp/redrocket-skills/redrocket-market/SKILL.md
   CODEX_HOME=/tmp/redrocket-release-codex /tmp/redrocket-release-check/bin/redrocket init --client codex --force
   test -f /tmp/redrocket-release-codex/skills/redrocket-market/SKILL.md
   CLAUDE_CONFIG_DIR=/tmp/redrocket-release-claude /tmp/redrocket-release-check/bin/redrocket init --client claude --force
   test -f /tmp/redrocket-release-claude/skills/redrocket-market/SKILL.md
   ```

4. 确认没有提交个人资产数据、截图、凭证、Cookie、Token 或其他敏感内容。

## 打 tag

```bash
git tag vX.Y.Z
git push origin main --tags
```

## GitHub Actions

推送 `v*.*.*` tag 后，release workflow 会：

1. 安装依赖。
2. 运行测试、lint 和 skill 校验。
3. 构建 sdist/wheel。
4. 上传构建产物。
5. 如果仓库变量 `PYPI_PUBLISH=true` 且 PyPI trusted publishing 已配置，则发布到 PyPI。

默认不会发布到 PyPI，避免新仓库还没配置 PyPI 项目时 tag workflow 失败。PyPI 发布前需要先在 PyPI 项目里配置 trusted publishing，并在 GitHub 仓库变量中设置 `PYPI_PUBLISH=true`。
