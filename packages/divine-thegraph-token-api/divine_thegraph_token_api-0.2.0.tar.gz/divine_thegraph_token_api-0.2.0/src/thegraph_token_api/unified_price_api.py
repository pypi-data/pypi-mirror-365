"""
Unified Price API for multi-blockchain price calculation.

Provides a single interface for getting cryptocurrency prices across different
blockchains using DEX swap data with smart caching and statistical analysis.
"""

import time
from typing import Any

from .constants import (
    DEFAULT_PRICE_SETTINGS,
    SUPPORTED_CURRENCIES,
    get_currency_config,
    is_currency_supported,
)
from .price_utils import (
    PriceCalculator,
    PriceData,
    create_price_cache,
    extract_ethereum_price,
    extract_solana_price,
    validate_price_confidence,
)
from .types import Currency, NetworkId, OrderBy, OrderDirection, Protocol, SolanaNetworkId, SwapPrograms


class UnifiedPriceAPI:
    """
    Unified Price API supporting multiple blockchains.

    Example:
        ```python
        import anyio
        from thegraph_token_api import UnifiedPriceAPI, TokenAPI, Currency

        async def main():
            api = TokenAPI(api_key="your_key")
            oracle = UnifiedPriceAPI(api)

            # Simple usage with Currency enum
            eth_price = await oracle.get(Currency.ETH)
            sol_price = await oracle.get(Currency.SOL)

            # Enum-only interface for type safety
            pol_price = await oracle.get(Currency.POL)

            # With statistics
            eth_stats = await oracle.get(Currency.ETH, include_stats=True)
            print(f"ETH: ${eth_stats['price']:.2f} (confidence: {eth_stats['confidence']:.0%})")

        anyio.run(main)
        ```
    """

    def __init__(self, token_api: Any) -> None:
        """
        Initialize the Unified Price API.

        Args:
            token_api: TokenAPI instance with EVM and SVM clients
        """
        self.token_api = token_api
        self.calculator = PriceCalculator(DEFAULT_PRICE_SETTINGS)
        self._price_caches: dict[Currency, PriceData] = {}

    async def get(
        self, currency: Currency, *, include_stats: bool = False, force_refresh: bool = False
    ) -> float | dict[str, Any] | None:
        """
        Get cryptocurrency price in USD.

        Args:
            currency: Currency enum (Currency.ETH, Currency.SOL, Currency.POL)
            include_stats: If True, returns detailed statistics instead of just price
            force_refresh: If True, bypass cache and fetch fresh data

        Returns:
            float: Current price in USD (if include_stats=False)
            dict: Price with statistics (if include_stats=True)
            None: If no valid price data available

        Raises:
            ValueError: If currency is invalid or unsupported
        """
        # Validate Currency enum only - no string support
        if not isinstance(currency, Currency):
            msg = (
                f"Currency must be Currency enum, got {type(currency)}. Use Currency.ETH, Currency.SOL, or Currency.POL"
            )
            raise TypeError(msg)

        # Check cache first (unless force refresh)
        if not force_refresh and currency in self._price_caches:
            cached_data = self._price_caches[currency]
            if cached_data.is_fresh:
                return cached_data.stats if include_stats else cached_data.price

        # Get fresh price data
        try:
            price_stats = await self._fetch_price(currency)
            if not price_stats or not validate_price_confidence(price_stats):
                return None

            # Cache the result
            price = price_stats["price"]
            self._price_caches[currency] = create_price_cache(price, price_stats)

            return price_stats if include_stats else price

        except Exception:  # noqa: BLE001
            return None

    async def get_supported_currencies(self) -> list[Currency]:
        """
        Get list of supported currencies.

        Returns:
            List of supported Currency enums
        """
        return list(SUPPORTED_CURRENCIES.keys())

    async def is_supported(self, currency: Currency) -> bool:
        """
        Check if a currency is supported.

        Args:
            currency: Currency enum (Currency.ETH, Currency.SOL, Currency.POL)

        Returns:
            True if currency is supported
        """
        if not isinstance(currency, Currency):
            msg = (
                f"Currency must be Currency enum, got {type(currency)}. Use Currency.ETH, Currency.SOL, or Currency.POL"
            )
            raise TypeError(msg)
        return is_currency_supported(currency)

    async def clear_cache(self, currency: Currency | None = None) -> None:
        """
        Clear price cache.

        Args:
            currency: Specific Currency enum to clear, or None to clear all
        """
        if currency:
            if not isinstance(currency, Currency):
                msg = f"Currency must be Currency enum, got {type(currency)}. Use Currency.ETH, Currency.SOL, or Currency.POL"
                raise TypeError(msg)
            if currency in self._price_caches:
                del self._price_caches[currency]
        else:
            self._price_caches.clear()

    async def _fetch_price(self, currency: Currency) -> dict[str, Any] | None:
        """
        Fetch fresh price data for a currency.

        Args:
            currency: Currency enum

        Returns:
            Price statistics dictionary or None if failed
        """
        config = get_currency_config(currency)
        if not config:
            return None

        blockchain = config["blockchain"]

        if blockchain == "ethereum":
            return await self._fetch_ethereum_price(config)
        if blockchain == "polygon":
            return await self._fetch_polygon_price(config)
        if blockchain == "solana":
            return await self._fetch_solana_price(config)
        return None

    async def _fetch_evm_price(self, config: dict[str, Any], network_id: NetworkId) -> dict[str, Any] | None:
        """
        Generic EVM price fetching for Ethereum and Polygon networks.

        Args:
            config: Currency configuration dictionary
            network_id: Network to fetch from (MAINNET or MATIC)

        Returns:
            Price statistics or None if failed
        """
        token_config = config["token_config"]
        dex_config = config["dex_config"]
        base_pair = config["base_pair"]

        # Progressive retry with smart parameter adjustment
        prices = []
        swaps = []

        for attempt in range(1, 5):
            trades, minutes = self.calculator.progressive_retry_params(attempt)

            try:
                # Fetch swaps from EVM API
                swaps = await self._fetch_evm_swaps(network_id, dex_config.protocol, trades, minutes)

                if not swaps:
                    continue

                # Extract prices using EVM logic (works for both Ethereum and Polygon)
                token_pair = (token_config.address, base_pair.address)
                prices = self.calculator.extract_prices_from_swaps(swaps, token_pair, extract_ethereum_price)

                if len(prices) >= self.calculator.settings.min_sample_size:
                    break

            except Exception as e:  # noqa: BLE001
                # Log the exception for debugging but continue retry logic
                print(f"Warning: Price fetch attempt failed: {e}")
                continue
        else:
            return None

        # Calculate statistics
        return self.calculator.calculate_price_statistics(prices, len(swaps))

    async def _fetch_ethereum_price(self, config: dict[str, Any]) -> dict[str, Any] | None:
        """
        Fetch ETH price using Ethereum DEX swaps.

        Args:
            config: Currency configuration dictionary

        Returns:
            Price statistics or None if failed
        """
        return await self._fetch_evm_price(config, NetworkId.MAINNET)

    async def _fetch_polygon_price(self, config: dict[str, Any]) -> dict[str, Any] | None:
        """
        Fetch MATIC price using Polygon DEX swaps.

        Args:
            config: Currency configuration dictionary

        Returns:
            Price statistics or None if failed
        """
        return await self._fetch_evm_price(config, NetworkId.MATIC)

    # Backward compatibility methods for tests
    async def _fetch_ethereum_swaps(
        self, protocol: Protocol | str, limit: int, minutes_back: int
    ) -> list[dict[str, Any]]:
        """Backward compatibility wrapper for _fetch_evm_swaps."""
        return await self._fetch_evm_swaps(NetworkId.MAINNET, protocol, limit, minutes_back)

    async def _fetch_polygon_swaps(
        self, protocol: Protocol | str, limit: int, minutes_back: int
    ) -> list[dict[str, Any]]:
        """Backward compatibility wrapper for _fetch_evm_swaps."""
        return await self._fetch_evm_swaps(NetworkId.MATIC, protocol, limit, minutes_back)

    async def _fetch_solana_price(self, config: dict[str, Any]) -> dict[str, Any] | None:
        """
        Fetch SOL price using Solana DEX swaps.

        Args:
            config: Currency configuration dictionary

        Returns:
            Price statistics or None if failed
        """
        token_config = config["token_config"]
        dex_config = config["dex_config"]
        base_pair = config["base_pair"]

        # Progressive retry with smart parameter adjustment
        for attempt in range(1, 5):
            trades, minutes = self.calculator.progressive_retry_params(attempt)

            try:
                # Fetch swaps from SVM API
                swaps = await self._fetch_solana_swaps(
                    dex_config.protocol, token_config.address, base_pair.address, trades, minutes
                )

                if not swaps:
                    continue

                # Extract prices using blockchain-specific logic
                token_pair = (token_config.address, base_pair.address)
                prices = self.calculator.extract_prices_from_swaps(swaps, token_pair, extract_solana_price)

                if len(prices) >= self.calculator.settings.min_sample_size:
                    break

            except Exception as e:  # noqa: BLE001
                # Log the exception for debugging but continue retry logic
                print(f"Warning: Price fetch attempt failed: {e}")
                continue
        else:
            return None

        # Calculate statistics
        return self.calculator.calculate_price_statistics(prices, len(swaps))

    async def _fetch_evm_swaps(
        self, network_id: NetworkId, protocol: Protocol | str, limit: int, minutes_back: int
    ) -> list[dict[str, Any]]:
        """
        Generic EVM swap fetching for any supported network.

        Args:
            network_id: EVM network to fetch from (MAINNET, MATIC, etc.)
            protocol: DEX protocol to query (should be UNISWAP_V3 for reliability)
            limit: Maximum number of swaps
            minutes_back: Time window in minutes

        Returns:
            List of swap dictionaries
        """
        end_time = int(time.time())

        # Network-specific optimizations: Polygon uses no time filter for maximum data
        start_time = None if network_id == NetworkId.MATIC else end_time - (minutes_back * 60)

        # Use direct API client access for better control
        async with self.token_api._api.evm(network_id) as evm_client:
            try:
                # Build parameters dynamically
                params = {
                    "protocol": protocol,
                    "order_by": OrderBy.TIMESTAMP,
                    "order_direction": OrderDirection.DESC,
                    "limit": limit,
                }

                # Only add time filters if they're set (None means no filter)
                if start_time is not None:
                    params["start_time"] = start_time
                if end_time is not None:
                    params["end_time"] = end_time

                swaps_response = await evm_client.get_swaps(**params)

                # Extract data from response - handles various response formats
                swaps_data = []
                if hasattr(swaps_response, "data") and hasattr(swaps_response.data, "data"):
                    swaps_data = swaps_response.data.data
                elif hasattr(swaps_response, "data") and isinstance(swaps_response.data, list):
                    swaps_data = swaps_response.data
                elif isinstance(swaps_response, dict) and "data" in swaps_response:
                    # Handle dict response with 'data' key (common API response format)
                    swaps_data = swaps_response["data"]
                elif isinstance(swaps_response, list):
                    swaps_data = swaps_response

                # Convert to list of dicts for price extraction
                result = []
                for swap in swaps_data:
                    if hasattr(swap, "model_dump"):
                        result.append(swap.model_dump())
                    elif hasattr(swap, "__dict__"):
                        result.append(swap.__dict__)
                    elif isinstance(swap, dict):
                        result.append(swap)
                    else:
                        result.append({})

                return result

            except Exception:  # noqa: BLE001
                return []

    async def _fetch_solana_swaps(
        self, program_id: SwapPrograms | str, token_address: str, base_token_address: str, limit: int, minutes_back: int
    ) -> list[dict[str, Any]]:
        """
        Fetch Solana swaps for price calculation.

        Aligned with existing SOL price implementation in svm.py for consistency.

        Args:
            program_id: Solana swap program ID
            token_address: Token mint address (SOL)
            base_token_address: Base token mint address (USDC)
            limit: Maximum number of swaps
            minutes_back: Time window in minutes

        Returns:
            List of swap dictionaries
        """
        end_time = int(time.time())
        start_time = end_time - (minutes_back * 60)

        # Get SVM client - access client directly for consistency with svm.py
        async with self.token_api._api.svm(SolanaNetworkId.SOLANA) as svm_client:
            try:
                # Try with both input and output mints first (matches svm.py approach)
                swaps = await svm_client.get_swaps(
                    program_id=program_id,
                    input_mint=token_address,
                    output_mint=base_token_address,
                    start_time=start_time,
                    end_time=end_time,
                    order_by=OrderBy.TIMESTAMP,
                    order_direction=OrderDirection.DESC,
                    limit=limit,
                )

                # If no results, try without specifying mints (matches svm.py fallback)
                if not swaps or len(swaps) == 0:
                    swaps = await svm_client.get_swaps(
                        program_id=program_id,
                        start_time=start_time,
                        end_time=end_time,
                        order_by=OrderBy.TIMESTAMP,
                        order_direction=OrderDirection.DESC,
                        limit=limit,
                    )

                # Convert to list of dicts (matches svm.py conversion logic)
                if not swaps:
                    return []

                result: list[dict[str, Any]] = []
                for swap in swaps:
                    if hasattr(swap, "__dict__"):
                        result.append(swap.__dict__)
                    elif hasattr(swap, "items"):
                        result.append(dict(swap))
                    else:
                        result.append(swap if isinstance(swap, dict) else {})

                return result

            except Exception:  # noqa: BLE001
                return []
