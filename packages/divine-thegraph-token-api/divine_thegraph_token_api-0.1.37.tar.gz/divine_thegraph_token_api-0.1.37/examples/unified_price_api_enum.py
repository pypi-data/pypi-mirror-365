#!/usr/bin/env python3
"""
Unified Price API Example with Currency Enum

Demonstrates the new Unified Price API using proper Currency enum
instead of string parsing for type safety and cleaner code.
"""

import os
import sys
import traceback
from pathlib import Path

import anyio
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from thegraph_token_api import Currency, TokenAPI

# Load environment variables
load_dotenv()


async def demo_simple_enum_prices(api: TokenAPI) -> None:
    """Demonstrate simple price queries using Currency enum."""
    print("\n📊 Simple Price Queries (Currency Enum)")
    print("-" * 40)

    print("🔍 Fetching current prices...")

    # Get ETH price using Currency enum
    eth_price = await api.price.get(Currency.ETH)
    if eth_price:
        print(f"💎 ETH: ${eth_price:.2f}")
    else:
        print("❌ ETH price unavailable")

    # Get SOL price using Currency enum
    sol_price = await api.price.get(Currency.SOL)
    if sol_price:
        print(f"☀️  SOL: ${sol_price:.2f}")
    else:
        print("❌ SOL price unavailable")

    # Get POL price using Currency enum (new!)
    pol_price = await api.price.get(Currency.POL)
    if pol_price:
        print(f"🔷  POL: ${pol_price:.2f}")
    else:
        print("❌ POL price unavailable")


async def demo_type_safety(api: TokenAPI) -> None:
    """Demonstrate type safety with Currency enum."""
    print("\n🛡️  Type Safety Demo")
    print("-" * 21)

    # Enum-only interface - no string acceptance
    print("✅ API accepts only Currency enums - no backward compatibility")
    print("   Example: Currency.ETH, Currency.SOL, Currency.POL")

    # Show POL support check
    pol_supported = await api.price.is_supported(Currency.POL)
    print(f"🔷  POL supported: {'✅ Yes' if pol_supported else '❌ No'}")


async def demo_supported_currencies_enum(api: TokenAPI) -> None:
    """Demonstrate supported currencies with enum."""
    print("\n🗂️  Supported Currencies")
    print("-" * 24)

    supported = await api.price.get_supported_currencies()
    print("✅ Currently supported Currency enums:")
    for currency in supported:
        print(f"   • Currency.{currency.value}")


async def demo_advanced_enum_usage(api: TokenAPI) -> None:
    """Demonstrate advanced usage with statistics using enum."""
    print("\n📈 Advanced Usage with Statistics")
    print("-" * 35)

    # Get detailed stats using enum
    eth_stats = await api.price.get(Currency.ETH, include_stats=True)

    if eth_stats:
        print("💎 ETH Detailed Analysis:")
        print(f"   💰 Price: ${eth_stats['price']:.2f}")
        print(f"   📊 Confidence: {eth_stats['confidence']:.0%}")
        print(f"   📈 Trades analyzed: {eth_stats['trades_analyzed']}")
        print(f"   📉 Volatility: ${eth_stats['std_deviation']:.2f}")
        print(f"   📋 Range: ${eth_stats['min_price']:.2f} - ${eth_stats['max_price']:.2f}")
    else:
        print("❌ ETH detailed analysis unavailable")


async def demo_cache_management(api: TokenAPI) -> None:
    """Demonstrate cache management features."""
    print("\n⚡ Cache Management")
    print("-" * 18)

    # Check what's supported
    eth_supported = await api.price.is_supported(Currency.ETH)

    print(f"📊 Currency.ETH supported: {'✅ Yes' if eth_supported else '❌ No'}")
    print("🔒 Only Currency enum values accepted - enhanced type safety")

    # Cache clearing
    print("\n🗑️  Cache Management:")
    print("   • Clear specific: await api.price.clear_cache(Currency.ETH)")
    print("   • Clear all: await api.price.clear_cache()")


def print_enum_demo_summary() -> None:
    """Print the enum demo summary and benefits."""
    print("\n🎉 Currency Enum Demo Complete!")
    print("\n💡 Key Benefits of Currency Enum:")
    print("   • Type safety at compile time")
    print("   • IDE autocomplete support")
    print("   • No string parsing errors")
    print("   • Clear API contracts")
    print("   • Enhanced security - no backward compatibility")
    print("   • Easy to extend (now supports ETH, SOL, POL)")

    print("\n📝 Example usage patterns:")
    print("   # Type-safe enum usage only")
    print("   eth_price = await api.price.get(Currency.ETH)")
    print("   sol_stats = await api.price.get(Currency.SOL, include_stats=True)")
    print("   pol_price = await api.price.get(Currency.POL)  # New!")
    print("   ")
    print("   # Get all supported currencies")
    print("   currencies = await api.price.get_supported_currencies()")
    print("   # Currently: [Currency.ETH, Currency.SOL, Currency.POL]")


async def main():
    """Demonstrate Unified Price API with Currency enum."""
    print("🌟 Unified Price API Demo (Currency Enum)")
    print("=" * 45)

    # Check for API key
    api_key = os.environ.get("THEGRAPH_API_KEY")
    if not api_key:
        print("❌ Error: THEGRAPH_API_KEY not found in environment")
        print("💡 Get a free API key at: https://thegraph.market")
        return

    # Initialize the API
    api = TokenAPI(api_key=api_key)

    try:
        await demo_simple_enum_prices(api)
        await demo_type_safety(api)
        await demo_supported_currencies_enum(api)
        await demo_advanced_enum_usage(api)
        await demo_cache_management(api)
        print_enum_demo_summary()

    except (ConnectionError, TimeoutError, ValueError) as e:
        print(f"❌ Demo failed with error: {e}")
        traceback.print_exc()
    except Exception as e:  # noqa: BLE001
        print(f"❌ Demo failed with unexpected error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    anyio.run(main)
