# Internal imports
from jira_genie.skill import install, uninstall


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


class TestUninstall:
    def test_removes_skill_dir(self, tmp_path):
        install(tmp_path)
        result = uninstall(tmp_path)
        assert result["action"] == "remove"
        assert not (tmp_path / "jira-genie").exists()

    def test_returns_none_when_not_installed(self, tmp_path):
        assert uninstall(tmp_path) is None
