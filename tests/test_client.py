from __future__ import annotations

from typing import Any

from redrocket_market.client import (
    ARTICLE_CONTENT_EXCERPT_MAX,
    BATCH_PRICE_PERCENT_ENDPOINT,
    BATCH_QUOTE_ENDPOINT,
    COMMUNITY_STATUS_DETAIL_ENDPOINT,
    COMPARE_ARCHIVES_ENDPOINT,
    COMPARE_CHART_ENDPOINT,
    COMPARE_COMPONENT_ENDPOINT,
    COMPARE_FUND_LIST_ENDPOINT,
    COMPARE_INDUSTRY_LEVEL_ENDPOINT,
    COMPARE_INTERVAL_CHANGE_ENDPOINT,
    COMPARE_MARKET_VALUE_ENDPOINT,
    COMPARE_MINUTE_CHART_ENDPOINT,
    COMPARE_PERFORMANCE_CORRELATION_ENDPOINT,
    COMPARE_SPECIAL_MARKET_ENDPOINT,
    COMPONENT_STOCK_ENDPOINT,
    ETF_FIVE_MFD_INFLOW_ENDPOINT,
    ETF_NET_SUBSCRIPTION_ENDPOINT,
    ETF_LINK_FUND_ENDPOINT,
    ETF_MARGIN_ENDPOINT,
    ETF_PANORAMA_ENDPOINT,
    ETF_QUOTE_ENDPOINT,
    ETF_LIST_ENDPOINT,
    ETF_SHARE_CHANGE_ENDPOINT,
    FUND_ASSET_DISTRIBUTION_ENDPOINT,
    FUND_ANNOUNCEMENT_DETAIL_ENDPOINT,
    FUND_ANNOUNCEMENT_LIST_ENDPOINT,
    FUND_COMPONENTS_ENDPOINT,
    FUND_HISTORY_NAV_ENDPOINT,
    FUND_NAV_CHART_ENDPOINT,
    FUND_PERFORMANCE_CHART_ENDPOINT,
    FUND_SALE_STATUS_ENDPOINT,
    COMPARE_SIMILARITY_ENDPOINT,
    COMPARE_RECOMMEND_ENDPOINT,
    COMPARE_TEN_WEIGHT_STOCK_ENDPOINT,
    COMPARE_VALUATION_GROWTH_ENDPOINT,
    VALUATION_ROE_TIME_ENDPOINT,
    CLASS_INFO_ENDPOINT,
    FOCUS_NEWS_ENDPOINT,
    HOME_PAGE_CONTENT_ENDPOINT,
    HEAT_ENDPOINT,
    HOT_LIST_ENDPOINT,
    HOT_SHOW_STATUS_ENDPOINT,
    INDUSTRY_CHART_ENDPOINT,
    INDUSTRY_CLASSIFY_DATA_ENDPOINT,
    INDUSTRY_CLASSIFY_ENDPOINT,
    INDUSTRY_INDEX_CODES_ENDPOINT,
    INDUSTRY_ID_ENDPOINT,
    INDUSTRY_LIST_ENDPOINT,
    INDUSTRY_MEMOIR_ENDPOINT,
    INDUSTRY_QUOTE_ENDPOINT,
    INDUSTRY_RELATED_ENDPOINT,
    INDEX_ARCHIVES_ENDPOINT,
    INDEX_COMPONENT_ENDPOINT,
    INDEX_LABEL_ENDPOINT,
    INDEX_MAIN_FUND_ENDPOINT,
    INDEX_REVENUE_PROFIT_ENDPOINT,
    INDEX_RISK_RETURN_ENDPOINT,
    INDEX_ROE_ENDPOINT,
    INDEX_VALUATION_ENDPOINT,
    KNOWLEDGE_ENDPOINT,
    MANAGER_DETAIL_ENDPOINT,
    MUST_READ_ENDPOINT,
    NEWS_ENDPOINT,
    SECURITY_CHANGE_LIST_ENDPOINT,
    SECURITY_CHART_ENDPOINT,
    SECURITY_COMPONENT_DEVELOP_ENDPOINT,
    SECURITY_D5_MINUTE_ENDPOINT,
    SECURITY_HISTORY_POSITION_ENDPOINT,
    SECURITY_INDUSTRY_DISTRIBUTION_ENDPOINT,
    SECURITY_INFO_ENDPOINT,
    SECURITY_MARKET_VALUE_DISTRIBUTE_ENDPOINT,
    SECURITY_MINUTE_ENDPOINT,
    SECURITY_MUST_SEE_ENDPOINT,
    SECURITY_TYPE_ENDPOINT,
    SECURITY_WEIGHT_CONCENTRATION_ENDPOINT,
    SIGNAL_DETAIL_ENDPOINT,
    TRACKING_INDEX_ENDPOINT,
    WIND_ENDPOINT,
    RedRocketClient,
    RequestResult,
    clean_text,
    extract_rows,
    normalize_fund_code,
    normalize_security,
)


DISCOVERY_SOURCE_LIMITS = [
    "Red Rocket valuation, flow, heat, news, wind-vane, and comparison rows are auxiliary discovery context, not standalone investment signals.",
    "Verify exchange quotes, fund announcements, sales-channel rules, and local investment policy before decision use.",
]

FUND_SOURCE_LIMITS = [
    "Red Rocket fund profiles, NAV/performance chart summaries, notices, manager background, sale status, and asset allocation are auxiliary context, not official fund-company, benchmark, exchange, or sales-channel records.",
    "Verify fund company NAV disclosures, benchmark/exchange data, actual sales-channel limits, fees, settlement rules, and local investment policy before decision use.",
]

def test_normalize_fund_code_adds_of_suffix() -> None:
    assert normalize_fund_code("110020") == "110020.OF"
    assert normalize_fund_code("110020.OF") == "110020.OF"


def test_extract_rows_accepts_common_payload_shapes() -> None:
    assert extract_rows({"data": [{"a": 1}, "x", {"b": 2}]}) == [{"a": 1}, {"b": 2}]
    assert extract_rows([{"a": 1}]) == [{"a": 1}]
    assert extract_rows({"data": {"not": "rows"}}) == []


def test_normalize_security_keeps_known_fields() -> None:
    row = {
        "securityCode": "000300.SH",
        "securityName": "沪深300",
        "pePercent": 42.5,
        "unknown": "drop",
    }
    assert normalize_security(row) == {
        "securityCode": "000300.SH",
        "securityName": "沪深300",
        "pePercent": 42.5,
    }


def test_clean_text_preserves_block_boundaries() -> None:
    assert clean_text("<p>低估</p><p>正常</p><ul><li>高估</li></ul>") == "低估 正常 高估"


class RecordingClient(RedRocketClient):
    def __init__(self, responses: dict[str, Any]) -> None:
        super().__init__()
        self.responses = responses
        self.get_calls: list[tuple[str, dict[str, str] | None]] = []
        self.post_calls: list[tuple[str, dict[str, str] | None, Any]] = []

    def get(self, path: str, params: dict[str, str] | None = None) -> RequestResult:
        self.get_calls.append((path, params))
        return RequestResult(self.responses.get(path, []), f"https://example.test{path}")

    def post(
        self,
        path: str,
        params: dict[str, str] | None = None,
        payload: Any | None = None,
    ) -> RequestResult:
        self.post_calls.append((path, params, payload))
        return RequestResult(self.responses.get(path, []), f"https://example.test{path}")


def test_etf_scan_defaults_to_etf_scale_order() -> None:
    client = RecordingClient({ETF_LIST_ENDPOINT: {"data": []}})

    client.scan("wide", etf=True)

    assert client.get_calls[0][0] == ETF_LIST_ENDPOINT
    assert client.get_calls[0][1]["orderBy"] == "l.scale"


def test_search_enriches_rows_with_batch_quote_data() -> None:
    client = RecordingClient(
        {
            "/fundex-quote/search/list": {
                "index": [
                    {
                        "securityCode": "000300.SH",
                        "securityType": "01",
                        "securityName": "沪深300",
                        "securityFullName": "沪深300指数",
                    }
                ],
                "etf": [
                    {
                        "securityCode": "510300.SH",
                        "securityType": "02",
                        "securityName": "沪深300ETF华泰柏瑞",
                    }
                ],
                "fund": [
                    {
                        "securityCode": "110020.OF",
                        "securityType": "04",
                        "securityName": "易方达沪深300ETF联接A",
                    }
                ],
                "stock": [
                    {
                        "securityCode": "000977.SZ",
                        "securityType": "03",
                        "securityName": "浪潮信息",
                    }
                ],
            },
            BATCH_QUOTE_ENDPOINT: {
                "indexList": [
                    {
                        "securityCode": "000300.SH",
                        "price": 4958.98,
                        "dayChangePercent": -0.4107,
                        "yearChangePercent": 12.34,
                        "componentStockCount": 300,
                        "relatedFundCount": 266,
                    }
                ],
                "etfList": [
                    {
                        "securityCode": "510300.SH",
                        "price": 4.988,
                        "dayChangePercent": -0.38,
                        "relatedFundScale": 1111.22,
                        "trackingIndex": "沪深300",
                    }
                ],
                "fundList": [
                    {
                        "securityCode": "110020.OF",
                        "price": 1.994,
                        "dayChangePercent": -0.39,
                        "relatedFundScale": 88.12,
                    }
                ],
                "stockList": [
                    {
                        "securityCode": "000977.SZ",
                        "price": 55.0,
                        "dayChangePercent": 1.23,
                        "marketValue": 80800000000,
                        "industryInvolved": "计算机设备",
                    }
                ],
            },
        }
    )

    result = client.search("沪深300", limit=4)

    assert client.get_calls == [
        (
            "/fundex-quote/search/list",
            {"searchKeyword": "沪深300", "isSearchAll": "false"},
        )
    ]
    assert client.post_calls == [
        (
            BATCH_QUOTE_ENDPOINT,
            None,
            {
                "securityType": "all",
                "securityCodeList": [
                    "000300.SH",
                    "510300.SH",
                    "110020.OF",
                    "000977.SZ",
                ],
            },
        )
    ]
    assert result["kind"] == "search"
    assert result["source"] == {
        "list": "https://example.test/fundex-quote/search/list",
        "batch_quote": "https://example.test/fundex-quote/search/batchQueryQuoteData",
    }
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["groups"] == {"index": 1, "etf": 1, "fund": 1, "stock": 1}
    assert result["rows"] == [
        {
            "securityCode": "000300.SH",
            "securityType": "01",
            "securityName": "沪深300",
            "securityFullName": "沪深300指数",
            "price": 4958.98,
            "dayChangePercent": -0.4107,
            "yearChangePercent": 12.34,
            "componentStockCount": 300,
            "relatedFundCount": 266,
        },
        {
            "securityCode": "510300.SH",
            "securityType": "02",
            "securityName": "沪深300ETF华泰柏瑞",
            "price": 4.988,
            "dayChangePercent": -0.38,
            "relatedFundScale": 1111.22,
            "trackingIndex": "沪深300",
        },
        {
            "securityCode": "110020.OF",
            "securityType": "04",
            "securityName": "易方达沪深300ETF联接A",
            "price": 1.994,
            "dayChangePercent": -0.39,
            "relatedFundScale": 88.12,
        },
        {
            "securityCode": "000977.SZ",
            "securityType": "03",
            "securityName": "浪潮信息",
            "price": 55.0,
            "dayChangePercent": 1.23,
            "marketValue": 80800000000,
            "industryInvolved": "计算机设备",
        },
    ]


def test_search_skips_batch_quote_when_no_codes() -> None:
    client = RecordingClient(
        {
            "/fundex-quote/search/list": {
                "index": [],
                "etf": [],
                "fund": [],
                "stock": [],
            }
        }
    )

    result = client.search("不存在", limit=4)

    assert client.post_calls == []
    assert result["source"] == {"list": "https://example.test/fundex-quote/search/list"}
    assert result["rows"] == []


def test_search_enriches_fund_rows_keyed_by_fund_code() -> None:
    client = RecordingClient(
        {
            "/fundex-quote/search/list": {
                "fund": [
                    {
                        "fundCode": "110020.OF",
                        "securityType": "04",
                        "fundName": "易方达沪深300ETF联接A",
                    }
                ]
            },
            BATCH_QUOTE_ENDPOINT: {
                "fundList": [
                    {
                        "fundCode": "110020.OF",
                        "price": 1.994,
                        "dayChangePercent": -0.39,
                        "relatedFundScale": 88.12,
                    }
                ],
            },
        }
    )

    result = client.search("110020", limit=3)

    assert client.post_calls == [
        (
            BATCH_QUOTE_ENDPOINT,
            None,
            {"securityType": "all", "securityCodeList": ["110020.OF"]},
        )
    ]
    assert result["rows"] == [
        {
            "securityType": "04",
            "fundCode": "110020.OF",
            "fundName": "易方达沪深300ETF联接A",
            "price": 1.994,
            "dayChangePercent": -0.39,
            "relatedFundScale": 88.12,
        }
    ]


def test_snapshot_reads_lightweight_price_and_security_type_metadata() -> None:
    client = RecordingClient(
        {
            BATCH_PRICE_PERCENT_ENDPOINT: [
                {
                    "securityCode": "000300.SH",
                    "securityName": "沪深300",
                    "price": 4958.98,
                    "changePercent": -0.4107,
                    "tradeDate": "2026-07-01",
                    "quoteInit": False,
                    "follow": False,
                },
                {
                    "securityCode": "159819.SZ",
                    "securityName": "人工智能ETF",
                    "price": 0.886,
                    "changePercent": 0.58,
                    "tradeDate": "2026-07-01",
                    "quoteInit": False,
                    "follow": False,
                },
            ],
            SECURITY_TYPE_ENDPOINT: {
                "securityCode": "159819.SZ",
                "securityAbbreviation": "人工智能ETF",
                "securityType": "02",
                "securityExchmarket": "SZ",
                "isDelay": False,
            },
        }
    )

    result = client.snapshot("000300.SH,159819.SZ")

    assert client.post_calls == [
        (
            BATCH_PRICE_PERCENT_ENDPOINT,
            {"securityCodes": "000300.SH,159819.SZ"},
            {"securityCodes": ["000300.SH", "159819.SZ"]},
        )
    ]
    assert client.get_calls == [
        (SECURITY_TYPE_ENDPOINT, {"securityCode": "000300.SH"}),
        (SECURITY_TYPE_ENDPOINT, {"securityCode": "159819.SZ"}),
    ]
    assert result["kind"] == "snapshot"
    assert result["source"] == {
        "snapshot": "https://example.test/fundex-quote/security/batchFindPriceAndPercent",
        "security_type": "https://example.test/fundex-quote/securityInfo/findSecurityType",
    }
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["security_codes"] == "000300.SH,159819.SZ"
    assert result["rows"] == [
        {
            "securityCode": "000300.SH",
            "securityName": "沪深300",
            "securityExchmarket": "SH",
            "price": 4958.98,
            "changePercent": -0.4107,
            "tradeDate": "2026-07-01",
            "quoteInit": False,
            "follow": False,
        },
        {
            "securityCode": "159819.SZ",
            "securityName": "人工智能ETF",
            "securityAbbreviation": "人工智能ETF",
            "securityType": "02",
            "securityExchmarket": "SZ",
            "isDelay": False,
            "price": 0.886,
            "changePercent": 0.58,
            "tradeDate": "2026-07-01",
            "quoteInit": False,
            "follow": False,
        },
    ]


def test_fund_components_use_post_security_code_query() -> None:
    client = RecordingClient(
        {
            "/fundex-quote/fund/otcFundBase": {"fundName": "测试基金"},
            "/fundex-quote/fund/fundSituation": {"fundFullName": "测试基金"},
            FUND_COMPONENTS_ENDPOINT: {
                "endDate": "20260331",
                "stockList": [{"dataCode": "600519.SH", "dataName": "贵州茅台"}],
            },
            FUND_HISTORY_NAV_ENDPOINT: {"data": [{"netValueDate": "2026-06-30"}]},
            FUND_NAV_CHART_ENDPOINT: [
                {"value": "1.0000", "dateValue": "2026-06-01"},
                {"value": "1.1200", "dateValue": "2026-07-01"},
            ],
            FUND_PERFORMANCE_CHART_ENDPOINT: {
                "defaultExponentCode": "000300.SH",
                "defaultExponentName": "沪深300",
                "pointList": [
                    {"value": "0.00%", "dateValue": "2026-06-01"},
                    {"value": "12.00%", "dateValue": "2026-07-01"},
                ],
                "exponentPointList": [
                    {"value": "0.00%", "dateValue": "2026-06-01"},
                    {"value": "8.00%", "dateValue": "2026-07-01"},
                ],
                "exponentList": [
                    {"exponentCode": "000300.SH", "exponentName": "沪深300"},
                ],
            },
            FUND_SALE_STATUS_ENDPOINT: {
                "fundCode": "110020.OF",
                "richChannel": "1",
                "financialLinkChannel": "0",
                "securityType": "04",
            },
            FUND_ASSET_DISTRIBUTION_ENDPOINT: {
                "endDate": "20260331",
                "assetDataList": [{"assetName": "股票", "assetVal": "80.00"}],
                "assetWeightDataList": [
                    {"dataCode": "600519.SH", "dataName": "贵州茅台", "dataValueToNav": "5.00"}
                ],
            },
        }
    )

    result = client.fund("110020", limit=3)

    assert result["source_limits"] == FUND_SOURCE_LIMITS
    assert client.post_calls == [
        (FUND_COMPONENTS_ENDPOINT, {"securityCode": "110020.OF"}, {}),
        (FUND_ASSET_DISTRIBUTION_ENDPOINT, {"securityCode": "110020.OF"}, {}),
    ]
    assert (
        FUND_NAV_CHART_ENDPOINT,
        {"fundCode": "110020.OF", "netType": "netUnit", "dateType": "oneYear"},
    ) in client.get_calls
    assert (
        FUND_PERFORMANCE_CHART_ENDPOINT,
        {"fundCode": "110020.OF", "exponentCode": "", "dateType": "oneYear"},
    ) in client.get_calls
    assert (FUND_SALE_STATUS_ENDPOINT, {"fundCode": "110020.OF"}) in client.get_calls
    assert result["components"] == [
        {"section": "stock", "dataCode": "600519.SH", "dataName": "贵州茅台"}
    ]
    assert result["sale_status"] == {
        "fundCode": "110020.OF",
        "richChannel": "1",
        "financialLinkChannel": "0",
        "securityType": "04",
    }
    assert result["asset_allocation"] == [{"assetName": "股票", "assetVal": "80.00"}]
    assert result["nav_chart"] == {
        "points": 2,
        "firstDate": "2026-06-01",
        "firstValue": 1.0,
        "lastDate": "2026-07-01",
        "lastValue": 1.12,
        "changePercent": 12.0,
    }
    assert result["performance_chart"] == {
        "defaultExponentCode": "000300.SH",
        "defaultExponentName": "沪深300",
        "fund": {
            "points": 2,
            "firstDate": "2026-06-01",
            "firstValue": 0.0,
            "lastDate": "2026-07-01",
            "lastValue": 12.0,
            "changePercent": 12.0,
        },
        "benchmark": {
            "points": 2,
            "firstDate": "2026-06-01",
            "firstValue": 0.0,
            "lastDate": "2026-07-01",
            "lastValue": 8.0,
            "changePercent": 8.0,
        },
        "availableExponents": [{"exponentCode": "000300.SH", "exponentName": "沪深300"}],
    }


def test_index_reads_archives_labels_and_roe() -> None:
    client = RecordingClient(
        {
            INDEX_ARCHIVES_ENDPOINT: {
                "security": {
                    "securityCode": "000300.SH",
                    "securityName": "沪深300指数",
                    "publisher": "中证指数有限公司",
                    "componentCount": 300,
                    "etfCount": 30,
                    "otcCount": 266,
                    "scale": 353986378214.173,
                    "fundCode": "000051.OF",
                    "fundName": "华夏沪深300ETF联接A",
                }
            },
            INDEX_LABEL_ENDPOINT: {
                "valuationTypeLabel": "PE",
                "valuationExists": True,
                "roeExists": True,
                "componentExists": True,
            },
            INDEX_ROE_ENDPOINT: {
                "reportDate": "03-31",
                "items": [
                    {"date": "2025-12-31", "value": "9.67%"},
                    {"date": "2026-03-31", "value": "9.37%"},
                ],
            },
        }
    )

    result = client.index("000300.SH", limit=1)

    assert client.get_calls == [
        (INDEX_ARCHIVES_ENDPOINT, {"securityCode": "000300.SH"}),
        (INDEX_LABEL_ENDPOINT, {"securityCode": "000300.SH"}),
        (INDEX_ROE_ENDPOINT, {"securityCode": "000300.SH"}),
    ]
    assert result["summary"] == {
        "securityCode": "000300.SH",
        "securityName": "沪深300指数",
        "publisher": "中证指数有限公司",
        "componentCount": 300,
        "etfCount": 30,
        "otcCount": 266,
        "scale": 353986378214.173,
        "fundCode": "000051.OF",
        "fundName": "华夏沪深300ETF联接A",
    }
    assert result["labels"] == {
        "valuationTypeLabel": "PE",
        "valuationExists": True,
        "roeExists": True,
        "componentExists": True,
    }
    assert result["roe"] == [{"date": "2026-03-31", "value": "9.37%"}]


def test_components_reads_full_component_stock_endpoint() -> None:
    client = RecordingClient(
        {
            COMPONENT_STOCK_ENDPOINT: {
                "total": 300,
                "industryType": "02",
                "showUpdateStr": "2026-07-01 盘中实时更新",
                "componentStockListVos": [
                    {
                        "securityCode": "600519.SH",
                        "securityName": "贵州茅台",
                        "weight": 5.12,
                        "changePercent": 1.23,
                        "netCapitalFlow": 100,
                        "priceEarningRatioTtm": 22.5,
                    },
                    {"securityCode": "300750.SZ", "securityName": "宁德时代", "weight": 2.3},
                ],
            }
        }
    )

    result = client.components("000300.SH", limit=1)

    assert client.get_calls == [
        (COMPONENT_STOCK_ENDPOINT, {"securityCode": "000300.SH", "isAll": "1"})
    ]
    assert result["total"] == 300
    assert result["update"] == "2026-07-01 盘中实时更新"
    assert result["rows"] == [
        {
            "securityCode": "600519.SH",
            "securityName": "贵州茅台",
            "weight": 5.12,
            "changePercent": 1.23,
            "netCapitalFlow": 100,
            "priceEarningRatioTtm": 22.5,
        }
    ]


def test_security_context_reads_runtime_security_context() -> None:
    client = RecordingClient(
        {
            SECURITY_INFO_ENDPOINT: {
                "securityCode": "000300.SH",
                "securityName": "沪深300",
                "securityType": "01",
                "securityCount": 300,
                "listingTimeFlag": "已发布",
            },
            SECURITY_CHANGE_LIST_ENDPOINT: [
                {"tradeDate": "2026-07-01", "changePercent": -0.41, "price": 4958.98}
            ],
            SECURITY_MINUTE_ENDPOINT: {
                "items": [
                    {"minute": "14:56", "price": 4958.98, "changePercent": -0.41}
                ],
            },
            SECURITY_CHART_ENDPOINT: {
                "benchmark": {
                    "securityCode": "000300.SH",
                    "securityName": "沪深300",
                    "itemsSize": 2,
                    "performance": {"yearlyPerformance": 12.3},
                    "items": [
                        {"tradeDate": "2026-06-30", "intervalChangePercent": 0.1},
                        {"tradeDate": "2026-07-01", "intervalChangePercent": 0.2},
                    ],
                },
                "security": {
                    "securityCode": "000300.SH",
                    "securityName": "沪深300",
                    "itemsSize": 2,
                    "performance": {"yearlyPerformance": 12.3},
                    "items": [
                        {"tradeDate": "2026-06-30", "intervalChangePercent": 0.1},
                        {"tradeDate": "2026-07-01", "intervalChangePercent": 0.2},
                    ],
                },
            },
            SECURITY_D5_MINUTE_ENDPOINT: {
                "securityCode": "000300.SH",
                "securityName": "沪深300指数",
                "itemsSize": 2,
                "columns": (
                    "tradeDate,price,changePercent,change,volume,avgPrice,amount,"
                    "datetime,ratio,weekly,minuteByHours,intervalChangePercent"
                ),
                "items": (
                    "2026-06-26,4981.83,-0.76,-38.27,292847200.000,29.830,"
                    "8735598700.000,2026-06-26 09:30,,星期五,09:30,-0.0076;"
                    "2026-07-01,5002.10,0.12,6.00,100.000,30.100,3000.000,"
                    "2026-07-01 14:56,,星期三,14:56,0.0012"
                ),
            },
            SECURITY_HISTORY_POSITION_ENDPOINT: {
                "items": [{"tradeDate": "2026-06-30", "weight": 1.23}]
            },
            SECURITY_MARKET_VALUE_DISTRIBUTE_ENDPOINT: {
                "items": [{"name": "大盘", "weight": 70.2}]
            },
            SECURITY_WEIGHT_CONCENTRATION_ENDPOINT: {
                "items": [{"name": "前十大权重", "weight": 28.3}]
            },
        }
    )

    result = client.security_context("000300.SH", limit=1)

    assert client.get_calls == [
        (SECURITY_INFO_ENDPOINT, {"securityCode": "000300.SH"}),
        (SECURITY_CHANGE_LIST_ENDPOINT, {"securityCode": "000300.SH"}),
        (SECURITY_MINUTE_ENDPOINT, {"securityCode": "000300.SH"}),
        (SECURITY_CHART_ENDPOINT, {"securityCode": "000300.SH", "period": "1Y"}),
        (SECURITY_D5_MINUTE_ENDPOINT, {"securityCode": "000300.SH"}),
        (SECURITY_HISTORY_POSITION_ENDPOINT, {"securityCode": "000300.SH"}),
        (SECURITY_MARKET_VALUE_DISTRIBUTE_ENDPOINT, {"securityCode": "000300.SH"}),
        (SECURITY_WEIGHT_CONCENTRATION_ENDPOINT, {"securityCode": "000300.SH"}),
    ]
    assert result["kind"] == "security_context"
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["info"] == {
        "securityCode": "000300.SH",
        "securityName": "沪深300",
        "securityType": "01",
        "securityCount": 300,
        "listingTimeFlag": "已发布",
    }
    assert result["change_rows"] == [
        {"tradeDate": "2026-07-01", "changePercent": -0.41, "price": 4958.98}
    ]
    assert result["minute_rows"] == [
        {"minute": "14:56", "price": 4958.98, "changePercent": -0.41}
    ]
    assert result["chart"] == {
        "benchmark": {
            "securityCode": "000300.SH",
            "securityName": "沪深300",
            "itemsSize": 2,
            "performance": {"yearlyPerformance": 12.3},
        },
        "security": {
            "securityCode": "000300.SH",
            "securityName": "沪深300",
            "itemsSize": 2,
            "performance": {"yearlyPerformance": 12.3},
        },
    }
    assert result["chart_rows"] == [
        {
            "tradeDate": "2026-07-01",
            "intervalChangePercent": 0.2,
            "benchmarkIntervalChangePercent": 0.2,
        }
    ]
    assert result["five_day_minute_rows"] == [
        {
            "tradeDate": "2026-07-01",
            "price": 5002.10,
            "changePercent": 0.12,
            "change": 6.00,
            "volume": 100.0,
            "avgPrice": 30.1,
            "amount": 3000.0,
            "datetime": "2026-07-01 14:56",
            "weekly": "星期三",
            "minuteByHours": "14:56",
            "intervalChangePercent": 0.0012,
        }
    ]
    assert result["history_position"] == [{"tradeDate": "2026-06-30", "weight": 1.23}]
    assert result["market_value_distribution"] == [{"name": "大盘", "weight": 70.2}]
    assert result["weight_concentration"] == [{"name": "前十大权重", "weight": 28.3}]


def test_security_context_handles_live_nested_runtime_shapes() -> None:
    client = RecordingClient(
        {
            SECURITY_INFO_ENDPOINT: {
                "securityCode": "000300.SH",
                "securityName": "沪深300指数",
            },
            SECURITY_CHANGE_LIST_ENDPOINT: [],
            SECURITY_MINUTE_ENDPOINT: {
                "security": {
                    "items": [
                        {
                            "tradeDate": "2026-07-01",
                            "datetime": "2026-07-01 09:30",
                            "minuteByHours": "09:30",
                            "price": 4972.69,
                            "avgPrice": 24.685,
                            "changePercent": -0.14,
                            "intervalChangePercent": None,
                        },
                        {
                            "tradeDate": "2026-07-01",
                            "datetime": "2026-07-01 09:31",
                            "minuteByHours": "09:31",
                            "price": 4981.85,
                            "avgPrice": 27.205,
                            "changePercent": 0.05,
                        },
                    ]
                }
            },
            SECURITY_CHART_ENDPOINT: {
                "benchmark": {
                    "securityCode": "000300.SH",
                    "securityName": "沪深300",
                    "items": [{"tradeDate": "2026-07-01", "intervalChangePercent": 0.11}],
                },
                "security": {
                    "securityCode": "000300.SH",
                    "securityName": "沪深300",
                    "items": [{"tradeDate": "2026-07-01", "intervalChangePercent": 0.11}],
                },
            },
            SECURITY_D5_MINUTE_ENDPOINT: {
                "columns": "tradeDate,price,changePercent,datetime,minuteByHours",
                "items": "2026-07-01,4981.85,0.05,2026-07-01 09:31,09:31",
            },
            SECURITY_HISTORY_POSITION_ENDPOINT: {
                "positionChangeDate": "2026-06-30",
                "latest": {
                    "indexComponentPOs": [
                        {
                            "indexCode": "000300.SH",
                            "securityCode": "300308.SZ",
                            "securityAbbreviation": "中际旭创",
                            "weight": 5.008,
                            "weightChangeFlag": "1",
                        }
                    ]
                },
            },
            SECURITY_MARKET_VALUE_DISTRIBUTE_ENDPOINT: {
                "largeCapStockCount": 270,
                "middleCapStockCount": 30,
                "totalMarketValue": 68611064255966.85,
                "avgMarketValue": 228703547519.8895,
                "tradeDate": "2026-07-01",
                "currencyCode": "CNY",
            },
            SECURITY_WEIGHT_CONCENTRATION_ENDPOINT: [
                {"annDate": "2021-07-30", "cr5": 15.301, "cr10": 22.316},
                {"annDate": "2026-07-01", "cr5": 11.1, "cr10": 20.2, "cr20": 31.3},
            ],
        }
    )

    result = client.security_context("000300.SH", limit=1)

    assert result["minute_rows"] == [
        {
            "tradeDate": "2026-07-01",
            "datetime": "2026-07-01 09:31",
            "minuteByHours": "09:31",
            "price": 4981.85,
            "avgPrice": 27.205,
            "changePercent": 0.05,
        }
    ]
    assert result["history_position"] == [
        {
            "indexCode": "000300.SH",
            "securityCode": "300308.SZ",
            "securityName": "中际旭创",
            "weight": 5.008,
            "weightChangeFlag": "1",
        }
    ]
    assert result["market_value_distribution"] == [
        {
            "tradeDate": "2026-07-01",
            "largeCapStockCount": 270,
            "middleCapStockCount": 30,
            "totalMarketValue": 68611064255966.85,
            "avgMarketValue": 228703547519.8895,
            "currencyCode": "CNY",
        }
    ]
    assert result["weight_concentration"] == [
        {"annDate": "2026-07-01", "cr5": 11.1, "cr10": 20.2, "cr20": 31.3}
    ]
    assert result["chart_rows"] == [
        {
            "tradeDate": "2026-07-01",
            "intervalChangePercent": 0.11,
            "benchmarkIntervalChangePercent": 0.11,
        }
    ]
    assert result["five_day_minute_rows"] == [
        {
            "tradeDate": "2026-07-01",
            "price": 4981.85,
            "changePercent": 0.05,
            "datetime": "2026-07-01 09:31",
            "minuteByHours": "09:31",
        }
    ]


def test_fund_notices_reads_list_and_optional_detail() -> None:
    client = RecordingClient(
        {
            FUND_ANNOUNCEMENT_LIST_ENDPOINT: [
                {
                    "id": "40674473607",
                    "title": "高级管理人员变更公告",
                    "announceTime": "19小时前",
                    "content": None,
                }
            ],
            FUND_ANNOUNCEMENT_DETAIL_ENDPOINT: {
                "id": "40674473607",
                "title": "高级管理人员变更公告",
                "announceTime": "19小时前",
                "content": '<p><a href="https://example.test/a.pdf">查看附件</a></p>',
            },
        }
    )

    result = client.fund_notices("110020", limit=3, detail_id="40674473607")

    assert client.get_calls == [
        (
            FUND_ANNOUNCEMENT_LIST_ENDPOINT,
            {"pageNum": "1", "pageSize": "3", "fundCode": "110020.OF"},
        ),
        (FUND_ANNOUNCEMENT_DETAIL_ENDPOINT, {"id": "40674473607"}),
    ]
    assert result["rows"] == [
        {
            "id": "40674473607",
            "title": "高级管理人员变更公告",
            "announceTime": "19小时前",
        }
    ]
    assert result["detail"] == {
        "id": "40674473607",
        "title": "高级管理人员变更公告",
        "announceTime": "19小时前",
        "attachmentUrls": ["https://example.test/a.pdf"],
    }


def test_manager_reads_manager_detail_endpoint() -> None:
    client = RecordingClient(
        {
            MANAGER_DETAIL_ENDPOINT: [
                {
                    "id": "123",
                    "name": "张三",
                    "employmentPeriod": "3年",
                    "resume": "基金经理履历",
                    "managedSecurities": [
                        {"securityCode": "110020.OF", "securityName": "易方达沪深300ETF联接A"}
                    ],
                }
            ]
        }
    )

    result = client.manager("110020", limit=1)

    assert client.get_calls == [(MANAGER_DETAIL_ENDPOINT, {"securityCode": "110020.OF"})]
    assert result["rows"] == [
        {
            "id": "123",
            "name": "张三",
            "employmentPeriod": "3年",
            "resume": "基金经理履历",
            "managedSecurities": [
                {"securityCode": "110020.OF", "securityName": "易方达沪深300ETF联接A"}
            ],
        }
    ]


def test_etf_detail_reads_quote_panorama_and_subscription() -> None:
    client = RecordingClient(
        {
            ETF_QUOTE_ENDPOINT: {
                "securityCode": "510300.SH",
                "securityName": "沪深300ETF华泰柏瑞",
                "price": 4.974,
                "changePercent": -0.9,
                "marketTip": "交易中",
                "marketValue": 94082651419.8,
            },
            ETF_PANORAMA_ENDPOINT: {
                "securityInfo": {
                    "securityCode": "510300.SH",
                    "securityName": "华泰柏瑞沪深300ETF",
                    "establishDate": "2012-05-04",
                    "scale": 199913855988.24,
                    "securityCompany": "华泰柏瑞基金",
                },
                "fundManager": [{"name": "柳军"}],
                "performanceReview": [
                    {
                        "dateRangeName": "近1年",
                        "rangeChangePercent": 29.15,
                        "sameKindRank": "189",
                        "sameKindRankTotal": "244",
                        "rankTag": "靠后",
                    }
                ],
            },
            ETF_NET_SUBSCRIPTION_ENDPOINT: {
                "tradeDt": "06-30",
                "totalShare": 18914887700,
                "netSubscriptionShares": -1021500000,
                "netSubscriptionSharePct": -0.054,
                "subscriptionShareList": [
                    {"tradeDt": "2026-06-30", "netSubscriptionShares": -1021500000}
                ],
            },
        }
    )

    result = client.etf_detail("510300.SH", limit=1)

    assert client.get_calls == [
        (ETF_QUOTE_ENDPOINT, {"securityCode": "510300.SH"}),
        (ETF_PANORAMA_ENDPOINT, {"securityCode": "510300.SH"}),
        (ETF_NET_SUBSCRIPTION_ENDPOINT, {"securityCode": "510300.SH"}),
    ]
    assert result["quote"] == {
        "securityCode": "510300.SH",
        "securityName": "沪深300ETF华泰柏瑞",
        "price": 4.974,
        "changePercent": -0.9,
        "marketTip": "交易中",
        "marketValue": 94082651419.8,
    }
    assert result["profile"] == {
        "securityCode": "510300.SH",
        "securityName": "华泰柏瑞沪深300ETF",
        "establishDate": "2012-05-04",
        "scale": 199913855988.24,
        "securityCompany": "华泰柏瑞基金",
        "managerNames": "柳军",
    }
    assert result["subscription"] == {
        "tradeDt": "06-30",
        "totalShare": 18914887700,
        "netSubscriptionShares": -1021500000,
        "netSubscriptionSharePct": -0.054,
    }
    assert result["subscription_rows"] == [
        {"tradeDt": "2026-06-30", "netSubscriptionShares": -1021500000}
    ]


def test_heat_reads_home_heat_rows() -> None:
    client = RecordingClient(
        {
            HEAT_ENDPOINT: {
                "marketDate": "2026-06-30",
                "homeHeat": [
                    {
                        "securityCode": "000688.SH",
                        "securityAbbreviation": "科创50",
                        "changePercent": 3.84,
                    }
                ],
            }
        }
    )

    result = client.heat(limit=1)

    assert result["kind"] == "heat"
    assert result["market_date"] == "2026-06-30"
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["rows"] == [
        {"securityCode": "000688.SH", "securityName": "科创50", "changePercent": 3.84}
    ]


def test_home_reads_compact_home_page_discovery_context() -> None:
    client = RecordingClient(
        {
            HOME_PAGE_CONTENT_ENDPOINT: {
                "classInfo": [{"value": "01", "lable": "宽基指数"}],
                "homepageOrder": [
                    {
                        "key": "homeHeat",
                        "tag": "junior_home_heat",
                        "name": "小白涨跌热力图",
                        "title": "快看行情",
                        "state": "1",
                    }
                ],
                "homeHeatVo": {
                    "homeHeat": [
                        {
                            "securityCode": "931865.CSI",
                            "securityAbbreviation": "中证半导",
                            "changePercent": -6.8,
                            "tradeDate": "2026-07-02 11:31:55",
                        }
                    ]
                },
                "homeNews": {
                    "groupList": [
                        [
                            {
                                "title": "养猪股集体爆发",
                                "skipAddr": "amcfundex://community/postDetail?statusId=N2607011748440455076",
                                "securityCode": "000949.CSI",
                                "securityName": "中证农业",
                                "valuation": "偏低",
                            }
                        ]
                    ]
                },
                "focusKanPanVo": {
                    "draw": "4054.09,-1.42,-58.36,09:30,,;4088.03,-0.59,-24.42,10:03,半导体设备,0;",
                    "drawColumns": "price,changePercent,change,minuteByHours,label,labelFluctuation",
                },
                "juniorHomeMuseVo": {
                    "indexWeaponSpectrumVo": {
                        "indexWeaponSpectrum": {
                            "index": {
                                "oneWeek": [
                                    {
                                        "indexCode": "950161.CSI",
                                        "indexName": "科创新药",
                                        "changePercent": 12.02,
                                    }
                                ],
                                "oneMonth": [],
                                "halfYear": [],
                            }
                        }
                    },
                    "ssfVo": {
                        "ssf": [
                            {
                                "securityCode": "561330.SH",
                                "securityName": "矿业ETF国泰",
                                "stockType": 1,
                                "changePercent": 2.54,
                                "proportionTotal": 44.13,
                                "stockTotal": 9,
                                "stockList": [
                                    {
                                        "securityCode": "601899.SH",
                                        "securityName": "紫金矿业",
                                        "proportion": 10.21,
                                    }
                                ],
                            }
                        ]
                    },
                },
            }
        }
    )

    result = client.home(limit=1)

    assert client.get_calls == [
        (HOME_PAGE_CONTENT_ENDPOINT, {"platform": "PC"}),
    ]
    assert result["kind"] == "home"
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["classes"] == [{"value": "01", "label": "宽基指数"}]
    assert result["modules"] == [
        {
            "key": "homeHeat",
            "tag": "junior_home_heat",
            "name": "小白涨跌热力图",
            "title": "快看行情",
            "state": "1",
        }
    ]
    assert result["heat"] == [
        {
            "securityCode": "931865.CSI",
            "securityName": "中证半导",
            "changePercent": -6.8,
            "tradeDate": "2026-07-02 11:31:55",
        }
    ]
    assert result["news"] == [
        {
            "statusId": "N2607011748440455076",
            "title": "养猪股集体爆发",
            "skipAddr": "amcfundex://community/postDetail?statusId=N2607011748440455076",
            "securityCode": "000949.CSI",
            "securityName": "中证农业",
            "valuation": "偏低",
        }
    ]
    assert result["focus"]["latest_point"] == {
        "price": "4088.03",
        "changePercent": "-0.59",
        "change": "-24.42",
        "minuteByHours": "10:03",
        "label": "半导体设备",
        "labelFluctuation": "0",
    }
    assert result["spectrum"] == {
        "oneWeek": [
            {
                "indexCode": "950161.CSI",
                "indexName": "科创新药",
                "changePercent": 12.02,
            }
        ],
        "oneMonth": [],
        "halfYear": [],
    }
    assert result["stock_funds"] == [
        {
            "securityCode": "561330.SH",
            "securityName": "矿业ETF国泰",
            "stockType": 1,
            "changePercent": 2.54,
            "proportionTotal": 44.13,
            "stockTotal": 9,
            "stocks": [
                {
                    "securityCode": "601899.SH",
                    "securityName": "紫金矿业",
                    "proportion": 10.21,
                }
            ],
        }
    ]


def test_hot_timeline_flattens_h5_market_events() -> None:
    client = RecordingClient(
        {
            HOT_SHOW_STATUS_ENDPOINT: True,
            HOT_LIST_ENDPOINT: [
                {
                    "timeInterval": "2026-07-01 15:03:00",
                    "changeType": "0",
                    "foldSize": 0,
                    "changeList": [
                        {
                            "id": 7722,
                            "changeTime": "2026-07-01 15:03:15",
                            "content": "<p>A股三大指数收盘涨跌不一。</p>",
                            "changePercent": 0.4408,
                            "contentId": "36b1",
                            "correlationIndexList": [
                                {
                                    "indexName": "上证指数",
                                    "indexCode": "000001.SH",
                                    "changePercent": 0.4408,
                                }
                            ],
                            "correlationEtfList": [
                                {
                                    "indexName": "上证指数ETF富国",
                                    "indexCode": "510210.SH",
                                    "changePercent": 0.5882,
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    )

    result = client.hot_timeline(limit=1)

    assert client.get_calls == [
        (HOT_SHOW_STATUS_ENDPOINT, None),
        (HOT_LIST_ENDPOINT, None),
    ]
    assert result["kind"] == "hot_timeline"
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["show_status"] is True
    assert result["rows"] == [
        {
            "id": 7722,
            "timeInterval": "2026-07-01 15:03:00",
            "changeType": "0",
            "foldSize": 0,
            "changeTime": "2026-07-01 15:03:15",
            "content": "A股三大指数收盘涨跌不一。",
            "changePercent": 0.4408,
            "contentId": "36b1",
            "relatedIndexes": [
                {
                    "indexCode": "000001.SH",
                    "indexName": "上证指数",
                    "changePercent": 0.4408,
                }
            ],
            "relatedEtfs": [
                {
                    "indexCode": "510210.SH",
                    "indexName": "上证指数ETF富国",
                    "changePercent": 0.5882,
                }
            ],
        }
    ]


def test_news_flattens_grouped_rows() -> None:
    client = RecordingClient(
        {
            NEWS_ENDPOINT: {
                "total": 2,
                "groupList": [
                    [
                        {
                            "title": "第一条",
                            "securityCode": "000300.SH",
                            "skipAddr": "amcfundex://community/postDetail?statusId=N2607010744100459043",
                        }
                    ],
                    [{"title": "第二条", "securityCode": "000688.SH"}],
                ],
            }
        }
    )

    result = client.news(limit=1)

    assert result["total"] == 2
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["rows"] == [
        {
            "title": "第一条",
            "securityCode": "000300.SH",
            "skipAddr": "amcfundex://community/postDetail?statusId=N2607010744100459043",
            "statusId": "N2607010744100459043",
        }
    ]


def test_article_detail_returns_limited_readonly_excerpt() -> None:
    client = RecordingClient(
        {
            COMMUNITY_STATUS_DETAIL_ENDPOINT: {
                "articleId": 77093,
                "statusId": "N2607011526280455070",
                "title": "人工智能领域权力更迭",
                "content": "<p>第一段很长很长。</p><p>第二段继续补充。</p>",
                "contentLabel": "AI,芯片",
                "nickName": "财联社",
                "publishTime": 1782884298000,
                "securityInfoVos": [
                    {"securityCode": "931071.CSI", "securityName": "人工智能"}
                ],
            }
        }
    )

    result = client.article("N2607011526280455070", content_limit=12)

    assert client.get_calls == [
        (COMMUNITY_STATUS_DETAIL_ENDPOINT, {"statusId": "N2607011526280455070"})
    ]
    assert result["kind"] == "article"
    assert result["status_id"] == "N2607011526280455070"
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["detail"] == {
        "articleId": 77093,
        "statusId": "N2607011526280455070",
        "title": "人工智能领域权力更迭",
        "content": "第一段很长很长。 第二段...",
        "contentLabel": "AI,芯片",
        "nickName": "财联社",
        "publishTime": 1782884298000,
        "securityInfoVos": [{"securityCode": "931071.CSI", "securityName": "人工智能"}],
    }


def test_article_detail_clamps_excessive_content_limit() -> None:
    long_content = "甲" * (ARTICLE_CONTENT_EXCERPT_MAX + 10)
    client = RecordingClient(
        {
            COMMUNITY_STATUS_DETAIL_ENDPOINT: {
                "statusId": "N2607011526280455070",
                "title": "人工智能领域权力更迭",
                "content": long_content,
            }
        }
    )

    result = client.article("N2607011526280455070", content_limit=1_000_000)

    assert result["detail"]["content"] == f"{'甲' * ARTICLE_CONTENT_EXCERPT_MAX}..."


def test_classes_reads_index_classification_tree() -> None:
    client = RecordingClient(
        {
            CLASS_INFO_ENDPOINT: {
                "allListSize": 512,
                "allList": [
                    {
                        "value": "0219",
                        "lable": "科技",
                        "count": 84,
                        "children": [{"value": "021910", "lable": "人工智能", "count": 6}],
                    }
                ],
                "cascade": [{"value": "02", "lable": "行业主题", "allCount": 412}],
            }
        }
    )

    result = client.classes(search_value="AI", limit=1)

    assert client.get_calls == [
        (
            CLASS_INFO_ENDPOINT,
            {"tableName": "index", "pageName": "index", "searchValue": "AI"},
        )
    ]
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["all_list_size"] == 512
    assert result["rows"] == [
        {
            "value": "0219",
            "label": "科技",
            "count": 84,
            "children": [{"value": "021910", "label": "人工智能", "count": 6}],
        }
    ]


def test_focus_news_returns_compact_market_context() -> None:
    client = RecordingClient(
        {
            FOCUS_NEWS_ENDPOINT: {
                "draw": "4090.76,-0.09,-3.64,09:30,,;4100.09,0.14,5.69,09:50,机器人,1;",
                "drawColumns": "price,changePercent,change,minuteByHours,label,labelFluctuation",
                "status": "02",
                "news": [
                    {
                        "id": "n1",
                        "m": "09:50",
                        "n": "机器人",
                        "mc": "<p>机器人板块异动</p>",
                        "rc": "<p>产业消息催化</p>",
                        "securityQuoteSimpleVoList": [
                            {"securityCode": "399006.SZ", "securityName": "创业板指"}
                        ],
                    }
                ],
            }
        }
    )

    result = client.focus_news(limit=1)

    assert client.get_calls == [(FOCUS_NEWS_ENDPOINT, {"newsSize": "1"})]
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["status"] == "02"
    assert result["latest_point"] == {
        "price": "4100.09",
        "changePercent": "0.14",
        "change": "5.69",
        "minuteByHours": "09:50",
        "label": "机器人",
        "labelFluctuation": "1",
    }
    assert result["rows"] == [
        {
            "id": "n1",
            "time": "09:50",
            "theme": "机器人",
            "summary": "机器人板块异动",
            "reason": "产业消息催化",
            "related": [{"securityCode": "399006.SZ", "securityName": "创业板指"}],
        }
    ]


def test_knowledge_reads_methodology_help_text() -> None:
    client = RecordingClient(
        {
            KNOWLEDGE_ENDPOINT: [
                {
                    "id": 361,
                    "knowledgeKey": "follw_valuation_tips",
                    "knowledgeTitle": "自选页估值标签说明",
                    "knowledgeContent": "<p>本页指数估值计算周期为最近5年。</p>",
                }
            ]
        }
    )

    result = client.knowledge(
        ["follw_valuation_tips", "fund_details_page_asset_allocation"],
        content_limit=40,
    )

    assert client.get_calls == [
        (
            KNOWLEDGE_ENDPOINT,
            {
                "knowledgeKeyList": "follw_valuation_tips,fund_details_page_asset_allocation",
            },
        )
    ]
    assert result["kind"] == "knowledge"
    assert result["knowledge_keys"] == [
        "follw_valuation_tips",
        "fund_details_page_asset_allocation",
    ]
    assert result["source_limits"] == [
        "Red Rocket knowledge-base rows are platform methodology/help text, not live market facts or official fund-company records.",
        "Use them only to interpret Red Rocket labels; verify decision-sensitive facts elsewhere.",
    ]
    assert result["rows"] == [
        {
            "id": 361,
            "knowledgeKey": "follw_valuation_tips",
            "title": "自选页估值标签说明",
            "content": "本页指数估值计算周期为最近5年。",
        }
    ]


def test_must_read_returns_metadata_without_article_bodies() -> None:
    client = RecordingClient(
        {
            MUST_READ_ENDPOINT: {
                "bigEvent": {
                    "statusId": "big-1",
                    "title": "年中盘点",
                    "content": "<p>长正文不应进入结果</p>",
                    "contentLabel": "AI,PCB",
                    "nickName": "财联社",
                    "publishTime": 1782724773000,
                },
                "statusList": {
                    "data": [
                        {
                            "statusId": "s1",
                            "title": "必读标题",
                            "content": "<p>正文</p>",
                            "contentLabel": "机器人",
                            "nickName": "红色火箭",
                            "publishTime": 1782724773000,
                            "securityInfoVos": [
                                {"securityCode": "000300.SH", "securityName": "沪深300"}
                            ],
                        }
                    ]
                },
            }
        }
    )

    result = client.must_read("000300.SH", limit=1)

    assert client.post_calls == [
        (
            MUST_READ_ENDPOINT,
            None,
            {"securityCode": "000300.SH", "pageNo": 1, "pageSize": 1, "isAll": "0", "flag": True},
        )
    ]
    assert "content" not in result["big_event"]
    assert result["big_event"] == {
        "statusId": "big-1",
        "title": "年中盘点",
        "contentLabel": "AI,PCB",
        "nickName": "财联社",
        "publishTime": 1782724773000,
    }
    assert result["rows"] == [
        {
            "statusId": "s1",
            "title": "必读标题",
            "contentLabel": "机器人",
            "nickName": "红色火箭",
            "publishTime": 1782724773000,
            "securityInfoVos": [{"securityCode": "000300.SH", "securityName": "沪深300"}],
        }
    ]


def test_compare_recommend_labels_discovery_source_limits() -> None:
    client = RecordingClient(
        {
            COMPARE_RECOMMEND_ENDPOINT: [
                {
                    "indexList": [
                        {"securityName": "沪深300", "securityCode": "000300.SH"},
                        {"securityName": "中证A500", "securityCode": "000510.CSI"},
                    ]
                }
            ]
        }
    )

    result = client.compare_recommend(limit=1)

    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["rows"] == [
        {
            "names": "沪深300, 中证A500",
            "codes": "000300.SH, 000510.CSI",
            "size": 2,
        }
    ]


def test_wind_reads_all_signal_rows() -> None:
    client = RecordingClient(
        {
            WIND_ENDPOINT: {
                "allSignal": {
                    "updateTime": "2026.07.01",
                    "signals": [
                        {
                            "securityCode": "399441.SZ",
                            "securityName": "生物医药",
                            "score": 79.0,
                            "scoreLabel": "积极看好",
                        }
                    ],
                }
            }
        }
    )

    result = client.wind(limit=1)

    assert result["update_time"] == "2026.07.01"
    assert result["source_limits"] == [
        "Red Rocket wind-vane scores and labels are Red Rocket methodology outputs, not standalone investment signals.",
        "Verify exchange quotes, fund/product rules, and local investment policy before decision use.",
    ]
    assert result["rows"] == [
        {
            "securityCode": "399441.SZ",
            "securityName": "生物医药",
            "score": 79.0,
            "scoreLabel": "积极看好",
        }
    ]


def test_signal_detail_summarizes_wind_vane_detail() -> None:
    client = RecordingClient(
        {
            SIGNAL_DETAIL_ENDPOINT: {
                "scoreArea": {
                    "securityCode": "000300.SH",
                    "securityName": "沪深300",
                    "score": 35.8,
                    "scoreLabel": "保持关注",
                    "scoreDate": "2026.07.01",
                    "tips": "或可持续观望",
                    "pointer": "中",
                    "hisDesc": "近30日提升1.93分",
                },
                "scoreDetails": [
                    {
                        "title": "估值",
                        "score": 45.0,
                        "avg": 50.0,
                        "pointerType": "neutral",
                        "desc": "<p>估值处于中位。</p>",
                    }
                ],
                "scoreTrend": [
                    {"scoreDate": "2026.06.30", "score": 34.2},
                    {"scoreDate": "2026.07.01", "score": 35.8},
                ],
                "strategicPerformance": {
                    "modelUpDownRate": -9.79,
                    "modelDetails": [{"very": "large"}],
                },
                "relatedFund": {"etf": 30, "otc": 266},
                "relateProduct": {
                    "productCode": "000051.OF",
                    "productName": "华夏沪深300ETF联接A",
                    "revenueRange": "近一年",
                    "performance": 1.23,
                },
            }
        }
    )

    result = client.signal_detail("000300.SH", limit=1)

    assert client.get_calls == [
        (SIGNAL_DETAIL_ENDPOINT, {"securityCode": "000300.SH"}),
    ]
    assert result["kind"] == "signal_detail"
    assert result["source_limits"] == [
        "Red Rocket wind-vane scores and labels are Red Rocket methodology outputs, not standalone investment signals.",
        "Verify exchange quotes, fund/product rules, and local investment policy before decision use.",
    ]
    assert result["score_area"] == {
        "securityCode": "000300.SH",
        "securityName": "沪深300",
        "score": 35.8,
        "scoreLabel": "保持关注",
        "scoreDate": "2026.07.01",
        "tips": "或可持续观望",
        "pointer": "中",
        "hisDesc": "近30日提升1.93分",
    }
    assert result["score_details"] == [
        {
            "title": "估值",
            "score": 45.0,
            "avg": 50.0,
            "pointerType": "neutral",
            "desc": "估值处于中位。",
        }
    ]
    assert result["score_trend"] == [{"scoreDate": "2026.07.01", "score": 35.8}]
    assert result["strategic_performance"] == {"modelUpDownRate": -9.79}
    assert "modelDetails" not in result["strategic_performance"]
    assert result["related_fund"] == {"etf": 30, "otc": 266}
    assert result["related_product"] == {
        "productCode": "000051.OF",
        "productName": "华夏沪深300ETF联接A",
        "revenueRange": "近一年",
        "performance": 1.23,
    }


def test_index_detail_plus_reads_deeper_readonly_context() -> None:
    client = RecordingClient(
        {
            INDEX_VALUATION_ENDPOINT: {
                "valuation": 12.3,
                "valuationQuantileNew": "42%",
                "percentile": "42%",
                "peg": 1.1,
                "items": [
                    {"date": "2026-06-30", "valuation": 12.3, "valuationQuantileNew": "42%"}
                ],
            },
            INDEX_COMPONENT_ENDPOINT: {
                "reportDate": "2026-03-31",
                "items": [
                    {"componentCode": "600519.SH", "componentName": "贵州茅台", "weight": 5.0}
                ],
            },
            INDEX_REVENUE_PROFIT_ENDPOINT: {
                "items": [{"year": "2025", "revenueGrowthRate": 3.2, "profitGrowthRate": 4.1}]
            },
            INDEX_RISK_RETURN_ENDPOINT: {
                "lastOneYearReturn": 8.8,
                "lastThreeYearReturn": -3.2,
            },
            SECURITY_INDUSTRY_DISTRIBUTION_ENDPOINT: {
                "latestDate": "2026-03-31",
                "resultMap": {"食品饮料": 12.3},
            },
            SECURITY_COMPONENT_DEVELOP_ENDPOINT: {
                "items": [{"year": "2025", "revTol": 123, "npTol": 45}]
            },
            SECURITY_MUST_SEE_ENDPOINT: {"pe": {"tips": "偏低"}, "roe": {"tips": "稳定"}},
            INDEX_MAIN_FUND_ENDPOINT: {
                "etf": [{"fundCode": "510300.SH", "fundName": "沪深300ETF"}],
                "otc": [{"fundCode": "000051.OF", "fundName": "沪深300联接A"}],
            },
        }
    )

    result = client.index_detail_plus(
        "000300.SH",
        valuation_type="PE",
        time_interval="last_5_years",
        limit=1,
    )

    assert client.get_calls == [
        (
            INDEX_VALUATION_ENDPOINT,
            {
                "securityCode": "000300.SH",
                "valuationType": "PE",
                "timeInterval": "last_5_years",
            },
        ),
        (
            INDEX_COMPONENT_ENDPOINT,
            {"securityCode": "000300.SH", "businessCode": "03", "industriesLevelNum": "2"},
        ),
        (
            INDEX_REVENUE_PROFIT_ENDPOINT,
            {"securityCode": "000300.SH", "range": "", "businessCode": "01"},
        ),
        (INDEX_RISK_RETURN_ENDPOINT, {"indexCode": "000300.SH"}),
        (
            SECURITY_INDUSTRY_DISTRIBUTION_ENDPOINT,
            {"securityCode": "000300.SH", "industryLevel": "3"},
        ),
        (SECURITY_COMPONENT_DEVELOP_ENDPOINT, {"securityCode": "000300.SH", "quarter": "LATEST"}),
        (SECURITY_MUST_SEE_ENDPOINT, {"securityCode": "000300.SH", "isCapital": "false"}),
        (INDEX_MAIN_FUND_ENDPOINT, {"securityCode": "000300.SH"}),
    ]
    assert result["kind"] == "index_detail_plus"
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["valuation"] == {
        "valuation": 12.3,
        "valuationQuantileNew": "42%",
        "percentile": "42%",
        "peg": 1.1,
    }
    assert result["valuation_rows"] == [
        {"date": "2026-06-30", "valuation": 12.3, "valuationQuantileNew": "42%"}
    ]
    assert result["components"] == [
        {"componentCode": "600519.SH", "componentName": "贵州茅台", "weight": 5.0}
    ]
    assert result["risk_return"] == {"lastOneYearReturn": 8.8, "lastThreeYearReturn": -3.2}
    assert result["industry_distribution"] == {
        "latestDate": "2026-03-31",
        "latest": [{"industryName": "食品饮料", "weight": 12.3}],
    }
    assert result["main_fund"]["etf"] == [{"fundCode": "510300.SH", "fundName": "沪深300ETF"}]


def test_index_detail_plus_preserves_date_keyed_industry_maps() -> None:
    client = RecordingClient(
        {
            INDEX_VALUATION_ENDPOINT: {},
            INDEX_COMPONENT_ENDPOINT: {},
            INDEX_REVENUE_PROFIT_ENDPOINT: {},
            INDEX_RISK_RETURN_ENDPOINT: {},
            SECURITY_INDUSTRY_DISTRIBUTION_ENDPOINT: {
                "latestDate": "2026-03-31",
                "resultMap": {
                    "2025年末": [{"industryName": "银行", "weight": 10.1}],
                    "2026年一季报": [{"industryName": "半导体", "weight": 7.2}],
                },
            },
            SECURITY_COMPONENT_DEVELOP_ENDPOINT: {},
            SECURITY_MUST_SEE_ENDPOINT: {},
            INDEX_MAIN_FUND_ENDPOINT: {},
        }
    )

    result = client.index_detail_plus("000300.SH", limit=1)

    assert result["industry_distribution"] == {
        "latestDate": "2026-03-31",
        "latestBucket": "2026年一季报",
        "latest": [{"industryName": "半导体", "weight": 7.2}],
    }


def test_index_detail_plus_matches_industry_bucket_to_latest_date() -> None:
    client = RecordingClient(
        {
            INDEX_VALUATION_ENDPOINT: {},
            INDEX_COMPONENT_ENDPOINT: {},
            INDEX_REVENUE_PROFIT_ENDPOINT: {},
            INDEX_RISK_RETURN_ENDPOINT: {},
            SECURITY_INDUSTRY_DISTRIBUTION_ENDPOINT: {
                "latestDate": "20260331",
                "resultMap": {
                    "2026年一季报": [{"industryName": "半导体", "weight": 7.2}],
                    "2025年末": [{"industryName": "银行", "weight": 10.1}],
                },
            },
            SECURITY_COMPONENT_DEVELOP_ENDPOINT: {},
            SECURITY_MUST_SEE_ENDPOINT: {},
            INDEX_MAIN_FUND_ENDPOINT: {},
        }
    )

    result = client.index_detail_plus("000300.SH", limit=1)

    assert result["industry_distribution"] == {
        "latestDate": "20260331",
        "latestBucket": "2026年一季报",
        "latest": [{"industryName": "半导体", "weight": 7.2}],
    }


def test_index_detail_plus_matches_raw_date_industry_bucket_to_latest_date() -> None:
    client = RecordingClient(
        {
            INDEX_VALUATION_ENDPOINT: {},
            INDEX_COMPONENT_ENDPOINT: {},
            INDEX_REVENUE_PROFIT_ENDPOINT: {},
            INDEX_RISK_RETURN_ENDPOINT: {},
            SECURITY_INDUSTRY_DISTRIBUTION_ENDPOINT: {
                "latestDate": "2026-03-31",
                "resultMap": {
                    "2025年末": [{"industryName": "银行", "weight": 10.1}],
                    "2026-03-31": [{"industryName": "半导体", "weight": 7.2}],
                },
            },
            SECURITY_COMPONENT_DEVELOP_ENDPOINT: {},
            SECURITY_MUST_SEE_ENDPOINT: {},
            INDEX_MAIN_FUND_ENDPOINT: {},
        }
    )

    result = client.index_detail_plus("000300.SH", limit=1)

    assert result["industry_distribution"] == {
        "latestDate": "2026-03-31",
        "latestBucket": "2026-03-31",
        "latest": [{"industryName": "半导体", "weight": 7.2}],
    }


def test_index_detail_plus_ranks_raw_date_industry_buckets_without_latest_date() -> None:
    client = RecordingClient(
        {
            INDEX_VALUATION_ENDPOINT: {},
            INDEX_COMPONENT_ENDPOINT: {},
            INDEX_REVENUE_PROFIT_ENDPOINT: {},
            INDEX_RISK_RETURN_ENDPOINT: {},
            SECURITY_INDUSTRY_DISTRIBUTION_ENDPOINT: {
                "resultMap": {
                    "2025年末": [{"industryName": "银行", "weight": 10.1}],
                    "2026-03-31": [{"industryName": "半导体", "weight": 7.2}],
                },
            },
            SECURITY_COMPONENT_DEVELOP_ENDPOINT: {},
            SECURITY_MUST_SEE_ENDPOINT: {},
            INDEX_MAIN_FUND_ENDPOINT: {},
        }
    )

    result = client.index_detail_plus("000300.SH", limit=1)

    assert result["industry_distribution"] == {
        "latestBucket": "2026-03-31",
        "latest": [{"industryName": "半导体", "weight": 7.2}],
    }


def test_etf_flow_reads_share_margin_and_tracking_context() -> None:
    client = RecordingClient(
        {
            ETF_NET_SUBSCRIPTION_ENDPOINT: {
                "tradeDt": "06-30",
                "totalShare": 1000,
                "netSubscriptionShares": -20,
                "subscriptionShareList": [
                    {"tradeDt": "2026-06-30", "netSubscriptionShares": -20}
                ],
            },
            ETF_SHARE_CHANGE_ENDPOINT: {
                "tradeDt": "06-30",
                "floatShare": 900,
                "shareList": [{"tradeDt": "2026-06-30", "floatShare": 900}],
            },
            ETF_MARGIN_ENDPOINT: {
                "tradeDt": "06-30",
                "marginNetInflow": 12,
                "marginDataList": [{"tradeDt": "2026-06-30", "marginNetInflow": 12}],
            },
            ETF_FIVE_MFD_INFLOW_ENDPOINT: [
                {"tradeDt": "2026-07-01", "SMfdInflow": -124116.6178},
                {"tradeDt": "2026-06-30", "SMfdInflow": 3000},
            ],
            ETF_LINK_FUND_ENDPOINT: {"fundCode": "000051.OF", "fundName": "沪深300联接A"},
            TRACKING_INDEX_ENDPOINT: {
                "securityCode": "000300.SH",
                "securityName": "沪深300",
                "changePercent": 0.8,
            },
        }
    )

    result = client.etf_flow("510300.SH", period="3M", limit=1)

    assert client.get_calls == [
        (ETF_NET_SUBSCRIPTION_ENDPOINT, {"securityCode": "510300.SH"}),
        (ETF_SHARE_CHANGE_ENDPOINT, {"securityCode": "510300.SH", "period": "3M"}),
        (ETF_MARGIN_ENDPOINT, {"securityCode": "510300.SH"}),
        (ETF_FIVE_MFD_INFLOW_ENDPOINT, {"securityCode": "510300.SH"}),
        (ETF_LINK_FUND_ENDPOINT, {"securityCode": "510300.SH"}),
        (TRACKING_INDEX_ENDPOINT, {"securityCode": "510300.SH"}),
    ]
    assert result["kind"] == "etf_flow"
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["subscription"] == {
        "tradeDt": "06-30",
        "totalShare": 1000,
        "netSubscriptionShares": -20,
    }
    assert result["share_change"] == {"tradeDt": "06-30", "floatShare": 900}
    assert result["margin"] == {"tradeDt": "06-30", "marginNetInflow": 12}
    assert result["five_mfd_inflow"] == {
        "days": 2,
        "latestTradeDate": "2026-07-01",
        "totalSMfdInflow": -121116.6178,
    }
    assert result["five_mfd_inflow_rows"] == [
        {"tradeDt": "2026-07-01", "SMfdInflow": -124116.6178}
    ]
    assert result["tracking_index"] == {
        "securityCode": "000300.SH",
        "securityName": "沪深300",
        "changePercent": 0.8,
    }


def test_industry_reads_stable_h5_industry_context() -> None:
    client = RecordingClient(
        {
            INDUSTRY_LIST_ENDPOINT: [
                {
                    "code": "industry_ArtificialIntelligence",
                    "value": "人工智能",
                    "hasShowDistribution": True,
                }
            ],
            INDUSTRY_ID_ENDPOINT: {
                "industryId": "industry_ArtificialIntelligence",
                "indexCode": "931071.CSI",
            },
            INDUSTRY_QUOTE_ENDPOINT: {
                "securityCode": "931071.CSI",
                "securityName": "人工智能",
                "price": 17610.22,
                "changePercent": 1.23,
                "marketTip": "交易中",
            },
            INDUSTRY_INDEX_CODES_ENDPOINT: [
                {
                    "securityCode": "980017.CNI",
                    "securityName": "国证芯片",
                    "securityDesc": "反映A股市场芯片产业全产业链表现。",
                }
            ],
            INDUSTRY_CLASSIFY_ENDPOINT: [
                {
                    "industryClassifyName": "需求指标",
                    "dataIndicatorList": [
                        {
                            "indicatorId": "001004",
                            "indicatorName": "全球半导体销售额",
                            "title": "什么是全球半导体销售额？",
                            "content": "<p>销售额说明</p>",
                        }
                    ],
                }
            ],
            INDUSTRY_CLASSIFY_DATA_ENDPOINT: {
                "indicatorId": "001004",
                "indicatorName": "全球半导体销售额",
                "content": "<p>指标详情</p>",
                "indicatorDataDetailVoList": [
                    {
                        "indicatorTm": "2026-12-31",
                        "indicatorValue": "9754.60",
                        "yoy": 23.21,
                    }
                ],
            },
            INDUSTRY_RELATED_ENDPOINT: {
                "indicatorTotal": 8,
                "indicatorData": [
                    {
                        "indicatorDataName": "全球半导体销售额",
                        "dataItem": "年销售额",
                        "indicatorTm": "2026-12-31",
                        "indicatorValue": "9754.60",
                        "yoy": 23.21,
                    }
                ],
            },
            INDUSTRY_CHART_ENDPOINT: {
                "securityCode": "000300.SH",
                "securityName": "沪深300",
                "chartDimension": "近10年",
                "itemsSize": 2427,
                "dimensionChange": 12.3,
                "performance": {"weeklyPerformance": 1.2, "yearlyPerformance": 8.8},
                "items": [
                    {"tradeDate": "2026-06-26", "intervalChangePercent": 0.5191},
                    {"tradeDate": "2026-07-01", "intervalChangePercent": 0.52},
                ],
            },
            INDUSTRY_MEMOIR_ENDPOINT: [
                {
                    "memoirTime": "2026-06-11 12:00:00",
                    "memoirTitle": "韩国6月上旬出口再创历史新高",
                    "memoirContent": "<p>行业事件内容</p>",
                    "memoirRating": 3,
                    "memoirPercentChange": 0.5076,
                    "tradeDate": "2026-06-11",
                }
            ],
        }
    )

    result = client.industry(
        industry_id=None,
        indicator_id="001004",
        index_code="931071.CSI",
        limit=1,
    )

    assert client.get_calls == [
        (INDUSTRY_LIST_ENDPOINT, None),
        (INDUSTRY_ID_ENDPOINT, {"indexCode": "931071.CSI"}),
        (INDUSTRY_QUOTE_ENDPOINT, {"industryId": "industry_ArtificialIntelligence"}),
        (INDUSTRY_INDEX_CODES_ENDPOINT, {"industryId": "industry_ArtificialIntelligence"}),
        (INDUSTRY_CLASSIFY_ENDPOINT, {"industryId": "industry_ArtificialIntelligence"}),
        (INDUSTRY_RELATED_ENDPOINT, {"industryId": "industry_ArtificialIntelligence"}),
        (
            INDUSTRY_CHART_ENDPOINT,
            {"industryId": "industry_ArtificialIntelligence", "indexCode": "931071.CSI"},
        ),
        (INDUSTRY_MEMOIR_ENDPOINT, {"industryId": "industry_ArtificialIntelligence"}),
        (
            INDUSTRY_CLASSIFY_DATA_ENDPOINT,
            {"industryId": "industry_ArtificialIntelligence", "indicatorId": "001004"},
        ),
    ]
    assert result["kind"] == "industry"
    assert result["industry_id"] == "industry_ArtificialIntelligence"
    assert result["industry_name"] == "人工智能"
    assert result["industry_lookup"] == {
        "industryId": "industry_ArtificialIntelligence",
        "indexCode": "931071.CSI",
    }
    assert result["quote"] == {
        "securityCode": "931071.CSI",
        "securityName": "人工智能",
        "price": 17610.22,
        "changePercent": 1.23,
        "marketTip": "交易中",
    }
    assert result["index_codes"] == [
        {
            "securityCode": "980017.CNI",
            "securityName": "国证芯片",
            "securityDesc": "反映A股市场芯片产业全产业链表现。",
        }
    ]
    assert result["classify"] == [
        {
            "industryClassifyName": "需求指标",
            "indicators": [
                {
                    "indicatorId": "001004",
                    "indicatorName": "全球半导体销售额",
                    "title": "什么是全球半导体销售额？",
                    "content": "销售额说明",
                }
            ],
        }
    ]
    assert result["indicator_detail"] == {
        "indicatorId": "001004",
        "indicatorName": "全球半导体销售额",
        "content": "指标详情",
        "rows": [
            {
                "indicatorTm": "2026-12-31",
                "indicatorValue": "9754.60",
                "yoy": 23.21,
            }
        ],
    }
    assert result["related_indicators"] == {
        "indicatorTotal": 8,
        "rows": [
            {
                "indicatorDataName": "全球半导体销售额",
                "dataItem": "年销售额",
                "indicatorTm": "2026-12-31",
                "indicatorValue": "9754.60",
                "yoy": 23.21,
            }
        ],
    }
    assert result["chart"] == {
        "securityCode": "000300.SH",
        "securityName": "沪深300",
        "chartDimension": "近10年",
        "itemsSize": 2427,
        "dimensionChange": 12.3,
        "performance": {"weeklyPerformance": 1.2, "yearlyPerformance": 8.8},
    }
    assert result["chart_rows"] == [
        {"tradeDate": "2026-07-01", "intervalChangePercent": 0.52}
    ]
    assert result["memoirs"] == [
        {
            "memoirTime": "2026-06-11 12:00:00",
            "memoirTitle": "韩国6月上旬出口再创历史新高",
            "memoirContent": "行业事件内容",
            "memoirRating": 3,
            "memoirPercentChange": 0.5076,
            "tradeDate": "2026-06-11",
        }
    ]


def test_index_compare_reads_stable_compare_detail_endpoints() -> None:
    client = RecordingClient(
        {
            COMPARE_ARCHIVES_ENDPOINT: [
                {"securityCode": "000300.SH", "securityName": "沪深300"}
            ],
            COMPARE_SIMILARITY_ENDPOINT: [{"similarity": "low"}],
            COMPARE_TEN_WEIGHT_STOCK_ENDPOINT: [
                {"securityCode": "000300.SH", "stockName": "贵州茅台"}
            ],
            COMPARE_MARKET_VALUE_ENDPOINT: [{"marketValueName": "大盘"}],
            COMPARE_PERFORMANCE_CORRELATION_ENDPOINT: {
                "000300.SH-沪深300": [{"date": "2026-06-30", "value": 1.0}]
            },
            COMPARE_VALUATION_GROWTH_ENDPOINT: {
                "items": [{"date": "2026-06-30", "000300.SH-沪深300": 1.2}]
            },
            COMPARE_INTERVAL_CHANGE_ENDPOINT: {
                "max": {"近一月": "000905.SH"},
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
            COMPARE_FUND_LIST_ENDPOINT: [
                {
                    "indexCode": "000300.SH",
                    "etfCount": 30,
                    "otcCount": 266,
                    "etfScale": 260963630904.252,
                    "otcScale": 132957360212.93,
                    "etfFundList": [
                        {
                            "fundCode": "510300.SH",
                            "fundName": "沪深300ETF",
                            "changePercentY1": 27.1,
                        }
                    ],
                    "otcFundList": [
                        {
                            "fundCode": "000051.OF",
                            "fundName": "沪深300联接A",
                            "changePercentY1": 27.2,
                        }
                    ],
                }
            ],
            VALUATION_ROE_TIME_ENDPOINT: {
                "valuationTime": "2026-07-01 wind",
                "roeTime": "2026-03-31 wind",
            },
            COMPARE_SPECIAL_MARKET_ENDPOINT: {
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
                            },
                            {
                                "securityCode": "000905.SH",
                                "securityName": "中证500",
                                "changePercent": 40.1,
                            },
                        ],
                    }
                ],
                "indexPerformanceVo": [
                    {
                        "securityCode": "000300.SH",
                        "securityName": "沪深300",
                        "itemSize": 510,
                        "items": [
                            {"tradeDate": "2026-06-26", "intervalChangePercent": 0.5191}
                        ],
                    }
                ],
            },
            COMPARE_CHART_ENDPOINT: [
                {
                    "securityCode": "000300.SH",
                    "securityName": "沪深300",
                    "itemSize": 2,
                    "items": [
                        {"tradeDate": "2026-07-01", "intervalChangePercent": 0.009},
                        {"tradeDate": "2026-07-02", "intervalChangePercent": -0.0145},
                    ],
                }
            ],
            COMPARE_MINUTE_CHART_ENDPOINT: [
                {
                    "securityCode": "000300.SH",
                    "securityName": "沪深300",
                    "tradeDate": "2026-07-02",
                    "tradeDateStatus": True,
                    "itemSize": 2,
                    "items": [
                        {"minuteByHours": "09:30", "changePercent": -1.89},
                        {"minuteByHours": "09:31", "changePercent": -1.9},
                    ],
                }
            ],
            COMPARE_INDUSTRY_LEVEL_ENDPOINT: [
                {"industryCodeLevel": "2", "industryNameLevel": "一级行业"}
            ],
            COMPARE_COMPONENT_ENDPOINT: {
                "knowledgeContent": "<p>行业分布说明</p>",
                "industryComponentList": [
                    {
                        "securityCode": "000300.SH",
                        "reportPeriodStr": "2026-03-31",
                        "industryLevel": "申万行业",
                        "items": [
                            {
                                "industriesName": "电子",
                                "proportion": "12.92%",
                                "value": 1504009304118.731,
                            }
                        ],
                    }
                ],
            },
        }
    )

    result = client.index_compare(
        [("000300.SH", "沪深300"), ("000905.SH", "中证500")],
        limit=1,
    )

    assert client.get_calls == [
        (COMPARE_ARCHIVES_ENDPOINT, {"indexCodes": "000300.SH,000905.SH"}),
        (COMPARE_SIMILARITY_ENDPOINT, {"indexCodes": "000300.SH,000905.SH"}),
        (COMPARE_TEN_WEIGHT_STOCK_ENDPOINT, {"indexCodes": "000300.SH,000905.SH"}),
        (COMPARE_MARKET_VALUE_ENDPOINT, {"indexCodes": "000300.SH,000905.SH"}),
        (COMPARE_PERFORMANCE_CORRELATION_ENDPOINT, {"indexCodes": "000300.SH,000905.SH"}),
        (
            COMPARE_VALUATION_GROWTH_ENDPOINT,
            {
                "indexInfos": "000300.SH-沪深300,000905.SH-中证500",
                "tabType": "PEG",
            },
        ),
        (COMPARE_INTERVAL_CHANGE_ENDPOINT, {"indexCodes": "000300.SH,000905.SH"}),
        (COMPARE_FUND_LIST_ENDPOINT, {"indexCodes": "000300.SH,000905.SH"}),
        (COMPARE_SPECIAL_MARKET_ENDPOINT, {"indexCodes": "000300.SH,000905.SH"}),
        (
            VALUATION_ROE_TIME_ENDPOINT,
            {"securityCodes": "000300.SH,000905.SH", "valuationType": "PE"},
        ),
        (
            COMPARE_CHART_ENDPOINT,
            {"indexCodes": "000300.SH,000905.SH", "period": "1M"},
        ),
        (
            COMPARE_MINUTE_CHART_ENDPOINT,
            {"indexInfos": "000300.SH-沪深300,000905.SH-中证500"},
        ),
        (
            COMPARE_INDUSTRY_LEVEL_ENDPOINT,
            {"indexCodes": "000300.SH,000905.SH"},
        ),
        (
            COMPARE_COMPONENT_ENDPOINT,
            {
                "securityCodes": "000300.SH,000905.SH",
                "businessCode": "03",
                "reportPeriod": "",
                "industriesLevelNum": "2",
            },
        ),
    ]
    assert result["kind"] == "index_compare"
    assert result["index_codes"] == "000300.SH,000905.SH"
    assert result["archives"] == [{"securityCode": "000300.SH", "securityName": "沪深300"}]
    assert result["similarity"] == [{"similarity": "low"}]
    assert result["valuation_growth"] == [
        {"date": "2026-06-30", "000300.SH-沪深300": 1.2}
    ]
    assert result["interval_change"]["max"] == {"近一月": "000905.SH"}
    assert result["interval_change"]["performances"] == [
        {
            "securityCode": "000300.SH",
            "securityName": "沪深300",
            "changePercent": -0.41,
            "weeklyPerformance": 0.32,
            "monthlyPerformance": 2.37,
            "yearlyPerformance": 25.77,
        }
    ]
    assert result["funds"] == [
        {
            "indexCode": "000300.SH",
            "etfCount": 30,
            "otcCount": 266,
            "etfScale": 260963630904.252,
            "otcScale": 132957360212.93,
            "etfFunds": [
                {
                    "fundCode": "510300.SH",
                    "fundName": "沪深300ETF",
                    "changePercentY1": 27.1,
                }
            ],
            "otcFunds": [
                {
                    "fundCode": "000051.OF",
                    "fundName": "沪深300联接A",
                    "changePercentY1": 27.2,
                }
            ],
        }
    ]
    assert result["data_time"] == {
        "valuationTime": "2026-07-01 wind",
        "roeTime": "2026-03-31 wind",
    }
    assert result["market_context"] == {
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
                    },
                    {
                        "securityCode": "000905.SH",
                        "securityName": "中证500",
                        "changePercent": 40.1,
                    },
                ],
            }
        ],
        "indexPerformance": [
            {
                "securityCode": "000300.SH",
                "securityName": "沪深300",
                "itemSize": 510,
                "latest": {"tradeDate": "2026-06-26", "intervalChangePercent": 0.5191},
            }
        ],
    }
    assert result["chart"] == [
        {
            "securityCode": "000300.SH",
            "securityName": "沪深300",
            "itemSize": 2,
            "latest": {"tradeDate": "2026-07-02", "intervalChangePercent": -0.0145},
            "items": [
                {"tradeDate": "2026-07-01", "intervalChangePercent": 0.009},
            ],
        }
    ]
    assert result["minute_chart"] == [
        {
            "securityCode": "000300.SH",
            "securityName": "沪深300",
            "tradeDate": "2026-07-02",
            "tradeDateStatus": True,
            "itemSize": 2,
            "latest": {"minuteByHours": "09:31", "changePercent": -1.9},
            "items": [{"minuteByHours": "09:30", "changePercent": -1.89}],
        }
    ]
    assert result["industry_levels"] == [
        {"industryCodeLevel": "2", "industryNameLevel": "一级行业"}
    ]
    assert result["industry_distribution"] == {
        "knowledgeContent": "行业分布说明",
        "levels": [
            {"industryCodeLevel": "2", "industryNameLevel": "一级行业"}
        ],
        "rows": [
            {
                "securityCode": "000300.SH",
                "reportPeriodStr": "2026-03-31",
                "industryLevel": "申万行业",
                "items": [
                    {
                        "industriesName": "电子",
                        "proportion": "12.92%",
                        "value": 1504009304118.731,
                    }
                ],
            }
        ],
    }
