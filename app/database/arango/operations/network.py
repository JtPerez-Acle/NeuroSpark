"""Network operations for ArangoDB."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from arango.database import StandardDatabase
from arango.exceptions import DocumentGetError, DocumentInsertError

from .base import BaseOperations

logger = logging.getLogger(__name__)

class NetworkOperations(BaseOperations):
    """Network operations for ArangoDB."""
    
    def create_indexes(self) -> None:
        """Create indexes for network related collections."""
        # Network-specific indexes already created in individual modules
        pass
    
    async def setup_blockchain_collections(self) -> None:
        """Set up collections for blockchain entities."""
        try:
            logger.info("Setting up blockchain collections")
            
            # Create document collections
            node_collections = [
                'wallets',
                'transactions',
                'contracts',
                'events',
                'alerts',
            ]
            
            for collection_name in node_collections:
                if not self._db.has_collection(collection_name):
                    logger.info(f"Creating collection: {collection_name}")
                    self._db.create_collection(collection_name)
            
            # Create edge collections
            edge_collections = [
                'wallet_to_wallet',      # For transactions between wallets
                'wallet_to_contract',    # For wallet-contract interactions
                'contract_to_contract',  # For contract calls
                'entity_to_alert',       # For connecting entities to alerts
            ]
            
            for collection_name in edge_collections:
                if not self._db.has_collection(collection_name):
                    logger.info(f"Creating edge collection: {collection_name}")
                    self._db.create_collection(collection_name, edge=True)
            
            # Create graph
            if not self._db.has_graph('blockchain'):
                logger.info("Creating blockchain graph")
                graph = self._db.create_graph('blockchain')
                
                # Define edge definitions
                edge_definitions = [
                    {
                        'edge_collection': 'wallet_to_wallet',
                        'from_vertex_collections': ['wallets'],
                        'to_vertex_collections': ['wallets'],
                    },
                    {
                        'edge_collection': 'wallet_to_contract',
                        'from_vertex_collections': ['wallets'],
                        'to_vertex_collections': ['contracts'],
                    },
                    {
                        'edge_collection': 'contract_to_contract',
                        'from_vertex_collections': ['contracts'],
                        'to_vertex_collections': ['contracts'],
                    },
                    {
                        'edge_collection': 'entity_to_alert',
                        'from_vertex_collections': ['wallets', 'contracts', 'transactions'],
                        'to_vertex_collections': ['alerts'],
                    },
                ]
                
                # Add edge definitions to graph
                for edge_def in edge_definitions:
                    graph.create_edge_definition(
                        edge_collection=edge_def['edge_collection'],
                        from_vertex_collections=edge_def['from_vertex_collections'],
                        to_vertex_collections=edge_def['to_vertex_collections']
                    )
            
            logger.info("Blockchain collections setup complete")
        except Exception as e:
            logger.error(f"Error setting up blockchain collections: {e}")
            raise
    
    async def get_blockchain_network(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get blockchain network data from the database with optional filters.
        
        Args:
            filters: Optional filters to apply to the network data
            
        Returns:
            Dictionary containing nodes and edges
        """
        # Default filters
        if filters is None:
            filters = {}
        
        # Build AQL query based on filters
        query_parts = []
        bind_vars = {}
        
        # Query wallet nodes first, then contract nodes, and combine them
        query_parts.append("""
        LET wallet_nodes = (
            FOR wallet IN wallets
        """)
        
        # Add wallet node filters if any
        if 'wallet_type' in filters:
            query_parts.append("    FILTER wallet.wallet_type == @wallet_type")
            bind_vars['wallet_type'] = filters['wallet_type']
        
        if 'min_risk' in filters:
            query_parts.append("    FILTER wallet.risk_score >= @min_risk")
            bind_vars['min_risk'] = filters['min_risk']
        
        # Complete wallets query
        query_parts.append("""
            RETURN {
                id: wallet.address,
                type: "wallet",
                subtype: wallet.wallet_type,
                risk_score: wallet.risk_score,
                chain: wallet.chain,
                properties: wallet
            }
        )
        """)
        
        # Add contract nodes query
        query_parts.append("""
        LET contract_nodes = (
            FOR contract IN contracts
        """)
        
        # Add contract node filters
        if 'verified' in filters:
            query_parts.append("    FILTER contract.verified == @verified")
            bind_vars['verified'] = filters['verified']
        
        # Complete contracts query
        query_parts.append("""
            RETURN {
                id: contract.address,
                type: "contract",
                subtype: contract.contract_type,
                risk_score: contract.risk_score,
                chain: contract.chain,
                properties: contract
            }
        )
        
        // Combine wallet and contract nodes
        LET nodes = APPEND(wallet_nodes, contract_nodes)
        """)
        
        # Start edges query (transactions as wallet-to-wallet)
        query_parts.append("""
        LET wallet_edges = (
            FOR edge IN wallet_to_wallet
        """)
        
        # Add edge filters
        if 'start_time' in filters:
            query_parts.append("    FILTER edge.timestamp >= @start_time")
            bind_vars['start_time'] = filters['start_time']
        
        if 'end_time' in filters:
            query_parts.append("    FILTER edge.timestamp <= @end_time")
            bind_vars['end_time'] = filters['end_time']
        
        if 'min_value' in filters:
            query_parts.append("    FILTER edge.value >= @min_value")
            bind_vars['min_value'] = filters['min_value']
        
        if 'chain' in filters:
            query_parts.append("    FILTER edge.chain == @chain")
            bind_vars['chain'] = filters['chain']
        
        if 'addresses' in filters and filters['addresses']:
            query_parts.append("""
            LET from_wallet = DOCUMENT(edge._from)
            LET to_wallet = DOCUMENT(edge._to)
            FILTER from_wallet.address IN @addresses OR to_wallet.address IN @addresses
            """)
            bind_vars['addresses'] = filters['addresses']
        
        # Complete wallet edges query
        query_parts.append("""
            LET from_wallet = DOCUMENT(edge._from)
            LET to_wallet = DOCUMENT(edge._to)
            RETURN {
                source: from_wallet.address,
                target: to_wallet.address,
                type: "transaction",
                tx_hash: edge.hash,
                value: edge.value,
                timestamp: edge.timestamp,
                properties: edge
            }
        )
        """)
        
        # Add wallet-to-contract edges
        query_parts.append("""
        LET contract_edges = (
            FOR edge IN wallet_to_contract
        """)
        
        # Add edge filters (same as for wallet edges)
        if 'start_time' in filters:
            query_parts.append("    FILTER edge.timestamp >= @start_time")
        
        if 'end_time' in filters:
            query_parts.append("    FILTER edge.timestamp <= @end_time")
        
        if 'chain' in filters:
            query_parts.append("    FILTER edge.chain == @chain")
        
        if 'addresses' in filters and filters['addresses']:
            query_parts.append("""
            LET wallet = DOCUMENT(edge._from)
            LET contract = DOCUMENT(edge._to)
            FILTER wallet.address IN @addresses OR contract.address IN @addresses
            """)
        
        # Complete contract edges query
        query_parts.append("""
            LET wallet = DOCUMENT(edge._from)
            LET contract = DOCUMENT(edge._to)
            RETURN {
                source: wallet.address,
                target: contract.address,
                type: "interaction",
                relationship: edge.relationship,
                timestamp: edge.timestamp,
                properties: edge
            }
        )
        """)
        
        # Return combined results
        query_parts.append("""
        RETURN {
            nodes: nodes,
            edges: APPEND(wallet_edges, contract_edges)
        }
        """)
        
        # Execute the query
        query = "\n".join(query_parts)
        cursor = self._db.aql.execute(query, bind_vars=bind_vars)
        result = next(cursor)
        
        return result
    
    async def get_network_data(self, node_type: Optional[str] = None, time_range: Optional[str] = None) -> Dict[str, Any]:
        """Get network data from the database with optional filters.
        
        Args:
            node_type: Optional type of nodes to query (wallet, contract)
            time_range: Optional time range filter (24h, 7d, 30d, all)
            
        Returns:
            Dictionary containing nodes and edges
        """
        # Convert time range to timestamps
        start_time = None
        if time_range:
            now = datetime.now()
            if time_range == "24h":
                start_time = (now - timedelta(hours=24)).isoformat()
            elif time_range == "7d":
                start_time = (now - timedelta(days=7)).isoformat()
            elif time_range == "30d":
                start_time = (now - timedelta(days=30)).isoformat()
        
        # Build query parameters
        filters = {}
        
        if node_type == "wallet":
            filters["node_type"] = "wallet"
        elif node_type == "contract":
            filters["node_type"] = "contract"
        
        if start_time:
            filters["start_time"] = start_time
        
        return await self.get_blockchain_network(filters)
    
    async def clear_database(self) -> Dict[str, Any]:
        """Clear all data from the database.
        
        Returns:
            Dict containing number of nodes and relationships deleted
        """
        try:
            logger.info("Clearing all data from the database")
            
            # Get all collections
            collections = self._db.collections()
            
            # Count documents before deletion
            collection_counts = {}
            for collection in collections:
                if not collection["system"]:  # Skip system collections
                    name = collection["name"]
                    count = self._db.collection(name).count()
                    collection_counts[name] = count
            
            # Traditional collections
            traditional_collections = ['agents', 'runs', 'interactions', 'participations']
            traditional_nodes = sum(collection_counts.get(col, 0) for col in ['agents', 'runs'])
            traditional_edges = sum(collection_counts.get(col, 0) for col in ['interactions', 'participations'])
            
            # Blockchain collections
            blockchain_nodes = sum(collection_counts.get(col, 0) for col in ['wallets', 'transactions', 'contracts', 'events', 'alerts'])
            blockchain_edges = sum(collection_counts.get(col, 0) for col in ['wallet_to_wallet', 'wallet_to_contract', 'contract_to_contract', 'entity_to_alert'])
            
            # Total counts
            total_nodes = traditional_nodes + blockchain_nodes
            total_edges = traditional_edges + blockchain_edges
            
            # Truncate each non-system collection
            for collection in collections:
                if not collection["system"]:
                    self._db.collection(collection["name"]).truncate()
            
            logger.info(f"Deleted {total_nodes} nodes and {total_edges} relationships")
            
            return {
                "success": True,
                "nodes_deleted": total_nodes,
                "relationships_deleted": total_edges,
                "traditional_nodes_deleted": traditional_nodes,
                "traditional_edges_deleted": traditional_edges,
                "blockchain_nodes_deleted": blockchain_nodes,
                "blockchain_edges_deleted": blockchain_edges
            }
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            raise