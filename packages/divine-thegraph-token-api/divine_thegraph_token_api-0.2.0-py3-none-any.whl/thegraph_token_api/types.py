"""
Type definitions for The Graph Token API.

This module contains all TypedDict and enum definitions based on the OpenAPI 3.1.0 specification.
All types are designed for use with divine-type-enforcer for runtime validation.
"""

from enum import Enum
from typing import Any, TypedDict

# ===== Common Types =====


class StringEnum(str, Enum):
    """Base enum class that returns the value as string."""

    def __str__(self) -> str:
        return str(self.value)


class BaseResponse(TypedDict, total=False):
    """Base response structure for all API endpoints."""

    results: int | None  # Number of results returned
    statistics: dict[str, Any] | None
    duration_ms: float | None
    pagination: dict[str, Any] | None
    request_time: str | None
    total_results: int | None


class NetworkId(StringEnum):
    """Supported EVM network IDs."""

    ARBITRUM_ONE = "arbitrum-one"
    AVALANCHE = "avalanche"
    BASE = "base"
    BSC = "bsc"
    MAINNET = "mainnet"
    MATIC = "matic"
    OPTIMISM = "optimism"
    UNICHAIN = "unichain"


class SolanaNetworkId(StringEnum):
    """Supported SVM network IDs."""

    SOLANA = "solana"


class TokenStandard(StringEnum):
    """NFT token standards."""

    EMPTY = ""
    ERC721 = "ERC721"
    ERC1155 = "ERC1155"


class ActivityType(str, Enum):
    """NFT activity types."""

    TRANSFER = "TRANSFER"
    MINT = "MINT"
    BURN = "BURN"


class OrderDirection(StringEnum):
    """Order direction for sorting."""

    ASC = "asc"
    DESC = "desc"


class OrderBy(StringEnum):
    """Order by field."""

    TIMESTAMP = "timestamp"
    VALUE = "value"


class Interval(StringEnum):
    """Time intervals for OHLC data."""

    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"


class Protocol(StringEnum):
    """DEX protocols."""

    UNISWAP_V2 = "uniswap_v2"
    UNISWAP_V3 = "uniswap_v3"
    UNISWAP_V4 = "uniswap_v4"


class SolanaPrograms(StringEnum):
    """Solana program IDs."""

    TOKEN_2022 = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"  # nosec B105  # noqa: S105  # pragma: allowlist secret
    TOKEN = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # nosec B105  # noqa: S105  # pragma: allowlist secret


class SwapPrograms(StringEnum):
    """Solana swap program IDs."""

    RAYDIUM = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"  # Raydium Liquidity Pool V4  # pragma: allowlist secret
    PUMP_FUN_CORE = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"  # Pump.fun  # pragma: allowlist secret
    PUMP_FUN_AMM = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"  # Pump.fun AMM  # pragma: allowlist secret
    JUPITER_V4 = "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB"  # Jupiter Aggregator v4  # pragma: allowlist secret
    JUPITER_V6 = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"  # Jupiter Aggregator v6  # pragma: allowlist secret


class Currency(StringEnum):
    """Supported currencies for Unified Price API."""

    ETH = "ETH"
    SOL = "SOL"
    POL = "POL"


# ===== Common Response Structure =====


class Statistics(TypedDict, total=False):
    """API response statistics."""

    elapsed: float
    rows_read: float
    bytes_read: float


# Removed duplicate BaseResponse


# ===== NFT Types =====


class NFTAttribute(TypedDict):
    """NFT attribute/trait."""

    trait_type: str
    value: str
    display_type: str | None


class NFTOwnership(TypedDict):
    """NFT ownership record."""

    token_id: str
    token_standard: TokenStandard
    contract: str
    owner: str
    network_id: str  # API returns string format
    symbol: str | None
    uri: str | None
    name: str | None
    image: str | None
    description: str | None


class NFTOwnershipsResponse(BaseResponse):
    """Response for NFT ownerships endpoint."""

    data: list[NFTOwnership]


class NFTCollection(TypedDict, total=False):
    """NFT collection metadata."""

    contract: str
    contract_creation: str
    contract_creator: str
    name: str
    symbol: str
    owners: float
    total_supply: float
    total_unique_supply: float
    total_transfers: float
    network_id: str  # API returns string format
    token_standard: str | None  # API may include this field


class NFTCollectionsResponse(BaseResponse):
    """Response for NFT collections endpoint."""

    data: list[NFTCollection]


class NFTItem(TypedDict):
    """NFT item/token details."""

    token_id: str
    token_standard: TokenStandard
    contract: str
    owner: str
    network_id: str  # API returns string format
    uri: str | None
    name: str | None
    image: str | None
    description: str | None
    attributes: list[NFTAttribute] | None


class NFTItemsResponse(BaseResponse):
    """Response for NFT items endpoint."""

    data: list[NFTItem]


NFTActivity = TypedDict(
    "NFTActivity",
    {
        "@type": str,  # API uses @type field
        "block_num": float,
        "block_hash": str,
        "timestamp": str,
        "tx_hash": str,
        "contract": str,
        "symbol": str | None,
        "name": str | None,
        "from": str,  # API uses 'from' field
        "to": str,
        "token_id": str,
        "amount": float,
        "transfer_type": str | None,
        "token_standard": str | None,
    },
    total=False,
)


class NFTActivitiesResponse(BaseResponse):
    """Response for NFT activities endpoint."""

    data: list[NFTActivity]


class NFTHolder(TypedDict):
    """NFT holder information."""

    token_standard: str
    address: str
    quantity: float
    unique_tokens: float
    percentage: float
    network_id: str  # API returns string format


class NFTHoldersResponse(TypedDict):
    """Response for NFT holders endpoint."""

    data: list[NFTHolder]
    statistics: Statistics | None


class NFTSale(TypedDict):
    """NFT sale record."""

    timestamp: str
    block_num: float
    tx_hash: str
    token: str
    token_id: str
    symbol: str
    name: str
    offerer: str
    recipient: str
    sale_amount: float
    sale_currency: str


class NFTSalesResponse(TypedDict):
    """Response for NFT sales endpoint."""

    data: list[NFTSale]
    statistics: Statistics | None


# ===== Balance Types =====


class Balance(TypedDict):
    """Token balance record."""

    block_num: float
    datetime: str
    contract: str
    amount: str
    value: float
    network_id: str  # API returns string format
    symbol: str | None
    decimals: float | None
    price_usd: float | None
    value_usd: float | None
    low_liquidity: bool | None


class BalancesResponse(BaseResponse):
    """Response for balances endpoint."""

    data: list[Balance]


class SolanaBalance(TypedDict):
    """Solana token balance record."""

    block_num: float
    datetime: str
    timestamp: float
    program_id: str
    token_account: str
    mint: str
    amount: str
    value: float
    decimals: float
    network_id: str  # API returns string format


class SolanaBalancesResponse(BaseResponse):
    """Response for Solana balances endpoint."""

    data: list[SolanaBalance]


# ===== Transfer Types =====

Transfer = TypedDict(
    "Transfer",
    {
        "block_num": float,
        "datetime": str,
        "timestamp": float,
        "transaction_id": str,
        "contract": str,
        "from": str,  # API uses 'from' field
        "to": str,
        "value": float,  # API uses 'value' not 'amount'
        "symbol": str | None,
        "decimals": float | None,
    },
    total=False,
)


class TransfersResponse(BaseResponse):
    """Response for transfers endpoint."""

    data: list[Transfer]


class SolanaTransfer(TypedDict):
    """Solana token transfer record."""

    block_num: float
    datetime: str
    timestamp: float
    signature: str
    program_id: str
    mint: str
    authority: str
    source: str
    destination: str
    amount: str
    value: float
    decimals: float | None
    network_id: str  # API returns string format


class SolanaTransfersResponse(BaseResponse):
    """Response for Solana transfers endpoint."""

    data: list[SolanaTransfer]


# ===== Token Types =====


class TokenIcon(TypedDict):
    """Token icon information."""

    web3icon: str


class Token(TypedDict, total=False):
    """Token metadata."""

    block_num: float
    datetime: str
    contract: str
    circulating_supply: str | float  # API can return either
    holders: float
    network_id: str  # API returns string format
    icon: TokenIcon | None
    symbol: str | None
    name: str | None
    decimals: float | None
    price_usd: float | None
    market_cap: float | None
    low_liquidity: bool | None


class TokensResponse(BaseResponse):
    """Response for tokens endpoint."""

    data: list[Token]


class TokenHolder(TypedDict):
    """Token holder information."""

    block_num: float
    datetime: str
    address: str
    amount: str
    value: float
    network_id: str  # API returns string format
    symbol: str | None
    decimals: float | None
    price_usd: float | None
    value_usd: float | None
    low_liquidity: bool | None


class TokenHoldersResponse(TypedDict):
    """Response for token holders endpoint."""

    data: list[TokenHolder]
    statistics: Statistics | None


# ===== Swap Types =====


class SwapToken(TypedDict):
    """Token information in swap."""

    address: str
    symbol: str
    decimals: float


class Swap(TypedDict, total=False):
    """DEX swap record."""

    block_num: float
    datetime: str
    timestamp: float
    network_id: str  # API returns different format than we send
    transaction_id: str
    caller: str
    sender: str
    recipient: str | None
    factory: str
    pool: str
    token0: SwapToken
    token1: SwapToken
    amount0: str
    amount1: str
    price0: float
    price1: float
    value0: float
    value1: float
    fee: str | None
    protocol: str


class SwapsResponse(BaseResponse):
    """Response for swaps endpoint."""

    data: list[Swap]


class SolanaMint(TypedDict):
    """Solana mint information."""

    address: str
    symbol: str
    decimals: float


class SolanaSwap(TypedDict, total=False):
    """Solana swap record."""

    block_num: float
    datetime: str
    timestamp: float
    transaction_index: float | None
    instruction_index: float | None
    signature: str
    program_id: str
    program_name: str
    user: str
    amm: str
    amm_name: str
    amm_pool: str | None
    input_mint: SolanaMint | str  # API can return either dict or string
    input_amount: float
    output_mint: SolanaMint | str  # API can return either dict or string
    output_amount: float
    network_id: str  # API returns string format


class SolanaSwapsResponse(BaseResponse):
    """Response for Solana swaps endpoint."""

    data: list[SolanaSwap]


# ===== Pool Types =====


class Pool(TypedDict):
    """Liquidity pool information."""

    block_num: float
    datetime: str
    network_id: str  # API returns string format
    transaction_id: str
    factory: str
    pool: str
    token0: SwapToken
    token1: SwapToken
    fee: float
    protocol: str


class PoolsResponse(BaseResponse):
    """Response for pools endpoint."""

    data: list[Pool]


# ===== OHLC Types =====


class OHLC(TypedDict):
    """OHLC price data."""

    datetime: str
    ticker: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    uaw: float
    transactions: float


class OHLCResponse(BaseResponse):
    """Response for OHLC endpoints."""

    data: list[OHLC]


# ===== Historical Types =====


class HistoricalBalance(TypedDict):
    """Historical balance data."""

    datetime: str
    contract: str
    name: str
    symbol: str
    decimals: str
    open: float
    high: float
    low: float
    close: float


class HistoricalBalancesResponse(TypedDict):
    """Response for historical balances endpoint."""

    data: list[HistoricalBalance]
    statistics: Statistics | None


# ===== Monitoring Types =====


class ErrorResponse(TypedDict):
    """Error response structure."""

    status: int
    code: str
    message: str


class VersionResponse(TypedDict):
    """Version information response."""

    version: str
    date: str
    commit: str


class NetworkIcon(TypedDict):
    """Network icon information."""

    web3Icons: dict[str, Any]


class Network(TypedDict):
    """Network information."""

    id: str
    fullName: str
    shortName: str
    caip2Id: str
    networkType: str
    icon: NetworkIcon
    alias: list[str]


class NetworksResponse(TypedDict):
    """Response for networks endpoint."""

    networks: list[Network]


# ===== Export All Types =====

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
    "Swap",
    "SwapPrograms",
    "SwapToken",
    "SwapsResponse",
    "Token",
    "TokenHolder",
    "TokenHoldersResponse",
    "TokenIcon",
    "TokenStandard",
    "TokensResponse",
    "Transfer",
    "TransfersResponse",
    "VersionResponse",
]
