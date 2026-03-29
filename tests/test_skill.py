# Internal imports
from jira_genie.skill import detect_targets, install, resolve_paths, uninstall


class TestInstall:
    def test_creates_skill_dir_and_copies_file(self, tmp_path):
        result = install(tmp_path)
        dest = tmp_path / "jira-genie" / "SKILL.md"
        assert dest.exists()
        assert result["action"] == "create"
        assert result["path"] == str(dest)
        assert "name: jira-genie" in dest.read_text()

    def test_overwrite_existing(self, tmp_path):
        install(tmp_path)
        result = install(tmp_path)
        assert result["action"] == "overwrite"

    def test_custom_source(self, tmp_path):
        source = tmp_path / "custom" / "SKILL.md"
        source.parent.mkdir()
        source.write_text("custom content")
        dest_dir = tmp_path / "dest"
        install(dest_dir, source=source)
        assert (dest_dir / "jira-genie" / "SKILL.md").read_text() == "custom content"


class TestDetectTargets:
    def test_detects_existing_dirs(self, tmp_path, monkeypatch):
        (tmp_path / ".pi").mkdir()
        (tmp_path / ".claude").mkdir()
        p = tmp_path
        monkeypatch.setattr("jira_genie.skill.TARGETS", {
            "pi": {"label": "Pi", "detect": str(p / ".pi"), "path": str(p / ".pi/skills")},
            "claude": {"label": "Claude", "detect": str(p / ".claude"), "path": str(p / ".claude/skills")},
            "codex": {"label": "Codex", "detect": str(p / ".codex"), "path": str(p / ".codex/skills")},
        })
        result = detect_targets()
        assert "pi" in result
        assert "claude" in result
        assert "codex" not in result

    def test_returns_empty_when_no_dirs(self, tmp_path, monkeypatch):
        monkeypatch.setattr("jira_genie.skill.TARGETS", {
            "pi": {"label": "Pi", "detect": str(tmp_path / ".pi"), "path": ""},
        })
        assert detect_targets() == []


class TestResolvePaths:
    def test_resolves_targets_to_paths(self, tmp_path, monkeypatch):
        monkeypatch.setattr("jira_genie.skill.TARGETS", {
            "pi": {"label": "Pi", "detect": "", "path": str(tmp_path / "pi-skills")},
        })
        result = resolve_paths(targets=["pi"])
        assert result == [tmp_path / "pi-skills"]

    def test_passes_explicit_paths_through(self, tmp_path):
        result = resolve_paths(paths=[str(tmp_path / "custom")])
        assert result == [tmp_path / "custom"]

    def test_combines_targets_and_paths(self, tmp_path, monkeypatch):
        monkeypatch.setattr("jira_genie.skill.TARGETS", {
            "pi": {"label": "Pi", "detect": "", "path": str(tmp_path / "pi")},
        })
        result = resolve_paths(targets=["pi"], paths=[str(tmp_path / "custom")])
        assert len(result) == 2

    def test_empty_returns_empty(self):
        assert resolve_paths() == []


class TestUninstall:
    def test_removes_skill_dir(self, tmp_path):
        install(tmp_path)
        result = uninstall(tmp_path)
        assert result["action"] == "remove"
        assert not (tmp_path / "jira-genie").exists()

    def test_returns_none_when_not_installed(self, tmp_path):
        assert uninstall(tmp_path) is None
