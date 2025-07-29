#!/usr/bin/env python3
"""Solana SPL Token Transfers Example - Get SPL token transfer events."""

from datetime import datetime

import anyio

from thegraph_token_api import SolanaPrograms, TokenAPI


async def main():
    print("Solana SPL Token Transfers")
    print("=" * 26)

    api = TokenAPI()

    try:
        # Get recent SPL token transfers
        print("\nRecent SPL Transfers:")
        transfers = await api.svm.transfers(limit=4)

        for i, transfer in enumerate(transfers, 1):
            mint = transfer.mint[:12] + "..."
            source = transfer.source[:8] + "..."
            destination = transfer.destination[:8] + "..."
            amount = transfer.amount

            time_str = datetime.fromtimestamp(transfer.timestamp).strftime("%H:%M") if transfer.timestamp else "?"

            print(f"  {i}. {mint} | {source} → {destination} | {time_str}")
            print(f"     Amount: {amount}")

        # Get USDC transfers
        print("\nUSDC Transfers:")
        usdc_transfers = await api.svm.transfers(
            mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # pragma: allowlist secret
            limit=3,
        )

        for i, transfer in enumerate(usdc_transfers, 1):
            amount = transfer.amount
            source = transfer.source[:10] + "..."
            destination = transfer.destination[:10] + "..."

            # USDC has 6 decimals
            usdc_amount = float(amount) / 1_000_000 if amount.isdigit() else 0

            print(f"  {i}. {usdc_amount:,.2f} USDC | {source} → {destination}")

        # Get Token Program transfers
        print("\nToken Program Transfers:")
        token_transfers = await api.svm.transfers(program_id=SolanaPrograms.TOKEN, limit=3)

        for i, transfer in enumerate(token_transfers, 1):
            mint = transfer.mint[:15] + "..."
            value = transfer.value

            print(f"  {i}. {mint} | Value: {value:.2f}")

        print("\n✅ Solana transfer data retrieved successfully!")

    except (ValueError, RuntimeError, OSError) as e:
        print(f"\u274c Error: {e}")


if __name__ == "__main__":
    anyio.run(main)
