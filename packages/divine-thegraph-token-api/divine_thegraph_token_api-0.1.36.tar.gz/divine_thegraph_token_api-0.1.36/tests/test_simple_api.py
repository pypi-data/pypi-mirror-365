"""
Simple API Testing - Comprehensive coverage for simple.py
Tests the user-facing TokenAPI wrapper with all internal methods and wrapper classes.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from thegraph_token_api.simple import EVMWrapper, NFTWrapper, SVMWrapper, TokenAPI
from thegraph_token_api.types import (
    Interval,
    OrderBy,
    OrderDirection,
    Protocol,
    SolanaPrograms,
    SwapPrograms,
    TokenStandard,
)


class TestTokenAPIInitialization:
    """Test TokenAPI initialization and configuration."""

    def test_initialization_with_api_key(self):
        """Test TokenAPI initialization with explicit API key."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)
        assert api._api.api_key == "test_key"  # pragma: allowlist secret
        assert api._default_network == "mainnet"
        assert isinstance(api.evm, EVMWrapper)
        assert isinstance(api.svm, SVMWrapper)
        assert isinstance(api.evm.nfts, NFTWrapper)

    def test_initialization_without_api_key_missing_env(self):
        """Test TokenAPI initialization fails when no API key and no env var."""
        with patch.dict("os.environ", {}, clear=True), pytest.raises(ValueError, match="API key not found"):
            TokenAPI(auto_load_env=False)

    def test_initialization_with_env_api_key(self):
        """Test TokenAPI initialization with API key from environment."""
        with patch.dict("os.environ", {"THEGRAPH_API_KEY": "env_key"}):  # pragma: allowlist secret
            api = TokenAPI(auto_load_env=False)
            assert api._api.api_key == "env_key"  # pragma: allowlist secret

    def test_initialization_with_custom_network(self):
        """Test TokenAPI initialization with custom default network."""
        api = TokenAPI(api_key="test_key", network="polygon", auto_load_env=False)
        assert api._default_network == "polygon"

    def test_initialization_auto_load_env(self):
        """Test auto-loading .env file."""
        with (
            patch("thegraph_token_api.simple.load_dotenv") as mock_load_dotenv,
            patch.dict("os.environ", {"THEGRAPH_API_KEY": "env_key"}),  # pragma: allowlist secret
        ):
            TokenAPI(auto_load_env=True)
            mock_load_dotenv.assert_called_once()

    def test_wrapper_initialization(self):
        """Test that wrappers are properly initialized."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        # Check wrapper initialization
        assert hasattr(api, "evm")
        assert hasattr(api, "svm")
        assert hasattr(api.evm, "nfts")

        # Check wrapper references point back to API
        assert api.evm._api is api
        assert api.svm._api is api
        assert api.evm.nfts._api is api


class TestTokenAPIUtilityMethods:
    """Test TokenAPI utility methods."""

    def test_extract_data_with_data_dict(self):
        """Test _extract_data with proper response containing data dict."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_response = MagicMock()
        mock_response.data = {"data": [{"symbol": "ETH"}]}

        result = api._extract_data(mock_response)
        assert result == [{"symbol": "ETH"}]

    def test_extract_data_no_data_key(self):
        """Test _extract_data when response.data has no 'data' key."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_response = MagicMock()
        mock_response.data = {"other": "value"}

        result = api._extract_data(mock_response)
        assert result == []

    def test_extract_data_no_data_attr(self):
        """Test _extract_data when response has no data attribute."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_response = MagicMock()
        del mock_response.data

        result = api._extract_data(mock_response)
        assert result == []

    @pytest.mark.anyio
    async def test_health_utility_method(self):
        """Test health utility method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with patch.object(api._api, "get_health") as mock_health:
            mock_health.return_value = "OK"

            result = await api.health()
            assert result == "OK"
            mock_health.assert_called_once()


class TestEVMInternalMethods:
    """Test EVM internal methods with proper async mocking."""

    @pytest.mark.anyio
    async def test_evm_balances_with_network(self):
        """Test _evm_balances with custom network."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"symbol": "ETH"}]}
        mock_client.get_balances = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_balances(address="0xtest", contract="0xtoken", limit=20, network="polygon")

            assert result == [{"symbol": "ETH"}]
            mock_evm.assert_called_with("polygon")
            mock_client.get_balances.assert_called_with(address="0xtest", contract="0xtoken", limit=20)

    @pytest.mark.anyio
    async def test_evm_balances_default_network(self):
        """Test _evm_balances with default network."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": []}
        mock_client.get_balances = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_balances(address="0xtest")

            assert result == []
            mock_evm.assert_called_with("mainnet")

    @pytest.mark.anyio
    async def test_evm_nfts(self):
        """Test _evm_nfts method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"token_id": "123"}]}
        mock_client.get_nft_ownerships = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_nfts(
                address="0xtest", token_standard=TokenStandard.ERC721, limit=15, network="mainnet"
            )

            assert result == [{"token_id": "123"}]
            mock_client.get_nft_ownerships.assert_called_with(
                address="0xtest", token_standard=TokenStandard.ERC721, limit=15
            )

    @pytest.mark.anyio
    async def test_evm_token_info_with_data(self):
        """Test _evm_token_info method returning data."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"symbol": "TEST"}]}
        mock_client.get_token = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_token_info(contract="0xtoken", network="polygon")

            assert result == {"symbol": "TEST"}

    @pytest.mark.anyio
    async def test_evm_token_info_empty_data(self):
        """Test _evm_token_info method with empty data."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": []}
        mock_client.get_token = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_token_info(contract="0xtoken")

            assert result is None

    @pytest.mark.anyio
    async def test_evm_transfers(self):
        """Test _evm_transfers method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"value": 1000}]}
        mock_client.get_transfers = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_transfers(
                from_address="0xfrom", to_address="0xto", contract="0xtoken", limit=30, network="arbitrum"
            )

            assert result == [{"value": 1000}]

    @pytest.mark.anyio
    async def test_evm_swaps_basic(self):
        """Test _evm_swaps method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"protocol": "uniswap_v3"}]}
        mock_client.get_swaps = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_swaps(pool="0xpool", protocol=Protocol.UNISWAP_V2, limit=50, network="mainnet")

            assert result == [{"protocol": "uniswap_v3"}]

    @pytest.mark.anyio
    async def test_evm_swaps_advanced(self):
        """Test _evm_swaps_advanced method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"transaction_id": "0xtx"}]}
        mock_client.get_swaps = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_swaps_advanced(
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
                limit=50,
                network="mainnet",
            )

            assert result == [{"transaction_id": "0xtx"}]

    @pytest.mark.anyio
    async def test_evm_nft_collection(self):
        """Test _evm_nft_collection method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"name": "Collection"}]}
        mock_client.get_nft_collection = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_nft_collection(contract="0xtest", network="polygon")

            assert result == {"name": "Collection"}

    @pytest.mark.anyio
    async def test_evm_nft_collection_empty(self):
        """Test _evm_nft_collection method with empty data."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": []}
        mock_client.get_nft_collection = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_nft_collection(contract="0xtest")

            assert result is None

    @pytest.mark.anyio
    async def test_evm_nft_activities(self):
        """Test _evm_nft_activities method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"activity_type": "transfer"}]}
        mock_client.get_nft_activities = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_nft_activities(
                contract="0xcontract", from_address="0xfrom", to_address="0xto", limit=25, network="matic"
            )

            assert result == [{"activity_type": "transfer"}]

    @pytest.mark.anyio
    async def test_evm_pools(self):
        """Test _evm_pools method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"pool": "0xpool"}]}
        mock_client.get_pools = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_pools(
                pool="0xpool", token="0xtoken", protocol=Protocol.UNISWAP_V2, limit=50, network="optimism"
            )

            assert result == [{"pool": "0xpool"}]

    @pytest.mark.anyio
    async def test_evm_price_history(self):
        """Test _evm_price_history method with datetime mocking."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"close": 1000.0}]}
        mock_client.get_ohlc_prices = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            # Mock datetime imports inside the function
            mock_now = MagicMock()
            mock_now.timestamp.return_value = 1640995200

            with patch("datetime.datetime") as mock_datetime_class, patch("datetime.timedelta") as mock_timedelta_class:
                mock_datetime_class.now.return_value = mock_now
                mock_timedelta_class.return_value = MagicMock()

                result = await api._evm_price_history(
                    token="0xtoken", interval=Interval.ONE_HOUR, days=7, limit=168, network="avalanche"
                )

                assert result == [{"close": 1000.0}]

    @pytest.mark.anyio
    async def test_evm_pool_history(self):
        """Test _evm_pool_history method with datetime mocking."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"volume": 500.0}]}
        mock_client.get_ohlc_pools = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            # Mock datetime imports inside the function
            mock_now = MagicMock()
            mock_now.timestamp.return_value = 1640995200

            with patch("datetime.datetime") as mock_datetime_class, patch("datetime.timedelta") as mock_timedelta_class:
                mock_datetime_class.now.return_value = mock_now
                mock_timedelta_class.return_value = MagicMock()

                result = await api._evm_pool_history(
                    pool="0xpool", interval=Interval.FOUR_HOURS, days=14, limit=84, network="unichain"
                )

                assert result == [{"volume": 500.0}]

    @pytest.mark.anyio
    async def test_evm_token_holders(self):
        """Test _evm_token_holders method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"address": "0xholder"}]}
        mock_client.get_token_holders = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "evm") as mock_evm:
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_evm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._evm_token_holders(contract="0xtoken", limit=100, network="bsc")

            assert result == [{"address": "0xholder"}]


class TestSVMInternalMethods:
    """Test SVM internal methods with proper async mocking."""

    @pytest.mark.anyio
    async def test_svm_balances(self):
        """Test _svm_balances method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"mint": "So11111111111111111111111111111111111111112"}]}
        mock_client.get_balances = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "svm") as mock_svm:
            mock_svm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_svm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._svm_balances(
                token_account="4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A",  # pragma: allowlist secret
                mint="So11111111111111111111111111111111111111112",
                program_id=SolanaPrograms.TOKEN,
                limit=25,
                network="solana",
            )

            assert result == [{"mint": "So11111111111111111111111111111111111111112"}]

    @pytest.mark.anyio
    async def test_svm_transfers(self):
        """Test _svm_transfers method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"signature": "sig123"}]}
        mock_client.get_transfers = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "svm") as mock_svm:
            mock_svm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_svm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._svm_transfers(
                signature="sig123",
                program_id=SolanaPrograms.TOKEN,
                mint="So11111111111111111111111111111111111111112",
                authority="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # pragma: allowlist secret
                source="4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A",  # pragma: allowlist secret
                destination="5dt8br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v360B",  # pragma: allowlist secret
                limit=35,
                network="solana",
            )

            assert result == [{"signature": "sig123"}]

    @pytest.mark.anyio
    async def test_svm_swaps(self):
        """Test _svm_swaps method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = {"data": [{"program_id": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"}]}
        mock_client.get_swaps = AsyncMock(return_value=mock_response)

        with patch.object(api._api, "svm") as mock_svm:
            mock_svm.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_svm.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await api._svm_swaps(
                program_id=SwapPrograms.RAYDIUM,
                amm="AMM123",
                amm_pool="POOL123",
                user="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # pragma: allowlist secret  # pragma: allowlist secret
                input_mint="So11111111111111111111111111111111111111112",
                output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # pragma: allowlist secret
                signature="swap_sig123",
                start_time=1640995200,
                end_time=1640995300,
                limit=45,
                network="solana",
            )

            assert result == [{"program_id": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"}]


class TestWrapperClasses:
    """Test wrapper class methods with model conversion."""

    @pytest.mark.anyio
    async def test_nft_wrapper_ownerships(self):
        """Test NFTWrapper.ownerships method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_nfts") as mock_evm_nfts,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_evm_nfts.return_value = [{"token_id": "123"}]
            mock_convert.return_value = ["nft_ownership"]

            result = await api.evm.nfts.ownerships(
                address="0xtest", token_standard=TokenStandard.ERC721, limit=10, network="mainnet"
            )

            assert result == ["nft_ownership"]
            mock_evm_nfts.assert_called_with(
                address="0xtest", token_standard=TokenStandard.ERC721, limit=10, network="mainnet"
            )

    @pytest.mark.anyio
    async def test_nft_wrapper_collection_with_data(self):
        """Test NFTWrapper.collection method with data."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_nft_collection") as mock_collection,
            patch("thegraph_token_api.simple.convert_to_model") as mock_convert,
        ):
            mock_collection.return_value = {"name": "Collection"}
            mock_convert.return_value = "nft_collection"

            result = await api.evm.nfts.collection(contract="0xtest", network="polygon")

            assert result == "nft_collection"
            mock_collection.assert_called_with(contract="0xtest", network="polygon")

    @pytest.mark.anyio
    async def test_nft_wrapper_collection_none(self):
        """Test NFTWrapper.collection method with None data."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with patch.object(api, "_evm_nft_collection") as mock_collection:
            mock_collection.return_value = None

            result = await api.evm.nfts.collection(contract="0xtest")

            assert result is None

    @pytest.mark.anyio
    async def test_nft_wrapper_activities(self):
        """Test NFTWrapper.activities method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_nft_activities") as mock_activities,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_activities.return_value = [{"activity_type": "transfer"}]
            mock_convert.return_value = ["nft_activity"]

            result = await api.evm.nfts.activities(
                contract="0xtest", from_address="0xfrom", to_address="0xto", limit=10, network="mainnet"
            )

            assert result == ["nft_activity"]

    @pytest.mark.anyio
    async def test_evm_wrapper_balances(self):
        """Test EVMWrapper.balances method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_balances") as mock_balances,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_balances.return_value = [{"symbol": "ETH"}]
            mock_convert.return_value = ["balance"]

            result = await api.evm.balances(address="0xtest", contract="0xtoken", limit=10, network="mainnet")

            assert result == ["balance"]

    @pytest.mark.anyio
    async def test_evm_wrapper_token_info_with_data(self):
        """Test EVMWrapper.token_info method with data."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_token_info") as mock_token_info,
            patch("thegraph_token_api.simple.convert_to_model") as mock_convert,
        ):
            mock_token_info.return_value = {"symbol": "TEST"}
            mock_convert.return_value = "token"

            result = await api.evm.token_info(contract="0xtest", network="polygon")

            assert result == "token"

    @pytest.mark.anyio
    async def test_evm_wrapper_token_info_none(self):
        """Test EVMWrapper.token_info method with None data."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with patch.object(api, "_evm_token_info") as mock_token_info:
            mock_token_info.return_value = None

            result = await api.evm.token_info(contract="0xtest")

            assert result is None

    @pytest.mark.anyio
    async def test_svm_wrapper_balances(self):
        """Test SVMWrapper.balances method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_svm_balances") as mock_balances,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_balances.return_value = [{"mint": "So11111111111111111111111111111111111111112"}]
            mock_convert.return_value = ["solana_balance"]

            result = await api.svm.balances(
                token_account="4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A",  # pragma: allowlist secret
                mint="So11111111111111111111111111111111111111112",
                program_id=SolanaPrograms.TOKEN,
                limit=10,
                network="solana",
            )

            assert result == ["solana_balance"]

    @pytest.mark.anyio
    async def test_svm_wrapper_swaps(self):
        """Test SVMWrapper.swaps method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_svm_swaps") as mock_swaps,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_swaps.return_value = [{"program_id": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"}]
            mock_convert.return_value = ["solana_swap"]

            result = await api.svm.swaps(
                program_id=SwapPrograms.RAYDIUM,
                amm="AMM123",
                user="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # pragma: allowlist secret
                limit=10,
                network="solana",
            )

            assert result == ["solana_swap"]


class TestEVMWrapperMissingMethods:
    """Test EVMWrapper methods not covered by existing tests."""

    @pytest.mark.anyio
    async def test_evm_wrapper_transfers(self):
        """Test EVMWrapper.transfers method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_transfers") as mock_transfers,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_transfers.return_value = [{"hash": "0xtx123"}]
            mock_convert.return_value = ["transfer"]

            result = await api.evm.transfers(
                from_address="0xfrom", to_address="0xto", contract="0xtoken", limit=5, network="mainnet"
            )

            assert result == ["transfer"]
            mock_transfers.assert_called_with(
                from_address="0xfrom", to_address="0xto", contract="0xtoken", limit=5, network="mainnet"
            )

    @pytest.mark.anyio
    async def test_evm_wrapper_swaps(self):
        """Test EVMWrapper.swaps method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_swaps") as mock_swaps,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_swaps.return_value = [{"protocol": "uniswap_v3"}]
            mock_convert.return_value = ["swap"]

            result = await api.evm.swaps(pool="0xpool", protocol=Protocol.UNISWAP_V3, limit=10, network="polygon")

            assert result == ["swap"]
            mock_swaps.assert_called_with(pool="0xpool", protocol=Protocol.UNISWAP_V3, limit=10, network="polygon")

    @pytest.mark.anyio
    async def test_evm_wrapper_swaps_advanced(self):
        """Test EVMWrapper.swaps_advanced method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_swaps_advanced") as mock_swaps_advanced,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_swaps_advanced.return_value = [{"transaction_id": "0xtx"}]
            mock_convert.return_value = ["swap"]

            result = await api.evm.swaps_advanced(
                pool="0xpool",
                caller="0xcaller",
                sender="0xsender",
                recipient="0xrecipient",
                protocol=Protocol.UNISWAP_V2,
                transaction_id="0xtx123",
                start_time=1640995200,
                end_time=1640995300,
                order_by=OrderBy.TIMESTAMP,
                order_direction=OrderDirection.DESC,
                limit=20,
                network="arbitrum",
            )

            assert result == ["swap"]
            mock_swaps_advanced.assert_called_with(
                pool="0xpool",
                caller="0xcaller",
                sender="0xsender",
                recipient="0xrecipient",
                protocol=Protocol.UNISWAP_V2,
                transaction_id="0xtx123",
                start_time=1640995200,
                end_time=1640995300,
                order_by=OrderBy.TIMESTAMP,
                order_direction=OrderDirection.DESC,
                limit=20,
                network="arbitrum",
            )

    @pytest.mark.anyio
    async def test_evm_wrapper_pools(self):
        """Test EVMWrapper.pools method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_pools") as mock_pools,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_pools.return_value = [{"pool": "0xpool123"}]
            mock_convert.return_value = ["pool"]

            result = await api.evm.pools(
                pool="0xpool", token="0xtoken", protocol=Protocol.UNISWAP_V3, limit=15, network="optimism"
            )

            assert result == ["pool"]
            mock_pools.assert_called_with(
                pool="0xpool", token="0xtoken", protocol=Protocol.UNISWAP_V3, limit=15, network="optimism"
            )

    @pytest.mark.anyio
    async def test_evm_wrapper_price_history(self):
        """Test EVMWrapper.price_history method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_price_history") as mock_price_history,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_price_history.return_value = [{"close": 1500.0}]
            mock_convert.return_value = ["ohlc"]

            result = await api.evm.price_history(
                token="0xtoken", interval=Interval.ONE_DAY, days=7, limit=168, network="base"
            )

            assert result == ["ohlc"]
            mock_price_history.assert_called_with(
                token="0xtoken", interval=Interval.ONE_DAY, days=7, limit=168, network="base"
            )

    @pytest.mark.anyio
    async def test_evm_wrapper_pool_history(self):
        """Test EVMWrapper.pool_history method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_pool_history") as mock_pool_history,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_pool_history.return_value = [{"volume": 1000.0}]
            mock_convert.return_value = ["ohlc"]

            result = await api.evm.pool_history(
                pool="0xpool", interval=Interval.FOUR_HOURS, days=3, limit=18, network="avalanche"
            )

            assert result == ["ohlc"]
            mock_pool_history.assert_called_with(
                pool="0xpool", interval=Interval.FOUR_HOURS, days=3, limit=18, network="avalanche"
            )

    @pytest.mark.anyio
    async def test_evm_wrapper_token_holders(self):
        """Test EVMWrapper.token_holders method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_evm_token_holders") as mock_token_holders,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_token_holders.return_value = [{"address": "0xholder"}]
            mock_convert.return_value = ["token_holder"]

            result = await api.evm.token_holders(contract="0xtoken", limit=50, network="bsc")

            assert result == ["token_holder"]
            mock_token_holders.assert_called_with(contract="0xtoken", limit=50, network="bsc")


class TestSVMWrapperMissingMethods:
    """Test SVMWrapper methods not covered by existing tests."""

    @pytest.mark.anyio
    async def test_svm_wrapper_transfers(self):
        """Test SVMWrapper.transfers method."""
        api = TokenAPI(api_key="test_key", auto_load_env=False)

        with (
            patch.object(api, "_svm_transfers") as mock_transfers,
            patch("thegraph_token_api.simple.convert_list_to_models") as mock_convert,
        ):
            mock_transfers.return_value = [{"signature": "sig123"}]
            mock_convert.return_value = ["solana_transfer"]

            result = await api.svm.transfers(
                signature="sig123",
                program_id=SolanaPrograms.TOKEN,
                mint="So11111111111111111111111111111111111111112",
                authority="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # pragma: allowlist secret
                source="4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A",  # pragma: allowlist secret
                destination="5dt8br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v360B",  # pragma: allowlist secret
                limit=25,
                network="solana",
            )

            assert result == ["solana_transfer"]
            mock_transfers.assert_called_with(
                signature="sig123",
                program_id=SolanaPrograms.TOKEN,
                mint="So11111111111111111111111111111111111111112",
                authority="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # pragma: allowlist secret
                source="4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A",  # pragma: allowlist secret
                destination="5dt8br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v360B",  # pragma: allowlist secret
                limit=25,
                network="solana",
            )
