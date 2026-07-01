from __future__ import annotations

from typing import Any

from redrocket_market.client import (
    ETF_NET_SUBSCRIPTION_ENDPOINT,
    ETF_PANORAMA_ENDPOINT,
    ETF_QUOTE_ENDPOINT,
    ETF_LIST_ENDPOINT,
    FUND_ASSET_DISTRIBUTION_ENDPOINT,
    FUND_COMPONENTS_ENDPOINT,
    FUND_HISTORY_NAV_ENDPOINT,
    FUND_SALE_STATUS_ENDPOINT,
    COMPARE_RECOMMEND_ENDPOINT,
    HEAT_ENDPOINT,
    INDEX_ARCHIVES_ENDPOINT,
    INDEX_LABEL_ENDPOINT,
    INDEX_ROE_ENDPOINT,
    NEWS_ENDPOINT,
    WIND_ENDPOINT,
    RedRocketClient,
    RequestResult,
    extract_rows,
    normalize_fund_code,
    normalize_security,
)


DISCOVERY_SOURCE_LIMITS = [
    "Red Rocket heat, news, and comparison rows are discovery context, not standalone investment signals.",
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
