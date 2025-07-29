"""
The Graph Token API Client.

A comprehensive, type-safe client for The Graph Token API with elegant EVM/SVM separation.
Provides both unified access and specialized network-specific clients.
"""

from .base import BaseTokenAPI
from .evm import EVMTokenAPI
from .svm import SVMTokenAPI
from .types import NetworkId, SolanaNetworkId
from .unified_price_api import UnifiedPriceAPI


class TheGraphTokenAPI(BaseTokenAPI):
    """
    Unified client for The Graph Token API with elegant EVM/SVM separation.

    Provides factory methods to create specialized network clients and direct access
    to monitoring endpoints. This is the main entry point for the API.

    Examples:
        ```python
        import anyio
        from thegraph_client import TheGraphTokenAPI, NetworkId, SolanaNetworkId

        async def main():
            # Method 1: Create specialized clients
            api = TheGraphTokenAPI(api_key="your_bearer_token")

            # Get EVM client for specific network
            evm = api.evm(NetworkId.MAINNET)
            async with evm:
                ownerships = await evm.get_nft_ownerships(
                    address="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                )

            # Get SVM client for Solana
            svm = api.svm(SolanaNetworkId.SOLANA)
            async with svm:
                balances = await svm.get_balances(
                    token_account="4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A"
                )

            # Method 2: Direct instantiation
            async with TheGraphTokenAPI.create_evm_client(
                network=NetworkId.BASE,
                api_key="your_bearer_token"
            ) as base_api:
                transfers = await base_api.get_transfers()

        anyio.run(main)
        ```
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        """
        Initialize The Graph Token API client.

        Args:
            api_key: Bearer token for API authentication
            base_url: API base URL (optional)
        """
        super().__init__(api_key, base_url)

    # ===== Factory Methods =====

    def evm(self, network: NetworkId | str) -> EVMTokenAPI:
        """
        Create an EVM-specific client for the given network.

        Args:
            network: EVM network (e.g., NetworkId.MAINNET, NetworkId.BASE)

        Returns:
            EVMTokenAPI instance configured for the specified network

        Example:
            ```python
            api = TheGraphTokenAPI(api_key="your_key")
            mainnet = api.evm(NetworkId.MAINNET)
            base = api.evm(NetworkId.BASE)

            async with mainnet:
                nfts = await mainnet.get_nft_ownerships("0x...")
            ```
        """
        return EVMTokenAPI(network=network, api_key=self.api_key, base_url=self.base_url)

    def svm(self, network: SolanaNetworkId | str = SolanaNetworkId.SOLANA) -> SVMTokenAPI:
        """
        Create an SVM-specific client for Solana.

        Args:
            network: SVM network (default: SolanaNetworkId.SOLANA)

        Returns:
            SVMTokenAPI instance configured for Solana

        Example:
            ```python
            api = TheGraphTokenAPI(api_key="your_key")
            solana = api.svm()

            async with solana:
                balances = await solana.get_balances(token_account="...")
            ```
        """
        return SVMTokenAPI(network=network, api_key=self.api_key, base_url=self.base_url)

    # ===== Class Methods for Direct Instantiation =====

    @classmethod
    def create_evm_client(
        cls, network: NetworkId | str, api_key: str | None = None, base_url: str | None = None
    ) -> EVMTokenAPI:
        """
        Create an EVM client directly without main API instance.

        Args:
            network: EVM network to use
            api_key: Bearer token for API authentication
            base_url: API base URL (optional)

        Returns:
            EVMTokenAPI instance

        Example:
            ```python
            async with TheGraphTokenAPI.create_evm_client(
                network=NetworkId.MAINNET,
                api_key="your_key"
            ) as api:
                nfts = await api.get_nft_ownerships("0x...")
            ```
        """
        return EVMTokenAPI(network=network, api_key=api_key, base_url=base_url)

    @classmethod
    def create_svm_client(
        cls,
        network: SolanaNetworkId | str = SolanaNetworkId.SOLANA,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> SVMTokenAPI:
        """
        Create an SVM client directly without main API instance.

        Args:
            network: SVM network to use (default: SolanaNetworkId.SOLANA)
            api_key: Bearer token for API authentication
            base_url: API base URL (optional)

        Returns:
            SVMTokenAPI instance

        Example:
            ```python
            async with TheGraphTokenAPI.create_svm_client(
                api_key="your_key"
            ) as api:
                swaps = await api.get_swaps(program_id=SwapPrograms.RAYDIUM)
            ```
        """
        return SVMTokenAPI(network=network, api_key=api_key, base_url=base_url)

    # ===== Unified Price API =====

    @property
    def price(self) -> UnifiedPriceAPI:
        """
        Get Unified Price API for multi-blockchain price calculation.

        Returns:
            UnifiedPriceAPI instance for getting cryptocurrency prices

        Example:
            ```python
            async def main():
                api = TheGraphTokenAPI(api_key="your_key")

                # Simple price queries
                eth_price = await api.price.get(Currency.ETH)
                sol_price = await api.price.get(Currency.SOL)

                # With detailed statistics
                eth_stats = await api.price.get(Currency.ETH, include_stats=True)
                print(f"ETH: ${eth_stats['price']:.2f} (confidence: {eth_stats['confidence']:.0%})")
            ```
        """
        return UnifiedPriceAPI(self)
