"""
Simplified Token API Interface

This module provides a clean, separated interface for EVM and SVM chains:
- Auto-loads environment variables
- Returns clean data (no response unwrapping)
- Uses smart defaults (mainnet, reasonable limits)
- Separated EVM and SVM methods

Usage:
    from thegraph_token_api import TokenAPI

    api = TokenAPI()  # Auto-loads from .env
    eth_balances = await api.evm.balances("0x...")  # EVM chains
    sol_balances = await api.svm.balances(mint="...")  # Solana
"""

import os
from datetime import datetime, timedelta
from typing import Any

from dotenv import load_dotenv

from .client import TheGraphTokenAPI
from .models import (
    OHLC,
    Balance,
    NFTActivity,
    NFTCollection,
    NFTOwnership,
    Pool,
    SolanaBalance,
    SolanaSwap,
    SolanaTransfer,
    Swap,
    Token,
    TokenHolder,
    Transfer,
    convert_list_to_models,
    convert_to_model,
)
from .types import (
    Interval,
    NetworkId,
    OrderBy,
    OrderDirection,
    Protocol,
    SolanaNetworkId,
    SolanaPrograms,
    SwapPrograms,
    TokenStandard,
)


class NFTWrapper:
    """NFT-specific methods wrapper for EVM chains."""

    def __init__(self, api_instance):
        self._api = api_instance

    async def ownerships(
        self,
        address: str,
        token_standard: TokenStandard | str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[NFTOwnership]:
        """Get NFT ownerships for an address."""
        data = await self._api._evm_nfts(address=address, token_standard=token_standard, limit=limit, network=network)
        return convert_list_to_models(data, NFTOwnership)

    async def collection(self, contract: str, network: NetworkId | str | None = None) -> NFTCollection | None:
        """Get NFT collection metadata by contract address."""
        data = await self._api._evm_nft_collection(contract=contract, network=network)
        return convert_to_model(data, NFTCollection) if data else None

    async def activities(
        self,
        contract: str,
        from_address: str | None = None,
        to_address: str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[NFTActivity]:
        """Get NFT activities (transfers, mints, burns) for a contract."""
        data = await self._api._evm_nft_activities(
            contract=contract, from_address=from_address, to_address=to_address, limit=limit, network=network
        )
        return convert_list_to_models(data, NFTActivity)

    async def item(self, contract: str, token_id: str, network: NetworkId | str | None = None) -> list[dict[str, Any]]:
        """Get specific NFT item metadata by contract and token ID."""
        data = await self._api._evm_nft_item(contract=contract, token_id=token_id, network=network)
        return data.get("items", []) if data else []

    async def holders(self, contract: str, network: NetworkId | str | None = None) -> list[dict[str, Any]]:
        """Get NFT holders for a contract."""
        data = await self._api._evm_nft_holders(contract=contract, network=network)
        return data.get("holders", []) if data else []

    async def sales(
        self,
        contract: str,
        token_id: str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[dict[str, Any]]:
        """Get NFT marketplace sales."""
        data = await self._api._evm_nft_sales(contract=contract, token_id=token_id, limit=limit, network=network)
        return data.get("sales", []) if data else []


class EVMWrapper:
    """EVM-specific methods wrapper."""

    def __init__(self, api_instance):
        self._api = api_instance

        # Initialize nested NFT wrapper
        self.nfts = NFTWrapper(api_instance)

    async def balances(
        self, address: str, contract: str | None = None, limit: int = 10, network: NetworkId | str | None = None
    ) -> list[Balance]:
        """Get EVM token balances for an address."""
        data = await self._api._evm_balances(address=address, contract=contract, limit=limit, network=network)
        return convert_list_to_models(data, Balance)

    async def historical_balances(
        self,
        address: str,
        contracts: list[str] | None = None,
        interval: Interval | str = Interval.ONE_DAY,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[dict[str, Any]]:
        """Get historical balance data for EVM addresses."""
        data = await self._api._evm_historical_balances(
            address=address, contracts=contracts, interval=interval, limit=limit, network=network
        )
        return data.get("balances", []) if data else []

    async def token_info(self, contract: str, network: NetworkId | str | None = None) -> Token | None:
        """Get EVM token contract information."""
        data = await self._api._evm_token_info(contract=contract, network=network)
        return convert_to_model(data, Token) if data else None

    async def transfers(
        self,
        from_address: str | None = None,
        to_address: str | None = None,
        contract: str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[Transfer]:
        """Get EVM token transfer events."""
        data = await self._api._evm_transfers(
            from_address=from_address, to_address=to_address, contract=contract, limit=limit, network=network
        )
        return convert_list_to_models(data, Transfer)

    async def swaps(
        self,
        pool: str | None = None,
        protocol: Protocol | str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[Swap]:
        """Get EVM DEX swap transactions."""
        data = await self._api._evm_swaps(pool=pool, protocol=protocol, limit=limit, network=network)
        return convert_list_to_models(data, Swap)

    async def swaps_advanced(
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
        network: NetworkId | str | None = None,
    ) -> list[Swap]:
        """Get EVM DEX swap transactions with advanced filtering."""
        data = await self._api._evm_swaps_advanced(
            pool=pool,
            caller=caller,
            sender=sender,
            recipient=recipient,
            protocol=protocol,
            transaction_id=transaction_id,
            start_time=start_time,
            end_time=end_time,
            order_by=order_by,
            order_direction=order_direction,
            limit=limit,
            network=network,
        )
        return convert_list_to_models(data, Swap)

    async def pools(
        self,
        pool: str | None = None,
        token: str | None = None,
        protocol: Protocol | str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[Pool]:
        """Get EVM DEX liquidity pools."""
        data = await self._api._evm_pools(pool=pool, token=token, protocol=protocol, limit=limit, network=network)
        return convert_list_to_models(data, Pool)

    async def price_history(
        self,
        token: str,
        interval: Interval | str = Interval.ONE_DAY,
        days: int = 1,
        limit: int = 24,
        network: NetworkId | str | None = None,
    ) -> list[OHLC]:
        """Get EVM OHLC price data for a token."""
        data = await self._api._evm_price_history(
            token=token, interval=interval, days=days, limit=limit, network=network
        )
        return convert_list_to_models(data, OHLC)

    async def pool_history(
        self,
        pool: str,
        interval: Interval | str = Interval.ONE_DAY,
        days: int = 1,
        limit: int = 24,
        network: NetworkId | str | None = None,
    ) -> list[OHLC]:
        """Get EVM OHLC data for a DEX pool."""
        data = await self._api._evm_pool_history(pool=pool, interval=interval, days=days, limit=limit, network=network)
        return convert_list_to_models(data, OHLC)

    async def token_holders(
        self, contract: str, limit: int = 10, network: NetworkId | str | None = None
    ) -> list[TokenHolder]:
        """Get EVM token holder balances by contract address."""
        data = await self._api._evm_token_holders(contract=contract, limit=limit, network=network)
        return convert_list_to_models(data, TokenHolder)


class SVMWrapper:
    """SVM-specific methods wrapper."""

    def __init__(self, api_instance):
        self._api = api_instance

    async def swaps(
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
        limit: int = 10,
        network: SolanaNetworkId | str = SolanaNetworkId.SOLANA,
    ) -> list[SolanaSwap]:
        """Get SVM DEX swap transactions."""
        data = await self._api._svm_swaps(
            program_id=program_id,
            amm=amm,
            amm_pool=amm_pool,
            user=user,
            input_mint=input_mint,
            output_mint=output_mint,
            signature=signature,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            network=network,
        )
        return convert_list_to_models(data, SolanaSwap)

    async def balances(
        self,
        token_account: str | None = None,
        mint: str | None = None,
        program_id: SolanaPrograms | str | None = None,
        limit: int = 10,
        network: SolanaNetworkId | str = SolanaNetworkId.SOLANA,
    ) -> list[SolanaBalance]:
        """Get SVM token balances."""
        data = await self._api._svm_balances(
            token_account=token_account, mint=mint, program_id=program_id, limit=limit, network=network
        )
        return convert_list_to_models(data, SolanaBalance)

    async def transfers(
        self,
        signature: str | None = None,
        program_id: SolanaPrograms | str | None = None,
        mint: str | None = None,
        authority: str | None = None,
        source: str | None = None,
        destination: str | None = None,
        limit: int = 10,
        network: SolanaNetworkId | str = SolanaNetworkId.SOLANA,
    ) -> list[SolanaTransfer]:
        """Get SVM token transfers."""
        data = await self._api._svm_transfers(
            signature=signature,
            program_id=program_id,
            mint=mint,
            authority=authority,
            source=source,
            destination=destination,
            limit=limit,
            network=network,
        )
        return convert_list_to_models(data, SolanaTransfer)

    async def get_sol_price(
        self, *, include_stats: bool = False, network: SolanaNetworkId | str = SolanaNetworkId.SOLANA
    ) -> float | dict[str, Any] | None:
        """
        Get current SOL price in USD with smart caching and auto-optimization.

        This method automatically:
        - Uses optimal trade sampling based on market conditions
        - Caches results with volatility-based TTL
        - Handles retries and outlier filtering
        - Adapts parameters based on data availability

        Args:
            include_stats: If True, returns detailed statistics instead of just price
            network: Solana network to use (default: mainnet)

        Returns:
            float: Current SOL price in USD (if include_stats=False)
            dict: Price with statistics (if include_stats=True)
            None: If no valid price data available

        Example:
            ```python
            # Simple usage
            price = await api.svm.get_sol_price()
            print(f"SOL price: ${price:.2f}")

            # With detailed stats
            stats = await api.svm.get_sol_price(include_stats=True)
            print(f"Price: ${stats['price']:.2f} (confidence: {stats['confidence']:.0%})")
            ```
        """
        return await self._api._svm_get_sol_price(include_stats=include_stats, network=network)  # type: ignore[no-any-return]


class TokenAPI:
    """
    Simplified Token API client with clean, separated EVM/SVM interface.

    This wrapper provides:
    - Auto environment loading
    - Clean data returns (no response unwrapping)
    - Smart defaults
    - Separated EVM/SVM methods

    Example:
        ```python
        from thegraph_token_api import TokenAPI, SwapPrograms, Protocol

        api = TokenAPI()  # Auto-loads API key from .env

        # EVM (Ethereum, Polygon, BSC, etc.)
        eth_balances = await api.evm.balances("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
        eth_nfts = await api.evm.nfts.ownerships("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
        nft_collection = await api.evm.nfts.collection("0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb")
        nft_activities = await api.evm.nfts.activities("0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb")
        eth_swaps = await api.evm.swaps(protocol=Protocol.UNISWAP_V3, limit=10)

        # SVM (Solana)
        sol_balances = await api.svm.balances(mint="So11111111111111111111111111111111111111112")
        sol_swaps = await api.svm.swaps(program_id=SwapPrograms.RAYDIUM, limit=10)
        sol_transfers = await api.svm.transfers(mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")  # pragma: allowlist secret
        sol_price = await api.svm.get_sol_price()  # Get current SOL price

        # Utility
        health = await api.health()
        ```
    """

    def __init__(
        self, api_key: str | None = None, network: NetworkId | str = NetworkId.MAINNET, auto_load_env: bool = True
    ):
        """
        Initialize simplified Token API client.

        Args:
            api_key: API key (auto-loads from THEGRAPH_API_KEY if None)
            network: Default network (mainnet by default)
            auto_load_env: Whether to auto-load from .env file
        """
        if auto_load_env:
            load_dotenv()

        # Auto-load API key if not provided
        if api_key is None:
            api_key = os.getenv("THEGRAPH_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key not found. Please provide api_key parameter or set THEGRAPH_API_KEY environment variable. "
                    "Get a free API key at: https://thegraph.market (click 'Get API Key')"
                )

        self._api = TheGraphTokenAPI(api_key=api_key)
        self._default_network = str(network)

        # Initialize nested API wrappers
        self.evm = EVMWrapper(self)
        self.svm = SVMWrapper(self)

    def _extract_data(self, response) -> list[dict[Any, Any]]:
        """Extract clean data from API response."""
        if hasattr(response, "data") and isinstance(response.data, dict):
            data = response.data.get("data", [])
            return data if isinstance(data, list) else []
        return []

    async def _call_evm_method(
        self, method_name: str, network: NetworkId | str | None = None, **kwargs: Any
    ) -> list[dict]:
        """Generic EVM method delegation helper."""
        net = str(network) if network else self._default_network
        async with self._api.evm(net) as client:
            method = getattr(client, method_name)
            response = await method(**kwargs)
            return self._extract_data(response)

    async def _call_evm_method_single(
        self, method_name: str, network: NetworkId | str | None = None, **kwargs: Any
    ) -> dict | None:
        """Generic EVM method delegation helper that returns single result."""
        data = await self._call_evm_method(method_name, network, **kwargs)
        return data[0] if data else None

    async def _call_svm_method(
        self, method_name: str, network: SolanaNetworkId | str = SolanaNetworkId.SOLANA, **kwargs: Any
    ) -> list[dict]:
        """Generic SVM method delegation helper."""
        async with self._api.svm(str(network)) as client:
            method = getattr(client, method_name)
            response = await method(**kwargs)
            # Handle both response objects and direct data returns
            if isinstance(response, list):
                # Method returns data directly (like get_swaps)
                return [item.model_dump() if hasattr(item, "model_dump") else item for item in response]
            # Method returns response object
            return self._extract_data(response)

    async def _call_svm_method_direct(
        self, method_name: str, network: SolanaNetworkId | str = SolanaNetworkId.SOLANA, **kwargs: Any
    ) -> Any:
        """Generic SVM method delegation helper that returns response directly."""
        async with self._api.svm(str(network)) as client:
            method = getattr(client, method_name)
            return await method(**kwargs)

    # ===== EVM Internal Methods =====

    async def _evm_balances(
        self, address: str, contract: str | None = None, limit: int = 10, network: NetworkId | str | None = None
    ) -> list[dict]:
        """Internal EVM balances implementation."""
        return await self._call_evm_method("get_balances", network, address=address, contract=contract, limit=limit)

    async def _evm_nfts(
        self,
        address: str,
        token_standard: TokenStandard | str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[dict]:
        """Internal EVM NFTs implementation."""
        return await self._call_evm_method(
            "get_nft_ownerships", network, address=address, token_standard=token_standard, limit=limit
        )

    async def _evm_token_info(self, contract: str, network: NetworkId | str | None = None) -> dict | None:
        """Internal EVM token info implementation."""
        return await self._call_evm_method_single("get_token", network, contract=contract)

    async def _evm_transfers(
        self,
        from_address: str | None = None,
        to_address: str | None = None,
        contract: str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[dict]:
        """Internal EVM transfers implementation."""
        return await self._call_evm_method(
            "get_transfers", network, from_address=from_address, to_address=to_address, contract=contract, limit=limit
        )

    async def _evm_swaps(
        self,
        pool: str | None = None,
        protocol: Protocol | str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[dict]:
        """Internal EVM swaps implementation."""
        return await self._call_evm_method("get_swaps", network, pool=pool, protocol=protocol, limit=limit)

    async def _evm_swaps_advanced(
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
        network: NetworkId | str | None = None,
    ) -> list[dict]:
        """Internal EVM advanced swaps implementation."""
        return await self._call_evm_method(
            "get_swaps",
            network,
            pool=pool,
            caller=caller,
            sender=sender,
            recipient=recipient,
            protocol=protocol,
            transaction_id=transaction_id,
            start_time=start_time,
            end_time=end_time,
            order_by=order_by,
            order_direction=order_direction,
            limit=limit,
        )

    async def _evm_nft_collection(self, contract: str, network: NetworkId | str | None = None) -> dict | None:
        """Internal EVM NFT collection implementation."""
        return await self._call_evm_method_single("get_nft_collection", network, contract=contract)

    async def _evm_nft_activities(
        self,
        contract: str,
        from_address: str | None = None,
        to_address: str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[dict]:
        """Internal EVM NFT activities implementation."""
        return await self._call_evm_method(
            "get_nft_activities",
            network,
            contract=contract,
            from_address=from_address,
            to_address=to_address,
            limit=limit,
        )

    async def _evm_nft_item(
        self, contract: str, token_id: str, network: NetworkId | str | None = None
    ) -> list[dict[Any, Any]]:
        """Internal EVM NFT item implementation."""
        return await self._call_evm_method("get_nft_item", network, contract=contract, token_id=token_id)

    async def _evm_nft_holders(self, contract: str, network: NetworkId | str | None = None) -> list[dict[Any, Any]]:
        """Internal EVM NFT holders implementation."""
        return await self._call_evm_method("get_nft_holders", network, contract=contract)

    async def _evm_nft_sales(
        self,
        contract: str,
        token_id: str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[dict[Any, Any]]:
        """Internal EVM NFT sales implementation."""
        return await self._call_evm_method("get_nft_sales", network, contract=contract, token_id=token_id, limit=limit)

    async def _evm_historical_balances(
        self,
        address: str,
        contracts: list[str] | None = None,
        interval: Interval | str = Interval.ONE_DAY,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[dict[Any, Any]]:
        """Internal EVM historical balances implementation."""
        return await self._call_evm_method(
            "get_historical_balances", network, address=address, contracts=contracts, interval=interval, limit=limit
        )

    async def _evm_pools(
        self,
        pool: str | None = None,
        token: str | None = None,
        protocol: Protocol | str | None = None,
        limit: int = 10,
        network: NetworkId | str | None = None,
    ) -> list[dict]:
        """Internal EVM pools implementation."""
        return await self._call_evm_method("get_pools", network, pool=pool, token=token, protocol=protocol, limit=limit)

    async def _evm_price_history(
        self,
        token: str,
        interval: Interval | str = Interval.ONE_DAY,
        days: int = 1,
        limit: int = 24,
        network: NetworkId | str | None = None,
    ) -> list[dict]:
        """Internal EVM price history implementation."""
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        return await self._call_evm_method(
            "get_ohlc_prices", network, token=token, interval=interval, start_time=start_time, limit=limit
        )

    async def _evm_pool_history(
        self,
        pool: str,
        interval: Interval | str = Interval.ONE_DAY,
        days: int = 1,
        limit: int = 24,
        network: NetworkId | str | None = None,
    ) -> list[dict]:
        """Internal EVM pool history implementation."""
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        return await self._call_evm_method(
            "get_ohlc_pools", network, pool=pool, interval=interval, start_time=start_time, limit=limit
        )

    async def _evm_token_holders(
        self, contract: str, limit: int = 10, network: NetworkId | str | None = None
    ) -> list[dict]:
        """Internal EVM token holders implementation."""
        return await self._call_evm_method("get_token_holders", network, contract=contract, limit=limit)

    # ===== SVM Internal Methods =====

    async def _svm_balances(
        self,
        token_account: str | None = None,
        mint: str | None = None,
        program_id: SolanaPrograms | str | None = None,
        limit: int = 10,
        network: SolanaNetworkId | str = SolanaNetworkId.SOLANA,
    ) -> list[dict]:
        """Internal SVM balances implementation."""
        return await self._call_svm_method(
            "get_balances", network, token_account=token_account, mint=mint, program_id=program_id, limit=limit
        )

    async def _svm_transfers(
        self,
        signature: str | None = None,
        program_id: SolanaPrograms | str | None = None,
        mint: str | None = None,
        authority: str | None = None,
        source: str | None = None,
        destination: str | None = None,
        limit: int = 10,
        network: SolanaNetworkId | str = SolanaNetworkId.SOLANA,
    ) -> list[dict]:
        """Internal SVM transfers implementation."""
        return await self._call_svm_method(
            "get_transfers",
            network,
            signature=signature,
            program_id=program_id,
            mint=mint,
            authority=authority,
            source=source,
            destination=destination,
            limit=limit,
        )

    async def _svm_swaps(
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
        limit: int = 10,
        network: SolanaNetworkId | str = SolanaNetworkId.SOLANA,
    ) -> list[dict]:
        """Internal SVM swaps implementation."""
        return await self._call_svm_method(
            "get_swaps",
            network,
            program_id=program_id,
            amm=amm,
            amm_pool=amm_pool,
            user=user,
            input_mint=input_mint,
            output_mint=output_mint,
            signature=signature,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    async def _svm_get_sol_price(
        self,
        include_stats: bool = False,
        network: SolanaNetworkId | str = SolanaNetworkId.SOLANA,
    ) -> float | dict[str, Any] | None:
        """Internal SVM SOL price implementation."""
        return await self._call_svm_method_direct("get_sol_price", network, include_stats=include_stats)  # type: ignore[no-any-return]

    # ===== Utility Methods =====

    async def version(self) -> list[dict[Any, Any]]:
        """Get API version information."""
        response = await self._api.get_version()
        return self._extract_data(response)

    async def networks(self) -> list[dict[Any, Any]]:
        """Get supported networks."""
        response = await self._api.get_networks()
        return self._extract_data(response)

    async def health(self) -> str:
        """Check API health status."""
        return await self._api.get_health()


# Make TokenAPI available as the main export
__all__ = ["TokenAPI"]
