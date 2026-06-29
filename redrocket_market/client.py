from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://hongsehuojian.com"
REFERER = f"{BASE_URL}/red-rocket/indexBrowser"

LIST_ENDPOINT = "/fundex-quote/allPage/findListBySecurity"
ETF_LIST_ENDPOINT = "/fundex-quote/allPage/findListByEtf"
SEARCH_ENDPOINT = "/fundex-quote/search/list"
BATCH_QUOTE_ENDPOINT = "/fundex-quote/search/batchQueryQuoteData"
BATCH_MINUTE_ENDPOINT = "/fundex-quote/security/batchMinute"
RELATED_FUNDS_ENDPOINT = "/fundex-quote/indexRelated/allFund"
FUND_SITUATION_ENDPOINT = "/fundex-quote/fund/fundSituation"
FUND_BASE_ENDPOINT = "/fundex-quote/fund/otcFundBase"
FUND_COMPONENTS_ENDPOINT = "/fundex-quote/fund/otcFundComponentsList"
FUND_HISTORY_NAV_ENDPOINT = "/fundex-quote/fund/historyNetValue"


PRESETS: dict[str, dict[str, str]] = {
    "wide": {"label": "宽基指数", "classA": "01", "classB": "", "classC": ""},
    "theme": {"label": "行业主题", "classA": "02", "classB": "", "classC": ""},
    "consumption": {"label": "消费", "classA": "02", "classB": "0215", "classC": ""},
    "tech": {"label": "科技", "classA": "02", "classB": "0219", "classC": ""},
    "strategy": {"label": "策略风格", "classA": "03", "classB": "", "classC": ""},
    "cross_border": {"label": "跨境指数", "classA": "05", "classB": "", "classC": ""},
}


class RedRocketError(RuntimeError):
    """Raised when a Red Rocket read-only request fails."""


@dataclass(frozen=True)
class RequestResult:
    data: Any
    url: str


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def compact_dict(data: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {key: data.get(key) for key in keys if data.get(key) not in (None, "")}


def normalize_fund_code(fund_code: str) -> str:
    text = fund_code.strip()
    return text if "." in text else f"{text}.OF"


def extract_rows(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        rows = data.get("data") or data.get("list") or data.get("records") or []
    else:
        rows = data
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


class RedRocketClient:
    def __init__(self, *, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def get(self, path: str, params: dict[str, str] | None = None) -> RequestResult:
        url = f"{BASE_URL}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        request = Request(
            url,
            headers={
                "Accept": "application/json,text/plain,*/*",
                "Referer": REFERER,
                "User-Agent": "Mozilla/5.0",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RedRocketError(f"无法读取红色火箭接口: {url} ({exc})") from exc
        if str(payload.get("code")) != "200":
            raise RedRocketError(f"红色火箭接口返回异常: {url} ({payload.get('msg')})")
        return RequestResult(payload.get("data"), url)

    def scan(
        self,
        preset: str,
        *,
        order_by: str = "pepercent",
        order: str = "asc",
        limit: int = 10,
        etf: bool = False,
    ) -> dict[str, Any]:
        preset_data = PRESETS[preset]
        result = self.get(
            ETF_LIST_ENDPOINT if etf else LIST_ENDPOINT,
            {
                "classA": preset_data["classA"],
                "classB": preset_data["classB"],
                "classC": preset_data["classC"],
                "orderBy": order_by,
                "order": order,
                "searchValue": "",
                "isSelected": "",
                "pageNo": "1",
                "pageSize": str(limit),
                "position": "",
            },
        )
        return {
            "kind": "etf_scan" if etf else "valuation_scan",
            "fetched_at": now_iso(),
            "source": result.url,
            "preset": preset,
            "label": preset_data["label"],
            "rows": [normalize_security(row) for row in extract_rows(result.data)[:limit]],
        }

    def search(self, keyword: str) -> dict[str, Any]:
        result = self.get(SEARCH_ENDPOINT, {"searchKeyword": keyword, "isSearchAll": "true"})
        return {
            "kind": "search",
            "fetched_at": now_iso(),
            "source": result.url,
            "keyword": keyword,
            "data": result.data,
        }

    def related(
        self,
        security_code: str,
        *,
        security_type: str = "etf",
        limit: int = 10,
    ) -> dict[str, Any]:
        result = self.get(
            RELATED_FUNDS_ENDPOINT,
            {
                "securityCode": security_code,
                "securityType": security_type,
                "pageNo": "1",
                "pageSize": str(limit),
            },
        )
        return {
            "kind": "related_funds",
            "fetched_at": now_iso(),
            "source": result.url,
            "security_code": security_code,
            "security_type": security_type,
            "rows": [normalize_related(row) for row in extract_rows(result.data)[:limit]],
        }

    def quote(self, security_codes: str) -> dict[str, Any]:
        result = self.get(
            BATCH_MINUTE_ENDPOINT,
            {"securityCodes": security_codes, "isFiledAll": "true"},
        )
        rows = result.data if isinstance(result.data, list) else extract_rows(result.data)
        return {
            "kind": "quote",
            "fetched_at": now_iso(),
            "source": result.url,
            "security_codes": security_codes,
            "rows": [normalize_quote(row) for row in rows if isinstance(row, dict)],
        }

    def fund(self, fund_code: str, *, limit: int = 10) -> dict[str, Any]:
        security_code = normalize_fund_code(fund_code)
        base = self.get(FUND_BASE_ENDPOINT, {"fundCode": security_code})
        situation = self.get(FUND_SITUATION_ENDPOINT, {"fundCode": security_code})
        components = self.get(
            FUND_COMPONENTS_ENDPOINT,
            {"fundCode": security_code, "pageNum": "1", "pageSize": str(limit)},
        )
        nav = self.get(
            FUND_HISTORY_NAV_ENDPOINT,
            {"fundCode": security_code, "startIndex": "1", "endIndex": str(limit)},
        )
        return {
            "kind": "fund",
            "fetched_at": now_iso(),
            "source": {
                "base": base.url,
                "situation": situation.url,
                "components": components.url,
                "nav": nav.url,
            },
            "fund_code": fund_code,
            "base": summarize_fund_base(base.data),
            "situation": summarize_fund_situation(situation.data),
            "components": extract_rows(components.data)[:limit],
            "nav": extract_rows(nav.data)[:limit],
        }


def normalize_security(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        row,
        [
            "securityCode",
            "securityName",
            "securityFullName",
            "name",
            "code",
            "market",
            "lastPrice",
            "changePercent",
            "pe",
            "pePercent",
            "pb",
            "pbPercent",
            "roe",
            "dividendRatio",
            "fundCompany",
            "trackingIndexName",
            "trackingIndexCode",
            "fundScale",
            "rate",
        ],
    )


def normalize_related(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        row,
        [
            "fundCode",
            "fundName",
            "fundCompany",
            "securityCode",
            "securityName",
            "fundType",
            "trackingError",
            "fundScale",
            "rate",
            "lastPrice",
            "changePercent",
        ],
    )


def normalize_quote(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        row,
        [
            "securityCode",
            "securityName",
            "lastPrice",
            "changePercent",
            "change",
            "open",
            "high",
            "low",
            "preClose",
            "amount",
            "volume",
            "marketTime",
            "tradeDate",
        ],
    )


def summarize_fund_base(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    base = data.get("baseInfo") if isinstance(data.get("baseInfo"), dict) else data
    return compact_dict(
        base,
        [
            "fundName",
            "fundCode",
            "fundType",
            "fundCompany",
            "fundManager",
            "establishDate",
            "fundScale",
            "trackingIndexName",
            "trackingIndexCode",
            "fundStatus",
        ],
    )


def summarize_fund_situation(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    return compact_dict(
        data,
        [
            "fundFullName",
            "fundCode",
            "fundType",
            "fundManager",
            "fundCompany",
            "fundScale",
            "fundStyle",
            "netValue",
            "netValueDate",
            "dayOfGrowth",
        ],
    )
