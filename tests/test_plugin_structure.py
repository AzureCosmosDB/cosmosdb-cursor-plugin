"""Tests that verify the overall plugin directory structure."""

import pathlib

from .conftest import EXPECTED_RULE_CATEGORIES, OVERVIEW_RULE_NAME


class TestRequiredFiles:
    """All files that must exist for a valid Cursor plugin."""

    REQUIRED_FILES = [
        ".cursor-plugin/plugin.json",
        ".mcp.json",
        "rules/cosmosdb-overview.mdc",
        "assets/logo.svg",
        "README.md",
        "LICENSE",
    ]

    def test_required_files_exist(self, project_root: pathlib.Path):
        for rel_path in self.REQUIRED_FILES:
            full = project_root / rel_path
            assert full.exists(), f"Required file missing: {rel_path}"

    def test_required_files_are_not_empty(self, project_root: pathlib.Path):
        for rel_path in self.REQUIRED_FILES:
            full = project_root / rel_path
            assert full.stat().st_size > 0, f"Required file is empty: {rel_path}"


class TestRequiredDirectories:
    """Directories that must exist for the plugin layout."""

    REQUIRED_DIRS = [
        ".cursor-plugin",
        ".cursor/prompts",
        "assets",
        "rules",
    ]

    def test_required_directories_exist(self, project_root: pathlib.Path):
        for rel_path in self.REQUIRED_DIRS:
            full = project_root / rel_path
            assert full.is_dir(), f"Required directory missing: {rel_path}"


class TestRuleFiles:
    """Each rule category must have a .mdc file in rules/."""

    def test_each_category_has_mdc_file(
        self, rules_dir: pathlib.Path, rule_categories: list[str]
    ):
        for category in rule_categories:
            rule_file = rules_dir / f"{category}.mdc"
            assert rule_file.is_file(), f"Rule file missing: rules/{category}.mdc"

    def test_overview_rule_exists(
        self, rules_dir: pathlib.Path
    ):
        overview = rules_dir / f"{OVERVIEW_RULE_NAME}.mdc"
        assert overview.is_file(), f"Overview rule missing: rules/{OVERVIEW_RULE_NAME}.mdc"

    def test_no_unexpected_rule_files(
        self, rules_dir: pathlib.Path, rule_categories: list[str]
    ):
        """No extra rule files should exist beyond the expected ones."""
        expected = sorted([f"{c}.mdc" for c in rule_categories] + [f"{OVERVIEW_RULE_NAME}.mdc"])
        actual = sorted(f.name for f in rules_dir.iterdir() if f.is_file())
        assert actual == expected, (
            f"Unexpected rule files: {set(actual) - set(expected)}"
        )

    def test_no_subdirectories_in_rules(
        self, rules_dir: pathlib.Path
    ):
        """Rules should be flat .mdc files, not subdirectories."""
        subdirs = [d.name for d in rules_dir.iterdir() if d.is_dir()]
        assert subdirs == [], (
            f"Unexpected subdirectories in rules/: {subdirs}"
        )


class TestGeneratePrompt:
    """The saved Cursor prompt for regeneration must exist."""

    def test_generate_rules_prompt_exists(self, project_root: pathlib.Path):
        prompt = project_root / ".cursor" / "prompts" / "generate-rules.md"
        assert prompt.is_file(), "generate-rules.md prompt is missing"

    def test_generate_rules_prompt_not_empty(self, project_root: pathlib.Path):
        prompt = project_root / ".cursor" / "prompts" / "generate-rules.md"
        assert prompt.stat().st_size > 0, "generate-rules.md prompt is empty"
