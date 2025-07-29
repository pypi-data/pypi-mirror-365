"""
The Graph Token API Client.

A clean, separated Python client for The Graph Token API with EVM and SVM support.
Built with divine-typed-requests for reliable HTTP handling and divine-type-enforcer
for robust runtime type validation.

Usage:
    ```python
    import anyio
    from thegraph_token_api import TokenAPI, SwapPrograms, Protocol

    async def main():
        api = TokenAPI()  # Auto-loads from .env

        # EVM chains (Ethereum, Polygon, BSC, etc.)
        eth_balances = await api.evm.balances("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
        eth_nfts = await api.evm.nfts.ownerships("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
        nft_collection = await api.evm.nfts.collection("0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb")
        eth_swaps = await api.evm.swaps(protocol=Protocol.UNISWAP_V3, limit=5)

        # SVM (Solana)
        sol_balances = await api.svm.balances(mint="So11111111111111111111111111111111111111112")
        sol_swaps = await api.svm.swaps(program_id=SwapPrograms.RAYDIUM, limit=5)
        sol_price = await api.svm.get_sol_price()  # Get current SOL price with smart caching

        # Utility
        health = await api.health()

    anyio.run(main)
    ```
"""

# Explicit imports from models module
from .models import (
    NFTActivity,
    Transfer,
)
from .simple import TokenAPI  # Main simplified interface

# Explicit imports from types module
from .types import (
    OHLC,
    ActivityType,
    Balance,
    BalancesResponse,
    BaseResponse,
    ErrorResponse,
    HistoricalBalance,
    HistoricalBalancesResponse,
    Interval,
    Network,
    NetworkId,
    NetworksResponse,
    NFTActivitiesResponse,
    NFTAttribute,
    NFTCollection,
    NFTCollectionsResponse,
    NFTHolder,
    NFTHoldersResponse,
    NFTItem,
    NFTItemsResponse,
    NFTOwnership,
    NFTOwnershipsResponse,
    NFTSale,
    NFTSalesResponse,
    OHLCResponse,
    OrderBy,
    OrderDirection,
    Pool,
    PoolsResponse,
    Protocol,
    SolanaBalance,
    SolanaBalancesResponse,
    SolanaMint,
    SolanaNetworkId,
    SolanaPrograms,
    SolanaSwap,
    SolanaSwapsResponse,
    SolanaTransfer,
    SolanaTransfersResponse,
    Statistics,
    StringEnum,
    Swap,
    SwapPrograms,
    SwapsResponse,
    SwapToken,
    Token,
    TokenHolder,
    TokenHoldersResponse,
    TokenIcon,
    TokensResponse,
    TokenStandard,
    TransfersResponse,
    VersionResponse,
)

__version__ = "0.1.22"
__all__ = [
    "OHLC",
    "ActivityType",
    "Balance",
    "BalancesResponse",
    "BaseResponse",
    "ErrorResponse",
    "HistoricalBalance",
    "HistoricalBalancesResponse",
    "Interval",
    "NFTActivitiesResponse",
    "NFTActivity",
    "NFTAttribute",
    "NFTCollection",
    "NFTCollectionsResponse",
    "NFTHolder",
    "NFTHoldersResponse",
    "NFTItem",
    "NFTItemsResponse",
    "NFTOwnership",
    "NFTOwnershipsResponse",
    "NFTSale",
    "NFTSalesResponse",
    "Network",
    "NetworkId",
    "NetworksResponse",
    "OHLCResponse",
    "OrderBy",
    "OrderDirection",
    "Pool",
    "PoolsResponse",
    "Protocol",
    "SolanaBalance",
    "SolanaBalancesResponse",
    "SolanaMint",
    "SolanaNetworkId",
    "SolanaPrograms",
    "SolanaSwap",
    "SolanaSwapsResponse",
    "SolanaTransfer",
    "SolanaTransfersResponse",
    "Statistics",
    "StringEnum",
    "Swap",
    "SwapPrograms",
    "SwapToken",
    "SwapsResponse",
    "Token",
    "TokenAPI",
    "TokenHolder",
    "TokenHoldersResponse",
    "TokenIcon",
    "TokenStandard",
    "TokensResponse",
    "Transfer",
    "TransfersResponse",
    "VersionResponse",
]
