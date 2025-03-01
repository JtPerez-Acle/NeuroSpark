"""Blockchain database interface module."""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

class DatabaseInterface(ABC):
    """Abstract base class for blockchain database operations."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    async def store_wallet(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a wallet in the database."""
        pass
    
    @abstractmethod
    async def store_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a transaction in the database."""
        pass
    
    # Legacy interface support - implementations can override this if needed
    async def store_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy method for storing interactions, now maps to transactions."""
        return await self.store_transaction(interaction_data)
    
    @abstractmethod
    async def store_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a smart contract in the database."""
        pass
    
    @abstractmethod
    async def store_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a blockchain event in the database."""
        pass
    
    @abstractmethod
    async def get_wallet(self, address: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get a wallet by address."""
        pass
    
    @abstractmethod
    async def get_wallets(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all wallets with pagination."""
        pass
    
    @abstractmethod
    async def get_transaction(self, tx_hash: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get a transaction by hash."""
        pass
    
    @abstractmethod
    async def get_transactions(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all transactions with pagination."""
        pass
    
    @abstractmethod
    async def get_wallet_transactions(self, address: str, chain: str = "ethereum", 
                                     limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get transactions for a wallet."""
        pass
    
    @abstractmethod
    async def get_contract(self, address: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get a contract by address."""
        pass
    
    @abstractmethod
    async def get_contracts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all contracts with pagination."""
        pass
    
    @abstractmethod
    async def get_contract_events(self, address: str, chain: str = "ethereum", 
                                limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get events for a contract."""
        pass
    
    @abstractmethod
    async def clear_database(self) -> Dict[str, Any]:
        """Clear all data from the database."""
        pass
