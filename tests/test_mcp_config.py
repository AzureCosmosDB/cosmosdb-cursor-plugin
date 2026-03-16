"""Tests for the .mcp.json configuration file."""

import json
import pathlib

import pytest


@pytest.fixture()
def mcp_json(project_root: pathlib.Path) -> dict:
    path = project_root / ".mcp.json"
    return json.loads(path.read_text(encoding="utf-8"))


class TestMcpJsonSchema:
    """Validate structure and content of .mcp.json."""

    def test_valid_json(self, project_root: pathlib.Path):
        path = project_root / ".mcp.json"
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            pytest.fail(f".mcp.json is not valid JSON: {exc}")

    def test_has_mcp_servers_key(self, mcp_json: dict):
        assert "mcpServers" in mcp_json, ".mcp.json must have 'mcpServers' key"

    def test_mcp_servers_is_dict(self, mcp_json: dict):
        assert isinstance(mcp_json["mcpServers"], dict)

    def test_has_at_least_one_server(self, mcp_json: dict):
        assert len(mcp_json["mcpServers"]) >= 1, "At least one MCP server must be configured"

    def test_azure_cosmosdb_server_defined(self, mcp_json: dict):
        assert "azure-cosmosdb" in mcp_json["mcpServers"], (
            "Expected 'azure-cosmosdb' server entry"
        )


class TestAzureCosmosDbServer:
    """Validate the azure-cosmosdb server configuration."""

    @pytest.fixture()
    def server_config(self, mcp_json: dict) -> dict:
        return mcp_json["mcpServers"]["azure-cosmosdb"]

    def test_has_url(self, server_config: dict):
        assert "url" in server_config, "Server config must include 'url'"

    def test_url_uses_env_variable(self, server_config: dict):
        """URL should reference an environment variable, not a hardcoded value."""
        url = server_config["url"]
        assert "${COSMOSDB_MCP_SERVER_URL}" in url, (
            "URL should use ${COSMOSDB_MCP_SERVER_URL} env variable placeholder"
        )

    def test_url_ends_with_mcp_path(self, server_config: dict):
        url = server_config["url"]
        assert url.endswith("/mcp"), "Server URL should end with '/mcp'"

    def test_has_authorization_header(self, server_config: dict):
        headers = server_config.get("headers", {})
        assert "Authorization" in headers, "Authorization header is required"

    def test_auth_uses_bearer_token_env_variable(self, server_config: dict):
        auth = server_config["headers"]["Authorization"]
        assert "Bearer" in auth, "Authorization should use Bearer scheme"
        assert "${COSMOSDB_MCP_JWT_TOKEN}" in auth, (
            "Authorization should reference ${COSMOSDB_MCP_JWT_TOKEN}"
        )
