from pathlib import Path

from redrocket_market.installer import (
    SKILL_NAME,
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


def test_resolve_client_destinations_supports_codex_and_agents(tmp_path: Path) -> None:
    home = tmp_path

    assert resolve_client_destinations("codex", home=home) == [home / ".agents" / "skills"]
    assert resolve_client_destinations("agents", home=home) == [home / ".agents" / "skills"]
