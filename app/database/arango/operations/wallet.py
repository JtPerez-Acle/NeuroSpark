"""Wallet operations for ArangoDB."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from arango.database import StandardDatabase
from arango.exceptions import DocumentGetError, DocumentInsertError

from .base import BaseOperations

logger = logging.getLogger(__name__)

class WalletOperations(BaseOperations):
    """Wallet operations for ArangoDB."""
    
    def create_indexes(self) -> None:
        """Create indexes for wallet collection."""
        if 'wallets' in self._db.collections():
            self._db.collection('wallets').add_hash_index(['address', 'chain'], unique=True)
            self._db.collection('wallets').add_hash_index(['wallet_type'], unique=False)
            self._db.collection('wallets').add_hash_index(['risk_score'], unique=False)
    
    async def store_wallet(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a wallet in the database.
        
        Args:
            wallet_data: Dictionary containing wallet data
            
        Returns:
            The stored wallet document
        """
        # Check if wallets collection exists, create if not
        if not self._db.has_collection('wallets'):
            self._db.create_collection('wallets')
            self.create_indexes()
        
        # Get wallets collection
        wallets_collection = self._db.collection('wallets')
        
        try:
            # Try to get the key from the document
            key = wallet_data.get('_key')
            if not key:
                # Create a key from the address and chain
                address = wallet_data.get('address', '').replace('0x', '')
                chain = wallet_data.get('chain', 'ethereum')
                key = f"{chain}_{address.lower()}"
                wallet_data['_key'] = key
            
            # Calculate risk score if not provided
            if 'risk_score' not in wallet_data:
                # Import here to avoid circular imports
                from app.risk.scoring import calculate_wallet_risk
                wallet_data['risk_score'] = calculate_wallet_risk(wallet_data)
                logger.info(f"Calculated risk score for wallet {key}: {wallet_data['risk_score']}")
            
            logger.info(f"Storing wallet with key: {key}")
            
            # Check if wallet exists, update or insert
            if self._document_exists(wallets_collection, key):
                wallets_collection.update(key, wallet_data)
                logger.info(f"Updated existing wallet: {key}")
            else:
                wallets_collection.insert(wallet_data)
                logger.info(f"Inserted new wallet: {key}")
                
            return wallet_data
        except Exception as e:
            logger.error(f"Error storing wallet: {e}")
            logger.error(f"Wallet data: {wallet_data}")
            raise
    
    async def get_wallet(self, address: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get wallet information from the database.
        
        Args:
            address: Wallet address
            chain: Blockchain identifier
            
        Returns:
            Wallet data dictionary or None if not found
        """
        # Check if wallets collection exists
        if not self._db.has_collection('wallets'):
            logger.warning("Wallets collection does not exist")
            return None
        
        try:
            # Normalize address
            normalized_address = address.replace('0x', '').lower()
            key = f"{chain}_{normalized_address}"
            
            # Get wallet from collection
            wallet = self._db.collection('wallets').get({'_key': key})
            
            if wallet:
                # Remove internal fields
                wallet.pop('_id', None)
                wallet.pop('_key', None)
                wallet.pop('_rev', None)
                return wallet
                
            return None
        except Exception as e:
            logger.error(f"Error getting wallet {address}: {e}")
            return None
    
    async def get_wallets(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all wallets from the database.
        
        Args:
            limit: Maximum number of wallets to return
            offset: Number of wallets to skip
            
        Returns:
            List of wallet dictionaries
        """
        # Ensure the collection exists
        if not self._db.has_collection('wallets'):
            return []
        
        query = """
        FOR wallet IN wallets
        SORT wallet.last_active DESC
        LIMIT @offset, @limit
        RETURN UNSET(wallet, '_id', '_key', '_rev')
        """
        
        cursor = self._db.aql.execute(query, bind_vars={'limit': limit, 'offset': offset})
        return [doc for doc in cursor]
    
    async def get_wallet_by_risk(self, min_risk_score: float = 75.0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get high-risk wallets from the database.
        
        Args:
            min_risk_score: Minimum risk score (0-100)
            limit: Maximum number of wallets to return
            
        Returns:
            List of high-risk wallet dictionaries
        """
        # Ensure the collection exists
        if not self._db.has_collection('wallets'):
            return []
        
        query = """
        FOR wallet IN wallets
        FILTER wallet.risk_score >= @min_risk_score
        SORT wallet.risk_score DESC
        LIMIT @limit
        RETURN UNSET(wallet, '_id', '_key', '_rev')
        """
        
        cursor = self._db.aql.execute(query, bind_vars={
            'min_risk_score': min_risk_score,
            'limit': limit
        })
        return [doc for doc in cursor]