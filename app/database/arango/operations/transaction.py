"""Transaction operations for ArangoDB."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from arango.database import StandardDatabase
from arango.exceptions import DocumentGetError, DocumentInsertError

from .base import BaseOperations

logger = logging.getLogger(__name__)

class TransactionOperations(BaseOperations):
    """Transaction operations for ArangoDB."""
    
    def create_indexes(self) -> None:
        """Create indexes for transaction collection."""
        if 'transactions' in self._db.collections():
            self._db.collection('transactions').add_hash_index(['hash', 'chain'], unique=True)
            self._db.collection('transactions').add_hash_index(['from_address'], unique=False)
            self._db.collection('transactions').add_hash_index(['to_address'], unique=False)
            self._db.collection('transactions').add_hash_index(['block_number'], unique=False)
            self._db.collection('transactions').add_hash_index(['timestamp'], unique=False)
            self._db.collection('transactions').add_hash_index(['status'], unique=False)
            self._db.collection('transactions').add_hash_index(['risk_score'], unique=False)
        
        if 'wallet_to_wallet' in self._db.collections():
            self._db.collection('wallet_to_wallet').add_hash_index(['timestamp'], unique=False)
            self._db.collection('wallet_to_wallet').add_hash_index(['tx_hash'], unique=False)
    
    async def store_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a transaction in the database.
        
        Args:
            transaction_data: Dictionary containing transaction data
            
        Returns:
            The stored transaction document
        """
        # Prepare transaction document
        tx_doc = transaction_data.copy()
        
        # Create transactions collection if it doesn't exist
        if not self._db.has_collection('transactions'):
            self._db.create_collection('transactions')
            self.create_indexes()
        
        # Create wallet_to_wallet edge collection if it doesn't exist
        if not self._db.has_collection('wallet_to_wallet'):
            self._db.create_collection('wallet_to_wallet', edge=True)
            # Create indexes
            self._db.collection('wallet_to_wallet').add_hash_index(['hash'], unique=False)
            self._db.collection('wallet_to_wallet').add_hash_index(['timestamp'], unique=False)
        
        # Ensure transaction has required fields
        if 'hash' not in tx_doc:
            raise ValueError("Transaction must have a hash")
        
        if 'from_address' not in tx_doc:
            raise ValueError("Transaction must have a sender address (from_address)")
        
        # Handle compatible field names
        if 'sender_id' in tx_doc and 'from_address' not in tx_doc:
            tx_doc['from_address'] = tx_doc['sender_id']
        
        if 'receiver_id' in tx_doc and 'to_address' not in tx_doc:
            tx_doc['to_address'] = tx_doc['receiver_id']
        
        # Set defaults for missing fields
        if 'chain' not in tx_doc:
            tx_doc['chain'] = 'ethereum'
        
        if 'timestamp' not in tx_doc:
            tx_doc['timestamp'] = datetime.now().isoformat()
        
        if 'block_number' not in tx_doc:
            # Use a placeholder value if not provided
            tx_doc['block_number'] = 0
        
        if 'status' not in tx_doc:
            tx_doc['status'] = 'success'
        
        # Create a safe key for ArangoDB (hash_chain)
        key = f"{tx_doc['hash']}_{tx_doc['chain']}".replace('-', '_').replace(':', '_').replace('/', '_')
        
        # Get transactions collection and wallet_to_wallet edge collection
        transactions_collection = self._db.collection('transactions')
        wallet_to_wallet = self._db.collection('wallet_to_wallet')
        
        try:
            logger.info(f"Storing transaction with hash: {tx_doc['hash']} on {tx_doc['chain']}")
            
            # First ensure that both sender and receiver wallets exist
            from_address = tx_doc['from_address']
            to_address = tx_doc.get('to_address')
            
            # Create wallet key format
            from_key = f"{from_address}_{tx_doc['chain']}".replace('-', '_').replace(':', '_').replace('/', '_')
            
            # Ensure wallets collection exists
            if not self._db.has_collection('wallets'):
                self._db.create_collection('wallets')
                # Create indexes
                self._db.collection('wallets').add_hash_index(['address', 'chain'], unique=True)
                self._db.collection('wallets').add_hash_index(['type'], unique=False)
            
            wallets_collection = self._db.collection('wallets')
            
            # Check if sender wallet exists, create if not
            if not self._document_exists(wallets_collection, from_key):
                logger.info(f"Creating sender wallet: {from_address}")
                wallets_collection.insert({
                    '_key': from_key,
                    'address': from_address,
                    'chain': tx_doc['chain'],
                    'type': 'EOA',  # Default to EOA
                    'first_seen': tx_doc['timestamp'],
                    'last_active': tx_doc['timestamp']
                })
            
            # If receiver address exists, check/create that wallet too
            if to_address:
                to_key = f"{to_address}_{tx_doc['chain']}".replace('-', '_').replace(':', '_').replace('/', '_')
                if not self._document_exists(wallets_collection, to_key):
                    logger.info(f"Creating receiver wallet: {to_address}")
                    wallets_collection.insert({
                        '_key': to_key,
                        'address': to_address,
                        'chain': tx_doc['chain'],
                        'type': 'unknown',  # Default to unknown, could be contract or EOA
                        'first_seen': tx_doc['timestamp'],
                        'last_active': tx_doc['timestamp']
                    })
            
            # Calculate risk score if not provided
            if 'risk_score' not in tx_doc:
                # Import here to avoid circular imports
                from app.risk.scoring import calculate_transaction_risk
                tx_doc['risk_score'] = calculate_transaction_risk(tx_doc)
                logger.info(f"Calculated risk score for transaction {key}: {tx_doc['risk_score']}")
            
            # Store transaction document
            if self._document_exists(transactions_collection, key):
                logger.info(f"Updating existing transaction: {key}")
                # Update existing transaction
                transactions_collection.update({'_key': key}, tx_doc)
            else:
                logger.info(f"Inserting new transaction: {key}")
                # Insert new transaction with key
                tx_doc['_key'] = key
                transactions_collection.insert(tx_doc)
            
            # Create wallet-to-wallet edge if we have both sender and receiver
            if to_address:
                edge_key = f"tx_{key}"
                edge = {
                    '_key': edge_key,
                    '_from': f'wallets/{from_key}',
                    '_to': f'wallets/{to_key}',
                    'hash': tx_doc['hash'],
                    'chain': tx_doc['chain'],
                    'value': tx_doc.get('value', 0),
                    'timestamp': tx_doc['timestamp'],
                    'block_number': tx_doc['block_number']
                }
                
                try:
                    if not self._document_exists(wallet_to_wallet, edge_key):
                        logger.info(f"Creating wallet-to-wallet edge: {from_address} -> {to_address}")
                        wallet_to_wallet.insert(edge)
                except DocumentInsertError as e:
                    logger.warning(f"Error creating wallet-to-wallet edge: {e}")
            
            return tx_doc
            
        except DocumentInsertError as e:
            logger.error(f"Error storing transaction: {e}")
            logger.error(f"Transaction data: {tx_doc}")
            raise
    
    async def get_transaction(self, tx_hash: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get a specific transaction by hash.
        
        Args:
            tx_hash: Transaction hash
            chain: Blockchain identifier
            
        Returns:
            Transaction data dictionary or None if not found
        """
        # Ensure the collection exists
        if not self._db.has_collection('transactions'):
            return None
        
        # Create key format (hash_chain)
        key = f"{tx_hash}_{chain}".replace('-', '_').replace(':', '_').replace('/', '_')
        
        try:
            doc = self._db.collection('transactions').get({'_key': key})
            if doc:
                # Remove internal fields
                doc.pop('_id', None)
                doc.pop('_key', None)
                doc.pop('_rev', None)
                return doc
            return None
        except DocumentGetError:
            return None
    
    async def get_transactions(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get transactions from the database.
        
        Args:
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List of transaction dictionaries
        """
        # Ensure the collection exists
        if not self._db.has_collection('transactions'):
            return []
        
        query = """
        FOR tx IN transactions
        SORT tx.timestamp DESC
        LIMIT @offset, @limit
        RETURN UNSET(tx, '_id', '_key', '_rev')
        """
        
        cursor = self._db.aql.execute(query, bind_vars={'limit': limit, 'offset': offset})
        return [doc for doc in cursor]
    
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
        # Ensure the collection exists
        if not self._db.has_collection('transactions'):
            return []
        
        # Validate sort direction
        if sort_direction not in ["asc", "desc"]:
            sort_direction = "desc"
        
        # Build sorting expression based on direction
        sort_expr = f"tx.{sort_field} {sort_direction.upper()}"
        
        query = f"""
        FOR tx IN transactions
            FILTER tx.chain == @chain
            FILTER tx.from_address == @address OR tx.to_address == @address
            SORT {sort_expr}
            LIMIT @offset, @limit
            RETURN UNSET(tx, '_id', '_key', '_rev')
        """
        
        cursor = self._db.aql.execute(query, bind_vars={
            'address': address,
            'chain': chain,
            'offset': offset,
            'limit': limit
        })
        return [doc for doc in cursor]
    
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
        # Ensure the collection exists
        if not self._db.has_collection('transactions'):
            return []
        
        query = """
        FOR tx IN transactions
        FILTER tx.chain == @chain AND tx.block_number == @block_number
        SORT tx.timestamp DESC
        LIMIT @limit
        RETURN UNSET(tx, '_id', '_key', '_rev')
        """
        
        cursor = self._db.aql.execute(query, bind_vars={
            'chain': chain,
            'block_number': block_number,
            'limit': limit
        })
        return [doc for doc in cursor]
        
    async def get_transaction_by_risk(self, min_risk_score: float = 75.0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get high-risk transactions from the database.
        
        Args:
            min_risk_score: Minimum risk score (0-100)
            limit: Maximum number of transactions to return
            
        Returns:
            List of high-risk transaction dictionaries
        """
        # Ensure the collection exists
        if not self._db.has_collection('transactions'):
            return []
        
        query = """
        FOR tx IN transactions
        FILTER tx.risk_score >= @min_risk_score
        SORT tx.risk_score DESC
        LIMIT @limit
        RETURN UNSET(tx, '_id', '_key', '_rev')
        """
        
        cursor = self._db.aql.execute(query, bind_vars={
            'min_risk_score': min_risk_score,
            'limit': limit
        })
        return [doc for doc in cursor]