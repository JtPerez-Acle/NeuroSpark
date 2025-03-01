"""Contract operations for ArangoDB."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from arango.database import StandardDatabase
from arango.exceptions import DocumentGetError, DocumentInsertError

from .base import BaseOperations

logger = logging.getLogger(__name__)

class ContractOperations(BaseOperations):
    """Contract operations for ArangoDB."""
    
    def create_indexes(self) -> None:
        """Create indexes for contract collection."""
        if 'contracts' in self._db.collections():
            self._db.collection('contracts').add_hash_index(['address', 'chain'], unique=True)
            self._db.collection('contracts').add_hash_index(['creator'], unique=False)
            self._db.collection('contracts').add_hash_index(['verified'], unique=False)
            self._db.collection('contracts').add_hash_index(['risk_score'], unique=False)
        
        if 'wallet_to_contract' in self._db.collections():
            self._db.collection('wallet_to_contract').add_hash_index(['timestamp'], unique=False)
            self._db.collection('wallet_to_contract').add_hash_index(['tx_hash'], unique=False)
    
    async def store_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a contract in the database.
        
        Args:
            contract_data: Dictionary containing contract data
            
        Returns:
            The stored contract document
        """
        # Check if contracts collection exists, create if not
        if not self._db.has_collection('contracts'):
            self._db.create_collection('contracts')
            self.create_indexes()
        
        # Get contracts collection
        contracts_collection = self._db.collection('contracts')
        
        try:
            # Try to get the key from the document
            key = contract_data.get('_key')
            if not key:
                # Create a key from the address and chain
                address = contract_data.get('address', '').replace('0x', '')
                chain = contract_data.get('chain', 'ethereum')
                key = f"{chain}_{address.lower()}"
                contract_data['_key'] = key
            
            # Calculate risk score if not provided
            if 'risk_score' not in contract_data:
                # Import here to avoid circular imports
                from app.risk.scoring import calculate_contract_risk
                contract_data['risk_score'] = calculate_contract_risk(contract_data)
                logger.info(f"Calculated risk score for contract {key}: {contract_data['risk_score']}")
            
            logger.info(f"Storing contract with key: {key}")
            
            # Check if contract exists, update or insert
            if self._document_exists(contracts_collection, key):
                contracts_collection.update(key, contract_data)
                logger.info(f"Updated existing contract: {key}")
            else:
                contracts_collection.insert(contract_data)
                logger.info(f"Inserted new contract: {key}")
                
            # If we have creator info, link creator to contract
            creator = contract_data.get('creator')
            chain = contract_data.get('chain', 'ethereum')
            
            if creator:
                # Get wallets collection
                wallets_collection = self._db.collection('wallets')
                
                # Normalize creator address
                creator_addr = creator.replace('0x', '').lower()
                creator_key = f"{chain}_{creator_addr}"
                
                # Ensure creator wallet exists
                if not self._document_exists(wallets_collection, creator_key):
                    # Create minimal creator wallet
                    wallets_collection.insert({
                        '_key': creator_key,
                        'address': creator,
                        'chain': chain,
                        'wallet_type': 'EOA',
                        'first_seen': contract_data.get('creation_timestamp'),
                        'last_active': contract_data.get('creation_timestamp')
                    })
                
                # Create wallet_to_contract edge collection if it doesn't exist
                if not self._db.has_collection('wallet_to_contract'):
                    self._db.create_collection('wallet_to_contract', edge=True)
                    self._db.collection('wallet_to_contract').add_hash_index(['timestamp'], unique=False)
                    self._db.collection('wallet_to_contract').add_hash_index(['tx_hash'], unique=False)
                
                # Create wallet_to_contract edge
                wallet_to_contract = self._db.collection('wallet_to_contract')
                edge_key = f"{creator_key}_created_{key}"
                
                # Check if edge already exists
                try:
                    if not self._document_exists(wallet_to_contract, edge_key):
                        wallet_to_contract.insert({
                            '_key': edge_key,
                            '_from': f'wallets/{creator_key}',
                            '_to': f'contracts/{key}',
                            'relationship': 'created',
                            'tx_hash': contract_data.get('creation_tx'),
                            'timestamp': contract_data.get('creation_timestamp'),
                            'chain': chain
                        })
                        logger.info(f"Created wallet_to_contract edge for contract creation: {key}")
                except Exception as e:
                    logger.warning(f"Error creating wallet_to_contract edge: {e}")
                
            return contract_data
        except Exception as e:
            logger.error(f"Error storing contract: {e}")
            logger.error(f"Contract data: {contract_data}")
            raise
    
    async def get_contract(self, address: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get contract information from the database.
        
        Args:
            address: Contract address
            chain: Blockchain identifier
            
        Returns:
            Contract data dictionary or None if not found
        """
        # Check if contracts collection exists
        if not self._db.has_collection('contracts'):
            logger.warning("Contracts collection does not exist")
            return None
        
        try:
            # Normalize address
            normalized_address = address.replace('0x', '').lower()
            key = f"{chain}_{normalized_address}"
            
            # Get contract from collection
            contract = self._db.collection('contracts').get({'_key': key})
            
            if contract:
                # Remove internal fields
                contract.pop('_id', None)
                contract.pop('_key', None)
                contract.pop('_rev', None)
                return contract
                
            return None
        except Exception as e:
            logger.error(f"Error getting contract {address}: {e}")
            return None
    
    async def get_contracts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get contracts from the database.
        
        Args:
            limit: Maximum number of contracts to return
            offset: Number of contracts to skip
            
        Returns:
            List of contract dictionaries
        """
        # Ensure the collection exists
        if not self._db.has_collection('contracts'):
            return []
        
        query = """
        FOR contract IN contracts
        SORT contract.creation_timestamp DESC
        LIMIT @offset, @limit
        RETURN UNSET(contract, '_id', '_key', '_rev')
        """
        
        cursor = self._db.aql.execute(query, bind_vars={'limit': limit, 'offset': offset})
        return [doc for doc in cursor]
    
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
        # Check if required collections exist
        if not self._db.has_collection('wallets') or not self._db.has_collection('wallet_to_contract'):
            logger.warning("Required collections do not exist")
            return []
        
        try:
            # Normalize address
            normalized_address = address.replace('0x', '').lower()
            wallet_key = f"{chain}_{normalized_address}"
            
            # Query contracts using AQL
            query = """
            FOR edge IN wallet_to_contract
                FILTER edge._from == @wallet_from
                LET contract = DOCUMENT(edge._to)
                SORT edge.timestamp DESC
                LIMIT @offset, @limit
                RETURN UNSET(contract, '_id', '_key', '_rev')
            """
            
            bind_vars = {
                "wallet_from": f"wallets/{wallet_key}",
                "offset": offset,
                "limit": limit
            }
            
            cursor = self._db.aql.execute(query, bind_vars=bind_vars)
            contracts = [doc for doc in cursor]
            
            return contracts
        except Exception as e:
            logger.error(f"Error getting wallet contracts for {address}: {e}")
            return []
            
    async def get_contract_by_risk(self, min_risk_score: float = 75.0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get high-risk contracts from the database.
        
        Args:
            min_risk_score: Minimum risk score (0-100)
            limit: Maximum number of contracts to return
            
        Returns:
            List of high-risk contract dictionaries
        """
        # Ensure the collection exists
        if not self._db.has_collection('contracts'):
            return []
        
        query = """
        FOR contract IN contracts
        FILTER contract.risk_score >= @min_risk_score
        SORT contract.risk_score DESC
        LIMIT @limit
        RETURN UNSET(contract, '_id', '_key', '_rev')
        """
        
        cursor = self._db.aql.execute(query, bind_vars={
            'min_risk_score': min_risk_score,
            'limit': limit
        })
        return [doc for doc in cursor]