#!/usr/bin/env python3
"""Health Check Example - Verify API connectivity in 10 seconds."""

import anyio

from thegraph_token_api import TokenAPI


async def main():
    print("🏥 API Health Check")
    print("=" * 18)

    api = TokenAPI()

    try:
        # Quick health check
        print("🔍 Checking API...")
        health = await api.health()

        if health.lower() == "ok":
            print("✅ API is healthy and ready!")

            # Quick connectivity test
            print("🧪 Testing data access...")
            data = await api.evm.balances("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", limit=1)
            print(f"✅ Connected! Found {len(data)} balance(s)")

        else:
            print(f"⚠️ API status: {health}")

    except (ValueError, RuntimeError, OSError) as e:
        print(f"\u274c Connection failed: {e}")
        print("\ud83d\udca1 Check your THEGRAPH_API_KEY environment variable")


if __name__ == "__main__":
    anyio.run(main)
