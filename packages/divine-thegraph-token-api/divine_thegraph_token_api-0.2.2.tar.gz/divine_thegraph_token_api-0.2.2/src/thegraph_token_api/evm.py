"""
EVM-specific client for The Graph Token API.

Provides access to EVM blockchain data including NFTs, tokens, balances, transfers, DEX data, and ETH price calculation.
"""

import time
from typing import Any

from .base import BaseTokenAPI
from .constants import USDC_ETH_ADDRESS, WETH_ADDRESS
from .price_utils import PriceCalculator, PriceData, create_price_cache
from .types import (
    BalancesResponse,
    HistoricalBalancesResponse,
    Interval,
    # Enums
    NetworkId,
    NFTActivitiesResponse,
    NFTCollectionsResponse,
    NFTHoldersResponse,
    NFTItemsResponse,
    # Response types
    NFTOwnershipsResponse,
    NFTSalesResponse,
    OHLCResponse,
    OrderBy,
    OrderDirection,
    PoolsResponse,
    Protocol,
    SwapsResponse,
    TokenHoldersResponse,
    TokensResponse,
    TokenStandard,
    TransfersResponse,
)


class EVMTokenAPI(BaseTokenAPI):
    """
    EVM-specific client for The Graph Token API.

    Provides access to EVM blockchain data with network-specific configuration.

    Example:
        ```python
        import anyio
        from thegraph_client import EVMTokenAPI, NetworkId

        async def main():
            # Create EVM client for specific network
            async with EVMTokenAPI(
                api_key="your_bearer_token",  # pragma: allowlist secret
                network=NetworkId.MAINNET
            ) as evm_api:
                # All methods automatically use the configured network
                ownerships = await evm_api.get_nft_ownerships(
                    address="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                )

                balances = await evm_api.get_balances(
                    address="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                )

        anyio.run(main)
        ```
    """

    def __init__(self, network: NetworkId | str, api_key: str | None = None, base_url: str | None = None):
        """
        Initialize EVM Token API client.

        Args:
            network: EVM network to use for all requests (e.g., NetworkId.MAINNET)
            api_key: Bearer token for API authentication
            base_url: API base URL (optional)
        """
        super().__init__(api_key, base_url)
        self.network = str(network)
        self._eth_price_cache: PriceData | None = None

    # ===== NFT Methods =====

    async def get_nft_ownerships(
        self,
        address: str,
        contract: str | None = None,
        token_standard: TokenStandard | str | None = None,
        limit: int = 10,
        page: int = 1,
    ) -> NFTOwnershipsResponse:
        """
        Get NFT ownerships for an EVM address.

        Args:
            address: EVM address to query
            contract: Filter by contract address
            token_standard: Filter by token standard (ERC721, ERC1155)
            limit: Maximum number of results (1-1000, default 10)
            page: Page number (default 1)

        Returns:
            NFTOwnershipsResponse with validated data
        """
        params = self._build_base_params(self.network, limit, page)
        self._add_optional_params(params, contract=contract, token_standard=token_standard)

        response = await self.manager.get(
            f"{self.base_url}/nft/ownerships/evm/{address}",
            headers=self._headers,
            params=params,
            expected_type=NFTOwnershipsResponse,
            timeout=30,
        )
        return response.data

    async def get_nft_collection(self, contract: str) -> NFTCollectionsResponse:
        """
        Get NFT collection metadata by contract address.

        Args:
            contract: NFT contract address

        Returns:
            NFTCollectionsResponse with validated data
        """
        params = {"network_id": self.network}

        response = await self.manager.get(
            f"{self.base_url}/nft/collections/evm/{contract}",
            headers=self._headers,
            params=params,
            expected_type=NFTCollectionsResponse,
            timeout=30,
        )
        return response.data

    async def get_nft_item(self, contract: str, token_id: str) -> NFTItemsResponse:
        """
        Get specific NFT item metadata by contract and token ID.

        Args:
            contract: NFT contract address
            token_id: NFT token ID

        Returns:
            NFTItemsResponse with validated data
        """
        params = {"network_id": self.network}

        response = await self.manager.get(
            f"{self.base_url}/nft/items/evm/contract/{contract}/token_id/{token_id}",
            headers=self._headers,
            params=params,
            expected_type=NFTItemsResponse,
            timeout=30,
        )
        return response.data

    async def get_nft_activities(
        self,
        contract: str,
        any_address: str | None = None,
        from_address: str | None = None,
        to_address: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        order_by: OrderBy | str = OrderBy.TIMESTAMP,
        order_direction: OrderDirection | str = OrderDirection.DESC,
        limit: int = 10,
        page: int = 1,
    ) -> NFTActivitiesResponse:
        """
        Get NFT activities (transfers, mints, burns) for a contract.

        Args:
            contract: NFT contract address (required)
            any_address: Filter by any address (from or to)
            from_address: Filter by from address
            to_address: Filter by to address
            start_time: Start time as UNIX timestamp
            end_time: End time as UNIX timestamp
            order_by: Field to order by
            order_direction: Order direction (asc/desc)
            limit: Maximum number of results (1-1000)
            page: Page number

        Returns:
            NFTActivitiesResponse with validated data
        """
        self._validate_pagination(limit, page)
        params = {
            "network_id": self.network,
            "contract": contract,
            "orderBy": str(order_by),
            "orderDirection": str(order_direction),
            "limit": limit,
            "page": page,
        }

        if any_address:
            params["anyAddress"] = any_address
        if from_address:
            params["fromAddress"] = from_address
        if to_address:
            params["toAddress"] = to_address
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        response = await self.manager.get(
            f"{self.base_url}/nft/activities/evm",
            headers=self._headers,
            params=params,
            expected_type=NFTActivitiesResponse,
            timeout=30,
        )
        return response.data

    async def get_nft_holders(self, contract: str) -> NFTHoldersResponse:
        """
        Get NFT holders for a contract.

        Args:
            contract: NFT contract address

        Returns:
            NFTHoldersResponse with validated data
        """
        params = {"network_id": self.network}

        response = await self.manager.get(
            f"{self.base_url}/nft/holders/evm/{contract}",
            headers=self._headers,
            params=params,
            expected_type=NFTHoldersResponse,
            timeout=30,
        )
        return response.data

    async def get_nft_sales(
        self,
        contract: str,
        token_id: str | None = None,
        any_address: str | None = None,
        offerer: str | None = None,
        recipient: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        order_by: OrderBy | str = OrderBy.TIMESTAMP,
        order_direction: OrderDirection | str = OrderDirection.DESC,
        limit: int = 10,
        page: int = 1,
    ) -> NFTSalesResponse:
        """
        Get NFT marketplace sales.

        Args:
            contract: NFT contract address (required)
            token_id: Filter by specific token ID
            any_address: Filter by any address
            offerer: Filter by offerer address
            recipient: Filter by recipient address
            start_time: Start time as UNIX timestamp
            end_time: End time as UNIX timestamp
            order_by: Field to order by
            order_direction: Order direction (asc/desc)
            limit: Maximum number of results (1-1000)
            page: Page number

        Returns:
            NFTSalesResponse with validated data
        """
        self._validate_pagination(limit, page)
        params = {
            "network_id": self.network,
            "contract": contract,
            "orderBy": str(order_by),
            "orderDirection": str(order_direction),
            "limit": limit,
            "page": page,
        }

        if token_id:
            params["token_id"] = token_id
        if any_address:
            params["anyAddress"] = any_address
        if offerer:
            params["offererAddress"] = offerer
        if recipient:
            params["recipientAddress"] = recipient
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        response = await self.manager.get(
            f"{self.base_url}/nft/sales/evm",
            headers=self._headers,
            params=params,
            expected_type=NFTSalesResponse,
            timeout=30,
        )
        return response.data

    # ===== Balance Methods =====

    async def get_balances(
        self, address: str, contract: str | None = None, limit: int = 10, page: int = 1
    ) -> BalancesResponse:
        """
        Get ERC-20 and native token balances for an address.

        Args:
            address: EVM address to query
            contract: Filter by specific contract
            limit: Maximum number of results
            page: Page number

        Returns:
            BalancesResponse with validated data
        """
        self._validate_pagination(limit, page)
        params = {"network_id": self.network, "limit": limit, "page": page}
        if contract:
            params["contract"] = contract

        response = await self.manager.get(
            f"{self.base_url}/balances/evm/{address}",
            headers=self._headers,
            params=params,
            expected_type=BalancesResponse,
            timeout=30,
        )
        return response.data

    # ===== Transfer Methods =====

    async def get_transfers(
        self,
        from_address: str | None = None,
        to_address: str | None = None,
        contract: str | None = None,
        transaction_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        order_by: OrderBy | str = OrderBy.TIMESTAMP,
        order_direction: OrderDirection | str = OrderDirection.DESC,
        limit: int = 10,
        page: int = 1,
    ) -> TransfersResponse:
        """
        Get ERC-20 and native token transfer events.

        Args:
            from_address: Filter by from address
            to_address: Filter by to address
            contract: Filter by contract address
            transaction_id: Filter by transaction hash
            start_time: Start time as UNIX timestamp
            end_time: End time as UNIX timestamp
            order_by: Field to order by
            order_direction: Order direction (asc/desc)
            limit: Maximum number of results
            page: Page number

        Returns:
            TransfersResponse with validated data
        """
        self._validate_pagination(limit, page)
        params = {
            "network_id": self.network,
            "orderBy": str(order_by),
            "orderDirection": str(order_direction),
            "limit": limit,
            "page": page,
        }

        if from_address:
            params["fromAddress"] = from_address
        if to_address:
            params["toAddress"] = to_address
        if contract:
            params["contract"] = contract
        if transaction_id:
            params["transaction_id"] = transaction_id
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        response = await self.manager.get(
            f"{self.base_url}/transfers/evm",
            headers=self._headers,
            params=params,
            expected_type=TransfersResponse,
            timeout=30,
        )
        return response.data

    # ===== Token Methods =====

    async def get_token(self, contract: str) -> TokensResponse:
        """
        Get ERC-20 token contract metadata.

        Args:
            contract: Token contract address

        Returns:
            TokensResponse with validated data
        """
        params = {"network_id": self.network}

        response = await self.manager.get(
            f"{self.base_url}/tokens/evm/{contract}",
            headers=self._headers,
            params=params,
            expected_type=TokensResponse,
            timeout=30,
        )
        # Return the full response object
        return response.data

    async def get_token_holders(
        self,
        contract: str,
        order_by: OrderBy | str = OrderBy.VALUE,
        order_direction: OrderDirection | str = OrderDirection.DESC,
        limit: int = 10,
        page: int = 1,
    ) -> TokenHoldersResponse:
        """
        Get ERC-20 token holder balances by contract address.

        Args:
            contract: Token contract address
            order_by: Field to order by
            order_direction: Order direction (asc/desc)
            limit: Maximum number of results
            page: Page number

        Returns:
            TokenHoldersResponse with validated data
        """
        self._validate_pagination(limit, page)
        params = {
            "network_id": self.network,
            "orderBy": str(order_by),
            "orderDirection": str(order_direction),
            "limit": limit,
            "page": page,
        }

        response = await self.manager.get(
            f"{self.base_url}/holders/evm/{contract}",
            headers=self._headers,
            params=params,
            expected_type=TokenHoldersResponse,
            timeout=30,
        )
        return response.data

    # ===== Swap Methods =====

    async def get_swaps(
        self,
        pool: str | None = None,
        caller: str | None = None,
        sender: str | None = None,
        recipient: str | None = None,
        protocol: Protocol | str | None = None,
        transaction_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        order_by: OrderBy | str = OrderBy.TIMESTAMP,
        order_direction: OrderDirection | str = OrderDirection.DESC,
        limit: int = 10,
        page: int = 1,
    ) -> SwapsResponse:
        """
        Get EVM DEX swap transactions.

        Args:
            pool: Filter by pool address
            caller: Filter by caller address
            sender: Filter by sender address
            recipient: Filter by recipient address
            protocol: Filter by DEX protocol
            transaction_id: Filter by transaction hash
            start_time: Start time as UNIX timestamp
            end_time: End time as UNIX timestamp
            order_by: Field to order by
            order_direction: Order direction (asc/desc)
            limit: Maximum number of results
            page: Page number

        Returns:
            SwapsResponse with validated data
        """
        self._validate_pagination(limit, page)
        params = {
            "network_id": self.network,
            "orderBy": str(order_by),
            "orderDirection": str(order_direction),
            "limit": limit,
            "page": page,
        }

        if pool:
            params["pool"] = pool
        if caller:
            params["caller"] = caller
        if sender:
            params["sender"] = sender
        if recipient:
            params["recipient"] = recipient
        if protocol:
            params["protocol"] = str(protocol)
        if transaction_id:
            params["transaction_id"] = transaction_id
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        response = await self.manager.get(
            f"{self.base_url}/swaps/evm", headers=self._headers, params=params, expected_type=SwapsResponse, timeout=30
        )
        # Return the full response object, since response is already the validated dict
        return response.data

    # ===== Pool Methods =====

    async def get_pools(
        self,
        pool: str | None = None,
        factory: str | None = None,
        token: str | None = None,
        symbol: str | None = None,
        protocol: Protocol | str | None = None,
        limit: int = 10,
        page: int = 1,
    ) -> PoolsResponse:
        """
        Get EVM DEX liquidity pools.

        Args:
            pool: Filter by pool address
            factory: Filter by factory address
            token: Filter by token address
            symbol: Filter by symbol
            protocol: Filter by DEX protocol
            limit: Maximum number of results
            page: Page number

        Returns:
            PoolsResponse with validated data
        """
        self._validate_pagination(limit, page)
        params = {"network_id": self.network, "limit": limit, "page": page}

        if pool:
            params["pool"] = pool
        if factory:
            params["factory"] = factory
        if token:
            params["token"] = token
        if symbol:
            params["symbol"] = symbol
        if protocol:
            params["protocol"] = str(protocol)

        response = await self.manager.get(
            f"{self.base_url}/pools/evm", headers=self._headers, params=params, expected_type=PoolsResponse, timeout=30
        )
        return response.data

    # ===== OHLC Methods =====

    async def get_ohlc_pools(
        self,
        pool: str,
        interval: Interval | str = Interval.ONE_DAY,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int = 10,
        page: int = 1,
    ) -> OHLCResponse:
        """
        Get OHLC data for EVM DEX pools.

        Args:
            pool: Pool address (required)
            interval: Time interval (1h, 4h, 1d, 1w)
            start_time: Start time as UNIX timestamp
            end_time: End time as UNIX timestamp
            limit: Maximum number of results (default 10)
            page: Page number

        Returns:
            OHLCResponse with validated data
        """
        self._validate_pagination(limit, page)
        params = {"network_id": self.network, "interval": str(interval), "limit": limit, "page": page}

        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        response = await self.manager.get(
            f"{self.base_url}/ohlc/pools/evm/{pool}",
            headers=self._headers,
            params=params,
            expected_type=OHLCResponse,
            timeout=30,
        )
        return response.data

    async def get_ohlc_prices(
        self,
        token: str,
        interval: Interval | str = Interval.ONE_DAY,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int = 10,
        page: int = 1,
    ) -> OHLCResponse:
        """
        Get OHLC price data for EVM tokens.

        Args:
            token: Token address (required)
            interval: Time interval (1h, 4h, 1d, 1w)
            start_time: Start time as UNIX timestamp
            end_time: End time as UNIX timestamp
            limit: Maximum number of results (default 10)
            page: Page number

        Returns:
            OHLCResponse with validated data
        """
        self._validate_pagination(limit, page)
        params = {"network_id": self.network, "interval": str(interval), "limit": limit, "page": page}

        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        response = await self.manager.get(
            f"{self.base_url}/ohlc/prices/evm/{token}",
            headers=self._headers,
            params=params,
            expected_type=OHLCResponse,
            timeout=30,
        )
        return response.data

    # ===== Historical Methods =====

    async def get_historical_balances(
        self,
        address: str,
        contracts: list[str] | None = None,
        interval: Interval | str = Interval.ONE_DAY,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int = 10,
        page: int = 1,
    ) -> HistoricalBalancesResponse:
        """
        Get historical balance data for EVM addresses.

        Args:
            address: EVM address to query (required)
            contracts: List of contract addresses to filter by
            interval: Time interval (1h, 4h, 1d, 1w)
            start_time: Start time as UNIX timestamp
            end_time: End time as UNIX timestamp
            limit: Maximum number of results (default 10)
            page: Page number

        Returns:
            HistoricalBalancesResponse with validated data
        """
        self._validate_pagination(limit, page)
        params = {"network_id": self.network, "interval": str(interval), "limit": limit, "page": page}

        if contracts:
            params["contracts"] = contracts
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        response = await self.manager.get(
            f"{self.base_url}/historical/balances/evm/{address}",
            headers=self._headers,
            params=params,
            expected_type=HistoricalBalancesResponse,
            timeout=30,
        )
        return response.data

    # ===== ETH Price Methods =====

    async def get_eth_price(self, *, include_stats: bool = False) -> float | dict[str, Any] | None:
        """
        Get current ETH price in USD with smart caching and auto-optimization.

        This method automatically:
        - Uses optimal trade sampling based on market conditions
        - Caches results with volatility-based TTL
        - Handles retries and outlier filtering
        - Adapts parameters based on data availability

        Args:
            include_stats: If True, returns detailed statistics instead of just price

        Returns:
            float: Current ETH price in USD (if include_stats=False)
            dict: Price with statistics (if include_stats=True)
            None: If no valid price data available
        """
        # Return cached data if fresh
        if self._eth_price_cache and self._eth_price_cache.is_fresh:
            return self._eth_price_cache.stats if include_stats else self._eth_price_cache.price

        # Initialize price calculator
        calculator = PriceCalculator()

        try:
            # Progressive retry with smart parameter adjustment
            for attempt in range(1, 5):
                trades, minutes = calculator.progressive_retry_params(attempt)

                swaps = await self._fetch_eth_usdc_swaps(trades, minutes)

                if not swaps:
                    continue

                prices = self._extract_eth_prices(swaps)

                if len(prices) >= 3:  # Need minimum sample size
                    break
            else:
                return None

            # Calculate statistics
            price_stats = calculator.calculate_price_statistics(prices, len(swaps))
            if not price_stats:
                return None

            # Cache with smart TTL
            price = price_stats["price"]
            self._eth_price_cache = create_price_cache(price, price_stats)

            return price_stats if include_stats else price

        except Exception:  # noqa: BLE001
            return None

    async def _fetch_eth_usdc_swaps(self, limit: int, minutes_back: int) -> list[dict[str, Any]]:
        """Fetch ETH/USDC swaps from Uniswap V3 using existing swap method."""
        end_time = int(time.time())
        start_time = end_time - (minutes_back * 60)

        # Try to get swaps from Uniswap V3 (most liquid for ETH/USDC)
        swaps = await self.get_swaps(
            protocol=Protocol.UNISWAP_V3, start_time=start_time, end_time=end_time, limit=limit
        )

        # If no results, try without protocol filter
        if not swaps or len(swaps) == 0:
            swaps = await self.get_swaps(start_time=start_time, end_time=end_time, limit=limit)

        # Convert to list of dicts for price extraction
        if not swaps:
            return []

        result: list[dict[str, Any]] = []
        for swap in swaps:
            if hasattr(swap, "__dict__"):
                result.append(swap.__dict__)
            elif isinstance(swap, dict):
                result.append(swap)
            else:
                result.append({})

        return result

    def _extract_eth_prices(self, swaps: list[dict[str, Any]]) -> list[float]:
        """Extract ETH prices from swap data with intelligent filtering."""
        prices = []

        for swap in swaps:
            try:
                # Get token addresses
                token0_addr = swap.get("token0", {}).get("address", "").lower()
                token1_addr = swap.get("token1", {}).get("address", "").lower()

                weth_addr = WETH_ADDRESS.lower()
                usdc_addr = USDC_ETH_ADDRESS.lower()

                # Only process WETH/USDC pairs
                if not self._is_eth_usdc_pair(token0_addr, token1_addr, weth_addr, usdc_addr):
                    continue

                # Get amounts and decimals
                amount0_str = swap.get("amount0", "0")
                amount1_str = swap.get("amount1", "0")
                token0_decimals = int(swap.get("token0", {}).get("decimals", 18))
                token1_decimals = int(swap.get("token1", {}).get("decimals", 6))

                # Convert string amounts to float (they might be very large numbers)
                amount0 = float(amount0_str)
                amount1 = float(amount1_str)

                if amount0 == 0 or amount1 == 0:
                    continue

                # Normalize amounts based on decimals
                amount0_normalized = abs(amount0) / (10**token0_decimals)
                amount1_normalized = abs(amount1) / (10**token1_decimals)

                # Calculate price based on which token is WETH
                if token0_addr == weth_addr:  # WETH is token0, USDC is token1
                    price = amount1_normalized / amount0_normalized
                else:  # USDC is token0, WETH is token1
                    price = amount0_normalized / amount1_normalized

                # Basic sanity check for ETH price (should be between $100 and $10,000)
                if 100 <= price <= 10000:
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

    def _is_eth_usdc_pair(self, token0: str, token1: str, weth_addr: str, usdc_addr: str) -> bool:
        """Check if the pair is WETH/USDC."""
        token_set = {token0, token1}
        target_set = {weth_addr, usdc_addr}
        return token_set == target_set
