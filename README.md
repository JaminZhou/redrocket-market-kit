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
redrocket scan --preset theme --class-b 0219 --search-value AI --order desc --limit 5
redrocket etf --preset cross_border --limit 10
redrocket home --limit 5
redrocket search 110020 --all --limit 10
redrocket snapshot 000300.SH,931071.CSI,159819.SZ
redrocket related 000300.SH --security-type etf --limit 10
redrocket index 000300.SH --limit 10
redrocket components 000300.SH --limit 20
redrocket security-context 000300.SH --period 3M --limit 10
redrocket index-detail-plus 000300.SH --limit 10
redrocket etf-detail 510300.SH --limit 10
redrocket etf-flow 510300.SH --period 3M --limit 10
redrocket industry --index-code 980017.CNI --indicator-id 001004 --limit 5
redrocket fund 110020 --limit 10 --chart-date-type oneYear --benchmark-code 000300.SH
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

常用场景：

- `scan`：按宽基、消费、科技、策略、跨境等预设扫描估值表；可用 `--class-a`、`--class-b`、`--class-c` 和 `--search-value` 复用 `classes` 查到的分类码与关键词过滤。
- `etf`：扫描 ETF 候选；支持和 `scan` 相同的分类与关键词过滤参数。
- `home`：读取 PC 首页聚合的只读发现摘要，包括模块顺序、热度列表、指数阶段榜单、热股选基、焦点点位和“值得看”标题；不输出 banner/登录/积分/关注/反馈等个人态或写入内容。
- `search`：按代码或名称搜索指数、ETF、基金、股票等，并用公开批量快照接口补齐候选行的价格、涨跌幅、规模/关联信息等辅助字段；默认读取页面精简候选，`--all` 可请求红色火箭公开全量搜索结果。
- `snapshot`：读取多个指数、ETF、基金或股票的轻量价格/涨跌幅快照，并补充标的类型、交易所和延迟状态等元信息；仅作辅助观察。
- `related`：查某个指数的关联 ETF/场外基金，并显示 ETF/场外数量和头部候选摘要。
- `index`：读取指数档案、估值口径标签和 ROE 历史序列。
- `components`：读取指数或跟踪标的的全量成分股和权重快照。
- `security-context`：读取单个指数、ETF 或股票的页面运行时只读上下文，包括标的信息、近期变化、分时点、可选窗口走势图摘要、近 5 日分钟点和结构分布摘要；`--period` 可设置 `1M`、`3M`、`6M`、`1Y`、`3Y`、`5Y` 等公开图表窗口。
- `index-detail-plus`：读取指数估值序列、成分、行业分布、营收利润、风险收益和关联主基金。
- `etf-detail`：读取 ETF 档案、快照、阶段表现和份额/净申赎辅助数据。
- `etf-flow`：读取 ETF 净申赎、份额变化、近 5 日主力资金净流入、融资融券、联接基金和跟踪指数辅助数据。
- `industry`：读取 H5 行业页的行业列表、代表指数、相关指数、分类指标、指标详情、走势图和行业事件摘要；可用 `--index-code` 自动映射行业。
- `fund`：读取场外基金只读档案、销售状态、资产配置、净值曲线摘要和基金/基准业绩曲线摘要。
- `fund-notices`：读取场外基金近期公告；可用 `--detail-id` 查看单条公告附件链接。
- `manager`：读取基金经理只读详情和在管产品摘要。
- `quote`：读取红色火箭快照行情，仅作辅助，不作为实时行情主源。
- `heat`：读取首页市场热度列表和主要指数快照。
- `hot-timeline`：读取 H5 热门市场事件时间线的压缩事件行和最近交易日窗口，用于盘中/盘后市场脉络复核。
- `news`：读取“值得看”资讯/机会列表。
- `classes`：读取指数浏览器分类树，用于发现行业主题筛选 code。
- `focus-news`：读取盘中焦点新闻 metadata 和上证分时最新点，仅作辅助观察。
- `knowledge`：读取红色火箭知识库/方法说明文本，用于解释估值标签等页面口径。
- `article`：按 `news` / `must-read` 返回的 `statusId` 读取文章详情短摘录；默认截断，不做长正文镜像。
- `must-read`：读取某个标的的“有料必读”标题/标签/关联标的 metadata，不输出长正文。
- `wind`：读取指数风向标信号列表，仅作红色火箭方法论下的辅助观察。
- `signal-detail`：读取单个标的风向标详情摘要，保留评分、分项和关联产品，不输出巨量策略明细。
- `compare`：读取推荐指数对比组合；深层对比详情接口仍在参数稳定化中。
- `index-compare`：对指定指数读取档案、相似度、前十大权重股、市值分布、表现相关性、PEG 对比、区间涨跌幅、1 月对比走势图、盘中分钟对比图、行业分布、历史市场阶段、相关基金数量/规模和估值/ROE 数据时间。

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
- 指数、ETF、场外基金之间的关联查询，包括某个指数关联 ETF/场外基金的数量和头部候选摘要。
- 产品候选清单和低估线索发现，包括搜索候选和指定标的列表的批量快照辅助字段。
- PC 首页聚合的公开发现摘要，包括热度、指数阶段榜单、热股选基、焦点看盘和“值得看”标题。
- 基金只读档案、净值曲线摘要和基金/基准业绩曲线补充。
- 指数档案、估值序列、全量成分、行业分布、风险收益、走势图摘要、近 5 日分钟点和关联基金辅助核验。
- ETF 档案、净申赎、份额变化、近 5 日主力资金净流入、融资融券、联接基金和跟踪指数辅助观察。
- H5 行业页的代表指数、相关指数、分类指标、指标详情、走势图、行业事件摘要和指数到行业的只读映射。
- 场外基金公告和基金经理只读背景资料。
- 指数浏览器分类、焦点新闻、H5 热门事件时间线、知识库说明、“值得看”短摘录、“有料必读”标题、风向标详情和指数对比等红色火箭方法论下的辅助观察；指定指数对比可附带区间表现、1 月走势、盘中分钟走势、行业分布、历史市场阶段、相关基金数量/规模和估值/ROE 数据时间。

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
