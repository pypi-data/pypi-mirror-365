#!/usr/bin/env python3
"""
Unified Price API Demo - Multi-Blockchain Cryptocurrency Prices

Demonstrates the Unified Price API that supports cryptocurrency price fetching
across multiple blockchains using a single, type-safe Currency enum interface.

Features:
- Type-safe Currency enum (Currency.ETH, Currency.SOL, Currency.POL, Currency.BNB, Currency.AVAX)
- Multi-blockchain support (Ethereum, Solana, Polygon, BSC, Avalanche)
- Smart caching with volatility-based TTL
- Detailed statistical analysis with confidence metrics
- Automatic outlier filtering and progressive retry logic
- No backward compatibility - enum-only interface for enhanced security
"""

import os
import sys
import time
import traceback
from pathlib import Path

import anyio
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from thegraph_token_api import Currency, TokenAPI

# Load environment variables
load_dotenv()


async def demo_all_supported_currencies(api: TokenAPI) -> None:
    """Demonstrate price fetching for all supported currencies."""
    print("\n💰 All Supported Cryptocurrency Prices")
    print("-" * 42)

    print("🔍 Fetching current prices using Currency enum...")

    # All supported currencies with their networks
    currencies = [
        (Currency.ETH, "💎", "Ethereum"),
        (Currency.SOL, "☀️", "Solana"),
        (Currency.POL, "🔷", "Polygon"),
        (Currency.BNB, "💛", "BSC"),
        (Currency.AVAX, "🔺", "Avalanche"),
    ]

    for currency, emoji, network in currencies:
        try:
            price = await api.price.get(currency)
            if price:
                print(f"{emoji}  {currency.value}: ${price:.2f} ({network})")
            else:
                print(f"❌ {currency.value} price unavailable ({network})")
        except Exception as e:  # noqa: BLE001
            print(f"❌ {currency.value} error: {e} ({network})")


async def demo_type_safety_and_enum_benefits(api: TokenAPI) -> None:
    """Demonstrate type safety and Currency enum benefits."""
    print("\n🛡️  Type Safety & Enum Benefits")
    print("-" * 33)

    print("✅ Currency Enum Enforcement:")
    print("   • Only Currency.* enums accepted - no strings!")
    print("   • Enhanced type safety at compile time")
    print("   • IDE autocomplete support")
    print("   • No string parsing errors")
    print("   • Clear API contracts")

    # Show supported currencies
    supported = await api.price.get_supported_currencies()
    print(f"\n🗂️  Currently supported: {len(supported)} currencies")
    for currency in supported:
        supported_check = await api.price.is_supported(currency)
        status = "✅" if supported_check else "❌"
        print(f"   {status} Currency.{currency.value}")

    print("\n💡 Example usage:")
    print("   price = await api.price.get(Currency.ETH)  # ✅ Correct")
    print("   price = await api.price.get('ETH')         # ❌ TypeError!")


async def demo_detailed_statistical_analysis(api: TokenAPI) -> None:
    """Demonstrate detailed price analysis with statistics."""
    print("\n📈 Detailed Statistical Analysis")
    print("-" * 34)

    # Analyze ETH with full statistics
    print("🔍 Analyzing ETH price data...")
    eth_stats = await api.price.get(Currency.ETH, include_stats=True)

    if eth_stats:
        print("💎 ETH Detailed Analysis:")
        print(f"   💰 Price: ${eth_stats['price']:.2f}")
        print(f"   📊 Confidence: {eth_stats['confidence']:.0%}")
        print(f"   📈 Trades analyzed: {eth_stats['trades_analyzed']}")
        print(f"   📉 Volatility: ${eth_stats['std_deviation']:.2f}")
        print(f"   📋 Range: ${eth_stats['min_price']:.2f} - ${eth_stats['max_price']:.2f}")

        # Confidence interpretation
        conf = eth_stats["confidence"]
        if conf >= 0.8:
            print("   🟢 High confidence - excellent data quality")
        elif conf >= 0.5:
            print("   🟡 Medium confidence - good data quality")
        else:
            print("   🟠 Low confidence - limited data available")
    else:
        print("❌ ETH detailed analysis unavailable")

    # Quick comparison with SOL
    print("\n🔍 Quick SOL comparison...")
    sol_stats = await api.price.get(Currency.SOL, include_stats=True)
    if sol_stats:
        print("☀️  SOL Analysis:")
        print(f"   💰 Price: ${sol_stats['price']:.2f}")
        print(f"   📊 Confidence: {sol_stats['confidence']:.0%}")
        print(f"   📈 Trades: {sol_stats['trades_analyzed']}")


async def demo_smart_caching_performance(api: TokenAPI) -> None:
    """Demonstrate smart caching with performance metrics."""
    print("\n⚡ Smart Caching Performance")
    print("-" * 29)

    # First call (fetches from DEX data)
    print("🌐 First call (fetching from blockchain)...")
    start = time.time()
    price1 = await api.price.get(Currency.ETH)
    time1 = time.time() - start

    # Second call (uses cache)
    print("⚡ Second call (using cache)...")
    start = time.time()
    price2 = await api.price.get(Currency.ETH)
    time2 = time.time() - start

    if price1 and price2:
        print("📊 Performance Results:")
        print(f"   🌐 Blockchain call: ${price1:.2f} - {time1:.3f}s")
        print(f"   ⚡ Cached response: ${price2:.2f} - {time2:.3f}s")

        if time1 > time2 > 0:
            speedup = time1 / time2
            print(f"   🚀 Cache speedup: {speedup:.0f}x faster!")
        elif time2 == 0:
            print("   🚀 Cache speedup: ∞x faster (instant response)!")

        print("\n💡 Caching Features:")
        print("   • Volatility-based TTL (more volatile = shorter cache)")
        print("   • Per-currency independent caching")
        print("   • Automatic cache invalidation")

    # Cache management demo
    print("\n🗑️  Cache Management:")
    print("   await api.price.clear_cache(Currency.ETH)  # Clear specific")
    print("   await api.price.clear_cache()              # Clear all")


async def demo_error_handling_and_robustness(_api: TokenAPI) -> None:
    """Demonstrate error handling and API robustness."""
    print("\n🛡️  Error Handling & Robustness")
    print("-" * 35)

    print("✅ Built-in Error Handling:")
    print("   • Progressive retry with adaptive sampling")
    print("   • Automatic outlier filtering")
    print("   • Fallback strategies for network issues")
    print("   • Confidence-based result validation")

    print("\n🔒 Security Features:")
    print("   • No backward compatibility (strings rejected)")
    print("   • Type-safe enum-only interface")
    print("   • Input validation at API boundaries")

    # Show what happens with invalid input (in documentation, not actual call)
    print("\n❌ Invalid Usage Examples:")
    print("   await api.price.get('ETH')        # TypeError: Must use Currency enum")
    print("   await api.price.get(123)          # TypeError: Must use Currency enum")
    print("   await api.price.get(None)         # TypeError: Must use Currency enum")

    print("\n✅ Correct Usage:")
    print("   await api.price.get(Currency.ETH) # ✅ Type-safe and validated")


def print_comprehensive_summary() -> None:
    """Print comprehensive demo summary."""
    print("\n🎉 Unified Price API Demo Complete!")
    print("\n💡 Key Features Demonstrated:")
    print("   • 🏗️  Type-safe Currency enum interface (Currency.ETH, Currency.SOL, etc.)")
    print("   • 🌐 Multi-blockchain support (Ethereum + Solana + Polygon + BSC + Avalanche)")
    print("   • ⚡ Smart caching with volatility-based TTL")
    print("   • 📊 Detailed statistical analysis with confidence metrics")
    print("   • 🎯 Automatic outlier filtering and progressive retry")
    print("   • 🛡️  Enhanced security - no backward compatibility")
    print("   • 🚀 High performance with intelligent caching")

    print("\n🏛️  Supported Blockchains & Currencies:")
    print("   • Ethereum (ETH) - Uniswap V3")
    print("   • Solana (SOL) - Jupiter aggregator")
    print("   • Polygon (POL) - Uniswap V3")
    print("   • BSC (BNB) - PancakeSwap V3")
    print("   • Avalanche (AVAX) - Uniswap V3")

    print("\n📝 Essential Usage Patterns:")
    print("   # Simple price fetching")
    print("   price = await api.price.get(Currency.ETH)")
    print("   ")
    print("   # Detailed analysis with statistics")
    print("   stats = await api.price.get(Currency.SOL, include_stats=True)")
    print('   print(f\'Price: ${stats["price"]:.2f}, Confidence: {stats["confidence"]:.0%}\')')
    print("   ")
    print("   # Check supported currencies")
    print("   supported = await api.price.get_supported_currencies()")
    print("   for currency in supported:")
    print("       price = await api.price.get(currency)")
    print("   ")
    print("   # Cache management")
    print("   await api.price.clear_cache(Currency.ETH)  # Clear specific cache")
    print("   await api.price.clear_cache()              # Clear all caches")

    print("\n🔗 Integration Tips:")
    print("   • Use Currency enum for type safety")
    print("   • Include confidence checks for critical applications")
    print("   • Leverage caching for high-frequency requests")
    print("   • Handle None responses gracefully")
    print("   • Consider using include_stats=True for analysis")


async def main():
    """Run comprehensive Unified Price API demonstration."""
    print("🌟 Unified Price API - Multi-Blockchain Demo")
    print("=" * 50)

    # Check for API key
    api_key = os.environ.get("THEGRAPH_API_KEY")
    if not api_key:
        print("❌ Error: THEGRAPH_API_KEY not found in environment")
        print("💡 Get a free API key at: https://thegraph.market")
        return

    # Initialize the API
    api = TokenAPI(api_key=api_key)

    try:
        await demo_all_supported_currencies(api)
        await demo_type_safety_and_enum_benefits(api)
        await demo_detailed_statistical_analysis(api)
        await demo_smart_caching_performance(api)
        await demo_error_handling_and_robustness(api)
        print_comprehensive_summary()

    except (ConnectionError, TimeoutError, ValueError) as e:
        print(f"❌ Demo failed with error: {e}")
        traceback.print_exc()
    except Exception as e:  # noqa: BLE001
        print(f"❌ Demo failed with unexpected error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    anyio.run(main)
