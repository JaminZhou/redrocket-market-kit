# 更新日志

本项目的显著变化记录在这里。

## 未发布

- 修正 `index-detail-plus` 对行业分布日期桶的选择，优先匹配 `latestDate` 或可识别报告期标签，而不是依赖 JSON 字段顺序。

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
