from __future__ import annotations

from typing import Any

from redrocket_market.client import (
    COMPARE_ARCHIVES_ENDPOINT,
    COMPARE_MARKET_VALUE_ENDPOINT,
    COMPARE_PERFORMANCE_CORRELATION_ENDPOINT,
    ETF_NET_SUBSCRIPTION_ENDPOINT,
    ETF_LINK_FUND_ENDPOINT,
    ETF_MARGIN_ENDPOINT,
    ETF_PANORAMA_ENDPOINT,
    ETF_QUOTE_ENDPOINT,
    ETF_LIST_ENDPOINT,
    ETF_SHARE_CHANGE_ENDPOINT,
    FUND_ASSET_DISTRIBUTION_ENDPOINT,
    FUND_COMPONENTS_ENDPOINT,
    FUND_HISTORY_NAV_ENDPOINT,
    FUND_SALE_STATUS_ENDPOINT,
    COMPARE_SIMILARITY_ENDPOINT,
    COMPARE_RECOMMEND_ENDPOINT,
    COMPARE_TEN_WEIGHT_STOCK_ENDPOINT,
    COMPARE_VALUATION_GROWTH_ENDPOINT,
    HEAT_ENDPOINT,
    INDEX_ARCHIVES_ENDPOINT,
    INDEX_COMPONENT_ENDPOINT,
    INDEX_LABEL_ENDPOINT,
    INDEX_MAIN_FUND_ENDPOINT,
    INDEX_REVENUE_PROFIT_ENDPOINT,
    INDEX_RISK_RETURN_ENDPOINT,
    INDEX_ROE_ENDPOINT,
    INDEX_VALUATION_ENDPOINT,
    NEWS_ENDPOINT,
    SECURITY_COMPONENT_DEVELOP_ENDPOINT,
    SECURITY_INDUSTRY_DISTRIBUTION_ENDPOINT,
    SECURITY_MUST_SEE_ENDPOINT,
    TRACKING_INDEX_ENDPOINT,
    WIND_ENDPOINT,
    RedRocketClient,
    RequestResult,
    extract_rows,
    normalize_fund_code,
    normalize_security,
)


DISCOVERY_SOURCE_LIMITS = [
    "Red Rocket valuation, flow, heat, news, wind-vane, and comparison rows are auxiliary discovery context, not standalone investment signals.",
    "Verify exchange quotes, fund announcements, sales-channel rules, and local investment policy before decision use.",
]

FUND_SOURCE_LIMITS = [
    "Red Rocket fund sale status and asset allocation are auxiliary context, not official sales-channel rules.",
    "Verify fund company announcements, actual sales-channel limits, fees, and settlement rules before decision use.",
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


def test_news_flattens_grouped_rows() -> None:
    client = RecordingClient(
        {
            NEWS_ENDPOINT: {
                "total": 2,
                "groupList": [
                    [{"title": "第一条", "securityCode": "000300.SH"}],
                    [{"title": "第二条", "securityCode": "000688.SH"}],
                ],
            }
        }
    )

    result = client.news(limit=1)

    assert result["total"] == 2
    assert result["source_limits"] == DISCOVERY_SOURCE_LIMITS
    assert result["rows"] == [{"title": "第一条", "securityCode": "000300.SH"}]


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
    assert result["tracking_index"] == {
        "securityCode": "000300.SH",
        "securityName": "沪深300",
        "changePercent": 0.8,
    }


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
    ]
    assert result["kind"] == "index_compare"
    assert result["index_codes"] == "000300.SH,000905.SH"
    assert result["archives"] == [{"securityCode": "000300.SH", "securityName": "沪深300"}]
    assert result["similarity"] == [{"similarity": "low"}]
    assert result["valuation_growth"] == [
        {"date": "2026-06-30", "000300.SH-沪深300": 1.2}
    ]
