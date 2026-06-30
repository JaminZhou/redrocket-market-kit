# 贡献指南

这个项目坚持只读边界。任何贡献都不能让 CLI 执行交易、申购、赎回、转换、转账或确认动作。

## 开发环境

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
ruff check .
python .github/scripts/validate_skill.py
python -m build
```

## Pull Request 检查项

- 行为变化必须补测试。
- 决策敏感输出必须标明来源、检查时间和 URL。
- 不提交个人持仓、账户标识、截图、凭证、Cookie、Token 或验证码。
- 不把红色火箭作为唯一投资决策来源。
- 不增加任何真实交易、申购、赎回、转换、转账或确认能力。
- 提交前运行完整开发命令。

## 版本规则

使用语义化版本。打 tag 前更新 `CHANGELOG.md`，并验证内置 skill 能从 CLI 安装：

```bash
redrocket init --dest /tmp/redrocket-skills --force
```
