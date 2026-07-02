from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from redrocket_market.client import PRESETS, RedRocketClient, RedRocketError
from redrocket_market.installer import (
    install_to_targets,
    print_skill,
    resolve_client_destinations,
    uninstall_from_targets,
)


def print_json(result: dict[str, Any]) -> None:
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cell(value: Any) -> str:
    if value in (None, ""):
        return "--"
    return str(value).replace("\n", " ")


def first_source(source: Any) -> str:
    if isinstance(source, dict):
        return cell(next(iter(source.values()), "--"))
    return cell(source)


def first_present(row: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def row_key_values(row: dict[str, Any], keys: list[str]) -> str:
    parts = [f"{key}={cell(row.get(key))}" for key in keys if row.get(key) not in (None, "")]
    return ", ".join(parts)


def security_structure_label(row: dict[str, Any]) -> str:
    return cell(
        first_present(
            row,
            [
                "name",
                "label",
                "marketValueName",
                "industryName",
                "securityName",
                "tradeDate",
                "annDate",
                "date",
            ],
        )
    )


def security_structure_value(row: dict[str, Any]) -> str:
    simple_value = first_present(
        row,
        ["weight", "proportion", "ratio", "value", "marketValue", "count"],
    )
    if simple_value not in (None, ""):
        return cell(simple_value)
    structure_summary = row_key_values(
        row,
        [
            "largeCapStockCount",
            "middleCapStockCount",
            "smallCapStockCount",
            "totalMarketValue",
            "avgMarketValue",
            "currencyCode",
            "cr5",
            "cr10",
            "cr20",
        ],
    )
    if structure_summary:
        return structure_summary
    return row_key_values(
        row,
        [
            key
            for key in row
            if key
            not in {
                "name",
                "label",
                "marketValueName",
                "industryName",
                "securityName",
                "tradeDate",
                "annDate",
                "date",
            }
        ],
    ) or "--"


def parse_index_info(value: str) -> tuple[str, str]:
    text = value.strip()
    for separator in (":", "-"):
        if separator in text:
            code, name = text.split(separator, 1)
            code = code.strip()
            name = name.strip()
            return code, name or code
    return text, text


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def summarize_risk_cell(value: Any) -> str:
    if not isinstance(value, dict):
        return cell(value)
    parts = [
        f"sharpe {cell(value.get('sharpRation'))}",
        f"volatility {cell(value.get('volatility'))}",
    ]
    if value.get("tradeDate"):
        parts.append(f"date {cell(value.get('tradeDate'))}")
    return ", ".join(parts)


def print_table(result: dict[str, Any]) -> None:
    print(f"# Red Rocket {result['kind']} ({result['fetched_at']})")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    rows = result.get("rows") or []
    if not rows:
        print("\n无结果。")
        return
    keys = sorted({key for row in rows for key in row.keys()})
    preferred = [
        "id",
        "statusId",
        "securityCode",
        "securityType",
        "securityName",
        "securityFullName",
        "names",
        "codes",
        "fundCode",
        "fundName",
        "title",
        "announceTime",
        "name",
        "employmentPeriod",
        "fundCompany",
        "price",
        "dayChangePercent",
        "yearChangePercent",
        "changePercent",
        "relatedFundScale",
        "trackingIndex",
        "componentStockCount",
        "relatedFundCount",
        "marketValue",
        "industryInvolved",
        "weight",
        "pePercent",
        "pbPercent",
        "score",
        "scoreLabel",
        "valuation",
        "performanceChangePercent",
        "fundScale",
        "rate",
    ]
    columns = [key for key in preferred if key in keys] + [key for key in keys if key not in preferred]
    columns = columns[:8]
    print()
    print("| " + " | ".join(columns) + " |")
    print("| " + " | ".join(["---"] * len(columns)) + " |")
    for row in rows:
        print("| " + " | ".join(cell(row.get(key)) for key in columns) + " |")


def print_home(result: dict[str, Any]) -> None:
    print(f"# Red Rocket home ({result['fetched_at']})")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    classes = result.get("classes") or []
    if classes:
        class_text = "; ".join(
            f"{cell(row.get('value'))} {cell(row.get('label'))}"
            for row in classes
            if isinstance(row, dict)
        )
        print(f"- Classes: {class_text}")
    modules = result.get("modules") or []
    if modules:
        print("\n## Modules")
        for row in modules:
            print(
                "- "
                f"{cell(row.get('key'))}: {cell(row.get('title') or row.get('name'))} "
                f"state {cell(row.get('state'))}"
            )
    heat = result.get("heat") or []
    if heat:
        print("\n## Heat")
        for row in heat:
            print(
                "- "
                f"{cell(row.get('securityCode'))} {cell(row.get('securityName'))}: "
                f"{cell(row.get('changePercent'))}% "
                f"date {cell(row.get('tradeDate'))}"
            )
    spectrum = result.get("spectrum") or {}
    if spectrum:
        print("\n## Index Spectrum")
        for period, rows in spectrum.items():
            values = [
                f"{cell(row.get('indexCode'))} {cell(row.get('indexName'))} {cell(row.get('changePercent'))}%"
                for row in rows
                if isinstance(row, dict)
            ]
            print(f"- {period}: {'; '.join(values) or '--'}")
    stock_funds = result.get("stock_funds") or []
    if stock_funds:
        print("\n## Hot Stock Funds")
        for row in stock_funds:
            stocks = row.get("stocks") if isinstance(row.get("stocks"), list) else []
            stock_text = "; ".join(
                f"{cell(stock.get('securityCode'))} {cell(stock.get('securityName'))} {cell(stock.get('proportion'))}%"
                for stock in stocks
                if isinstance(stock, dict)
            )
            print(
                "- "
                f"{cell(row.get('securityCode'))} {cell(row.get('securityName'))}: "
                f"{cell(row.get('changePercent'))}%, "
                f"top stocks {stock_text or '--'}"
            )
    focus = result.get("focus") or {}
    latest = focus.get("latest_point") if isinstance(focus, dict) else {}
    if latest:
        print(
            "\n## Focus\n"
            f"- Latest point: {cell(latest.get('minuteByHours'))} "
            f"{cell(latest.get('price'))} {cell(latest.get('changePercent'))}%"
        )
    news = result.get("news") or []
    if news:
        print("\n## News")
        for row in news:
            print(
                "- "
                f"{cell(row.get('statusId'))} "
                f"{cell(row.get('title'))}: "
                f"{cell(row.get('securityName'))} "
                f"{cell(row.get('valuation'))}"
            )


def print_snapshot(result: dict[str, Any]) -> None:
    print(f"# Red Rocket snapshot ({result['fetched_at']})")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    rows = result.get("rows") or []
    if not rows:
        print("\n无结果。")
        return
    keys = {key for row in rows for key in row.keys()}
    preferred = [
        "securityCode",
        "securityType",
        "securityExchmarket",
        "securityName",
        "price",
        "changePercent",
        "tradeDate",
        "isDelay",
        "quoteInit",
        "follow",
    ]
    columns = [key for key in preferred if key in keys]
    print()
    print("| " + " | ".join(columns) + " |")
    print("| " + " | ".join(["---"] * len(columns)) + " |")
    for row in rows:
        print("| " + " | ".join(cell(row.get(key)) for key in columns) + " |")


def print_fund(result: dict[str, Any]) -> None:
    print(f"# Red Rocket fund ({result['fetched_at']})")
    print(f"- Fund: {result['fund_code']}")
    print(f"- Source: {result['source']['base']}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    base = result.get("base") or {}
    situation = result.get("situation") or {}
    for label, value in [
        ("Name", situation.get("fundFullName") or base.get("fundName")),
        ("Type", situation.get("fundType") or base.get("fundType")),
        ("Manager", situation.get("fundManager") or base.get("fundManager")),
        ("Company", situation.get("fundCompany") or base.get("fundCompany")),
        ("Net value", situation.get("netValue")),
        ("Net value date", situation.get("netValueDate")),
    ]:
        print(f"- {label}: {cell(value)}")
    if result.get("nav"):
        print("\n## Recent NAV")
        for row in result["nav"][:5]:
            print(f"- {cell(row)}")
    nav_chart = result.get("nav_chart") if isinstance(result.get("nav_chart"), dict) else {}
    if nav_chart:
        print("\n## NAV Chart")
        print(
            "- "
            f"{cell(nav_chart.get('firstDate'))}~{cell(nav_chart.get('lastDate'))}: "
            f"{cell(nav_chart.get('firstValue'))} -> {cell(nav_chart.get('lastValue'))}, "
            f"change {cell(nav_chart.get('changePercent'))}%, "
            f"points {cell(nav_chart.get('points'))}"
        )
    performance_chart = (
        result.get("performance_chart")
        if isinstance(result.get("performance_chart"), dict)
        else {}
    )
    fund_chart = (
        performance_chart.get("fund")
        if isinstance(performance_chart.get("fund"), dict)
        else {}
    )
    benchmark_chart = (
        performance_chart.get("benchmark")
        if isinstance(performance_chart.get("benchmark"), dict)
        else {}
    )
    if fund_chart or benchmark_chart:
        print("\n## Performance Chart")
        if fund_chart:
            print(
                "- Fund: "
                f"{cell(fund_chart.get('firstDate'))}~{cell(fund_chart.get('lastDate'))}, "
                f"change {cell(fund_chart.get('changePercent'))}%, "
                f"points {cell(fund_chart.get('points'))}"
            )
        if benchmark_chart:
            print(
                "- Benchmark "
                f"{cell(performance_chart.get('defaultExponentCode'))} "
                f"{cell(performance_chart.get('defaultExponentName'))}: "
                f"{cell(benchmark_chart.get('firstDate'))}~{cell(benchmark_chart.get('lastDate'))}, "
                f"change {cell(benchmark_chart.get('changePercent'))}%, "
                f"points {cell(benchmark_chart.get('points'))}"
            )
    if result.get("sale_status"):
        print("\n## Sale Status")
        for key, value in result["sale_status"].items():
            print(f"- {key}: {cell(value)}")
    if result.get("asset_allocation"):
        print("\n## Asset Allocation")
        for row in result["asset_allocation"][:5]:
            print(f"- {cell(row.get('assetName'))}: {cell(row.get('assetVal'))}")


def print_fund_notices(result: dict[str, Any]) -> None:
    print(f"# Red Rocket fund notices ({result['fetched_at']})")
    print(f"- Fund: {result['fund_code']}")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")

    rows = result.get("rows") or []
    if rows:
        print("\n## Notices")
        for row in rows:
            print(
                "- "
                f"{cell(row.get('announceTime'))} "
                f"{cell(row.get('title'))} "
                f"({cell(row.get('id'))})"
            )
    else:
        print("\n无结果。")

    detail = result.get("detail") or {}
    if not detail:
        return

    print("\n## Detail")
    for label, value in [
        ("ID", detail.get("id")),
        ("Title", detail.get("title")),
        ("Announce time", detail.get("announceTime")),
    ]:
        print(f"- {label}: {cell(value)}")

    attachments = detail.get("attachmentUrls") or []
    if attachments:
        print("- Attachments:")
        for attachment in attachments:
            print(f"  - {cell(attachment)}")


def print_index(result: dict[str, Any]) -> None:
    print(f"# Red Rocket index ({result['fetched_at']})")
    print(f"- Index: {result['security_code']}")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    summary = result.get("summary") or {}
    labels = result.get("labels") or {}
    for label, value in [
        ("Name", summary.get("securityName")),
        ("Publisher", summary.get("publisher")),
        ("Components", summary.get("componentCount")),
        ("ETF count", summary.get("etfCount")),
        ("OTC count", summary.get("otcCount")),
        ("Scale", summary.get("scale")),
        ("Valuation type", labels.get("valuationTypeLabel")),
    ]:
        print(f"- {label}: {cell(value)}")
    if result.get("roe"):
        print("\n## Recent ROE")
        for row in result["roe"][:5]:
            print(f"- {cell(row.get('date'))}: {cell(row.get('value'))}")


def print_index_detail_plus(result: dict[str, Any]) -> None:
    print(f"# Red Rocket index detail+ ({result['fetched_at']})")
    print(f"- Index: {result['security_code']}")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    valuation = result.get("valuation") or {}
    risk_return = result.get("risk_return") or {}
    for label, value in [
        ("Valuation", valuation.get("valuation")),
        ("Valuation percentile", valuation.get("valuationQuantileNew")),
        ("PEG", valuation.get("peg")),
        ("1Y return", risk_return.get("lastOneYearReturn")),
        ("3Y return", risk_return.get("lastThreeYearReturn")),
        ("Component report date", result.get("component_report_date")),
    ]:
        if label in {"1Y return", "3Y return"}:
            print(f"- {label}: {summarize_risk_cell(value)}")
        else:
            print(f"- {label}: {cell(value)}")
    if result.get("components"):
        print("\n## Components")
        for row in result["components"][:5]:
            name = (
                row.get("componentName")
                or row.get("securityName")
                or row.get("stockName")
                or row.get("industriesName")
            )
            code = (
                row.get("componentCode")
                or row.get("securityCode")
                or row.get("stockCode")
                or row.get("industriesCode")
            )
            weight = row.get("weight") or row.get("proportion") or row.get("value")
            print(f"- {cell(name)} ({cell(code)}): {cell(weight)}")
    main_fund = result.get("main_fund") or {}
    etfs = main_fund.get("etf") if isinstance(main_fund.get("etf"), list) else []
    if etfs:
        print("\n## Main ETFs")
        for row in etfs[:5]:
            name = row.get("fundName") or row.get("securityType")
            value = row.get("fundCode")
            if value in (None, ""):
                value = f"count {cell(row.get('totalNumber'))}, scale {cell(row.get('totalScale'))}"
            print(f"- {cell(name)}: {cell(value)}")


def print_security_context(result: dict[str, Any]) -> None:
    print(f"# Red Rocket security context ({result['fetched_at']})")
    print(f"- Security: {result['security_code']}")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    info = result.get("info") or {}
    for label, value in [
        ("Name", info.get("securityName")),
        ("Type", info.get("securityType")),
        ("Count", info.get("securityCount")),
        ("Price", info.get("lastPrice") or info.get("price")),
        ("Change percent", info.get("changePercent")),
        ("Market", info.get("marketTip") or info.get("marketType")),
    ]:
        print(f"- {label}: {cell(value)}")
    latest_minute = (result.get("minute_rows") or [])[-1:] or []
    if latest_minute:
        row = latest_minute[0]
        print(
            "- Latest minute: "
            f"{cell(row.get('minute') or row.get('minuteByHours') or row.get('time'))} "
            f"{cell(row.get('price') or row.get('lastPrice'))} "
            f"{cell(row.get('changePercent'))}%"
        )
    if result.get("change_rows"):
        print("\n## Recent Changes")
        for row in result["change_rows"][:5]:
            print(
                "- "
                f"{cell(row.get('tradeDate') or row.get('date'))}: "
                f"{cell(row.get('price') or row.get('lastPrice'))}, "
                f"{cell(row.get('changePercent'))}%"
            )
    chart = result.get("chart") or {}
    if chart:
        print("\n## Chart")
        for label, key in [("Security", "security"), ("Benchmark", "benchmark")]:
            row = chart.get(key) if isinstance(chart.get(key), dict) else {}
            if not row:
                continue
            performance = row.get("performance") if isinstance(row.get("performance"), dict) else {}
            print(
                f"- {label}: "
                f"{cell(row.get('securityCode'))} {cell(row.get('securityName'))} "
                f"points {cell(row.get('itemsSize'))} "
                f"yearly {cell(performance.get('yearlyPerformance'))}"
            )
    chart_rows = result.get("chart_rows") or []
    if chart_rows:
        print("\n## Chart Rows")
        for row in chart_rows[:5]:
            print(
                "- "
                f"{cell(row.get('tradeDate') or row.get('date'))}: "
                f"{cell(row.get('intervalChangePercent'))} "
                f"vs benchmark {cell(row.get('benchmarkIntervalChangePercent'))}"
            )
    five_day_rows = result.get("five_day_minute_rows") or []
    if five_day_rows:
        print("\n## 5D Minute")
        for row in five_day_rows[:5]:
            print(
                "- "
                f"{cell(row.get('tradeDate'))} "
                f"{cell(row.get('minuteByHours') or row.get('time'))}: "
                f"{cell(row.get('price'))} "
                f"{cell(row.get('changePercent'))}%"
            )
    for title, key in [
        ("History Position", "history_position"),
        ("Market Value Distribution", "market_value_distribution"),
        ("Weight Concentration", "weight_concentration"),
    ]:
        rows = result.get(key) or []
        if not rows:
            continue
        print(f"\n## {title}")
        for row in rows[:5]:
            print(f"- {security_structure_label(row)}: {security_structure_value(row)}")


def print_etf_detail(result: dict[str, Any]) -> None:
    print(f"# Red Rocket ETF detail ({result['fetched_at']})")
    print(f"- ETF: {result['security_code']}")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    quote = result.get("quote") or {}
    profile = result.get("profile") or {}
    subscription = result.get("subscription") or {}
    for label, value in [
        ("Name", quote.get("securityName") or profile.get("securityName")),
        ("Price", quote.get("lastPrice") or quote.get("price")),
        ("Change percent", quote.get("changePercent")),
        ("Market", quote.get("marketTip") or quote.get("marketType")),
        ("Company", profile.get("securityCompany")),
        ("Scale", profile.get("scale")),
        ("Managers", profile.get("managerNames")),
        ("Net subscription shares", subscription.get("netSubscriptionShares")),
    ]:
        print(f"- {label}: {cell(value)}")
    if result.get("performance"):
        print("\n## Performance")
        for row in result["performance"][:5]:
            print(
                "- "
                f"{cell(row.get('dateRangeName'))}: "
                f"{cell(row.get('rangeChangePercent'))}, "
                f"rank {cell(row.get('sameKindRank'))}/{cell(row.get('sameKindRankTotal'))}"
            )


def print_etf_flow(result: dict[str, Any]) -> None:
    print(f"# Red Rocket ETF flow ({result['fetched_at']})")
    print(f"- ETF: {result['security_code']}")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    subscription = result.get("subscription") or {}
    share_change = result.get("share_change") or {}
    margin = result.get("margin") or {}
    tracking = result.get("tracking_index") or {}
    for label, value in [
        ("Net subscription shares", subscription.get("netSubscriptionShares")),
        ("Total share", subscription.get("totalShare")),
        ("Total/float share", share_change.get("totalShare") or share_change.get("floatShare")),
        ("Share change", share_change.get("shareChange")),
        ("Margin net inflow", margin.get("marginNetInflow")),
        ("Tracking index", tracking.get("securityName")),
        ("Tracking index change", tracking.get("changePercent")),
    ]:
        print(f"- {label}: {cell(value)}")
    five_day = result.get("five_mfd_inflow") or {}
    if five_day:
        print(f"- 5D main-fund inflow total: {cell(five_day.get('totalSMfdInflow'))}")
        print(f"- 5D latest trade date: {cell(five_day.get('latestTradeDate'))}")
    rows = result.get("five_mfd_inflow_rows") or []
    if rows:
        print("\n## 5D Main-Fund Inflow")
        for row in rows:
            print(f"- {cell(row.get('tradeDt'))}: {cell(row.get('SMfdInflow'))}")


def print_industry(result: dict[str, Any]) -> None:
    print(f"# Red Rocket industry ({result['fetched_at']})")
    print(
        "- Industry: "
        f"{cell(result.get('industry_id'))} {cell(result.get('industry_name'))}"
    )
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    quote = result.get("quote") or {}
    if quote:
        print(
            "- Representative index: "
            f"{cell(quote.get('securityCode'))} "
            f"{cell(quote.get('securityName'))} "
            f"{cell(quote.get('price'))} "
            f"{cell(quote.get('changePercent'))}%"
        )
    indexes = result.get("index_codes") or []
    if indexes:
        print("\n## Related Indexes")
        for row in indexes:
            print(
                "- "
                f"{cell(row.get('securityCode'))} "
                f"{cell(row.get('securityName'))}: "
                f"{cell(row.get('securityDesc'))}"
            )
    classify = result.get("classify") or []
    if classify:
        print("\n## Indicators")
        for group in classify:
            indicators = group.get("indicators") if isinstance(group, dict) else []
            text = "; ".join(
                f"{cell(item.get('indicatorId'))} {cell(item.get('indicatorName'))}"
                for item in indicators
                if isinstance(item, dict)
            )
            print(f"- {cell(group.get('industryClassifyName'))}: {text or '--'}")
    detail = result.get("indicator_detail") or {}
    detail_rows = detail.get("rows") if isinstance(detail.get("rows"), list) else []
    if detail_rows:
        print("\n## Indicator Detail")
        for row in detail_rows:
            print(
                "- "
                f"{cell(detail.get('indicatorName'))}: "
                f"{cell(row.get('indicatorTm'))} "
                f"{cell(row.get('indicatorValue'))} "
                f"yoy {cell(row.get('yoy'))}"
            )
    related = result.get("related_indicators") or {}
    related_rows = related.get("rows") if isinstance(related.get("rows"), list) else []
    if related_rows:
        print("\n## Related Indicator Values")
        print(f"- Indicator total: {cell(related.get('indicatorTotal'))}")
        for row in related_rows:
            print(
                "- "
                f"{cell(row.get('indicatorDataName'))}: "
                f"{cell(row.get('indicatorTm'))} "
                f"{cell(row.get('indicatorValue'))} "
                f"yoy {cell(row.get('yoy'))}"
            )
    chart = result.get("chart") or {}
    if chart:
        print(
            "\n## Chart\n"
            f"- Chart: {cell(chart.get('securityName'))} "
            f"{cell(chart.get('chartDimension'))} "
            f"change {cell(chart.get('dimensionChange'))}"
        )
    chart_rows = result.get("chart_rows") or []
    for row in chart_rows[:5]:
        print(
            "- "
            f"{cell(row.get('tradeDate') or row.get('date'))}: "
            f"{cell(row.get('intervalChangePercent') or row.get('changePercent'))}"
        )
    memoirs = result.get("memoirs") or []
    if memoirs:
        print("\n## Memoirs")
        for row in memoirs:
            print(f"- {cell(row.get('memoirTime'))} {cell(row.get('memoirTitle'))}")


def print_index_compare(result: dict[str, Any]) -> None:
    print(f"# Red Rocket index compare ({result['fetched_at']})")
    print(f"- Indexes: {cell(result.get('index_infos') or result.get('index_codes'))}")
    data_time = result.get("data_time") or {}
    if data_time:
        print(
            "- Data time: "
            f"valuation {cell(data_time.get('valuationTime'))}; "
            f"ROE {cell(data_time.get('roeTime'))}"
        )
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    interval_change = result.get("interval_change") or {}
    interval_rows = interval_change.get("performances") or []
    if interval_rows:
        columns = [
            "securityCode",
            "securityName",
            "changePercent",
            "weeklyPerformance",
            "monthlyPerformance",
            "yearlyPerformance",
        ]
        print("\n## Interval Change")
        print("| " + " | ".join(columns) + " |")
        print("| " + " | ".join(["---"] * len(columns)) + " |")
        for row in interval_rows:
            print("| " + " | ".join(cell(row.get(key)) for key in columns) + " |")
    winners = interval_change.get("max")
    if isinstance(winners, dict) and winners:
        print("\n## Interval Winners")
        for label, value in winners.items():
            print(f"- {cell(label)}: {cell(value)}")
    market_context = result.get("market_context") or {}
    market_info = market_context.get("marketInfo") if isinstance(market_context, dict) else []
    if market_info:
        print("\n## Market Context")
        for row in market_info:
            print(
                "- "
                f"{cell(row.get('marketName'))} "
                f"{cell(row.get('startTime'))}~{cell(row.get('endTime'))}: "
                f"{cell(row.get('marketSummary'))}"
            )
            percent_rows = row.get("percentList") if isinstance(row.get("percentList"), list) else []
            if percent_rows:
                values = [
                    f"{cell(item.get('securityCode'))} {cell(item.get('securityName'))} {cell(item.get('changePercent'))}%"
                    for item in percent_rows
                    if isinstance(item, dict)
                ]
                print(f"  {'; '.join(values)}")
    performance_rows = (
        market_context.get("indexPerformance")
        if isinstance(market_context.get("indexPerformance"), list)
        else []
    )
    if performance_rows:
        print("\n## Market Performance Series")
        for row in performance_rows:
            latest = row.get("latest") if isinstance(row.get("latest"), dict) else {}
            print(
                "- "
                f"{cell(row.get('securityCode'))} {cell(row.get('securityName'))}: "
                f"latest {cell(latest.get('tradeDate'))} "
                f"{cell(latest.get('intervalChangePercent'))}, "
                f"points {cell(row.get('itemSize'))}"
            )
    chart_rows = result.get("chart") or []
    if chart_rows:
        print("\n## Compare Chart")
        for row in chart_rows:
            latest = row.get("latest") if isinstance(row.get("latest"), dict) else {}
            print(
                "- "
                f"{cell(row.get('securityCode'))} {cell(row.get('securityName'))}: "
                f"latest {cell(latest.get('tradeDate'))} "
                f"{cell(latest.get('intervalChangePercent'))}, "
                f"points {cell(row.get('itemSize'))}"
            )
    minute_rows = result.get("minute_chart") or []
    if minute_rows:
        print("\n## Compare Minute Chart")
        for row in minute_rows:
            latest = row.get("latest") if isinstance(row.get("latest"), dict) else {}
            print(
                "- "
                f"{cell(row.get('securityCode'))} {cell(row.get('securityName'))}: "
                f"{cell(row.get('tradeDate'))} "
                f"{cell(latest.get('minuteByHours'))} "
                f"{cell(latest.get('changePercent'))}%, "
                f"points {cell(row.get('itemSize'))}"
            )
    industry_distribution = result.get("industry_distribution") or {}
    distribution_rows = (
        industry_distribution.get("rows")
        if isinstance(industry_distribution.get("rows"), list)
        else []
    )
    if distribution_rows:
        print("\n## Industry Distribution")
        for row in distribution_rows:
            items = row.get("items") if isinstance(row.get("items"), list) else []
            item_text = "; ".join(
                f"{cell(item.get('industriesName'))} {cell(item.get('proportion'))}"
                for item in items
                if isinstance(item, dict)
            )
            print(
                "- "
                f"{cell(row.get('securityCode'))} "
                f"{cell(row.get('reportPeriodStr'))} "
                f"{cell(row.get('industryLevel'))}: "
                f"{item_text or '--'}"
            )
    if result.get("funds"):
        print("\n## Related Funds")
        for row in result["funds"]:
            print(
                "- "
                f"{cell(row.get('indexCode'))}: "
                f"ETF {cell(row.get('etfCount'))} / OTC {cell(row.get('otcCount'))}; "
                f"ETF scale {cell(row.get('etfScale'))}; "
                f"OTC scale {cell(row.get('otcScale'))}"
            )
    if result.get("archives"):
        print("\n## Archives")
        for row in result["archives"][:5]:
            print(f"- {cell(row.get('securityName'))}: {cell(row.get('securityCode'))}")
    if result.get("similarity"):
        print("\n## Similarity")
        for row in result["similarity"][:5]:
            pairs = row.get("componentStockSimilarity")
            if isinstance(pairs, list):
                values = [
                    f"{cell(item.get('indexCode'))} {cell(item.get('similarity'))}%"
                    for item in pairs
                    if isinstance(item, dict)
                ]
                print(f"- {cell(row.get('indexName'))}: {', '.join(values)}")
            else:
                print(f"- {cell(row)}")


def print_focus_news(result: dict[str, Any]) -> None:
    print(f"# Red Rocket focus news ({result['fetched_at']})")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    latest = result.get("latest_point") or {}
    if latest:
        print(
            "- Latest point: "
            f"{cell(latest.get('minuteByHours'))} "
            f"{cell(latest.get('price'))} "
            f"{cell(latest.get('changePercent'))}%"
        )
    if result.get("rows"):
        print("\n## News")
        for row in result["rows"]:
            print(
                "- "
                f"{cell(row.get('time'))} "
                f"{cell(row.get('theme'))}: "
                f"{cell(row.get('summary'))}"
            )


def print_hot_timeline(result: dict[str, Any]) -> None:
    print(f"# Red Rocket hot timeline ({result['fetched_at']})")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    print(f"- Show status: {cell(result.get('show_status'))}")
    rows = result.get("rows") or []
    if not rows:
        print("\n无结果。")
        return
    print("\n## Events")
    for row in rows:
        print(f"- {cell(row.get('changeTime'))} {cell(row.get('content'))}")
        related_indexes = row.get("relatedIndexes") or []
        if related_indexes:
            print(f"  Indexes: {format_related_hot_items(related_indexes)}")
        related_etfs = row.get("relatedEtfs") or []
        if related_etfs:
            print(f"  ETFs: {format_related_hot_items(related_etfs)}")


def format_related_hot_items(rows: list[dict[str, Any]]) -> str:
    return "; ".join(
        f"{cell(row.get('indexCode'))} {cell(row.get('indexName'))}"
        for row in rows
        if isinstance(row, dict)
    )


def print_must_read(result: dict[str, Any]) -> None:
    print(f"# Red Rocket must-read ({result['fetched_at']})")
    print(f"- Security: {result['security_code']}")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    big_event = result.get("big_event") or {}
    if big_event:
        print(f"- Big event: {cell(big_event.get('statusId'))} {cell(big_event.get('title'))}")
    if result.get("rows"):
        print("\n## Rows")
        for row in result["rows"]:
            print(
                "- "
                f"{cell(row.get('statusId'))} "
                f"{cell(row.get('title'))} "
                f"[{cell(row.get('contentLabel'))}] "
                f"{cell(row.get('nickName'))}"
            )


def print_knowledge(result: dict[str, Any]) -> None:
    print(f"# Red Rocket knowledge ({result['fetched_at']})")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    if result.get("knowledge_keys"):
        print(f"- Keys: {', '.join(result['knowledge_keys'])}")
    if not result.get("rows"):
        print("\n无结果。")
        return
    print("\n## Rows")
    for row in result["rows"]:
        print(f"- {cell(row.get('knowledgeKey'))}: {cell(row.get('title'))}")
        if row.get("content"):
            print(f"  {cell(row.get('content'))}")


def print_article(result: dict[str, Any]) -> None:
    print(f"# Red Rocket article ({result['fetched_at']})")
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    detail = result.get("detail") or {}
    if not detail:
        print("\n无结果。")
        return
    print(f"- Status ID: {cell(result.get('status_id'))}")
    print(f"- Title: {cell(detail.get('title'))}")
    if detail.get("contentLabel"):
        print(f"- Labels: {cell(detail.get('contentLabel'))}")
    if detail.get("nickName"):
        print(f"- Author: {cell(detail.get('nickName'))}")
    if detail.get("publishTime"):
        print(f"- Publish time: {cell(detail.get('publishTime'))}")
    if detail.get("securityInfoVos"):
        print("\n## Related")
        for item in detail["securityInfoVos"]:
            print(f"- {cell(item.get('securityCode'))} {cell(item.get('securityName'))}")
    if detail.get("content"):
        print("\n## Excerpt")
        print(cell(detail.get("content")))


def print_signal_detail(result: dict[str, Any]) -> None:
    print(f"# Red Rocket signal detail ({result['fetched_at']})")
    score_area = result.get("score_area") or {}
    print(
        "- Security: "
        f"{cell(result.get('security_code'))} "
        f"{cell(score_area.get('securityName'))}"
    )
    print(f"- Source: {first_source(result['source'])}")
    for source_limit in result.get("source_limits", []):
        print(f"- Source limit: {source_limit}")
    print(f"- Score: {cell(score_area.get('score'))} {cell(score_area.get('scoreLabel'))}")
    for label, value in [
        ("Score date", score_area.get("scoreDate")),
        ("Tips", score_area.get("tips")),
        ("Pointer", score_area.get("pointer")),
        ("History", score_area.get("hisDesc")),
    ]:
        if value not in (None, ""):
            print(f"- {label}: {cell(value)}")
    if result.get("score_details"):
        print("\n## Score Details")
        for row in result["score_details"]:
            print(
                "- "
                f"{cell(row.get('title'))}: "
                f"score {cell(row.get('score'))}, "
                f"avg {cell(row.get('avg'))}, "
                f"pointer {cell(row.get('pointerType'))}"
            )
            if row.get("desc") or row.get("scoreDesc"):
                print(f"  {cell(row.get('desc') or row.get('scoreDesc'))}")
    related_product = result.get("related_product") or {}
    if related_product:
        print(
            "- Related product: "
            f"{cell(related_product.get('productCode'))} "
            f"{cell(related_product.get('productName'))}"
        )


def emit(result: dict[str, Any], *, fmt: str) -> None:
    if fmt == "json":
        print_json(result)
    elif result.get("kind") == "home":
        print_home(result)
    elif result.get("kind") == "fund":
        print_fund(result)
    elif result.get("kind") == "fund_notices":
        print_fund_notices(result)
    elif result.get("kind") == "index":
        print_index(result)
    elif result.get("kind") == "index_detail_plus":
        print_index_detail_plus(result)
    elif result.get("kind") == "security_context":
        print_security_context(result)
    elif result.get("kind") == "snapshot":
        print_snapshot(result)
    elif result.get("kind") == "etf_detail":
        print_etf_detail(result)
    elif result.get("kind") == "etf_flow":
        print_etf_flow(result)
    elif result.get("kind") == "industry":
        print_industry(result)
    elif result.get("kind") == "index_compare":
        print_index_compare(result)
    elif result.get("kind") == "focus_news":
        print_focus_news(result)
    elif result.get("kind") == "hot_timeline":
        print_hot_timeline(result)
    elif result.get("kind") == "must_read":
        print_must_read(result)
    elif result.get("kind") == "knowledge":
        print_knowledge(result)
    elif result.get("kind") == "article":
        print_article(result)
    elif result.get("kind") == "signal_detail":
        print_signal_detail(result)
    else:
        print_table(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="redrocket",
        description="Read-only Red Rocket market data CLI.",
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Install the bundled agent skill.")
    init.add_argument("--client", choices=["codex", "agents", "claude"], default="codex")
    init.add_argument("--dest", help="Custom skills directory. Overrides --client.")
    init.add_argument("--force", action="store_true", help="Overwrite an existing installed skill.")
    init.add_argument("--uninstall", action="store_true", help="Remove the installed skill.")
    init.add_argument("--print", action="store_true", help="Print bundled SKILL.md without installing.")
    init.add_argument("--json", action="store_true", help="Emit compact JSON.")

    scan = sub.add_parser("scan", help="Scan index valuation tables.")
    add_common_options(scan)
    scan.add_argument("--preset", choices=sorted(PRESETS), default="wide")
    scan.add_argument("--order-by", default="pepercent")
    scan.add_argument("--order", choices=["asc", "desc"], default="asc")
    scan.add_argument("--limit", type=int, default=10)

    etf = sub.add_parser("etf", help="Scan ETF tables.")
    add_common_options(etf)
    etf.add_argument("--preset", choices=sorted(PRESETS), default="wide")
    etf.add_argument("--order-by", default="l.scale")
    etf.add_argument("--order", choices=["asc", "desc"], default="asc")
    etf.add_argument("--limit", type=int, default=10)

    home = sub.add_parser("home", help="Read compact Red Rocket PC home-page discovery context.")
    add_common_options(home)
    home.add_argument("--limit", type=int, default=5)

    search = sub.add_parser("search", help="Search Red Rocket securities.")
    add_common_options(search)
    search.add_argument("keyword")
    search.add_argument("--limit", type=int, default=20)

    snapshot = sub.add_parser("snapshot", help="Read lightweight multi-security quote snapshots.")
    add_common_options(snapshot)
    snapshot.add_argument(
        "security_codes",
        help="Comma-separated security codes, e.g. 000300.SH,931071.CSI,159819.SZ.",
    )

    related = sub.add_parser("related", help="List related funds/ETFs for an index.")
    add_common_options(related)
    related.add_argument("security_code")
    related.add_argument("--security-type", default="etf")
    related.add_argument("--limit", type=int, default=10)

    index = sub.add_parser("index", help="Read an index profile, labels, and recent ROE.")
    add_common_options(index)
    index.add_argument("security_code")
    index.add_argument("--limit", type=int, default=10)

    components = sub.add_parser(
        "components",
        help="Read full component-stock rows for an index or tracked security.",
    )
    add_common_options(components)
    components.add_argument("security_code")
    components.add_argument("--limit", type=int, default=20)

    security_context = sub.add_parser(
        "security-context",
        help="Read runtime read-only security context for one index, ETF, or stock.",
    )
    add_common_options(security_context)
    security_context.add_argument("security_code")
    security_context.add_argument("--limit", type=int, default=10)

    index_detail_plus = sub.add_parser(
        "index-detail-plus",
        help="Read deeper read-only index valuation, component, and product context.",
    )
    add_common_options(index_detail_plus)
    index_detail_plus.add_argument("security_code")
    index_detail_plus.add_argument("--valuation-type", default="PE")
    index_detail_plus.add_argument("--time-interval", default="last_5_years")
    index_detail_plus.add_argument("--industry-level", default="3")
    index_detail_plus.add_argument("--limit", type=int, default=10)

    quote = sub.add_parser("quote", help="Read Red Rocket quote snapshots.")
    add_common_options(quote)
    quote.add_argument("security_codes", help="Comma-separated security codes, e.g. 000300.SH,000688.SH")

    etf_detail = sub.add_parser("etf-detail", help="Read an ETF profile, quote, and share-flow context.")
    add_common_options(etf_detail)
    etf_detail.add_argument("security_code")
    etf_detail.add_argument("--limit", type=int, default=10)

    etf_flow = sub.add_parser(
        "etf-flow",
        help="Read deeper read-only ETF share, margin, subscription, and tracking-index context.",
    )
    add_common_options(etf_flow)
    etf_flow.add_argument("security_code")
    etf_flow.add_argument("--period", default="3M")
    etf_flow.add_argument("--limit", type=int, default=10)

    industry = sub.add_parser(
        "industry",
        help="Read H5 industry page context, indicators, related indexes, and memoirs.",
    )
    add_common_options(industry)
    industry.add_argument("--industry-id", help="Industry code from industry/list.")
    industry.add_argument("--indicator-id", help="Optional indicator ID for detail rows.")
    industry.add_argument(
        "--index-code",
        default="",
        help="Optional index code for the industry chart overlay, e.g. 000300.SH.",
    )
    industry.add_argument("--limit", type=int, default=5)

    heat = sub.add_parser("heat", help="Read Red Rocket home heat rows.")
    add_common_options(heat)
    heat.add_argument("--order-by", default="changePercent")
    heat.add_argument("--order", choices=["asc", "desc"], default="desc")
    heat.add_argument("--class-a", default="", help="Optional Red Rocket classA filter, e.g. 01 or 02.")
    heat.add_argument("--limit", type=int, default=10)

    hot_timeline = sub.add_parser("hot-timeline", help="Read compact H5 hot-market event timeline rows.")
    add_common_options(hot_timeline)
    hot_timeline.add_argument("--limit", type=int, default=8)

    news = sub.add_parser("news", help="Read Red Rocket worth-looking news/opportunity rows.")
    add_common_options(news)
    news.add_argument("--page", type=int, default=1)
    news.add_argument("--limit", type=int, default=8)

    classes = sub.add_parser("classes", help="Read Red Rocket index-browser class filters.")
    add_common_options(classes)
    classes.add_argument("--table-name", default="index")
    classes.add_argument("--page-name", default="index")
    classes.add_argument("--search-value", default="")
    classes.add_argument("--limit", type=int, default=20)

    focus_news = sub.add_parser("focus-news", help="Read compact focus-news market context.")
    add_common_options(focus_news)
    focus_news.add_argument("--limit", type=int, default=8)

    knowledge = sub.add_parser("knowledge", help="Read Red Rocket methodology/help text by key.")
    add_common_options(knowledge)
    knowledge.add_argument("knowledge_keys", nargs="+")
    knowledge.add_argument("--content-limit", type=positive_int, default=240)

    article = sub.add_parser("article", help="Read compact Red Rocket article detail by status ID.")
    add_common_options(article)
    article.add_argument("status_id")
    article.add_argument("--content-limit", type=positive_int, default=240)

    wind = sub.add_parser("wind", help="Read Red Rocket index wind-vane signal rows.")
    add_common_options(wind)
    wind.add_argument("--limit", type=int, default=10)

    signal_detail = sub.add_parser("signal-detail", help="Read compact wind-vane detail for one security.")
    add_common_options(signal_detail)
    signal_detail.add_argument("security_code")
    signal_detail.add_argument("--limit", type=int, default=5)

    compare = sub.add_parser("compare", help="Read recommended index comparison groups.")
    add_common_options(compare)
    compare.add_argument("--limit", type=int, default=8)

    index_compare = sub.add_parser(
        "index-compare",
        help="Read stable detail endpoints for explicit index comparisons.",
    )
    add_common_options(index_compare)
    index_compare.add_argument(
        "index_infos",
        nargs="+",
        help="Index specs as CODE:NAME, e.g. 000300.SH:沪深300 000905.SH:中证500.",
    )
    index_compare.add_argument("--limit", type=int, default=10)

    fund = sub.add_parser("fund", help="Read an OTC fund profile.")
    add_common_options(fund)
    fund.add_argument("fund_code")
    fund.add_argument("--limit", type=int, default=10)
    fund.add_argument(
        "--chart-date-type",
        default="oneYear",
        choices=[
            "oneMonth",
            "threeMonths",
            "sixMonths",
            "oneYear",
            "threeYears",
            "fiveYears",
            "thisYear",
            "establish",
        ],
        help="Fund chart date window used by Red Rocket H5 endpoints.",
    )
    fund.add_argument(
        "--net-type",
        dest="nav_net_type",
        default="netUnit",
        choices=["netUnit", "netTotal", "weekAnnualized", "netEstimates"],
        help="Fund NAV chart type.",
    )
    fund.add_argument(
        "--benchmark-code",
        default="",
        help="Optional benchmark code for performance chart, e.g. 000300.SH.",
    )

    fund_notices = sub.add_parser("fund-notices", help="Read recent OTC fund announcements.")
    add_common_options(fund_notices)
    fund_notices.add_argument("fund_code")
    fund_notices.add_argument("--page", type=int, default=1)
    fund_notices.add_argument("--limit", type=int, default=10)
    fund_notices.add_argument("--detail-id")

    must_read = sub.add_parser("must-read", help="Read compact must-read metadata for a security.")
    add_common_options(must_read)
    must_read.add_argument("security_code")
    must_read.add_argument("--limit", type=int, default=10)

    manager = sub.add_parser("manager", help="Read Red Rocket fund-manager detail rows.")
    add_common_options(manager)
    manager.add_argument("security_code")
    manager.add_argument("--limit", type=int, default=10)
    return parser


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--timeout", type=float, default=argparse.SUPPRESS)
    parser.add_argument("--format", choices=["markdown", "json"], default=argparse.SUPPRESS)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        if args.print:
            if args.uninstall or args.dest or args.force:
                parser.error("init --print cannot be combined with --uninstall, --dest, or --force")
            content = print_skill()
            if args.json:
                print(json.dumps({"action": "printed", "content": content}, ensure_ascii=False))
            else:
                print(content, end="" if content.endswith("\n") else "\n")
            return 0
        destinations = (
            [Path(args.dest).expanduser()]
            if args.dest
            else resolve_client_destinations(args.client)
        )
        try:
            result = (
                uninstall_from_targets(destinations)
                if args.uninstall
                else install_to_targets(destinations, force=args.force)
            )
        except (OSError, ValueError) as exc:
            print(f"redrocket init: {exc}", file=sys.stderr)
            return 2
        if args.json:
            print(result.to_json())
        else:
            verb = "Removed" if args.uninstall else "Installed"
            for path in result.paths:
                print(f"{verb} redrocket-market skill -> {path}")
        return 0

    client = RedRocketClient(timeout=args.timeout)
    try:
        if args.command == "scan":
            result = client.scan(
                args.preset,
                order_by=args.order_by,
                order=args.order,
                limit=args.limit,
            )
        elif args.command == "etf":
            result = client.scan(
                args.preset,
                order_by=args.order_by,
                order=args.order,
                limit=args.limit,
                etf=True,
            )
        elif args.command == "home":
            result = client.home(limit=args.limit)
        elif args.command == "search":
            result = client.search(args.keyword, limit=args.limit)
        elif args.command == "snapshot":
            result = client.snapshot(args.security_codes)
        elif args.command == "related":
            result = client.related(
                args.security_code,
                security_type=args.security_type,
                limit=args.limit,
            )
        elif args.command == "index":
            result = client.index(args.security_code, limit=args.limit)
        elif args.command == "components":
            result = client.components(args.security_code, limit=args.limit)
        elif args.command == "security-context":
            result = client.security_context(args.security_code, limit=args.limit)
        elif args.command == "index-detail-plus":
            result = client.index_detail_plus(
                args.security_code,
                valuation_type=args.valuation_type,
                time_interval=args.time_interval,
                industry_level=args.industry_level,
                limit=args.limit,
            )
        elif args.command == "quote":
            result = client.quote(args.security_codes)
        elif args.command == "etf-detail":
            result = client.etf_detail(args.security_code, limit=args.limit)
        elif args.command == "etf-flow":
            result = client.etf_flow(
                args.security_code,
                period=args.period,
                limit=args.limit,
            )
        elif args.command == "industry":
            result = client.industry(
                industry_id=args.industry_id,
                indicator_id=args.indicator_id,
                index_code=args.index_code,
                limit=args.limit,
            )
        elif args.command == "heat":
            result = client.heat(
                order_by=args.order_by,
                order=args.order,
                class_a=args.class_a,
                limit=args.limit,
            )
        elif args.command == "hot-timeline":
            result = client.hot_timeline(limit=args.limit)
        elif args.command == "news":
            result = client.news(page=args.page, limit=args.limit)
        elif args.command == "classes":
            result = client.classes(
                table_name=args.table_name,
                page_name=args.page_name,
                search_value=args.search_value,
                limit=args.limit,
            )
        elif args.command == "focus-news":
            result = client.focus_news(limit=args.limit)
        elif args.command == "knowledge":
            result = client.knowledge(
                args.knowledge_keys,
                content_limit=args.content_limit,
            )
        elif args.command == "article":
            result = client.article(args.status_id, content_limit=args.content_limit)
        elif args.command == "wind":
            result = client.wind(limit=args.limit)
        elif args.command == "signal-detail":
            result = client.signal_detail(args.security_code, limit=args.limit)
        elif args.command == "compare":
            result = client.compare_recommend(limit=args.limit)
        elif args.command == "index-compare":
            result = client.index_compare(
                [parse_index_info(value) for value in args.index_infos],
                limit=args.limit,
            )
        elif args.command == "fund":
            result = client.fund(
                args.fund_code,
                limit=args.limit,
                chart_date_type=args.chart_date_type,
                nav_net_type=args.nav_net_type,
                benchmark_code=args.benchmark_code,
            )
        elif args.command == "fund-notices":
            result = client.fund_notices(
                args.fund_code,
                page=args.page,
                limit=args.limit,
                detail_id=args.detail_id,
            )
        elif args.command == "must-read":
            result = client.must_read(args.security_code, limit=args.limit)
        elif args.command == "manager":
            result = client.manager(args.security_code, limit=args.limit)
        else:
            parser.error(f"unknown command: {args.command}")
    except RedRocketError as exc:
        print(f"redrocket: {exc}", file=sys.stderr)
        return 2
    emit(result, fmt=args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
