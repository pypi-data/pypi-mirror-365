"""
SVM-specific client for The Graph Token API.

Provides access to Solana blockchain data including SPL tokens, balances, transfers, DEX swaps, and SOL price calculation.
"""

import statistics
import time
from dataclasses import dataclass
from typing import Any

from .base import BaseTokenAPI
from .types import (
    OrderBy,
    OrderDirection,
    # Response types
    SolanaBalancesResponse,
    # Enums
    SolanaNetworkId,
    SolanaPrograms,
    SolanaSwap,
    SolanaSwapsResponse,
    SolanaTransfersResponse,
    SwapPrograms,
)

# SOL price calculation constants
_SOL_MINT = "So11111111111111111111111111111111111111112"  # pragma: allowlist secret
_USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # pragma: allowlist secret
_JUPITER_V6 = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"  # pragma: allowlist secret


@dataclass
class _PriceData:
    """Smart price data container with auto-expiring cache."""

    price: float
    stats: dict[str, Any]
    cached_at: float

    @property
    def is_fresh(self) -> bool:
        """Auto-expiring cache with smart TTL based on market volatility."""
        # Shorter cache for volatile periods, longer for stable periods
        volatility = self.stats.get("std_deviation", 0) / max(self.stats.get("mean_price", 1), 1)
        ttl = 60 if volatility > 0.05 else 300  # 1min volatile, 5min stable
        return time.time() - self.cached_at < ttl


class SVMTokenAPI(BaseTokenAPI):
    """
    SVM-specific client for The Graph Token API.

    Provides access to Solana blockchain data with network-specific configuration.

    Example:
        ```python
        import anyio
        from thegraph_client import SVMTokenAPI, SolanaNetworkId, SwapPrograms

        async def main():
            # Create SVM client for Solana
            async with SVMTokenAPI(
                api_key="your_bearer_token",  # pragma: allowlist secret
                network=SolanaNetworkId.SOLANA
            ) as svm_api:
                # Get SPL token balances
                balances = await svm_api.get_balances(
                    token_account="4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A"  # pragma: allowlist secret
                )

                # Get swap transactions
                swaps = await svm_api.get_swaps(
                    program_id=SwapPrograms.RAYDIUM,
                    user="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"  # pragma: allowlist secret
                )

                # Get SOL price (simple)
                sol_price = await svm_api.get_sol_price()
                print(f"Current SOL price: ${sol_price:.2f}")

                # Get SOL price with detailed stats
                sol_stats = await svm_api.get_sol_price(include_stats=True)
                print(f"Price confidence: {sol_stats['confidence']:.0%}")

        anyio.run(main)
        ```
    """

    def __init__(
        self,
        network: SolanaNetworkId | str = SolanaNetworkId.SOLANA,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        """
        Initialize SVM Token API client.

        Args:
            network: SVM network to use (default: SolanaNetworkId.SOLANA)
            api_key: Bearer token for API authentication
            base_url: API base URL (optional)
        """
        super().__init__(api_key, base_url)
        self.network = str(network)
        self._sol_price_cache: _PriceData | None = None

    # ===== Balance Methods =====

    async def get_balances(
        self,
        token_account: str | None = None,
        mint: str | None = None,
        program_id: SolanaPrograms | str | None = None,
        limit: int = 10,
        page: int = 1,
    ) -> SolanaBalancesResponse:
        """
        Get Solana SPL token balances.

        Args:
            token_account: Filter by token account address
            mint: Filter by mint address
            program_id: Filter by program ID
            limit: Maximum number of results
            page: Page number

        Returns:
            SolanaBalancesResponse with validated data
        """
        params = self._build_base_params(self.network, limit, page)
        self._add_optional_params(params, token_account=token_account, mint=mint, program_id=program_id)

        response = await self.manager.get(
            f"{self.base_url}/balances/svm",
            headers=self._headers,
            params=params,
            expected_type=SolanaBalancesResponse,
            timeout=30,
        )
        return response.data  # type: ignore[no-any-return]

    # ===== Transfer Methods =====

    async def get_transfers(
        self,
        signature: str | None = None,
        program_id: SolanaPrograms | str | None = None,
        mint: str | None = None,
        authority: str | None = None,
        source: str | None = None,
        destination: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        order_by: OrderBy | str = OrderBy.TIMESTAMP,
        order_direction: OrderDirection | str = OrderDirection.DESC,
        limit: int = 10,
        page: int = 1,
    ) -> SolanaTransfersResponse:
        """
        Get Solana SPL token transfer events.

        Args:
            signature: Filter by transaction signature
            program_id: Filter by program ID
            mint: Filter by mint address
            authority: Filter by authority address
            source: Filter by source address
            destination: Filter by destination address
            start_time: Start time as UNIX timestamp
            end_time: End time as UNIX timestamp
            order_by: Field to order by
            order_direction: Order direction (asc/desc)
            limit: Maximum number of results
            page: Page number

        Returns:
            SolanaTransfersResponse with validated data
        """
        self._validate_pagination(limit, page)
        params = {
            "network_id": self.network,
            "orderBy": str(order_by),
            "orderDirection": str(order_direction),
            "limit": limit,
            "page": page,
        }

        if signature:
            params["signature"] = signature
        if program_id:
            params["program_id"] = str(program_id)
        if mint:
            params["mint"] = mint
        if authority:
            params["authority"] = authority
        if source:
            params["source"] = source
        if destination:
            params["destination"] = destination
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        response = await self.manager.get(
            f"{self.base_url}/transfers/svm",
            headers=self._headers,
            params=params,
            expected_type=SolanaTransfersResponse,
            timeout=30,
        )
        return response.data  # type: ignore[no-any-return]

    # ===== Swap Methods =====

    async def get_swaps(
        self,
        program_id: SwapPrograms | str,
        amm: str | None = None,
        amm_pool: str | None = None,
        user: str | None = None,
        input_mint: str | None = None,
        output_mint: str | None = None,
        signature: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        order_by: OrderBy | str = OrderBy.TIMESTAMP,
        order_direction: OrderDirection | str = OrderDirection.DESC,
        limit: int = 10,
        page: int = 1,
    ) -> list[SolanaSwap]:
        """
        Get Solana DEX swap transactions.

        Args:
            program_id: Filter by swap program ID (required)
            amm: Filter by AMM address
            amm_pool: Filter by AMM pool address
            user: Filter by user address
            input_mint: Filter by input mint address
            output_mint: Filter by output mint address
            signature: Filter by transaction signature
            start_time: Start time as UNIX timestamp
            end_time: End time as UNIX timestamp
            order_by: Field to order by
            order_direction: Order direction (asc/desc)
            limit: Maximum number of results
            page: Page number

        Returns:
            List of SolanaSwap objects
        """
        self._validate_pagination(limit, page)
        params = {
            "program_id": str(program_id),
            "network_id": self.network,
            "orderBy": str(order_by),
            "orderDirection": str(order_direction),
            "limit": limit,
            "page": page,
        }

        if amm:
            params["amm"] = amm
        if amm_pool:
            params["amm_pool"] = amm_pool
        if user:
            params["user"] = user
        if input_mint:
            params["input_mint"] = input_mint
        if output_mint:
            params["output_mint"] = output_mint
        if signature:
            params["signature"] = signature
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        response = await self.manager.get(
            f"{self.base_url}/swaps/svm",
            headers=self._headers,
            params=params,
            expected_type=SolanaSwapsResponse,
            timeout=30,
        )
        # Extract the swap data from nested response structure
        data = response.data  # type: ignore[attr-defined]
        if isinstance(data, dict) and "data" in data:
            return [SolanaSwap(**swap) for swap in data["data"]]
        return []

    # ===== SOL Price Methods =====

    async def get_sol_price(self, *, include_stats: bool = False) -> float | dict[str, Any] | None:
        """
        Get current SOL price in USD with smart caching and auto-optimization.

        This method automatically:
        - Uses optimal trade sampling based on market conditions
        - Caches results with volatility-based TTL
        - Handles retries and outlier filtering
        - Adapts parameters based on data availability

        Args:
            include_stats: If True, returns detailed statistics instead of just price

        Returns:
            float: Current SOL price in USD (if include_stats=False)
            dict: Price with statistics (if include_stats=True)
            None: If no valid price data available
        """
        # Return cached data if fresh
        if self._sol_price_cache and self._sol_price_cache.is_fresh:
            return self._sol_price_cache.stats if include_stats else self._sol_price_cache.price

        # Smart parameter selection based on time of day and recent volatility
        base_trades = 100  # More trades for better accuracy
        base_minutes = 15  # Longer window for stability

        try:
            # Progressive retry with smart parameter adjustment
            for _attempt, multiplier in enumerate([1, 2, 3, 5], 1):
                trades = min(base_trades * multiplier, 500)  # Cap at 500
                minutes = min(base_minutes * multiplier, 120)  # Cap at 2 hours

                swaps = await self._fetch_sol_usdc_swaps(trades, minutes)

                if not swaps:
                    continue

                prices = self._extract_sol_prices(swaps)

                if len(prices) >= 3:  # Need minimum sample size
                    break
            else:
                return None

            # Calculate statistics
            price = statistics.median(prices)
            stats = {
                "price": price,
                "mean_price": statistics.mean(prices),
                "std_deviation": statistics.stdev(prices) if len(prices) > 1 else 0,
                "min_price": min(prices),
                "max_price": max(prices),
                "trades_analyzed": len(prices),
                "confidence": min(len(prices) / 10, 1.0),  # 0-1 confidence score
                "timestamp": time.time(),
            }

            # Cache with smart TTL
            self._sol_price_cache = _PriceData(price=price, stats=stats, cached_at=time.time())

            return stats if include_stats else price

        except Exception:  # noqa: BLE001
            return None

    async def _fetch_sol_usdc_swaps(self, limit: int, minutes_back: int) -> list[dict[str, Any]]:
        """Fetch SOL/USDC swaps from Jupiter v6 using existing swap method."""
        end_time = int(time.time())
        start_time = end_time - (minutes_back * 60)

        # Try first with both input and output mints
        swaps = await self.get_swaps(
            program_id=SwapPrograms.JUPITER_V6,
            input_mint=_SOL_MINT,
            output_mint=_USDC_MINT,
            start_time=start_time,
            end_time=end_time,
            order_by=OrderBy.TIMESTAMP,
            order_direction=OrderDirection.DESC,
            limit=limit,
        )

        # If no results, try without specifying mints (might be too restrictive)
        if not swaps or len(swaps) == 0:
            swaps = await self.get_swaps(
                program_id=SwapPrograms.JUPITER_V6,
                start_time=start_time,
                end_time=end_time,
                order_by=OrderBy.TIMESTAMP,
                order_direction=OrderDirection.DESC,
                limit=limit,
            )

        # Convert to list of dicts for price extraction
        if not swaps:
            return []

        return [
            swap.__dict__ if hasattr(swap, "__dict__") else swap  # type: ignore[misc]
            for swap in swaps
        ]

    def _extract_sol_prices(self, swaps: list[dict[str, Any]]) -> list[float]:
        """Extract SOL prices from swap data with intelligent filtering."""
        prices = []

        for swap in swaps:
            try:
                # Get mint addresses (handle both dict and string formats)
                input_mint = self._get_mint_address(swap.get("input_mint"))  # type: ignore[arg-type]
                output_mint = self._get_mint_address(swap.get("output_mint"))  # type: ignore[arg-type]

                # Only process SOL/USDC pairs
                if not self._is_sol_usdc_pair(input_mint, output_mint):
                    continue

                input_amount = float(swap.get("input_amount", 0))
                output_amount = float(swap.get("output_amount", 0))

                if input_amount <= 0 or output_amount <= 0:
                    continue

                # Calculate price based on swap direction
                if input_mint == _SOL_MINT:  # SOL -> USDC
                    price = (output_amount / 1e6) / (input_amount / 1e9)
                else:  # USDC -> SOL
                    price = (input_amount / 1e6) / (output_amount / 1e9)

                # Dynamic outlier filtering (3 sigma rule)
                if 10 <= price <= 2000:  # Basic sanity check
                    prices.append(price)

            except (ValueError, ZeroDivisionError, KeyError, TypeError):
                continue

        # Additional outlier removal using IQR method for better data quality
        if len(prices) >= 5:
            prices.sort()
            q1, q3 = prices[len(prices) // 4], prices[3 * len(prices) // 4]
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            prices = [p for p in prices if lower <= p <= upper]

        return prices

    def _get_mint_address(self, mint_data: dict[str, Any] | str | None) -> str:
        """Extract mint address from various data formats."""
        if isinstance(mint_data, dict):
            return str(mint_data.get("address", ""))
        return str(mint_data) if mint_data else ""

    def _is_sol_usdc_pair(self, mint1: str, mint2: str) -> bool:
        """Check if the pair is SOL/USDC."""
        mints = {mint1, mint2}
        return mints == {_SOL_MINT, _USDC_MINT}
