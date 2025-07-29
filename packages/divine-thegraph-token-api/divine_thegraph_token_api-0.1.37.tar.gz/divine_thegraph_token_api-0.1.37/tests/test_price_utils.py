"""
Test suite for price_utils.py to achieve 100% coverage.

Focuses on edge cases and exception handling paths not covered by test_unified_price_api.py.
"""

from thegraph_token_api.price_utils import extract_ethereum_price, extract_solana_price


class TestExtractSolanaPriceEdgeCases:
    """Test edge cases for extract_solana_price function."""

    def test_extract_solana_price_string_mint_address(self):
        """Test Solana price extraction with string mint addresses (line 219)."""
        swap = {
            "input_mint": "So11111111111111111111111111111111111111112",  # String format
            "output_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # String format
            "input_amount": 1000000000,  # 1 SOL (9 decimals)
            "output_amount": 100000000,  # 100 USDC (6 decimals)
        }

        token_pair = ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        price = extract_solana_price(swap, token_pair)

        assert price == 100.0

    def test_extract_solana_price_none_mint_address(self):
        """Test Solana price extraction with None mint address (line 219)."""
        swap = {
            "input_mint": None,  # None value
            "output_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "input_amount": 1000000000,
            "output_amount": 100000000,
        }

        token_pair = ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        price = extract_solana_price(swap, token_pair)

        assert price is None  # Should return None due to invalid mint

    def test_extract_solana_price_exception_in_calculation(self):
        """Test Solana price extraction with exception during calculation (lines 246-247)."""
        swap = {
            "input_mint": "So11111111111111111111111111111111111111112",
            "output_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "input_amount": "invalid",  # String instead of number - will cause ValueError
            "output_amount": 100000000,
        }

        token_pair = ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        price = extract_solana_price(swap, token_pair)

        assert price is None  # Should return None due to exception

    def test_extract_solana_price_key_error(self):
        """Test Solana price extraction with missing keys (lines 246-247)."""
        swap = {
            "input_mint": "So11111111111111111111111111111111111111112",
            "output_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            # Missing input_amount and output_amount
        }

        token_pair = ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        price = extract_solana_price(swap, token_pair)

        assert price is None


class TestExtractEthereumPriceEdgeCases:
    """Test edge cases for extract_ethereum_price function."""

    def test_extract_ethereum_price_string_token_addresses(self):
        """Test Ethereum price extraction with string token addresses (lines 276-277, 281-282)."""
        swap = {
            "token0": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # String format instead of dict
            "token1": "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108",  # String format instead of dict
            "amount0": "1000000000000000000",  # 1 ETH
            "amount1": "3500000000",  # 3500 USDC
        }

        token_pair = ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108")
        price = extract_ethereum_price(swap, token_pair)

        assert price == 3500.0

    def test_extract_ethereum_price_reverse_pair_usdc_token0(self):
        """Test Ethereum price extraction where USDC is token0 (line 310)."""
        swap = {
            "token0": {"address": "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108", "decimals": 6},  # USDC first
            "token1": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},  # ETH second
            "amount0": "3500000000",  # 3500 USDC
            "amount1": "1000000000000000000",  # 1 ETH
        }

        token_pair = ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108")
        price = extract_ethereum_price(swap, token_pair)

        assert price == 3500.0

    def test_extract_ethereum_price_out_of_range_price(self):
        """Test Ethereum price extraction with out of range price (line 314)."""
        swap = {
            "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},
            "token1": {"address": "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108", "decimals": 6},
            "amount0": "1000000000000000000",  # 1 ETH
            "amount1": "2000000000000000",  # 2,000,000,000 USDC - unrealistic price
        }

        token_pair = ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108")
        price = extract_ethereum_price(swap, token_pair)

        assert price is None  # Should return None due to price > 1,000,000

    def test_extract_ethereum_price_exception_handling(self):
        """Test Ethereum price extraction with exception (lines 318-319)."""
        swap = {
            "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},
            "token1": {"address": "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108", "decimals": 6},
            "amount0": None,  # None will cause AttributeError when trying float()
            "amount1": "3500000000",
        }

        token_pair = ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108")
        price = extract_ethereum_price(swap, token_pair)

        assert price is None  # Should return None due to exception

    def test_extract_ethereum_price_type_error(self):
        """Test Ethereum price extraction with TypeError (lines 318-319)."""
        swap = {
            "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},
            "token1": {"address": "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108", "decimals": 6},
            "amount0": {"nested": "object"},  # Dict instead of number - will cause TypeError
            "amount1": "3500000000",
        }

        token_pair = ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108")
        price = extract_ethereum_price(swap, token_pair)

        assert price is None  # Should return None due to exception

    def test_extract_ethereum_price_mixed_string_dict_tokens(self):
        """Test Ethereum price extraction with mixed string/dict token data."""
        swap = {
            "token0": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # String format
            "token1": {"address": "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108", "decimals": 6},  # Dict format
            "amount0": "1000000000000000000",  # 1 ETH (using default 18 decimals)
            "amount1": "3500000000",  # 3500 USDC
        }

        token_pair = ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108")
        price = extract_ethereum_price(swap, token_pair)

        assert price == 3500.0

    def test_extract_ethereum_price_negative_price_check(self):
        """Test Ethereum price extraction with zero/negative price (line 314)."""
        swap = {
            "token0": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "decimals": 18},
            "token1": {"address": "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108", "decimals": 6},
            "amount0": "1000000000000000000",  # 1 ETH
            "amount1": "0",  # 0 USDC - will result in 0 price
        }

        token_pair = ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0xA0b86991c33E7407a0d2D5Ac14BD0a006Da31108")
        price = extract_ethereum_price(swap, token_pair)

        assert price is None  # Should return None due to price <= 0
