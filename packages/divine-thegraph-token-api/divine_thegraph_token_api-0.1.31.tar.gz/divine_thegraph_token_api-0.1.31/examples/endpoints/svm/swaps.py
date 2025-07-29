#!/usr/bin/env python3
"""Solana DEX Swaps Example - Track Solana trading activity."""

# Import shared helper functions
import sys
from pathlib import Path

import anyio

from thegraph_token_api import SwapPrograms, TokenAPI

sys.path.append(str(Path(__file__).parent.parent.parent))
from _helpers import format_time, get_symbol


async def main():
    print("⚡ Solana DEX Tracker")
    print("=" * 20)

    api = TokenAPI()

    try:
        # Raydium swaps
        print("🌊 Raydium DEX:")
        raydium = await api.svm.swaps(program_id=SwapPrograms.RAYDIUM, limit=3)

        for i, swap in enumerate(raydium, 1):
            input_sym = get_symbol(swap.input_mint)
            output_sym = get_symbol(swap.output_mint)
            user = swap.user[:8] + "..."
            time = format_time(swap.timestamp)

            print(f"  {i}. {input_sym} → {output_sym} | {user} | {time}")

        # Jupiter swaps
        print("\n🪐 Jupiter DEX:")
        jupiter = await api.svm.swaps(program_id=SwapPrograms.JUPITER_V6, limit=3)

        for i, swap in enumerate(jupiter, 1):
            input_sym = get_symbol(swap.input_mint)
            output_sym = get_symbol(swap.output_mint)
            input_amt = swap.input_amount
            output_amt = swap.output_amount

            print(f"  {i}. {input_sym} → {output_sym}")
            print(f"     {input_amt:.2f} → {output_amt:.2f}")

        # SOL/USDC price discovery
        print("\n💰 SOL/USDC Trading:")
        sol_usdc = await api.svm.swaps(
            program_id=SwapPrograms.RAYDIUM,
            input_mint="So11111111111111111111111111111111111111112",  # SOL
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC  # pragma: allowlist secret
            limit=2,
        )

        for i, swap in enumerate(sol_usdc, 1):
            sol_amount = swap.input_amount
            usdc_amount = swap.output_amount
            price = usdc_amount / sol_amount if sol_amount > 0 else 0

            print(f"  {i}. {sol_amount:.2f} SOL → {usdc_amount:.2f} USDC")
            print(f"     Rate: ${price:.2f} per SOL")

        print("\n✅ Solana trading data loaded!")

    except (ValueError, RuntimeError, OSError) as e:
        print(f"\u274c Failed to load Solana data: {e}")
        print("\ud83d\udca1 Solana queries can take a moment...")


if __name__ == "__main__":
    anyio.run(main)
