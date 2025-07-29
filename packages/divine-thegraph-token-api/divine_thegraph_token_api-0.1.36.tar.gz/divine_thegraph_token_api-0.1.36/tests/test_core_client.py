"""
Core Client Testing - Comprehensive coverage for client.py
Tests TheGraphTokenAPI factory methods and client creation.
"""

from thegraph_token_api.client import TheGraphTokenAPI
from thegraph_token_api.evm import EVMTokenAPI
from thegraph_token_api.svm import SVMTokenAPI
from thegraph_token_api.types import NetworkId, SolanaNetworkId


class TestTheGraphTokenAPIInitialization:
    """Test TheGraphTokenAPI initialization."""

    def test_initialization_with_api_key(self):
        """Test TheGraphTokenAPI initialization with API key."""
        client = TheGraphTokenAPI("test_key")
        assert client.api_key == "test_key"

    def test_initialization_with_api_key_and_base_url(self):
        """Test TheGraphTokenAPI initialization with API key and base URL."""
        client = TheGraphTokenAPI("test_key", "https://custom.api.com")
        assert client.api_key == "test_key"
        assert client.base_url == "https://custom.api.com"

    def test_inheritance_from_base_token_api(self):
        """Test TheGraphTokenAPI inherits from BaseTokenAPI (line 68)."""
        client = TheGraphTokenAPI("test_key", "https://custom.api.com")

        # Should have inherited properties and methods
        assert hasattr(client, "api_key")
        assert hasattr(client, "base_url")
        assert hasattr(client, "_validate_pagination")
        assert client.api_key == "test_key"
        assert client.base_url == "https://custom.api.com"


class TestEVMFactoryMethods:
    """Test EVM client factory methods."""

    def test_evm_factory_method(self):
        """Test evm factory method (line 92)."""
        client = TheGraphTokenAPI("test_key")

        # Test evm factory method with string network
        evm_client = client.evm("mainnet")
        assert isinstance(evm_client, EVMTokenAPI)
        assert evm_client.network == "mainnet"
        assert evm_client.api_key == "test_key"

    def test_evm_factory_method_with_enum(self):
        """Test evm factory method with NetworkId enum."""
        client = TheGraphTokenAPI("test_key")

        # Test evm factory method with enum
        evm_client = client.evm(NetworkId.MAINNET)
        assert isinstance(evm_client, EVMTokenAPI)
        assert evm_client.network == "mainnet"
        assert evm_client.api_key == "test_key"

    def test_evm_factory_method_with_custom_base_url(self):
        """Test evm factory method inherits custom base URL."""
        client = TheGraphTokenAPI("test_key", "https://custom.api.com")

        evm_client = client.evm("polygon")
        assert isinstance(evm_client, EVMTokenAPI)
        assert evm_client.network == "polygon"
        assert evm_client.api_key == "test_key"
        assert evm_client.base_url == "https://custom.api.com"

    def test_create_evm_client_class_method(self):
        """Test create_evm_client class method (line 152)."""
        # Test create_evm_client class method with all parameters
        evm_client = TheGraphTokenAPI.create_evm_client(
            network="mainnet", api_key="test_key", base_url="https://custom.api.com"
        )
        assert isinstance(evm_client, EVMTokenAPI)
        assert evm_client.network == "mainnet"
        assert evm_client.api_key == "test_key"
        assert evm_client.base_url == "https://custom.api.com"

    def test_create_evm_client_class_method_minimal(self):
        """Test create_evm_client class method with minimal parameters."""
        evm_client = TheGraphTokenAPI.create_evm_client(network=NetworkId.MATIC, api_key="test_key")
        assert isinstance(evm_client, EVMTokenAPI)
        assert evm_client.network == "matic"  # Enum value
        assert evm_client.api_key == "test_key"


class TestSVMFactoryMethods:
    """Test SVM client factory methods."""

    def test_svm_factory_method(self):
        """Test svm factory method (line 117)."""
        client = TheGraphTokenAPI("test_key")

        # Test svm factory method with string network
        svm_client = client.svm("solana")
        assert isinstance(svm_client, SVMTokenAPI)
        assert svm_client.network == "solana"
        assert svm_client.api_key == "test_key"

    def test_svm_factory_method_with_enum(self):
        """Test svm factory method with SolanaNetworkId enum."""
        client = TheGraphTokenAPI("test_key")

        # Test svm factory method with enum
        svm_client = client.svm(SolanaNetworkId.SOLANA)
        assert isinstance(svm_client, SVMTokenAPI)
        assert svm_client.network == "solana"
        assert svm_client.api_key == "test_key"

    def test_svm_factory_method_default_network(self):
        """Test svm factory method with default network."""
        client = TheGraphTokenAPI("test_key")

        # Test default network
        svm_client_default = client.svm()
        assert isinstance(svm_client_default, SVMTokenAPI)
        assert svm_client_default.network == "solana"  # Default
        assert svm_client_default.api_key == "test_key"

    def test_svm_factory_method_with_custom_base_url(self):
        """Test svm factory method inherits custom base URL."""
        client = TheGraphTokenAPI("test_key", "https://custom.api.com")

        svm_client = client.svm()
        assert isinstance(svm_client, SVMTokenAPI)
        assert svm_client.network == "solana"
        assert svm_client.api_key == "test_key"
        assert svm_client.base_url == "https://custom.api.com"

    def test_create_svm_client_class_method(self):
        """Test create_svm_client class method (line 180)."""
        # Test create_svm_client class method with all parameters
        svm_client = TheGraphTokenAPI.create_svm_client(
            network="solana", api_key="test_key", base_url="https://custom.api.com"
        )
        assert isinstance(svm_client, SVMTokenAPI)
        assert svm_client.network == "solana"
        assert svm_client.api_key == "test_key"
        assert svm_client.base_url == "https://custom.api.com"

    def test_create_svm_client_class_method_with_defaults(self):
        """Test create_svm_client class method with default parameters."""
        # Test with defaults
        svm_client_default = TheGraphTokenAPI.create_svm_client(api_key="test_key")
        assert isinstance(svm_client_default, SVMTokenAPI)
        assert svm_client_default.network == "solana"  # Default network
        assert svm_client_default.api_key == "test_key"

    def test_create_svm_client_class_method_with_enum(self):
        """Test create_svm_client class method with enum network."""
        svm_client = TheGraphTokenAPI.create_svm_client(network=SolanaNetworkId.SOLANA, api_key="test_key")
        assert isinstance(svm_client, SVMTokenAPI)
        assert svm_client.network == "solana"
        assert svm_client.api_key == "test_key"


class TestFactoryMethodsIntegration:
    """Test factory methods integration scenarios."""

    def test_multiple_client_creation(self):
        """Test creating multiple clients from the same factory."""
        main_client = TheGraphTokenAPI("test_key")

        # Create multiple EVM clients for different networks
        mainnet_client = main_client.evm(NetworkId.MAINNET)
        polygon_client = main_client.evm(NetworkId.MATIC)
        base_client = main_client.evm(NetworkId.BASE)

        assert mainnet_client.network == "mainnet"
        assert polygon_client.network == "matic"
        assert base_client.network == "base"

        # All should share the same API key
        assert mainnet_client.api_key == "test_key"
        assert polygon_client.api_key == "test_key"
        assert base_client.api_key == "test_key"

        # Create SVM client
        solana_client = main_client.svm()
        assert solana_client.network == "solana"
        assert solana_client.api_key == "test_key"

    def test_class_methods_vs_instance_methods(self):
        """Test class methods produce equivalent results to instance methods."""
        # Instance method approach
        main_client = TheGraphTokenAPI("test_key", "https://custom.com")
        evm_instance = main_client.evm("mainnet")
        svm_instance = main_client.svm("solana")

        # Class method approach
        evm_class = TheGraphTokenAPI.create_evm_client("mainnet", "test_key", "https://custom.com")
        svm_class = TheGraphTokenAPI.create_svm_client("solana", "test_key", "https://custom.com")

        # Should be equivalent
        assert isinstance(evm_instance, type(evm_class))
        assert isinstance(svm_instance, type(svm_class))
        assert evm_instance.network == evm_class.network
        assert svm_instance.network == svm_class.network
        assert evm_instance.api_key == evm_class.api_key
        assert svm_instance.api_key == svm_class.api_key

    def test_factory_methods_with_different_api_keys(self):
        """Test factory methods with different API keys."""
        # Main client with one key
        client1 = TheGraphTokenAPI("key1")
        evm1 = client1.evm("mainnet")

        # Direct creation with different key
        evm2 = TheGraphTokenAPI.create_evm_client("mainnet", "key2")

        assert evm1.api_key == "key1"
        assert evm2.api_key == "key2"
        assert evm1.network == evm2.network  # Same network

    def test_network_parameter_types(self):
        """Test factory methods accept both string and enum network parameters."""
        client = TheGraphTokenAPI("test_key")

        # String parameters
        evm_str = client.evm("mainnet")
        svm_str = client.svm("solana")

        # Enum parameters
        evm_enum = client.evm(NetworkId.MAINNET)
        svm_enum = client.svm(SolanaNetworkId.SOLANA)

        # Should produce equivalent results
        assert evm_str.network == evm_enum.network
        assert svm_str.network == svm_enum.network
