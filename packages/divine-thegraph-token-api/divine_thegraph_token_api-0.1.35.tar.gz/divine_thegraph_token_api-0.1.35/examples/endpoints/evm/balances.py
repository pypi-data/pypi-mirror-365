#!/usr/bin/env python3
"""Token Balances Example - See your crypto portfolio instantly."""

# Import shared helper functions
import sys
from pathlib import Path

import anyio

from thegraph_token_api import TokenAPI

sys.path.append(str(Path(__file__).parent.parent.parent))
from _helpers import format_amount


async def main():
    print("💰 Token Balances")
    print("=" * 17)

    api = TokenAPI()
    wallet = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik's wallet

    try:
        print(f"📊 Portfolio for {wallet[:8]}...")
        balances = await api.evm.balances(wallet, limit=5)

        print("\n🏆 Top Holdings:")
        for i, balance in enumerate(balances, 1):
            symbol = balance.symbol or "UNKNOWN"
            amount = format_amount(balance.value)
            print(f"  {i}. {symbol}: {amount}")

        # Show specific token
        print("\n🎯 Specific Token:")
        imagine = await api.evm.balances(wallet, contract="0x6A1B2AE3a55B5661b40d86c2bF805f7DAdB16978", limit=1)

        if imagine:
            token = imagine[0]
            print(f"  {token.symbol or 'TOKEN'}: {format_amount(token.value)}")
        else:
            print("  No balance found for this token")

        print("\n✅ Portfolio loaded!")

    except (ValueError, RuntimeError, OSError) as e:
        print(f"\u274c Failed to load portfolio: {e}")
        print(
            "\ud83d\udca1 Make sure your API key is set: export THEGRAPH_API_KEY='your_key'"  # pragma: allowlist secret
        )


if __name__ == "__main__":
    anyio.run(main)
