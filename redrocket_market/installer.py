from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


SKILL_NAME = "redrocket-market"
ClientName = Literal["codex", "agents", "claude"]


@dataclass(frozen=True)
class InitResult:
    action: str
    paths: list[Path]

    def to_json(self) -> str:
        return json.dumps(
            {"action": self.action, "paths": [str(path) for path in self.paths]},
            ensure_ascii=False,
            separators=(",", ":"),
        )


def bundled_skill_dir() -> Path:
    package_resource = Path(__file__).parent / "resources" / "skills" / SKILL_NAME
    if (package_resource / "SKILL.md").exists():
        return package_resource

    repo_resource = Path(__file__).resolve().parents[1] / "skills" / SKILL_NAME
    if (repo_resource / "SKILL.md").exists():
        return repo_resource

    raise FileNotFoundError("Bundled redrocket-market skill was not found.")


def print_skill() -> str:
    return (bundled_skill_dir() / "SKILL.md").read_text(encoding="utf-8")


def resolve_client_destinations(
    client: ClientName,
    *,
    home: Path | None = None,
    env: dict[str, str] | None = None,
) -> list[Path]:
    root = home or Path.home()
    environ = env if env is not None else os.environ
    if client == "agents":
        return [root / ".agents" / "skills"]
    if client == "codex":
        return [codex_home(root=root, env=environ) / "skills"]
    if client == "claude":
        return [claude_home(root=root, env=environ) / "skills"]
    raise ValueError(f"Unsupported client: {client}")


def codex_home(*, root: Path, env: dict[str, str]) -> Path:
    value = env.get("CODEX_HOME", "").strip()
    return Path(value).expanduser() if value else root / ".codex"


def claude_home(*, root: Path, env: dict[str, str]) -> Path:
    value = env.get("CLAUDE_CONFIG_DIR", "").strip()
    return Path(value).expanduser() if value else root / ".claude"


def install_skill(destination: Path, *, force: bool = False) -> Path:
    source = bundled_skill_dir()
    target = destination / SKILL_NAME
    assert_not_bundled_skill_target(target)
    destination.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if not force:
            raise FileExistsError(
                f"Skill already installed at {target}. Re-run with --force to overwrite."
            )
        shutil.rmtree(target)
    shutil.copytree(source, target)
    return target


def uninstall_skill(destination: Path) -> Path:
    target = destination / SKILL_NAME
    assert_not_bundled_skill_target(target)
    if target.exists():
        shutil.rmtree(target)
    return target


def assert_not_bundled_skill_target(target: Path) -> None:
    source = bundled_skill_dir().resolve()
    if target.expanduser().resolve() == source:
        raise ValueError(
            f"Refusing to modify bundled {SKILL_NAME} skill at {source}. Choose a different --dest."
        )


def install_to_targets(destinations: list[Path], *, force: bool = False) -> InitResult:
    return InitResult(
        action="installed",
        paths=[install_skill(destination, force=force) for destination in destinations],
    )


def uninstall_from_targets(destinations: list[Path]) -> InitResult:
    return InitResult(
        action="uninstalled",
        paths=[uninstall_skill(destination) for destination in destinations],
    )
