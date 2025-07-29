"""
Test suite for the Unified Price API system.

Tests the Currency enum, UnifiedPriceAPI class, and all price calculation functionality
across different blockchains with proper mocking and error handling.
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from thegraph_token_api.constants import get_currency_config, is_currency_supported
from thegraph_token_api.price_utils import (
    PriceCalculator,
    create_price_cache,
    extract_ethereum_price,
    extract_solana_price,
    validate_price_confidence,
)
from thegraph_token_api.simple import TokenAPI
from thegraph_token_api.types import Currency, OrderBy, OrderDirection, Protocol, SwapPrograms
from thegraph_token_api.unified_price_api import UnifiedPriceAPI


class TestCurrencyEnum:
    """Test Currency enum functionality."""

    def test_currency_enum_values(self):
        """Test that Currency enum has expected values."""
        assert Currency.ETH == "ETH"
        assert Currency.SOL == "SOL"
        assert Currency.POL == "POL"
        assert str(Currency.ETH) == "ETH"
        assert str(Currency.SOL) == "SOL"
        assert str(Currency.POL) == "POL"

    def test_currency_enum_creation(self):
        """Test creating Currency enum from strings."""
        assert Currency("ETH") == Currency.ETH
        assert Currency("SOL") == Currency.SOL
        assert Currency("POL") == Currency.POL
        # Note: Currency enum is case-sensitive as designed

    def test_currency_enum_invalid(self):
        """Test that invalid currency strings raise ValueError."""
        with pytest.raises(ValueError):
            Currency("BTC")
        with pytest.raises(ValueError):
            Currency("INVALID")
        with pytest.raises(ValueError):
            Currency("")


class TestCurrencyConfig:
    """Test currency configuration functions."""

    def test_get_currency_config_enum(self):
        """Test getting config with Currency enum."""
        eth_config = get_currency_config(Currency.ETH)
        assert eth_config is not None
        assert eth_config["blockchain"] == "ethereum"
        assert "token_config" in eth_config
        assert "dex_config" in eth_config

        sol_config = get_currency_config(Currency.SOL)
        assert sol_config is not None
        assert sol_config["blockchain"] == "solana"

        pol_config = get_currency_config(Currency.POL)
        assert pol_config is not None
        assert pol_config["blockchain"] == "ethereum"

    def test_get_currency_config_string(self):
        """Test getting config with string (utility function still supports strings)."""
        eth_config = get_currency_config("ETH")
        assert eth_config is not None
        assert eth_config["blockchain"] == "ethereum"

        sol_config = get_currency_config("sol")  # Case insensitive
        assert sol_config is not None
        assert sol_config["blockchain"] == "solana"

        pol_config = get_currency_config("POL")
        assert pol_config is not None
        assert pol_config["blockchain"] == "ethereum"

    def test_get_currency_config_invalid(self):
        """Test getting config with invalid currency."""
        assert get_currency_config("BTC") is None
        assert get_currency_config("INVALID") is None

    def test_is_currency_supported_enum(self):
        """Test currency support check with enum."""
        assert is_currency_supported(Currency.ETH) is True
        assert is_currency_supported(Currency.SOL) is True
        assert is_currency_supported(Currency.POL) is True

    def test_is_currency_supported_string(self):
        """Test currency support check with string (utility function still supports strings)."""
        assert is_currency_supported("ETH") is True
        assert is_currency_supported("sol") is True  # Case insensitive
        assert is_currency_supported("POL") is True
        assert is_currency_supported("BTC") is False
        assert is_currency_supported("INVALID") is False


class TestPriceCalculator:
    """Test price calculation utilities."""

    def test_price_calculator_statistics(self):
        """Test price statistics calculation."""
        calculator = PriceCalculator()
        prices = [100.0, 102.0, 98.0, 101.0, 99.0]

        stats = calculator.calculate_price_statistics(prices)
        assert stats is not None
        assert stats["price"] == 100.0  # Median
        assert stats["mean_price"] == 100.0
        assert stats["trades_analyzed"] == 5
        assert 0 <= stats["confidence"] <= 1
        assert stats["min_price"] == 98.0
        assert stats["max_price"] == 102.0

    def test_price_calculator_insufficient_data(self):
        """Test price calculator with insufficient data."""
        calculator = PriceCalculator()
        prices = [100.0]  # Less than min_sample_size (3)

        stats = calculator.calculate_price_statistics(prices)
        assert stats is None

    def test_outlier_filtering_basic(self):
        """Test basic outlier filtering."""
        calculator = PriceCalculator()
        prices = [100.0, 101.0, 102.0, 15000.0, 99.0]  # 15000 is outlier (above 10000 max)

        filtered = calculator.filter_outliers_basic(prices)
        assert 15000.0 not in filtered
        assert len(filtered) == 4

    def test_outlier_filtering_iqr(self):
        """Test IQR outlier filtering."""
        calculator = PriceCalculator()
        prices = [100.0, 101.0, 102.0, 103.0, 104.0, 200.0]  # 200 is outlier

        filtered = calculator.filter_outliers_iqr(prices)
        assert 200.0 not in filtered

    def test_progressive_retry_params(self):
        """Test progressive retry parameter generation."""
        calculator = PriceCalculator()

        trades1, minutes1 = calculator.progressive_retry_params(1)
        trades2, minutes2 = calculator.progressive_retry_params(2)

        assert trades2 >= trades1
        assert minutes2 >= minutes1
        assert trades1 >= 100  # Base trades
        assert minutes1 >= 15  # Base minutes

    def test_outlier_filtering_iqr_insufficient_data(self):
        """Test IQR filtering with insufficient data."""
        calculator = PriceCalculator()
        prices = [100.0, 101.0, 102.0]  # Less than 5 data points

        filtered = calculator.filter_outliers_iqr(prices)
        assert filtered == prices  # Should return original prices

    def test_extract_prices_from_swaps(self):
        """Test generic price extraction from swaps."""
        calculator = PriceCalculator()
        swaps = [
            {"token0": "A", "token1": "B", "price": 100.0},
            {"token0": "A", "token1": "B", "price": 200.0},  # outlier
            {"token0": "A", "token1": "B", "price": 102.0},
        ]

        def mock_extractor(swap, token_pair):
            if swap.get("price") == 200.0:
                return 20000.0  # This will be filtered as outlier
            return swap.get("price")

        prices = calculator.extract_prices_from_swaps(swaps, ("A", "B"), mock_extractor)
        assert 20000.0 not in prices  # Outlier should be filtered
        assert 100.0 in prices
        assert 102.0 in prices

    def test_extract_prices_from_swaps_with_exceptions(self):
        """Test price extraction with extractor exceptions."""
        calculator = PriceCalculator()
        swaps = [
            {"valid": True, "price": 100.0},
            {"invalid": True},  # Will cause exception in extractor
            {"valid": True, "price": 101.0},
        ]

        def mock_extractor(swap, token_pair):
            if swap.get("invalid"):
                raise ValueError("Invalid swap")
            return swap.get("price")

        prices = calculator.extract_prices_from_swaps(swaps, ("A", "B"), mock_extractor)
        assert len(prices) == 2  # Only valid swaps should be included
        assert 100.0 in prices
        assert 101.0 in prices

    def test_validate_price_confidence_low(self):
        """Test price confidence validation with low confidence."""

        stats = {"confidence": 0.05, "trades_analyzed": 2}
        assert validate_price_confidence(stats) is False

    def test_validate_price_confidence_high(self):
        """Test price confidence validation with high confidence."""

        stats = {"confidence": 0.8, "trades_analyzed": 10}
        assert validate_price_confidence(stats) is True

    def test_extract_solana_price_valid(self):
        """Test Solana price extraction with valid data."""

        swap = {
            "input_mint": {"address": "So11111111111111111111111111111111111111112"},
            "output_mint": {"address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},
            "input_amount": 1000000000,  # 1 SOL
            "output_amount": 150000000,  # 150 USDC
        }
        token_pair = ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

        price = extract_solana_price(swap, token_pair)
        assert price == 150.0

    def test_extract_solana_price_invalid_pair(self):
        """Test Solana price extraction with invalid token pair."""

        swap = {
            "input_mint": {"address": "WRONG_MINT"},
            "output_mint": {"address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},
            "input_amount": 1000000000,
            "output_amount": 150000000,
        }
        token_pair = ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

        price = extract_solana_price(swap, token_pair)
        assert price is None

    def test_extract_solana_price_zero_amounts(self):
        """Test Solana price extraction with zero amounts."""

        swap = {
            "input_mint": {"address": "So11111111111111111111111111111111111111112"},
            "output_mint": {"address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},
            "input_amount": 0,
            "output_amount": 150000000,
        }
        token_pair = ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

        price = extract_solana_price(swap, token_pair)
        assert price is None

    def test_extract_solana_price_reverse(self):
        """Test Solana price extraction with reverse direction."""

        swap = {
            "input_mint": {"address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},  # USDC first
            "output_mint": {"address": "So11111111111111111111111111111111111111112"},  # SOL second
            "input_amount": 150000000,  # 150 USDC
            "output_amount": 1000000000,  # 1 SOL
        }
        token_pair = ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

        price = extract_solana_price(swap, token_pair)
        assert price == 150.0

    def test_extract_solana_price_out_of_range(self):
        """Test Solana price extraction with out of range price."""

        swap = {
            "input_mint": {"address": "So11111111111111111111111111111111111111112"},
            "output_mint": {"address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},
            "input_amount": 1000000000,  # 1 SOL
            "output_amount": 5000000000,  # 5000 USDC - out of range
        }
        token_pair = ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

        price = extract_solana_price(swap, token_pair)
        assert price is None

    def test_extract_ethereum_price_valid(self):
        """Test Ethereum price extraction with valid data."""

        swap = {
            "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},
            "token1": {"address": "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af", "decimals": 6},
            "amount0": "1000000000000000000",  # 1 ETH
            "amount1": "3500000000",  # 3500 USDC
        }
        token_pair = ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af")

        price = extract_ethereum_price(swap, token_pair)
        assert price == 3500.0

    def test_extract_ethereum_price_invalid_pair(self):
        """Test Ethereum price extraction with invalid token pair."""

        swap = {
            "token0": {"address": "0xWRONG", "decimals": 18},
            "token1": {"address": "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af", "decimals": 6},
            "amount0": "1000000000000000000",
            "amount1": "3500000000",
        }
        token_pair = ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af")

        price = extract_ethereum_price(swap, token_pair)
        assert price is None

    def test_extract_ethereum_price_zero_amount(self):
        """Test Ethereum price extraction with zero amount."""

        swap = {
            "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},
            "token1": {"address": "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af", "decimals": 6},
            "amount0": "0",  # Zero amount
            "amount1": "3500000000",
        }
        token_pair = ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af")

        price = extract_ethereum_price(swap, token_pair)
        assert price is None


class TestPriceData:
    """Test PriceData cache functionality."""

    def test_price_data_creation(self):
        """Test creating PriceData cache entry."""
        stats = {"price": 100.0, "mean_price": 100.0, "std_deviation": 1.0, "confidence": 0.8, "timestamp": time.time()}

        cache = create_price_cache(100.0, stats)
        assert cache.price == 100.0
        assert cache.stats == stats
        assert isinstance(cache.cached_at, float)

    def test_price_data_freshness_stable(self):
        """Test cache freshness for stable market."""
        stats = {
            "price": 100.0,
            "mean_price": 100.0,
            "std_deviation": 0.1,  # Low volatility
        }

        cache = create_price_cache(100.0, stats)
        assert cache.is_fresh is True  # Should be fresh immediately

    def test_price_data_freshness_volatile(self):
        """Test cache freshness for volatile market."""
        stats = {
            "price": 100.0,
            "mean_price": 100.0,
            "std_deviation": 10.0,  # High volatility
        }

        cache = create_price_cache(100.0, stats)
        assert cache.is_fresh is True  # Should be fresh immediately

        # Mock old timestamp
        cache.cached_at = time.time() - 120  # 2 minutes ago
        # Should be stale due to high volatility (TTL = 60s)
        assert cache.is_fresh is False


class TestUnifiedPriceAPI:
    """Test unified price oracle functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_token_api = MagicMock()
        self.mock_evm_client = AsyncMock()
        self.mock_svm_client = AsyncMock()

        # Configure mock API
        self.mock_token_api.evm.return_value = self.mock_evm_client
        self.mock_token_api.svm.return_value = self.mock_svm_client

        self.oracle = UnifiedPriceAPI(self.mock_token_api)

    @pytest.mark.asyncio
    async def test_unified_price_api_initialization(self):
        """Test Unified Price API initialization."""
        assert self.oracle.token_api == self.mock_token_api
        assert isinstance(self.oracle.calculator, PriceCalculator)
        assert isinstance(self.oracle._price_caches, dict)

    @pytest.mark.asyncio
    async def test_get_price_enum_input(self):
        """Test getting price with Currency enum input."""
        # Mock successful price calculation
        with patch.object(self.oracle, "_fetch_price") as mock_fetch:
            mock_fetch.return_value = {
                "price": 3500.0,
                "confidence": 0.9,
                "trades_analyzed": 10,
                "timestamp": time.time(),
            }

            price = await self.oracle.get(Currency.ETH)
            assert price == 3500.0
            mock_fetch.assert_called_once_with(Currency.ETH)

    @pytest.mark.asyncio
    async def test_get_price_non_enum_input(self):
        """Test getting price with non-enum input raises TypeError."""
        with pytest.raises(TypeError, match="Currency must be Currency enum"):
            await self.oracle.get("SOL")

    @pytest.mark.asyncio
    async def test_get_price_invalid_type(self):
        """Test getting price with invalid type."""
        with pytest.raises(TypeError, match="Currency must be Currency enum"):
            await self.oracle.get(123)

    @pytest.mark.asyncio
    async def test_get_price_with_stats(self):
        """Test getting price with statistics."""
        mock_stats = {
            "price": 3500.0,
            "mean_price": 3505.0,
            "std_deviation": 50.0,
            "confidence": 0.9,
            "trades_analyzed": 15,
            "timestamp": time.time(),
        }

        with patch.object(self.oracle, "_fetch_price") as mock_fetch:
            mock_fetch.return_value = mock_stats

            result = await self.oracle.get(Currency.ETH, include_stats=True)
            assert result == mock_stats
            assert result["price"] == 3500.0
            assert result["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_get_price_cache_hit(self):
        """Test price cache hit."""
        # First call
        with patch.object(self.oracle, "_fetch_price") as mock_fetch:
            mock_fetch.return_value = {
                "price": 3500.0,
                "confidence": 0.9,
                "trades_analyzed": 10,
                "timestamp": time.time(),
            }

            price1 = await self.oracle.get(Currency.ETH)
            assert price1 == 3500.0
            assert mock_fetch.call_count == 1

            # Second call should use cache
            price2 = await self.oracle.get(Currency.ETH)
            assert price2 == 3500.0
            assert mock_fetch.call_count == 1  # No additional call

    @pytest.mark.asyncio
    async def test_get_price_force_refresh(self):
        """Test force refresh bypasses cache."""
        with patch.object(self.oracle, "_fetch_price") as mock_fetch:
            mock_fetch.return_value = {
                "price": 3500.0,
                "confidence": 0.9,
                "trades_analyzed": 10,
                "timestamp": time.time(),
            }

            # First call
            await self.oracle.get(Currency.ETH)
            assert mock_fetch.call_count == 1

            # Force refresh should bypass cache
            await self.oracle.get(Currency.ETH, force_refresh=True)
            assert mock_fetch.call_count == 2

    @pytest.mark.asyncio
    async def test_get_price_fetch_failure(self):
        """Test price fetch failure returns None."""
        with patch.object(self.oracle, "_fetch_price") as mock_fetch:
            mock_fetch.return_value = None

            price = await self.oracle.get(Currency.ETH)
            assert price is None

    @pytest.mark.asyncio
    async def test_get_supported_currencies(self):
        """Test getting supported currencies."""
        currencies = await self.oracle.get_supported_currencies()
        assert isinstance(currencies, list)
        assert Currency.ETH in currencies
        assert Currency.SOL in currencies
        assert Currency.POL in currencies

    @pytest.mark.asyncio
    async def test_is_supported(self):
        """Test currency support checking."""
        assert await self.oracle.is_supported(Currency.ETH) is True
        assert await self.oracle.is_supported(Currency.SOL) is True
        assert await self.oracle.is_supported(Currency.POL) is True

    @pytest.mark.asyncio
    async def test_is_supported_invalid_type(self):
        """Test is_supported with invalid type."""
        with pytest.raises(TypeError, match="Currency must be Currency enum"):
            await self.oracle.is_supported("BTC")

    @pytest.mark.asyncio
    async def test_clear_cache_specific(self):
        """Test clearing specific currency cache."""
        # Add some cache entries
        self.oracle._price_caches[Currency.ETH] = create_price_cache(
            3500.0, {"price": 3500.0, "timestamp": time.time()}
        )
        self.oracle._price_caches[Currency.SOL] = create_price_cache(150.0, {"price": 150.0, "timestamp": time.time()})

        # Clear ETH cache
        await self.oracle.clear_cache(Currency.ETH)
        assert Currency.ETH not in self.oracle._price_caches
        assert Currency.SOL in self.oracle._price_caches

    @pytest.mark.asyncio
    async def test_clear_cache_all(self):
        """Test clearing all cache."""
        # Add some cache entries
        self.oracle._price_caches[Currency.ETH] = create_price_cache(
            3500.0, {"price": 3500.0, "timestamp": time.time()}
        )
        self.oracle._price_caches[Currency.SOL] = create_price_cache(150.0, {"price": 150.0, "timestamp": time.time()})

        # Clear all cache
        await self.oracle.clear_cache()
        assert len(self.oracle._price_caches) == 0

    @pytest.mark.asyncio
    async def test_clear_cache_invalid_type(self):
        """Test clear_cache with invalid type."""
        with pytest.raises(TypeError, match="Currency must be Currency enum"):
            await self.oracle.clear_cache("ETH")

    @pytest.mark.asyncio
    async def test_fetch_price_ethereum(self):
        """Test _fetch_price routing to Ethereum."""
        with patch.object(self.oracle, "_fetch_ethereum_price") as mock_fetch:
            mock_fetch.return_value = {"price": 3500.0}

            result = await self.oracle._fetch_price(Currency.ETH)
            assert result == {"price": 3500.0}
            mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_price_solana(self):
        """Test _fetch_price routing to Solana."""
        with patch.object(self.oracle, "_fetch_solana_price") as mock_fetch:
            mock_fetch.return_value = {"price": 150.0}

            result = await self.oracle._fetch_price(Currency.SOL)
            assert result == {"price": 150.0}
            mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_price_pol(self):
        """Test _fetch_price routing to POL (Ethereum)."""
        with patch.object(self.oracle, "_fetch_ethereum_price") as mock_fetch:
            mock_fetch.return_value = {"price": 0.5}

            result = await self.oracle._fetch_price(Currency.POL)
            assert result == {"price": 0.5}
            mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_price_invalid_config(self):
        """Test _fetch_price with invalid currency config."""
        # Mock get_currency_config to return None
        with patch("thegraph_token_api.unified_price_api.get_currency_config") as mock_config:
            mock_config.return_value = None

            result = await self.oracle._fetch_price(Currency.ETH)
            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_price_unknown_blockchain(self):
        """Test _fetch_price with unknown blockchain."""
        # Mock get_currency_config to return invalid blockchain
        with patch("thegraph_token_api.unified_price_api.get_currency_config") as mock_config:
            mock_config.return_value = {"blockchain": "unknown"}

            result = await self.oracle._fetch_price(Currency.ETH)
            assert result is None

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in price fetching."""
        # Mock exception in fetch
        with patch.object(self.oracle, "_fetch_price") as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")

            result = await self.oracle.get(Currency.ETH)
            assert result is None  # Should return None on error

    @pytest.mark.asyncio
    async def test_low_confidence_handling(self):
        """Test handling of low confidence price data."""
        with patch.object(self.oracle, "_fetch_price") as mock_fetch:
            # Mock low confidence data
            mock_fetch.return_value = {
                "price": 3500.0,
                "confidence": 0.05,  # Very low confidence
                "trades_analyzed": 1,  # Insufficient trades
                "timestamp": time.time(),
            }

            result = await self.oracle.get(Currency.ETH)
            assert result is None  # Should reject low confidence data

    @pytest.mark.anyio
    async def test_get_with_include_stats_true(self):
        """Test get method with include_stats=True returns detailed statistics."""
        # Mock successful responses from multiple sources
        with patch.object(self.oracle, "_fetch_price") as mock_fetch:
            mock_fetch.return_value = {
                "price": 2000.0,
                "confidence": 0.95,
                "trades_analyzed": 50,
                "timestamp": time.time(),
                "source_count": 3,
                "sources": ["ethereum_swaps", "polygon_swaps", "arbitrum_swaps"],
            }

            result = await self.oracle.get(Currency.ETH, include_stats=True)

            # Should return dictionary with statistics when include_stats=True
            assert isinstance(result, dict)
            assert "price" in result
            assert "confidence" in result
            assert "source_count" in result
            assert "sources" in result
            assert result["price"] == 2000.0
            assert result["confidence"] == 0.95

    @pytest.mark.anyio
    async def test_force_refresh_bypasses_cache(self):
        """Test that force_refresh=True bypasses cache."""
        with patch.object(self.oracle, "_fetch_price") as mock_fetch:
            mock_fetch.return_value = {
                "price": 2000.0,
                "confidence": 0.95,
                "trades_analyzed": 50,
                "timestamp": time.time(),
            }

            # First call to populate cache
            result1 = await self.oracle.get(Currency.ETH)
            assert result1 == 2000.0

            # Change mock to return different price
            mock_fetch.return_value = {
                "price": 2500.0,
                "confidence": 0.95,
                "trades_analyzed": 50,
                "timestamp": time.time(),
            }

            # Normal call should use cache
            result2 = await self.oracle.get(Currency.ETH)
            assert result2 == 2000.0  # Should use cached value

            # Force refresh should get new value
            result3 = await self.oracle.get(Currency.ETH, force_refresh=True)
            assert result3 == 2500.0  # Should get fresh value

    @pytest.mark.anyio
    async def test_cache_mechanism_basic(self):
        """Test basic cache mechanism."""
        currency = Currency.ETH

        # Mock successful price fetch
        with patch.object(self.oracle, "_fetch_price") as mock_fetch:
            mock_fetch.return_value = {
                "price": 2000.0,
                "confidence": 0.95,
                "trades_analyzed": 50,
                "timestamp": time.time(),
            }

            # First call should fetch and cache
            result1 = await self.oracle.get(currency)
            assert result1 == 2000.0

            # Second call should use cache (no new fetch)
            result2 = await self.oracle.get(currency)
            assert result2 == 2000.0

            # Should only have called the fetch method once
            assert mock_fetch.call_count == 1

    @pytest.mark.anyio
    async def test_price_cache_structure(self):
        """Test that price cache uses correct structure."""
        # The cache should use Currency enums as keys, not strings
        assert isinstance(self.oracle._price_caches, dict)

        # Add some mock data to test cache access
        mock_price_data = MagicMock()
        mock_price_data.is_fresh = True
        mock_price_data.price = 2000.0

        self.oracle._price_caches[Currency.ETH] = mock_price_data

        # Should be able to access by Currency enum
        assert Currency.ETH in self.oracle._price_caches
        assert self.oracle._price_caches[Currency.ETH].price == 2000.0


class TestUnifiedPriceAPIInternalMethods:
    """Test internal price fetching methods of UnifiedPriceAPI."""

    def setup_method(self):
        """Set up test fixtures."""

        self.token_api = TokenAPI(api_key="test_key", auto_load_env=False)
        self.oracle = UnifiedPriceAPI(self.token_api)

    @pytest.mark.anyio
    async def test_fetch_ethereum_price_with_config(self):
        """Test _fetch_ethereum_price internal method with proper config."""
        # Mock the configuration structure
        config = {
            "token_config": MagicMock(address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
            "dex_config": MagicMock(protocol=Protocol.UNISWAP_V3),
            "base_pair": MagicMock(address="0xA0b86a33E6417E97e54A0FE34e2eBfB3Cc88C7e1"),
        }

        # Mock the calculator methods
        with (
            patch.object(self.oracle.calculator, "progressive_retry_params", return_value=(100, 15)),
            patch.object(self.oracle, "_fetch_ethereum_swaps") as mock_fetch_swaps,
            patch.object(self.oracle.calculator, "extract_prices_from_swaps", return_value=[2000.0, 2001.0, 1999.0]),
            patch.object(
                self.oracle.calculator,
                "calculate_price_statistics",
                return_value={"price": 2000.0, "confidence": 0.95, "trades_analyzed": 3, "timestamp": time.time()},
            ),
        ):
            mock_fetch_swaps.return_value = [{"swap": "data1"}, {"swap": "data2"}, {"swap": "data3"}]

            result = await self.oracle._fetch_ethereum_price(config)

            assert result is not None
            assert result["price"] == 2000.0
            assert result["confidence"] == 0.95
            mock_fetch_swaps.assert_called_once()

    @pytest.mark.anyio
    async def test_fetch_ethereum_price_retry_logic(self):
        """Test _fetch_ethereum_price retry logic when swaps are insufficient."""
        config = {
            "token_config": MagicMock(address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
            "dex_config": MagicMock(protocol=Protocol.UNISWAP_V3),
            "base_pair": MagicMock(address="0xA0b86a33E6417E97e54A0FE34e2eBfB3Cc88C7e1"),
        }

        # Mock progressive retry params to return different values for different attempts
        retry_calls = [(50, 10), (100, 15), (200, 30), (400, 60)]

        with (
            patch.object(self.oracle.calculator, "progressive_retry_params", side_effect=retry_calls),
            patch.object(self.oracle, "_fetch_ethereum_swaps") as mock_fetch_swaps,
            patch.object(self.oracle.calculator, "extract_prices_from_swaps") as mock_extract,
            patch.object(
                self.oracle.calculator,
                "calculate_price_statistics",
                return_value={"price": 2000.0, "confidence": 0.95, "trades_analyzed": 10, "timestamp": time.time()},
            ),
        ):
            # First 3 attempts return insufficient data, 4th succeeds
            mock_fetch_swaps.side_effect = [
                [{"swap": "data1"}],  # Attempt 1: insufficient
                [{"swap": "data2"}],  # Attempt 2: insufficient
                [{"swap": "data3"}],  # Attempt 3: insufficient
                [{"swap": f"data{i}"} for i in range(10)],  # Attempt 4: sufficient
            ]

            # Mock extract_prices to return insufficient then sufficient data
            mock_extract.side_effect = [
                [2000.0],  # Attempt 1: 1 price (insufficient)
                [2000.0],  # Attempt 2: 1 price (insufficient)
                [2000.0],  # Attempt 3: 1 price (insufficient)
                [2000.0 + i for i in range(10)],  # Attempt 4: 10 prices (sufficient)
            ]

            # Mock minimum sample size
            self.oracle.calculator.settings = MagicMock(min_sample_size=5)

            result = await self.oracle._fetch_ethereum_price(config)

            assert result is not None
            assert mock_fetch_swaps.call_count == 4  # Should retry 4 times
            assert result["price"] == 2000.0

    @pytest.mark.anyio
    async def test_fetch_ethereum_price_all_attempts_fail(self):
        """Test _fetch_ethereum_price when all retry attempts fail."""
        config = {
            "token_config": MagicMock(address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
            "dex_config": MagicMock(protocol=Protocol.UNISWAP_V3),
            "base_pair": MagicMock(address="0xA0b86a33E6417E97e54A0FE34e2eBfB3Cc88C7e1"),
        }

        with (
            patch.object(self.oracle.calculator, "progressive_retry_params", return_value=(100, 15)),
            patch.object(self.oracle, "_fetch_ethereum_swaps", return_value=[]),
            patch.object(self.oracle.calculator, "extract_prices_from_swaps", return_value=[]),
        ):
            result = await self.oracle._fetch_ethereum_price(config)

            assert result is None

    @pytest.mark.anyio
    async def test_fetch_ethereum_price_exception_handling(self):
        """Test _fetch_ethereum_price exception handling during retry."""
        config = {
            "token_config": MagicMock(address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
            "dex_config": MagicMock(protocol=Protocol.UNISWAP_V3),
            "base_pair": MagicMock(address="0xA0b86a33E6417E97e54A0FE34e2eBfB3Cc88C7e1"),
        }

        with (
            patch.object(self.oracle.calculator, "progressive_retry_params", return_value=(100, 15)),
            patch.object(self.oracle, "_fetch_ethereum_swaps", side_effect=Exception("Network error")),
            patch("builtins.print") as mock_print,
        ):  # Capture print statements
            result = await self.oracle._fetch_ethereum_price(config)

            assert result is None
            # Should have printed warning messages
            assert mock_print.call_count >= 1
            assert "Warning: Price fetch attempt failed" in str(mock_print.call_args_list[0])

    @pytest.mark.anyio
    async def test_fetch_solana_price_with_config(self):
        """Test _fetch_solana_price internal method with proper config."""
        config = {
            "token_config": MagicMock(address="So11111111111111111111111111111111111111112"),
            "dex_config": MagicMock(protocol=SwapPrograms.RAYDIUM),
            "base_pair": MagicMock(address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        }

        with (
            patch.object(self.oracle.calculator, "progressive_retry_params", return_value=(100, 15)),
            patch.object(self.oracle, "_fetch_solana_swaps") as mock_fetch_swaps,
            patch.object(self.oracle.calculator, "extract_prices_from_swaps", return_value=[100.0, 101.0, 99.0]),
            patch.object(
                self.oracle.calculator,
                "calculate_price_statistics",
                return_value={"price": 100.0, "confidence": 0.95, "trades_analyzed": 3, "timestamp": time.time()},
            ),
        ):
            mock_fetch_swaps.return_value = [{"swap": "data1"}, {"swap": "data2"}, {"swap": "data3"}]

            result = await self.oracle._fetch_solana_price(config)

            assert result is not None
            assert result["price"] == 100.0
            assert result["confidence"] == 0.95
            mock_fetch_swaps.assert_called_once()

    @pytest.mark.anyio
    async def test_fetch_solana_price_retry_logic(self):
        """Test _fetch_solana_price retry logic when swaps are insufficient."""
        config = {
            "token_config": MagicMock(address="So11111111111111111111111111111111111111112"),
            "dex_config": MagicMock(protocol=SwapPrograms.RAYDIUM),
            "base_pair": MagicMock(address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        }

        with (
            patch.object(self.oracle.calculator, "progressive_retry_params", return_value=(100, 15)),
            patch.object(self.oracle, "_fetch_solana_swaps") as mock_fetch_swaps,
            patch.object(self.oracle.calculator, "extract_prices_from_swaps") as mock_extract,
            patch.object(
                self.oracle.calculator,
                "calculate_price_statistics",
                return_value={"price": 100.0, "confidence": 0.95, "trades_analyzed": 5, "timestamp": time.time()},
            ),
        ):
            # First attempt insufficient, second sufficient
            mock_fetch_swaps.side_effect = [
                [{"swap": "data1"}],  # Insufficient
                [{"swap": f"data{i}"} for i in range(5)],  # Sufficient
            ]

            mock_extract.side_effect = [
                [100.0],  # 1 price (insufficient)
                [100.0 + i for i in range(5)],  # 5 prices (sufficient)
            ]

            self.oracle.calculator.settings = MagicMock(min_sample_size=3)

            result = await self.oracle._fetch_solana_price(config)

            assert result is not None
            assert mock_fetch_swaps.call_count == 2

    @pytest.mark.anyio
    async def test_fetch_ethereum_swaps_method(self):
        """Test _fetch_ethereum_swaps internal method."""
        protocol = Protocol.UNISWAP_V3
        limit = 100
        minutes_back = 60

        # Mock time
        current_time = int(time.time())
        start_time = current_time - (minutes_back * 60)

        # Mock response with nested data structure
        mock_response = MagicMock()
        mock_response.data = MagicMock()
        mock_response.data.data = [
            {"token_amount": "1000000000000000000", "amount_usd": "2000.0"},
            {"token_amount": "500000000000000000", "amount_usd": "1000.0"},
        ]

        with patch.object(self.oracle.token_api._api, "evm") as mock_evm, patch("time.time", return_value=current_time):
            mock_evm_client = AsyncMock()
            mock_evm_client.get_swaps.return_value = mock_response
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_evm_client)
            mock_evm.return_value.__aexit__ = AsyncMock()

            result = await self.oracle._fetch_ethereum_swaps(protocol, limit, minutes_back)

            assert len(result) == 2
            assert result[0]["token_amount"] == "1000000000000000000"
            assert result[0]["amount_usd"] == "2000.0"

            # Verify correct API call
            mock_evm_client.get_swaps.assert_called_once_with(
                protocol=protocol,
                start_time=start_time,
                end_time=current_time,
                order_by=OrderBy.TIMESTAMP,
                order_direction=OrderDirection.DESC,
                limit=limit,
            )

    @pytest.mark.anyio
    async def test_fetch_ethereum_swaps_different_response_formats(self):
        """Test _fetch_ethereum_swaps with different response formats."""
        protocol = Protocol.UNISWAP_V2
        limit = 50
        minutes_back = 30

        # Test response with direct data list
        mock_response = MagicMock()
        mock_response.data = [{"swap": "data1"}, {"swap": "data2"}]

        with patch.object(self.oracle.token_api._api, "evm") as mock_evm:
            mock_evm_client = AsyncMock()
            mock_evm_client.get_swaps.return_value = mock_response
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_evm_client)
            mock_evm.return_value.__aexit__ = AsyncMock()

            result = await self.oracle._fetch_ethereum_swaps(protocol, limit, minutes_back)

            assert len(result) == 2
            assert result[0]["swap"] == "data1"

    @pytest.mark.anyio
    async def test_fetch_ethereum_swaps_model_dump_conversion(self):
        """Test _fetch_ethereum_swaps with model objects that have model_dump method."""
        protocol = Protocol.UNISWAP_V3
        limit = 50
        minutes_back = 30

        # Mock swap objects with model_dump method
        mock_swap1 = MagicMock()
        mock_swap1.model_dump.return_value = {"id": 1, "amount": "1000"}
        mock_swap2 = MagicMock()
        mock_swap2.model_dump.return_value = {"id": 2, "amount": "2000"}

        mock_response = MagicMock()
        mock_response.data = MagicMock()
        mock_response.data.data = [mock_swap1, mock_swap2]

        with patch.object(self.oracle.token_api._api, "evm") as mock_evm:
            mock_evm_client = AsyncMock()
            mock_evm_client.get_swaps.return_value = mock_response
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_evm_client)
            mock_evm.return_value.__aexit__ = AsyncMock()

            result = await self.oracle._fetch_ethereum_swaps(protocol, limit, minutes_back)

            assert len(result) == 2
            assert result[0] == {"id": 1, "amount": "1000"}
            assert result[1] == {"id": 2, "amount": "2000"}
            mock_swap1.model_dump.assert_called_once()
            mock_swap2.model_dump.assert_called_once()

    @pytest.mark.anyio
    async def test_fetch_ethereum_swaps_exception_handling(self):
        """Test _fetch_ethereum_swaps exception handling."""
        protocol = Protocol.UNISWAP_V3
        limit = 100
        minutes_back = 60

        with patch.object(self.oracle.token_api._api, "evm") as mock_evm:
            mock_evm_client = AsyncMock()
            mock_evm_client.get_swaps.side_effect = Exception("API Error")
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_evm_client)
            mock_evm.return_value.__aexit__ = AsyncMock()

            result = await self.oracle._fetch_ethereum_swaps(protocol, limit, minutes_back)

            assert result == []

    @pytest.mark.anyio
    async def test_fetch_solana_swaps_method(self):
        """Test _fetch_solana_swaps internal method."""
        program_id = SwapPrograms.RAYDIUM
        token_address = "So11111111111111111111111111111111111111112"
        base_token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        limit = 100
        minutes_back = 60

        # Mock time
        current_time = int(time.time())
        start_time = current_time - (minutes_back * 60)

        # Mock successful swap response
        mock_swap1 = MagicMock()
        mock_swap1.__dict__ = {"input_mint": token_address, "output_mint": base_token_address, "amount": 1000}
        mock_swap2 = MagicMock()
        mock_swap2.__dict__ = {"input_mint": token_address, "output_mint": base_token_address, "amount": 2000}

        with patch.object(self.oracle.token_api._api, "svm") as mock_svm, patch("time.time", return_value=current_time):
            mock_svm_client = AsyncMock()
            mock_svm_client.get_swaps.return_value = [mock_swap1, mock_swap2]
            mock_svm.return_value.__aenter__ = AsyncMock(return_value=mock_svm_client)
            mock_svm.return_value.__aexit__ = AsyncMock()

            result = await self.oracle._fetch_solana_swaps(
                program_id, token_address, base_token_address, limit, minutes_back
            )

            assert len(result) == 2
            assert result[0]["input_mint"] == token_address
            assert result[0]["amount"] == 1000

            # Verify correct API call
            mock_svm_client.get_swaps.assert_called_once_with(
                program_id=program_id,
                input_mint=token_address,
                output_mint=base_token_address,
                start_time=start_time,
                end_time=current_time,
                order_by=OrderBy.TIMESTAMP,
                order_direction=OrderDirection.DESC,
                limit=limit,
            )

    @pytest.mark.anyio
    async def test_fetch_solana_swaps_fallback_logic(self):
        """Test _fetch_solana_swaps fallback when specific mint search fails."""
        program_id = SwapPrograms.RAYDIUM
        token_address = "So11111111111111111111111111111111111111112"
        base_token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        limit = 100
        minutes_back = 60

        # Mock successful fallback response
        mock_swap = MagicMock()
        mock_swap.__dict__ = {"program_id": str(program_id), "amount": 1000}

        with patch.object(self.oracle.token_api._api, "svm") as mock_svm:
            mock_svm_client = AsyncMock()
            # First call (with mints) returns empty, second call (without mints) succeeds
            mock_svm_client.get_swaps.side_effect = [[], [mock_swap]]
            mock_svm.return_value.__aenter__ = AsyncMock(return_value=mock_svm_client)
            mock_svm.return_value.__aexit__ = AsyncMock()

            result = await self.oracle._fetch_solana_swaps(
                program_id, token_address, base_token_address, limit, minutes_back
            )

            assert len(result) == 1
            assert result[0]["program_id"] == str(program_id)

            # Should have called get_swaps twice (fallback logic)
            assert mock_svm_client.get_swaps.call_count == 2

    @pytest.mark.anyio
    async def test_fetch_solana_swaps_plain_dict_objects(self):
        """Test _fetch_solana_swaps with plain dict objects."""
        program_id = SwapPrograms.JUPITER_V6
        token_address = "So11111111111111111111111111111111111111112"
        base_token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        limit = 50
        minutes_back = 30

        # Test with plain dictionary objects
        mock_swap = {"key1": "value1", "key2": "value2"}

        with patch.object(self.oracle.token_api._api, "svm") as mock_svm:
            mock_svm_client = AsyncMock()
            mock_svm_client.get_swaps.return_value = [mock_swap]
            mock_svm.return_value.__aenter__ = AsyncMock(return_value=mock_svm_client)
            mock_svm.return_value.__aexit__ = AsyncMock()

            result = await self.oracle._fetch_solana_swaps(
                program_id, token_address, base_token_address, limit, minutes_back
            )

            assert len(result) == 1
            assert result[0] == {"key1": "value1", "key2": "value2"}

    @pytest.mark.anyio
    async def test_fetch_solana_swaps_fallback_empty_results(self):
        """Test _fetch_solana_swaps when all swaps are empty."""
        program_id = SwapPrograms.RAYDIUM
        token_address = "So11111111111111111111111111111111111111112"
        base_token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        limit = 50
        minutes_back = 30

        with patch.object(self.oracle.token_api._api, "svm") as mock_svm:
            mock_svm_client = AsyncMock()
            # Both calls return empty results
            mock_svm_client.get_swaps.side_effect = [[], []]
            mock_svm.return_value.__aenter__ = AsyncMock(return_value=mock_svm_client)
            mock_svm.return_value.__aexit__ = AsyncMock()

            result = await self.oracle._fetch_solana_swaps(
                program_id, token_address, base_token_address, limit, minutes_back
            )

            assert result == []
            # Should have tried both calls
            assert mock_svm_client.get_swaps.call_count == 2

    @pytest.mark.anyio
    async def test_fetch_ethereum_swaps_direct_list_response(self):
        """Test _fetch_ethereum_swaps when response is directly a list."""
        protocol = Protocol.UNISWAP_V3
        limit = 50
        minutes_back = 30

        # Mock response that is directly a list
        mock_response = [{"swap": "data1"}, {"swap": "data2"}]

        with patch.object(self.oracle.token_api._api, "evm") as mock_evm:
            mock_evm_client = AsyncMock()
            mock_evm_client.get_swaps.return_value = mock_response
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_evm_client)
            mock_evm.return_value.__aexit__ = AsyncMock()

            result = await self.oracle._fetch_ethereum_swaps(protocol, limit, minutes_back)

            assert len(result) == 2
            assert result[0]["swap"] == "data1"
            assert result[1]["swap"] == "data2"

    @pytest.mark.anyio
    async def test_fetch_ethereum_swaps_object_with_dict_attribute(self):
        """Test _fetch_ethereum_swaps with objects that have __dict__ attribute."""
        protocol = Protocol.UNISWAP_V2
        limit = 50
        minutes_back = 30

        # Mock objects with __dict__ attribute
        class SwapObject:
            def __init__(self, data):
                self.__dict__.update(data)

        swap1 = SwapObject({"id": 1, "amount": "1000"})
        swap2 = SwapObject({"id": 2, "amount": "2000"})

        mock_response = MagicMock()
        mock_response.data = MagicMock()
        mock_response.data.data = [swap1, swap2]

        with patch.object(self.oracle.token_api._api, "evm") as mock_evm:
            mock_evm_client = AsyncMock()
            mock_evm_client.get_swaps.return_value = mock_response
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_evm_client)
            mock_evm.return_value.__aexit__ = AsyncMock()

            result = await self.oracle._fetch_ethereum_swaps(protocol, limit, minutes_back)

            assert len(result) == 2
            assert result[0] == {"id": 1, "amount": "1000"}
            assert result[1] == {"id": 2, "amount": "2000"}

    @pytest.mark.anyio
    async def test_fetch_solana_swaps_exception_handling(self):
        """Test _fetch_solana_swaps exception handling."""
        program_id = SwapPrograms.RAYDIUM
        token_address = "So11111111111111111111111111111111111111112"
        base_token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        limit = 100
        minutes_back = 60

        with patch.object(self.oracle.token_api._api, "svm") as mock_svm:
            mock_svm_client = AsyncMock()
            mock_svm_client.get_swaps.side_effect = Exception("SVM API Error")
            mock_svm.return_value.__aenter__ = AsyncMock(return_value=mock_svm_client)
            mock_svm.return_value.__aexit__ = AsyncMock()

            result = await self.oracle._fetch_solana_swaps(
                program_id, token_address, base_token_address, limit, minutes_back
            )

            assert result == []

    @pytest.mark.anyio
    async def test_fetch_solana_price_empty_swaps_continue(self):
        """Test _fetch_solana_price handles empty swaps list (line 243)."""
        config = {
            "token_config": MagicMock(address="So11111111111111111111111111111111111111112"),
            "dex_config": MagicMock(protocol=SwapPrograms.JUPITER_V6),
            "base_pair": MagicMock(address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        }

        # Mock _fetch_solana_swaps to return empty list for first few attempts
        with patch.object(self.oracle, "_fetch_solana_swaps") as mock_fetch_swaps:
            mock_fetch_swaps.side_effect = [
                [],  # First attempt - empty (triggers continue)
                [],  # Second attempt - empty (triggers continue)
                [],  # Third attempt - empty (triggers continue)
                [],  # Fourth attempt - empty (triggers continue)
            ]

            result = await self.oracle._fetch_solana_price(config)

            # Should return None after all attempts with empty swaps
            assert result is None
            assert mock_fetch_swaps.call_count == 4

    @pytest.mark.anyio
    async def test_fetch_solana_price_exception_handling(self):
        """Test _fetch_solana_price exception handling (lines 252-257)."""
        config = {
            "token_config": MagicMock(address="So11111111111111111111111111111111111111112"),
            "dex_config": MagicMock(protocol=SwapPrograms.JUPITER_V6),
            "base_pair": MagicMock(address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
        }

        # Mock _fetch_solana_swaps to raise an exception
        with (
            patch.object(self.oracle, "_fetch_solana_swaps") as mock_fetch_swaps,
            patch("builtins.print") as mock_print,
        ):
            mock_fetch_swaps.side_effect = Exception("Network error")

            result = await self.oracle._fetch_solana_price(config)

            # Should return None after exception
            assert result is None
            # Should have attempted 4 times due to retry logic, each with exception
            assert mock_fetch_swaps.call_count == 4
            # Should have printed warning for each attempt
            assert mock_print.call_count >= 4
            assert "Warning: Price fetch attempt failed" in str(mock_print.call_args_list[0])

    @pytest.mark.anyio
    async def test_fetch_ethereum_swaps_empty_dict_fallback(self):
        """Test _fetch_ethereum_swaps empty dict fallback (line 313)."""
        with patch.object(self.oracle.token_api._api, "evm") as mock_evm:
            mock_evm_client = AsyncMock()
            mock_evm.return_value.__aenter__ = AsyncMock(return_value=mock_evm_client)
            mock_evm.return_value.__aexit__ = AsyncMock()

            # Mock response with swap that has no convertible attributes
            mock_swap = object()  # Object with no __dict__, model_dump, or dict conversion
            mock_response = MagicMock()
            mock_response.data = MagicMock()
            mock_response.data.data = [mock_swap]
            mock_evm_client.get_swaps.return_value = mock_response

            result = await self.oracle._fetch_ethereum_swaps(Protocol.UNISWAP_V3, 10, 60)

            # Should have one empty dict for the non-convertible swap
            assert len(result) == 1
            assert result[0] == {}

    @pytest.mark.anyio
    async def test_fetch_solana_swaps_fallback_conversion(self):
        """Test _fetch_solana_swaps fallback conversion (line 378)."""
        with patch.object(self.oracle.token_api._api, "svm") as mock_svm:
            mock_svm_client = AsyncMock()
            mock_svm.return_value.__aenter__ = AsyncMock(return_value=mock_svm_client)
            mock_svm.return_value.__aexit__ = AsyncMock()

            # Mock swap that's not a dict and has no __dict__ or items attributes
            mock_swap = object()  # Object with no conversion methods
            mock_svm_client.get_swaps.return_value = [mock_swap]

            result = await self.oracle._fetch_solana_swaps(
                SwapPrograms.JUPITER_V6,
                "So11111111111111111111111111111111111111112",
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                10,
                60,
            )

            # Should have one empty dict for the non-convertible swap
            assert len(result) == 1
            assert result[0] == {}
