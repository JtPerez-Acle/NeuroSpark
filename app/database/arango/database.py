"""ArangoDB database implementation."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from arango.database import StandardDatabase
from arango.exceptions import DocumentGetError, DocumentInsertError

from ..base import DatabaseInterface
from .connection import ArangoConnection
from .operations.base import BaseOperations
from .operations.wallet import WalletOperations
from .operations.transaction import TransactionOperations
from .operations.contract import ContractOperations
from .operations.event import EventOperations
from .operations.alert import AlertOperations
from .operations.network import NetworkOperations

logger = logging.getLogger(__name__)

class ArangoDatabase(DatabaseInterface):
    """ArangoDB database implementation."""
    
    def __init__(self, host: str, port: int, username: str, password: str, db_name: str):
        """Initialize the database.
        
        Args:
            host: ArangoDB host
            port: ArangoDB port
            username: Username
            password: Password
            db_name: Database name
        """
        self._connection = ArangoConnection(host, port, username, password, db_name)
        self._db = None
        self._wallet_ops = None
        self._transaction_ops = None
        self._contract_ops = None
        self._event_ops = None
        self._alert_ops = None
        self._network_ops = None
    
    async def connect(self) -> None:
        """Connect to the database."""
        await self._connection.connect()
        self._db = self._connection.get_database()
        
        # Initialize operation modules
        self._wallet_ops = WalletOperations(self._db)
        self._transaction_ops = TransactionOperations(self._db)
        self._contract_ops = ContractOperations(self._db)
        self._event_ops = EventOperations(self._db)
        self._alert_ops = AlertOperations(self._db)
        self._network_ops = NetworkOperations(self._db)
        
        # Ensure indexes exist for better performance
        self._create_indexes()
    
    def _create_indexes(self) -> None:
        """Create indexes for better query performance."""
        # Create indexes using operation modules
        if hasattr(self, '_wallet_ops') and self._wallet_ops:
            self._wallet_ops.create_indexes()
            
        if hasattr(self, '_transaction_ops') and self._transaction_ops:
            self._transaction_ops.create_indexes()
            
        if hasattr(self, '_contract_ops') and self._contract_ops:
            self._contract_ops.create_indexes()
            
        if hasattr(self, '_event_ops') and self._event_ops:
            self._event_ops.create_indexes()
            
        if hasattr(self, '_alert_ops') and self._alert_ops:
            self._alert_ops.create_indexes()
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        await self._connection.disconnect()
        self._db = None
        self._wallet_ops = None
        self._transaction_ops = None
        self._contract_ops = None
        self._event_ops = None
        self._alert_ops = None
        self._network_ops = None
    
    def is_connected(self) -> bool:
        """Check if database is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self._db is not None
    
    # ====================
    # = Wallet Operations =
    # ====================
    
    async def store_wallet(self, wallet: Dict[str, Any]) -> Dict[str, Any]:
        """Store a wallet in the database.
        
        Args:
            wallet: Dictionary containing wallet data
            
        Returns:
            The stored wallet document
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._wallet_ops.store_wallet(wallet)
    
    async def get_wallets(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all wallets from the database.
        
        Args:
            limit: Maximum number of wallets to return
            offset: Number of wallets to skip
            
        Returns:
            List of wallet dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._wallet_ops.get_wallets(limit, offset)
    
    async def get_wallet(self, address: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get a single wallet from the database.
        
        Args:
            address: Blockchain address of the wallet
            chain: Blockchain identifier (default: ethereum)
            
        Returns:
            Wallet dictionary or None if not found
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._wallet_ops.get_wallet(address, chain)
    
    async def get_wallets_by_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get wallets by query filter.
        
        Args:
            query: Dictionary of query filters (key-value pairs)
            
        Returns:
            List of wallet dictionaries matching the query
        """
        if not self.is_connected():
            await self.connect()
        
        # Build AQL query
        aql_parts = ["FOR w IN wallets"]
        bind_vars = {}
        
        # Add filters
        filters = []
        for key, value in query.items():
            filters.append(f"w.{key} == @{key}")
            bind_vars[key] = value
        
        if filters:
            aql_parts.append("FILTER " + " AND ".join(filters))
        
        aql_parts.append("RETURN UNSET(w, '_id', '_key', '_rev')")
        
        aql_query = " ".join(aql_parts)
        
        # Execute query
        cursor = self._db.aql.execute(aql_query, bind_vars=bind_vars)
        return [doc for doc in cursor]
            
    async def get_wallet_by_risk(self, min_risk_score: float = 75.0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get high-risk wallets from the database.
        
        Args:
            min_risk_score: Minimum risk score (0-100)
            limit: Maximum number of wallets to return
            
        Returns:
            List of high-risk wallet dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._wallet_ops.get_wallet_by_risk(min_risk_score, limit)
    
    # =========================
    # = Transaction Operations =
    # =========================
    
    async def store_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Store a blockchain transaction in the database.
        
        Args:
            transaction: Dictionary containing transaction data
            
        Returns:
            The stored transaction document
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._transaction_ops.store_transaction(transaction)
    
    async def get_transactions(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get transactions from the database.
        
        Args:
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List of transaction dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._transaction_ops.get_transactions(limit, offset)
    
    async def get_wallet_transactions(self, address: str, chain: str = "ethereum", 
                                     limit: int = 20, offset: int = 0,
                                     sort_field: str = "timestamp", 
                                     sort_direction: str = "desc") -> List[Dict[str, Any]]:
        """Get all transactions associated with a wallet.
        
        Args:
            address: Wallet address
            chain: Blockchain identifier
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            sort_field: Field to sort by
            sort_direction: Sort direction (asc or desc)
            
        Returns:
            List of transactions
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._transaction_ops.get_wallet_transactions(
            address, chain, limit, offset, sort_field, sort_direction
        )
    
    async def get_transaction(self, tx_hash: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get a specific transaction by hash.
        
        Args:
            tx_hash: Transaction hash
            chain: Blockchain identifier
            
        Returns:
            Transaction data dictionary or None if not found
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._transaction_ops.get_transaction(tx_hash, chain)
            
    async def get_transactions_by_block(self, block_number: int, chain: str = "ethereum",
                                       limit: int = 100) -> List[Dict[str, Any]]:
        """Get transactions by block number.
        
        Args:
            block_number: Block number
            chain: Blockchain identifier
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._transaction_ops.get_transactions_by_block(block_number, chain, limit)
    
    # ======================
    # = Contract Operations =
    # ======================
    
    async def store_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a contract in the database.
        
        Args:
            contract_data: Dictionary containing contract data
            
        Returns:
            The stored contract document
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._contract_ops.store_contract(contract_data)
    
    async def get_contract(self, address: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get contract information from the database.
        
        Args:
            address: Contract address
            chain: Blockchain identifier
            
        Returns:
            Contract data dictionary or None if not found
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._contract_ops.get_contract(address, chain)
    
    async def get_contracts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get contracts from the database.
        
        Args:
            limit: Maximum number of contracts to return
            offset: Number of contracts to skip
            
        Returns:
            List of contract dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._contract_ops.get_contracts(limit, offset)
    
    async def get_wallet_contracts(self, address: str, chain: str = "ethereum",
                                 limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get contracts deployed or interacted with by a wallet.
        
        Args:
            address: Wallet address
            chain: Blockchain identifier
            limit: Maximum number of contracts to return
            offset: Number of contracts to skip
            
        Returns:
            List of contract dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._contract_ops.get_wallet_contracts(address, chain, limit, offset)
    
    # ====================
    # = Event Operations =
    # ====================
    
    async def store_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store an event in the database.
        
        Args:
            event_data: Dictionary containing event data
            
        Returns:
            The stored event document
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._event_ops.store_event(event_data)
    
    async def get_events(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get events from the database.
        
        Args:
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of event dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._event_ops.get_events(limit, offset)
    
    async def get_contract_events(self, contract_address: str, chain: str = "ethereum",
                               event_name: Optional[str] = None, 
                               from_block: Optional[int] = None,
                               to_block: Optional[int] = None,
                               limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get events for a contract.
        
        Args:
            contract_address: Contract address
            chain: Blockchain identifier
            event_name: Optional event name filter
            from_block: Optional starting block number
            to_block: Optional ending block number
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of event dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._event_ops.get_contract_events(
            contract_address, chain, event_name, from_block, to_block, limit, offset
        )
    
    # ====================
    # = Alert Operations =
    # ====================
    
    async def store_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store an alert in the database.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            The stored alert document
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._alert_ops.store_alert(alert_data)
    
    async def get_alerts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get alerts from the database.
        
        Args:
            limit: Maximum number of alerts to return
            offset: Number of alerts to skip
            
        Returns:
            List of alert dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._alert_ops.get_alerts(limit, offset)
    
    async def get_active_alerts(self, 
                              severity: Optional[str] = None,
                              entity_type: Optional[str] = None,
                              alert_type: Optional[str] = None,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """Get active security alerts from the database.
        
        Args:
            severity: Optional filter by severity level (low, medium, high, critical)
            entity_type: Optional filter by entity type (wallet, contract, transaction)
            alert_type: Optional filter by alert type
            limit: Maximum number of alerts to return
            
        Returns:
            List of active alert dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._alert_ops.get_active_alerts(severity, entity_type, alert_type, limit)
    
    async def get_entity_alerts(self, entity: str, entity_type: str, 
                              limit: int = 20) -> List[Dict[str, Any]]:
        """Get alerts for a specific entity.
        
        Args:
            entity: Entity identifier (address, tx hash, etc.)
            entity_type: Type of entity (wallet, contract, transaction)
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries for the entity
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._alert_ops.get_entity_alerts(entity, entity_type, limit)
    
    # =====================
    # = Network Operations =
    # =====================
    
    async def setup_blockchain_collections(self) -> None:
        """Set up collections for blockchain entities."""
        if not self.is_connected():
            await self.connect()
        
        await self._network_ops.setup_blockchain_collections()
    
    async def get_blockchain_network(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get blockchain network data from the database with optional filters.
        
        Args:
            filters: Optional filters to apply to the network data
            
        Returns:
            Dictionary containing nodes and edges
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._network_ops.get_blockchain_network(filters)
    
    async def get_network_data(self, node_type: Optional[str] = None, 
                            time_range: Optional[str] = None) -> Dict[str, Any]:
        """Get network data from the database with optional filters.
        
        Args:
            node_type: Optional type of nodes to query (wallet, contract)
            time_range: Optional time range filter (24h, 7d, 30d, all)
            
        Returns:
            Dictionary containing nodes and edges
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._network_ops.get_network_data(node_type, time_range)
    
    async def clear_database(self) -> Dict[str, Any]:
        """Clear all data from the database.
        
        Returns:
            Dict containing number of nodes and relationships deleted
        """
        if not self.is_connected():
            await self.connect()
        
        return await self._network_ops.clear_database()
    
    # =====================
    # = Risk Operations =
    # =====================
    
    async def get_high_risk_entities(self, entity_type: str, min_risk_score: float = 75.0, 
                                   limit: int = 20) -> List[Dict[str, Any]]:
        """Get high-risk entities from the database.
        
        Args:
            entity_type: Type of entity (wallets, contracts, transactions)
            min_risk_score: Minimum risk score threshold (0-100)
            limit: Maximum number of entities to return
            
        Returns:
            List of high-risk entities
        """
        if not self.is_connected():
            await self.connect()
        
        # Route to appropriate operations based on entity type
        if entity_type == "wallets":
            return await self._wallet_ops.get_wallet_by_risk(min_risk_score, limit)
        elif entity_type == "contracts":
            return await self._contract_ops.get_contract_by_risk(min_risk_score, limit)
        elif entity_type == "transactions":
            return await self._transaction_ops.get_transaction_by_risk(min_risk_score, limit)
        else:
            logger.warning(f"Invalid entity type for risk query: {entity_type}")
            return []
    
    # =====================
    # = Graph/Network API =
    # =====================
    
    async def get_network(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get network data from the database with optional filters.
        
        Args:
            filters: Optional filters to apply to the network data
            
        Returns:
            Dictionary containing nodes and edges
        """
        if not self.is_connected():
            await self.connect()
        
        # For backward compatibility, redirect to blockchain network
        return await self._network_ops.get_blockchain_network(filters)
    
    async def query_network(self, node_type: Optional[str] = None, 
                          relationship_type: Optional[str] = None,
                          start_time: Optional[str] = None, 
                          end_time: Optional[str] = None,
                          addresses: Optional[List[str]] = None, 
                          limit: Optional[int] = None,
                          include_properties: bool = True) -> Dict[str, Any]:
        """Advanced query for blockchain network data with multiple filter options.
        
        Args:
            node_type: Filter nodes by type (wallet, contract)
            relationship_type: Filter relationships by type (transaction, call)
            start_time: Filter for transactions after this time
            end_time: Filter for transactions before this time
            addresses: Filter for transactions involving these blockchain addresses
            limit: Maximum number of results to return
            include_properties: Whether to include node and edge properties
            
        Returns:
            Dictionary containing nodes and edges matching the query
        """
        if not self.is_connected():
            await self.connect()
        
        # Prepare blockchain network filters
        filters = {
            "node_type": node_type,
            "relationship_type": relationship_type,
            "start_time": start_time,
            "end_time": end_time,
            "addresses": addresses,
            "include_properties": include_properties
        }
        
        # Filter out None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Get blockchain network with filters
        result = await self._network_ops.get_blockchain_network(filters)
        
        # Apply limit if specified
        if limit and isinstance(limit, int):
            result["nodes"] = result["nodes"][:limit]
            result["edges"] = result["edges"][:limit]
            
        return result