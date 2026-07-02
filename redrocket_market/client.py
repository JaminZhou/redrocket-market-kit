from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from html import unescape
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


BASE_URL = "https://hongsehuojian.com"
REFERER = f"{BASE_URL}/red-rocket/indexBrowser"

LIST_ENDPOINT = "/fundex-quote/allPage/findListBySecurity"
ETF_LIST_ENDPOINT = "/fundex-quote/allPage/findListByEtf"
SEARCH_ENDPOINT = "/fundex-quote/search/list"
BATCH_QUOTE_ENDPOINT = "/fundex-quote/search/batchQueryQuoteData"
BATCH_PRICE_PERCENT_ENDPOINT = "/fundex-quote/security/batchFindPriceAndPercent"
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
SECURITY_INFO_ENDPOINT = "/fundex-quote/security/info"
SECURITY_TYPE_ENDPOINT = "/fundex-quote/securityInfo/findSecurityType"
SECURITY_CHANGE_LIST_ENDPOINT = "/fundex-quote/change/list"
SECURITY_MINUTE_ENDPOINT = "/fundex-quote/security/minute"
SECURITY_HISTORY_POSITION_ENDPOINT = (
    "/fundex-quote/security/component/historyPositionChange"
)
SECURITY_MARKET_VALUE_DISTRIBUTE_ENDPOINT = (
    "/fundex-quote/security/component/marketValueDistribute"
)
SECURITY_WEIGHT_CONCENTRATION_ENDPOINT = (
    "/fundex-quote/security/component/weightConcentrationRatio"
)
ETF_QUOTE_ENDPOINT = "/fundex-quote/security/quote"
ETF_PANORAMA_ENDPOINT = "/fundex-quote/security/detail/etf/panorama"
ETF_NET_SUBSCRIPTION_ENDPOINT = "/fundex-quote/security/detail/etf/queryNetSubscription"
ETF_SHARE_CHANGE_ENDPOINT = "/fundex-quote/security/detail/etf/queryEtfShareChange"
ETF_MARGIN_ENDPOINT = "/fundex-quote/security/detail/etf/queryMarginData"
ETF_FIVE_MFD_INFLOW_ENDPOINT = "/fundex-quote/security/detail/etf/queryFiveMfdInFlow"
ETF_LINK_FUND_ENDPOINT = "/fundex-quote/security/detail/etf/getLinkFund"
TRACKING_INDEX_ENDPOINT = "/fundex-quote/security/component/trackingIndex"
INDUSTRY_LIST_ENDPOINT = "/fundex-quote/industry/list"
INDUSTRY_QUOTE_ENDPOINT = "/fundex-quote/industry/industryIndexQuote"
INDUSTRY_INDEX_CODES_ENDPOINT = "/fundex-quote/industry/getIndexCodeList"
INDUSTRY_CLASSIFY_ENDPOINT = "/fundex-quote/industry/getClassifyList"
INDUSTRY_CLASSIFY_DATA_ENDPOINT = "/fundex-quote/industry/getClassifyDataList"
INDUSTRY_RELATED_ENDPOINT = "/fundex-quote/industry/indexRelatedIndustry"
INDUSTRY_CHART_ENDPOINT = "/fundex-quote/industry/chart"
INDUSTRY_MEMOIR_ENDPOINT = "/fundex-quote/industry/getMemoirList"
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
HOT_SHOW_STATUS_ENDPOINT = "/fundex-activity/hot/getShowStatus"
HOT_LIST_ENDPOINT = "/fundex-activity/hot/getList"
NEWS_ENDPOINT = "/fundex-activity/opportunity/findHomeNews"
FOCUS_NEWS_ENDPOINT = "/fundex-activity/opportunity/focusNews"
KNOWLEDGE_ENDPOINT = "/fundex-activity/knowledgeBase/findKnowledgeInfoListByKeyList"
CLASS_INFO_ENDPOINT = "/fundex-quote/allPage/findClassInfo"
MUST_READ_ENDPOINT = "/fundex-status/status/findFreshList"
COMMUNITY_STATUS_DETAIL_ENDPOINT = "/fundex-status/community/status/detail"
WIND_ENDPOINT = "/fundex-quote/signal/getOneLevelPage"
SIGNAL_DETAIL_ENDPOINT = "/fundex-quote/signal/getDetailPage"
COMPARE_RECOMMEND_ENDPOINT = "/fundex-quote/compare/recommendCompareList"
COMPARE_ARCHIVES_ENDPOINT = "/fundex-quote/compare/index/archives"
COMPARE_SIMILARITY_ENDPOINT = "/fundex-quote/compare/index/compareSimilarity"
COMPARE_TEN_WEIGHT_STOCK_ENDPOINT = "/fundex-quote/compare/index/compareTenWeightStock"
COMPARE_MARKET_VALUE_ENDPOINT = "/fundex-quote/compare/index/compareMarketValue"
COMPARE_PERFORMANCE_CORRELATION_ENDPOINT = (
    "/fundex-quote/compare/index/performanceCorrelation"
)
COMPARE_VALUATION_GROWTH_ENDPOINT = "/fundex-quote/compare/index/valuationGrowthRatio"
COMPARE_INTERVAL_CHANGE_ENDPOINT = "/fundex-quote/compare/index/intervalChangePercent"
COMPARE_FUND_LIST_ENDPOINT = "/fundex-quote/compare/fundListCompare"
COMPARE_SPECIAL_MARKET_ENDPOINT = "/fundex-quote/compare/getSpecialMarketInfo"
VALUATION_ROE_TIME_ENDPOINT = "/fundex-quote/knowledgebase/queryValuationAndRoeTime"

SEARCH_GROUP_KEYS = ("index", "etf", "fund", "stock")
SEARCH_BATCH_LIST_KEYS = ("indexList", "etfList", "fundList", "stockList")

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

KNOWLEDGE_SOURCE_LIMITS = [
    "Red Rocket knowledge-base rows are platform methodology/help text, not live market facts or official fund-company records.",
    "Use them only to interpret Red Rocket labels; verify decision-sensitive facts elsewhere.",
]

ARTICLE_CONTENT_EXCERPT_MAX = 1000


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


def split_security_codes(security_codes: str) -> list[str]:
    return [code.strip() for code in security_codes.split(",") if code.strip()]


def infer_exchange_market(security_code: Any) -> str | None:
    if not isinstance(security_code, str) or "." not in security_code:
        return None
    suffix = security_code.rsplit(".", 1)[1].strip()
    return suffix or None


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

    def search(self, keyword: str, *, limit: int = 20) -> dict[str, Any]:
        result = self.get(SEARCH_ENDPOINT, {"searchKeyword": keyword, "isSearchAll": "false"})
        candidates = extract_search_candidates(result.data, limit)
        source = {"list": result.url}
        quote_by_code: dict[str, dict[str, Any]] = {}
        security_codes = [
            code
            for row in candidates
            if (code := search_candidate_code(row)) is not None
        ]
        if security_codes:
            batch_quote = self.post(
                BATCH_QUOTE_ENDPOINT,
                None,
                {"securityType": "all", "securityCodeList": security_codes},
            )
            source["batch_quote"] = batch_quote.url
            quote_by_code = extract_batch_quote_map(batch_quote.data)
        return {
            "kind": "search",
            "fetched_at": now_iso(),
            "source": source,
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "keyword": keyword,
            "groups": count_search_groups(result.data),
            "rows": [
                normalize_search_result(row, quote_by_code.get(search_candidate_code(row) or "") or {})
                for row in candidates
            ],
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

    def snapshot(self, security_codes: str) -> dict[str, Any]:
        codes = split_security_codes(security_codes)
        normalized_codes = ",".join(codes)
        snapshot = self.post(
            BATCH_PRICE_PERCENT_ENDPOINT,
            {"securityCodes": normalized_codes},
            {"securityCodes": codes},
        )
        source = {"snapshot": snapshot.url}
        type_by_code: dict[str, dict[str, Any]] = {}
        for code in codes:
            security_type = self.get(SECURITY_TYPE_ENDPOINT, {"securityCode": code})
            source["security_type"] = security_type.url
            if (
                isinstance(security_type.data, dict)
                and security_type.data.get("securityCode") == code
            ):
                type_by_code[code] = security_type.data
        rows = snapshot.data if isinstance(snapshot.data, list) else extract_rows(snapshot.data)
        return {
            "kind": "snapshot",
            "fetched_at": now_iso(),
            "source": source,
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "security_codes": normalized_codes,
            "rows": [
                normalize_snapshot(row, type_by_code.get(row.get("securityCode") or "") or {})
                for row in rows
                if isinstance(row, dict)
            ],
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

    def security_context(self, security_code: str, *, limit: int = 10) -> dict[str, Any]:
        info = self.get(SECURITY_INFO_ENDPOINT, {"securityCode": security_code})
        changes = self.get(SECURITY_CHANGE_LIST_ENDPOINT, {"securityCode": security_code})
        minute = self.get(SECURITY_MINUTE_ENDPOINT, {"securityCode": security_code})
        history_position = self.get(
            SECURITY_HISTORY_POSITION_ENDPOINT,
            {"securityCode": security_code},
        )
        market_value_distribution = self.get(
            SECURITY_MARKET_VALUE_DISTRIBUTE_ENDPOINT,
            {"securityCode": security_code},
        )
        weight_concentration = self.get(
            SECURITY_WEIGHT_CONCENTRATION_ENDPOINT,
            {"securityCode": security_code},
        )
        return {
            "kind": "security_context",
            "fetched_at": now_iso(),
            "source": {
                "info": info.url,
                "change": changes.url,
                "minute": minute.url,
                "history_position": history_position.url,
                "market_value_distribution": market_value_distribution.url,
                "weight_concentration": weight_concentration.url,
            },
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "security_code": security_code,
            "info": summarize_security_info(info.data),
            "change_rows": extract_security_change_rows(changes.data, limit),
            "minute_rows": extract_security_minute_rows(minute.data, limit),
            "history_position": extract_security_structure_rows(
                history_position.data,
                limit,
            ),
            "market_value_distribution": extract_security_structure_rows(
                market_value_distribution.data,
                limit,
            ),
            "weight_concentration": extract_security_structure_rows(
                weight_concentration.data,
                limit,
                latest=True,
            ),
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
        five_mfd_inflow = self.get(
            ETF_FIVE_MFD_INFLOW_ENDPOINT,
            {"securityCode": security_code},
        )
        link_fund = self.get(ETF_LINK_FUND_ENDPOINT, {"securityCode": security_code})
        tracking_index = self.get(TRACKING_INDEX_ENDPOINT, {"securityCode": security_code})
        return {
            "kind": "etf_flow",
            "fetched_at": now_iso(),
            "source": {
                "subscription": subscription.url,
                "share_change": share_change.url,
                "margin": margin.url,
                "five_mfd_inflow": five_mfd_inflow.url,
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
            "five_mfd_inflow": summarize_five_mfd_inflow(five_mfd_inflow.data),
            "five_mfd_inflow_rows": extract_five_mfd_inflow_rows(
                five_mfd_inflow.data,
                limit,
            ),
            "link_fund": summarize_link_fund(link_fund.data),
            "tracking_index": summarize_tracking_index(tracking_index.data),
        }

    def industry(
        self,
        *,
        industry_id: str | None = None,
        indicator_id: str | None = None,
        index_code: str = "",
        limit: int = 5,
    ) -> dict[str, Any]:
        industry_list = self.get(INDUSTRY_LIST_ENDPOINT)
        industries = extract_industries(industry_list.data, limit)
        selected_id = industry_id or (industries[0].get("code") if industries else "")
        selected_name = next(
            (
                row.get("value")
                for row in industries
                if row.get("code") == selected_id and row.get("value")
            ),
            selected_id,
        )
        quote = self.get(INDUSTRY_QUOTE_ENDPOINT, {"industryId": selected_id})
        index_codes = self.get(INDUSTRY_INDEX_CODES_ENDPOINT, {"industryId": selected_id})
        classify = self.get(INDUSTRY_CLASSIFY_ENDPOINT, {"industryId": selected_id})
        related = self.get(INDUSTRY_RELATED_ENDPOINT, {"industryId": selected_id})
        chart = self.get(
            INDUSTRY_CHART_ENDPOINT,
            {"industryId": selected_id, "indexCode": index_code},
        )
        memoir = self.get(INDUSTRY_MEMOIR_ENDPOINT, {"industryId": selected_id})
        source = {
            "list": industry_list.url,
            "quote": quote.url,
            "index_codes": index_codes.url,
            "classify": classify.url,
            "related": related.url,
            "chart": chart.url,
            "memoir": memoir.url,
        }
        indicator_detail_data = None
        if indicator_id:
            indicator_detail = self.get(
                INDUSTRY_CLASSIFY_DATA_ENDPOINT,
                {"industryId": selected_id, "indicatorId": indicator_id},
            )
            source["indicator_detail"] = indicator_detail.url
            indicator_detail_data = indicator_detail.data
        return {
            "kind": "industry",
            "fetched_at": now_iso(),
            "source": source,
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "industry_id": selected_id,
            "industry_name": selected_name,
            "industries": industries,
            "quote": normalize_industry_quote(quote.data),
            "index_codes": extract_industry_index_codes(index_codes.data, limit),
            "classify": extract_industry_classify(classify.data, limit),
            "indicator_detail": summarize_industry_indicator_detail(
                indicator_detail_data,
                limit,
            ),
            "related_indicators": summarize_industry_related(related.data, limit),
            "chart": summarize_industry_chart(chart.data),
            "chart_rows": extract_industry_chart_rows(chart.data, limit),
            "memoirs": extract_industry_memoirs(memoir.data, limit),
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

    def hot_timeline(self, *, limit: int = 8) -> dict[str, Any]:
        status = self.get(HOT_SHOW_STATUS_ENDPOINT)
        timeline = self.get(HOT_LIST_ENDPOINT)
        buckets = timeline.data if isinstance(timeline.data, list) else []
        return {
            "kind": "hot_timeline",
            "fetched_at": now_iso(),
            "source": {
                "timeline": timeline.url,
                "show_status": status.url,
            },
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "show_status": status.data if isinstance(status.data, bool) else None,
            "rows": extract_hot_timeline_rows(buckets, limit),
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

    def classes(
        self,
        *,
        table_name: str = "index",
        page_name: str = "index",
        search_value: str = "",
        limit: int = 20,
    ) -> dict[str, Any]:
        result = self.get(
            CLASS_INFO_ENDPOINT,
            {"tableName": table_name, "pageName": page_name, "searchValue": search_value},
        )
        data = result.data if isinstance(result.data, dict) else {}
        rows = data.get("allList") if isinstance(data.get("allList"), list) else []
        cascade = data.get("cascade") if isinstance(data.get("cascade"), list) else []
        return {
            "kind": "classes",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "table_name": table_name,
            "page_name": page_name,
            "search_value": search_value,
            "all_list_size": data.get("allListSize"),
            "rows": [normalize_class_info(row) for row in rows[:limit] if isinstance(row, dict)],
            "cascade": [
                normalize_class_info(row)
                for row in cascade[:limit]
                if isinstance(row, dict)
            ],
        }

    def focus_news(self, *, limit: int = 8) -> dict[str, Any]:
        result = self.get(FOCUS_NEWS_ENDPOINT, {"newsSize": str(limit)})
        data = result.data if isinstance(result.data, dict) else {}
        columns = data.get("drawColumns") if isinstance(data.get("drawColumns"), str) else ""
        draw_points = parse_draw_points(data.get("draw"), columns)
        news_rows = data.get("news") if isinstance(data.get("news"), list) else []
        return {
            "kind": "focus_news",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "status": data.get("status"),
            "draw_columns": columns,
            "latest_point": draw_points[-1] if draw_points else None,
            "label_points": [row for row in draw_points if row.get("label")],
            "rows": [
                normalize_focus_news(row)
                for row in news_rows[:limit]
                if isinstance(row, dict)
            ],
        }

    def knowledge(
        self,
        knowledge_keys: list[str],
        *,
        content_limit: int = 240,
    ) -> dict[str, Any]:
        keys = [key.strip() for key in knowledge_keys if key.strip()]
        result = self.get(KNOWLEDGE_ENDPOINT, {"knowledgeKeyList": ",".join(keys)})
        return {
            "kind": "knowledge",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": KNOWLEDGE_SOURCE_LIMITS,
            "knowledge_keys": keys,
            "rows": [
                normalize_knowledge(row, content_limit=content_limit)
                for row in extract_rows(result.data)
            ],
        }

    def article(self, status_id: str, *, content_limit: int = 240) -> dict[str, Any]:
        result = self.get(COMMUNITY_STATUS_DETAIL_ENDPOINT, {"statusId": status_id})
        return {
            "kind": "article",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "status_id": status_id,
            "detail": normalize_article_detail(result.data, content_limit=content_limit),
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

    def signal_detail(self, security_code: str, *, limit: int = 5) -> dict[str, Any]:
        result = self.get(SIGNAL_DETAIL_ENDPOINT, {"securityCode": security_code})
        data = result.data if isinstance(result.data, dict) else {}
        score_details = (
            data.get("scoreDetails")
            if isinstance(data.get("scoreDetails"), list)
            else []
        )
        score_trend = (
            data.get("scoreTrend")
            if isinstance(data.get("scoreTrend"), list)
            else []
        )
        return {
            "kind": "signal_detail",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": WIND_SOURCE_LIMITS,
            "security_code": security_code,
            "score_area": normalize_signal_score_area(data.get("scoreArea")),
            "score_details": [
                normalize_signal_score_detail(row)
                for row in score_details[:limit]
                if isinstance(row, dict)
            ],
            "score_trend": [
                compact_dict(row, ["scoreDate", "score"])
                for row in score_trend[-limit:]
                if isinstance(row, dict)
            ],
            "strategic_performance": normalize_strategic_performance(
                data.get("strategicPerformance")
            ),
            "related_fund": normalize_signal_related_fund(data.get("relatedFund")),
            "related_product": normalize_signal_related_product(data.get("relateProduct")),
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
        interval_change = self.get(
            COMPARE_INTERVAL_CHANGE_ENDPOINT,
            {"indexCodes": index_codes},
        )
        funds = self.get(COMPARE_FUND_LIST_ENDPOINT, {"indexCodes": index_codes})
        special_market = self.get(COMPARE_SPECIAL_MARKET_ENDPOINT, {"indexCodes": index_codes})
        data_time = self.get(
            VALUATION_ROE_TIME_ENDPOINT,
            {"securityCodes": index_codes, "valuationType": "PE"},
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
                "interval_change": interval_change.url,
                "funds": funds.url,
                "special_market": special_market.url,
                "data_time": data_time.url,
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
            "interval_change": summarize_compare_interval_change(interval_change.data, limit),
            "funds": extract_compare_fund_rows(funds.data, limit),
            "market_context": summarize_compare_market_context(special_market.data, limit),
            "data_time": summarize_valuation_roe_time(data_time.data),
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

    def must_read(self, security_code: str, *, limit: int = 10) -> dict[str, Any]:
        payload = {
            "securityCode": security_code,
            "pageNo": 1,
            "pageSize": limit,
            "isAll": "0",
            "flag": True,
        }
        result = self.post(MUST_READ_ENDPOINT, None, payload)
        data = result.data if isinstance(result.data, dict) else {}
        status_list = (
            data.get("statusList")
            if isinstance(data.get("statusList"), dict)
            else {}
        )
        rows = status_list.get("data") if isinstance(status_list.get("data"), list) else []
        return {
            "kind": "must_read",
            "fetched_at": now_iso(),
            "source": result.url,
            "source_limits": DISCOVERY_SOURCE_LIMITS,
            "security_code": security_code,
            "big_event": normalize_status_metadata(data.get("bigEvent")),
            "rows": [
                normalize_status_metadata(row)
                for row in rows[:limit]
                if isinstance(row, dict)
            ],
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


def count_search_groups(data: Any) -> dict[str, int]:
    if not isinstance(data, dict):
        return {key: 0 for key in SEARCH_GROUP_KEYS}
    return {
        key: len(data.get(key))
        if isinstance(data.get(key), list)
        else 0
        for key in SEARCH_GROUP_KEYS
    }


def extract_search_candidates(data: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(data, dict) or limit <= 0:
        return []
    candidates: list[dict[str, Any]] = []
    for key in SEARCH_GROUP_KEYS:
        rows = data.get(key)
        if not isinstance(rows, list):
            continue
        candidates.extend(row for row in rows if isinstance(row, dict))
        if len(candidates) >= limit:
            return candidates[:limit]
    return candidates[:limit]


def extract_batch_quote_map(data: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(data, dict):
        return {}
    quote_by_code: dict[str, dict[str, Any]] = {}
    for key in SEARCH_BATCH_LIST_KEYS:
        rows = data.get(key)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            code = row.get("securityCode") or row.get("fundCode")
            if code not in (None, ""):
                quote_by_code[str(code)] = row
    return quote_by_code


def search_candidate_code(row: dict[str, Any]) -> str | None:
    code = row.get("securityCode") or row.get("fundCode")
    return str(code) if code not in (None, "") else None


def normalize_search_result(
    candidate: dict[str, Any],
    quote: dict[str, Any],
) -> dict[str, Any]:
    merged = {**quote, **candidate}
    return compact_dict(
        merged,
        [
            "securityCode",
            "securityType",
            "securityName",
            "securityFullName",
            "fundCode",
            "fundName",
            "fundCompany",
            "classA",
            "classB",
            "fundInvestType",
            "price",
            "lastPrice",
            "dayChangePercent",
            "yearChangePercent",
            "changePercent",
            "relatedFundScale",
            "trackingIndex",
            "trackingIndexName",
            "trackingIndexCode",
            "componentStockCount",
            "relatedFundCount",
            "marketValue",
            "industryInvolved",
            "netCapitalFlow",
            "etfFundCode",
            "etfFundName",
            "ofFundCode",
            "ofFundName",
        ],
    )


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


def normalize_snapshot(row: dict[str, Any], security_type: dict[str, Any]) -> dict[str, Any]:
    merged = {**security_type, **row}
    if not merged.get("securityExchmarket"):
        merged["securityExchmarket"] = infer_exchange_market(merged.get("securityCode"))
    return compact_dict(
        merged,
        [
            "securityCode",
            "securityName",
            "securityAbbreviation",
            "securityType",
            "deListStatus",
            "status",
            "dynamicEffectLimit",
            "securityExchmarket",
            "isDelay",
            "price",
            "lastPrice",
            "changePercent",
            "change",
            "tradeDate",
            "quoteInit",
            "follow",
            "marketTip",
            "marketType",
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


def summarize_security_info(data: Any) -> dict[str, Any]:
    return (
        compact_dict(
            data,
            [
                "securityCode",
                "securityName",
                "securityType",
                "securityCount",
                "listingTimeFlag",
                "price",
                "lastPrice",
                "change",
                "changePercent",
                "yearlyPerformance",
                "tradeDate",
                "marketTip",
                "marketType",
                "marketValue",
            ],
        )
        if isinstance(data, dict)
        else {}
    )


def extract_security_change_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    return [
        compact_dict(
            row,
            [
                "tradeDate",
                "date",
                "price",
                "lastPrice",
                "change",
                "changePercent",
                "pe",
                "pb",
                "roe",
                "amount",
                "volume",
            ],
        )
        for row in extract_security_runtime_rows(data, limit)
    ]


def extract_security_minute_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    rows = extract_security_runtime_rows(data)
    normalized = [
        compact_dict(
            row,
            [
                "tradeDate",
                "datetime",
                "minute",
                "minuteByHours",
                "time",
                "price",
                "lastPrice",
                "avgPrice",
                "change",
                "changePercent",
                "intervalChangePercent",
                "amount",
                "volume",
            ],
        )
        for row in rows
    ]
    return normalized[-limit:] if limit > 0 else []


def extract_security_structure_rows(
    data: Any,
    limit: int,
    *,
    latest: bool = False,
) -> list[dict[str, Any]]:
    rows = extract_security_runtime_rows(data)
    selected = rows[-limit:] if latest and limit > 0 else rows[:limit]
    return [normalize_security_structure_row(row) for row in selected]


def extract_security_runtime_rows(data: Any, limit: int | None = None) -> list[dict[str, Any]]:
    rows: list[Any]
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        security = data.get("security") if isinstance(data.get("security"), dict) else {}
        latest = data.get("latest") if isinstance(data.get("latest"), dict) else {}
        if isinstance(security.get("items"), list):
            rows = security["items"]
        elif isinstance(latest.get("indexComponentPOs"), list):
            rows = latest["indexComponentPOs"]
        elif isinstance(data.get("items"), list):
            rows = data["items"]
        elif isinstance(data.get("data"), list):
            rows = data["data"]
        elif isinstance(data.get("list"), list):
            rows = data["list"]
        elif isinstance(data.get("records"), list):
            rows = data["records"]
        else:
            rows = [data]
    else:
        rows = []
    normalized = [row for row in rows if isinstance(row, dict)]
    return normalized[:limit] if limit is not None and limit > 0 else normalized


def normalize_security_structure_row(row: dict[str, Any]) -> dict[str, Any]:
    expanded = {
        **row,
        "securityName": row.get("securityName") or row.get("securityAbbreviation"),
    }
    return compact_dict(
        expanded,
        [
            "tradeDate",
            "date",
            "annDate",
            "name",
            "label",
            "marketValueName",
            "industryName",
            "indexCode",
            "securityCode",
            "securityName",
            "weight",
            "weightChangeFlag",
            "proportion",
            "ratio",
            "value",
            "marketValue",
            "count",
            "cr5",
            "cr10",
            "cr20",
            "largeCapStockCount",
            "middleCapStockCount",
            "smallCapStockCount",
            "totalMarketValue",
            "avgMarketValue",
            "currencyCode",
            "constituentType",
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


def summarize_five_mfd_inflow(data: Any) -> dict[str, Any]:
    rows = [row for row in data if isinstance(row, dict)] if isinstance(data, list) else []
    if not rows:
        return {}
    values = [row.get("SMfdInflow") for row in rows]
    numeric_values = [value for value in values if isinstance(value, (int, float))]
    return compact_dict(
        {
            "days": len(rows),
            "latestTradeDate": rows[0].get("tradeDt"),
            "totalSMfdInflow": sum(numeric_values) if numeric_values else None,
        },
        ["days", "latestTradeDate", "totalSMfdInflow"],
    )


def extract_five_mfd_inflow_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    rows = [row for row in data if isinstance(row, dict)] if isinstance(data, list) else []
    return [
        compact_dict(row, ["tradeDt", "SMfdInflow"])
        for row in rows[:limit]
    ]


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


def extract_industries(data: Any, limit: int) -> list[dict[str, Any]]:
    rows = [row for row in data if isinstance(row, dict)] if isinstance(data, list) else []
    return [
        compact_dict(row, ["code", "value", "industryImage", "industryUrl", "hasShowDistribution"])
        for row in rows[:limit]
    ]


def normalize_industry_quote(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    return compact_dict(
        data,
        [
            "securityCode",
            "securityName",
            "price",
            "change",
            "changePercent",
            "up",
            "down",
            "equality",
            "marketTip",
            "marketType",
            "marketValue",
            "volume",
            "netCapitalFlow",
        ],
    )


def extract_industry_index_codes(data: Any, limit: int) -> list[dict[str, Any]]:
    rows = [row for row in data if isinstance(row, dict)] if isinstance(data, list) else []
    return [
        compact_dict(
            {
                **row,
                "securityDesc": clean_text(row.get("securityDesc"), limit=180),
            },
            ["securityCode", "securityName", "percentChange", "securityDesc", "initQuote"],
        )
        for row in rows[:limit]
    ]


def extract_industry_classify(data: Any, limit: int) -> list[dict[str, Any]]:
    rows = [row for row in data if isinstance(row, dict)] if isinstance(data, list) else []
    result: list[dict[str, Any]] = []
    for row in rows[:limit]:
        indicators = (
            row.get("dataIndicatorList")
            if isinstance(row.get("dataIndicatorList"), list)
            else []
        )
        result.append(
            compact_dict(
                {
                    "industryClassifyName": row.get("industryClassifyName"),
                    "indicators": [
                        normalize_industry_indicator(item)
                        for item in indicators[:limit]
                        if isinstance(item, dict)
                    ],
                },
                ["industryClassifyName", "indicators"],
            )
        )
    return result


def normalize_industry_indicator(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        {
            "indicatorId": row.get("indicatorId"),
            "indicatorName": row.get("indicatorName"),
            "title": row.get("title"),
            "content": clean_text(row.get("content"), limit=180),
        },
        ["indicatorId", "indicatorName", "title", "content"],
    )


def summarize_industry_indicator_detail(data: Any, limit: int) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    rows = (
        data.get("indicatorDataDetailVoList")
        if isinstance(data.get("indicatorDataDetailVoList"), list)
        else []
    )
    return compact_dict(
        {
            "indicatorId": data.get("indicatorId"),
            "indicatorName": data.get("indicatorName"),
            "title": data.get("title"),
            "content": clean_text(data.get("content"), limit=240),
            "rows": [
                normalize_industry_indicator_data(row)
                for row in rows[:limit]
                if isinstance(row, dict)
            ],
        },
        ["indicatorId", "indicatorName", "title", "content", "rows"],
    )


def summarize_industry_related(data: Any, limit: int) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    rows = data.get("indicatorData") if isinstance(data.get("indicatorData"), list) else []
    return compact_dict(
        {
            "indicatorTotal": data.get("indicatorTotal"),
            "rows": [
                normalize_industry_indicator_data(row)
                for row in rows[:limit]
                if isinstance(row, dict)
            ],
        },
        ["indicatorTotal", "rows"],
    )


def normalize_industry_indicator_data(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        row,
        [
            "indicatorDataId",
            "indicatorDataName",
            "indicatorLegend",
            "dataItem",
            "dataUnit",
            "indicatorTm",
            "indicatorValue",
            "yoy",
        ],
    )


def summarize_industry_chart(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    performance = data.get("performance") if isinstance(data.get("performance"), dict) else None
    return compact_dict(
        {
            "securityCode": data.get("securityCode"),
            "securityName": data.get("securityName"),
            "chartDimension": data.get("chartDimension"),
            "itemsSize": data.get("itemsSize"),
            "dimensionChange": data.get("dimensionChange"),
            "performance": compact_dict(
                performance,
                [
                    "weeklyPerformance",
                    "monthlyPerformance",
                    "quarterlyPerformance",
                    "halfYearPerformance",
                    "yearlyPerformance",
                    "threeYearPerformance",
                ],
            )
            if performance
            else None,
        },
        [
            "securityCode",
            "securityName",
            "chartDimension",
            "itemsSize",
            "dimensionChange",
            "performance",
        ],
    )


def extract_industry_chart_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    rows = data.get("items") if isinstance(data.get("items"), list) else []
    normalized = [
        compact_dict(
            row,
            ["tradeDate", "date", "intervalChangePercent", "price", "changePercent"],
        )
        for row in rows
        if isinstance(row, dict)
    ]
    return normalized[-limit:] if limit > 0 else []


def extract_industry_memoirs(data: Any, limit: int) -> list[dict[str, Any]]:
    rows = [row for row in data if isinstance(row, dict)] if isinstance(data, list) else []
    return [
        compact_dict(
            {
                **row,
                "memoirContent": clean_text(row.get("memoirContent"), limit=180),
            },
            [
                "memoirTime",
                "memoirFlag",
                "memoirTitle",
                "memoirRating",
                "memoirContent",
                "memoirPercentChange",
                "price",
                "memoirMarketValue",
                "tradeDate",
            ],
        )
        for row in rows[:limit]
    ]


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


def extract_hot_timeline_rows(buckets: list[Any], limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if limit <= 0:
        return rows
    for bucket in buckets:
        if not isinstance(bucket, dict):
            continue
        events = (
            bucket.get("changeList")
            if isinstance(bucket.get("changeList"), list)
            else []
        )
        for event in events:
            if not isinstance(event, dict):
                continue
            rows.append(normalize_hot_timeline_event(bucket, event))
            if len(rows) >= limit:
                return rows
    return rows


def normalize_hot_timeline_event(
    bucket: dict[str, Any],
    event: dict[str, Any],
) -> dict[str, Any]:
    related_indexes = (
        event.get("correlationIndexList")
        if isinstance(event.get("correlationIndexList"), list)
        else []
    )
    related_etfs = (
        event.get("correlationEtfList")
        if isinstance(event.get("correlationEtfList"), list)
        else []
    )
    return compact_dict(
        {
            "id": event.get("id"),
            "timeInterval": bucket.get("timeInterval"),
            "changeType": bucket.get("changeType"),
            "foldSize": bucket.get("foldSize"),
            "changeTime": event.get("changeTime"),
            "content": clean_text(event.get("content"), limit=220),
            "changePercent": event.get("changePercent"),
            "contentId": event.get("contentId"),
            "relatedIndexes": [
                normalize_hot_related_security(row)
                for row in related_indexes[:3]
                if isinstance(row, dict)
            ],
            "relatedEtfs": [
                normalize_hot_related_security(row)
                for row in related_etfs[:3]
                if isinstance(row, dict)
            ],
        },
        [
            "id",
            "timeInterval",
            "changeType",
            "foldSize",
            "changeTime",
            "content",
            "changePercent",
            "contentId",
            "relatedIndexes",
            "relatedEtfs",
        ],
    )


def normalize_hot_related_security(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        {
            "indexCode": row.get("indexCode") or row.get("securityCode"),
            "indexName": row.get("indexName") or row.get("securityName"),
            "changePercent": row.get("changePercent"),
            "tradingStatus": row.get("tradingStatus"),
        },
        ["indexCode", "indexName", "changePercent", "tradingStatus"],
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
        {
            **row,
            "statusId": extract_status_id(row.get("skipAddr")) or row.get("statusId"),
        },
        [
            "id",
            "statusId",
            "title",
            "subtitle",
            "bubble",
            "skipAddr",
            "startTime",
            "securityCode",
            "securityName",
            "performanceRangeName",
            "performanceChangePercent",
            "valuation",
            "belongToDate",
        ],
    )


def extract_status_id(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    status_ids = query.get("statusId")
    return status_ids[0] if status_ids else None


def normalize_class_info(row: dict[str, Any]) -> dict[str, Any]:
    children = row.get("children") if isinstance(row.get("children"), list) else []
    normalized = compact_dict(
        {
            "value": row.get("value"),
            "label": row.get("lable") or row.get("label"),
            "count": row.get("count") or row.get("allCount"),
            "filterType": row.get("filterType"),
        },
        ["value", "label", "count", "filterType"],
    )
    if children:
        normalized["children"] = [
            normalize_class_info(child)
            for child in children
            if isinstance(child, dict)
        ]
    return normalized


def parse_draw_points(draw: Any, columns: str) -> list[dict[str, str]]:
    if not isinstance(draw, str) or not columns:
        return []
    keys = [key.strip() for key in columns.split(",") if key.strip()]
    points: list[dict[str, str]] = []
    for item in draw.split(";"):
        if not item:
            continue
        values = item.split(",")
        row = {
            key: values[index]
            for index, key in enumerate(keys)
            if index < len(values) and values[index] not in ("", None)
        }
        if row:
            points.append(row)
    return points


def normalize_focus_news(row: dict[str, Any]) -> dict[str, Any]:
    related = (
        row.get("securityQuoteSimpleVoList")
        if isinstance(row.get("securityQuoteSimpleVoList"), list)
        else []
    )
    return compact_dict(
        {
            "id": row.get("id"),
            "time": row.get("m"),
            "theme": clean_text(row.get("n"), limit=80),
            "summary": clean_text(row.get("mc"), limit=160),
            "reason": clean_text(row.get("rc"), limit=160),
            "status": row.get("status"),
            "related": [
                compact_dict(item, ["securityCode", "securityName", "changePercent"])
                for item in related
                if isinstance(item, dict)
            ],
        },
        ["id", "time", "theme", "summary", "reason", "status", "related"],
    )


def clean_text(value: Any, *, limit: int = 160) -> str | None:
    if value in (None, ""):
        return None
    text = re.sub(
        r"</?(?:p|div|section|article|ul|ol|li|br|h[1-6]|tr|td|th)\b[^>]*>",
        " ",
        str(value),
        flags=re.IGNORECASE,
    )
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", unescape(text)).strip()
    if limit > 0 and len(text) > limit:
        return f"{text[:limit].rstrip()}..."
    return text


def clamp_article_content_limit(content_limit: int) -> int:
    return max(1, min(content_limit, ARTICLE_CONTENT_EXCERPT_MAX))


def normalize_status_metadata(row: Any) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    securities = row.get("securityInfoVos") or row.get("securityDto") or []
    if isinstance(securities, dict):
        securities = [securities]
    if not isinstance(securities, list):
        securities = []
    related = [
        compact_dict(item, ["securityCode", "securityName", "changePercent"])
        for item in securities
        if isinstance(item, dict)
    ]
    value = compact_dict(
        {
            "statusId": row.get("statusId") or row.get("id"),
            "title": row.get("title"),
            "contentLabel": row.get("contentLabel") or row.get("contentLable"),
            "nickName": row.get("nickName") or (row.get("user") or {}).get("nickName")
            if isinstance(row.get("user"), dict)
            else row.get("nickName"),
            "publishTime": row.get("publishTime"),
            "securityInfoVos": related,
        },
        [
            "statusId",
            "title",
            "contentLabel",
            "nickName",
            "publishTime",
            "securityInfoVos",
        ],
    )
    if not related:
        value.pop("securityInfoVos", None)
    return value


def normalize_article_detail(row: Any, *, content_limit: int) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    content_limit = clamp_article_content_limit(content_limit)
    return compact_dict(
        {
            **normalize_status_metadata(row),
            "articleId": row.get("articleId"),
            "content": clean_text(row.get("content"), limit=content_limit),
        },
        [
            "articleId",
            "statusId",
            "title",
            "content",
            "contentLabel",
            "nickName",
            "publishTime",
            "securityInfoVos",
        ],
    )


def normalize_knowledge(row: dict[str, Any], *, content_limit: int) -> dict[str, Any]:
    return compact_dict(
        {
            "id": row.get("id"),
            "knowledgeKey": row.get("knowledgeKey"),
            "title": row.get("knowledgeTitle"),
            "content": clean_text(row.get("knowledgeContent"), limit=content_limit),
        },
        ["id", "knowledgeKey", "title", "content"],
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


def normalize_signal_score_area(row: Any) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    return compact_dict(
        row,
        [
            "securityCode",
            "securityName",
            "score",
            "scoreLabel",
            "hisScoreType",
            "scoreType",
            "scoreDate",
            "tips",
            "pointer",
            "hisDesc",
            "shortHisDesc",
            "changePercent",
        ],
    )


def normalize_signal_score_detail(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        {
            "title": row.get("title"),
            "score": row.get("score"),
            "avg": row.get("avg"),
            "pointerType": row.get("pointerType"),
            "scoreDesc": clean_text(row.get("scoreDesc"), limit=160),
            "desc": clean_text(row.get("desc"), limit=160),
        },
        ["title", "score", "avg", "pointerType", "scoreDesc", "desc"],
    )


def normalize_strategic_performance(row: Any) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    return compact_dict(row, ["modelUpDownRate", "upDownRate", "winRate", "maxDrawdown"])


def normalize_signal_related_fund(row: Any) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    return compact_dict(row, ["etf", "otc"])


def normalize_signal_related_product(row: Any) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    return compact_dict(
        row,
        [
            "productCode",
            "productName",
            "securityType",
            "revenueRange",
            "performance",
            "richChannel",
            "financialLinkChannel",
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


def summarize_compare_interval_change(data: Any, limit: int) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    performances = (
        data.get("performances")
        if isinstance(data.get("performances"), list)
        else []
    )
    return compact_dict(
        {
            "max": data.get("max") if isinstance(data.get("max"), dict) else None,
            "performances": [
                normalize_compare_performance(row)
                for row in performances[:limit]
                if isinstance(row, dict)
            ],
        },
        ["max", "performances"],
    )


def summarize_compare_market_context(data: Any, limit: int) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    market_info = data.get("marketInfo") if isinstance(data.get("marketInfo"), list) else []
    performance = (
        data.get("indexPerformanceVo")
        if isinstance(data.get("indexPerformanceVo"), list)
        else []
    )
    return compact_dict(
        {
            "marketInfo": [
                normalize_compare_market_info(row)
                for row in market_info[:limit]
                if isinstance(row, dict)
            ],
            "indexPerformance": [
                normalize_compare_index_performance(row)
                for row in performance[:limit]
                if isinstance(row, dict)
            ],
        },
        ["marketInfo", "indexPerformance"],
    )


def normalize_compare_market_info(row: dict[str, Any]) -> dict[str, Any]:
    percent_list = (
        row.get("percentList") if isinstance(row.get("percentList"), list) else []
    )
    return compact_dict(
        {
            "marketName": row.get("marketName"),
            "startTime": row.get("startTime"),
            "endTime": row.get("endTime"),
            "marketSummary": clean_text(row.get("marketSummary"), limit=160),
            "percentList": [
                compact_dict(item, ["securityCode", "securityName", "changePercent"])
                for item in percent_list
                if isinstance(item, dict)
            ],
        },
        ["marketName", "startTime", "endTime", "marketSummary", "percentList"],
    )


def normalize_compare_index_performance(row: dict[str, Any]) -> dict[str, Any]:
    items = row.get("items") if isinstance(row.get("items"), list) else []
    return compact_dict(
        {
            "securityCode": row.get("securityCode"),
            "securityName": row.get("securityName"),
            "itemSize": row.get("itemSize"),
            "latest": compact_dict(
                items[-1],
                ["tradeDate", "intervalChangePercent"],
            )
            if items and isinstance(items[-1], dict)
            else None,
        },
        ["securityCode", "securityName", "itemSize", "latest"],
    )


def normalize_compare_performance(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        row,
        [
            "securityCode",
            "securityName",
            "changePercent",
            "weeklyPerformance",
            "monthlyPerformance",
            "quarterlyPerformance",
            "halfYearPerformance",
            "yearlyPerformance",
            "threeYearPerformance",
        ],
    )


def extract_compare_fund_rows(data: Any, limit: int) -> list[dict[str, Any]]:
    return [
        normalize_compare_fund_row(row, limit)
        for row in extract_rows(data)[:limit]
    ]


def normalize_compare_fund_row(row: dict[str, Any], limit: int) -> dict[str, Any]:
    etf_funds = row.get("etfFundList") if isinstance(row.get("etfFundList"), list) else []
    otc_funds = row.get("otcFundList") if isinstance(row.get("otcFundList"), list) else []
    return compact_dict(
        {
            **row,
            "etfFunds": [
                normalize_compare_fund_item(item)
                for item in etf_funds[:limit]
                if isinstance(item, dict)
            ],
            "otcFunds": [
                normalize_compare_fund_item(item)
                for item in otc_funds[:limit]
                if isinstance(item, dict)
            ],
        },
        [
            "indexCode",
            "indexName",
            "etfCount",
            "otcCount",
            "etfScale",
            "otcScale",
            "etfFunds",
            "otcFunds",
        ],
    )


def normalize_compare_fund_item(row: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        row,
        [
            "fundCode",
            "fundName",
            "changePercentY1",
            "establishedY1",
            "richChannel",
            "financialLinkChannel",
        ],
    )


def summarize_valuation_roe_time(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    return compact_dict(data, ["valuationTime", "roeTime", "knowledgeTitle"])


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
