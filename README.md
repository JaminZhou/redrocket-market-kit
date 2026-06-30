# redrocket-market-kit

[![CI](https://github.com/JaminZhou/redrocket-market-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/JaminZhou/redrocket-market-kit/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/JaminZhou/redrocket-market-kit?sort=semver)](https://github.com/JaminZhou/redrocket-market-kit/releases)
[![Python](https://img.shields.io/badge/python-3.9--3.12-blue.svg)](pyproject.toml)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](CHANGELOG.md)
[![Agent Skill](https://img.shields.io/badge/Agent%20skill-Codex%20%2F%20Claude-111827.svg)](skills/redrocket-market/SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

语言：中文 | [English](README.en.md)

红色火箭公开数据的只读工具包，用于 A 股指数估值、ETF/基金候选发现、关联产品查询和基金只读档案整理。

这个项目是数据连接器和投研辅助工具，不做交易、不申购、不赎回、不转换、不转账，也不保存个人持仓或账户信息。

> 重要边界：本项目不是红色火箭官方项目，不提供实时行情主源，不构成投资建议，也不会执行任何交易、申购、赎回、转换、转账或确认动作。

## 当前状态

Alpha。红色火箭公开接口可能变化，输出只能作为估值和产品线索辅助，不构成投资建议，也不能替代交易所行情、基金公司公告或销售平台状态。

## 安装

### 本地开发

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

用于脚本或 CI 时，也可以不激活虚拟环境，直接使用 `./.venv/bin/python`。

### 从 Git 安装

```bash
pipx install git+https://github.com/JaminZhou/redrocket-market-kit.git
```

## CLI 用法

```bash
redrocket scan --preset wide --limit 5
redrocket scan --preset tech --order desc --limit 5
redrocket etf --preset cross_border --limit 10
redrocket search 110020
redrocket related 000300.SH --security-type etf --limit 10
redrocket fund 110020 --limit 10
redrocket quote 000300.SH,000688.SH
```

常用场景：

- `scan`：按宽基、消费、科技、策略、跨境等预设扫描估值表。
- `etf`：扫描 ETF 候选。
- `search`：按代码或名称搜索指数、ETF、基金、股票等。
- `related`：查某个指数的关联 ETF/场外基金。
- `fund`：读取场外基金只读档案。
- `quote`：读取红色火箭快照行情，仅作辅助，不作为实时行情主源。

## 安装 Agent Skill

CLI 内置了 `redrocket-market` skill，可以一条命令安装到本机 Agent、Codex 或 Claude 技能目录：

```bash
redrocket init                       # 默认安装到 $CODEX_HOME/skills 或 ~/.codex/skills
redrocket init --client agents       # 安装到 ~/.agents/skills
redrocket init --client claude       # 安装到 $CLAUDE_CONFIG_DIR/skills 或 ~/.claude/skills
redrocket init --dest ~/.agents/skills
redrocket init --print
redrocket init --uninstall
```

`--client codex` 使用 Codex 自身的 `CODEX_HOME` 约定；`--client agents`
使用兼容 Agent Skills 的开放用户目录；`--client claude` 使用 Claude Code
的 `CLAUDE_CONFIG_DIR` 约定，未设置时回落到 `~/.claude`。

安装后，支持 `SKILL.md` 的 Agent、Codex 或 Claude 环境可以在需要估值扫描、ETF/基金候选发现、红色火箭数据解释时使用该 skill。

## 数据边界

红色火箭适合作为：

- 估值分位和估值排行参考。
- 指数、ETF、场外基金之间的关联查询。
- 产品候选清单和低估线索发现。
- 基金只读档案补充。

红色火箭不适合作为：

- 盘中实时价格主源。
- 基金申购/赎回限额的唯一来源。
- 单一买卖、申购、赎回信号。
- 任何真实交易动作的执行工具。

决策敏感场景必须再核验交易所行情、基金公司公告、销售渠道规则和本地投资纪律。

## 开发

```bash
python -m pytest
ruff check .
python .github/scripts/validate_skill.py
python -m build
```

## 发布检查

1. 更新 `CHANGELOG.md`。
2. 运行测试、lint、skill 校验和 package build。
3. 用干净环境安装 wheel，验证 `redrocket init` 能安装内置 skill。
4. 打 tag，例如 `git tag v0.1.1`。
5. 推送 tag，由 GitHub Actions 构建发布产物。

完整流程见 [docs/release.md](docs/release.md)。
