#!/usr/bin/env python3
"""Token Information Example - Get token metadata and holder data."""

import anyio

from thegraph_token_api import TokenAPI


async def main():
    print("Token Information Example")
    print("=" * 25)

    api = TokenAPI()

    try:
        # Get token information
        print("\nChainlink (LINK) Token Info:")
        token = await api.evm.token_info("0x514910771AF9Ca656af840dff83E8264EcF986CA")

        if token:
            name = token.name or "?"
            symbol = token.symbol or "?"
            decimals = token.decimals or "?"
            holders = token.holders
            price = token.price_usd

            print(f"  {name} ({symbol})")
            print(f"  Decimals: {decimals}")
            print(f"  Holders: {holders:,}" if isinstance(holders, int | float) else f"  Holders: {holders}")
            if price:
                print(f"  Price: ${price:.4f}")

        # Get token holders (may timeout for popular tokens)
        print("\nTop Token Holders:")
        try:
            holders = await api.evm.token_holders("0x6A1B2AE3a55B5661b40d86c2bF805f7DAdB16978", limit=3)

            for i, holder in enumerate(holders, 1):
                address = holder.address[:10] + "..."
                value = holder.value
                formatted = f"{value:,.0f}" if value > 1000 else f"{value:.2f}"
                print(f"  {i}. {address} | {formatted}")

        except (ValueError, RuntimeError, OSError):
            print("  (Request timeout - common for popular tokens)")

        print("\n✅ Token data retrieved successfully!")

    except (ValueError, RuntimeError, OSError) as e:
        print(f"\u274c Error: {e}")


if __name__ == "__main__":
    anyio.run(main)
