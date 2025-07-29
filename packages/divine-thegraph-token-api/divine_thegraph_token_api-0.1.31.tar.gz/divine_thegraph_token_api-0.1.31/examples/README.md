# Token API Examples

Optimized, user-friendly examples demonstrating The Graph Token API with real blockchain data. All examples feature clean output, helpful error messages, and professional formatting.

## 🚀 Quick Start

**1. Set your API key:**
```bash
export THEGRAPH_API_KEY="your_api_key_here"  # pragma: allowlist secret
```
Get a free API key at: [thegraph.market](https://thegraph.market)

**2. Try the quick start:**
```bash
python examples/quickstart.py              # Everything in one script!
```

**3. Explore specific examples:**
```bash
# EVM examples
python examples/endpoints/evm/health.py     # 🏥 API connectivity
python examples/endpoints/evm/balances.py   # 💰 Token portfolios
python examples/endpoints/evm/nfts.py       # 🎨 NFT collections

# SVM examples
python examples/endpoints/svm/balances.py   # ⚡ SPL token balances
python examples/endpoints/svm/swaps.py      # 🌊 Solana DEX trading
```

## ✨ **NEW: Optimized for Simplicity**

All examples now feature:
- 🎨 **Visual output** with emojis and clear formatting
- 💡 **Smart error messages** with troubleshooting tips
- 📊 **Professional displays** with K/M number formatting
- 🚀 **Faster execution** with streamlined code
- 🛠️ **Helper functions** for consistent, maintainable code

## 📁 Examples Structure

### 🔗 EVM (Ethereum Virtual Machine)
**Location**: [`endpoints/evm/`](endpoints/evm/)

Supports Ethereum, Polygon, BSC, Arbitrum, Optimism, Avalanche, Base, and other EVM-compatible chains.

- `health.py` - API connectivity and health checks
- `balances.py` - Token balance queries with real wallets
- `tokens.py` - Token information and holder analysis
- `transfers.py` - Token transfer event tracking
- `swaps.py` - DEX swap transaction analysis
- `nfts.py` - Complete NFT analysis (ownerships, collections, activities)
- `prices.py` - Price history and OHLC data

### ⚡ SVM (Solana Virtual Machine)
**Location**: [`endpoints/svm/`](endpoints/svm/)

Supports Solana mainnet with SPL tokens and Solana DEXs.

- `balances.py` - Solana SPL token balances
- `transfers.py` - SPL token transfer tracking
- `swaps.py` - Cross-DEX analysis (Raydium, Jupiter, Pump.fun)

## 🎯 API Interface

All examples use the clean, separated `TokenAPI` interface:

```python
from thegraph_token_api import TokenAPI, SwapPrograms, Protocol

async def main():
    api = TokenAPI()  # Auto-loads from .env

    # EVM methods (Ethereum, Polygon, BSC, etc.)
    balances = await api.evm.balances("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
    nfts = await api.evm.nfts.ownerships("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
    swaps = await api.evm.swaps(protocol=Protocol.UNISWAP_V3)

    # SVM methods (Solana)
    sol_balances = await api.svm.balances(mint="So11111111111111111111111111111111111111112")
    sol_swaps = await api.svm.swaps(program_id=SwapPrograms.RAYDIUM)

    # Clean structured data access
    for balance in balances:
        print(f"{balance.symbol}: {balance.value:.2f}")

    for swap in swaps:
        print(f"{swap.token0.symbol} → {swap.token1.symbol}")
```

## 🎯 Use Cases by Role

### 📊 **Traders & Investors**
- `evm/balances.py` - Portfolio tracking across wallets
- `evm/swaps.py` - Market activity and volume analysis
- `evm/prices.py` - Price history and trend analysis
- `svm/swaps.py` - Solana DEX arbitrage opportunities

### 🎨 **NFT Enthusiasts**
- `evm/nfts.py` - Complete NFT market analysis
- Collection floor price tracking
- Whale activity monitoring

### 🛠️ **Developers**
- Production-ready integration patterns
- Modern async/await architecture
- Error handling and edge case management
- Clean structured data access

### 🔍 **Researchers**
- Cross-chain ecosystem analysis
- Market microstructure studies
- Multi-protocol volume analysis

## 🔧 Technical Features

### **Structured Data Access**
Examples demonstrate clean attribute access instead of dictionary lookups:
```python
# Clean structured access
balance.symbol          # vs balance.get('symbol', '?')
swap.token0.symbol      # vs swap.get('token0', {}).get('symbol', '?')
nft.token_standard      # vs nft.get('token_standard', 'unknown')
```

### **Async Programming**
All examples use modern `anyio` for:
- Concurrent API calls
- Proper resource management
- High-performance networking

### **Error Handling**
- Comprehensive try/catch blocks
- Graceful API error recovery
- User-friendly error messages
- Timeout handling for slow endpoints

### **Real-time Data**
- Live blockchain data from multiple networks
- Recent transactions and activities
- Time-filtered queries

## 📈 Sample Output

```
🏥 API Health Check Example
===================================

🔍 Checking API Health...
  Status: OK
  ✅ API is healthy and responding

🧪 Testing API Connectivity...
  ✅ API call successful - received 1 result(s)
  🌐 Connection to The Graph Token API is working

✅ Health check completed successfully!
```

```
💰 EVM Token Balances
=====================

Vitalik's Portfolio:
  1. ETH: 631.58 ($1,574,850.23)
  2. USDC: 50,000.00 ($50,000.00)
  3. LINK: 1,250.75 ($18,761.25)

✅ Balance data retrieved successfully!
```

## 📝 Customization

Examples are designed to be easily customized:

1. **Change addresses** - Replace wallet/contract addresses with your own
2. **Adjust time windows** - Modify time ranges for different periods
3. **Add new networks** - Include additional EVM networks
4. **Filter data** - Add specific token or NFT filters

```python
# Customize wallet address
your_wallet = "0xYourWalletAddressHere"
balances = await api.evm.balances(your_wallet, limit=10)
```

## 🆘 Troubleshooting

**Missing API Key:**
```
❌ Please set THEGRAPH_API_KEY environment variable
```
*Solution: Set your API key as shown above*

**Network Errors:**
```
❌ Error occurred: NetworkingError
```
*Solution: Check internet connection and API key validity*

**Timeout Issues:**
```
⚠️ Request timeout (this is common for holder queries)
```
*Solution: Normal for computationally expensive queries*

## ⚠️ Important Notes

- **Free tier**: 1,000 requests/month, paid plans available
- **No blockchain costs**: Examples query data only (no gas fees)
- **Live data**: Results vary based on current blockchain activity
- **Safe to run**: Examples are read-only and can be run repeatedly

## 🚀 Next Steps

1. **Start with `endpoints/evm/health.py`** to verify connectivity
2. **Explore `endpoints/evm/balances.py`** for basic data queries
3. **Try `endpoints/svm/swaps.py`** for Solana ecosystem analysis
4. **Customize examples** with your own addresses and contracts
5. **Build applications** using these patterns as foundations

## 📚 Additional Resources

- [Token API Documentation](../README.md)
- [API Reference](../API_REFERENCE.md)
- [Type Definitions](../src/thegraph_token_api/types.py)
- [The Graph Token API](https://thegraph.market)

---

*All examples use real blockchain data and demonstrate production-ready patterns for building blockchain applications with the Token API Client.*
