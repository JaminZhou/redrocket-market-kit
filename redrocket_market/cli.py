from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from redrocket_market.client import PRESETS, RedRocketClient, RedRocketError


def print_json(result: dict[str, Any]) -> None:
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cell(value: Any) -> str:
    if value in (None, ""):
        return "--"
    return str(value).replace("\n", " ")


def print_table(result: dict[str, Any]) -> None:
    print(f"# Red Rocket {result['kind']} ({result['fetched_at']})")
    print(f"- Source: {result['source']}")
    rows = result.get("rows") or []
    if not rows:
        print("\n无结果。")
        return
    keys = sorted({key for row in rows for key in row.keys()})
    preferred = [
        "securityCode",
        "securityName",
        "fundCode",
        "fundName",
        "fundCompany",
        "changePercent",
        "pePercent",
        "pbPercent",
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


def print_fund(result: dict[str, Any]) -> None:
    print(f"# Red Rocket fund ({result['fetched_at']})")
    print(f"- Fund: {result['fund_code']}")
    print(f"- Source: {result['source']['base']}")
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


def emit(result: dict[str, Any], *, fmt: str) -> None:
    if fmt == "json":
        print_json(result)
    elif result.get("kind") == "fund":
        print_fund(result)
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

    scan = sub.add_parser("scan", help="Scan index valuation tables.")
    add_common_options(scan)
    scan.add_argument("--preset", choices=sorted(PRESETS), default="wide")
    scan.add_argument("--order-by", default="pepercent")
    scan.add_argument("--order", choices=["asc", "desc"], default="asc")
    scan.add_argument("--limit", type=int, default=10)

    etf = sub.add_parser("etf", help="Scan ETF tables.")
    add_common_options(etf)
    etf.add_argument("--preset", choices=sorted(PRESETS), default="wide")
    etf.add_argument("--order-by", default="pepercent")
    etf.add_argument("--order", choices=["asc", "desc"], default="asc")
    etf.add_argument("--limit", type=int, default=10)

    search = sub.add_parser("search", help="Search Red Rocket securities.")
    add_common_options(search)
    search.add_argument("keyword")

    related = sub.add_parser("related", help="List related funds/ETFs for an index.")
    add_common_options(related)
    related.add_argument("security_code")
    related.add_argument("--security-type", default="etf")
    related.add_argument("--limit", type=int, default=10)

    quote = sub.add_parser("quote", help="Read Red Rocket quote snapshots.")
    add_common_options(quote)
    quote.add_argument("security_codes", help="Comma-separated security codes, e.g. 000300.SH,000688.SH")

    fund = sub.add_parser("fund", help="Read an OTC fund profile.")
    add_common_options(fund)
    fund.add_argument("fund_code")
    fund.add_argument("--limit", type=int, default=10)
    return parser


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--timeout", type=float, default=argparse.SUPPRESS)
    parser.add_argument("--format", choices=["markdown", "json"], default=argparse.SUPPRESS)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
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
        elif args.command == "search":
            result = client.search(args.keyword)
        elif args.command == "related":
            result = client.related(
                args.security_code,
                security_type=args.security_type,
                limit=args.limit,
            )
        elif args.command == "quote":
            result = client.quote(args.security_codes)
        elif args.command == "fund":
            result = client.fund(args.fund_code, limit=args.limit)
        else:
            parser.error(f"unknown command: {args.command}")
    except RedRocketError as exc:
        print(f"redrocket: {exc}", file=sys.stderr)
        return 2
    emit(result, fmt=args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
