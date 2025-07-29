"""
Data classes for structured API responses.

This module provides clean, attribute-accessible data classes that replace
raw dictionary access with proper structured types. All classes use modern
dataclass attribute access (obj.symbol) for clean, type-safe interfaces.
"""

import inspect
from dataclasses import dataclass
from typing import Any


@dataclass
class BaseModel:
    """Base model class."""


@dataclass
class Balance(BaseModel):
    """Token balance with clean attribute access."""

    block_num: float
    datetime: str
    contract: str
    amount: str
    value: float
    network_id: str
    symbol: str | None = None
    decimals: float | None = None
    price_usd: float | None = None
    value_usd: float | None = None
    low_liquidity: bool | None = None


@dataclass
class SolanaBalance(BaseModel):
    """Solana token balance with clean attribute access."""

    block_num: float
    datetime: str
    timestamp: float
    program_id: str
    token_account: str
    mint: str
    amount: str
    value: float
    decimals: float
    network_id: str


@dataclass
class SwapToken(BaseModel):
    """Token information in swap."""

    address: str
    symbol: str
    decimals: float


@dataclass
class Swap(BaseModel):
    """EVM swap with clean attribute access."""

    block_num: float
    datetime: str
    timestamp: float
    network_id: str
    transaction_id: str
    caller: str
    sender: str
    factory: str
    pool: str
    token0: SwapToken
    token1: SwapToken
    amount0: str
    amount1: str
    price0: float
    price1: float
    value0: float
    value1: float
    protocol: str
    recipient: str | None = None
    fee: str | None = None


@dataclass
class SolanaMint(BaseModel):
    """Solana mint information."""

    address: str
    symbol: str
    decimals: float


@dataclass
class SolanaSwap(BaseModel):
    """Solana swap with clean attribute access."""

    block_num: float
    datetime: str
    timestamp: float
    signature: str
    program_id: str
    program_name: str
    user: str
    amm: str
    amm_name: str
    input_mint: SolanaMint | str
    input_amount: float
    output_mint: SolanaMint | str
    output_amount: float
    network_id: str
    transaction_index: float | None = None
    instruction_index: float | None = None
    amm_pool: str | None = None


@dataclass
class Transfer(BaseModel):
    """EVM transfer with clean attribute access."""

    block_num: float
    datetime: str
    timestamp: float
    transaction_id: str
    contract: str
    from_address: str  # Using from_address instead of 'from' to avoid keyword conflict
    to: str
    value: float
    symbol: str | None = None
    decimals: float | None = None


@dataclass
class SolanaTransfer(BaseModel):
    """Solana transfer with clean attribute access."""

    block_num: float
    datetime: str
    timestamp: float
    signature: str
    program_id: str
    mint: str
    authority: str
    source: str
    destination: str
    amount: str
    value: float
    network_id: str
    decimals: float | None = None


@dataclass
class NFTOwnership(BaseModel):
    """NFT ownership with clean attribute access."""

    token_id: str
    token_standard: str
    contract: str
    owner: str
    network_id: str
    symbol: str | None = None
    uri: str | None = None
    name: str | None = None
    image: str | None = None
    description: str | None = None


@dataclass
class NFTCollection(BaseModel):
    """NFT collection with clean attribute access."""

    contract: str
    name: str
    symbol: str
    owners: float
    total_supply: float
    network_id: str
    contract_creation: str | None = None
    contract_creator: str | None = None
    total_unique_supply: float | None = None
    total_transfers: float | None = None
    token_standard: str | None = None


@dataclass
class NFTActivity(BaseModel):
    """NFT activity with clean attribute access."""

    activity_type: str  # Using activity_type instead of '@type'
    block_num: float
    block_hash: str
    timestamp: str
    tx_hash: str
    contract: str
    from_address: str  # Using from_address instead of 'from'
    to: str
    token_id: str
    amount: float
    symbol: str | None = None
    name: str | None = None
    transfer_type: str | None = None
    token_standard: str | None = None


@dataclass
class Token(BaseModel):
    """Token metadata with clean attribute access."""

    block_num: float
    datetime: str
    contract: str
    circulating_supply: str | float
    holders: float
    network_id: str
    symbol: str | None = None
    name: str | None = None
    decimals: float | None = None
    price_usd: float | None = None
    market_cap: float | None = None
    low_liquidity: bool | None = None


@dataclass
class TokenHolder(BaseModel):
    """Token holder with clean attribute access."""

    block_num: float
    datetime: str
    address: str
    amount: str
    value: float
    network_id: str
    symbol: str | None = None
    decimals: float | None = None
    price_usd: float | None = None
    value_usd: float | None = None
    low_liquidity: bool | None = None


@dataclass
class Pool(BaseModel):
    """Liquidity pool with clean attribute access."""

    block_num: float
    datetime: str
    network_id: str
    transaction_id: str
    factory: str
    pool: str
    token0: SwapToken
    token1: SwapToken
    fee: float
    protocol: str


@dataclass
class OHLC(BaseModel):
    """OHLC price data with clean attribute access."""

    datetime: str
    ticker: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    uaw: float
    transactions: float


def convert_to_model[T: BaseModel](data: dict[str, Any], model_class: type[T]) -> T | None:
    """Convert dictionary data to structured model."""
    if not data:
        return None

    # Handle special field mappings
    converted_data = {}
    for key, value in data.items():
        if key == "from":
            converted_data["from_address"] = value
        elif key == "@type":
            converted_data["activity_type"] = value
        else:
            converted_data[key] = value

    # Handle nested objects
    if model_class == Swap and "token0" in converted_data:
        if isinstance(converted_data["token0"], dict):
            converted_data["token0"] = SwapToken(**converted_data["token0"])
        if isinstance(converted_data["token1"], dict):
            converted_data["token1"] = SwapToken(**converted_data["token1"])

    elif model_class == SolanaSwap:
        if "input_mint" in converted_data and isinstance(converted_data["input_mint"], dict):
            converted_data["input_mint"] = SolanaMint(**converted_data["input_mint"])
        if "output_mint" in converted_data and isinstance(converted_data["output_mint"], dict):
            converted_data["output_mint"] = SolanaMint(**converted_data["output_mint"])

    elif model_class == Pool:
        if isinstance(converted_data.get("token0"), dict):
            converted_data["token0"] = SwapToken(**converted_data["token0"])
        if isinstance(converted_data.get("token1"), dict):
            converted_data["token1"] = SwapToken(**converted_data["token1"])

    # Filter only fields that exist in the dataclass
    signature = inspect.signature(model_class)
    valid_fields = set(signature.parameters.keys())
    filtered_data = {k: v for k, v in converted_data.items() if k in valid_fields}

    try:
        return model_class(**filtered_data)
    except TypeError:
        # Fallback: create with only the fields that match
        working_data = {}
        for field_name in valid_fields:
            if field_name in filtered_data:
                working_data[field_name] = filtered_data[field_name]
        return model_class(**working_data)


def convert_list_to_models[T: BaseModel](data_list: list[dict[str, Any]], model_class: type[T]) -> list[T]:
    """Convert list of dictionaries to list of structured models."""
    return [model for item in data_list if item and (model := convert_to_model(item, model_class)) is not None]
