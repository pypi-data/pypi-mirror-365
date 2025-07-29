# EVM Endpoint Examples

This directory contains focused examples for Ethereum Virtual Machine (EVM) endpoints. Each example demonstrates EVM-specific functionality with real blockchain data from Ethereum, Polygon, and other EVM chains.

## Available Examples

### 📊 Core Token Data
- **[`balances.py`](balances.py)** - Get ERC-20 and native token balances for any wallet
- **[`tokens.py`](tokens.py)** - Get token contract metadata and holder information
- **[`transfers.py`](transfers.py)** - Track token transfer events and movements

### 🎨 NFT Data
- **[`nfts.py`](nfts.py)** - Get NFT ownership, collection info, and activities

### 💱 DeFi Data
- **[`swaps.py`](swaps.py)** - Get DEX swap transactions from Uniswap and other protocols
- **[`prices.py`](prices.py)** - Get OHLC price history for tokens and pools

### 🛠️ Utility
- **[`health.py`](health.py)** - Check API health and verify connectivity

## Quick Start

Each example is self-contained and can be run independently:

```bash
# Check API health
python3 examples/endpoints/evm/health.py

# Get token balances
python3 examples/endpoints/evm/balances.py

# Get recent swaps
python3 examples/endpoints/evm/swaps.py
```

## Requirements

1. **API Key**: Set `THEGRAPH_API_KEY` in your `.env` file
2. **Python 3.13+** with `anyio` and other dependencies

## Usage Pattern

All examples follow the same simple pattern:

```python
from thegraph_token_api import TokenAPI

async def main():
    api = TokenAPI()  # Auto-loads from .env

    # Get data (clean list/dict returned)
    data = await api.method_name(parameters)

    # Process data
    for item in data:
        print(item)

anyio.run(main)
```

## Real Data

All examples use real blockchain data:
- **Vitalik's wallet**: `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`
- **Your Imagine token**: `0x6A1B2AE3a55B5661b40d86c2bF805f7DAdB16978`
- **Your Uniswap pool**: `0x3E456E2A71adafb6fe0AF8098334ee41ef53A7C6`
- **Popular tokens**: LINK, CryptoPunks, etc.

## Error Handling

Examples include proper error handling and helpful error messages. If you see timeouts, it's typically due to API load - the code is correct.

## Next Steps

- Combine multiple endpoints for comprehensive analysis
- Add your own addresses and contracts
- Build dashboards using this data
- Integrate into your applications
