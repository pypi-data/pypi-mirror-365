# The Graph Token API Client

[![PyPI version](https://badge.fury.io/py/divine-thegraph-token-api.svg)](https://badge.fury.io/py/divine-thegraph-token-api)
[![Python versions](https://img.shields.io/pypi/pyversions/divine-thegraph-token-api.svg)](https://pypi.org/project/divine-thegraph-token-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25+-brightgreen.svg)](https://github.com/divinescreener/thegraph-token-api)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A powerful Python client for The Graph Token API that brings blockchain data to your fingertips. Access token balances, NFT ownership, DeFi swaps, and price histories across Ethereum, Solana, and 8+ other chains with an elegant, type-safe interface.

*Current Spec version: 4.0*

## 🌟 Why The Graph Token API Client?

### The Challenge

Accessing blockchain data is complex:
- **Multiple chains** with different APIs and data formats 🔗
- **Inconsistent interfaces** between EVM and Solana ecosystems 🤔
- **Raw responses** requiring extensive parsing and validation 📊
- **Rate limiting** and error handling complexity 🚦

### Our Solution

The Graph Token API Client provides a **unified, elegant interface** for all your blockchain data needs:

```python
# Without this client - Complex and error-prone 😰
import requests
response = requests.get(
    "https://api.thegraph.com/v1/tokens/evm/ethereum/balances",
    headers={"Authorization": f"Bearer {api_key}"},
    params={"address": wallet_address}
)
if response.status_code == 200:
    data = response.json()
    # Parse nested structures, handle errors...

# With this client - Clean and simple ✨
from thegraph_token_api import TokenAPI

api = TokenAPI()
balances = await api.evm.balances(wallet_address)
# That's it! Fully typed, validated, and ready to use
```

## ✨ Features

- 🏗️ **Elegant Architecture**: Intuitive separation between EVM and SVM (Solana) chains
- 🌐 **Multi-Chain Support**: 9 chains including Ethereum, Polygon, BSC, Arbitrum, and Solana
- 📊 **Comprehensive Data**: Token balances, NFTs, DeFi swaps, prices, transfers, and more
- ⚡ **High Performance**: Async/await support with connection pooling
- 🛡️ **Type Safety**: Full type hints with runtime validation
- 🔄 **Smart Defaults**: Auto-loads API keys, sensible limits, mainnet defaults
- 📈 **Time-Series Data**: Historical prices and time-filtered swap data
- 🎯 **Developer Friendly**: Clean API, great docs, extensive examples

## 📦 Installation

```bash
# Using pip
pip install divine-thegraph-token-api

# Using uv
uv add divine-thegraph-token-api

# For development
git clone https://github.com/divine/thegraph-token-api
cd thegraph-token-api
uv sync
```

### Requirements
- Python 3.13+
- API key from [thegraph.market](https://thegraph.market) (free tier available)

## 🚀 Quick Start

### 1. Get Your API Key

Visit [thegraph.market](https://thegraph.market) and click "Get API Key" (free tier available).

### 2. Set Up Environment

Create a `.env` file:
```bash
THEGRAPH_API_KEY=your_api_key_here
```

### 3. Start Coding!

```python
import anyio
from thegraph_token_api import TokenAPI

async def main():
    # Initialize client (auto-loads from .env)
    api = TokenAPI()
    
    # Get Ethereum token balances
    vitalik_wallet = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    balances = await api.evm.balances(vitalik_wallet)
    
    for token in balances:
        if token["balance"] > 0:
            print(f"{token['symbol']}: {token['balance']} (${token['value_usd']:,.2f})")
    
    # Get Solana NFTs
    sol_nfts = await api.svm.balances(
        mint="So11111111111111111111111111111111111111112"
    )
    
    print(f"\nFound {len(sol_nfts)} Solana NFT holders")

anyio.run(main)
```

## 📖 Core Concepts

### Chain Separation

The API elegantly separates EVM and SVM operations:

```python
# EVM chains (Ethereum, Polygon, BSC, etc.)
await api.evm.balances(address)        # Get token balances
await api.evm.nfts.ownerships(address) # Get NFT holdings
await api.evm.swaps(protocol=...)      # Get DEX swaps

# SVM (Solana)
await api.svm.balances(mint=...)       # Get SPL token holders
await api.svm.transfers(mint=...)      # Get token transfers
await api.svm.swaps(program_id=...)    # Get DEX swaps
```

### Smart Organization

Methods are logically grouped for discoverability:

```python
# NFT operations grouped together
api.evm.nfts.ownerships(address)    # What NFTs does this address own?
api.evm.nfts.collection(contract)   # Get collection details
api.evm.nfts.activities(contract)   # Recent NFT activities

# Pool operations grouped together
api.evm.pools(token=address)        # Find liquidity pools
api.evm.pool_history(pool, "1h")    # Get pool metrics over time
```

## 🔥 Usage Examples

### Token Balances Across Chains

```python
from thegraph_token_api import TokenAPI, Chain

api = TokenAPI()

# Check balances on multiple chains
async def check_portfolio(address: str):
    chains = [Chain.ETHEREUM, Chain.POLYGON, Chain.ARBITRUM]
    
    total_value = 0
    for chain in chains:
        balances = await api.evm.balances(address, chain=chain)
        
        print(f"\n{chain.value.title()} Holdings:")
        for token in balances[:5]:  # Top 5 tokens
            value = token.get("value_usd", 0)
            total_value += value
            print(f"  {token['symbol']}: ${value:,.2f}")
    
    print(f"\nTotal Portfolio Value: ${total_value:,.2f}")
```

### NFT Collection Analytics

```python
# Analyze an NFT collection
async def analyze_nft_collection(contract: str):
    # Get collection info
    collection = await api.evm.nfts.collection(contract)
    print(f"Collection: {collection['name']}")
    print(f"Total Supply: {collection['total_supply']}")
    
    # Get recent activities
    activities = await api.evm.nfts.activities(
        contract, 
        chain=Chain.ETHEREUM,
        limit=10
    )
    
    for activity in activities:
        print(f"{activity['type']}: Token #{activity['token_id']} "
              f"for {activity['price']} ETH")
```

### DeFi Swap Monitoring

```python
from datetime import datetime, timedelta
from thegraph_token_api import Protocol, SwapPrograms

# Monitor recent Uniswap V3 swaps
async def monitor_uniswap_swaps():
    swaps = await api.evm.swaps(
        protocol=Protocol.UNISWAP_V3,
        chain=Chain.ETHEREUM,
        limit=20
    )
    
    for swap in swaps:
        print(f"Swap: {swap['amount_in']} {swap['token_in_symbol']} → "
              f"{swap['amount_out']} {swap['token_out_symbol']}")
        print(f"Value: ${swap['value_usd']:,.2f}")
        print(f"DEX: {swap['dex_name']}\n")

# Monitor Solana swaps with time filtering
async def monitor_solana_swaps():
    # Get swaps from last 30 minutes
    end_time = int(datetime.now().timestamp())
    start_time = int((datetime.now() - timedelta(minutes=30)).timestamp())
    
    swaps = await api.svm.swaps(
        program_id=SwapPrograms.RAYDIUM,
        start_time=start_time,
        end_time=end_time,
        limit=10
    )
    
    print(f"Recent Raydium swaps (last 30 min):")
    for swap in swaps:
        print(f"${swap['value_usd']:,.2f} swap at "
              f"{datetime.fromtimestamp(swap['timestamp'])}")
```

### Price History Analysis

```python
# Get historical token prices
async def analyze_token_price(token_address: str):
    # Get 7-day price history with daily intervals
    prices = await api.evm.price_history(
        token=token_address,
        chain=Chain.ETHEREUM,
        interval="1d",
        days=7
    )
    
    # Calculate price change
    if len(prices) >= 2:
        start_price = prices[0]["price_usd"]
        end_price = prices[-1]["price_usd"]
        change = ((end_price - start_price) / start_price) * 100
        
        print(f"7-day price change: {change:+.2f}%")
        print(f"Current price: ${end_price:,.4f}")
        
        # Find min/max
        min_price = min(p["price_usd"] for p in prices)
        max_price = max(p["price_usd"] for p in prices)
        print(f"7-day range: ${min_price:,.4f} - ${max_price:,.4f}")
```

### Token Holder Analysis

```python
# Analyze token holders
async def analyze_token_holders(token_address: str):
    holders = await api.evm.token_holders(
        token_address,
        chain=Chain.ETHEREUM,
        limit=100
    )
    
    # Calculate concentration
    total_supply = sum(h["balance"] for h in holders)
    top_10_balance = sum(h["balance"] for h in holders[:10])
    concentration = (top_10_balance / total_supply) * 100
    
    print(f"Top 10 holders own {concentration:.1f}% of supply")
    
    # Show top holders
    for i, holder in enumerate(holders[:5], 1):
        pct = (holder["balance"] / total_supply) * 100
        print(f"{i}. {holder['address'][:10]}... - {pct:.2f}%")
```

## 🌐 Supported Networks & Protocols

### Blockchains

| Network | Chain ID | Type | Status |
|---------|----------|------|--------|
| Ethereum | `ethereum` | EVM | ✅ Supported |
| Polygon | `polygon` | EVM | ✅ Supported |
| BNB Chain | `bsc` | EVM | ✅ Supported |
| Arbitrum | `arbitrum` | EVM | ✅ Supported |
| Optimism | `optimism` | EVM | ✅ Supported |
| Avalanche | `avalanche` | EVM | ✅ Supported |
| Base | `base` | EVM | ✅ Supported |
| Unichain | `unichain` | EVM | ✅ Supported |
| Solana | `solana` | SVM | ✅ Supported |

### DEX Protocols

**EVM DEXs:**
- Uniswap V2 & V3
- SushiSwap
- PancakeSwap
- And more...

**Solana DEXs:**
- Raydium
- Orca
- Jupiter
- Pump.fun

## 📚 API Reference

### Core Classes

#### `TokenAPI`

The main entry point for all API operations.

```python
api = TokenAPI(api_key: Optional[str] = None)
# If api_key is None, loads from THEGRAPH_API_KEY env var
```

#### `EVMInterface`

Access via `api.evm` - handles all EVM chain operations.

```python
# Token operations
await api.evm.balances(address: str, chain: Chain = Chain.ETHEREUM)
await api.evm.token_info(contract: str, chain: Chain = Chain.ETHEREUM)
await api.evm.token_holders(contract: str, chain: Chain = Chain.ETHEREUM)

# NFT operations  
await api.evm.nfts.ownerships(address: str, chain: Chain = Chain.ETHEREUM)
await api.evm.nfts.collection(contract: str, chain: Chain = Chain.ETHEREUM)
await api.evm.nfts.activities(contract: str, chain: Chain = Chain.ETHEREUM)

# DeFi operations
await api.evm.swaps(protocol: Protocol, chain: Chain = Chain.ETHEREUM)
await api.evm.pools(token: str, chain: Chain = Chain.ETHEREUM)

# Price data
await api.evm.price_history(token: str, interval: str, days: int)
await api.evm.pool_history(pool: str, interval: str)

# Transfers
await api.evm.transfers(from_address: str = None, to_address: str = None)
```

#### `SVMInterface`

Access via `api.svm` - handles Solana operations.

```python
# Token operations
await api.svm.balances(mint: str, limit: int = 100)
await api.svm.transfers(mint: str, limit: int = 100)

# DEX operations with time filtering
await api.svm.swaps(
    program_id: str = None,
    start_time: int = None,
    end_time: int = None,
    limit: int = 100
)
```

### Enums

```python
from thegraph_token_api import Chain, Protocol, SwapPrograms

# EVM chains
Chain.ETHEREUM
Chain.POLYGON
Chain.BSC
# ... etc

# EVM DEX protocols
Protocol.UNISWAP_V2
Protocol.UNISWAP_V3
Protocol.SUSHISWAP
# ... etc

# Solana DEX programs
SwapPrograms.RAYDIUM
SwapPrograms.ORCA
SwapPrograms.JUPITER
SwapPrograms.PUMP_FUN
```

### Error Handling

```python
from thegraph_token_api import TokenAPIError
from type_enforcer import ValidationError

try:
    balances = await api.evm.balances(address)
except TokenAPIError as e:
    print(f"API error: {e}")
except ValidationError as e:
    print(f"Data validation error: {e}")
```

## 🛠️ Advanced Usage

### Custom API Configuration

```python
from thegraph_token_api import TokenAPI

# Custom initialization
api = TokenAPI(
    api_key="your_api_key",
    timeout=30.0,  # Request timeout in seconds
    max_retries=3  # Number of retries on failure
)
```

### Batch Operations

```python
# Fetch data for multiple addresses efficiently
async def batch_fetch_balances(addresses: list[str]):
    tasks = [
        api.evm.balances(addr, chain=Chain.ETHEREUM)
        for addr in addresses
    ]
    
    results = await anyio.gather(*tasks)
    
    for addr, balances in zip(addresses, results):
        total_value = sum(t.get("value_usd", 0) for t in balances)
        print(f"{addr}: ${total_value:,.2f}")
```

### Caching Strategies

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache token info for 1 hour
@lru_cache(maxsize=1000)
async def get_token_info_cached(contract: str, chain: str):
    return await api.evm.token_info(contract, Chain(chain))

# Cache with TTL
class CachedTokenAPI:
    def __init__(self, api: TokenAPI, ttl: int = 3600):
        self.api = api
        self.cache = {}
        self.ttl = ttl
    
    async def get_token_info(self, contract: str):
        key = f"token:{contract}"
        now = datetime.now()
        
        if key in self.cache:
            data, timestamp = self.cache[key]
            if now - timestamp < timedelta(seconds=self.ttl):
                return data
        
        data = await self.api.evm.token_info(contract)
        self.cache[key] = (data, now)
        return data
```

## 🔧 Development

### Setup

```bash
# Clone the repository
git clone https://github.com/divinescreener/thegraph-token-api
cd thegraph-token-api

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run mypy src

# Run examples
uv run python examples/basic_usage.py
```

### Project Structure

```
thegraph-token-api/
├── src/
│   └── thegraph_token_api/
│       ├── __init__.py
│       ├── core.py          # Main API client
│       ├── evm.py           # EVM chain interface
│       ├── svm.py           # Solana interface
│       ├── types.py         # Type definitions
│       └── utils.py         # Helper functions
├── tests/                   # Test suite
├── examples/                # Usage examples
│   ├── endpoints/          
│   │   ├── evm/            # EVM examples
│   │   └── svm/            # Solana examples
│   └── basic_usage.py      # Getting started
├── API_REFERENCE.md        # Detailed API docs
└── pyproject.toml          # Project configuration
```

### Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

Key requirements:
- Maintain >90% test coverage
- Follow the existing code style
- Add tests for new features
- Update documentation

## 📊 Performance

The client is optimized for production use:

- **Connection Pooling**: Reuses HTTP connections
- **Async Operations**: Non-blocking I/O for high throughput
- **Smart Caching**: SOL price caching reduces API calls
- **Batch Support**: Efficient multi-request handling

## 🔒 Security

- **API Key Safety**: Never logged or exposed
- **Input Validation**: All parameters validated
- **Type Safety**: Runtime type checking
- **Secure HTTP**: TLS 1.2+ enforced

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built on [The Graph](https://thegraph.com/) infrastructure
- Type safety via [divine-type-enforcer](https://github.com/divinescreener/type-enforcer)
- HTTP handling by [divine-typed-requests](https://github.com/divinescreener/typed-requests)

## 🆘 Support

- 📖 **Documentation**: [API Reference](API_REFERENCE.md) | [Official Docs](https://thegraph.com/docs/en/token-api/quick-start/)
- 💬 **Discord**: [The Graph Discord](https://discord.gg/thegraph)
- 🐛 **Issues**: [GitHub Issues](https://github.com/divinescreener/thegraph-token-api/issues)
- 🔑 **API Keys**: [thegraph.market](https://thegraph.market)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/divinescreener">DIVINE</a>
</p>