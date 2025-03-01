"""Ethereum blockchain connector."""
import asyncio
import logging
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

from web3 import Web3
from web3.exceptions import TransactionNotFound, BlockNotFound

from .base import BlockchainConnector
from ..models.wallet import Wallet
from ..models.transaction import EthereumTransaction
from ..models.contract import EthereumContract
from ..models.event import EthereumEvent

logger = logging.getLogger(__name__)


class EthereumConnector(BlockchainConnector):
    """Ethereum blockchain connector using Web3.py."""
    
    def __init__(self, provider_url: str, api_key: Optional[str] = None, 
                 max_retries: int = 3, retry_delay: float = 0.5):
        """Initialize the connector.
        
        Args:
            provider_url: Web3 provider URL (HTTP or WebSocket)
            api_key: Optional API key for providers that require it
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        self._provider_url = provider_url
        self._api_key = api_key
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._web3 = None
        self._connected = False
        
        # Configure rate limiting
        self._etherscan_rate_limit = 5  # requests per second
        self._etherscan_last_request = 0
        
        # Etherscan API URL
        self._etherscan_api_url = "https://api.etherscan.io/api"
        
        logger.info(f"Initialized Ethereum connector with provider {provider_url}")
    
    async def connect(self) -> None:
        """Connect to the Ethereum blockchain."""
        try:
            # Initialize Web3 (synchronous operation)
            if self._provider_url.startswith(("ws://", "wss://")):
                # Use the Web3 auto provider selection to handle different provider types
                self._web3 = Web3(Web3.WebsocketProvider(self._provider_url))
            else:
                # Use HTTP provider
                self._web3 = Web3(Web3.HTTPProvider(self._provider_url))
            
            # Test connection
            await asyncio.to_thread(self._web3.eth.chain_id)
            self._connected = True
            
            logger.info(f"Connected to Ethereum network, chain ID: {await asyncio.to_thread(self._web3.eth.chain_id)}")
        except Exception as e:
            logger.error(f"Failed to connect to Ethereum network: {e}")
            self._connected = False
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from the Ethereum blockchain."""
        if self._web3 and hasattr(self._web3.provider, 'disconnect'):
            await asyncio.to_thread(self._web3.provider.disconnect)
        
        self._connected = False
        logger.info("Disconnected from Ethereum network")
    
    def is_connected(self) -> bool:
        """Check if connected to the Ethereum blockchain.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connected and self._web3 is not None
    
    async def get_current_block_number(self) -> int:
        """Get current block number.
        
        Returns:
            Current block number
        """
        if not self.is_connected():
            await self.connect()
        
        block_number = await asyncio.to_thread(self._web3.eth.block_number)
        return block_number
    
    async def get_block(self, block_identifier: Union[int, str]) -> Dict[str, Any]:
        """Get block data.
        
        Args:
            block_identifier: Block number or hash
            
        Returns:
            Block data
        """
        if not self.is_connected():
            await self.connect()
        
        for attempt in range(self._max_retries):
            try:
                # Get block with transaction hashes only
                block = await asyncio.to_thread(
                    self._web3.eth.get_block,
                    block_identifier,
                    full_transactions=False
                )
                return dict(block)
            except BlockNotFound:
                logger.warning(f"Block {block_identifier} not found")
                return None
            except Exception as e:
                if attempt < self._max_retries - 1:
                    logger.warning(f"Retrying get_block {block_identifier} after error: {e}")
                    await asyncio.sleep(self._retry_delay)
                else:
                    logger.error(f"Failed to get block {block_identifier}: {e}")
                    raise
    
    async def get_transaction(self, tx_hash: str) -> Optional[EthereumTransaction]:
        """Get transaction by hash.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            EthereumTransaction object or None if not found
        """
        if not self.is_connected():
            await self.connect()
        
        for attempt in range(self._max_retries):
            try:
                # Get transaction and receipt
                tx_data = await asyncio.to_thread(self._web3.eth.get_transaction, tx_hash)
                if not tx_data:
                    return None
                
                receipt_data = await asyncio.to_thread(self._web3.eth.get_transaction_receipt, tx_hash)
                
                # Get block timestamp if block number is available
                timestamp = None
                if tx_data.get('blockNumber'):
                    block_data = await self.get_block(tx_data['blockNumber'])
                    if block_data:
                        timestamp = block_data.get('timestamp')
                
                # Add timestamp to transaction data
                tx_data_dict = dict(tx_data)
                if timestamp:
                    tx_data_dict['timestamp'] = timestamp
                
                # Create transaction object
                transaction = EthereumTransaction.from_web3_transaction(tx_data_dict, dict(receipt_data) if receipt_data else None)
                return transaction
            
            except TransactionNotFound:
                logger.warning(f"Transaction {tx_hash} not found")
                return None
            except Exception as e:
                if attempt < self._max_retries - 1:
                    logger.warning(f"Retrying get_transaction {tx_hash} after error: {e}")
                    await asyncio.sleep(self._retry_delay)
                else:
                    logger.error(f"Failed to get transaction {tx_hash}: {e}")
                    raise
    
    async def get_wallet(self, address: str) -> Optional[Wallet]:
        """Get wallet information.
        
        Args:
            address: Wallet address
            
        Returns:
            Wallet object or None if not found
        """
        if not self.is_connected():
            await self.connect()
        
        for attempt in range(self._max_retries):
            try:
                # Ensure address is valid
                valid_address = await asyncio.to_thread(self._web3.isAddress, address)
                if not valid_address:
                    logger.warning(f"Invalid Ethereum address: {address}")
                    return None
                
                # Convert to checksum address
                checksum_address = await asyncio.to_thread(self._web3.toChecksumAddress, address)
                
                # Get balance
                balance = await asyncio.to_thread(self._web3.eth.get_balance, checksum_address)
                
                # Get code to determine if it's a contract
                code = await asyncio.to_thread(self._web3.eth.get_code, checksum_address)
                wallet_type = "contract" if code and code != "0x" and code != b"0x" else "EOA"
                
                # Get first and last activity through Etherscan API
                first_seen, last_active = await self._get_wallet_activity_times(checksum_address)
                
                # Create wallet object
                wallet = Wallet(
                    address=checksum_address,
                    chain="ethereum",
                    balance=balance,
                    wallet_type=wallet_type,
                    first_seen=first_seen,
                    last_active=last_active
                )
                
                return wallet
            except Exception as e:
                if attempt < self._max_retries - 1:
                    logger.warning(f"Retrying get_wallet {address} after error: {e}")
                    await asyncio.sleep(self._retry_delay)
                else:
                    logger.error(f"Failed to get wallet {address}: {e}")
                    raise
    
    async def get_contract(self, address: str) -> Optional[EthereumContract]:
        """Get contract information.
        
        Args:
            address: Contract address
            
        Returns:
            EthereumContract object or None if not found or not a contract
        """
        if not self.is_connected():
            await self.connect()
        
        for attempt in range(self._max_retries):
            try:
                # Ensure address is valid
                valid_address = await asyncio.to_thread(self._web3.isAddress, address)
                if not valid_address:
                    logger.warning(f"Invalid Ethereum address: {address}")
                    return None
                
                # Convert to checksum address
                checksum_address = await asyncio.to_thread(self._web3.toChecksumAddress, address)
                
                # Get code to determine if it's a contract
                code = await asyncio.to_thread(self._web3.eth.get_code, checksum_address)
                if not code or code == "0x" or code == b"0x":
                    logger.warning(f"Address {checksum_address} is not a contract")
                    return None
                
                # Get contract details from Etherscan
                contract_data = await self._get_contract_from_etherscan(checksum_address)
                
                if contract_data:
                    return EthereumContract.from_etherscan_data(checksum_address, contract_data)
                
                # If Etherscan data not available, create minimal contract object
                return EthereumContract(
                    address=checksum_address,
                    bytecode=code.hex() if isinstance(code, bytes) else code,
                    verified=False
                )
            except Exception as e:
                if attempt < self._max_retries - 1:
                    logger.warning(f"Retrying get_contract {address} after error: {e}")
                    await asyncio.sleep(self._retry_delay)
                else:
                    logger.error(f"Failed to get contract {address}: {e}")
                    raise
    
    async def get_transactions_for_address(self, address: str, 
                                          limit: int = 100, 
                                          offset: int = 0) -> List[EthereumTransaction]:
        """Get transactions for an address.
        
        Args:
            address: Wallet or contract address
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List of EthereumTransaction objects
        """
        if not self.is_connected():
            await self.connect()
        
        # Ensure address is valid
        valid_address = await asyncio.to_thread(self._web3.isAddress, address)
        if not valid_address:
            logger.warning(f"Invalid Ethereum address: {address}")
            return []
        
        # Convert to checksum address
        checksum_address = await asyncio.to_thread(self._web3.toChecksumAddress, address)
        
        # Get transactions from Etherscan
        params = {
            "module": "account",
            "action": "txlist",
            "address": checksum_address,
            "startblock": 0,
            "endblock": 99999999,
            "page": (offset // limit) + 1,
            "offset": limit,
            "sort": "desc",
        }
        
        if self._api_key:
            params["apikey"] = self._api_key
        
        session = aiohttp.ClientSession()
        try:
            async with session:
                # Fetch transactions from Etherscan
                response = await session.get(self._etherscan_api_url, params=params)
                data = await response.json()
                
                if data.get("status") != "1":
                    logger.warning(f"Etherscan API error: {data.get('message')}")
                    return []
                
                transactions = []
                for tx_data in data.get("result", []):
                    try:
                        # Convert string values to appropriate types
                        tx_data_processed = {
                            "hash": tx_data.get("hash", ""),
                            "blockNumber": int(tx_data.get("blockNumber", 0)),
                            "timestamp": int(tx_data.get("timeStamp", 0)),
                            "from": tx_data.get("from", ""),
                            "to": tx_data.get("to", ""),
                            "value": int(tx_data.get("value", 0)),
                            "gas": int(tx_data.get("gas", 0)),
                            "gasPrice": int(tx_data.get("gasPrice", 0)),
                            "input": tx_data.get("input", "0x")
                        }
                        
                        # Get transaction status
                        status = "success"
                        if tx_data.get("isError") == "1":
                            status = "failed"
                        
                        # Create transaction object
                        transaction = EthereumTransaction(
                            hash=tx_data_processed["hash"],
                            block_number=tx_data_processed["blockNumber"],
                            timestamp=tx_data_processed["timestamp"],
                            from_address=tx_data_processed["from"],
                            to_address=tx_data_processed["to"],
                            value=tx_data_processed["value"],
                            gas_limit=tx_data_processed["gas"],
                            gas_price=tx_data_processed["gasPrice"],
                            input_data=tx_data_processed["input"],
                            status=status
                        )
                        
                        transactions.append(transaction)
                    except Exception as e:
                        logger.warning(f"Failed to process transaction: {e}")
                
                return transactions
        except Exception as e:
            logger.error(f"Failed to get transactions for address {address}: {e}")
            return []
    
    async def get_events_for_contract(self, contract_address: str, 
                                     event_name: Optional[str] = None,
                                     from_block: Optional[int] = None,
                                     to_block: Optional[int] = None,
                                     limit: int = 100) -> List[EthereumEvent]:
        """Get events for a contract.
        
        Args:
            contract_address: Contract address
            event_name: Optional event name filter
            from_block: Optional starting block number
            to_block: Optional ending block number
            limit: Maximum number of events to return
            
        Returns:
            List of EthereumEvent objects
        """
        if not self.is_connected():
            await self.connect()
        
        # Ensure address is valid
        valid_address = await asyncio.to_thread(self._web3.isAddress, contract_address)
        if not valid_address:
            logger.warning(f"Invalid Ethereum address: {contract_address}")
            return []
        
        # Convert to checksum address
        checksum_address = await asyncio.to_thread(self._web3.toChecksumAddress, contract_address)
        
        # Get ABI for the contract
        contract_data = await self._get_contract_from_etherscan(checksum_address)
        abi = None
        if contract_data and contract_data.get("ABI"):
            import json
            try:
                abi = json.loads(contract_data["ABI"])
            except (json.JSONDecodeError, TypeError):
                pass
        
        # If we don't have ABI, we can't filter by event name
        if event_name and not abi:
            logger.warning(f"Cannot filter by event name without ABI for contract {checksum_address}")
            event_name = None
        
        # Get events using eth_getLogs
        current_block = await self.get_current_block_number()
        
        # Set default block range
        if from_block is None:
            from_block = current_block - 1000  # Default to last 1000 blocks
            if from_block < 0:
                from_block = 0
        
        if to_block is None:
            to_block = current_block
        
        # Create filter parameters
        filter_params = {
            "address": checksum_address,
            "fromBlock": from_block,
            "toBlock": to_block
        }
        
        # Add event filter if we have ABI and event name
        if abi and event_name:
            # Find the event signature in the ABI
            for item in abi:
                if item.get("type") == "event" and item.get("name") == event_name:
                    # Create event signature
                    inputs = [f"{inp['type']}" for inp in item.get("inputs", [])]
                    signature = f"{event_name}({','.join(inputs)})"
                    
                    # Hash the signature
                    signature_hash = await asyncio.to_thread(
                        self._web3.keccak, text=signature
                    )
                    
                    filter_params["topics"] = [signature_hash.hex()]
                    break
        
        try:
            # Get logs
            logs = await asyncio.to_thread(
                self._web3.eth.get_logs,
                filter_params
            )
            
            events = []
            logs_to_process = logs[:limit]  # Limit number of logs to process
            
            for log in logs_to_process:
                # Get block timestamp
                block_data = await self.get_block(log.get("blockNumber"))
                block_timestamp = block_data.get("timestamp") if block_data else None
                
                # Create event object
                event = EthereumEvent.from_web3_log(dict(log), block_timestamp)
                events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Failed to get events for contract {contract_address}: {e}")
            return []
    
    async def _get_wallet_activity_times(self, address: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get first seen and last active timestamps for a wallet.
        
        Args:
            address: Wallet address
            
        Returns:
            Tuple of (first_seen, last_active) as datetime objects or None
        """
        # Get first transaction
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": 1,
            "sort": "asc",
        }
        
        if self._api_key:
            params["apikey"] = self._api_key
        
        first_seen = None
        last_active = None
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get first transaction
                async with session.get(self._etherscan_api_url, params=params) as response:
                    data = await response.json()
                    
                    if data.get("status") == "1" and data.get("result"):
                        timestamp = int(data["result"][0]["timeStamp"])
                        first_seen = datetime.fromtimestamp(timestamp)
                
                # Get latest transaction
                params["sort"] = "desc"
                async with session.get(self._etherscan_api_url, params=params) as response:
                    data = await response.json()
                    
                    if data.get("status") == "1" and data.get("result"):
                        timestamp = int(data["result"][0]["timeStamp"])
                        last_active = datetime.fromtimestamp(timestamp)
                
                return first_seen, last_active
        except Exception as e:
            logger.warning(f"Failed to get wallet activity times for {address}: {e}")
            return None, None
    
    async def _get_contract_from_etherscan(self, address: str) -> Optional[Dict[str, Any]]:
        """Get contract details from Etherscan.
        
        Args:
            address: Contract address
            
        Returns:
            Contract data or None if not found
        """
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": address,
        }
        
        if self._api_key:
            params["apikey"] = self._api_key
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._etherscan_api_url, params=params) as response:
                    data = await response.json()
                    
                    if data.get("status") == "1" and data.get("result"):
                        return data["result"][0]
        except Exception as e:
            logger.warning(f"Failed to get contract from Etherscan for {address}: {e}")
        
        return None