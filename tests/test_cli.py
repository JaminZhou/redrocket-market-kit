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

    monkeypatch.setattr("redrocket_market.cli.RedRocketClient", FakeClient)

    assert main(["heat", "--limit", "3"]) == 0
    assert main(["news", "--page", "2", "--limit", "4"]) == 0
    assert main(["wind", "--limit", "5"]) == 0
    assert main(["compare", "--limit", "6"]) == 0

    capsys.readouterr()
    assert calls == [
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
    ]
