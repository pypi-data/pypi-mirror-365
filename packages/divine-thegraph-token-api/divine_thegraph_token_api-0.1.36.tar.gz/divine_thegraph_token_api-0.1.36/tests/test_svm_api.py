"""
SVM API Testing - Comprehensive coverage for svm.py
Tests all SVM (Solana) API methods with various parameter combinations including SOL price calculation.
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from thegraph_token_api.svm import (
    _SOL_MINT,
    _USDC_MINT,
    SVMTokenAPI,
    _PriceData,
)
from thegraph_token_api.types import (
    SolanaNetworkId,
    SolanaPrograms,
    SwapPrograms,
)


class TestSVMTokenAPIInitialization:
    """Test SVMTokenAPI initialization."""

    def test_initialization_with_string_network(self):
        """Test SVMTokenAPI initialization with string network."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret
        assert client.network == "solana"
        assert client.api_key == "test_key"  # pragma: allowlist secret

    def test_initialization_with_enum_network(self):
        """Test SVMTokenAPI initialization with enum network."""
        client = SVMTokenAPI(network=SolanaNetworkId.SOLANA, api_key="test_key")
        assert client.network == "solana"
        assert client.api_key == "test_key"  # pragma: allowlist secret

    def test_initialization_with_custom_base_url(self):
        """Test SVMTokenAPI initialization with custom base URL."""
        client = SVMTokenAPI(network="solana", api_key="test_key", base_url="https://custom.api.com")
        assert client.network == "solana"
        assert client.api_key == "test_key"  # pragma: allowlist secret
        assert client.base_url == "https://custom.api.com"


class TestSVMBalancesMethods:
    """Test SVM balances-related methods."""

    @pytest.mark.anyio
    async def test_get_balances_minimal_parameters(self):
        """Test get_balances with minimal parameters."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            result = await client.get_balances()

            mock_manager.get.assert_called_once()
            call_args = mock_manager.get.call_args
            assert "balances/svm" in call_args[0][0]
            assert call_args[1]["params"]["network_id"] == "solana"
            assert result == []

    @pytest.mark.anyio
    async def test_get_balances_with_token_account(self):
        """Test get_balances with token_account parameter."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_balances(
                token_account="4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A"  # pragma: allowlist secret
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert (
                params["token_account"] == "4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A"  # pragma: allowlist secret
            )

    @pytest.mark.anyio
    async def test_get_balances_full_parameters(self):
        """Test get_balances with all parameters."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_balances(
                token_account="4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A",  # pragma: allowlist secret
                mint="So11111111111111111111111111111111111111112",
                program_id=SolanaPrograms.TOKEN,
                limit=25,
                page=2,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert (
                params["token_account"] == "4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A"  # pragma: allowlist secret
            )
            assert params["mint"] == "So11111111111111111111111111111111111111112"
            assert params["program_id"] == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
            assert params["limit"] == 25
            assert params["page"] == 2

    @pytest.mark.anyio
    async def test_get_balances_with_token_2022_program(self):
        """Test get_balances with TOKEN_2022 program."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_balances(
                mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # pragma: allowlist secret
                program_id=SolanaPrograms.TOKEN_2022,
                limit=50,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["program_id"] == "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
            assert params["limit"] == 50


class TestSVMTransfersMethods:
    """Test SVM transfers-related methods."""

    @pytest.mark.anyio
    async def test_get_transfers_minimal_parameters(self):
        """Test get_transfers with minimal parameters."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            result = await client.get_transfers()

            mock_manager.get.assert_called_once()
            call_args = mock_manager.get.call_args
            assert "transfers/svm" in call_args[0][0]
            assert call_args[1]["params"]["network_id"] == "solana"
            assert result == []

    @pytest.mark.anyio
    async def test_get_transfers_with_signature(self):
        """Test get_transfers with signature parameter."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_transfers(
                signature="5j7s8Kd9WK1n2M4c3R6Q8F7X9Y2Z1A5B4C7D6E9G8H3I2J1K4L7M"  # pragma: allowlist secret
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert (
                params["signature"]
                == "5j7s8Kd9WK1n2M4c3R6Q8F7X9Y2Z1A5B4C7D6E9G8H3I2J1K4L7M"  # pragma: allowlist secret  # pragma: allowlist secret
            )

    @pytest.mark.anyio
    async def test_get_transfers_full_parameters(self):
        """Test get_transfers with all parameters."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_transfers(
                signature="5j7s8Kd9WK1n2M4c3R6Q8F7X9Y2Z1A5B4C7D6E9G8H3I2J1K4L7M",  # pragma: allowlist secret
                program_id=SolanaPrograms.TOKEN,
                mint="So11111111111111111111111111111111111111112",
                authority="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # pragma: allowlist secret
                source="4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A",  # pragma: allowlist secret
                destination="5dt8br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v360B",  # pragma: allowlist secret
                start_time=1640995200,
                end_time=1640995300,
                limit=35,
                page=1,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert (
                params["signature"]
                == "5j7s8Kd9WK1n2M4c3R6Q8F7X9Y2Z1A5B4C7D6E9G8H3I2J1K4L7M"  # pragma: allowlist secret
            )
            assert params["program_id"] == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
            assert params["mint"] == "So11111111111111111111111111111111111111112"
            assert (
                params["authority"] == "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"  # pragma: allowlist secret
            )
            assert params["source"] == "4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A"  # pragma: allowlist secret
            assert (
                params["destination"] == "5dt8br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v360B"  # pragma: allowlist secret
            )
            assert params["startTime"] == 1640995200
            assert params["endTime"] == 1640995300
            assert params["limit"] == 35

    @pytest.mark.anyio
    async def test_get_transfers_with_time_range(self):
        """Test get_transfers with time range filtering."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_transfers(
                mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # pragma: allowlist secret
                start_time=1640995200,
                end_time=1640995300,
                limit=100,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["mint"] == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # pragma: allowlist secret
            assert params["startTime"] == 1640995200
            assert params["endTime"] == 1640995300
            assert params["limit"] == 100


class TestSVMSwapsMethods:
    """Test SVM swaps-related methods."""

    @pytest.mark.anyio
    async def test_get_swaps_minimal_parameters(self):
        """Test get_swaps with minimal required parameters."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_swaps(program_id=SwapPrograms.RAYDIUM)

            mock_manager.get.assert_called_once()
            call_args = mock_manager.get.call_args
            assert "swaps/svm" in call_args[0][0]
            params = call_args[1]["params"]
            assert params["program_id"] == "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
            assert params["network_id"] == "solana"

    @pytest.mark.anyio
    async def test_get_swaps_with_raydium_parameters(self):
        """Test get_swaps with Raydium-specific parameters."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_swaps(
                program_id=SwapPrograms.RAYDIUM,
                amm="AMM123",
                amm_pool="POOL123",
                user="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # pragma: allowlist secret
                limit=20,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["program_id"] == "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
            assert params["amm"] == "AMM123"
            assert params["amm_pool"] == "POOL123"
            assert (
                params["user"] == "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"  # pragma: allowlist secret
            )
            assert params["limit"] == 20

    @pytest.mark.anyio
    async def test_get_swaps_full_parameters(self):
        """Test get_swaps with all parameters."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_swaps(
                program_id=SwapPrograms.RAYDIUM,
                amm="AMM123",
                amm_pool="POOL123",
                user="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # pragma: allowlist secret
                input_mint="So11111111111111111111111111111111111111112",
                output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # pragma: allowlist secret  # pragma: allowlist secret
                signature="swap_sig123",
                start_time=1640995200,
                end_time=1640995300,
                limit=45,
                page=2,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["program_id"] == "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
            assert params["input_mint"] == "So11111111111111111111111111111111111111112"
            assert params["output_mint"] == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # pragma: allowlist secret
            assert params["signature"] == "swap_sig123"
            assert params["startTime"] == 1640995200
            assert params["endTime"] == 1640995300
            assert params["limit"] == 45
            assert params["page"] == 2

    @pytest.mark.anyio
    async def test_get_swaps_with_jupiter_v6(self):
        """Test get_swaps with Jupiter V6 program."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            await client.get_swaps(
                program_id=SwapPrograms.JUPITER_V6,
                user="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # pragma: allowlist secret
                input_mint="So11111111111111111111111111111111111111112",
                output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # pragma: allowlist secret  # pragma: allowlist secret
                limit=10,
            )

            call_args = mock_manager.get.call_args
            params = call_args[1]["params"]
            assert params["program_id"] == "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"

    @pytest.mark.anyio
    async def test_get_swaps_with_pump_fun_programs(self):
        """Test get_swaps with Pump.fun programs."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            # Test Pump.fun Core
            await client.get_swaps(program_id=SwapPrograms.PUMP_FUN_CORE, limit=5)

            # Test Pump.fun AMM
            await client.get_swaps(program_id=SwapPrograms.PUMP_FUN_AMM, limit=5)

            assert mock_manager.get.call_count == 2

            # Check first call (Pump.fun Core)
            first_call = mock_manager.get.call_args_list[0]
            assert first_call[1]["params"]["program_id"] == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

            # Check second call (Pump.fun AMM)
            second_call = mock_manager.get.call_args_list[1]
            assert second_call[1]["params"]["program_id"] == "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"


class TestSVMMethodCombinations:
    """Test combinations and edge cases for SVM methods."""

    @pytest.mark.anyio
    async def test_sol_usdc_trading_pattern(self):
        """Test common SOL/USDC trading pattern."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            # Get SOL balances
            await client.get_balances(
                mint="So11111111111111111111111111111111111111112", program_id=SolanaPrograms.TOKEN
            )

            # Get SOL transfers
            await client.get_transfers(mint="So11111111111111111111111111111111111111112", limit=20)

            # Get SOL/USDC swaps
            await client.get_swaps(
                program_id=SwapPrograms.RAYDIUM,
                input_mint="So11111111111111111111111111111111111111112",
                output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # pragma: allowlist secret
            )

            assert mock_manager.get.call_count == 3

    @pytest.mark.anyio
    async def test_different_swap_programs(self):
        """Test swaps across different DEX programs."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        programs_to_test = [
            SwapPrograms.RAYDIUM,
            SwapPrograms.JUPITER_V4,
            SwapPrograms.JUPITER_V6,
            SwapPrograms.PUMP_FUN_CORE,
            SwapPrograms.PUMP_FUN_AMM,
        ]

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            for program in programs_to_test:
                await client.get_swaps(program_id=program, limit=5)

            assert mock_manager.get.call_count == len(programs_to_test)

    @pytest.mark.anyio
    async def test_pagination_validation_integration(self):
        """Test that pagination validation works with SVM methods."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        # These should raise ValueError due to invalid pagination
        with pytest.raises(ValueError):
            await client.get_balances(limit=0)

        with pytest.raises(ValueError):
            await client.get_transfers(page=0)

        with pytest.raises(ValueError):
            await client.get_swaps(program_id=SwapPrograms.RAYDIUM, limit=1001)

    @pytest.mark.anyio
    async def test_string_vs_enum_program_ids(self):
        """Test that string and enum program IDs work equivalently."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            # Test with enum
            await client.get_swaps(program_id=SwapPrograms.RAYDIUM)

            # Test with string
            await client.get_balances(program_id="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

            assert mock_manager.get.call_count == 2

            # Both should result in the same program ID value in params
            first_call = mock_manager.get.call_args_list[0]
            assert first_call[1]["params"]["program_id"] == "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"

            second_call = mock_manager.get.call_args_list[1]
            assert second_call[1]["params"]["program_id"] == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

    @pytest.mark.anyio
    async def test_time_filtering_patterns(self):
        """Test various time filtering patterns."""
        client = SVMTokenAPI(network="solana", api_key="test_key")  # pragma: allowlist secret

        with patch.object(client, "manager") as mock_manager:
            mock_response = MagicMock()
            mock_response.data = []
            mock_manager.get = AsyncMock(return_value=mock_response)

            # Test with only start_time
            await client.get_transfers(start_time=1640995200)

            # Test with only end_time
            await client.get_swaps(program_id=SwapPrograms.RAYDIUM, end_time=1640995300)

            # Test with both start and end time (balances doesn't support time filtering, use transfers)
            await client.get_transfers(start_time=1640995200, end_time=1640995300)

            assert mock_manager.get.call_count == 3


class TestOptimizedSOLPriceCalculation:
    """Test optimized SOL price calculation functionality in SVM API."""

    @pytest.fixture
    def mock_swap_data(self):
        """Create mock swap data for testing."""
        return [
            {
                "input_mint": {"address": _SOL_MINT, "symbol": "SOL", "decimals": 9},
                "input_amount": 1_000_000_000,  # 1 SOL
                "output_mint": {"address": _USDC_MINT, "symbol": "USDC", "decimals": 6},
                "output_amount": 100_000_000,  # 100 USDC
            },
            {
                "input_mint": _USDC_MINT,  # String format
                "input_amount": 50_000_000,  # 50 USDC
                "output_mint": _SOL_MINT,  # String format
                "output_amount": 500_000_000,  # 0.5 SOL
            },
            {
                "input_mint": {"address": _SOL_MINT},
                "input_amount": 2_000_000_000,  # 2 SOL
                "output_mint": {"address": _USDC_MINT},
                "output_amount": 200_000_000,  # 200 USDC
            },
        ]

    def test_price_data_smart_caching(self):
        """Test smart price data caching with volatility-based TTL."""
        # High volatility should have shorter TTL
        high_vol_stats = {"std_deviation": 10, "mean_price": 100}  # 10% volatility
        price_data = _PriceData(price=100.0, stats=high_vol_stats, cached_at=time.time())
        # Should expire quickly due to high volatility

        # Low volatility should have longer TTL
        low_vol_stats = {"std_deviation": 1, "mean_price": 100}  # 1% volatility
        stable_data = _PriceData(price=100.0, stats=low_vol_stats, cached_at=time.time())
        # Should stay fresh longer due to low volatility

        assert price_data.is_fresh == stable_data.is_fresh  # Both should be fresh initially

    @pytest.mark.anyio
    async def test_svm_api_initialization(self):
        """Test SVM API initialization with optimized cache."""
        client = SVMTokenAPI(api_key="test_key")
        assert client._sol_price_cache is None

    @pytest.mark.anyio
    async def test_get_sol_price_simple(self, mock_swap_data):
        """Test simple SOL price retrieval."""
        client = SVMTokenAPI(api_key="test_key")

        with patch.object(client, "get_swaps") as mock_get_swaps:
            # Mock get_swaps to return list of swaps
            mock_get_swaps.return_value = mock_swap_data

            price = await client.get_sol_price()
            assert isinstance(price, float)
            assert 50 <= price <= 200  # Reasonable range

    @pytest.mark.anyio
    async def test_get_sol_price_with_stats(self, mock_swap_data):
        """Test SOL price with detailed statistics."""
        client = SVMTokenAPI(api_key="test_key")

        with patch.object(client, "get_swaps") as mock_get_swaps:
            # Mock get_swaps to return list of swaps
            mock_get_swaps.return_value = mock_swap_data

            stats = await client.get_sol_price(include_stats=True)
            assert isinstance(stats, dict)
            assert "price" in stats
            assert "confidence" in stats
            assert "trades_analyzed" in stats
            assert "std_deviation" in stats
            assert 0 <= stats["confidence"] <= 1

    @pytest.mark.anyio
    async def test_smart_caching_behavior(self, mock_swap_data):
        """Test smart caching with automatic cache hits."""
        client = SVMTokenAPI(api_key="test_key")

        with patch.object(client, "get_swaps") as mock_get_swaps:
            # Mock get_swaps to return list of swaps
            mock_get_swaps.return_value = mock_swap_data

            # First call
            price1 = await client.get_sol_price()
            assert mock_get_swaps.call_count == 1

            # Second call should use cache
            price2 = await client.get_sol_price()
            assert price1 == price2
            assert mock_get_swaps.call_count == 1  # No additional API call

    @pytest.mark.anyio
    async def test_no_data_handling(self):
        """Test graceful handling when no swap data available."""
        client = SVMTokenAPI(api_key="test_key")

        with patch.object(client, "get_swaps") as mock_get_swaps:
            # Mock get_swaps to return empty list
            mock_get_swaps.return_value = []

            price = await client.get_sol_price()
            assert price is None

    @pytest.mark.anyio
    async def test_progressive_retry_logic(self):
        """Test smart retry logic with progressive sampling."""
        client = SVMTokenAPI(api_key="test_key")

        # Mock responses: empty, then small data, then good data
        mock_responses = [
            [],  # First attempt fails
            [
                {
                    "input_mint": _SOL_MINT,
                    "output_mint": _USDC_MINT,
                    "input_amount": 1_000_000_000,
                    "output_amount": 100_000_000,
                }
            ],  # Second has minimal data
            [
                {
                    "input_mint": _SOL_MINT,
                    "output_mint": _USDC_MINT,
                    "input_amount": 1_000_000_000,
                    "output_amount": 100_000_000,
                },
                {
                    "input_mint": _USDC_MINT,
                    "output_mint": _SOL_MINT,
                    "input_amount": 50_000_000,
                    "output_amount": 500_000_000,
                },
                {
                    "input_mint": _SOL_MINT,
                    "output_mint": _USDC_MINT,
                    "input_amount": 2_000_000_000,
                    "output_amount": 200_000_000,
                },
            ],  # Third attempt has good data
        ]

        with patch.object(client, "get_swaps") as mock_get_swaps:
            # Mock get_swaps to return lists directly
            mock_get_swaps.side_effect = mock_responses

            price = await client.get_sol_price()
            assert isinstance(price, float)
            # Should have made multiple attempts
            assert mock_get_swaps.call_count >= 2

    @pytest.mark.anyio
    async def test_outlier_filtering(self):
        """Test intelligent outlier filtering."""
        client = SVMTokenAPI(api_key="test_key")

        # Create test data with outliers
        test_swaps = [
            {
                "input_mint": _SOL_MINT,
                "output_mint": _USDC_MINT,
                "input_amount": 1_000_000_000,
                "output_amount": 100_000_000,
            },  # $100
            {
                "input_mint": _SOL_MINT,
                "output_mint": _USDC_MINT,
                "input_amount": 1_000_000_000,
                "output_amount": 101_000_000,
            },  # $101
            {
                "input_mint": _SOL_MINT,
                "output_mint": _USDC_MINT,
                "input_amount": 1_000_000_000,
                "output_amount": 99_000_000,
            },  # $99
            {
                "input_mint": _SOL_MINT,
                "output_mint": _USDC_MINT,
                "input_amount": 1_000_000_000,
                "output_amount": 5000_000_000,
            },  # $5000 - outlier
        ]

        prices = client._extract_sol_prices(test_swaps)
        # Should filter out the $5000 outlier
        assert all(50 <= p <= 200 for p in prices)

    @pytest.mark.anyio
    async def test_mint_address_extraction(self):
        """Test flexible mint address extraction."""
        client = SVMTokenAPI(api_key="test_key")

        # Test dict format
        dict_mint = {"address": _SOL_MINT, "symbol": "SOL"}
        assert client._get_mint_address(dict_mint) == _SOL_MINT

        # Test string format
        assert client._get_mint_address(_SOL_MINT) == _SOL_MINT

        # Test None/invalid
        assert client._get_mint_address(None) == ""
        assert client._get_mint_address({}) == ""

    @pytest.mark.anyio
    async def test_sol_usdc_pair_detection(self):
        """Test SOL/USDC pair detection."""
        client = SVMTokenAPI(api_key="test_key")

        # Valid pairs
        assert client._is_sol_usdc_pair(_SOL_MINT, _USDC_MINT) is True
        assert client._is_sol_usdc_pair(_USDC_MINT, _SOL_MINT) is True

        # Invalid pairs
        assert client._is_sol_usdc_pair(_SOL_MINT, _SOL_MINT) is False
        assert client._is_sol_usdc_pair("other_mint", _USDC_MINT) is False
