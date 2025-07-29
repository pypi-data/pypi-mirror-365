# SVM (Solana) Endpoint Examples

This directory contains focused examples for Solana Virtual Machine (SVM) endpoints. Each example demonstrates Solana-specific functionality with real SPL tokens and DEX data.

## Available Examples

### 💰 SPL Token Data
- **[`balances.py`](balances.py)** - Get SPL token balances for Solana wallet addresses
- **[`transfers.py`](transfers.py)** - Track SPL token transfer events and movements

### 🔄 Solana DEX Data
- **[`swaps.py`](swaps.py)** - Get DEX swap transactions from Raydium, Orca, Jupiter, and other Solana DEXs

## Quick Start

Each example is self-contained and can be run independently:

```bash
# Get SPL token balances
python3 examples/endpoints/svm/balances.py

# Get token transfers
python3 examples/endpoints/svm/transfers.py

# Get DEX swaps
python3 examples/endpoints/svm/swaps.py
```

## Requirements

1. **API Key**: Set `THEGRAPH_API_KEY` in your `.env` file
2. **Python 3.13+** with `anyio` and other dependencies

## Usage Pattern

All SVM examples follow the same simple pattern:

```python
from thegraph_token_api import TokenAPI, SwapPrograms, SolanaPrograms

async def main():
    api = TokenAPI()  # Auto-loads from .env

    # Get Solana data (clean list returned)
    data = await api.svm_method_name(parameters)

    # Process data
    for item in data:
        print(item)

anyio.run(main)
```

## Solana-Specific Features

### Program IDs
Use enum constants for better code:

```python
# SPL Token Programs
SolanaPrograms.TOKEN        # Token Program
SolanaPrograms.TOKEN_2022   # Token-2022 Program

# DEX Programs
SwapPrograms.RAYDIUM       # Raydium DEX
SwapPrograms.ORCA          # Orca DEX
SwapPrograms.JUPITER_V4    # Jupiter V4
SwapPrograms.JUPITER_V6    # Jupiter V6
SwapPrograms.PUMP_FUN      # Pump.fun
```

### Common Solana Addresses
Examples use real Solana data:
- **USDC Mint**: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- **Wrapped SOL**: `So11111111111111111111111111111111111111112`
- **Example Wallet**: `9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM`

### Data Format
Solana data includes specific fields:
- **Signatures**: Transaction signatures (not hashes)
- **Mints**: Token mint addresses
- **Token Accounts**: SPL token account addresses
- **Programs**: Program IDs for different protocols
- **Decimals**: Token decimal precision

## Real Data

All examples use real Solana blockchain data:
- SPL token balances and transfers
- DEX swaps from major Solana AMMs
- Real mint addresses and token accounts
- Actual program IDs and signatures

## Network Support

Currently supports:
- **Solana Mainnet**: Primary Solana network

## Next Steps

- Combine with EVM data for cross-chain analysis
- Build Solana-specific trading dashboards
- Track DeFi activity across Solana DEXs
- Monitor SPL token movements and liquidity
