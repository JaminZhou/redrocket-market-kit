from pathlib import Path
from typing import Any

import pytest

from redrocket_market.cli import main


def test_cli_init_installs_skill_to_dest(tmp_path: Path, capsys) -> None:
    exit_code = main(["init", "--dest", str(tmp_path)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Installed redrocket-market skill" in output
    assert (tmp_path / "redrocket-market" / "SKILL.md").exists()


def test_cli_init_print_outputs_skill(capsys) -> None:
    exit_code = main(["init", "--print"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "name: redrocket-market" in output


def test_cli_init_uninstalls_skill_from_dest(tmp_path: Path) -> None:
    assert main(["init", "--dest", str(tmp_path)]) == 0

    exit_code = main(["init", "--dest", str(tmp_path), "--uninstall"])

    assert exit_code == 0
    assert not (tmp_path / "redrocket-market").exists()


def test_cli_init_refuses_to_modify_bundled_skill(capsys) -> None:
    exit_code = main(["init", "--dest", "skills", "--force"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Refusing to modify bundled redrocket-market skill" in captured.err
    assert (Path("skills") / "redrocket-market" / "SKILL.md").exists()


def test_cli_init_with_codex_client_honors_codex_home(tmp_path: Path, monkeypatch) -> None:
    codex_home = tmp_path / ".codex-custom"
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    exit_code = main(["init", "--client", "codex"])

    assert exit_code == 0
    assert (codex_home / "skills" / "redrocket-market" / "SKILL.md").exists()


def test_cli_init_with_claude_client_honors_claude_config_dir(
    tmp_path: Path, monkeypatch
) -> None:
    claude_home = tmp_path / ".claude-custom"
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(claude_home))

    exit_code = main(["init", "--client", "claude"])

    assert exit_code == 0
    assert (claude_home / "skills" / "redrocket-market" / "SKILL.md").exists()


def test_cli_rejects_non_positive_knowledge_content_limit(capsys) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["knowledge", "follw_valuation_tips", "--content-limit", "0"])

    assert excinfo.value.code == 2
    assert "positive integer" in capsys.readouterr().err


def test_cli_dispatches_new_readonly_commands(monkeypatch, capsys) -> None:
    calls: list[tuple[str, dict[str, Any]]] = []

    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            calls.append(("init", {"timeout": timeout}))

        def index(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("index", {"security_code": security_code, **kwargs}))
            return {
                "kind": "index",
                "fetched_at": "now",
                "source": {"archives": "url"},
                "security_code": security_code,
                "summary": {},
            }

        def search(self, keyword: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("search", {"keyword": keyword, **kwargs}))
            return {
                "kind": "search",
                "fetched_at": "now",
                "source": {"list": "url"},
                "keyword": keyword,
                "rows": [],
            }

        def snapshot(self, security_codes: str) -> dict[str, Any]:
            calls.append(("snapshot", {"security_codes": security_codes}))
            return {
                "kind": "snapshot",
                "fetched_at": "now",
                "source": {"snapshot": "url"},
                "security_codes": security_codes,
                "rows": [],
            }

        def components(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("components", {"security_code": security_code, **kwargs}))
            return {
                "kind": "components",
                "fetched_at": "now",
                "source": "url",
                "security_code": security_code,
                "rows": [],
            }

        def security_context(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("security_context", {"security_code": security_code, **kwargs}))
            return {
                "kind": "security_context",
                "fetched_at": "now",
                "source": {"info": "url"},
                "security_code": security_code,
                "info": {},
            }

        def etf_detail(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("etf_detail", {"security_code": security_code, **kwargs}))
            return {
                "kind": "etf_detail",
                "fetched_at": "now",
                "source": {"quote": "url"},
                "security_code": security_code,
                "quote": {},
            }

        def heat(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(("heat", kwargs))
            return {"kind": "heat", "fetched_at": "now", "source": "url", "rows": []}

        def hot_timeline(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(("hot_timeline", kwargs))
            return {
                "kind": "hot_timeline",
                "fetched_at": "now",
                "source": {"timeline": "url"},
                "rows": [],
            }

        def news(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(("news", kwargs))
            return {"kind": "news", "fetched_at": "now", "source": "url", "rows": []}

        def classes(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(("classes", kwargs))
            return {"kind": "classes", "fetched_at": "now", "source": "url", "rows": []}

        def focus_news(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(("focus_news", kwargs))
            return {"kind": "focus_news", "fetched_at": "now", "source": "url", "rows": []}

        def knowledge(
            self,
            knowledge_keys: list[str],
            **kwargs: Any,
        ) -> dict[str, Any]:
            calls.append(("knowledge", {"knowledge_keys": knowledge_keys, **kwargs}))
            return {"kind": "knowledge", "fetched_at": "now", "source": "url", "rows": []}

        def article(self, status_id: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("article", {"status_id": status_id, **kwargs}))
            return {
                "kind": "article",
                "fetched_at": "now",
                "source": "url",
                "status_id": status_id,
                "detail": {"title": "文章标题"},
            }

        def wind(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(("wind", kwargs))
            return {"kind": "wind", "fetched_at": "now", "source": "url", "rows": []}

        def signal_detail(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("signal_detail", {"security_code": security_code, **kwargs}))
            return {
                "kind": "signal_detail",
                "fetched_at": "now",
                "source": "url",
                "security_code": security_code,
                "score_area": {},
            }

        def compare_recommend(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(("compare", kwargs))
            return {"kind": "compare_recommend", "fetched_at": "now", "source": "url", "rows": []}

        def index_detail_plus(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("index_detail_plus", {"security_code": security_code, **kwargs}))
            return {
                "kind": "index_detail_plus",
                "fetched_at": "now",
                "source": {"valuation": "url"},
                "security_code": security_code,
            }

        def etf_flow(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("etf_flow", {"security_code": security_code, **kwargs}))
            return {
                "kind": "etf_flow",
                "fetched_at": "now",
                "source": {"subscription": "url"},
                "security_code": security_code,
            }

        def industry(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(("industry", kwargs))
            return {
                "kind": "industry",
                "fetched_at": "now",
                "source": {"list": "url"},
                "industry_id": kwargs.get("industry_id") or "industry_semiconductor",
                "industry_name": "半导体",
                "industries": [],
            }

        def index_compare(
            self,
            index_infos: list[tuple[str, str]],
            **kwargs: Any,
        ) -> dict[str, Any]:
            calls.append(("index_compare", {"index_infos": index_infos, **kwargs}))
            return {
                "kind": "index_compare",
                "fetched_at": "now",
                "source": {"archives": "url"},
                "index_codes": ",".join(code for code, _ in index_infos),
            }

        def fund_notices(self, fund_code: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("fund_notices", {"fund_code": fund_code, **kwargs}))
            return {
                "kind": "fund_notices",
                "fetched_at": "now",
                "source": "url",
                "fund_code": fund_code,
                "rows": [],
            }

        def must_read(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("must_read", {"security_code": security_code, **kwargs}))
            return {
                "kind": "must_read",
                "fetched_at": "now",
                "source": "url",
                "security_code": security_code,
                "rows": [],
            }

        def manager(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            calls.append(("manager", {"security_code": security_code, **kwargs}))
            return {
                "kind": "manager",
                "fetched_at": "now",
                "source": "url",
                "security_code": security_code,
                "rows": [],
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["index", "000300.SH", "--limit", "2"]) == 0
    assert main(["search", "110020", "--limit", "3"]) == 0
    assert main(["snapshot", "000300.SH,159819.SZ"]) == 0
    assert main(["components", "000300.SH", "--limit", "2"]) == 0
    assert main(["security-context", "000300.SH", "--limit", "3"]) == 0
    assert main(["etf-detail", "510300.SH", "--limit", "3"]) == 0
    assert main(["heat", "--limit", "3"]) == 0
    assert main(["hot-timeline", "--limit", "4"]) == 0
    assert main(["news", "--page", "2", "--limit", "4"]) == 0
    assert main(["classes", "--search-value", "AI", "--limit", "3"]) == 0
    assert main(["focus-news", "--limit", "4"]) == 0
    assert main(
        [
            "knowledge",
            "follw_valuation_tips",
            "fund_details_page_asset_allocation",
            "--content-limit",
            "80",
        ]
    ) == 0
    assert main(["article", "N2607011526280455070", "--content-limit", "80"]) == 0
    assert main(["wind", "--limit", "5"]) == 0
    assert main(["signal-detail", "000300.SH", "--limit", "3"]) == 0
    assert main(["compare", "--limit", "6"]) == 0
    assert main(
        [
            "index-detail-plus",
            "000300.SH",
            "--valuation-type",
            "PB",
            "--time-interval",
            "last_3_years",
            "--limit",
            "2",
        ]
    ) == 0
    assert main(["etf-flow", "510300.SH", "--period", "1M", "--limit", "3"]) == 0
    assert main(
        [
            "industry",
            "--industry-id",
            "industry_semiconductor",
            "--indicator-id",
            "001004",
            "--index-code",
            "000300.SH",
            "--limit",
            "3",
        ]
    ) == 0
    assert main(
        [
            "index-compare",
            "000300.SH:沪深300",
            "000905.SH:中证500",
            "--limit",
            "4",
        ]
    ) == 0
    assert main(["fund-notices", "110020", "--limit", "3", "--detail-id", "40674473607"]) == 0
    assert main(["must-read", "000300.SH", "--limit", "3"]) == 0
    assert main(["manager", "110020", "--limit", "2"]) == 0

    capsys.readouterr()
    assert calls == [
        ("init", {"timeout": 10.0}),
        ("index", {"security_code": "000300.SH", "limit": 2}),
        ("init", {"timeout": 10.0}),
        ("search", {"keyword": "110020", "limit": 3}),
        ("init", {"timeout": 10.0}),
        ("snapshot", {"security_codes": "000300.SH,159819.SZ"}),
        ("init", {"timeout": 10.0}),
        ("components", {"security_code": "000300.SH", "limit": 2}),
        ("init", {"timeout": 10.0}),
        ("security_context", {"security_code": "000300.SH", "limit": 3}),
        ("init", {"timeout": 10.0}),
        ("etf_detail", {"security_code": "510300.SH", "limit": 3}),
        ("init", {"timeout": 10.0}),
        (
            "heat",
            {"order_by": "changePercent", "order": "desc", "class_a": "", "limit": 3},
        ),
        ("init", {"timeout": 10.0}),
        ("hot_timeline", {"limit": 4}),
        ("init", {"timeout": 10.0}),
        ("news", {"page": 2, "limit": 4}),
        ("init", {"timeout": 10.0}),
        ("classes", {"table_name": "index", "page_name": "index", "search_value": "AI", "limit": 3}),
        ("init", {"timeout": 10.0}),
        ("focus_news", {"limit": 4}),
        ("init", {"timeout": 10.0}),
        (
            "knowledge",
            {
                "knowledge_keys": [
                    "follw_valuation_tips",
                    "fund_details_page_asset_allocation",
                ],
                "content_limit": 80,
            },
        ),
        ("init", {"timeout": 10.0}),
        (
            "article",
            {"status_id": "N2607011526280455070", "content_limit": 80},
        ),
        ("init", {"timeout": 10.0}),
        ("wind", {"limit": 5}),
        ("init", {"timeout": 10.0}),
        ("signal_detail", {"security_code": "000300.SH", "limit": 3}),
        ("init", {"timeout": 10.0}),
        ("compare", {"limit": 6}),
        ("init", {"timeout": 10.0}),
        (
            "index_detail_plus",
            {
                "security_code": "000300.SH",
                "valuation_type": "PB",
                "time_interval": "last_3_years",
                "industry_level": "3",
                "limit": 2,
            },
        ),
        ("init", {"timeout": 10.0}),
        ("etf_flow", {"security_code": "510300.SH", "period": "1M", "limit": 3}),
        ("init", {"timeout": 10.0}),
        (
            "industry",
            {
                "industry_id": "industry_semiconductor",
                "indicator_id": "001004",
                "index_code": "000300.SH",
                "limit": 3,
            },
        ),
        ("init", {"timeout": 10.0}),
        (
            "index_compare",
            {
                "index_infos": [("000300.SH", "沪深300"), ("000905.SH", "中证500")],
                "limit": 4,
            },
        ),
        ("init", {"timeout": 10.0}),
        (
            "fund_notices",
            {"fund_code": "110020", "page": 1, "limit": 3, "detail_id": "40674473607"},
        ),
        ("init", {"timeout": 10.0}),
        ("must_read", {"security_code": "000300.SH", "limit": 3}),
        ("init", {"timeout": 10.0}),
        ("manager", {"security_code": "110020", "limit": 2}),
    ]


def test_cli_prints_source_limits(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def wind(self, **kwargs: Any) -> dict[str, Any]:
            return {
                "kind": "wind",
                "fetched_at": "now",
                "source": "url",
                "source_limits": ["methodology label; verify elsewhere"],
                "rows": [],
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["wind"]) == 0

    output = capsys.readouterr().out
    assert "- Source limit: methodology label; verify elsewhere" in output


def test_cli_prints_enriched_search_rows(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def search(self, keyword: str, **kwargs: Any) -> dict[str, Any]:
            return {
                "kind": "search",
                "fetched_at": "now",
                "source": {"list": "list-url", "batch_quote": "batch-url"},
                "source_limits": ["auxiliary discovery context"],
                "keyword": keyword,
                "rows": [
                    {
                        "securityCode": "000300.SH",
                        "securityType": "01",
                        "securityName": "沪深300",
                        "price": 4958.98,
                        "dayChangePercent": -0.4107,
                        "yearChangePercent": 12.34,
                    }
                ],
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["search", "沪深300", "--limit", "1"]) == 0

    output = capsys.readouterr().out
    assert "| securityCode | securityType | securityName | price | dayChangePercent |" in output
    assert "000300.SH" in output
    assert "- Source limit: auxiliary discovery context" in output


def test_cli_prints_security_context_structure_fields(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def security_context(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            return {
                "kind": "security_context",
                "fetched_at": "now",
                "source": {"info": "info-url"},
                "security_code": security_code,
                "info": {"securityName": "沪深300"},
                "market_value_distribution": [
                    {
                        "tradeDate": "2026-07-01",
                        "largeCapStockCount": 270,
                        "totalMarketValue": 68611064255966.85,
                    }
                ],
                "weight_concentration": [
                    {"annDate": "2026-07-01", "cr5": 11.1, "cr10": 20.2}
                ],
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["security-context", "000300.SH"]) == 0

    output = capsys.readouterr().out
    assert "largeCapStockCount=270" in output
    assert "totalMarketValue=68611064255966.85" in output
    assert "2026-07-01: cr5=11.1, cr10=20.2" in output
    assert "2026-07-01: --" not in output


def test_cli_prints_snapshot_rows(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def snapshot(self, security_codes: str) -> dict[str, Any]:
            return {
                "kind": "snapshot",
                "fetched_at": "now",
                "source": {"snapshot": "snapshot-url", "security_type": "type-url"},
                "source_limits": ["auxiliary quote snapshot"],
                "security_codes": security_codes,
                "rows": [
                    {
                        "securityCode": "159819.SZ",
                        "securityName": "人工智能ETF",
                        "securityType": "02",
                        "securityExchmarket": "SZ",
                        "price": 0.886,
                        "changePercent": 0.58,
                    }
                ],
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["snapshot", "159819.SZ"]) == 0

    output = capsys.readouterr().out
    assert "# Red Rocket snapshot (now)" in output
    assert "| securityCode | securityType | securityExchmarket | securityName | price | changePercent |" in output
    assert "159819.SZ" in output
    assert "SZ" in output
    assert "- Source limit: auxiliary quote snapshot" in output


def test_cli_prints_index_compare_context(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def index_compare(
            self,
            index_infos: list[tuple[str, str]],
            **kwargs: Any,
        ) -> dict[str, Any]:
            return {
                "kind": "index_compare",
                "fetched_at": "now",
                "source": {"archives": "archives-url"},
                "source_limits": ["verify exchange and fund-company records"],
                "index_codes": ",".join(code for code, _ in index_infos),
                "data_time": {
                    "valuationTime": "2026-07-01 wind",
                    "roeTime": "2026-03-31 wind",
                },
                "interval_change": {
                    "max": {"近一月": "931071.CSI"},
                    "performances": [
                        {
                            "securityCode": "000300.SH",
                            "securityName": "沪深300",
                            "changePercent": -0.41,
                            "weeklyPerformance": 0.32,
                            "monthlyPerformance": 2.37,
                            "yearlyPerformance": 25.77,
                        }
                    ],
                },
                "funds": [
                    {
                        "indexCode": "000300.SH",
                        "etfCount": 30,
                        "otcCount": 266,
                        "etfScale": 260963630904.252,
                        "otcScale": 132957360212.93,
                    }
                ],
                "archives": [],
                "similarity": [],
                "ten_weight": [],
                "market_value": [],
                "valuation_growth": [],
                "market_context": {
                    "marketInfo": [
                        {
                            "marketName": "牛市",
                            "startTime": "2016-01-28",
                            "endTime": "2018-01-29",
                            "marketSummary": "以大为美",
                            "percentList": [
                                {
                                    "securityCode": "000300.SH",
                                    "securityName": "沪深300",
                                    "changePercent": 50.75,
                                }
                            ],
                        }
                    ],
                    "indexPerformance": [
                        {
                            "securityCode": "000300.SH",
                            "securityName": "沪深300",
                            "itemSize": 510,
                            "latest": {
                                "tradeDate": "2026-06-26",
                                "intervalChangePercent": 0.5191,
                            },
                        }
                    ],
                },
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["index-compare", "000300.SH:沪深300", "931071.CSI:人工智能"]) == 0

    output = capsys.readouterr().out
    assert "# Red Rocket index compare (now)" in output
    assert "- Data time: valuation 2026-07-01 wind; ROE 2026-03-31 wind" in output
    assert "| securityCode | securityName | changePercent | weeklyPerformance | monthlyPerformance | yearlyPerformance |" in output
    assert "| 000300.SH | 沪深300 | -0.41 | 0.32 | 2.37 | 25.77 |" in output
    assert "- 近一月: 931071.CSI" in output
    assert "- 牛市 2016-01-28~2018-01-29: 以大为美" in output
    assert "000300.SH 沪深300 50.75%" in output
    assert "- 000300.SH 沪深300: latest 2026-06-26 0.5191, points 510" in output
    assert "- 000300.SH: ETF 30 / OTC 266; ETF scale 260963630904.252; OTC scale 132957360212.93" in output
    assert "- Source limit: verify exchange and fund-company records" in output


def test_cli_prints_etf_five_day_money_flow(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def etf_flow(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            return {
                "kind": "etf_flow",
                "fetched_at": "now",
                "source": {"subscription": "url"},
                "security_code": security_code,
                "five_mfd_inflow": {
                    "days": 2,
                    "latestTradeDate": "2026-07-01",
                    "totalSMfdInflow": -121116.6178,
                },
                "five_mfd_inflow_rows": [
                    {"tradeDt": "2026-07-01", "SMfdInflow": -124116.6178}
                ],
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["etf-flow", "510300.SH"]) == 0

    output = capsys.readouterr().out
    assert "- 5D main-fund inflow total: -121116.6178" in output
    assert "- 2026-07-01: -124116.6178" in output


def test_cli_prints_industry_context(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def industry(self, **kwargs: Any) -> dict[str, Any]:
            return {
                "kind": "industry",
                "fetched_at": "now",
                "source": {"list": "list-url"},
                "source_limits": ["auxiliary industry context"],
                "industry_id": kwargs.get("industry_id"),
                "industry_name": "半导体",
                "quote": {
                    "securityCode": "980017.CNI",
                    "securityName": "国证芯片",
                    "price": 17610.22,
                    "changePercent": 1.23,
                },
                "index_codes": [
                    {
                        "securityCode": "980017.CNI",
                        "securityName": "国证芯片",
                        "securityDesc": "反映A股市场芯片产业全产业链表现。",
                    }
                ],
                "classify": [
                    {
                        "industryClassifyName": "需求指标",
                        "indicators": [
                            {
                                "indicatorId": "001004",
                                "indicatorName": "全球半导体销售额",
                            }
                        ],
                    }
                ],
                "indicator_detail": {
                    "indicatorId": "001004",
                    "indicatorName": "全球半导体销售额",
                    "rows": [
                        {
                            "indicatorTm": "2026-12-31",
                            "indicatorValue": "9754.60",
                            "yoy": 23.21,
                        }
                    ],
                },
                "related_indicators": {
                    "indicatorTotal": 8,
                    "rows": [
                        {
                            "indicatorDataName": "全球半导体销售额",
                            "indicatorValue": "9754.60",
                        }
                    ],
                },
                "chart": {
                    "securityName": "沪深300",
                    "chartDimension": "近10年",
                    "dimensionChange": 12.3,
                },
                "chart_rows": [
                    {"tradeDate": "2026-07-01", "intervalChangePercent": 0.52}
                ],
                "memoirs": [
                    {
                        "memoirTime": "2026-06-11 12:00:00",
                        "memoirTitle": "韩国6月上旬出口再创历史新高",
                    }
                ],
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["industry", "--industry-id", "industry_semiconductor"]) == 0

    output = capsys.readouterr().out
    assert "# Red Rocket industry (now)" in output
    assert "- Industry: industry_semiconductor 半导体" in output
    assert "- Representative index: 980017.CNI 国证芯片 17610.22 1.23%" in output
    assert "- 980017.CNI 国证芯片: 反映A股市场芯片产业全产业链表现。" in output
    assert "- 需求指标: 001004 全球半导体销售额" in output
    assert "- 全球半导体销售额: 2026-12-31 9754.60 yoy 23.21" in output
    assert "- Chart: 沪深300 近10年 change 12.3" in output
    assert "- 2026-06-11 12:00:00 韩国6月上旬出口再创历史新高" in output
    assert "- Source limit: auxiliary industry context" in output


def test_cli_prints_fund_source_limits(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def fund(self, fund_code: str, **kwargs: Any) -> dict[str, Any]:
            return {
                "kind": "fund",
                "fetched_at": "now",
                "source": {"base": "url"},
                "fund_code": fund_code,
                "source_limits": ["verify fund company and sales-channel rules"],
                "base": {},
                "situation": {},
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["fund", "110020"]) == 0

    output = capsys.readouterr().out
    assert "- Source limit: verify fund company and sales-channel rules" in output


def test_cli_prints_fund_notice_detail_links(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def fund_notices(self, fund_code: str, **kwargs: Any) -> dict[str, Any]:
            return {
                "kind": "fund_notices",
                "fetched_at": "now",
                "source": {"list": "list-url", "detail": "detail-url"},
                "source_limits": ["verify fund company announcement page"],
                "fund_code": fund_code,
                "rows": [
                    {
                        "id": "notice-1",
                        "title": "基金公告",
                        "announceTime": "2026-07-01",
                    }
                ],
                "detail": {
                    "id": "notice-1",
                    "title": "基金公告",
                    "announceTime": "2026-07-01",
                    "attachmentUrls": ["https://example.test/notice.pdf"],
                },
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["fund-notices", "110020", "--detail-id", "notice-1"]) == 0

    output = capsys.readouterr().out
    assert "https://example.test/notice.pdf" in output


def test_cli_prints_news_status_id_for_article_lookup(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def news(self, **kwargs: Any) -> dict[str, Any]:
            return {
                "kind": "news",
                "fetched_at": "now",
                "source": "url",
                "rows": [
                    {
                        "id": "5042",
                        "statusId": "N2607010744100459043",
                        "title": "工业互联网政策",
                        "securityCode": "950180.CSI",
                        "securityName": "科创AI",
                    }
                ],
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["news"]) == 0

    output = capsys.readouterr().out
    assert "| id | statusId | securityCode | securityName | title |" in output
    assert "N2607010744100459043" in output


def test_cli_prints_must_read_status_ids_for_article_lookup(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def must_read(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            return {
                "kind": "must_read",
                "fetched_at": "now",
                "source": "url",
                "security_code": security_code,
                "big_event": {
                    "statusId": "N2607011526280455070",
                    "title": "AI 年中盘点",
                },
                "rows": [
                    {
                        "statusId": "N2607010744100459043",
                        "title": "工业互联网政策",
                        "contentLabel": "AI",
                        "nickName": "财联社",
                    }
                ],
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["must-read", "000300.SH"]) == 0

    output = capsys.readouterr().out
    assert "- Big event: N2607011526280455070 AI 年中盘点" in output
    assert "- N2607010744100459043 工业互联网政策 [AI] 财联社" in output


def test_cli_prints_hot_timeline_rows(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def hot_timeline(self, **kwargs: Any) -> dict[str, Any]:
            return {
                "kind": "hot_timeline",
                "fetched_at": "now",
                "source": {"timeline": "url"},
                "source_limits": ["auxiliary market-event context"],
                "show_status": True,
                "rows": [
                    {
                        "changeTime": "2026-07-01 15:03:15",
                        "content": "A股三大指数收盘涨跌不一。",
                        "relatedIndexes": [
                            {"indexCode": "000001.SH", "indexName": "上证指数"}
                        ],
                        "relatedEtfs": [
                            {"indexCode": "510210.SH", "indexName": "上证指数ETF富国"}
                        ],
                    }
                ],
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["hot-timeline"]) == 0

    output = capsys.readouterr().out
    assert "# Red Rocket hot timeline" in output
    assert "- Show status: True" in output
    assert "- 2026-07-01 15:03:15 A股三大指数收盘涨跌不一。" in output
    assert "Indexes: 000001.SH 上证指数" in output
    assert "ETFs: 510210.SH 上证指数ETF富国" in output


def test_cli_prints_signal_detail_summary(monkeypatch, capsys) -> None:
    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def signal_detail(self, security_code: str, **kwargs: Any) -> dict[str, Any]:
            return {
                "kind": "signal_detail",
                "fetched_at": "now",
                "source": "url",
                "source_limits": ["methodology output"],
                "security_code": security_code,
                "score_area": {
                    "securityName": "沪深300",
                    "score": 35.8,
                    "scoreLabel": "保持关注",
                    "scoreDate": "2026.07.01",
                    "tips": "或可持续观望",
                },
                "score_details": [
                    {"title": "估值", "score": 45.0, "avg": 50.0, "pointerType": "neutral"}
                ],
                "related_product": {"productCode": "000051.OF", "productName": "沪深300联接A"},
            }

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["signal-detail", "000300.SH"]) == 0

    output = capsys.readouterr().out
    assert "# Red Rocket signal detail" in output
    assert "- Security: 000300.SH 沪深300" in output
    assert "- Score: 35.8 保持关注" in output
    assert "- 估值: score 45.0, avg 50.0, pointer neutral" in output
    assert "- Related product: 000051.OF 沪深300联接A" in output
