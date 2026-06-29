from redrocket_market.client import extract_rows, normalize_fund_code, normalize_security


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

