from pathlib import Path

from redrocket_market.installer import (
    SKILL_NAME,
    bundled_skill_dir,
    install_skill,
    print_skill,
    resolve_client_destinations,
    uninstall_skill,
)


def test_print_skill_includes_redrocket_skill_frontmatter() -> None:
    content = print_skill()
    assert "name: redrocket-market" in content
    assert "Red Rocket" in content


def test_install_skill_copies_bundled_skill_to_destination(tmp_path: Path) -> None:
    installed = install_skill(tmp_path)

    target = tmp_path / SKILL_NAME
    assert installed == target
    assert (target / "SKILL.md").read_text(encoding="utf-8").startswith("---")
    assert (target / "references" / "source-limits.md").exists()


def test_install_skill_refuses_existing_without_force(tmp_path: Path) -> None:
    target = tmp_path / SKILL_NAME
    target.mkdir()
    (target / "SKILL.md").write_text("local edits", encoding="utf-8")

    try:
        install_skill(tmp_path)
    except FileExistsError as exc:
        assert str(target) in str(exc)
    else:
        raise AssertionError("install_skill should refuse existing installs without force")

    assert (target / "SKILL.md").read_text(encoding="utf-8") == "local edits"


def test_install_skill_force_replaces_existing_skill(tmp_path: Path) -> None:
    target = tmp_path / SKILL_NAME
    target.mkdir()
    (target / "SKILL.md").write_text("local edits", encoding="utf-8")

    install_skill(tmp_path, force=True)

    assert "name: redrocket-market" in (target / "SKILL.md").read_text(encoding="utf-8")


def test_uninstall_skill_removes_installed_skill(tmp_path: Path) -> None:
    target = install_skill(tmp_path)

    removed = uninstall_skill(tmp_path)

    assert removed == target
    assert not target.exists()


def test_install_skill_refuses_to_overwrite_bundled_skill() -> None:
    bundled = bundled_skill_dir()

    try:
        install_skill(bundled.parent, force=True)
    except ValueError as exc:
        assert str(bundled) in str(exc)
    else:
        raise AssertionError("install_skill should refuse to overwrite the bundled skill")

    assert (bundled / "SKILL.md").exists()


def test_uninstall_skill_refuses_to_remove_bundled_skill() -> None:
    bundled = bundled_skill_dir()

    try:
        uninstall_skill(bundled.parent)
    except ValueError as exc:
        assert str(bundled) in str(exc)
    else:
        raise AssertionError("uninstall_skill should refuse to remove the bundled skill")

    assert (bundled / "SKILL.md").exists()


def test_resolve_client_destinations_supports_codex_agents_and_claude(tmp_path: Path) -> None:
    home = tmp_path

    assert resolve_client_destinations("codex", home=home, env={}) == [home / ".codex" / "skills"]
    assert resolve_client_destinations("agents", home=home) == [home / ".agents" / "skills"]
    assert resolve_client_destinations("claude", home=home) == [home / ".claude" / "skills"]


def test_resolve_client_destinations_honors_codex_home(tmp_path: Path) -> None:
    codex_home = tmp_path / "custom-codex"

    assert resolve_client_destinations("codex", env={"CODEX_HOME": str(codex_home)}) == [
        codex_home / "skills"
    ]


def test_resolve_client_destinations_honors_claude_config_dir(tmp_path: Path) -> None:
    claude_home = tmp_path / "custom-claude"

    assert resolve_client_destinations("claude", env={"CLAUDE_CONFIG_DIR": str(claude_home)}) == [
        claude_home / "skills"
    ]
