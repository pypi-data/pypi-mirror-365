#!/usr/bin/env python3
"""Price History Example - Track token prices over time."""

# Import shared helper functions
import sys
from datetime import datetime
from pathlib import Path

import anyio

from thegraph_token_api import Interval, TokenAPI

sys.path.append(str(Path(__file__).parent.parent.parent))
from _helpers import format_price_change


def parse_datetime(datetime_str):
    """Parse ISO datetime string safely."""
    try:
        return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


async def main():
    print("📈 Price History")
    print("=" * 16)

    api = TokenAPI()
    link_address = "0x514910771AF9Ca656af840dff83E8264EcF986CA"  # nosec B105  # not a password, this is a public token address
    uniswap_pool = "0x3E456E2A71adafb6fe0AF8098334ee41ef53A7C6"

    try:
        # Token price history
        print("🔗 LINK Token (7 days):")
        prices = await api.evm.price_history(
            token=link_address,
            interval=Interval.ONE_DAY,
            days=7,
        )

        for candle in prices[:5]:
            dt = parse_datetime(candle.datetime)
            date_str = dt.strftime("%m/%d") if dt else "??/??"

            open_price = candle.open
            close_price = candle.close
            change = format_price_change(open_price, close_price)

            print(f"  {date_str}: ${open_price:.2f} → ${close_price:.2f} ({change})")

        # Pool price tracking
        print("\n🏊 Pool Prices (24h):")
        pool_prices = await api.evm.pool_history(pool=uniswap_pool, interval=Interval.ONE_HOUR, days=1)

        for candle in pool_prices[:3]:
            dt = parse_datetime(candle.datetime)
            time_str = dt.strftime("%H:%M") if dt else "??:??"

            open_price = candle.open
            close_price = candle.close

            print(f"  {time_str}: {open_price:.6f} → {close_price:.6f}")

        print("\n✅ Price data loaded!")

    except (ValueError, RuntimeError, OSError) as e:
        print(f"\u274c Failed to load price data: {e}")
        print("\ud83d\udca1 Price queries can take longer for historical data")


if __name__ == "__main__":
    anyio.run(main)
