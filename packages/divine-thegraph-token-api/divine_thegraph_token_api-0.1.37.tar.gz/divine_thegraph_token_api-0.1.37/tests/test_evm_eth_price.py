"""
Test suite for EVM ETH price methods to achieve 100% coverage.

Tests the get_eth_price method and its helper functions.
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from thegraph_token_api.evm import EVMTokenAPI
from thegraph_token_api.price_utils import create_price_cache
from thegraph_token_api.types import NetworkId, Protocol


class TestEVMGetEthPrice:
    """Test get_eth_price method and helpers."""

    @pytest.mark.asyncio
    async def test_get_eth_price_basic(self):
        """Test basic ETH price fetching."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        # Mock the internal methods
        with (
            patch.object(evm_api, "_fetch_eth_usdc_swaps") as mock_fetch,
            patch.object(evm_api, "_extract_eth_prices") as mock_extract,
        ):
            # Mock swap data
            mock_fetch.return_value = [{"swap": "data"}] * 10
            mock_extract.return_value = [3500.0, 3501.0, 3499.0, 3502.0, 3498.0]

            price = await evm_api.get_eth_price()

            assert price is not None
            assert isinstance(price, float)
            assert 3498 <= price <= 3502  # Should be around median

    @pytest.mark.asyncio
    async def test_get_eth_price_with_cache(self):
        """Test ETH price with cache hit (lines 729-730)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        # Set up fresh cache
        mock_stats = {
            "price": 3500.0,
            "mean_price": 3500.0,
            "std_deviation": 10.0,
            "confidence": 0.9,
            "trades_analyzed": 50,
            "timestamp": time.time(),
        }
        evm_api._eth_price_cache = create_price_cache(3500.0, mock_stats)

        # Get price - should use cache
        price = await evm_api.get_eth_price()
        assert price == 3500.0

        # Get price with stats - should use cache
        stats = await evm_api.get_eth_price(include_stats=True)
        assert stats == mock_stats

    @pytest.mark.asyncio
    async def test_get_eth_price_retry_logic(self):
        """Test ETH price retry logic (lines 737-750)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        with (
            patch.object(evm_api, "_fetch_eth_usdc_swaps") as mock_fetch,
            patch.object(evm_api, "_extract_eth_prices") as mock_extract,
        ):
            # First 3 attempts return insufficient data, 4th succeeds
            mock_fetch.side_effect = [
                [{"swap": "data1"}],  # Attempt 1
                [{"swap": "data2"}],  # Attempt 2
                [{"swap": "data3"}],  # Attempt 3
                [{"swap": f"data{i}"} for i in range(10)],  # Attempt 4
            ]

            mock_extract.side_effect = [
                [3500.0],  # Only 1 price (insufficient)
                [3500.0, 3501.0],  # Only 2 prices (insufficient)
                [3500.0, 3501.0],  # Still insufficient
                [3500.0 + i for i in range(10)],  # Sufficient data
            ]

            price = await evm_api.get_eth_price()

            assert price is not None
            assert mock_fetch.call_count == 4
            assert mock_extract.call_count == 4

    @pytest.mark.asyncio
    async def test_get_eth_price_all_attempts_fail(self):
        """Test ETH price when all retry attempts fail (line 750)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        with (
            patch.object(evm_api, "_fetch_eth_usdc_swaps") as mock_fetch,
            patch.object(evm_api, "_extract_eth_prices") as mock_extract,
        ):
            # All attempts return insufficient data
            mock_fetch.return_value = [{"swap": "data"}]
            mock_extract.return_value = [3500.0]  # Only 1 price (insufficient)

            price = await evm_api.get_eth_price()

            assert price is None
            assert mock_fetch.call_count == 4  # Should try 4 times

    @pytest.mark.asyncio
    async def test_get_eth_price_no_stats(self):
        """Test ETH price when calculate_price_statistics returns None (lines 754-755)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        with (
            patch.object(evm_api, "_fetch_eth_usdc_swaps") as mock_fetch,
            patch.object(evm_api, "_extract_eth_prices") as mock_extract,
            patch("thegraph_token_api.evm.PriceCalculator") as mock_calc_class,
        ):
            mock_calc = MagicMock()
            mock_calc.progressive_retry_params.return_value = (100, 15)
            mock_calc.calculate_price_statistics.return_value = None  # No stats
            mock_calc_class.return_value = mock_calc

            mock_fetch.return_value = [{"swap": "data"}] * 10
            mock_extract.return_value = [3500.0] * 10

            price = await evm_api.get_eth_price()

            assert price is None

    @pytest.mark.asyncio
    async def test_get_eth_price_exception_handling(self):
        """Test ETH price exception handling (lines 763-764)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        with patch.object(evm_api, "_fetch_eth_usdc_swaps") as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")

            price = await evm_api.get_eth_price()

            assert price is None

    @pytest.mark.asyncio
    async def test_get_eth_price_empty_swaps_continue(self):
        """Test ETH price when swaps is empty (line 743)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        with (
            patch.object(evm_api, "_fetch_eth_usdc_swaps") as mock_fetch,
            patch.object(evm_api, "_extract_eth_prices") as mock_extract,
        ):
            # First attempts return empty swaps, last attempt returns data
            mock_fetch.side_effect = [
                [],  # Empty swaps - triggers continue
                [],  # Empty swaps - triggers continue
                [],  # Empty swaps - triggers continue
                [{"swap": "data"}] * 10,  # Valid data on last attempt
            ]

            mock_extract.return_value = [3500.0] * 5  # Valid prices

            price = await evm_api.get_eth_price()

            assert price is not None
            assert mock_fetch.call_count == 4
            # Extract should only be called once (for the non-empty swaps)
            assert mock_extract.call_count == 1

    @pytest.mark.asyncio
    async def test_fetch_eth_usdc_swaps(self):
        """Test _fetch_eth_usdc_swaps method (lines 768-793)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        # Mock swap object with __dict__
        mock_swap1 = MagicMock()
        mock_swap1.__dict__ = {"id": 1, "amount": "1000"}

        # Mock swap as dict
        mock_swap2 = {"id": 2, "amount": "2000"}

        # Mock swap with neither __dict__ nor dict format
        mock_swap3 = object()

        with patch.object(evm_api, "get_swaps") as mock_get_swaps:
            mock_get_swaps.return_value = [mock_swap1, mock_swap2, mock_swap3]

            result = await evm_api._fetch_eth_usdc_swaps(100, 60)

            assert len(result) == 3
            assert result[0] == {"id": 1, "amount": "1000"}
            assert result[1] == {"id": 2, "amount": "2000"}
            assert result[2] == {}  # Empty dict for unconvertible object

    @pytest.mark.asyncio
    async def test_fetch_eth_usdc_swaps_fallback(self):
        """Test _fetch_eth_usdc_swaps fallback when Uniswap V3 returns no results (lines 777-778)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        with patch.object(evm_api, "get_swaps") as mock_get_swaps:
            # First call (Uniswap V3) returns empty, second call returns data
            mock_get_swaps.side_effect = [
                [],  # Uniswap V3 returns empty
                [{"id": 1, "swap": "data"}],  # Fallback returns data
            ]

            result = await evm_api._fetch_eth_usdc_swaps(100, 60)

            assert len(result) == 1
            assert mock_get_swaps.call_count == 2

            # Check first call was with Uniswap V3
            first_call = mock_get_swaps.call_args_list[0]
            assert first_call.kwargs["protocol"] == Protocol.UNISWAP_V3

    @pytest.mark.asyncio
    async def test_fetch_eth_usdc_swaps_empty(self):
        """Test _fetch_eth_usdc_swaps when no swaps found (lines 781-782)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        with patch.object(evm_api, "get_swaps") as mock_get_swaps:
            mock_get_swaps.return_value = None

            result = await evm_api._fetch_eth_usdc_swaps(100, 60)

            assert result == []

    def test_extract_eth_prices(self):
        """Test _extract_eth_prices method (lines 797-850)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        swaps = [
            {
                "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},  # WETH
                "token1": {"address": "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af", "decimals": 6},  # USDC
                "amount0": "1000000000000000000",  # 1 ETH
                "amount1": "3500000000",  # 3500 USDC
            },
            {
                "token0": {"address": "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af", "decimals": 6},  # USDC
                "token1": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},  # WETH
                "amount0": "3600000000",  # 3600 USDC
                "amount1": "1000000000000000000",  # 1 ETH
            },
            # Invalid swap - different tokens
            {
                "token0": {"address": "0xInvalid", "decimals": 18},
                "token1": {"address": "0xAlsoInvalid", "decimals": 6},
                "amount0": "1000",
                "amount1": "2000",
            },
            # Zero amount swap
            {
                "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},
                "token1": {"address": "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af", "decimals": 6},
                "amount0": "0",
                "amount1": "3500000000",
            },
            # Out of range price
            {
                "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},
                "token1": {"address": "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af", "decimals": 6},
                "amount0": "1000000000000000000",  # 1 ETH
                "amount1": "50000000000",  # 50,000 USDC - out of range
            },
        ]

        prices = evm_api._extract_eth_prices(swaps)

        assert len(prices) == 2
        assert 3500 in prices
        assert 3600 in prices

    def test_extract_eth_prices_with_outliers(self):
        """Test _extract_eth_prices with outlier removal (lines 843-848)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        # Create 6 swaps with one outlier
        swaps = []
        for _i, price in enumerate([3500, 3501, 3502, 3503, 3504, 10000]):  # 10000 is outlier
            swaps.append(
                {
                    "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},
                    "token1": {"address": "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af", "decimals": 6},
                    "amount0": "1000000000000000000",  # 1 ETH
                    "amount1": str(price * 1000000),  # Price in USDC with 6 decimals
                }
            )

        prices = evm_api._extract_eth_prices(swaps)

        # Outlier should be removed by IQR method
        assert 10000 not in prices
        assert len(prices) == 5
        assert all(3500 <= p <= 3504 for p in prices)

    def test_extract_eth_prices_exception_handling(self):
        """Test _extract_eth_prices exception handling (lines 839-840)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        swaps = [
            # Valid swap
            {
                "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},
                "token1": {"address": "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af", "decimals": 6},
                "amount0": "1000000000000000000",
                "amount1": "3500000000",
            },
            # Swap that will cause ValueError
            {
                "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},
                "token1": {"address": "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af", "decimals": 6},
                "amount0": "invalid_number",
                "amount1": "3500000000",
            },
            # Swap missing required fields (KeyError)
            {
                "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"},
                # Missing token1
            },
        ]

        prices = evm_api._extract_eth_prices(swaps)

        # Should only have the valid swap price
        assert len(prices) == 1
        assert prices[0] == 3500.0

    def test_is_eth_usdc_pair(self):
        """Test _is_eth_usdc_pair method (lines 854-856)."""
        evm_api = EVMTokenAPI(NetworkId.MAINNET, "test_key")

        weth_addr = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        usdc_addr = "0xa0b86a33e7c473d00e05a7b8a4bcf1e50e93d1af"

        # Valid pair
        assert evm_api._is_eth_usdc_pair(weth_addr, usdc_addr, weth_addr, usdc_addr) is True
        assert evm_api._is_eth_usdc_pair(usdc_addr, weth_addr, weth_addr, usdc_addr) is True

        # Invalid pairs
        assert evm_api._is_eth_usdc_pair("0xother", usdc_addr, weth_addr, usdc_addr) is False
        assert evm_api._is_eth_usdc_pair(weth_addr, "0xother", weth_addr, usdc_addr) is False
        assert evm_api._is_eth_usdc_pair("0xother1", "0xother2", weth_addr, usdc_addr) is False
