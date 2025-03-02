"""Data generator module for creating synthetic blockchain data."""
from datetime import datetime, timezone, timedelta
import random
import uuid
import string
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from abc import ABC, abstractmethod

class ScenarioGenerator(ABC):
    """Base interface for scenario generators."""
    
    @abstractmethod
    def generate_data(self, num_agents: int, num_interactions: int, **kwargs) -> Dict[str, Any]:
        """Generate data for the scenario."""
        pass
    
    @abstractmethod
    def create_agent(self, **kwargs) -> Dict[str, Any]:
        """Create an agent for this scenario."""
        pass
    
    @abstractmethod
    def generate_interaction(self, sender: Dict[str, Any], receiver: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate an interaction between agents."""
        pass


class BlockchainScenarioGenerator(ScenarioGenerator):
    """Ethereum Blockchain scenario generator for creating synthetic blockchain data."""
    
    def __init__(self):
        """Initialize BlockchainScenarioGenerator."""
        # Wallet types and roles
        self.wallet_types = ["EOA", "contract"]
        self.eoa_roles = ["trader", "liquidity_provider", "borrower", "lender", "nft_collector", "whale", "retail"]
        self.contract_roles = ["dex", "token", "lending", "nft", "bridge", "dao", "staking"]
        
        # Transaction types
        self.transaction_types = [
            "transfer", "swap", "mint", "burn", "deposit", "withdraw", 
            "borrow", "repay", "stake", "unstake", "vote", "claim"
        ]
        
        # Token details
        self.token_symbols = ["ETH", "USDT", "USDC", "DAI", "WETH", "WBTC", "LINK", "UNI", "AAVE", "CRV"]
        self.token_decimals = {
            "ETH": 18, "USDT": 6, "USDC": 6, "DAI": 18, "WETH": 18, 
            "WBTC": 8, "LINK": 18, "UNI": 18, "AAVE": 18, "CRV": 18
        }
        
        # Preset scenario templates
        self.scenarios = {
            "dex": {
                "name": "Decentralized Exchange",
                "contracts": ["dex", "token", "token"],
                "eoawallet_roles": ["trader", "liquidity_provider", "whale", "retail"],
                "interactions": ["swap", "add_liquidity", "remove_liquidity"]
            },
            "lending": {
                "name": "Lending Protocol",
                "contracts": ["lending", "token", "token"],
                "eoawallet_roles": ["borrower", "lender", "whale", "retail"],
                "interactions": ["deposit", "withdraw", "borrow", "repay"]
            },
            "nft": {
                "name": "NFT Marketplace",
                "contracts": ["nft", "token"],
                "eoawallet_roles": ["nft_collector", "trader", "whale", "retail"],
                "interactions": ["mint", "transfer", "list", "buy", "sell"]
            },
            "token_transfer": {
                "name": "Token Transfer",
                "contracts": ["token"],
                "eoawallet_roles": ["trader", "whale", "retail"],
                "interactions": ["transfer"]
            }
        }
        
        # Current block and time tracking
        self.current_block = 16000000
        self.current_time = datetime.now(timezone.utc)
        self.block_time = 12  # seconds
    
    def _generate_eth_address(self) -> str:
        """Generate a random Ethereum address."""
        return f"0x{''.join(random.choices('0123456789abcdef', k=40))}"
    
    def _generate_tx_hash(self) -> str:
        """Generate a random transaction hash."""
        return f"0x{''.join(random.choices('0123456789abcdef', k=64))}"
    
    def _generate_block_hash(self) -> str:
        """Generate a random block hash."""
        return f"0x{''.join(random.choices('0123456789abcdef', k=64))}"
    
    def _generate_token_amount(self, token: str, is_whale: bool = False) -> int:
        """Generate a realistic token amount in base units."""
        decimals = self.token_decimals.get(token, 18)
        
        if is_whale:
            min_amount = 10 ** (decimals + random.randint(2, 4))  # 100-10,000 tokens for whales
            max_amount = 10 ** (decimals + random.randint(5, 8))  # 100K-100M tokens for whales
        else:
            min_amount = 10 ** (decimals - random.randint(1, 3))  # 0.001-0.1 tokens for normal users
            max_amount = 10 ** (decimals + random.randint(0, 2))  # 1-100 tokens for normal users
            
        return random.randint(min_amount, max_amount)
    
    def _generate_gas_params(self) -> Tuple[int, int, int]:
        """Generate realistic gas parameters (gas_price, gas_limit, gas_used)."""
        gas_price = random.randint(1, 100) * 10**9  # 1-100 gwei
        gas_limit = random.choice([21000, 50000, 100000, 200000, 300000])
        gas_used = int(gas_limit * random.uniform(0.6, 1.0))  # 60-100% of limit
        return gas_price, gas_limit, gas_used
    
    def _advance_blockchain(self) -> None:
        """Advance blockchain state by one block."""
        self.current_block += 1
        self.current_time += timedelta(seconds=self.block_time)
    
    def _tokenize_name(self, name: str) -> str:
        """Generate a token symbol from a name."""
        words = name.split()
        if len(words) > 1:
            return ''.join(word[0].upper() for word in words)
        else:
            return name[:3].upper()
    
    def create_agent(self, agent_type: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
        """Create a blockchain agent (wallet or contract)."""
        if not agent_type:
            agent_type = random.choice(self.wallet_types)
            
        if not role:
            if agent_type == "EOA":
                role = random.choice(self.eoa_roles)
            else:  # Contract
                role = random.choice(self.contract_roles)
        
        # Generate address and base agent properties
        address = self._generate_eth_address()
        agent_id = address.lower()
        
        # Common properties
        agent = {
            "id": agent_id,
            "address": address,
            "type": agent_type,
            "role": role,
            "chain": "ethereum",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "first_seen": self.current_time.isoformat(),
            "last_active": self.current_time.isoformat(),
            "balance": 0.0,
            "transactions": [],
            "tags": [role]
        }
        
        # Type-specific properties
        if agent_type == "EOA":
            # Regular wallet
            agent["balance"] = round(random.uniform(0.1, 100.0), 6)  # ETH balance
            agent["nonce"] = random.randint(1, 100)
            
            # Add role-specific properties
            if role == "whale":
                agent["balance"] = round(random.uniform(100.0, 10000.0), 6)
                agent["tags"].append("high_value")
            elif role == "trader":
                agent["tags"].append("high_frequency")
            elif role == "liquidity_provider":
                agent["tags"].append("defi")
            elif role == "nft_collector":
                agent["tags"].append("nft")
        
        else:  # Contract
            # Smart contract
            agent["verified"] = random.choice([True, False])
            agent["creation_tx"] = self._generate_tx_hash()
            agent["creation_block"] = self.current_block
            
            # Contract-specific properties based on role
            if role == "token":
                token_name = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))
                agent["name"] = f"{token_name} Token"
                agent["symbol"] = token_name
                agent["decimals"] = random.choice([6, 8, 18])
                agent["total_supply"] = 10 ** (agent["decimals"] + random.randint(7, 9))
                agent["tags"].extend(["erc20", "token"])
            
            elif role == "dex":
                agent["name"] = f"{random.choice(['Swap', 'Dex', 'Exchange', 'Uni', 'Sushi'])}Swap v{random.randint(1,3)}"
                agent["factory"] = self._generate_eth_address()
                agent["fee_tier"] = random.choice([0.01, 0.05, 0.1, 0.3, 1.0])
                agent["total_volume_usd"] = random.randint(10**5, 10**9)
                agent["tags"].extend(["defi", "dex", "amm"])
            
            elif role == "lending":
                agent["name"] = f"{random.choice(['Lend', 'Borrow', 'Compound', 'Aave', 'Lend'])}Protocol"
                agent["total_supplied"] = random.randint(10**6, 10**9)
                agent["total_borrowed"] = int(agent["total_supplied"] * random.uniform(0.4, 0.8))
                agent["tags"].extend(["defi", "lending", "borrow"])
            
            elif role == "nft":
                agent["name"] = f"{random.choice(['Crypto', 'Bored', 'Punk', 'Cool', 'Super'])} {random.choice(['Apes', 'Punks', 'Bears', 'Pandas', 'Art'])}"
                agent["floor_price"] = round(random.uniform(0.01, 100.0), 3)
                agent["total_supply"] = random.randint(1000, 10000)
                agent["minted"] = random.randint(100, agent["total_supply"])
                agent["tags"].extend(["nft", "erc721"])
        
        # Calculate risk score based on randomized attributes
        agent["risk_score"] = random.uniform(0, 100)
        
        return agent
    
    def generate_interaction(
        self, 
        sender: Dict[str, Any], 
        receiver: Dict[str, Any], 
        scenario: str = "token_transfer",
        block_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a blockchain interaction between two agents."""
        # Use current block if not specified
        if block_number is None:
            block_number = self.current_block
            
        # Determine interaction type based on scenario and agent roles
        interaction_types = self.scenarios[scenario]["interactions"]
        interaction_type = random.choice(interaction_types)
        
        # Generate common transaction properties
        tx_hash = self._generate_tx_hash()
        gas_price, gas_limit, gas_used = self._generate_gas_params()
        value = 0  # Default to 0 ETH unless specified
        
        # Generate transaction based on type
        if interaction_type == "transfer":
            # Simple token or ETH transfer
            if random.random() < 0.3:  # 30% chance of ETH transfer
                value = int(random.uniform(0.001, 1.0) * 10**18)  # Convert ETH to wei
                token_symbol = "ETH"
                token_amount = value
                message = f"Transferred {value / 10**18:.6f} ETH from {sender['role']} to {receiver['role']}"
            else:  # Token transfer
                token_symbol = random.choice(self.token_symbols)
                token_amount = self._generate_token_amount(token_symbol, sender["role"] == "whale")
                message = f"Transferred {token_amount / 10**self.token_decimals[token_symbol]:.6f} {token_symbol} from {sender['role']} to {receiver['role']}"
                
        elif interaction_type == "swap":
            # DEX swap
            token_in = random.choice(self.token_symbols)
            token_out = random.choice([t for t in self.token_symbols if t != token_in])
            amount_in = self._generate_token_amount(token_in, sender["role"] == "whale")
            amount_out = int(amount_in * random.uniform(0.9, 1.1) * 
                            (10**self.token_decimals[token_out] / 10**self.token_decimals[token_in]))
            
            message = f"Swapped {amount_in / 10**self.token_decimals[token_in]:.6f} {token_in} for {amount_out / 10**self.token_decimals[token_out]:.6f} {token_out}"
            token_symbol = f"{token_in}→{token_out}"
            token_amount = amount_in
        
        elif interaction_type in ["deposit", "withdraw"]:
            # Lending protocol interaction
            token_symbol = random.choice(self.token_symbols)
            token_amount = self._generate_token_amount(token_symbol, sender["role"] == "whale")
            
            if interaction_type == "deposit":
                message = f"Deposited {token_amount / 10**self.token_decimals[token_symbol]:.6f} {token_symbol} into {receiver.get('name', 'protocol')}"
            else:
                message = f"Withdrew {token_amount / 10**self.token_decimals[token_symbol]:.6f} {token_symbol} from {receiver.get('name', 'protocol')}"
                
        elif interaction_type in ["borrow", "repay"]:
            # Lending protocol interaction
            token_symbol = random.choice(self.token_symbols)
            token_amount = self._generate_token_amount(token_symbol, sender["role"] == "whale")
            interest_rate = round(random.uniform(0.01, 0.2), 4)
            
            if interaction_type == "borrow":
                message = f"Borrowed {token_amount / 10**self.token_decimals[token_symbol]:.6f} {token_symbol} at {interest_rate:.2%} interest"
            else:
                message = f"Repaid {token_amount / 10**self.token_decimals[token_symbol]:.6f} {token_symbol} loan"
        
        elif interaction_type in ["mint", "burn"]:
            # NFT or token mint/burn
            if receiver.get("role") == "nft":
                token_amount = random.randint(1, 5)  # Number of NFTs
                if interaction_type == "mint":
                    message = f"Minted {token_amount} NFT(s) from {receiver.get('name', 'collection')}"
                else:
                    message = f"Burned {token_amount} NFT(s) from {receiver.get('name', 'collection')}"
                token_symbol = f"{receiver.get('name', 'NFT')} NFT"
            else:
                token_symbol = random.choice(self.token_symbols)
                token_amount = self._generate_token_amount(token_symbol, sender["role"] == "whale")
                if interaction_type == "mint":
                    message = f"Minted {token_amount / 10**self.token_decimals[token_symbol]:.6f} {token_symbol}"
                else:
                    message = f"Burned {token_amount / 10**self.token_decimals[token_symbol]:.6f} {token_symbol}"
        
        elif interaction_type in ["add_liquidity", "remove_liquidity"]:
            # DEX liquidity provision
            token_a = random.choice(self.token_symbols)
            token_b = random.choice([t for t in self.token_symbols if t != token_a])
            token_a_amount = self._generate_token_amount(token_a, sender["role"] == "whale")
            token_b_amount = self._generate_token_amount(token_b, sender["role"] == "whale")
            
            if interaction_type == "add_liquidity":
                message = f"Added liquidity: {token_a_amount / 10**self.token_decimals[token_a]:.6f} {token_a} and {token_b_amount / 10**self.token_decimals[token_b]:.6f} {token_b}"
            else:
                message = f"Removed liquidity: {token_a_amount / 10**self.token_decimals[token_a]:.6f} {token_a} and {token_b_amount / 10**self.token_decimals[token_b]:.6f} {token_b}"
            token_symbol = f"{token_a}/{token_b}"
            token_amount = token_a_amount
            
        elif interaction_type in ["list", "buy", "sell"]:
            # NFT marketplace interactions
            nft_id = random.randint(1, 10000)
            price = round(random.uniform(0.01, 100.0), 3)
            token_amount = 1
            
            if interaction_type == "list":
                message = f"Listed NFT #{nft_id} from {receiver.get('name', 'collection')} for {price} ETH"
            elif interaction_type == "buy":
                message = f"Bought NFT #{nft_id} from {receiver.get('name', 'collection')} for {price} ETH"
                value = int(price * 10**18)  # Convert ETH to wei
            else:
                message = f"Sold NFT #{nft_id} from {receiver.get('name', 'collection')} for {price} ETH"
            token_symbol = f"{receiver.get('name', 'NFT')} #{nft_id}"
            
        else:
            # Generic interaction
            token_symbol = random.choice(self.token_symbols)
            token_amount = self._generate_token_amount(token_symbol, sender["role"] == "whale")
            message = f"{interaction_type} interaction: {sender['role']} to {receiver['role']}"
            
        # Create transaction data (following blockchain model structure)
        transaction = {
            "hash": tx_hash,
            "block_number": block_number,
            "timestamp": self.current_time.isoformat(),
            "from_address": sender["address"],
            "to_address": receiver["address"],
            "value": value,
            "gas_price": gas_price,
            "gas_limit": gas_limit,
            "gas_used": gas_used,
            "status": "success",
            "chain": "ethereum"
        }
            
        # Create interaction based on the transaction
        interaction = {
            "interaction_id": tx_hash,
            "timestamp": self.current_time.isoformat(),
            "sender_id": sender["id"],
            "receiver_id": receiver["id"],
            "topic": f"ethereum_{interaction_type}",
            "message": message,
            "interaction_type": interaction_type,
            "metadata": {
                "scenario": scenario,
                "transaction": transaction,
                "token_symbol": token_symbol,
                "token_amount": token_amount,
                "block": block_number,
                "blockchain": "ethereum",
                "gas_fee_eth": (gas_price * gas_used) / 10**18
            }
        }
        
        return interaction
    
    def generate_data(
        self, 
        num_agents: int, 
        num_interactions: int, 
        scenario: str = "token_transfer", 
        blocks: int = 100, 
        **kwargs
    ) -> Dict[str, Any]:
        """Generate blockchain scenario data.
        
        Args:
            num_agents: Number of agents to create
            num_interactions: Number of interactions to generate
            scenario: Type of scenario (dex, lending, nft, token_transfer)
            blocks: Number of blocks to simulate
            
        Returns:
            Dictionary containing agents, interactions, and run metadata
        """
        # Validate scenario
        if scenario not in self.scenarios:
            scenario = "token_transfer"  # Default to simple transfers
            
        # Determine agent distribution
        num_contracts = max(1, num_agents // 5)  # 20% contracts
        num_eoa = num_agents - num_contracts
        
        # Select roles based on scenario
        contract_roles = self.scenarios[scenario]["contracts"]
        eoa_roles = self.scenarios[scenario]["eoawallet_roles"]
        
        # Create agents (wallets and contracts)
        contracts = []
        for _ in range(num_contracts):
            role = random.choice(contract_roles)
            contracts.append(self.create_agent("contract", role))
            
        eoa_wallets = []
        for _ in range(num_eoa):
            role = random.choice(eoa_roles)
            eoa_wallets.append(self.create_agent("EOA", role))
            
        agents = eoa_wallets + contracts
        
        # Create a run ID
        run_id = str(uuid.uuid4()).replace('-', '_')
        
        # Generate interactions across a range of blocks
        interactions = []
        interactions_per_block = max(1, num_interactions // blocks)
        
        for _ in range(blocks):
            # Generate interactions for this block
            for _ in range(interactions_per_block):
                # Select agents based on scenario logic
                if scenario == "dex":
                    # DEX interactions: trader/LP -> DEX contract
                    sender = random.choice(eoa_wallets)
                    dex_contracts = [c for c in contracts if c["role"] == "dex"]
                    # Make sure we have at least one DEX contract
                    if not dex_contracts:
                        # Create a DEX contract if none exists
                        new_contract = self.create_agent("contract", "dex")
                        contracts.append(new_contract)
                        agents.append(new_contract)
                        dex_contracts = [new_contract]
                    receiver = random.choice(dex_contracts)
                        
                elif scenario == "lending":
                    # Lending interactions: borrower/lender -> lending contract
                    sender = random.choice(eoa_wallets)
                    lending_contracts = [c for c in contracts if c["role"] == "lending"]
                    # Make sure we have at least one lending contract
                    if not lending_contracts:
                        # Create a lending contract if none exists
                        new_contract = self.create_agent("contract", "lending")
                        contracts.append(new_contract)
                        agents.append(new_contract)
                        lending_contracts = [new_contract]
                    receiver = random.choice(lending_contracts)
                
                elif scenario == "nft":
                    # NFT interactions: collector -> NFT contract
                    sender = random.choice(eoa_wallets)
                    nft_contracts = [c for c in contracts if c["role"] == "nft"]
                    # Make sure we have at least one NFT contract
                    if not nft_contracts:
                        # Create an NFT contract if none exists
                        new_contract = self.create_agent("contract", "nft")
                        contracts.append(new_contract)
                        agents.append(new_contract)
                        nft_contracts = [new_contract]
                    receiver = random.choice(nft_contracts)
                
                else:  # token_transfer
                    # Token transfers between wallets
                    sender = random.choice(eoa_wallets)
                    if random.random() < 0.3:  # 30% chance for wallet-to-contract
                        receiver = random.choice(contracts) if contracts else random.choice(eoa_wallets)
                    else:  # 70% chance for wallet-to-wallet
                        receiver = random.choice([w for w in eoa_wallets if w["id"] != sender["id"]])
                
                # Generate the interaction
                interaction = self.generate_interaction(
                    sender, 
                    receiver, 
                    scenario=scenario,
                    block_number=self.current_block
                )
                
                # Add run ID
                interaction["run_id"] = run_id
                interactions.append(interaction)
            
            # Advance blockchain state
            self._advance_blockchain()
            
            # Limit to requested number of interactions if specified
            if len(interactions) >= num_interactions:
                interactions = interactions[:num_interactions]
                break
        
        return {
            "agents": agents,
            "interactions": interactions,
            "run_id": run_id,
            "scenario": scenario,
            "blockchain": "ethereum",
            "start_block": self.current_block - blocks,
            "end_block": self.current_block - 1
        }


class DataGenerator:
    """Generate synthetic blockchain data for testing."""
    
    def __init__(self, scenario: Optional[str] = None):
        """Initialize blockchain data generator."""
        # Web3 blockchain scenarios
        self.blockchain_scenarios = {
            "dex": "Decentralized Exchange Trading",
            "lending": "Lending Protocol Activity",
            "nft": "NFT Marketplace",
            "token_transfer": "Token Transfer Network"
        }
        
        # Set up blockchain scenario generator
        self.scenario = scenario if scenario in self.blockchain_scenarios else "token_transfer"
        self.scenario_generator = BlockchainScenarioGenerator()
    
    def create_wallet(self, wallet_type: str = "EOA", role: Optional[str] = None) -> Dict[str, Any]:
        """Create a single blockchain wallet."""
        return self.scenario_generator.create_agent(wallet_type, role)

    def create_wallets(self, num_wallets: int, wallet_type: str = "EOA") -> List[Dict[str, Any]]:
        """Create multiple blockchain wallets."""
        return [self.create_wallet(wallet_type) for _ in range(num_wallets)]

    def generate_transaction(
        self, 
        sender: Dict[str, Any], 
        receiver: Dict[str, Any], 
        scenario: Optional[str] = None,
        block_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a blockchain transaction between two wallets."""
        if not scenario:
            scenario = self.scenario
            
        return self.scenario_generator.generate_interaction(
            sender=sender,
            receiver=receiver,
            scenario=scenario,
            block_number=block_number
        )

    def generate_blockchain_data(
        self, 
        num_wallets: int, 
        num_transactions: int, 
        scenario: Optional[str] = None, 
        blocks: int = 100
    ) -> Dict[str, Any]:
        """Generate synthetic blockchain dataset with wallets and transactions."""
        if not scenario:
            scenario = self.scenario
            
        return self.scenario_generator.generate_data(
            num_agents=num_wallets,
            num_interactions=num_transactions,
            scenario=scenario,
            blocks=blocks
        )
    
    def generate_scenario_data(
        self,
        num_agents: int,
        num_interactions: int,
        scenario: str = "token_transfer",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate data for a specific blockchain scenario.

        This is an alias for generate_blockchain_data to maintain
        backward compatibility with older tests.
        
        Args:
            num_agents: Number of agents to generate
            num_interactions: Number of interactions to generate
            scenario: Scenario type (dex, lending, nft, token_transfer)
            **kwargs: Additional parameters to pass to the generator
            
        Returns:
            Dictionary with generated agents and interactions
        """
        return self.generate_blockchain_data(
            num_wallets=num_agents,
            num_transactions=num_interactions,
            scenario=scenario,
            **kwargs
        )
    
    def get_available_scenarios(self) -> Dict[str, str]:
        """Get available blockchain scenarios with descriptions."""
        return self.blockchain_scenarios
