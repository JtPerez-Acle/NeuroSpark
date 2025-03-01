"""Tests for blockchain data generator module."""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Mock the logging before importing the module
with patch('app.monitoring.logging_config.setup_logging', MagicMock()):
    from app.data_generator import DataGenerator, BlockchainScenarioGenerator

class TestBlockchainDataGenerator:
    """Test cases for blockchain data generator."""

    def setup_method(self):
        """Set up test cases."""
        self.generator = DataGenerator()
        self.scenario_generator = BlockchainScenarioGenerator()

    def test_create_wallet(self):
        """Test creating a single wallet."""
        # Test with specific type and role
        wallet = self.generator.create_wallet("EOA", "trader")
        assert wallet["type"] == "EOA"
        assert wallet["role"] == "trader"
        assert "address" in wallet
        assert wallet["address"].startswith("0x")
        assert "created_at" in wallet
        assert "chain" in wallet
        assert wallet["chain"] == "ethereum"
        
        # Test contract wallet
        contract = self.generator.create_wallet("contract", "dex")
        assert contract["type"] == "contract"
        assert contract["role"] == "dex"
        assert "address" in contract
        assert "verified" in contract
        assert "creation_tx" in contract
        assert "creation_block" in contract
        
        # Test with random type
        random_wallet = self.generator.create_wallet()
        assert random_wallet["type"] in ["EOA", "contract"]
        assert "role" in random_wallet
        assert "address" in random_wallet

    def test_create_wallets(self):
        """Test creating multiple wallets."""
        num_wallets = 3
        wallets = self.generator.create_wallets(num_wallets)
        
        assert len(wallets) == num_wallets
        for wallet in wallets:
            assert "address" in wallet
            assert "type" in wallet
            assert "role" in wallet
            assert "created_at" in wallet
            assert "chain" in wallet
            assert wallet["chain"] == "ethereum"

    def test_generate_blockchain_data(self):
        """Test generating a complete blockchain dataset."""
        num_wallets = 5
        num_transactions = 10
        data = self.generator.generate_blockchain_data(num_wallets, num_transactions)
        
        assert "agents" in data
        assert "interactions" in data
        assert "run_id" in data
        assert "scenario" in data
        assert "blockchain" in data
        assert "start_block" in data
        assert "end_block" in data
        assert data["blockchain"] == "ethereum"
        assert len(data["agents"]) == num_wallets
        assert len(data["interactions"]) == num_transactions
        
        # Verify wallet structure
        for agent in data["agents"]:
            assert "id" in agent
            assert "address" in agent
            assert "type" in agent
            assert "role" in agent
            assert "chain" in agent
            assert "tags" in agent
            assert "created_at" in agent
        
        # Verify transaction structure
        for interaction in data["interactions"]:
            assert "interaction_id" in interaction
            assert "sender_id" in interaction
            assert "receiver_id" in interaction
            assert "topic" in interaction
            assert "message" in interaction
            assert "interaction_type" in interaction
            assert "timestamp" in interaction
            assert "metadata" in interaction
            assert "transaction" in interaction["metadata"]
            assert "blockchain" in interaction["metadata"]
            assert interaction["metadata"]["blockchain"] == "ethereum"
            
            # Check transaction fields
            tx = interaction["metadata"]["transaction"]
            assert "hash" in tx
            assert "block_number" in tx
            assert "timestamp" in tx
            assert "from_address" in tx
            assert "to_address" in tx
            assert "gas_price" in tx
            assert "gas_used" in tx
            assert "status" in tx
            assert "chain" in tx
            assert tx["chain"] == "ethereum"

    def test_scenario_generator_init(self):
        """Test initializing generator with a scenario."""
        # Test each scenario type
        generator_dex = DataGenerator(scenario="dex")
        assert generator_dex.scenario == "dex"
        assert generator_dex.scenario_generator is not None
        
        generator_lending = DataGenerator(scenario="lending")
        assert generator_lending.scenario == "lending"
        assert generator_lending.scenario_generator is not None
        
        generator_nft = DataGenerator(scenario="nft")
        assert generator_nft.scenario == "nft"
        assert generator_nft.scenario_generator is not None
        
        generator_token = DataGenerator(scenario="token_transfer")
        assert generator_token.scenario == "token_transfer"
        assert generator_token.scenario_generator is not None
        
        # Test invalid scenario
        generator_invalid = DataGenerator(scenario="invalid")
        assert generator_invalid.scenario == "token_transfer"  # Default
        assert generator_invalid.scenario_generator is not None

    def test_blockchain_dex_scenario(self):
        """Test DEX scenario generation."""
        generator = DataGenerator(scenario="dex")
        data = generator.generate_blockchain_data(10, 15)
        
        assert data["scenario"] == "dex"
        
        # Verify agents include DEX contracts
        dex_contracts = [a for a in data["agents"] if a["type"] == "contract" and a["role"] == "dex"]
        assert len(dex_contracts) > 0
        
        # Verify we have interactions related to DEX
        dex_interactions = [i for i in data["interactions"] 
                           if i["interaction_type"] in ["swap", "add_liquidity", "remove_liquidity"]]
        assert len(dex_interactions) > 0

    def test_blockchain_lending_scenario(self):
        """Test lending scenario generation."""
        generator = DataGenerator(scenario="lending")
        data = generator.generate_blockchain_data(10, 15)
        
        assert data["scenario"] == "lending"
        
        # Verify agents include lending contracts
        lending_contracts = [a for a in data["agents"] if a["type"] == "contract" and a["role"] == "lending"]
        assert len(lending_contracts) > 0
        
        # Verify we have interactions related to lending
        lending_interactions = [i for i in data["interactions"] 
                               if i["interaction_type"] in ["deposit", "withdraw", "borrow", "repay"]]
        assert len(lending_interactions) > 0

    def test_generate_transaction(self):
        """Test generating a transaction between wallets."""
        sender = self.generator.create_wallet("EOA", "trader")
        receiver = self.generator.create_wallet("contract", "token")
        
        transaction = self.generator.generate_transaction(sender, receiver, scenario="token_transfer")
        
        assert "interaction_id" in transaction
        assert "sender_id" in transaction
        assert "receiver_id" in transaction
        assert transaction["sender_id"] == sender["id"]
        assert transaction["receiver_id"] == receiver["id"]
        assert "topic" in transaction and "ethereum" in transaction["topic"]
        assert "message" in transaction
        assert "interaction_type" in transaction
        assert "timestamp" in transaction
        assert "metadata" in transaction
        assert "transaction" in transaction["metadata"]
        assert "token_symbol" in transaction["metadata"]
        assert "token_amount" in transaction["metadata"]
        assert "blockchain" in transaction["metadata"]
        assert transaction["metadata"]["blockchain"] == "ethereum"

    def test_blockchain_helper_functions(self):
        """Test blockchain helper functions."""
        # Test address generation
        eth_address = self.scenario_generator._generate_eth_address()
        assert eth_address.startswith("0x")
        assert len(eth_address) == 42  # 0x + 40 hex chars
        
        # Test transaction hash generation
        tx_hash = self.scenario_generator._generate_tx_hash()
        assert tx_hash.startswith("0x")
        assert len(tx_hash) == 66  # 0x + 64 hex chars
        
        # Test block hash generation
        block_hash = self.scenario_generator._generate_block_hash()
        assert block_hash.startswith("0x")
        assert len(block_hash) == 66  # 0x + 64 hex chars
        
        # Test token amount generation
        token_amount = self.scenario_generator._generate_token_amount("ETH")
        assert isinstance(token_amount, int)
        assert token_amount > 0
        
        # Test gas params generation
        gas_price, gas_limit, gas_used = self.scenario_generator._generate_gas_params()
        assert isinstance(gas_price, int)
        assert isinstance(gas_limit, int)
        assert isinstance(gas_used, int)
        assert gas_price > 0
        assert gas_limit > 0
        assert gas_used > 0
        assert gas_used <= gas_limit
        
        # Test blockchain advancement
        initial_block = self.scenario_generator.current_block
        initial_time = self.scenario_generator.current_time
        self.scenario_generator._advance_blockchain()
        assert self.scenario_generator.current_block == initial_block + 1
        assert (self.scenario_generator.current_time - initial_time).total_seconds() == self.scenario_generator.block_time

    def test_get_available_scenarios(self):
        """Test getting available blockchain scenarios."""
        scenarios = self.generator.get_available_scenarios()
        
        assert isinstance(scenarios, dict)
        assert "dex" in scenarios
        assert "lending" in scenarios
        assert "nft" in scenarios
        assert "token_transfer" in scenarios
        assert len(scenarios) >= 4