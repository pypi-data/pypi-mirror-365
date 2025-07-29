#!/usr/bin/env python3
"""NFT Example - Explore NFT collections and ownership."""

import anyio

from thegraph_token_api import TokenAPI


def shorten_id(token_id):
    """Shorten long token IDs for display."""
    id_str = str(token_id)
    return id_str if len(id_str) <= 6 else id_str[:6] + "..."


async def main():
    print("🎨 NFT Explorer")
    print("=" * 15)

    api = TokenAPI()
    wallet = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik's wallet
    cryptopunks = "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"

    try:
        # Show owned NFTs
        print(f"🖼️  NFTs owned by {wallet[:8]}...")
        nfts = await api.evm.nfts.ownerships(wallet, limit=3)

        for i, nft in enumerate(nfts, 1):
            name = (nft.name or "Unknown NFT")[:25]
            token_id = shorten_id(nft.token_id)
            print(f"  {i}. {name} #{token_id}")

        # Show collection stats
        print("\n📊 CryptoPunks Collection:")
        collection = await api.evm.nfts.collection(cryptopunks)

        if collection:
            print(f"  📈 {collection.name}")
            print(f"  🎯 {collection.total_supply:,} total items")
            print(f"  👥 {collection.owners:,} unique owners")

        # Show recent activity
        print("\n⚡ Recent Activity:")
        activities = await api.evm.nfts.activities(cryptopunks, limit=3)

        for i, activity in enumerate(activities, 1):
            action = activity.activity_type
            token_id = shorten_id(activity.token_id)
            from_addr = activity.from_address[:6] + "..."
            to_addr = activity.to[:6] + "..."

            print(f"  {i}. {action} #{token_id}: {from_addr} → {to_addr}")

        print("\n✅ NFT data loaded!")

    except (ValueError, RuntimeError, OSError) as e:
        print(f"\u274c Failed to load NFT data: {e}")
        print("\ud83d\udca1 NFT queries can be slow - this is normal!")


if __name__ == "__main__":
    anyio.run(main)
