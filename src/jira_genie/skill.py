"""Install/uninstall the jira-genie agent skill."""

from pathlib import Path
import shutil

SKILL_DIR = "jira-genie"

TARGETS = {
    "agents": {"label": "Agent Skills standard", "detect": "~/.agents", "path": "~/.agents/skills"},
    "pi": {"label": "Pi", "detect": "~/.pi", "path": "~/.pi/agent/skills"},
    "claude": {"label": "Claude Code", "detect": "~/.claude", "path": "~/.claude/skills"},
    "codex": {"label": "Codex", "detect": "~/.codex", "path": "~/.codex/skills"},
}


def bundled_skill() -> Path:
    """Return path to the bundled SKILL.md."""
    return Path(__file__).parent / "skills" / SKILL_DIR / "SKILL.md"


def detect_targets() -> list[str]:
    """Return target names whose config directories exist."""
    return [name for name, info in TARGETS.items() if Path(info["detect"]).expanduser().is_dir()]


def resolve_paths(targets=None, paths=None) -> list[Path]:
    """Resolve --target names and explicit paths into a list of skill parent dirs."""
    result = []
    for name in (targets or []):
        result.append(Path(TARGETS[name]["path"]).expanduser())
    for p in (paths or []):
        result.append(Path(p).expanduser())
    return result


def install(dest_dir, source=None) -> dict:
    """Install SKILL.md into dest_dir/jira-genie/. Returns action dict."""
    source = source or bundled_skill()
    if not source.exists():
        raise FileNotFoundError(f"Bundled skill not found: {source}")

    skill_dir = Path(dest_dir) / SKILL_DIR
    dest_file = skill_dir / "SKILL.md"
    exists = dest_file.exists()

    skill_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest_file)

    return {"path": str(dest_file), "action": "overwrite" if exists else "create"}


def uninstall(dest_dir) -> dict | None:
    """Remove jira-genie/ from dest_dir. Returns action dict or None."""
    skill_dir = Path(dest_dir) / SKILL_DIR
    if not skill_dir.exists():
        return None
    shutil.rmtree(skill_dir)
    return {"path": str(skill_dir), "action": "remove"}
