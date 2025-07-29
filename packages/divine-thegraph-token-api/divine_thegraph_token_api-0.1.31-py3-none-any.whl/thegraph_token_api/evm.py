"""
EVM-specific client for The Graph Token API.

Provides access to EVM blockchain data including NFTs, tokens, balances, transfers, and DEX data.
"""

from .base import BaseTokenAPI
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

    # ===== NFT Methods =====

    async def get_nft_ownerships(
        self, address: str, token_standard: TokenStandard | str | None = None, limit: int = 10, page: int = 1
    ) -> NFTOwnershipsResponse:
        """
        Get NFT ownerships for an EVM address.

        Args:
            address: EVM address to query
            token_standard: Filter by token standard (ERC721, ERC1155)
            limit: Maximum number of results (1-1000, default 10)
            page: Page number (default 1)

        Returns:
            NFTOwnershipsResponse with validated data
        """
        params = self._build_base_params(self.network, limit, page)
        self._add_optional_params(params, token_standard=token_standard)

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
            params["any"] = any_address
        if from_address:
            params["from"] = from_address
        if to_address:
            params["to"] = to_address
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
            params["any"] = any_address
        if offerer:
            params["offerer"] = offerer
        if recipient:
            params["recipient"] = recipient
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
            params["from"] = from_address
        if to_address:
            params["to"] = to_address
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
        interval: Interval | str = Interval.ONE_HOUR,
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
        interval: Interval | str = Interval.ONE_HOUR,
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
        interval: Interval | str = Interval.ONE_HOUR,
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
