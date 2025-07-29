"""
Reusable price calculation utilities for Unified Price API.

Contains statistical methods, caching logic, and common price calculation
functions that can be shared across different blockchain implementations.
"""

import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .constants import DEFAULT_PRICE_SETTINGS, PriceSettings


@dataclass
class PriceData:
    """Smart price data container with auto-expiring cache."""

    price: float
    stats: dict[str, Any]
    cached_at: float
    settings: PriceSettings = field(default_factory=lambda: DEFAULT_PRICE_SETTINGS)

    @property
    def is_fresh(self) -> bool:
        """Auto-expiring cache with smart TTL based on market volatility."""
        # Shorter cache for volatile periods, longer for stable periods
        volatility = self.stats.get("std_deviation", 0) / max(self.stats.get("mean_price", 1), 1)
        ttl = (
            self.settings.cache_ttl_volatile
            if volatility > self.settings.volatility_threshold
            else self.settings.cache_ttl_stable
        )
        return time.time() - self.cached_at < ttl


class PriceCalculator:
    """Reusable price calculation logic for different blockchain implementations."""

    def __init__(self, settings: PriceSettings = DEFAULT_PRICE_SETTINGS):
        """Initialize with price calculation settings."""
        self.settings = settings

    def calculate_price_statistics(
        self, prices: list[float], trades_analyzed: int | None = None
    ) -> dict[str, Any] | None:
        """
        Calculate comprehensive price statistics from a list of prices.

        Args:
            prices: List of price values
            trades_analyzed: Optional override for number of trades (defaults to len(prices))

        Returns:
            Dictionary with price statistics or None if insufficient data
        """
        if len(prices) < self.settings.min_sample_size:
            return None

        # Calculate core statistics
        price = statistics.median(prices)
        mean_price = statistics.mean(prices)
        std_deviation = statistics.stdev(prices) if len(prices) > 1 else 0

        return {
            "price": price,
            "mean_price": mean_price,
            "std_deviation": std_deviation,
            "min_price": min(prices),
            "max_price": max(prices),
            "trades_analyzed": trades_analyzed or len(prices),
            "confidence": min(len(prices) / 10, 1.0),  # 0-1 confidence score
            "timestamp": time.time(),
        }

    def filter_outliers_basic(self, prices: list[float]) -> list[float]:
        """
        Apply basic outlier filtering using sanity check thresholds.

        Args:
            prices: List of raw price values

        Returns:
            Filtered list of prices
        """
        min_price, max_price = self.settings.outlier_threshold
        return [p for p in prices if min_price <= p <= max_price]

    def filter_outliers_iqr(self, prices: list[float]) -> list[float]:
        """
        Apply IQR (Interquartile Range) method for outlier removal.

        Args:
            prices: List of price values (should already be basic filtered)

        Returns:
            List of prices with outliers removed
        """
        if len(prices) < 5:  # Need sufficient data for IQR
            return prices

        sorted_prices = sorted(prices)
        q1 = sorted_prices[len(sorted_prices) // 4]
        q3 = sorted_prices[3 * len(sorted_prices) // 4]
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        return [p for p in prices if lower_bound <= p <= upper_bound]

    def progressive_retry_params(self, attempt: int) -> tuple[int, int]:
        """
        Generate progressive retry parameters for trade sampling.

        Args:
            attempt: Retry attempt number (1-based)

        Returns:
            Tuple of (trades_limit, time_window_minutes)
        """
        multiplier = min(attempt, 5)  # Cap at 5x multiplier

        trades = min(self.settings.base_trades * multiplier, self.settings.max_trades)
        minutes = min(self.settings.base_minutes * multiplier, self.settings.max_minutes)

        return trades, minutes

    def extract_prices_from_swaps(
        self,
        swaps: list[dict[str, Any]],
        token_pair: tuple[str, str],
        price_extractor_func: Callable[[dict[str, Any], tuple[str, str]], float | None],
    ) -> list[float]:
        """
        Generic price extraction from swap data.

        Args:
            swaps: List of swap dictionaries
            token_pair: Tuple of (token1_address, token2_address) to filter for
            price_extractor_func: Function to extract price from individual swap

        Returns:
            List of extracted and filtered prices
        """
        raw_prices = []

        for swap in swaps:
            try:
                price = price_extractor_func(swap, token_pair)
                if price is not None:
                    raw_prices.append(price)
            except (ValueError, ZeroDivisionError, KeyError, TypeError):
                continue  # Skip invalid swaps

        # Apply outlier filtering
        basic_filtered = self.filter_outliers_basic(raw_prices)
        return self.filter_outliers_iqr(basic_filtered)


def create_price_cache(
    price: float, stats: dict[str, Any], settings: PriceSettings = DEFAULT_PRICE_SETTINGS
) -> PriceData:
    """
    Create a new price cache entry.

    Args:
        price: The calculated price
        stats: Price statistics dictionary
        settings: Price calculation settings

    Returns:
        PriceData cache entry
    """
    return PriceData(price=price, stats=stats, cached_at=time.time(), settings=settings)


def validate_price_confidence(stats: dict[str, Any], min_confidence: float = 0.1) -> bool:
    """
    Validate if price statistics meet minimum confidence requirements.

    Args:
        stats: Price statistics dictionary
        min_confidence: Minimum confidence threshold (0-1)

    Returns:
        True if price meets confidence requirements
    """
    confidence = stats.get("confidence", 0)
    trades_analyzed = stats.get("trades_analyzed", 0)

    return bool(confidence >= min_confidence and trades_analyzed >= DEFAULT_PRICE_SETTINGS.min_sample_size)


# ===== Blockchain-Specific Price Extractors =====


def extract_solana_price(swap: dict[str, Any], token_pair: tuple[str, str]) -> float | None:
    """
    Extract SOL price from Solana swap data.

    Aligned with the existing SOL price implementation in svm.py for consistency.

    Args:
        swap: Solana swap dictionary
        token_pair: Tuple of (sol_mint, usdc_mint)

    Returns:
        Price in USD or None if invalid
    """
    sol_mint, usdc_mint = token_pair

    # Get mint addresses (handle both dict and string formats) - matches svm.py implementation
    def get_mint_address(mint_data: dict[str, Any] | str | None) -> str:
        if isinstance(mint_data, dict):
            return str(mint_data.get("address", ""))
        return str(mint_data) if mint_data else ""

    input_mint = get_mint_address(swap.get("input_mint"))
    output_mint = get_mint_address(swap.get("output_mint"))

    # Only process SOL/USDC pairs - matches svm.py logic
    if {input_mint, output_mint} != {sol_mint, usdc_mint}:
        return None

    try:
        input_amount = float(swap.get("input_amount", 0))
        output_amount = float(swap.get("output_amount", 0))

        if input_amount <= 0 or output_amount <= 0:
            return None

        # Calculate price based on swap direction (matches svm.py calculation)
        if input_mint == sol_mint:  # SOL -> USDC
            price = (output_amount / 1e6) / (input_amount / 1e9)
        else:  # USDC -> SOL
            price = (input_amount / 1e6) / (output_amount / 1e9)

        # Basic sanity check (matches svm.py range)
        if 10 <= price <= 2000:
            return float(price)
        return None

    except (ValueError, ZeroDivisionError, KeyError, TypeError):
        return None


def extract_ethereum_price(swap: dict[str, Any], token_pair: tuple[str, str]) -> float | None:
    """
    Extract token price from Ethereum swap data.

    Supports ETH, POL, and other ERC-20 tokens paired with USDC on Uniswap V3.

    Args:
        swap: Ethereum swap dictionary
        token_pair: Tuple of (token_address, usdc_address)

    Returns:
        Price in USD or None if invalid
    """
    target_token_address, usdc_address = token_pair

    try:
        # Get token addresses from swap (handle different response formats)
        token0_data = swap.get("token0", {})
        token1_data = swap.get("token1", {})

        token0_addr = ""
        token1_addr = ""

        # Handle different data formats
        if isinstance(token0_data, dict):
            token0_addr = token0_data.get("address", "").lower()
        elif isinstance(token0_data, str):
            token0_addr = token0_data.lower()

        if isinstance(token1_data, dict):
            token1_addr = token1_data.get("address", "").lower()
        elif isinstance(token1_data, str):
            token1_addr = token1_data.lower()

        target_token_address = target_token_address.lower()
        usdc_address = usdc_address.lower()

        # Check if this is a target_token/USDC pair
        if {token0_addr, token1_addr} != {target_token_address, usdc_address}:
            return None

        # Get amounts and decimals
        amount0 = float(swap.get("amount0", 0))
        amount1 = float(swap.get("amount1", 0))

        # Get decimals with fallbacks
        token0_decimals = (
            int(token0_data.get("decimals", 18)) if isinstance(token0_data, dict) else 18
        )  # Default for most ERC-20 tokens
        token1_decimals = int(token1_data.get("decimals", 6)) if isinstance(token1_data, dict) else 6  # USDC decimals

        if amount0 == 0 or amount1 == 0:
            return None

        # Normalize amounts based on decimals
        amount0_normalized = abs(amount0) / (10**token0_decimals)
        amount1_normalized = abs(amount1) / (10**token1_decimals)

        # Calculate price based on which token is the target token
        if token0_addr == target_token_address:  # Target token is token0, USDC is token1
            price = amount1_normalized / amount0_normalized
        else:  # USDC is token0, target token is token1
            price = amount0_normalized / amount1_normalized

        # Basic sanity check - reasonable price range for crypto tokens
        if price <= 0 or price > 1000000:  # Very broad range to accommodate different tokens
            return None

        return float(price)

    except (ValueError, ZeroDivisionError, KeyError, TypeError, AttributeError):
        return None
