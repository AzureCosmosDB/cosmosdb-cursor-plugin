"""Shared fixtures for cosmosdb-cursor-plugin tests."""

import pathlib

import pytest

# Resolve project root (one level up from tests/)
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Category names matching the .mdc filenames (without extension)
EXPECTED_RULE_CATEGORIES = [
    "data-modeling",
    "design-patterns",
    "global-distribution",
    "indexing",
    "monitoring",
    "partition-key",
    "query-optimization",
    "sdk-patterns",
    "throughput",
    "vector-search",
]

# The overview .mdc file name (without extension)
OVERVIEW_RULE_NAME = "cosmosdb-overview"


@pytest.fixture()
def project_root() -> pathlib.Path:
    return PROJECT_ROOT


@pytest.fixture()
def rules_dir(project_root: pathlib.Path) -> pathlib.Path:
    return project_root / "rules"


@pytest.fixture()
def rule_categories() -> list[str]:
    return EXPECTED_RULE_CATEGORIES
