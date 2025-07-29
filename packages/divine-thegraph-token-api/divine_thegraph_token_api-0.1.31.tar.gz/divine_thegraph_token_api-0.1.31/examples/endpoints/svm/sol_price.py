"""
Example: Optimized SOL price calculation with smart SVM API.

This example demonstrates the new optimized SOL price functionality:
1. Super simple price retrieval with smart defaults
2. Detailed statistics with confidence scoring
3. Automatic caching with volatility-based TTL
4. Zero-config usage - just works!
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Use pathlib to resolve the parent directory four levels up
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from dotenv import load_dotenv

from thegraph_token_api import SwapPrograms, TokenAPI

# Load environment variables
load_dotenv()


async def example_simple_usage():
    """Example: Super simple SOL price - just one line!"""
    print("\n=== ✨ Optimized Simple Usage ===")

    api_key = os.environ.get("THEGRAPH_API_KEY")
    if not api_key:
        print("Error: THEGRAPH_API_KEY not found in environment")
        return

    api = TokenAPI(api_key=api_key)
    # One line to get SOL price - that's it!
    price = await api.svm.get_sol_price()

    if price:
        print(f"💰 Current SOL price: ${price:.2f}")
        print("✅ Auto-cached with smart TTL based on volatility")
        print("⚡ Smart retry logic with progressive sampling")
        print("🎯 Automatic outlier filtering using IQR method")
    else:
        print("❌ Failed to get SOL price")


async def example_with_confidence():
    """Example: Get SOL price with confidence and stats."""
    print("\n=== 📊 Price with Intelligence ===")

    api_key = os.environ.get("THEGRAPH_API_KEY")
    if not api_key:
        print("Error: THEGRAPH_API_KEY not found in environment")
        return

    api = TokenAPI(api_key=api_key)
    # Get detailed stats with one parameter
    stats = await api.svm.get_sol_price(include_stats=True)

    if stats and stats.get("price"):
        print(f"💰 Price: ${stats['price']:.2f}")
        print(f"📈 Confidence: {stats['confidence']:.0%}")
        print(f"📊 Trades analyzed: {stats['trades_analyzed']}")
        print(f"📉 Volatility: {stats['std_deviation']:.2f}")
        print(f"⏰ Data age: {datetime.now().timestamp() - stats['timestamp']:.0f}s")

        # Show confidence interpretation
        conf = stats["confidence"]
        if conf >= 0.8:
            print("🟢 High confidence - excellent data quality")
        elif conf >= 0.5:
            print("🟡 Medium confidence - good data quality")
        else:
            print("🟠 Low confidence - limited data available")
    else:
        print("❌ No price data available")


async def example_cached_performance():
    """Example: Show smart caching in action."""
    print("\n=== ⚡ Smart Caching Demo ===")

    api_key = os.environ.get("THEGRAPH_API_KEY")
    if not api_key:
        print("Error: THEGRAPH_API_KEY not found in environment")
        return

    api = TokenAPI(api_key=api_key)

    # First call - fetches from API
    start = time.time()
    price1 = await api.svm.get_sol_price()
    time1 = time.time() - start

    # Second call - uses smart cache
    start = time.time()
    price2 = await api.svm.get_sol_price()
    time2 = time.time() - start

    if price1 and price2:
        print(f"🌐 First call (API): ${price1:.2f} - took {time1:.2f}s")
        print(f"⚡ Second call (cache): ${price2:.2f} - took {time2:.3f}s")
        print(f"🚀 Speedup: {time1 / time2:.0f}x faster!")
    else:
        print(f"❌ Cache demo failed - price1: {price1}, price2: {price2}")
        return

    # Show cache intelligence
    stats = await api.svm.get_sol_price(include_stats=True)
    if stats:
        volatility = stats["std_deviation"] / stats["price"]
        ttl = 60 if volatility > 0.05 else 300
        print(f"🧠 Smart TTL: {ttl}s (based on {volatility:.1%} volatility)")


async def example_integration():
    """Example: Show how it integrates seamlessly with other SVM functions."""
    print("\n=== 🔗 Seamless Integration ===")

    api_key = os.environ.get("THEGRAPH_API_KEY")
    if not api_key:
        print("Error: THEGRAPH_API_KEY not found in environment")
        return

    api = TokenAPI(api_key=api_key)
    # All in one API session - share connections efficiently

    # Get current SOL price
    sol_price = await api.svm.get_sol_price()

    # Get recent Jupiter swaps
    swaps = await api.svm.swaps(program_id=SwapPrograms.JUPITER_V6, limit=3)

    # Get SOL balance example (if you have a token account)
    # balances = await api.svm.balances(mint="So11111111111111111111111111111111111111112")

    if sol_price:
        print(f"💰 Current SOL price: ${sol_price:.2f}")

    if swaps:
        print(f"📋 Recent Jupiter swaps: {len(swaps)}")
        if len(swaps) > 0:
            latest = swaps[0]
            print(f"   Latest: {getattr(latest, 'datetime', 'N/A')}")

    print("🎯 All data fetched in same session with optimized connections!")


async def main():
    """Run all examples."""
    await example_simple_usage()
    await example_with_confidence()
    await example_cached_performance()
    await example_integration()


if __name__ == "__main__":
    asyncio.run(main())
