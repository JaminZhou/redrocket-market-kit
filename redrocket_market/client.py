from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
import re
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
INDEX_ARCHIVES_ENDPOINT = "/fundex-quote/index/archives"
INDEX_LABEL_ENDPOINT = "/fundex-quote/index/indexLabel"
INDEX_ROE_ENDPOINT = "/fundex-quote/index/roe"
INDEX_COMPONENT_ENDPOINT = "/fundex-quote/index/component"
INDEX_VALUATION_ENDPOINT = "/fundex-quote/index/valuation"
INDEX_REVENUE_PROFIT_ENDPOINT = "/fundex-quote/index/revenueProfit"
INDEX_RISK_RETURN_ENDPOINT = "/fundex-quote/index/riskReturn"
INDEX_MAIN_FUND_ENDPOINT = "/fundex-quote/indexRelated/mainFund"
COMPONENT_STOCK_ENDPOINT = "/fundex-quote/security/component/componentStock"
SECURITY_INDUSTRY_DISTRIBUTION_ENDPOINT = (
    "/fundex-quote/security/component/industryDistribution"
)
SECURITY_COMPONENT_DEVELOP_ENDPOINT = "/fundex-quote/security/component/componentDevelop"
SECURITY_MUST_SEE_ENDPOINT = "/fundex-quote/security/info/queryMustSee"
ETF_QUOTE_ENDPOINT = "/fundex-quote/security/quote"
ETF_PANORAMA_ENDPOINT = "/fundex-quote/security/detail/etf/panorama"
ETF_NET_SUBSCRIPTION_ENDPOINT = "/fundex-quote/security/detail/etf/queryNetSubscription"
ETF_SHARE_CHANGE_ENDPOINT = "/fundex-quote/security/detail/etf/queryEtfShareChange"
ETF_MARGIN_ENDPOINT = "/fundex-quote/security/detail/etf/queryMarginData"
ETF_LINK_FUND_ENDPOINT = "/fundex-quote/security/detail/etf/getLinkFund"
TRACKING_INDEX_ENDPOINT = "/fundex-quote/security/component/trackingIndex"
FUND_SITUATION_ENDPOINT = "/fundex-quote/fund/fundSituation"
FUND_BASE_ENDPOINT = "/fundex-quote/fund/otcFundBase"
FUND_COMPONENTS_ENDPOINT = "/fundex-quote/fund/otcFundComponentsList"
FUND_HISTORY_NAV_ENDPOINT = "/fundex-quote/fund/historyNetValue"
FUND_SALE_STATUS_ENDPOINT = "/fundex-quote/fund/queryFundSaleStatus"
FUND_ASSET_DISTRIBUTION_ENDPOINT = "/fundex-quote/fund/otcFundAssetDistribution"
FUND_ANNOUNCEMENT_LIST_ENDPOINT = "/fundex-quote/fund/announcement/list"
FUND_ANNOUNCEMENT_DETAIL_ENDPOINT = "/fundex-quote/fund/announcement/detail"
MANAGER_DETAIL_ENDPOINT = "/fundex-quote/manager/detail"
HEAT_ENDPOINT = "/fundex-activity/opportunity/findHomeHeatV3"
NEWS_ENDPOINT = "/fundex-activity/opportunity/findHomeNews"
WIND_ENDPOINT = "/fundex-quote/signal/getOneLevelPage"
COMPARE_RECOMMEND_ENDPOINT = "/fundex-quote/compare/recommendCompareList"
COMPARE_ARCHIVES_ENDPOINT = "/fundex-quote/compare/index/archives"
COMPARE_SIMILARITY_ENDPOINT = "/fundex-quote/compare/index/compareSimilarity"
COMPARE_TEN_WEIGHT_STOCK_ENDPOINT = "/fundex-quote/compare/index/compareTenWeightStock"
COMPARE_MARKET_VALUE_ENDPOINT = "/fundex-quote/compare/index/compareMarketValue"
COMPARE_PERFORMANCE_CORRELATION_ENDPOINT = (
    "/fundex-quote/compare/index/performanceCorrelation"
)
COMPARE_VALUATION_GROWTH_ENDPOINT = "/fundex-quote/compare/index/valuationGrowthRatio"

DISCOVERY_SOURCE_LIMITS = [
    "Red Rocket valuation, flow, heat, news, wind-vane, and comparison rows are auxiliary discovery context, not standalone investment signals.",
    "Verify exchange quotes, fund announcements, sales-channel rules, and local investment policy before decision use.",
]

FUND_SOURCE_LIMITS = [
    "Red Rocket fund profiles, notices, manager background, sale status, and asset allocation are auxiliary context, not official fund-company or sales-channel records.",
    "Verify fund company announcements, actual sales-channel limits, fees, settlement rules, and local investment policy before decision use.",
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

    def index(self, security_code: str, *, limit: int = 10) -> dict[str, Any]:
        archives = self.get(INDEX_ARCHIVES_ENDPOINT, {"securityCode": security_code})
        labels = self.get(INDEX_LABEL_ENDPOINT, {"securityCode": security_code})
        roe = self.get(INDEX_ROE_ENDPOINT, {"securityCode": security_code})
        return {
            "kind": "index",
            "fetched_at": now_iso(),
            "source": {
                "archives": archives.url,
                "labels": labels.url,
                "roe": roe.url,
            },
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "security_code": security_code,
            "summary": summarize_index_archives(archives.data),
            "labels": summarize_index_labels(labels.data),
            "roe_report_date": roe.data.get("reportDate") if isinstance(roe.data, dict) else None,
            "roe": extract_recent_series(roe.data, limit),
        }

    def index_detail_plus(
        self,
        security_code: str,
        *,
        valuation_type: str = "PE",
        time_interval: str = "last_5_years",
        industry_level: str = "3",
        limit: int = 10,
    ) -> dict[str, Any]:
        valuation = self.get(
            INDEX_VALUATION_ENDPOINT,
            {
                "securityCode": security_code,
                "valuationType": valuation_type,
                "timeInterval": time_interval,
            },
        )
        components = self.get(
            INDEX_COMPONENT_ENDPOINT,
            {
                "securityCode": security_code,
                "businessCode": "03",
                "industriesLevelNum": "2",
            },
        )
        revenue_profit = self.get(
            INDEX_REVENUE_PROFIT_ENDPOINT,
            {"securityCode": security_code, "range": "", "businessCode": "01"},
        )
        risk_return = self.get(INDEX_RISK_RETURN_ENDPOINT, {"indexCode": security_code})
        industry_distribution = self.get(
            SECURITY_INDUSTRY_DISTRIBUTION_ENDPOINT,
            {"securityCode": security_code, "industryLevel": industry_level},
        )
        component_develop = self.get(
            SECURITY_COMPONENT_DEVELOP_ENDPOINT,
            {"securityCode": security_code, "quarter": "LATEST"},
        )
        must_see = self.get(
            SECURITY_MUST_SEE_ENDPOINT,
            {"securityCode": security_code, "isCapital": "false"},
        )
        main_fund = self.get(INDEX_MAIN_FUND_ENDPOINT, {"securityCode": security_code})
        return {
            "kind": "index_detail_plus",
            "fetched_at": now_iso(),
            "source": {
                "valuation": valuation.url,
                "components": components.url,
                "revenue_profit": revenue_profit.url,
                "risk_return": risk_return.url,
                "industry_distribution": industry_distribution.url,
                "component_develop": component_develop.url,
                "must_see": must_see.url,
                "main_fund": main_fund.url,
            },
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "security_code": security_code,
            "valuation_type": valuation_type,
            "time_interval": time_interval,
            "valuation": summarize_index_valuation(valuation.data),
            "valuation_rows": extract_valuation_rows(valuation.data, limit),
            "component_report_date": (
                components.data.get("reportDate")
                if isinstance(components.data, dict)
                else None
            ),
            "components": extract_index_component_rows(components.data, limit),
            "revenue_profit": extract_revenue_profit_rows(revenue_profit.data, limit),
            "risk_return": summarize_risk_return(risk_return.data),
            "industry_distribution": summarize_industry_distribution(
                industry_distribution.data,
                limit,
            ),
            "component_develop": extract_component_develop_rows(
                component_develop.data,
                limit,
            ),
            "must_see": summarize_must_see(must_see.data),
            "main_fund": extract_main_funds(main_fund.data, limit),
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

    def components(self, security_code: str, *, limit: int = 20) -> dict[str, Any]:
        result = self.get(
            COMPONENT_STOCK_ENDPOINT,
            {"securityCode": security_code, "isAll": "1"},
        )
        data = result.data if isinstance(result.data, dict) else {}
        rows = data.get("componentStockListVos")
        if not isinstance(rows, list):
            rows = extract_rows(result.data)
        return {
            "kind": "components",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "security_code": security_code,
            "total": data.get("total"),
            "industry_type": data.get("industryType"),
            "update": data.get("showUpdateStr"),
            "rows": [
                normalize_component_stock(row)
                for row in rows[:limit]
                if isinstance(row, dict)
            ],
        }

    def etf_detail(self, security_code: str, *, limit: int = 10) -> dict[str, Any]:
        quote = self.get(ETF_QUOTE_ENDPOINT, {"securityCode": security_code})
        panorama = self.get(ETF_PANORAMA_ENDPOINT, {"securityCode": security_code})
        subscription = self.get(ETF_NET_SUBSCRIPTION_ENDPOINT, {"securityCode": security_code})
        return {
            "kind": "etf_detail",
            "fetched_at": now_iso(),
            "source": {
                "quote": quote.url,
                "panorama": panorama.url,
                "subscription": subscription.url,
            },
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "security_code": security_code,
            "quote": summarize_etf_quote(quote.data),
            "profile": summarize_etf_profile(panorama.data),
            "performance": summarize_etf_performance(panorama.data, limit),
            "subscription": summarize_subscription(subscription.data),
            "subscription_rows": extract_subscription_rows(subscription.data, limit),
        }

    def etf_flow(
        self,
        security_code: str,
        *,
        period: str = "3M",
        limit: int = 10,
    ) -> dict[str, Any]:
        subscription = self.get(
            ETF_NET_SUBSCRIPTION_ENDPOINT,
            {"securityCode": security_code},
        )
        share_change = self.get(
            ETF_SHARE_CHANGE_ENDPOINT,
            {"securityCode": security_code, "period": period},
        )
        margin = self.get(ETF_MARGIN_ENDPOINT, {"securityCode": security_code})
        link_fund = self.get(ETF_LINK_FUND_ENDPOINT, {"securityCode": security_code})
        tracking_index = self.get(TRACKING_INDEX_ENDPOINT, {"securityCode": security_code})
        return {
            "kind": "etf_flow",
            "fetched_at": now_iso(),
            "source": {
                "subscription": subscription.url,
                "share_change": share_change.url,
                "margin": margin.url,
                "link_fund": link_fund.url,
                "tracking_index": tracking_index.url,
            },
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "security_code": security_code,
            "period": period,
            "subscription": summarize_subscription(subscription.data),
            "subscription_rows": extract_subscription_rows(subscription.data, limit),
            "share_change": summarize_share_change(share_change.data),
            "share_change_rows": extract_share_change_rows(share_change.data, limit),
            "margin": summarize_margin(margin.data),
            "margin_rows": extract_margin_rows(margin.data, limit),
            "link_fund": summarize_link_fund(link_fund.data),
            "tracking_index": summarize_tracking_index(tracking_index.data),
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

    def index_compare(
        self,
        index_infos: list[tuple[str, str]],
        *,
        limit: int = 10,
    ) -> dict[str, Any]:
        index_codes = ",".join(code for code, _ in index_infos)
        index_info_text = ",".join(f"{code}-{name}" for code, name in index_infos)
        archives = self.get(COMPARE_ARCHIVES_ENDPOINT, {"indexCodes": index_codes})
        similarity = self.get(COMPARE_SIMILARITY_ENDPOINT, {"indexCodes": index_codes})
        ten_weight = self.get(
            COMPARE_TEN_WEIGHT_STOCK_ENDPOINT,
            {"indexCodes": index_codes},
        )
        market_value = self.get(
            COMPARE_MARKET_VALUE_ENDPOINT,
            {"indexCodes": index_codes},
        )
        performance = self.get(
            COMPARE_PERFORMANCE_CORRELATION_ENDPOINT,
            {"indexCodes": index_codes},
        )
        valuation_growth = self.get(
            COMPARE_VALUATION_GROWTH_ENDPOINT,
            {"indexInfos": index_info_text, "tabType": "PEG"},
        )
        return {
            "kind": "index_compare",
            "fetched_at": now_iso(),
            "source": {
                "archives": archives.url,
                "similarity": similarity.url,
                "ten_weight": ten_weight.url,
                "market_value": market_value.url,
                "performance_correlation": performance.url,
                "valuation_growth": valuation_growth.url,
            },
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "index_codes": index_codes,
            "index_infos": index_info_text,
            "archives": extract_compare_rows(archives.data, limit),
            "similarity": extract_compare_rows(similarity.data, limit),
            "ten_weight": extract_compare_rows(ten_weight.data, limit),
            "market_value": extract_compare_rows(market_value.data, limit),
            "performance_correlation": limit_nested_series(performance.data, limit),
            "valuation_growth": extract_items(valuation_growth.data, limit),
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
        sale_status = self.get(FUND_SALE_STATUS_ENDPOINT, {"fundCode": security_code})
        asset_distribution = self.post(
            FUND_ASSET_DISTRIBUTION_ENDPOINT,
            {"securityCode": security_code},
            {},
        )
        return {
            "kind": "fund",
            "fetched_at": now_iso(),
            "source_limits": FUND_SOURCE_LIMITS,
            "source": {
                "base": base.url,
                "situation": situation.url,
                "components": components.url,
                "nav": nav.url,
                "sale_status": sale_status.url,
                "asset_distribution": asset_distribution.url,
            },
            "fund_code": fund_code,
            "base": summarize_fund_base(base.data),
            "situation": summarize_fund_situation(situation.data),
            "components": extract_component_rows(components.data, limit),
            "nav": extract_rows(nav.data)[:limit],
            "sale_status": summarize_fund_sale_status(sale_status.data),
            "asset_allocation": extract_asset_allocation(asset_distribution.data),
            "asset_weights": extract_asset_weight_rows(asset_distribution.data, limit),
        }

    def fund_notices(
        self,
        fund_code: str,
        *,
        page: int = 1,
        limit: int = 10,
        detail_id: str | None = None,
    ) -> dict[str, Any]:
        security_code = normalize_fund_code(fund_code)
        notices = self.get(
            FUND_ANNOUNCEMENT_LIST_ENDPOINT,
            {"pageNum": str(page), "pageSize": str(limit), "fundCode": security_code},
        )
        detail = None
        source: dict[str, str] = {"list": notices.url}
        if detail_id:
            detail_result = self.get(FUND_ANNOUNCEMENT_DETAIL_ENDPOINT, {"id": detail_id})
            detail = summarize_notice_detail(detail_result.data)
            source["detail"] = detail_result.url
        return {
            "kind": "fund_notices",
            "fetched_at": now_iso(),
            "source": source,
            "source_limits": FUND_SOURCE_LIMITS,
            "fund_code": fund_code,
            "normalized_fund_code": security_code,
            "page": page,
            "rows": [
                normalize_notice(row)
                for row in extract_rows(notices.data)[:limit]
            ],
            "detail": detail,
        }

    def manager(self, security_code: str, *, limit: int = 10) -> dict[str, Any]:
        normalized_code = normalize_fund_code(security_code)
        result = self.get(MANAGER_DETAIL_ENDPOINT, {"securityCode": normalized_code})
        return {
            "kind": "manager",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": FUND_SOURCE_LIMITS,
            "security_code": security_code,
            "normalized_security_code": normalized_code,
            "rows": [
                normalize_manager(row, limit=limit)
                for row in extract_rows(result.data)[:limit]
            ],
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
            "price",
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
            "marketTip",
            "marketType",
            "marketValue",
            "volumeRatio",
        ],
    )


def summarize_index_archives(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    security = data.get("security") if isinstance(data.get("security"), dict) else data
    return compact_dict(
        security,
        [
            "securityCode",
            "securityName",
            "securityAbbreviation",
            "publisher",
            "baseDay",
            "basePoint",
            "componentCount",
            "etfCount",
            "otcCount",
            "scale",
            "etfMarketValue",
            "otcMarketValue",
            "fundCode",
            "fundName",
            "fundType",
            "changePercentY1",
        ],
    )


def summarize_index_labels(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    return compact_dict(
        data,
        [
            "valuationTypeLabel",
            "focusValPubLabel",
            "valuationExists",
            "roeExists",
            "revenueProfitExists",
            "componentExists",
            "isContainsHk",
            "isAllHk",
        ],
    )


def normalize_component_stock(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        row,
        [
            "securityCode",
            "securityName",
            "changePercent",
            "price",
            "volume",
            "amount",
            "weight",
            "changeWeight",
            "ratio",
            "netCapitalFlow",
            "turnoverRate",
            "priceEarningRatioTtm",
            "marketValue",
        ],
    )


def extract_recent_series(data: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    rows = data.get("items") if isinstance(data.get("items"), list) else []
    normalized = [
        compact_dict(row, ["date", "value"])
        for row in rows
        if isinstance(row, dict)
    ]
    return normalized[-limit:] if limit > 0 else []


def summarize_index_valuation(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    return compact_dict(
        data,
        [
            "valuation",
            "valuationQuantileNew",
            "percentile",
            "valuationTag",
            "pe",
            "pb",
            "peg",
            "maxValuation",
            "minValuation",
        ],
    )


def extract_items(data: Any, limit: int) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        rows = data.get("items") if isinstance(data.get("items"), list) else []
    else:
        rows = data if isinstance(data, list) else []
    filtered = [row for row in rows if isinstance(row, dict)]
    return filtered[:limit] if limit > 0 else []


def extract_valuation_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    rows = extract_items(data, 10_000)
    normalized = [
        compact_dict(
            row,
            [
                "date",
                "tradeDate",
                "valuation",
                "valuationValue",
                "valuationQuantileNew",
                "percentile",
                "historicalPercentile",
                "pe",
                "pb",
                "peg",
            ],
        )
        for row in rows
    ]
    return normalized[:limit] if limit > 0 else []


def extract_index_component_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    return [
        compact_dict(
            row,
            [
                "securityCode",
                "securityName",
                "componentCode",
                "componentName",
                "stockCode",
                "stockName",
                "industriesCode",
                "industriesName",
                "industryName",
                "weight",
                "proportion",
                "value",
                "marketValue",
            ],
        )
        for row in extract_items(data, limit)
    ]


def extract_revenue_profit_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    return [
        compact_dict(
            row,
            [
                "year",
                "date",
                "revenue",
                "revenueGrowthRate",
                "profit",
                "profitGrowthRate",
            ],
        )
        for row in extract_items(data, limit)
    ]


def summarize_risk_return(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    return compact_dict(
        data,
        [
            "lastOneYearReturn",
            "lastThreeYearReturn",
            "lastFiveYearReturn",
            "lastOneYearMaxDrawdown",
            "lastThreeYearMaxDrawdown",
            "lastFiveYearMaxDrawdown",
        ],
    )


def summarize_industry_distribution(data: Any, limit: int) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    result = compact_dict(data, ["latestDate", "industryLevelType"])
    result_map = data.get("resultMap")
    if isinstance(result_map, dict):
        bucket_name, rows = select_industry_distribution_bucket(
            result_map,
            normalize_report_date(data.get("latestDate")),
        )
        if bucket_name:
            result["latestBucket"] = bucket_name
        if rows:
            result["latest"] = rows[:limit]
    return result


def select_industry_distribution_bucket(
    result_map: dict[str, Any],
    latest_date: str | None = None,
) -> tuple[str | None, list[dict[str, Any]]]:
    latest = result_map.get("最新")
    if isinstance(latest, list):
        return "最新", normalize_industry_distribution_rows(latest)

    list_buckets = [
        (name, value)
        for name, value in result_map.items()
        if isinstance(value, list)
    ]
    if list_buckets:
        if latest_date:
            matched = find_industry_bucket_by_date(list_buckets, latest_date)
            if matched:
                name, value = matched
                return name, normalize_industry_distribution_rows(value)
        named = [
            (date, name, value)
            for name, value in list_buckets
            if (date := normalize_report_date(name) or parse_industry_bucket_date(name))
        ]
        if named:
            _, name, value = max(named, key=lambda item: item[0])
            return name, normalize_industry_distribution_rows(value)
        name, value = list_buckets[-1]
        return name, normalize_industry_distribution_rows(value)

    rows = []
    for name, value in result_map.items():
        if isinstance(value, dict):
            rows.append({"industryName": name, **value})
        elif value not in (None, ""):
            rows.append({"industryName": name, "weight": value})
    return None, normalize_industry_distribution_rows(rows)


def find_industry_bucket_by_date(
    list_buckets: list[tuple[str, Any]],
    latest_date: str,
) -> tuple[str, Any] | None:
    for name, value in list_buckets:
        if normalize_report_date(name) == latest_date:
            return name, value
        rows = [row for row in value if isinstance(row, dict)]
        if any(normalize_report_date(row.get("report")) == latest_date for row in rows):
            return name, value
        if parse_industry_bucket_date(name) == latest_date:
            return name, value
    return None


def normalize_report_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    digits = re.sub(r"\D", "", str(value))
    if len(digits) == 8:
        return digits
    return None


def parse_industry_bucket_date(name: str) -> str | None:
    year_match = re.search(r"(20\d{2}|\d{2})", name)
    if not year_match:
        return None
    year_text = year_match.group(1)
    year = int(year_text) if len(year_text) == 4 else 2000 + int(year_text)
    if "一季" in name or "一季报" in name or "Q1" in name.upper():
        return f"{year}0331"
    if "中报" in name or "半年" in name or "Q2" in name.upper():
        return f"{year}0630"
    if "三季" in name or "三季报" in name or "Q3" in name.upper():
        return f"{year}0930"
    if "年末" in name or "年报" in name or "Q4" in name.upper():
        return f"{year}1231"
    return None


def normalize_industry_distribution_rows(rows: list[Any]) -> list[dict[str, Any]]:
    return [
        compact_dict(row, ["industryName", "weight", "report", "industryLevelType"])
        for row in rows
        if isinstance(row, dict)
    ]


def extract_component_develop_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    return [
        compact_dict(
            row,
            [
                "year",
                "revTol",
                "csrTen",
                "csRateTen",
                "npTol",
                "npTTen",
                "npRateTen",
            ],
        )
        for row in extract_items(data, limit)
    ]


def summarize_must_see(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    return compact_dict(data, ["capital", "pe", "roe", "profit"])


def extract_main_funds(data: Any, limit: int) -> dict[str, list[dict[str, Any]]]:
    if not isinstance(data, dict):
        return {"etf": [], "otc": []}
    result: dict[str, list[dict[str, Any]]] = {"etf": [], "otc": []}
    for key in result:
        section = data.get(key)
        if isinstance(section, list):
            result[key] = [
                normalize_related(row)
                for row in section[:limit]
                if isinstance(row, dict)
            ]
        elif isinstance(section, dict):
            result[key] = [summarize_main_fund_entry(section)]
    return result


def summarize_main_fund_entry(data: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        data,
        [
            "fundCode",
            "fundName",
            "securityCode",
            "securityName",
            "securityType",
            "changePercent",
            "scale",
            "totalNumber",
            "totalScale",
        ],
    )


def summarize_etf_quote(data: Any) -> dict[str, Any]:
    return normalize_quote(data) if isinstance(data, dict) else {}


def summarize_etf_profile(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    security_info = (
        data.get("securityInfo") if isinstance(data.get("securityInfo"), dict) else {}
    )
    managers = data.get("fundManager") if isinstance(data.get("fundManager"), list) else []
    manager_names = [
        row.get("name")
        for row in managers
        if isinstance(row, dict) and row.get("name")
    ]
    result = compact_dict(
        security_info,
        [
            "securityCode",
            "securityName",
            "establishDate",
            "investType",
            "share",
            "scale",
            "securityCompany",
            "custodianBank",
            "tradeDate",
        ],
    )
    if manager_names:
        result["managerNames"] = ", ".join(manager_names)
    return result


def summarize_etf_performance(data: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    rows = data.get("performanceReview") if isinstance(data.get("performanceReview"), list) else []
    return [
        compact_dict(
            row,
            [
                "dateRangeName",
                "rangeChangePercent",
                "sameKindAvg",
                "sameKindRank",
                "sameKindRankTotal",
                "rankTag",
            ],
        )
        for row in rows[:limit]
        if isinstance(row, dict)
    ]


def summarize_subscription(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    return compact_dict(
        data,
        [
            "tradeDt",
            "totalShare",
            "netSubscriptionShares",
            "netSubscriptionSharePct",
        ],
    )


def extract_subscription_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    rows = data.get("subscriptionShareList")
    if not isinstance(rows, list):
        return []
    return [
        compact_dict(row, ["tradeDt", "totalShare", "netSubscriptionShares", "price"])
        for row in rows[-limit:]
        if isinstance(row, dict)
    ]


def summarize_share_change(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    float_share = data.get("floatShare")
    if isinstance(float_share, dict):
        return compact_dict(
            float_share,
            [
                "tradeDt",
                "totalShare",
                "shareChange",
                "scale",
                "scaleChange",
                "price",
            ],
        )
    return compact_dict(
        data,
        [
            "tradeDt",
            "floatShare",
            "share",
            "shareChange",
            "shareChangePct",
        ],
    )


def extract_share_change_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    rows = data.get("shareList") if isinstance(data.get("shareList"), list) else []
    normalized = [
        compact_dict(
            row,
            [
                "tradeDt",
                "floatShare",
                "share",
                "totalShare",
                "shareChange",
                "shareChangePct",
                "scale",
                "scaleChange",
                "price",
            ],
        )
        for row in rows
        if isinstance(row, dict)
    ]
    return normalized[-limit:] if limit > 0 else []


def summarize_margin(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    return compact_dict(
        data,
        [
            "tradeDt",
            "marginNetInflow",
            "fiveMarginNetInflow",
            "twentyMarginNetInflow",
            "sixtyMarginNetInflow",
        ],
    )


def extract_margin_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    rows = data.get("marginDataList")
    if not isinstance(rows, list):
        return []
    normalized = [
        compact_dict(
            row,
            [
                "tradeDt",
                "marginNetInflow",
                "finBalance",
                "secBalance",
                "marginBalance",
            ],
        )
        for row in rows
        if isinstance(row, dict)
    ]
    return normalized[-limit:] if limit > 0 else []


def summarize_link_fund(data: Any) -> dict[str, Any]:
    return normalize_related(data) if isinstance(data, dict) else {}


def summarize_tracking_index(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    return compact_dict(
        data,
        [
            "securityCode",
            "securityName",
            "securityType",
            "price",
            "changePercent",
            "change",
            "securityCount",
            "yearlyPerformance",
            "listingTimeFlag",
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


def extract_compare_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    rows = extract_rows(data)
    return rows[:limit] if limit > 0 else []


def limit_nested_series(data: Any, limit: int) -> Any:
    if isinstance(data, list):
        return data[:limit] if limit > 0 else []
    if not isinstance(data, dict):
        return data
    limited: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, list):
            limited[key] = value[-limit:] if limit > 0 else []
        else:
            limited[key] = value
    return limited


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


def summarize_fund_sale_status(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    return compact_dict(
        data,
        [
            "fundCode",
            "richChannel",
            "financialLinkChannel",
            "securityType",
        ],
    )


def extract_asset_allocation(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    rows = data.get("assetDataList")
    if not isinstance(rows, list):
        return []
    return [
        compact_dict(row, ["assetName", "assetVal"])
        for row in rows
        if isinstance(row, dict)
    ]


def extract_asset_weight_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    rows = data.get("assetWeightDataList")
    if not isinstance(rows, list):
        return []
    return [
        compact_dict(
            row,
            ["dataCode", "dataName", "dataPriceChange", "dataValueToNav", "dataValueRatio"],
        )
        for row in rows[:limit]
        if isinstance(row, dict)
    ]


def normalize_notice(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(row, ["id", "title", "announceTime"])


def summarize_notice_detail(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    result = compact_dict(data, ["id", "title", "announceTime"])
    content = str(data.get("content") or "")
    links = re.findall(r'href=[\"\']([^\"\']+)[\"\']', content)
    if links:
        result["attachmentUrls"] = links
    return result


def normalize_manager(row: dict[str, Any], *, limit: int) -> dict[str, Any]:
    result = compact_dict(row, ["id", "name", "employmentPeriod", "resume"])
    securities = row.get("managedSecurities")
    if isinstance(securities, list):
        result["managedSecurities"] = [
            normalize_related(item)
            for item in securities[:limit]
            if isinstance(item, dict)
        ]
    return result
