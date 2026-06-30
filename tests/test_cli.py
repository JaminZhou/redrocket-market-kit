from pathlib import Path

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
