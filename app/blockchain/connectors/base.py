"""Base blockchain connector interface."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from ..models.wallet import Wallet
from ..models.transaction import Transaction
from ..models.contract import Contract
from ..models.event import Event


class BlockchainConnector(ABC):
    """Abstract base class for blockchain connectors."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the blockchain."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the blockchain."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the blockchain.
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_transaction(self, tx_hash: str) -> Optional[Transaction]:
        """Get transaction by hash.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction object or None if not found
        """
        pass
    
    @abstractmethod
    async def get_wallet(self, address: str) -> Optional[Wallet]:
        """Get wallet information.
        
        Args:
            address: Wallet address
            
        Returns:
            Wallet object or None if not found
        """
        pass
    
    @abstractmethod
    async def get_contract(self, address: str) -> Optional[Contract]:
        """Get contract information.
        
        Args:
            address: Contract address
            
        Returns:
            Contract object or None if not found
        """
        pass
    
    @abstractmethod
    async def get_transactions_for_address(self, address: str, 
                                           limit: int = 100, 
                                           offset: int = 0) -> List[Transaction]:
        """Get transactions for an address.
        
        Args:
            address: Wallet or contract address
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List of transactions
        """
        pass
    
    @abstractmethod
    async def get_events_for_contract(self, contract_address: str, 
                                     event_name: Optional[str] = None,
                                     from_block: Optional[int] = None,
                                     to_block: Optional[int] = None,
                                     limit: int = 100) -> List[Event]:
        """Get events for a contract.
        
        Args:
            contract_address: Contract address
            event_name: Optional event name filter
            from_block: Optional starting block number
            to_block: Optional ending block number
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        pass
    
    @abstractmethod
    async def get_current_block_number(self) -> int:
        """Get current block number.
        
        Returns:
            Current block number
        """
        pass