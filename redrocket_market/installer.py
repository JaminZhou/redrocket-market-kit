from __future__ import annotations

import json
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


def resolve_client_destinations(client: ClientName, *, home: Path | None = None) -> list[Path]:
    root = home or Path.home()
    if client in ("codex", "agents"):
        return [root / ".agents" / "skills"]
    if client == "claude":
        return [root / ".claude" / "skills"]
    raise ValueError(f"Unsupported client: {client}")


def install_skill(destination: Path, *, force: bool = False) -> Path:
    source = bundled_skill_dir()
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / SKILL_NAME
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
    if target.exists():
        shutil.rmtree(target)
    return target


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

