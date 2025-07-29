#!/usr/bin/env python3
"""
Quick Start Example - Everything you need in one simple script.

This example demonstrates the most common token-api use cases:
- API health check
- Token balances
- NFT ownership
- Recent swaps

Run this first to verify your setup works!
"""

import anyio
from _helpers import WALLETS, format_amount, print_header, print_section, shorten_address, shorten_id

from thegraph_token_api import SwapPrograms, TokenAPI


async def main():
    print_header("Token API Quick Start", "🚀")

    api = TokenAPI()

    try:
        # 1. Health Check
        print_section("Health Check", "🏥")
        health = await api.health()
        print(f"API Status: {health}")

        if health.lower() != "ok":
            print("⚠️ API may have issues")
            return

        # 2. Portfolio Balances
        print_section("Portfolio", "💰")
        balances = await api.evm.balances(WALLETS["vitalik"], limit=3)

        for i, balance in enumerate(balances, 1):
            symbol = balance.symbol or "TOKEN"
            amount = format_amount(balance.value)
            print(f"  {i}. {symbol}: {amount}")

        # 3. NFT Collection
        print_section("NFTs", "🎨")
        nfts = await api.evm.nfts.ownerships(WALLETS["vitalik"], limit=2)

        for i, nft in enumerate(nfts, 1):
            name = (nft.name or "Unknown")[:20]
            token_id = shorten_id(nft.token_id)
            print(f"  {i}. {name} #{token_id}")

        # 4. Recent Swaps
        print_section("Recent Swaps", "⚡")
        swaps = await api.svm.swaps(program_id=SwapPrograms.RAYDIUM, limit=2)

        for i, swap in enumerate(swaps, 1):
            input_symbol = getattr(swap.input_mint, "symbol", "TOKEN")
            output_symbol = getattr(swap.output_mint, "symbol", "TOKEN")
            user = shorten_address(swap.user)
            print(f"  {i}. {input_symbol} → {output_symbol} | {user}")

        print("\n✅ Quick start completed!")
        print("💡 Check out other examples in the endpoints/ folder")

    except (ValueError, RuntimeError, OSError) as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Set your API key: export THEGRAPH_API_KEY='your_key'")  # pragma: allowlist secret
        print("2. Get a key at: https://thegraph.market")
        print("3. Check your internet connection")


if __name__ == "__main__":
    anyio.run(main)
