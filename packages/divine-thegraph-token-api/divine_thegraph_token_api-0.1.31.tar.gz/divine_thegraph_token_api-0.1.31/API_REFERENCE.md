# Token API Reference

Complete technical documentation for The Graph Token API client with EVM and SVM support.

## Table of Contents

- [Getting Started](#getting-started)
- [EVM API Reference](#evm-api-reference)
  - [Balances](#evm-balances)
  - [NFTs](#evm-nfts)
  - [Tokens](#evm-tokens)
  - [Transfers](#evm-transfers)
  - [Swaps](#evm-swaps)
  - [Pools](#evm-pools)
  - [Price Data](#evm-price-data)
  - [Historical Balances](#evm-historical-balances)
- [SVM API Reference](#svm-api-reference)
  - [Balances](#svm-balances)
  - [Transfers](#svm-transfers)
  - [Swaps](#svm-swaps)
- [Utility Functions](#utility-functions)
- [Types and Enums](#types-and-enums)
- [Error Handling](#error-handling)

## Getting Started

### Installation

```bash
pip install divine-thegraph-token-api
```

### Basic Setup

```python
import anyio
from thegraph_token_api import TokenAPI, SwapPrograms, Protocol

async def main():
    # Auto-loads from .env file
    api = TokenAPI()

    # Or provide API key directly
    api = TokenAPI(api_key="your_api_key_here")

anyio.run(main)
```

### Environment Variables

Create a `.env` file in your project root:

```bash
THEGRAPH_API_KEY=your_api_key_here
```

Get your free API key at: [https://thegraph.market](https://thegraph.market) (click "Get API Key")

---

## EVM API Reference

EVM methods support Ethereum, Polygon, BSC, Arbitrum, Optimism, Avalanche, Base, and other EVM-compatible chains.

### EVM Balances

#### `api.evm.balances(address, contract=None, limit=10, page=1, network=None)`

Get ERC-20 token balances for a wallet address.

**Parameters:**
- `address` (str, required): Wallet address to query
- `contract` (str, optional): Filter by specific token contract address
- `limit` (int, optional): Number of results to return (default: 10, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[Balance]`: List of balance objects with structured data access

**Example:**
```python
# Get top 10 token balances
balances = await api.evm.balances("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")

# Filter by specific token
usdc_balance = await api.evm.balances(
    "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    contract="0xA0b86a33E6441b8C06DD7b08aEeB2Fa9F06b3c9E"
)

# Query different network
polygon_balances = await api.evm.balances(
    "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    network="matic"  # or NetworkId.MATIC
)

# Access structured data with clean attribute syntax
for balance in balances:
    print(f"{balance.symbol}: {balance.value:.2f}")
    print(f"Contract: {balance.contract}")
    print(f"Amount: {balance.amount}")
```

**Response Schema:**
```python
{
    "data": [
        {
            "block_num": 18500000.0,
            "datetime": "2023-11-01T12:00:00Z",
            "contract": "0xA0b86a33E6441b8C06DD7b08aEeB2Fa9F06b3c9E",
            "amount": "1000000000000000000",
            "value": 1000.0,
            "network_id": "mainnet",
            "symbol": "USDC",
            "decimals": 6.0,
            "price_usd": 1.0,
            "value_usd": 1000.0,
            "low_liquidity": false
        }
    ],
    "statistics": {
        "elapsed": 0.125,
        "rows_read": 100,
        "bytes_read": 2048
    }
}
```

---

### EVM NFTs

#### `api.evm.nfts.ownerships(address, token_standard=None, limit=10, page=1, network=None)`

Get NFT ownerships for a wallet address.

**Parameters:**
- `address` (str, required): Wallet address to query
- `token_standard` (TokenStandard, optional): Filter by standard (ERC721, ERC1155)
- `limit` (int, optional): Number of results to return (default: 10, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[NFTOwnership]`: List of NFT ownership objects with structured data access

**Example:**
```python
# Get all NFTs
nfts = await api.evm.nfts.ownerships("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")

# Filter by ERC721 only
erc721_nfts = await api.evm.nfts.ownerships(
    "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    token_standard="ERC721"  # or TokenStandard.ERC721
)
```

#### `api.evm.nfts.collection(contract, network=None)`

Get NFT collection metadata by contract address.

**Parameters:**
- `contract` (str, required): NFT contract address
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `Optional[NFTCollection]`: Collection metadata object or None if not found

**Example:**
```python
# Get CryptoPunks collection info
collection = await api.evm.nfts.collection("0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb")
print(f"Collection: {collection.name} ({collection.symbol})")
print(f"Total Supply: {collection.total_supply}")
```

#### `api.evm.nfts.activities(contract, from_address=None, to_address=None, any_address=None, start_time=None, end_time=None, order_by=None, order_direction=None, limit=10, page=1, network=None)`

Get NFT activities (transfers, mints, burns) for a contract.

**Parameters:**
- `contract` (str, required): NFT contract address
- `from_address` (str, optional): Filter by sender address
- `to_address` (str, optional): Filter by recipient address
- `any_address` (str, optional): Filter by either sender or recipient address
- `start_time` (int, optional): Start time as UNIX timestamp
- `end_time` (int, optional): End time as UNIX timestamp
- `order_by` (OrderBy, optional): Field to order by (default: timestamp)
- `order_direction` (OrderDirection, optional): Order direction (default: desc)
- `limit` (int, optional): Number of results to return (default: 10, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[NFTActivity]`: List of NFT activity objects with structured data access

**Example:**
```python
# Get recent activities
activities = await api.evm.nfts.activities("0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb")

# Filter by recipient
mints = await api.evm.nfts.activities(
    "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb",
    to_address="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
)

# Get activities in last hour
from datetime import datetime, timedelta
end_time = int(datetime.now().timestamp())
start_time = int((datetime.now() - timedelta(hours=1)).timestamp())

recent_activities = await api.evm.nfts.activities(
    "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb",
    start_time=start_time,
    end_time=end_time
)
```

#### `api.evm.nfts.item(contract, token_id, network=None)`

Get specific NFT item metadata by contract and token ID.

**Parameters:**
- `contract` (str, required): NFT contract address
- `token_id` (str, required): Token ID
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `Optional[NFTItem]`: NFT item metadata object or None if not found

**Example:**
```python
# Get specific NFT item
nft_item = await api.evm.nfts.item(
    "0xbd3531da5cf5857e7cfaa92426877b022e612cf8",
    "5712"
)
print(f"NFT: {nft_item.name}")
print(f"Owner: {nft_item.owner}")
print(f"Attributes: {nft_item.attributes or []}")
```

#### `api.evm.nfts.holders(contract, network=None)`

Get NFT holders for a contract address.

**Parameters:**
- `contract` (str, required): NFT contract address
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[NFTHolder]`: List of NFT holder objects with structured data access

**Example:**
```python
# Get NFT holders
holders = await api.evm.nfts.holders("0xbd3531da5cf5857e7cfaa92426877b022e612cf8")
for holder in holders:
    print(f"Address: {holder.address}")
    print(f"Quantity: {holder.quantity}")
    print(f"Percentage: {holder.percentage:.2f}%")
```

#### `api.evm.nfts.sales(contract=None, token_id=None, any_address=None, offerer=None, recipient=None, start_time=None, end_time=None, order_by=None, order_direction=None, limit=10, page=1, network=None)`

Get NFT marketplace sales data.

**Parameters:**
- `contract` (str, required): NFT contract address
- `token_id` (str, optional): Filter by specific token ID
- `any_address` (str, optional): Filter by either offerer or recipient address
- `offerer` (str, optional): Filter by seller address
- `recipient` (str, optional): Filter by buyer address
- `start_time` (int, optional): Start time as UNIX timestamp
- `end_time` (int, optional): End time as UNIX timestamp
- `order_by` (OrderBy, optional): Field to order by (default: timestamp)
- `order_direction` (OrderDirection, optional): Order direction (default: desc)
- `limit` (int, optional): Number of results to return (default: 10, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[NFTSale]`: List of NFT sale objects with structured data access

**Example:**
```python
# Get recent sales
sales = await api.evm.nfts.sales("0xbd3531da5cf5857e7cfaa92426877b022e612cf8")

# Get sales for specific token
token_sales = await api.evm.nfts.sales(
    "0xbd3531da5cf5857e7cfaa92426877b022e612cf8",
    token_id="5712"
)

# Get high-value sales in last 24 hours
from datetime import datetime, timedelta
end_time = int(datetime.now().timestamp())
start_time = int((datetime.now() - timedelta(days=1)).timestamp())

recent_sales = await api.evm.nfts.sales(
    "0xbd3531da5cf5857e7cfaa92426877b022e612cf8",
    start_time=start_time,
    end_time=end_time
)
```

---

### EVM Tokens

#### `api.evm.token_info(contract, network=None)`

Get token contract metadata and information.

**Parameters:**
- `contract` (str, required): Token contract address
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `Optional[Token]`: Token information object or None if not found

**Example:**
```python
# Get LINK token info
token = await api.evm.token_info("0x514910771AF9Ca656af840dff83E8264EcF986CA")
print(f"Token: {token.name} ({token.symbol})")
print(f"Decimals: {token.decimals}")
print(f"Price: ${token.price_usd}")
```

#### `api.evm.token_holders(contract, limit=10, network=None)`

Get token holder balances by contract address.

**Parameters:**
- `contract` (str, required): Token contract address
- `limit` (int, optional): Number of results to return (default: 10)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[TokenHolder]`: List of token holder objects with structured data access

**Example:**
```python
# Get top LINK holders
holders = await api.evm.token_holders("0x514910771AF9Ca656af840dff83E8264EcF986CA", limit=20)
for holder in holders:
    print(f"Address: {holder.address}, Balance: {holder.value} LINK")
```

---

### EVM Transfers

#### `api.evm.transfers(from_address=None, to_address=None, contract=None, transaction_id=None, start_time=None, end_time=None, order_by=None, order_direction=None, limit=10, page=1, network=None)`

Get ERC-20 token transfer events.

**Parameters:**
- `from_address` (str, optional): Filter by sender address
- `to_address` (str, optional): Filter by recipient address
- `contract` (str, optional): Filter by token contract address
- `transaction_id` (str, optional): Filter by transaction hash
- `start_time` (int, optional): Start time as UNIX timestamp
- `end_time` (int, optional): End time as UNIX timestamp
- `order_by` (OrderBy, optional): Field to order by (default: timestamp)
- `order_direction` (OrderDirection, optional): Order direction (default: desc)
- `limit` (int, optional): Number of results to return (default: 10, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[Transfer]`: List of transfer objects with structured data access

**Example:**
```python
# Get transfers for a specific token
transfers = await api.evm.transfers(contract="0xA0b86a33E6441b8C06DD7b08aEeB2Fa9F06b3c9E")

# Get outgoing transfers from an address
outgoing = await api.evm.transfers(from_address="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")

# Get incoming transfers to an address
incoming = await api.evm.transfers(to_address="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
```

---

### EVM Swaps

#### `api.evm.swaps(pool=None, caller=None, sender=None, recipient=None, protocol=None, transaction_id=None, start_time=None, end_time=None, order_by=None, order_direction=None, limit=10, page=1, network=None)`

Get DEX swap transactions with filtering and time range support.

**Parameters:**
- `pool` (str, optional): Filter by pool address
- `caller` (str, optional): Filter by caller address
- `sender` (str, optional): Filter by sender address
- `recipient` (str, optional): Filter by recipient address
- `protocol` (Protocol, optional): Filter by protocol (uniswap_v2, uniswap_v3)
- `transaction_id` (str, optional): Filter by transaction hash
- `start_time` (int, optional): Start time as UNIX timestamp
- `end_time` (int, optional): End time as UNIX timestamp
- `order_by` (OrderBy, optional): Field to order by (default: timestamp)
- `order_direction` (OrderDirection, optional): Order direction (default: desc)
- `limit` (int, optional): Number of results to return (default: 10, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[Swap]`: List of swap objects with structured data access

**Example:**
```python
# Get recent swaps
swaps = await api.evm.swaps(limit=5)

# Get Uniswap V3 swaps
v3_swaps = await api.evm.swaps(protocol="uniswap_v3")  # or Protocol.UNISWAP_V3

# Get swaps for specific pool
pool_swaps = await api.evm.swaps(pool="0x3E456E2A71adafb6fe0AF8098334ee41ef53A7C6")
```

#### `api.evm.swaps_advanced(...)`

Get DEX swap transactions with advanced filtering and time range support.

**Parameters:**
- `pool` (str, optional): Filter by pool address
- `caller` (str, optional): Filter by caller address
- `sender` (str, optional): Filter by sender address
- `recipient` (str, optional): Filter by recipient address
- `protocol` (Protocol, optional): Filter by protocol
- `transaction_id` (str, optional): Filter by transaction hash
- `start_time` (int, optional): Start time as UNIX timestamp
- `end_time` (int, optional): End time as UNIX timestamp
- `order_by` (OrderBy, optional): Field to order by (default: timestamp)
- `order_direction` (OrderDirection, optional): Order direction (default: desc)
- `limit` (int, optional): Number of results to return (default: 10)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[Swap]`: List of swap objects with structured data access

**Example:**
```python
from datetime import datetime, timedelta

# Get last hour of Uniswap V3 swaps
end_time = int(datetime.now().timestamp())
start_time = int((datetime.now() - timedelta(hours=1)).timestamp())

recent_swaps = await api.evm.swaps_advanced(
    protocol="uniswap_v3",  # or Protocol.UNISWAP_V3
    start_time=start_time,
    end_time=end_time,
    limit=50
)
```

---

### EVM Pools

#### `api.evm.pools(pool=None, factory=None, token=None, symbol=None, protocol=None, limit=10, page=1, network=None)`

Get DEX liquidity pool information.

**Parameters:**
- `pool` (str, optional): Filter by pool address
- `factory` (str, optional): Filter by factory address
- `token` (str, optional): Filter by token address
- `symbol` (str, optional): Filter by token symbol
- `protocol` (Protocol, optional): Filter by protocol
- `limit` (int, optional): Number of results to return (default: 10, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[Pool]`: List of pool objects with structured data access

**Example:**
```python
# Get recent pools
pools = await api.evm.pools()

# Get pools containing USDC
usdc_pools = await api.evm.pools(token="0xA0b86a33E6441b8C06DD7b08aEeB2Fa9F06b3c9E")

# Get Uniswap V3 pools
v3_pools = await api.evm.pools(protocol="uniswap_v3")  # or Protocol.UNISWAP_V3
```

---

### EVM Price Data

#### `api.evm.price_history(token, interval=Interval.ONE_HOUR, start_time=None, end_time=None, limit=24, page=1, network=None)`

Get OHLC price data for a token.

**Parameters:**
- `token` (str, required): Token contract address
- `interval` (Interval, optional): Time interval (default: 1h)
- `start_time` (int, optional): Start time as UNIX timestamp
- `end_time` (int, optional): End time as UNIX timestamp
- `limit` (int, optional): Number of results to return (default: 24, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[PriceHistory]`: List of OHLC price objects with structured data access

**Example:**
```python
# Get hourly price data for last 24 hours
prices = await api.evm.price_history(
    token="0x514910771AF9Ca656af840dff83E8264EcF986CA",
    interval=Interval.ONE_HOUR,
    days=1
)

# Get daily price data for last week
weekly_prices = await api.evm.price_history(
    token="0x514910771AF9Ca656af840dff83E8264EcF986CA",
    interval=Interval.ONE_DAY,
    days=7,
    limit=7
)
```

#### `api.evm.pool_history(pool, interval=Interval.ONE_HOUR, start_time=None, end_time=None, limit=24, page=1, network=None)`

Get OHLC data for a DEX pool.

**Parameters:**
- `pool` (str, required): Pool contract address
- `interval` (Interval, optional): Time interval (default: 1h)
- `start_time` (int, optional): Start time as UNIX timestamp
- `end_time` (int, optional): End time as UNIX timestamp
- `limit` (int, optional): Number of results to return (default: 24, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[PoolHistory]`: List of OHLC pool data objects with structured data access

**Example:**
```python
# Get pool price history
pool_data = await api.evm.pool_history(
    pool="0x3E456E2A71adafb6fe0AF8098334ee41ef53A7C6",
    interval=Interval.FOUR_HOURS,
    days=7
)
```

---

### EVM Historical Balances

#### `api.evm.historical_balances(address, interval=Interval.ONE_HOUR, contracts=None, start_time=None, end_time=None, limit=10, page=1, network=None)`

Get historical ERC-20 & Native balances by wallet address with time intervals.

**Parameters:**
- `address` (str, required): Wallet address to query
- `interval` (Interval, optional): Time interval for data points (default: 1h)
- `contracts` (List[str], optional): Filter by specific token contract addresses
- `start_time` (int, optional): Start time as UNIX timestamp
- `end_time` (int, optional): End time as UNIX timestamp
- `limit` (int, optional): Number of results to return (default: 10, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (NetworkId, optional): Network to query (default: mainnet)

**Returns:**
- `List[HistoricalBalance]`: List of historical balance objects with structured data access

**Example:**
```python
# Get hourly balance history for last 24 hours
historical_balances = await api.evm.historical_balances(
    "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    interval=Interval.ONE_HOUR,
    limit=24
)

# Get daily balance history for specific tokens
usdc_weth_history = await api.evm.historical_balances(
    "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    interval=Interval.ONE_DAY,
    contracts=[
        "0xA0b86a33E6441b8C06DD7b08aEeB2Fa9F06b3c9E",  # USDC
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"   # WETH
    ],
    limit=7
)

# Get weekly balance history with time range
from datetime import datetime, timedelta
end_time = int(datetime.now().timestamp())
start_time = int((datetime.now() - timedelta(weeks=4)).timestamp())

monthly_history = await api.evm.historical_balances(
    "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    interval=Interval.ONE_WEEK,
    start_time=start_time,
    end_time=end_time,
    limit=4
)

# Get 4-hour interval history on Polygon
polygon_history = await api.evm.historical_balances(
    "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    interval=Interval.FOUR_HOURS,
    network="matic",  # or NetworkId.MATIC
    limit=12
)
```

**Response Schema:**
```python
{
    "data": [
        {
            "block_num": 18500000.0,
            "datetime": "2023-11-01T12:00:00Z",
            "timestamp": 1698768000.0,
            "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
            "contract": "0xA0b86a33E6441b8C06DD7b08aEeB2Fa9F06b3c9E",
            "amount": "1000000000000000000",
            "value": 1000.0,
            "network_id": "mainnet",
            "symbol": "USDC",
            "decimals": 6.0,
            "price_usd": 1.0,
            "value_usd": 1000.0,
            "interval": "1h",
            "low_liquidity": false
        },
        {
            "block_num": 18496400.0,
            "datetime": "2023-11-01T11:00:00Z",
            "timestamp": 1698764400.0,
            "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
            "contract": "0x0000000000000000000000000000000000000000",
            "amount": "5000000000000000000",
            "value": 5.0,
            "network_id": "mainnet",
            "symbol": "ETH",
            "decimals": 18.0,
            "price_usd": 2000.0,
            "value_usd": 10000.0,
            "interval": "1h",
            "low_liquidity": false
        }
    ],
    "statistics": {
        "elapsed": 0.125,
        "rows_read": 200,
        "bytes_read": 4096
    }
}
```

---

## SVM API Reference

SVM methods support Solana mainnet with SPL tokens and Solana DEXs.

### SVM Balances

#### `api.svm.balances(token_account=None, mint=None, program_id=None, limit=10, page=1, network="solana")`

Get Solana SPL token balances.

**Parameters:**
- `token_account` (str, optional): Filter by token account address
- `mint` (str, optional): Filter by mint address
- `program_id` (SolanaPrograms, optional): Filter by program ID
- `limit` (int, optional): Number of results to return (default: 10, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (SolanaNetworkId, optional): Solana network (default: solana)

**Returns:**
- `List[SolanaBalance]`: List of Solana balance objects with structured data access

**Example:**
```python
# Get recent SPL token balances
balances = await api.svm.balances(limit=20)

# Get balances for specific mint (USDC)
usdc_balances = await api.svm.balances(mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v  # pragma: allowlist secret")

# Get Token 2022 program balances
token_2022_balances = await api.svm.balances(
    program_id="TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb  # pragma: allowlist secret"  # or SolanaPrograms.TOKEN_2022
)
```

**Response Schema:**
```python
{
    "data": [
        {
            "block_num": 150000000.0,
            "datetime": "2023-11-01T12:00:00Z",
            "timestamp": 1698768000.0,
            "program_id": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA  # pragma: allowlist secret",
            "token_account": "4ct7br2vTPzfdmY3S5HLtTxcGSBfn6pnw98hsS6v359A",
            "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v  # pragma: allowlist secret",
            "amount": "1000000",
            "value": 1.0,
            "decimals": 6.0,
            "network_id": "solana"
        }
    ],
    "statistics": {
        "elapsed": 0.125,
        "rows_read": 100,
        "bytes_read": 2048
    }
}
```

---

### SVM Transfers

#### `api.svm.transfers(signature=None, program_id=None, mint=None, authority=None, source=None, destination=None, start_time=None, end_time=None, order_by=None, order_direction=None, limit=10, page=1, network="solana")`

Get Solana SPL token transfer events.

**Parameters:**
- `signature` (str, optional): Filter by transaction signature
- `program_id` (SolanaPrograms, optional): Filter by program ID
- `mint` (str, optional): Filter by mint address
- `authority` (str, optional): Filter by authority address
- `source` (str, optional): Filter by source address
- `destination` (str, optional): Filter by destination address
- `start_time` (int, optional): Start time as UNIX timestamp
- `end_time` (int, optional): End time as UNIX timestamp
- `order_by` (OrderBy, optional): Field to order by (default: timestamp)
- `order_direction` (OrderDirection, optional): Order direction (default: desc)
- `limit` (int, optional): Number of results to return (default: 10, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (SolanaNetworkId, optional): Solana network (default: solana)

**Returns:**
- `List[SolanaTransfer]`: List of Solana transfer objects with structured data access

**Example:**
```python
# Get recent transfers
transfers = await api.svm.transfers(limit=10)

# Get transfers for USDC
usdc_transfers = await api.svm.transfers(
    mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v  # pragma: allowlist secret"
)

# Get transfers by authority
authority_transfers = await api.svm.transfers(
    authority="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
)

# Get Token Program transfers
token_transfers = await api.svm.transfers(
    program_id="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA  # pragma: allowlist secret"  # or SolanaPrograms.TOKEN
)
```

---

### SVM Swaps

#### `api.svm.swaps(program_id, amm=None, amm_pool=None, user=None, input_mint=None, output_mint=None, signature=None, start_time=None, end_time=None, order_by=None, order_direction=None, limit=10, page=1, network="solana")`

Get Solana DEX swap transactions with time filtering support.

**Parameters:**
- `program_id` (SwapPrograms, required): Swap program ID (Raydium, Orca, Jupiter, etc.)
- `amm` (str, optional): Filter by AMM address
- `amm_pool` (str, optional): Filter by AMM pool address
- `user` (str, optional): Filter by user address
- `input_mint` (str, optional): Filter by input mint address
- `output_mint` (str, optional): Filter by output mint address
- `signature` (str, optional): Filter by transaction signature
- `start_time` (int, optional): Start time as UNIX timestamp
- `end_time` (int, optional): End time as UNIX timestamp
- `order_by` (OrderBy, optional): Field to order by (default: timestamp)
- `order_direction` (OrderDirection, optional): Order direction (default: desc)
- `limit` (int, optional): Number of results to return (default: 10, max: 1000)
- `page` (int, optional): Page number for pagination (default: 1)
- `network` (SolanaNetworkId, optional): Solana network (default: solana)

**Returns:**
- `List[SolanaSwap]`: List of Solana swap objects with structured data access

**Example:**
```python
# Get Raydium swaps
raydium_swaps = await api.svm.swaps(
    program_id="675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8  # pragma: allowlist secret",  # or SwapPrograms.RAYDIUM
    limit=10
)

# Get Orca swaps
orca_swaps = await api.svm.swaps(
    program_id="6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P  # pragma: allowlist secret",  # or SwapPrograms.ORCA
    limit=5
)

# Get Jupiter V6 swaps
jupiter_swaps = await api.svm.swaps(
    program_id="JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4  # pragma: allowlist secret"  # or SwapPrograms.JUPITER_V6
)

# Get swaps for specific pool with time filtering
from datetime import datetime, timedelta
end_time = int(datetime.now().timestamp())
start_time = int((datetime.now() - timedelta(minutes=30)).timestamp())

recent_swaps = await api.svm.swaps(
    program_id="675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8  # pragma: allowlist secret",  # or SwapPrograms.RAYDIUM
    amm_pool="H7zh7kBJY8cGHcbHgKpJgRC9vmQGf3Bk4m8fdbNdy3hL",
    start_time=start_time,
    end_time=end_time,
    limit=50
)

# Get SOL/USDC swaps
sol_usdc_swaps = await api.svm.swaps(
    program_id="675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8  # pragma: allowlist secret",  # or SwapPrograms.RAYDIUM
    input_mint="So11111111111111111111111111111111111111112  # pragma: allowlist secret",  # SOL
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v  # pragma: allowlist secret"  # USDC
)
```

**Response Schema:**
```python
{
    "data": [
        {
            "block_num": 150000000.0,
            "datetime": "2023-11-01T12:00:00Z",
            "timestamp": 1698768000.0,
            "transaction_index": 1,
            "instruction_index": 0,
            "signature": "5J8oyTo6W1tBKhEDE7RyT5RqPZkY8q1YWZXMFfPsxQktqxqX",
            "program_id": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8  # pragma: allowlist secret",
            "program_name": "Raydium",
            "user": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
            "amm": "EYTBKuQnvjGx7LSDKPBQJbKb8Jw5YWPfMTtdqXRpK7zx",
            "amm_name": "Raydium AMM",
            "amm_pool": "H7zh7kBJY8cGHcbHgKpJgRC9vmQGf3Bk4m8fdbNdy3hL",
            "input_mint": {
                "address": "So11111111111111111111111111111111111111112  # pragma: allowlist secret",
                "symbol": "SOL",
                "decimals": 9.0
            },
            "input_amount": 1.5,
            "output_mint": {
                "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v  # pragma: allowlist secret",
                "symbol": "USDC",
                "decimals": 6.0
            },
            "output_amount": 150.0,
            "network_id": "solana"
        }
    ],
    "statistics": {
        "elapsed": 0.125,
        "rows_read": 100,
        "bytes_read": 2048
    }
}
```

---

## Utility Functions

#### `api.health()`

Check API health status and connectivity.

**Parameters:** None

**Returns:**
- `str`: Health status ("OK" or error message)

**Example:**
```python
health = await api.health()
if health == "OK":
    print("API is healthy")
else:
    print(f"API issue: {health}")
```

#### `api.version()`

Get API version information.

**Parameters:** None

**Returns:**
- `dict`: Version information with version, date, and commit

**Example:**
```python
version_info = await api.version()
print(f"API Version: {version_info.version}")
print(f"Release Date: {version_info.date}")
print(f"Commit: {version_info.commit}")
```

**Response Schema:**
```python
{
    "version": "2.2.10",
    "date": "2025-07-10",
    "commit": "af1bb70",
    "repo": "pinax-network/token-api"
}
```

#### `api.networks()`

Get supported networks and their configuration.

**Parameters:** None

**Returns:**
- `dict`: Networks configuration with supported chains

**Example:**
```python
networks = await api.networks()
for network in networks.networks:
    print(f"Network: {network.fullName} ({network.id})")
    print(f"Type: {network.networkType}")
    print(f"CAIP-2 ID: {network.caip2Id}")
```

**Response Schema:**
```python
{
    "networks": [
        {
            "id": "mainnet",
            "fullName": "Ethereum Mainnet",
            "shortName": "Ethereum",
            "caip2Id": "eip155:1",
            "networkType": "mainnet",
            "icon": {
                "web3Icons": {
                    "name": "ethereum"
                }
            },
            "alias": ["ethereum", "eth", "eth-mainnet", "evm-1"]
        }
    ]
}
```

---

## Types and Enums

### Network IDs

**EVM Networks:**
```python
# Use string network IDs as they appear in the API
"mainnet"      # Ethereum Mainnet
"matic"        # Polygon
"bsc"          # Binance Smart Chain
"arbitrum-one" # Arbitrum One
"optimism"     # Optimism
"avalanche"    # Avalanche C-Chain
"base"         # Base
"unichain"     # Unichain

# Or use the NetworkId enum for type safety
from thegraph_token_api import NetworkId
NetworkId.MAINNET      # Ethereum
NetworkId.MATIC        # Polygon
NetworkId.BSC          # Binance Smart Chain
NetworkId.ARBITRUM_ONE # Arbitrum
NetworkId.OPTIMISM     # Optimism
NetworkId.AVALANCHE    # Avalanche
NetworkId.BASE         # Base
NetworkId.UNICHAIN     # Unichain
```

**SVM Networks:**
```python
# Use string network ID
"solana"       # Solana mainnet

# Or use the enum for type safety
from thegraph_token_api import SolanaNetworkId
SolanaNetworkId.SOLANA  # Solana mainnet
```

### Protocols

```python
# Use string protocol names as they appear in the API
"uniswap_v2"  # Uniswap V2
"uniswap_v3"  # Uniswap V3

# Or use the enum for type safety
from thegraph_token_api import Protocol
Protocol.UNISWAP_V2  # Uniswap V2
Protocol.UNISWAP_V3  # Uniswap V3
```

### Solana Programs

```python
# SPL Token Program IDs (use strings as they appear in API)
"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA  # pragma: allowlist secret"  # SPL Token Program
"TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb  # pragma: allowlist secret"  # SPL Token 2022 Program

# DEX Program IDs
"675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8  # pragma: allowlist secret"  # Raydium
"6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P  # pragma: allowlist secret"   # Orca
"JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB  # pragma: allowlist secret"  # Jupiter V4
"JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4  # pragma: allowlist secret"  # Jupiter V6
"pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA  # pragma: allowlist secret"  # Pump.fun

# Or use enums for type safety
from thegraph_token_api import SolanaPrograms, SwapPrograms

# SPL Token Programs
SolanaPrograms.TOKEN      # SPL Token Program
SolanaPrograms.TOKEN_2022 # SPL Token 2022 Program

# DEX Programs
SwapPrograms.RAYDIUM     # Raydium
SwapPrograms.ORCA        # Orca
SwapPrograms.JUPITER_V4  # Jupiter V4
SwapPrograms.JUPITER_V6  # Jupiter V6
SwapPrograms.PUMP_FUN    # Pump.fun
```

### Time Intervals

```python
from thegraph_token_api import Interval

Interval.ONE_HOUR    # 1h
Interval.FOUR_HOURS  # 4h
Interval.ONE_DAY     # 1d
Interval.ONE_WEEK    # 1w
```

### Token Standards

```python
from thegraph_token_api import TokenStandard

TokenStandard.ERC721   # ERC-721 NFTs
TokenStandard.ERC1155  # ERC-1155 NFTs
```

### Ordering

```python
from thegraph_token_api import OrderBy, OrderDirection

# Order by field
OrderBy.TIMESTAMP  # Order by timestamp
OrderBy.VALUE      # Order by value

# Order direction
OrderDirection.ASC   # Ascending
OrderDirection.DESC  # Descending
```

---

## Error Handling

The API client includes comprehensive error handling:

```python
try:
    balances = await api.evm.balances("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
except ValueError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"API error: {e}")
```

**Common Error Scenarios:**
- Invalid API key → `ValueError`
- Invalid address format → `ValueError`
- Network timeout → `Exception`
- Rate limiting → `Exception`
- Invalid network ID → `ValueError`

**Best Practices:**
1. Always wrap API calls in try-catch blocks
2. Check for empty results before processing
3. Implement retry logic for network errors
4. Validate addresses before making API calls
5. Use appropriate timeouts for your use case

---

## Support

- **Documentation**: [API Reference](API_REFERENCE.md)
- **Examples**: See `examples/` directory
- **Issues**: Report bugs and feature requests on GitHub
- **API Key**: Get yours at [thegraph.market](https://thegraph.market) (click "Get API Key")
