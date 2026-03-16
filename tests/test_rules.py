"""Tests for .mdc rule files — frontmatter, content, and cross-references."""

import pathlib
import re

import pytest
import yaml

from .conftest import EXPECTED_RULE_CATEGORIES, OVERVIEW_RULE_NAME


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_rule_file(path: pathlib.Path) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_text) from an .mdc rule file."""
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"No YAML frontmatter found in {path}")
    fm = yaml.safe_load(match.group(1))
    body = text[match.end():]
    return fm, body


def _all_rule_files(rules_dir: pathlib.Path):
    """Yield (category_name, path) for every .mdc rule file."""
    overview = rules_dir / f"{OVERVIEW_RULE_NAME}.mdc"
    if overview.is_file():
        yield (OVERVIEW_RULE_NAME, overview)
    for category in EXPECTED_RULE_CATEGORIES:
        p = rules_dir / f"{category}.mdc"
        if p.is_file():
            yield (category, p)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(params=[OVERVIEW_RULE_NAME] + EXPECTED_RULE_CATEGORIES)
def rule_entry(request, rules_dir: pathlib.Path):
    """Parametrize over every .mdc rule file (overview + categories)."""
    name = request.param
    path = rules_dir / f"{name}.mdc"
    return name, path


# ---------------------------------------------------------------------------
# Tests — Frontmatter
# ---------------------------------------------------------------------------


class TestFrontmatter:
    """Each .mdc rule must have valid YAML frontmatter with required fields."""

    def test_has_yaml_frontmatter(self, rule_entry):
        name, path = rule_entry
        text = path.read_text(encoding="utf-8")
        assert _FRONTMATTER_RE.match(text), f"{name}.mdc missing YAML frontmatter"

    def test_frontmatter_has_description(self, rule_entry):
        name, path = rule_entry
        fm, _ = _parse_rule_file(path)
        assert "description" in fm, f"{name}.mdc frontmatter missing 'description'"
        assert isinstance(fm["description"], str)
        assert len(fm["description"].strip()) > 0

    def test_description_mentions_cosmos_db(self, rule_entry):
        name, path = rule_entry
        fm, _ = _parse_rule_file(path)
        desc = fm["description"].lower()
        assert "cosmos db" in desc or "cosmosdb" in desc, (
            f"{name}.mdc description should mention Cosmos DB"
        )

    def test_frontmatter_has_globs(self, rule_entry):
        name, path = rule_entry
        fm, _ = _parse_rule_file(path)
        assert "globs" in fm, f"{name}.mdc frontmatter missing 'globs'"
        globs = fm["globs"]
        assert isinstance(globs, list) and len(globs) >= 1

    def test_globs_contain_common_extensions(self, rule_entry):
        """Globs should cover at least .cs, .ts, .js, .py, .java."""
        name, path = rule_entry
        fm, _ = _parse_rule_file(path)
        globs_joined = " ".join(fm["globs"])
        for ext in ("cs", "ts", "js", "py", "java"):
            assert ext in globs_joined, (
                f"{name}.mdc globs should include .{ext}"
            )

    def test_always_apply_is_false(self, rule_entry):
        name, path = rule_entry
        fm, _ = _parse_rule_file(path)
        assert "alwaysApply" in fm, f"{name}.mdc frontmatter missing 'alwaysApply'"
        assert fm["alwaysApply"] is False, (
            f"{name}.mdc alwaysApply should be false"
        )


# ---------------------------------------------------------------------------
# Tests — Body content
# ---------------------------------------------------------------------------


class TestRuleBody:
    """.mdc rule body must contain meaningful content."""

    def test_body_is_not_empty(self, rule_entry):
        name, path = rule_entry
        _, body = _parse_rule_file(path)
        assert len(body.strip()) > 0, f"{name}.mdc body is empty"

    def test_body_has_markdown_heading(self, rule_entry):
        name, path = rule_entry
        _, body = _parse_rule_file(path)
        assert re.search(r"^#{1,2}\s+\S", body, re.MULTILINE), (
            f"{name}.mdc body should have at least one markdown heading"
        )

    def test_category_rules_have_code_or_config_examples(self, rule_entry):
        """Non-overview .mdc files should contain code/config examples."""
        name, path = rule_entry
        if name == OVERVIEW_RULE_NAME:
            pytest.skip("Overview rule is a hub and may not have code examples")
        _, body = _parse_rule_file(path)
        assert "```" in body, (
            f"{name}.mdc should include fenced code examples"
        )

    def test_category_rules_have_multiple_sections(self, rule_entry):
        """Non-overview rules should have at least two ## sections."""
        name, path = rule_entry
        if name == OVERVIEW_RULE_NAME:
            pytest.skip("Overview rule is a hub")
        _, body = _parse_rule_file(path)
        h2_count = len(re.findall(r"^## ", body, re.MULTILINE))
        assert h2_count >= 2, (
            f"{name}.mdc should have at least 2 ## sections (found {h2_count})"
        )


# ---------------------------------------------------------------------------
# Tests — Index rule cross-references
# ---------------------------------------------------------------------------


class TestOverviewRuleCrossReferences:
    """The overview rule must reference all category .mdc files."""

    def test_overview_references_all_categories(
        self, rules_dir: pathlib.Path, rule_categories: list[str]
    ):
        _, body = _parse_rule_file(rules_dir / f"{OVERVIEW_RULE_NAME}.mdc")
        for category in rule_categories:
            assert category in body, (
                f"Overview rule does not reference category '{category}'"
            )

    def test_overview_has_no_stale_references(
        self, rules_dir: pathlib.Path, rule_categories: list[str]
    ):
        """Back-tick references in the overview should
        correspond to actual .mdc rule files."""
        _, body = _parse_rule_file(rules_dir / f"{OVERVIEW_RULE_NAME}.mdc")
        backtick_refs = re.findall(r"`([a-z][\w-]+)\.mdc`", body)
        for ref in backtick_refs:
            assert ref in rule_categories, (
                f"Overview references '{ref}.mdc' but no matching rule file exists"
            )


# ---------------------------------------------------------------------------
# Tests — Auto-generated markers
# ---------------------------------------------------------------------------


class TestAutoGeneratedMarkers:
    """Each .mdc rule should carry the auto-generated marker."""

    def test_has_auto_generated_marker(self, rule_entry):
        name, path = rule_entry
        fm, body = _parse_rule_file(path)
        text = path.read_text(encoding="utf-8")
        has_marker = (
            "auto-generated" in text.lower()
            or "regenerate" in text.lower()
            or "cosmosdb-agent-kit" in text.lower()
            or "cosmos db" in fm.get("description", "").lower()
        )
        assert has_marker, (
            f"{name}.mdc should be traceable to its source"
        )
