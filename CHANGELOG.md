# 更新日志

本项目的显著变化记录在这里。

## 未发布

- 修正多来源只读 CLI 命令的 Markdown 输出，逐条标注来源 endpoint，避免只显示第一条来源导致验证对象不完整。
- 增强 `related` 只读 CLI 命令，补充某个指数关联 ETF/场外基金的聚合数量和头部候选摘要。
- 新增 `home` 只读 CLI 命令，读取 PC 首页聚合发现摘要，包括模块顺序、热度、指数阶段榜单、热股选基、焦点点位和“值得看”标题。
- 增强 `security-context` 只读 CLI 命令，补充 1 年走势图摘要、最近图表点和近 5 日分钟点。
- 增强 `industry` 只读 CLI 命令，支持通过 `--index-code` 自动映射红色火箭行业 ID。
- 增强 `index-compare` 只读 CLI 命令，补充区间涨跌幅、区间赢家、1 月对比走势图、盘中分钟对比图、行业分布、历史市场阶段、相关基金数量/规模和估值/ROE 数据时间。
- 增强 `etf-flow` 只读 CLI 命令，补充近 5 日主力资金净流入摘要。
- 新增 `industry` 只读 CLI 命令，读取 H5 行业页的代表指数、相关指数、指标分类、指标详情、图表和纪要上下文。
- 新增 `snapshot` 只读 CLI 命令，读取多标的轻量价格/涨跌幅快照，并补充标的类型、交易所和延迟状态等元信息。
- 新增 `security-context` 只读 CLI 命令，读取单个指数、ETF 或股票页面运行时的标的信息、近期变化、分时点和结构分布摘要。
- 增强 `search` 只读 CLI 命令：按页面实际流程调用搜索列表后，再用公开批量快照接口富化候选表，输出指数、ETF、场外基金、股票的价格、涨跌幅、规模/关联信息等辅助字段。
- 新增 `hot-timeline` 只读 CLI 命令，读取 H5 热门市场事件时间线的压缩事件行，用于盘中/盘后市场脉络复核。
- 新增 `signal-detail` 只读 CLI 命令，读取单个标的的红色火箭风向标详情摘要；保留评分、分项和关联产品摘要，不输出巨量策略明细。
- 新增 `knowledge` 只读 CLI 命令，读取红色火箭知识库/方法说明文本，用于解释估值标签等页面口径。
- 新增 `article` 只读 CLI 命令，按 `statusId` 读取“值得看”文章详情短摘录；`news` 结果会从 `skipAddr` 提取 `statusId`，默认不输出长正文。

## 0.5.0 - 2026-07-01

- 新增 `classes`、`focus-news`、`must-read` 只读 CLI 命令，覆盖指数分类树、焦点新闻 metadata 和标的“有料必读”标题列表；不输出文章长正文。

## 0.4.0 - 2026-07-01

- 新增 `components`、`fund-notices`、`manager` 只读 CLI 命令，覆盖全量成分股、场外基金公告和基金经理背景资料。
- 修正 `fund-notices --detail-id` 的默认 Markdown 输出，展示公告详情和附件链接。

## 0.3.2 - 2026-07-01

- 修正 `index-detail-plus` 在缺少可用 `latestDate` 时对原始日期行业分布桶的排序，避免被较旧的中文报告期标签覆盖。

## 0.3.1 - 2026-07-01

- 修正 `index-detail-plus` 对行业分布日期桶的选择，优先匹配 `latestDate`、原始日期桶名或可识别报告期标签，而不是依赖 JSON 字段顺序。

## 0.3.0 - 2026-07-01

- 新增 `index-detail-plus`、`etf-flow`、`index-compare` 只读 CLI 命令，覆盖指数深层估值/成分/行业/风险收益、ETF 资金流/份额/融资融券、指定指数对比详情。
- 修正 `index-detail-plus` 对行业分布 `resultMap` 的兼容，保留直接行业映射和非“最新”日期桶数据。

## 0.2.0 - 2026-07-01

- 新增 `heat`、`news`、`wind`、`compare` 只读 CLI 命令，覆盖红色火箭首页热度、“值得看”、指数风向标和推荐对比组合。
- 新增 `index` 和 `etf-detail` 只读 CLI 命令，覆盖指数档案/ROE、ETF 档案/阶段表现/份额净申赎等研究上下文。
- 增强 `fund` 命令，补充场外基金销售状态和资产配置辅助信息。
- 修正 `etf` 默认排序字段，改为页面实际使用的 `l.scale`。
- 修正 `fund` 持仓接口，使用红色火箭页面实际的 POST `securityCode` 请求。

## 0.1.1 - 2026-06-30

- 修正 `redrocket init --client codex` 的安装目录，改为 `$CODEX_HOME/skills` 或 `~/.codex/skills`。
- 修正 `redrocket init --client claude` 的安装目录，支持 `CLAUDE_CONFIG_DIR`。
- 阻止自定义 `--dest` 覆盖或卸载项目内置的 `redrocket-market` skill。
- 将 skill 文档口径扩展为 Agent/Codex/Claude 通用安装口径，并补充 Claude 安装验证说明。
- 新增轻量开源治理文件，包括 `AGENTS.md`、`CLAUDE.md` 软链接、行为准则、issue templates、PR template 和 Dependabot 配置。
- 在 README 中前置非官方、非实时行情、非投资建议和不执行交易动作的边界提示。
- 升级 GitHub Actions 工作流依赖 `actions/checkout` 和 `actions/upload-artifact`。

## 0.1.0 - 2026-06-29

- 新增红色火箭只读 client，支持估值扫描、ETF 扫描、搜索、关联产品、行情快照和基金档案。
- 新增 `redrocket` CLI。
- 新增 `redrocket init`，支持安装、打印、卸载内置 Agent skill。
- 新增 `redrocket-market` Agent skill，明确数据来源限制和金融动作安全边界。
- 新增 CI、release workflow、贡献指南、安全策略和发布流程文档。
