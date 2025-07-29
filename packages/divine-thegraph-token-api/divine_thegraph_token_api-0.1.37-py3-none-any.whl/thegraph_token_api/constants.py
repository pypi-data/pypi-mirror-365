"""
Constants for Unified Price API system.

Contains token addresses, DEX configurations, and other constants used across
different blockchain implementations for price calculation.
"""

from dataclasses import dataclass
from typing import Any

from .types import Currency, Protocol, SwapPrograms

# ===== Ethereum Mainnet Token Addresses =====

# Native and wrapped ETH
ETH_ADDRESS = "0x0000000000000000000000000000000000000000"  # Native ETH (zero address)
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # Wrapped ETH

# Stablecoins on Ethereum
USDC_ETH_ADDRESS = "0xA0b86a33E7c473D00e05A7B8A4bcF1e50e93D1Af"  # USDC on Ethereum
USDT_ETH_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT on Ethereum

# POL (previously MATIC) on Ethereum
POL_ETH_ADDRESS = "0x455e53908438CC0ad355CA94c63FEcF6F5F44E3c"  # POL token on Ethereum

# ===== Solana Token Addresses =====

# Native SOL and stablecoins (existing from svm.py)
SOL_MINT = "So11111111111111111111111111111111111111112"  # Native SOL
USDC_SOL_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC on Solana


@dataclass
class TokenConfig:
    """Configuration for a token on a specific blockchain."""

    address: str
    symbol: str
    decimals: int
    blockchain: str  # "ethereum" or "solana"


@dataclass
class DEXConfig:
    """Configuration for DEX-specific price calculation."""

    protocol: Protocol | SwapPrograms | str
    preferred_pairs: list[tuple[str, str]]  # List of (token1, token2) pairs to try
    min_liquidity_threshold: float = 1000.0  # Minimum USD value for valid swaps


# ===== Token Configurations =====

TOKEN_CONFIGS = {
    "ETH": TokenConfig(
        address=WETH_ADDRESS,  # Use WETH for swap calculations
        symbol="ETH",
        decimals=18,
        blockchain="ethereum",
    ),
    "SOL": TokenConfig(address=SOL_MINT, symbol="SOL", decimals=9, blockchain="solana"),
    "POL": TokenConfig(address=POL_ETH_ADDRESS, symbol="POL", decimals=18, blockchain="ethereum"),
    "USDC_ETH": TokenConfig(address=USDC_ETH_ADDRESS, symbol="USDC", decimals=6, blockchain="ethereum"),
    "USDC_SOL": TokenConfig(address=USDC_SOL_MINT, symbol="USDC", decimals=6, blockchain="solana"),
}

# ===== DEX Configurations =====

DEX_CONFIGS = {
    "ethereum": DEXConfig(
        protocol=Protocol.UNISWAP_V3,  # Most liquid for ETH/USDC
        preferred_pairs=[
            (WETH_ADDRESS, USDC_ETH_ADDRESS),  # WETH/USDC is most liquid
            (ETH_ADDRESS, USDC_ETH_ADDRESS),  # Native ETH/USDC as fallback
        ],
        min_liquidity_threshold=5000.0,  # Higher threshold for Ethereum due to gas costs
    ),
    "solana": DEXConfig(
        protocol=SwapPrograms.JUPITER_V6,  # Best aggregated liquidity
        preferred_pairs=[
            (SOL_MINT, USDC_SOL_MINT),  # SOL/USDC primary pair
        ],
        min_liquidity_threshold=1000.0,  # Lower threshold for Solana
    ),
}

# ===== Price Calculation Settings =====


@dataclass
class PriceSettings:
    """Settings for price calculation algorithms."""

    base_trades: int = 100  # Base number of trades to sample
    base_minutes: int = 15  # Base time window in minutes
    max_trades: int = 500  # Maximum trades to sample
    max_minutes: int = 120  # Maximum time window in minutes
    min_sample_size: int = 3  # Minimum trades needed for price calculation
    outlier_threshold: tuple[float, float] = (10.0, 10000.0)  # (min_price, max_price) sanity check
    confidence_threshold: float = 0.1  # Minimum confidence score (0-1)
    cache_ttl_volatile: int = 60  # Cache TTL for volatile markets (seconds)
    cache_ttl_stable: int = 300  # Cache TTL for stable markets (seconds)
    volatility_threshold: float = 0.05  # Volatility threshold for cache TTL selection


# Default price settings
DEFAULT_PRICE_SETTINGS = PriceSettings()

# ===== Supported Currencies =====

SUPPORTED_CURRENCIES = {
    Currency.ETH: {
        "blockchain": "ethereum",
        "token_config": TOKEN_CONFIGS["ETH"],
        "dex_config": DEX_CONFIGS["ethereum"],
        "base_pair": TOKEN_CONFIGS["USDC_ETH"],
    },
    Currency.SOL: {
        "blockchain": "solana",
        "token_config": TOKEN_CONFIGS["SOL"],
        "dex_config": DEX_CONFIGS["solana"],
        "base_pair": TOKEN_CONFIGS["USDC_SOL"],
    },
    Currency.POL: {
        "blockchain": "ethereum",
        "token_config": TOKEN_CONFIGS["POL"],
        "dex_config": DEX_CONFIGS["ethereum"],
        "base_pair": TOKEN_CONFIGS["USDC_ETH"],
    },
}

# ===== Helper Functions =====


def get_currency_config(currency: Currency | str) -> dict[str, Any] | None:
    """Get configuration for a supported currency."""
    if isinstance(currency, str):
        # Try to convert string to Currency enum
        try:
            currency = Currency(currency.upper())
        except ValueError:
            return None
    return SUPPORTED_CURRENCIES.get(currency)


def is_currency_supported(currency: Currency | str) -> bool:
    """Check if a currency is supported."""
    if isinstance(currency, str):
        try:
            currency = Currency(currency.upper())
        except ValueError:
            return False
    return currency in SUPPORTED_CURRENCIES
