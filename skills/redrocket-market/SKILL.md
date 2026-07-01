---
name: redrocket-market
description: Use Red Rocket public read-only market data for China index valuation, ETF/fund discovery, related product lookup, and fund profile context. Trigger when the user asks for undervalued China market channels, Red Rocket data, index/fund/ETF valuation scans, or candidate discovery; do not use it as a primary real-time quote source or as a standalone trading signal.
---

# Redrocket Market

Use this skill to gather Red Rocket valuation and product-discovery context through the local `redrocket` CLI in this repository.

## Safety Rules

- Treat Red Rocket as an auxiliary source for valuation, fund/ETF discovery, index relationship mapping, and read-only fund context.
- Do not use Red Rocket as the primary real-time price source. Use a dedicated quote source for real-time trading-window checks.
- Do not convert Red Rocket output directly into a buy/sell/redeem recommendation. Cross-check with portfolio policy, live market data, fund公告/基金公司/销售平台 status, and user constraints.
- Never execute or click any trade, subscription, redemption, conversion, transfer, order, cancellation, or confirmation action.
- Include `checked_at`, source URL, and source limitations in user-facing investment analysis.

## Quick Commands

Run from the repository root:

```bash
redrocket scan --preset wide --limit 5
redrocket scan --preset tech --order desc --limit 5
redrocket etf --preset cross_border --limit 10
redrocket search 110020
redrocket related 000300.SH --security-type etf --limit 10
redrocket index 000300.SH --limit 10
redrocket components 000300.SH --limit 20
redrocket index-detail-plus 000300.SH --limit 10
redrocket etf-detail 510300.SH --limit 10
redrocket etf-flow 510300.SH --period 3M --limit 10
redrocket fund 110020 --limit 10
redrocket fund-notices 110020 --limit 5
redrocket manager 110020 --limit 5
redrocket quote 000300.SH,000688.SH
redrocket heat --limit 10
redrocket news --page 1 --limit 8
redrocket classes --search-value AI --limit 10
redrocket focus-news --limit 8
redrocket knowledge follw_valuation_tips fund_details_page_asset_allocation
redrocket article N2607011526280455070 --content-limit 240
redrocket must-read 000300.SH --limit 5
redrocket wind --limit 10
redrocket compare --limit 8
redrocket index-compare 000300.SH:沪深300 000905.SH:中证500 --limit 10
```

If the package is not installed, use:

```bash
python -m redrocket_market.cli scan --preset wide --limit 5
```

## Workflow

1. Identify whether the task is valuation scan, ETF/fund discovery, search, related products, index profile, full components, deeper index detail, ETF detail, ETF flow context, quote snapshot, fund profile, fund announcements, manager background, classification lookup, heat/news/focus/must-read/article context, knowledge-base methodology notes, wind-vane signals, or index comparisons.
2. Run the narrowest CLI command that answers the question.
3. Summarize useful candidates and explicitly label Red Rocket as an auxiliary source.
4. For any decision-sensitive conclusion, verify current market facts and fund/product constraints from stronger primary sources.

## Presets

- `wide`: broad market indexes.
- `theme`: industry/theme indexes.
- `consumption`: consumption indexes.
- `tech`: technology indexes.
- `strategy`: strategy/style indexes.
- `cross_border`: cross-border indexes.

## Output Discipline

Prefer concise Chinese summaries for Jamin:

- 先给结论。
- 区分事实、推断、待核验项。
- 标出不能验证的地方，不要假装没有变化。
- 对投资动作只给“复核条件/失效条件”，不写成直接下单指令。
