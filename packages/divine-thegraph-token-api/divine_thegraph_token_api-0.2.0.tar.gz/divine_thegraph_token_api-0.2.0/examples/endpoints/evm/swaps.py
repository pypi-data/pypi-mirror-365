#!/usr/bin/env python3
"""DeFi Swaps Example - Get DEX swap transactions."""

from datetime import datetime

import anyio

from thegraph_token_api import Protocol, TokenAPI


async def main():
    print("DeFi Swaps Example")
    print("=" * 20)

    api = TokenAPI()

    try:
        # Get recent Uniswap V3 swaps
        print("\nUniswap V3 Swaps:")
        swaps = await api.evm.swaps(protocol=Protocol.UNISWAP_V3, limit=5)

        for i, swap in enumerate(swaps, 1):
            token0 = swap.token0.symbol
            token1 = swap.token1.symbol
            protocol = swap.protocol

            time_str = datetime.fromtimestamp(swap.timestamp).strftime("%H:%M") if swap.timestamp else "?"

            print(f"  {i}. {token0} ↔ {token1} | {protocol} | {time_str}")

        # Get swaps from specific pool
        print("\nSpecific Pool Swaps:")
        pool_swaps = await api.evm.swaps(pool="0x3E456E2A71adafb6fe0AF8098334ee41ef53A7C6", limit=3)

        for i, swap in enumerate(pool_swaps, 1):
            token0 = swap.token0.symbol
            token1 = swap.token1.symbol
            amount0 = swap.value0
            amount1 = swap.value1

            print(f"  {i}. {amount0:.2f} {token0} → {amount1:.2f} {token1}")

        print("\n✅ Swap data retrieved successfully!")

    except (ValueError, RuntimeError, OSError) as e:
        print(f"\u274c Error: {e}")


if __name__ == "__main__":
    anyio.run(main)
