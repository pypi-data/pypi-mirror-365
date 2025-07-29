"""
EVM API Testing - Comprehensive coverage for evm.py
Tests all EVM API methods with various parameter combinations.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from thegraph_token_api.evm import EVMTokenAPI
from thegraph_token_api.types import (
    Interval,
    NetworkId,
    OrderBy,
    OrderDirection,
    Protocol,
    TokenStandard,
)


class TestEVMTokenAPIInitialization:
    """Test EVMTokenAPI initialization."""

    def test_initialization_with_string_network(self):
        """Test EVMTokenAPI initialization with string network (line 66)."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret
        assert client.network == "mainnet"
        assert client.api_key == "test_key"  # pragma: allowlist secret

    def test_initialization_with_enum_network(self):
        """Test EVMTokenAPI initialization with enum network."""
        client = EVMTokenAPI(network=NetworkId.MATIC, api_key="test_key")  # pragma: allowlist secret
        assert client.network == "matic"  # Enum value
        assert client.api_key == "test_key"  # pragma: allowlist secret

    def test_initialization_with_custom_base_url(self):
        """Test EVMTokenAPI initialization with custom base URL."""
        client = EVMTokenAPI(
            network="mainnet",
            api_key="test_key",  # pragma: allowlist secret
            base_url="https://custom.api.com",
        )
        assert client.network == "mainnet"
        assert client.api_key == "test_key"  # pragma: allowlist secret
        assert client.base_url == "https://custom.api.com"


class TestEVMNFTMethods:
    """Test EVM NFT-related methods."""

    @pytest.mark.anyio
    async def test_get_nft_ownerships_minimal(self):
        """Test get_nft_ownerships with minimal parameters."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            result = await client.get_nft_ownerships(address="0xtest")

            mock_manager.get.assert_called_once()
            call_args = mock_manager.get.call_args
            assert "nft/ownerships/evm/0xtest" in call_args[0][0]
            assert call_args[1]["params"]["network_id"] == "mainnet"
            assert result == []

    @pytest.mark.anyio
    async def test_get_nft_ownerships_full_parameters(self):
        """Test get_nft_ownerships with all parameters."""
        client = EVMTokenAPI(network="polygon", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_nft_ownerships(address="0xtest", token_standard=TokenStandard.ERC721, limit=20, page=2)

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["network_id"] == "polygon"
            assert params["token_standard"] == "ERC721"
            assert params["limit"] == 20
            assert params["page"] == 2

    @pytest.mark.anyio
    async def test_get_nft_collection(self):
        """Test get_nft_collection method."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = {"name": "Test Collection"}
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_nft_collection(contract="0xtest")

            mock_manager.get.assert_called_once()
            call_args = mock_manager.get.call_args
            assert "nft/collections/evm/0xtest" in call_args[0][0]
            assert call_args[1]["params"]["network_id"] == "mainnet"

    @pytest.mark.anyio
    async def test_get_nft_item(self):
        """Test get_nft_item method."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = {"token_id": "123"}
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_nft_item(contract="0xtest", token_id="123")

            mock_manager.get.assert_called_once()
            call_args = mock_manager.get.call_args
            assert "nft/items/evm/contract/0xtest/token_id/123" in call_args[0][0]

    @pytest.mark.anyio
    async def test_get_nft_activities_full_parameters(self):
        """Test get_nft_activities with all parameters."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_nft_activities(
                contract="0xtest",
                any_address="0xany",
                from_address="0xfrom",
                to_address="0xto",
                start_time=1640995200,
                end_time=1640995300,
                order_by=OrderBy.TIMESTAMP,
                order_direction=OrderDirection.DESC,
                limit=25,
                page=2,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["contract"] == "0xtest"
            assert params["any"] == "0xany"
            assert params["from"] == "0xfrom"
            assert params["to"] == "0xto"
            assert params["startTime"] == 1640995200
            assert params["endTime"] == 1640995300
            assert params["orderBy"] == "timestamp"
            assert params["orderDirection"] == "desc"

    @pytest.mark.anyio
    async def test_get_nft_holders(self):
        """Test get_nft_holders method."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_nft_holders(contract="0xtest")

            mock_manager.get.assert_called_once()
            call_args = mock_manager.get.call_args
            assert "nft/holders/evm/0xtest" in call_args[0][0]

    @pytest.mark.anyio
    async def test_get_nft_sales_full_parameters(self):
        """Test get_nft_sales with all parameters."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_nft_sales(
                contract="0xtest",
                token_id="123",
                any_address="0xany",
                offerer="0xofferer",
                recipient="0xrecipient",
                start_time=1640995200,
                end_time=1640995300,
                order_by=OrderBy.TIMESTAMP,
                order_direction=OrderDirection.DESC,
                limit=15,
                page=1,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["contract"] == "0xtest"
            assert params["token_id"] == "123"
            assert params["offerer"] == "0xofferer"
            assert params["recipient"] == "0xrecipient"


class TestEVMTokenMethods:
    """Test EVM token-related methods."""

    @pytest.mark.anyio
    async def test_get_balances_minimal(self):
        """Test get_balances with minimal parameters."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_balances(address="0xtest")

            mock_manager.get.assert_called_once()
            call_args = mock_manager.get.call_args
            assert "balances/evm/0xtest" in call_args[0][0]
            assert call_args[1]["params"]["network_id"] == "mainnet"

    @pytest.mark.anyio
    async def test_get_balances_with_contract_filter(self):
        """Test get_balances with contract filter."""
        client = EVMTokenAPI(network="polygon", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_balances(address="0xtest", contract="0xtoken", limit=50, page=2)

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["contract"] == "0xtoken"
            assert params["limit"] == 50
            assert params["page"] == 2

    @pytest.mark.anyio
    async def test_get_token(self):
        """Test get_token method."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_token(contract="0xtoken")

            mock_manager.get.assert_called_once()
            call_args = mock_manager.get.call_args
            assert "tokens/evm/0xtoken" in call_args[0][0]

    @pytest.mark.anyio
    async def test_get_token_holders_with_ordering(self):
        """Test get_token_holders with ordering parameters."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_token_holders(
                contract="0xtoken", order_by=OrderBy.VALUE, order_direction=OrderDirection.ASC, limit=100, page=3
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["orderBy"] == "value"
            assert params["orderDirection"] == "asc"
            assert params["limit"] == 100
            assert params["page"] == 3


class TestEVMTradingMethods:
    """Test EVM trading-related methods (transfers, swaps, pools)."""

    @pytest.mark.anyio
    async def test_get_transfers_full_parameters(self):
        """Test get_transfers with all parameters."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_transfers(
                from_address="0xfrom",
                to_address="0xto",
                contract="0xtoken",
                transaction_id="0xtx",
                start_time=1640995200,
                end_time=1640995300,
                order_by=OrderBy.TIMESTAMP,
                order_direction=OrderDirection.DESC,
                limit=25,
                page=1,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["from"] == "0xfrom"
            assert params["to"] == "0xto"
            assert params["contract"] == "0xtoken"
            assert params["transaction_id"] == "0xtx"
            assert params["startTime"] == 1640995200
            assert params["endTime"] == 1640995300

    @pytest.mark.anyio
    async def test_get_swaps_full_parameters(self):
        """Test get_swaps with all parameters."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_swaps(
                pool="0xpool",
                caller="0xcaller",
                sender="0xsender",
                recipient="0xrecipient",
                protocol=Protocol.UNISWAP_V3,
                transaction_id="0xtx",
                start_time=1640995200,
                end_time=1640995300,
                order_by=OrderBy.TIMESTAMP,
                order_direction=OrderDirection.DESC,
                limit=20,
                page=1,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["pool"] == "0xpool"
            assert params["caller"] == "0xcaller"
            assert params["protocol"] == "uniswap_v3"
            assert params["transaction_id"] == "0xtx"

    @pytest.mark.anyio
    async def test_get_pools_with_filters(self):
        """Test get_pools with various filters."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_pools(
                pool="0xpool",
                factory="0xfactory",
                token="0xtoken",
                symbol="ETH",
                protocol=Protocol.UNISWAP_V2,
                limit=30,
                page=1,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["pool"] == "0xpool"
            assert params["factory"] == "0xfactory"
            assert params["token"] == "0xtoken"
            assert params["symbol"] == "ETH"
            assert params["protocol"] == "uniswap_v2"


class TestEVMPricingMethods:
    """Test EVM pricing and historical data methods."""

    @pytest.mark.anyio
    async def test_get_ohlc_pools_full_parameters(self):
        """Test get_ohlc_pools with all parameters."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_ohlc_pools(
                pool="0xpool", interval=Interval.ONE_HOUR, start_time=1640995200, end_time=1640995300, limit=24, page=1
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["interval"] == "1h"
            assert params["startTime"] == 1640995200
            assert params["endTime"] == 1640995300
            assert "ohlc/pools/evm/0xpool" in call_args[0][0]

    @pytest.mark.anyio
    async def test_get_ohlc_prices_different_intervals(self):
        """Test get_ohlc_prices with different intervals."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            # Test with FOUR_HOURS interval
            await client.get_ohlc_prices(
                token="0xtoken",
                interval=Interval.FOUR_HOURS,
                start_time=1640995200,
                end_time=1640995300,
                limit=48,
                page=1,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["interval"] == "4h"
            assert "ohlc/prices/evm/0xtoken" in call_args[0][0]

    @pytest.mark.anyio
    async def test_get_historical_balances_with_contracts(self):
        """Test get_historical_balances with contract filters."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_historical_balances(
                address="0xtest",
                contracts=["0xtoken1", "0xtoken2"],
                interval=Interval.ONE_DAY,
                start_time=1640995200,
                end_time=1640995300,
                limit=30,
                page=1,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["contracts"] == ["0xtoken1", "0xtoken2"]
            assert params["interval"] == "1d"
            assert "historical/balances/evm/0xtest" in call_args[0][0]


class TestEVMMethodCombinations:
    """Test combinations and edge cases for EVM methods."""

    @pytest.mark.anyio
    async def test_multiple_conditional_parameters(self):
        """Test methods with multiple conditional parameters set."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            # Test transfers with transaction_id (covers line 390)
            await client.get_transfers(transaction_id="0xtx123")

            # Test swaps with transaction_id (covers more conditional lines)
            await client.get_swaps(transaction_id="0xtx456")

            # Test pools with factory and symbol (covers lines 577, 581)
            await client.get_pools(factory="0xfactory", symbol="ETH")

            # Verify all calls were made
            assert mock_manager.get.call_count == 3

    @pytest.mark.anyio
    async def test_different_network_configurations(self):
        """Test methods work with different network configurations."""
        networks = ["mainnet", "polygon", "bsc", "arbitrum", "optimism"]

        for network in networks:
            client = EVMTokenAPI(network=network, api_key="test_key")

            with patch.object(client, "manager") as mock_manager:
                mock_response = MagicMock()
                mock_response.data = []
                mock_manager.get = AsyncMock(return_value=mock_response)

                await client.get_balances(address="0xtest")

                call_args = mock_manager.get.call_args
                assert call_args[1]["params"]["network_id"] == network

    @pytest.mark.anyio
    async def test_pagination_validation_integration(self):
        """Test that pagination validation works with EVM methods."""
        client = EVMTokenAPI(network="mainnet", api_key="test_key")  # pragma: allowlist secret

        # These should raise ValueError due to invalid pagination
        with pytest.raises(ValueError):
            await client.get_balances(address="0xtest", limit=0)

        with pytest.raises(ValueError):
            await client.get_nft_ownerships(address="0xtest", page=0)

        with pytest.raises(ValueError):
            await client.get_transfers(limit=1001)
