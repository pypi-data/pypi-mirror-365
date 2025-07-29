"""
Core Types Testing - Comprehensive coverage for types.py
Tests all enum string conversions and type definitions.
"""

from thegraph_token_api.types import (
    ActivityType,
    BaseResponse,
    Interval,
    NetworkId,
    OrderBy,
    OrderDirection,
    Protocol,
    SolanaNetworkId,
    SolanaPrograms,
    SwapPrograms,
    TokenStandard,
)


class TestEnumStringConversions:
    """Test string conversion for all enum values to achieve 100% coverage."""

    def test_network_id_string_conversion(self):
        """Test NetworkId enum string conversion."""
        for network in [
            NetworkId.MAINNET,
            NetworkId.MATIC,
            NetworkId.BSC,
            NetworkId.ARBITRUM_ONE,
            NetworkId.OPTIMISM,
            NetworkId.AVALANCHE,
            NetworkId.BASE,
            NetworkId.UNICHAIN,
        ]:
            assert isinstance(str(network), str)
            assert str(network) == network.value

    def test_solana_network_id_string_conversion(self):
        """Test SolanaNetworkId enum string conversion."""
        for network in [SolanaNetworkId.SOLANA]:
            assert isinstance(str(network), str)
            assert str(network) == network.value

    def test_token_standard_string_conversion(self):
        """Test TokenStandard enum string conversion (including EMPTY to hit __str__ method)."""
        for standard in [TokenStandard.EMPTY, TokenStandard.ERC721, TokenStandard.ERC1155]:
            assert isinstance(str(standard), str)
            assert str(standard) == standard.value

    def test_activity_type_string_conversion(self):
        """Test ActivityType enum string conversion (no custom __str__ method)."""
        for activity in [ActivityType.TRANSFER, ActivityType.MINT, ActivityType.BURN]:
            assert isinstance(str(activity), str)
            # ActivityType doesn't have a custom __str__ method, so it returns the enum name
            assert str(activity) == f"ActivityType.{activity.name}"

    def test_order_direction_string_conversion(self):
        """Test OrderDirection enum string conversion (explicit __str__ call to hit line 70)."""
        for direction in [OrderDirection.ASC, OrderDirection.DESC]:
            assert isinstance(str(direction), str)
            assert str(direction) == direction.value

    def test_order_by_string_conversion(self):
        """Test OrderBy enum string conversion (explicit __str__ call to hit line 79)."""
        for order in [OrderBy.TIMESTAMP, OrderBy.VALUE]:
            assert isinstance(str(order), str)
            assert str(order) == order.value

    def test_interval_string_conversion(self):
        """Test Interval enum string conversion (explicit __str__ call to hit line 90)."""
        for interval in [Interval.ONE_HOUR, Interval.FOUR_HOURS, Interval.ONE_DAY, Interval.ONE_WEEK]:
            assert isinstance(str(interval), str)
            assert str(interval) == interval.value

    def test_protocol_string_conversion(self):
        """Test Protocol enum string conversion."""
        for protocol in [Protocol.UNISWAP_V2, Protocol.UNISWAP_V3, Protocol.UNISWAP_V4]:
            assert isinstance(str(protocol), str)
            assert str(protocol) == protocol.value

    def test_solana_programs_string_conversion(self):
        """Test SolanaPrograms enum string conversion (explicit __str__ call to hit line 108)."""
        for program in [SolanaPrograms.TOKEN, SolanaPrograms.TOKEN_2022]:
            assert isinstance(str(program), str)
            assert str(program) == program.value

    def test_swap_programs_string_conversion(self):
        """Test SwapPrograms enum string conversion (explicit __str__ call to hit line 120)."""
        for program in [
            SwapPrograms.RAYDIUM,
            SwapPrograms.PUMP_FUN_CORE,
            SwapPrograms.JUPITER_V4,
            SwapPrograms.JUPITER_V6,
            SwapPrograms.PUMP_FUN_AMM,
        ]:
            assert isinstance(str(program), str)
            assert str(program) == program.value


class TestTypeDefinitions:
    """Test type definitions and structures."""

    def test_base_response_structure(self):
        """Test BaseResponse TypedDict structure."""
        # Verify BaseResponse is properly defined
        assert hasattr(BaseResponse, "__annotations__")

    def test_network_id_values(self):
        """Test NetworkId enum has all expected values."""
        expected_networks = ["arbitrum-one", "avalanche", "base", "bsc", "mainnet", "matic", "optimism", "unichain"]
        actual_networks = [network.value for network in NetworkId]
        assert set(expected_networks) == set(actual_networks)

    def test_swap_programs_values(self):
        """Test SwapPrograms enum has all expected values."""
        expected_programs = [
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # RAYDIUM
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # PUMP_FUN_CORE
            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",  # PUMP_FUN_AMM
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",  # JUPITER_V4
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",  # JUPITER_V6
        ]
        actual_programs = [program.value for program in SwapPrograms]
        assert set(expected_programs) == set(actual_programs)
