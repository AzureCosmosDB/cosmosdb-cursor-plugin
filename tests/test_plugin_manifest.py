"""Tests for the .cursor-plugin/plugin.json manifest."""

import json
import pathlib

import pytest


@pytest.fixture()
def plugin_json(project_root: pathlib.Path) -> dict:
    path = project_root / ".cursor-plugin" / "plugin.json"
    return json.loads(path.read_text(encoding="utf-8"))


class TestPluginJsonSchema:
    """Validate required fields in plugin.json."""

    REQUIRED_TOP_LEVEL_KEYS = [
        "name",
        "version",
        "description",
        "author",
        "license",
    ]

    def test_valid_json(self, project_root: pathlib.Path):
        path = project_root / ".cursor-plugin" / "plugin.json"
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            pytest.fail(f"plugin.json is not valid JSON: {exc}")

    @pytest.mark.parametrize("key", REQUIRED_TOP_LEVEL_KEYS)
    def test_has_required_field(self, plugin_json: dict, key: str):
        assert key in plugin_json, f"plugin.json missing required field: {key}"

    def test_name_is_string(self, plugin_json: dict):
        assert isinstance(plugin_json["name"], str)
        assert len(plugin_json["name"]) > 0

    def test_version_format(self, plugin_json: dict):
        """Version should be a semver-like string (e.g. '0.1.0')."""
        version = plugin_json["version"]
        parts = version.split(".")
        assert len(parts) == 3, f"Version '{version}' is not semver (X.Y.Z)"
        for part in parts:
            assert part.isdigit(), f"Version segment '{part}' is not numeric"

    def test_description_not_empty(self, plugin_json: dict):
        assert len(plugin_json["description"].strip()) > 0

    def test_author_has_name(self, plugin_json: dict):
        author = plugin_json["author"]
        assert isinstance(author, dict), "author should be an object"
        assert "name" in author, "author.name is required"
        assert len(author["name"].strip()) > 0

    def test_license_is_mit(self, plugin_json: dict):
        assert plugin_json["license"] == "MIT"

    def test_keywords_include_cosmosdb(self, plugin_json: dict):
        keywords = plugin_json.get("keywords", [])
        assert isinstance(keywords, list)
        lower_keywords = [k.lower() for k in keywords]
        assert any(
            "cosmos" in kw for kw in lower_keywords
        ), "keywords should contain a Cosmos DB-related entry"

    def test_logo_path_points_to_existing_file(
        self, plugin_json: dict, project_root: pathlib.Path
    ):
        logo = plugin_json.get("logo")
        if logo is not None:
            logo_path = project_root / logo
            assert logo_path.is_file(), f"Logo file does not exist: {logo}"
