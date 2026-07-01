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
HEAT_ENDPOINT = "/fundex-activity/opportunity/findHomeHeatV3"
NEWS_ENDPOINT = "/fundex-activity/opportunity/findHomeNews"
WIND_ENDPOINT = "/fundex-quote/signal/getOneLevelPage"
COMPARE_RECOMMEND_ENDPOINT = "/fundex-quote/compare/recommendCompareList"

DISCOVERY_SOURCE_LIMITS = [
    "Red Rocket heat, news, and comparison rows are discovery context, not standalone investment signals.",
    "Verify exchange quotes, fund announcements, sales-channel rules, and local investment policy before decision use.",
]

WIND_SOURCE_LIMITS = [
    "Red Rocket wind-vane scores and labels are Red Rocket methodology outputs, not standalone investment signals.",
    "Verify exchange quotes, fund/product rules, and local investment policy before decision use.",
]


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
        return self._request("GET", path, params)

    def post(
        self,
        path: str,
        params: dict[str, str] | None = None,
        payload: Any | None = None,
    ) -> RequestResult:
        return self._request("POST", path, params, {} if payload is None else payload)

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        payload: Any | None = None,
    ) -> RequestResult:
        url = f"{BASE_URL}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            url,
            data=data,
            headers={
                "Accept": "application/json,text/plain,*/*",
                "Content-Type": "application/json;charset=UTF-8",
                "Referer": REFERER,
                "User-Agent": "Mozilla/5.0",
            },
            method=method,
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
        order_by: str | None = None,
        order: str = "asc",
        limit: int = 10,
        etf: bool = False,
    ) -> dict[str, Any]:
        preset_data = PRESETS[preset]
        actual_order_by = order_by or ("l.scale" if etf else "pepercent")
        result = self.get(
            ETF_LIST_ENDPOINT if etf else LIST_ENDPOINT,
            {
                "classA": preset_data["classA"],
                "classB": preset_data["classB"],
                "classC": preset_data["classC"],
                "orderBy": actual_order_by,
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

    def heat(
        self,
        *,
        order_by: str = "changePercent",
        order: str = "desc",
        class_a: str = "",
        limit: int = 10,
    ) -> dict[str, Any]:
        params = {"orderBy": order_by, "order": order}
        if class_a:
            params["classA"] = class_a
        result = self.get(HEAT_ENDPOINT, params)
        data = result.data if isinstance(result.data, dict) else {}
        rows = data.get("homeHeat") if isinstance(data.get("homeHeat"), list) else []
        indexes = data.get("indexList") if isinstance(data.get("indexList"), list) else []
        return {
            "kind": "heat",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "market_date": data.get("marketDate"),
            "rows": [normalize_heat(row) for row in rows[:limit] if isinstance(row, dict)],
            "indexes": [normalize_heat_index(row) for row in indexes if isinstance(row, dict)],
        }

    def news(self, *, page: int = 1, limit: int = 8) -> dict[str, Any]:
        result = self.get(NEWS_ENDPOINT, {"pageNo": str(page), "pageSize": str(limit)})
        data = result.data if isinstance(result.data, dict) else {}
        rows = flatten_group_list(data.get("groupList"))[:limit]
        return {
            "kind": "news",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "page": page,
            "total": data.get("total"),
            "rows": [normalize_news(row) for row in rows],
        }

    def wind(self, *, limit: int = 10) -> dict[str, Any]:
        result = self.get(WIND_ENDPOINT)
        data = result.data if isinstance(result.data, dict) else {}
        all_signal = data.get("allSignal") if isinstance(data.get("allSignal"), dict) else {}
        signals = all_signal.get("signals") if isinstance(all_signal.get("signals"), list) else []
        return {
            "kind": "wind",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": WIND_SOURCE_LIMITS,
            "update_time": all_signal.get("updateTime"),
            "rows": [normalize_wind(row) for row in signals[:limit] if isinstance(row, dict)],
        }

    def compare_recommend(self, *, limit: int = 8) -> dict[str, Any]:
        result = self.get(COMPARE_RECOMMEND_ENDPOINT)
        return {
            "kind": "compare_recommend",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "rows": [normalize_compare_group(row) for row in extract_rows(result.data)[:limit]],
        }

    def fund(self, fund_code: str, *, limit: int = 10) -> dict[str, Any]:
        security_code = normalize_fund_code(fund_code)
        base = self.get(FUND_BASE_ENDPOINT, {"fundCode": security_code})
        situation = self.get(FUND_SITUATION_ENDPOINT, {"fundCode": security_code})
        components = self.post(
            FUND_COMPONENTS_ENDPOINT,
            {"securityCode": security_code},
            {},
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
            "components": extract_component_rows(components.data, limit),
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


def normalize_heat(row: dict[str, Any]) -> dict[str, Any]:
    normalized = compact_dict(
        row,
        [
            "securityCode",
            "securityName",
            "securityAbbreviation",
            "price",
            "changePercent",
            "netInflowLatest",
            "amount",
            "scale",
            "tradeDate",
        ],
    )
    if "securityName" not in normalized and row.get("securityAbbreviation"):
        normalized["securityName"] = row["securityAbbreviation"]
        normalized.pop("securityAbbreviation", None)
    return normalized


def normalize_heat_index(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        row,
        [
            "securityCode",
            "securityName",
            "securityType",
            "price",
            "changePercent",
            "tradeDate",
            "northBoundInflow",
        ],
    )


def flatten_group_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    rows: list[dict[str, Any]] = []
    for group in value:
        if isinstance(group, list):
            rows.extend(row for row in group if isinstance(row, dict))
        elif isinstance(group, dict):
            rows.append(group)
    return rows


def normalize_news(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        row,
        [
            "id",
            "title",
            "subtitle",
            "bubble",
            "startTime",
            "securityCode",
            "securityName",
            "performanceRangeName",
            "performanceChangePercent",
            "valuation",
            "belongToDate",
        ],
    )


def normalize_wind(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        row,
        [
            "securityCode",
            "securityName",
            "score",
            "scoreLabel",
            "tips",
            "pointer",
            "hisDesc",
            "shortHisDesc",
            "changePercent",
            "scoreChange",
            "classA",
        ],
    )


def normalize_compare_group(row: dict[str, Any]) -> dict[str, Any]:
    indexes = row.get("indexList") if isinstance(row.get("indexList"), list) else []
    index_rows = [item for item in indexes if isinstance(item, dict)]
    names = [item.get("securityName") for item in index_rows if item.get("securityName")]
    codes = [item.get("securityCode") for item in index_rows if item.get("securityCode")]
    return compact_dict(
        {
            "names": ", ".join(names),
            "codes": ", ".join(codes),
            "size": len(index_rows),
        },
        ["names", "codes", "size"],
    )


def extract_component_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return extract_rows(data)[:limit]
    rows: list[dict[str, Any]] = []
    for section, key in [
        ("fund", "fundDataList"),
        ("stock", "stockList"),
        ("bond", "bondList"),
    ]:
        section_rows = data.get(key)
        if not isinstance(section_rows, list):
            continue
        for row in section_rows:
            if isinstance(row, dict):
                rows.append({"section": section, **row})
            if len(rows) >= limit:
                return rows
    return rows


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
