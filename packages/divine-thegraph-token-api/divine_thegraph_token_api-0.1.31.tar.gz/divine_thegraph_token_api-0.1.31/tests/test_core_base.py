"""
Core Base API Testing - Comprehensive coverage for base.py
Tests BaseTokenAPI initialization, validation, and async functionality.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from thegraph_token_api.base import BaseTokenAPI


class TestBaseTokenAPIInitialization:
    """Test BaseTokenAPI initialization and configuration."""

    def test_initialization_without_api_key_raises_error(self):
        """Test BaseTokenAPI initialization fails when no API key and no env var (line 43)."""
        with patch.dict("os.environ", {}, clear=True), pytest.raises(ValueError, match="API key is required"):
            BaseTokenAPI()

    def test_initialization_with_explicit_api_key(self):
        """Test BaseTokenAPI initialization with explicit API key."""
        client = BaseTokenAPI("test_key")  # pragma: allowlist secret
        assert client.api_key == "test_key"  # pragma: allowlist secret

    def test_initialization_with_env_variables(self):
        """Test BaseTokenAPI initialization with environment variables (lines 56-59)."""
        with patch.dict(
            "os.environ",
            {
                "THEGRAPH_API_KEY": "env_key",  # pragma: allowlist secret
                "THEGRAPH_API_ENDPOINT": "https://custom.endpoint.com",
            },  # pragma: allowlist secret
        ):
            client = BaseTokenAPI()
            assert client.api_key == "env_key"  # pragma: allowlist secret
            assert client.base_url == "https://custom.endpoint.com"

    def test_initialization_with_custom_base_url(self):
        """Test BaseTokenAPI initialization with custom base URL (lines 63-64)."""
        client = BaseTokenAPI("test_key", base_url="https://custom.api.com")  # pragma: allowlist secret
        assert client.api_key == "test_key"  # pragma: allowlist secret
        assert client.base_url == "https://custom.api.com"

    def test_initialization_with_default_base_url(self):
        """Test BaseTokenAPI initialization with default base URL (line 68)."""
        client = BaseTokenAPI("test_key")
        assert "thegraph.com" in client.base_url


class TestBaseTokenAPIPagination:
    """Test pagination validation functionality."""

    def test_pagination_validation_valid_params(self):
        """Test _validate_pagination with valid parameters."""
        client = BaseTokenAPI("test_key")

        # These should not raise any exceptions
        client._validate_pagination(1, 1)
        client._validate_pagination(10, 5)
        client._validate_pagination(1000, 1)

    def test_pagination_validation_invalid_limit_low(self):
        """Test _validate_pagination with limit too low."""
        client = BaseTokenAPI("test_key")

        with pytest.raises(ValueError, match="limit must be between 1 and 1000"):
            client._validate_pagination(0, 1)

    def test_pagination_validation_invalid_limit_high(self):
        """Test _validate_pagination with limit too high."""
        client = BaseTokenAPI("test_key")

        with pytest.raises(ValueError, match="limit must be between 1 and 1000"):
            client._validate_pagination(1001, 1)

    def test_pagination_validation_invalid_page(self):
        """Test _validate_pagination with invalid page number."""
        client = BaseTokenAPI("test_key")

        with pytest.raises(ValueError, match="page must be 1 or greater"):
            client._validate_pagination(10, 0)


class TestBaseTokenAPIAsyncMethods:
    """Test async methods and context manager functionality."""

    @pytest.mark.anyio
    async def test_async_context_manager(self):
        """Test BaseTokenAPI async context manager (lines 79-83)."""
        client = BaseTokenAPI("test_key")

        # Mock the manager for context manager
        with patch.object(client, "manager") as mock_manager:
            mock_manager.startup = AsyncMock()
            mock_manager.shutdown = AsyncMock()

            async with client as ctx:
                assert ctx is client
                mock_manager.startup.assert_called_once()

            mock_manager.shutdown.assert_called_once()

    @pytest.mark.anyio
    async def test_get_health(self):
        """Test get_health method (lines 79-83)."""
        client = BaseTokenAPI("test_key")

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.text = "OK"
            mock_manager.get = AsyncMock(return_value=mock_response)

            result = await client.get_health()
            assert result == "OK"

            mock_manager.get.assert_called_once_with(f"{client.base_url}/health", headers=client._headers, timeout=30)

    @pytest.mark.anyio
    async def test_get_version(self):
        """Test get_version method (lines 92-97)."""
        client = BaseTokenAPI("test_key")

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = {"version": "1.0.0", "date": "2023-11-01", "commit": "abc123"}
            mock_manager.get = AsyncMock(return_value=mock_response)

            result = await client.get_version()
            assert result["version"] == "1.0.0"

            # The actual implementation uses VersionResponse type
            mock_manager.get.assert_called_once()

    @pytest.mark.anyio
    async def test_get_networks(self):
        """Test get_networks method (lines 106-111)."""
        client = BaseTokenAPI("test_key")

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = {"networks": [{"id": "mainnet", "name": "Ethereum Mainnet"}]}
            mock_manager.get = AsyncMock(return_value=mock_response)

            result = await client.get_networks()
            assert "networks" in result

            # The actual implementation uses NetworksResponse type
            mock_manager.get.assert_called_once()


class TestBaseTokenAPIProperties:
    """Test BaseTokenAPI properties and headers."""

    def test_headers_property(self):
        """Test _headers property generates correct headers."""
        client = BaseTokenAPI("test_key")
        headers = client._headers

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_key"
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"

    def test_headers_property_with_none_api_key(self):
        """Test _headers property with None API key."""
        with patch.dict("os.environ", {"THEGRAPH_API_KEY": "env_key"}):  # pragma: allowlist secret
            client = BaseTokenAPI()
            headers = client._headers

            assert headers["Authorization"] == "Bearer env_key"


class TestBaseTokenAPIIntegration:
    """Test BaseTokenAPI integration scenarios."""

    def test_multiple_initialization_patterns(self):
        """Test various initialization patterns work correctly."""
        # Pattern 1: Direct API key
        client1 = BaseTokenAPI("direct_key")  # pragma: allowlist secret
        assert client1.api_key == "direct_key"  # pragma: allowlist secret

        # Pattern 2: API key + custom URL
        client2 = BaseTokenAPI("key2", "https://custom.com")  # pragma: allowlist secret
        assert client2.api_key == "key2"  # pragma: allowlist secret
        assert client2.base_url == "https://custom.com"

        # Pattern 3: Environment variable
        with patch.dict("os.environ", {"THEGRAPH_API_KEY": "env_key"}):  # pragma: allowlist secret
            client3 = BaseTokenAPI()
            assert client3.api_key == "env_key"  # pragma: allowlist secret

    @pytest.mark.anyio
    async def test_error_handling_in_async_methods(self):
        """Test error handling in async methods."""
        client = BaseTokenAPI("test_key")

        with patch.object(client, "manager") as mock_manager:
            # Simulate an exception
            mock_manager.get = AsyncMock(side_effect=Exception("Network error"))

            with pytest.raises(Exception, match="Network error"):
                await client.get_health()

    def test_manager_property_initialization(self):
        """Test that manager property is properly initialized."""
        client = BaseTokenAPI("test_key")

        # Manager should be initialized directly
        assert hasattr(client, "manager")

        # Accessing manager should return the initialized instance
        manager = client.manager
        assert manager is not None

        # Second access should return the same instance
        assert client.manager is manager
