from pathlib import Path
from typing import Any

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

        def news(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(("news", kwargs))
            return {"kind": "news", "fetched_at": "now", "source": "url", "rows": []}

        def wind(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(("wind", kwargs))
            return {"kind": "wind", "fetched_at": "now", "source": "url", "rows": []}

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

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["index", "000300.SH", "--limit", "2"]) == 0
    assert main(["etf-detail", "510300.SH", "--limit", "3"]) == 0
    assert main(["heat", "--limit", "3"]) == 0
    assert main(["news", "--page", "2", "--limit", "4"]) == 0
    assert main(["wind", "--limit", "5"]) == 0
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
            "index-compare",
            "000300.SH:沪深300",
            "000905.SH:中证500",
            "--limit",
            "4",
        ]
    ) == 0

    capsys.readouterr()
    assert calls == [
        ("init", {"timeout": 10.0}),
        ("index", {"security_code": "000300.SH", "limit": 2}),
        ("init", {"timeout": 10.0}),
        ("etf_detail", {"security_code": "510300.SH", "limit": 3}),
        ("init", {"timeout": 10.0}),
        (
            "heat",
            {"order_by": "changePercent", "order": "desc", "class_a": "", "limit": 3},
        ),
        ("init", {"timeout": 10.0}),
        ("news", {"page": 2, "limit": 4}),
        ("init", {"timeout": 10.0}),
        ("wind", {"limit": 5}),
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
            "index_compare",
            {
                "index_infos": [("000300.SH", "沪深300"), ("000905.SH", "中证500")],
                "limit": 4,
            },
        ),
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
