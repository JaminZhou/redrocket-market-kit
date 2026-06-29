from __future__ import annotations

from pathlib import Path

import yaml


skill = Path("skills/redrocket-market/SKILL.md")
text = skill.read_text(encoding="utf-8")

if not text.startswith("---\n"):
    raise SystemExit("SKILL.md missing YAML frontmatter")

frontmatter = text.split("---", 2)[1]
data = yaml.safe_load(frontmatter)
if data.get("name") != "redrocket-market":
    raise SystemExit("SKILL.md name must be redrocket-market")
if not data.get("description"):
    raise SystemExit("SKILL.md description is required")

agent = Path("skills/redrocket-market/agents/openai.yaml")
if not agent.exists():
    raise SystemExit("agents/openai.yaml is required")

