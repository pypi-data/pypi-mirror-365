"""
SVM API Testing - Comprehensive coverage for svm.py
Tests all SVM (Solana) API methods with various parameter combinations including SOL price calculation.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from thegraph_token_api.svm import SVMTokenAPI
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

    @pytest.mark.asyncio
    async def test_get_swaps_edge_case_response(self):
        """Test get_swaps with edge case response format."""
        svm_api = SVMTokenAPI(SolanaNetworkId.SOLANA, "test_key")

        with patch.object(svm_api.manager, "get") as mock_get:
            # Mock response with non-dict data
            mock_get.return_value = MagicMock(data=[])  # Not a dict with "data" key

            result = await svm_api.get_swaps(SwapPrograms.JUPITER_V6)

            # Should return empty list for invalid format
            assert result == []

    @pytest.mark.asyncio
    async def test_get_swaps_nested_dict_response(self):
        """Test get_swaps with nested dict response format (line 258)."""
        svm_api = SVMTokenAPI(SolanaNetworkId.SOLANA, "test_key")

        with patch.object(svm_api.manager, "get") as mock_get:
            # Mock response with nested dict structure
            mock_swap_data = {
                "program_id": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
                "amm": "test_amm",
                "amm_pool": "test_pool",
                "user": "test_user",
                "input_mint": "So11111111111111111111111111111111111111112",
                "output_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "input_amount": 1000000000,
                "output_amount": 100000000,
                "timestamp": 1640995200,
                "signature": "test_signature",
            }

            # Mock the response object with nested data structure
            mock_response = MagicMock()
            mock_response.data = {"data": [mock_swap_data]}  # This triggers line 258
            mock_get.return_value = mock_response

            result = await svm_api.get_swaps(SwapPrograms.RAYDIUM)

            # Should return list with data from the nested structure
            assert len(result) == 1
            # The result should contain the expected data (may be dict or object depending on conversion)
            swap = result[0]
            # Test works with both dict and object formats
            if hasattr(swap, "program_id"):
                assert swap.program_id == "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
                assert swap.input_mint == "So11111111111111111111111111111111111111112"
            else:
                assert swap["program_id"] == "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
                assert swap["input_mint"] == "So11111111111111111111111111111111111111112"
