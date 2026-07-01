from __future__ import annotations

from typing import Any

from redrocket_market.client import (
    ETF_LIST_ENDPOINT,
    FUND_COMPONENTS_ENDPOINT,
    FUND_HISTORY_NAV_ENDPOINT,
    HEAT_ENDPOINT,
    NEWS_ENDPOINT,
    WIND_ENDPOINT,
    RedRocketClient,
    RequestResult,
    extract_rows,
    normalize_fund_code,
    normalize_security,
)


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
        }
    )

    result = client.fund("110020", limit=3)

    assert client.post_calls == [
        (FUND_COMPONENTS_ENDPOINT, {"securityCode": "110020.OF"}, {})
    ]
    assert result["components"] == [
        {"section": "stock", "dataCode": "600519.SH", "dataName": "贵州茅台"}
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
    assert result["rows"] == [{"title": "第一条", "securityCode": "000300.SH"}]


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
