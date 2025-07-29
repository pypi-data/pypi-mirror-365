#!/usr/bin/env python3
"""
Helper functions for token-api examples.

This module provides common utility functions used across examples
to format data, handle timestamps, and display information cleanly.
"""

from datetime import datetime


def format_amount(value, precision=2):
    """
    Format large numbers with K/M suffixes for readability.

    Args:
        value: Numeric value to format
        precision: Decimal places (default: 2)

    Returns:
        Formatted string (e.g., "1.5M", "234.6K", "45.67")
    """
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.{precision}f}"


def format_time(timestamp):
    """
    Convert Unix timestamp to readable time format.

    Args:
        timestamp: Unix timestamp (int/float)

    Returns:
        Time string in HH:MM format, or "??:??" if invalid
    """
    try:
        return datetime.fromtimestamp(timestamp).strftime("%H:%M")
    except (ValueError, TypeError, OSError):
        return "??:??"


def format_date(timestamp):
    """
    Convert Unix timestamp to readable date format.

    Args:
        timestamp: Unix timestamp (int/float)

    Returns:
        Date string in MM/DD format, or "??/??" if invalid
    """
    try:
        return datetime.fromtimestamp(timestamp).strftime("%m/%d")
    except (ValueError, TypeError, OSError):
        return "??/??"


def shorten_address(address, length=6):
    """
    Shorten blockchain address for display.

    Args:
        address: Full blockchain address
        length: Number of characters to show (default: 6)

    Returns:
        Shortened address with "..." (e.g., "0x1234...")
    """
    if not address or len(address) <= length + 3:
        return str(address)
    return str(address)[:length] + "..."


def shorten_id(token_id, max_length=6):
    """
    Shorten long token IDs for display.

    Args:
        token_id: Token ID (any type)
        max_length: Maximum length before shortening

    Returns:
        Shortened ID string
    """
    id_str = str(token_id)
    if len(id_str) <= max_length:
        return id_str
    return id_str[:max_length] + "..."


def get_symbol(mint_obj, fallback_length=6):
    """
    Get token symbol from mint object, with fallback to shortened address.

    Args:
        mint_obj: Token mint object (may have .symbol attribute)
        fallback_length: Length for fallback address shortening

    Returns:
        Token symbol or shortened address
    """
    if hasattr(mint_obj, "symbol") and mint_obj.symbol:
        return mint_obj.symbol
    return shorten_address(str(mint_obj), fallback_length)


def format_price_change(open_price, close_price):
    """
    Calculate and format price change percentage.

    Args:
        open_price: Opening price
        close_price: Closing price

    Returns:
        Formatted percentage string (e.g., "+2.5%", "-1.8%")
    """
    if not open_price or open_price == 0:
        return "±0.0%"

    change = ((close_price - open_price) / open_price) * 100
    return f"{change:+.1f}%"


def print_header(title, emoji=""):
    """
    Print a formatted header for examples.

    Args:
        title: Header title
        emoji: Optional emoji prefix
    """
    full_title = f"{emoji} {title}" if emoji else title
    print(full_title)
    print("=" * len(full_title))


def print_section(title, emoji=""):
    """
    Print a formatted section header.

    Args:
        title: Section title
        emoji: Optional emoji prefix
    """
    full_title = f"{emoji} {title}" if emoji else title
    print(f"\n{full_title}:")


# Common wallet addresses for examples
WALLETS = {
    "vitalik": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "imagine_token": "0x6A1B2AE3a55B5661b40d86c2bF805f7DAdB16978",
    "cryptopunks": "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb",
    "link_token": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "uniswap_pool": "0x3E456E2A71adafb6fe0AF8098334ee41ef53A7C6",
}

# Common Solana mint addresses
SOLANA_MINTS = {
    "sol": "So11111111111111111111111111111111111111112",
    "usdc": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # pragma: allowlist secret
}
