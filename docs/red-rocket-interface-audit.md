# 红色火箭页面与接口审计

检查时间：2026-07-01

本文件记录通过 Chrome 页面探索和无 Cookie、无个人参数的公开请求核验到的红色火箭页面接口。它只作为维护 CLI 和 skill 的工程清单，不代表红色火箭官方接口文档。

## 安全边界

- 不保存浏览器 Cookie、Token、OpenID、用户 ID、加密参数或任何账户信息。
- 只封装可用公开接口的只读请求。
- 不封装任何交易、申购、赎回、转换、转账、下单、撤单或确认动作。
- 决策敏感场景仍需核验交易所行情、基金公司公告、销售渠道规则和本地投资纪律。

## 已封装接口

| 页面 | CLI | 接口 | 说明 |
| --- | --- | --- | --- |
| `/red-rocket/indexBrowser` | `scan` | `/fundex-quote/allPage/findListBySecurity` | 指数估值列表。 |
| `/red-rocket/indexBrowser` | `etf` | `/fundex-quote/allPage/findListByEtf` | ETF 列表；默认排序使用页面实际排序字段 `l.scale`。 |
| 搜索入口 | `search` | `/fundex-quote/search/list` | 证券/基金/指数搜索。 |
| 指数相关基金 | `related` | `/fundex-quote/indexRelated/allFund` | 指数关联 ETF/场外基金。 |
| 快照行情 | `quote` | `/fundex-quote/security/batchMinute` | 辅助行情快照，不作为实时主源。 |
| 场外基金档案 | `fund` | `/fundex-quote/fund/otcFundBase` | 基金基础档案。 |
| 场外基金档案 | `fund` | `/fundex-quote/fund/fundSituation` | 基金近况。 |
| 场外基金档案 | `fund` | `/fundex-quote/fund/otcFundComponentsList` | 基金持仓；需要 POST，查询参数为 `securityCode`。 |
| 场外基金档案 | `fund` | `/fundex-quote/fund/historyNetValue` | 历史净值。 |
| `/red-rocket/home` 与 `/red-rocket/hot` | `heat` | `/fundex-activity/opportunity/findHomeHeatV3` | 首页热度/机会列表和主要指数快照。 |
| `/red-rocket/beWorthLookList` | `news` | `/fundex-activity/opportunity/findHomeNews` | “值得看”资讯/机会分页列表。 |
| `/red-rocket/tool/indexWindVane` | `wind` | `/fundex-quote/signal/getOneLevelPage` | 指数风向标信号列表。 |
| `/red-rocket/tool/indexContrast` | `compare` | `/fundex-quote/compare/recommendCompareList` | 推荐指数对比组合。 |

## 已发现但暂不封装的接口

| 页面 | 接口 | 暂不封装原因 |
| --- | --- | --- |
| `/index/h5/fundexh5bai/hotMarket.html` | `/fundex-activity/hot/getList` | 裸请求返回空；页面请求带动态时间参数，后续需要稳定化参数生成。 |
| `/index/h5/fundexh5bai/hotMarket.html` | `/fundex-activity/hot/getFoldList` | 裸请求返回服务端异常；后续需要页面参数复现。 |
| `/index/h5/fundexh5bai/hotMarket.html` | `/fundex-activity/hot/getShowStatus` | 属于热榜展示状态，当前 CLI 尚无直接使用场景。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/index/archives` | 对比详情依赖已选指数列表参数。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/getMinuteChartWithCodes` | 对比详情图表接口，需稳定参数和输出结构。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/getChartWithCodes` | 对比详情图表接口，需稳定参数和输出结构。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/index/valuationData` | 对比估值详情，需稳定指数组合参数。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/index/valuationDetail` | 对比估值详情，需稳定指数组合参数。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/index/valuationGrowthRatio` | PEG/PB-ROE 等对比数据，需稳定指数组合参数。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/index/performanceCorrelation` | 投资表现相关性，需稳定指数组合参数。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/index/intervalChangePercent` | 区间涨跌幅，需稳定指数组合参数。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/index/compareTenWeightStock` | 十大权重股对比，部分参数错误时会 400。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/index/compareSimilarity` | 成分相似度，部分参数错误时会 400。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/component` | 成分对比，需稳定分页和指数组合参数。 |
| `/index/h5/fundexh5bai/idxSelection.html` | `/fundex-quote/compare/fundListCompare` | 相关基金对比，需稳定参数。 |

## 页面观察

- `/red-rocket/hot`、`/red-rocket/tool/indexContrast`、`/red-rocket/tool/indexWindVane` 的 PC 页面会嵌入 H5 页面或回到首页 shell；H5 接口和 PC shell 接口不是一套完整等价 API。
- `/red-rocket/indexBrowser` 的 ETF 表格与指数表格字段不同，ETF 默认排序不应沿用指数估值分位字段。
- `/red-rocket/beWorthLookList` 使用分页接口，返回 `groupList` 嵌套数组，CLI 会扁平化为资讯行。
- `wind` 输出来自红色火箭自身风向标方法论，只能作为发现和解释线索，不应当独立触发交易建议。
