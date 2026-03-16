"""Tests for README.md completeness and correctness."""

import pathlib
import re

import pytest


@pytest.fixture()
def readme_text(project_root: pathlib.Path) -> str:
    return (project_root / "README.md").read_text(encoding="utf-8")


class TestReadmeSections:
    """README must contain key sections for a plugin README."""

    REQUIRED_HEADINGS = [
        "What's Included",
        "MCP Tools Available",
        "Prerequisites",
        "Setup",
        "Project Structure",
        "License",
    ]

    @pytest.mark.parametrize(
        "heading",
        REQUIRED_HEADINGS,
    )
    def test_has_required_section(self, readme_text: str, heading: str):
        pattern = re.compile(rf"^#{{1,3}}\s+{re.escape(heading)}", re.MULTILINE)
        assert pattern.search(readme_text), (
            f"README.md missing required section: {heading}"
        )

    def test_mentions_cosmos_db(self, readme_text: str):
        assert "cosmos db" in readme_text.lower()

    def test_mentions_cursor(self, readme_text: str):
        assert "cursor" in readme_text.lower()


class TestReadmeMcpToolsTable:
    """The MCP tools table should list the expected tools."""

    EXPECTED_TOOLS = [
        "list_databases",
        "list_collections",
        "get_approximate_schema",
        "get_recent_documents",
        "find_document_by_id",
        "text_search",
        "vector_search",
    ]

    @pytest.mark.parametrize("tool", EXPECTED_TOOLS)
    def test_tool_listed_in_readme(self, readme_text: str, tool: str):
        assert tool in readme_text, f"README.md MCP tools table missing: {tool}"


class TestReadmeRuleCategories:
    """README project structure should list all rule category directories."""

    def test_lists_all_rule_categories(
        self, readme_text: str, rule_categories: list[str]
    ):
        for category in rule_categories:
            assert category in readme_text, (
                f"README.md project structure missing rule category: {category}"
            )


class TestReadmeLinks:
    """Key external links should be present."""

    def test_has_mcp_toolkit_link(self, readme_text: str):
        assert "MCPToolKit" in readme_text or "mcptoolkit" in readme_text.lower()

    def test_has_agent_kit_link(self, readme_text: str):
        assert "cosmosdb-agent-kit" in readme_text

    def test_has_cosmos_db_docs_link(self, readme_text: str):
        assert "learn.microsoft.com" in readme_text or "azure.microsoft.com" in readme_text
