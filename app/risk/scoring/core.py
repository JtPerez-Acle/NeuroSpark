"""Core risk scoring algorithms."""
import logging
from typing import Dict, Any, List, Optional
import math

logger = logging.getLogger(__name__)

def calculate_wallet_risk(wallet_data: Dict[str, Any]) -> float:
    """Calculate risk score for a wallet.
    
    Risk factors include:
    - Transaction patterns (frequency, volume, etc.)
    - Network behavior (centrality, interaction patterns)
    - Historical associations (with known risky entities)
    - Age of wallet
    
    Args:
        wallet_data: Dictionary containing wallet data
        
    Returns:
        Risk score between 0 and 100
    """
    try:
        # Base risk score
        risk_score = 0.0
        
        # Risk factor: Wallet type
        wallet_type = wallet_data.get('type', 'unknown')
        if wallet_type == 'unknown':
            risk_score += 20.0  # Unknown wallet types are higher risk
        elif wallet_type == 'EOA':
            risk_score += 10.0  # Basic EOA risk
        elif wallet_type == 'contract':
            risk_score += 15.0  # Contracts have higher base risk than EOAs
            
        # Risk factor: Known tags/labels
        tags = wallet_data.get('tags', [])
        for tag in tags:
            if tag.lower() in ['scam', 'phishing', 'hack', 'exploit', 'suspicious']:
                risk_score += 50.0  # High risk for known bad actors
                break
                
        # Risk factor: Age of wallet
        if wallet_data.get('first_seen') and wallet_data.get('last_active'):
            # New wallets are higher risk
            first_seen = wallet_data.get('first_seen')
            if first_seen:
                # Simple logic - newer wallets are riskier
                # More sophisticated time-based calculations would be implemented in a real system
                risk_score += 10.0  # Default addition for new wallets
                
        # Risk factor: Transaction count and frequency
        # In a real system, you would calculate this from transaction history data
        # Since we don't have that here, we'll use a placeholder
        tx_count = wallet_data.get('tx_count', 0)
        if tx_count < 5:
            risk_score += 15.0  # Very few transactions is suspicious
        
        # Risk factor: Network behavior
        # In a real system, this would come from graph analysis results
        # We'll use placeholder values here
        network_risk = wallet_data.get('network_risk', 0.0)
        risk_score += network_risk
        
        # Blockchain-specific risk factors
        chain = wallet_data.get('chain', 'ethereum').lower()
        
        # Ethereum-specific risk factors
        if chain == 'ethereum':
            # High-value wallets are higher risk targets
            balance = float(wallet_data.get('balance', 0))
            if balance > 100 * 10**18:  # >100 ETH
                risk_score += 15.0  # High-value wallet
            elif balance > 10 * 10**18:  # >10 ETH
                risk_score += 5.0  # Medium-value wallet
                
            # No activity for a long time then sudden activity is suspicious
            if wallet_data.get('last_active') and wallet_data.get('first_seen'):
                # This would be a more sophisticated calculation in a real system
                pass
        
        # Cap the risk score at 100
        risk_score = min(100.0, risk_score)
        
        return risk_score
    
    except Exception as e:
        logger.error(f"Error calculating wallet risk score: {e}")
        return 0.0  # Default to zero risk in case of error

def calculate_transaction_risk(transaction_data: Dict[str, Any]) -> float:
    """Calculate risk score for a transaction.
    
    Risk factors include:
    - Transaction value (unusual amounts)
    - Gas used/price (unusual settings)
    - Sender/receiver risk scores
    - Pattern matching (similarity to known fraud patterns)
    
    Args:
        transaction_data: Dictionary containing transaction data
        
    Returns:
        Risk score between 0 and 100
    """
    try:
        # Base risk score
        risk_score = 0.0
        
        # Risk factor: Value
        value = float(transaction_data.get('value', 0))
        if value > 1000000000000000000 * 100:  # >100 ETH
            risk_score += 20.0  # Large transactions are higher risk
        elif value > 1000000000000000000 * 10:  # >10 ETH
            risk_score += 10.0
            
        # Risk factor: Gas price/usage
        gas_price = float(transaction_data.get('gas_price', 0))
        gas_used = float(transaction_data.get('gas_used', 0))
        
        if gas_price > 0 and gas_price * gas_used > 1000000000000000000:  # >1 ETH in gas
            risk_score += 15.0  # High gas cost is suspicious
            
        # Risk factor: Status
        status = transaction_data.get('status', 'unknown')
        if status != 'success':
            risk_score += 10.0  # Failed transactions are more suspicious
            
        # Risk factor: Sender/receiver risk
        # In a real system, you would look up the risk scores of the wallet entities
        from_address = transaction_data.get('from_address', transaction_data.get('from', ''))
        to_address = transaction_data.get('to_address', transaction_data.get('to', ''))
        
        # Add placeholder values for sender/receiver risk
        # In a production system, these would be retrieved from the database
        sender_risk = transaction_data.get('sender_risk', 0.0)
        receiver_risk = transaction_data.get('receiver_risk', 0.0)
        
        # Known high-risk addresses (would be from a database in a real system)
        high_risk_addresses = [
            "0x0000000000000000000000000000000000000000",  # Zero address (token burn)
            "0xdead000000000000000000000000000000000000",  # Dead address
        ]
        
        # Check for suspicious addresses
        if from_address in high_risk_addresses or to_address in high_risk_addresses:
            risk_score += 30.0  # Suspicious address involvement
        
        # Apply entity risk contribution (at most 50% from entity risk)
        risk_score += max(sender_risk, receiver_risk) * 0.5
        
        # Risk factor: Input data complexity
        # Complex input data might indicate complex contract interactions
        input_data = transaction_data.get('input_data', '')
        if input_data and len(input_data) > 1000:
            risk_score += 10.0  # Complex contract calls
            
        # Risk factor: Chain-specific
        chain = transaction_data.get('chain', 'ethereum').lower()
        if chain == 'ethereum':
            # Add Ethereum-specific risk factors
            
            # Smart contract interaction (check for input data)
            if input_data and input_data != '0x':
                # Interaction with contract
                if len(input_data) > 10000:
                    risk_score += 15.0  # Very complex contract interaction
                elif len(input_data) > 5000:
                    risk_score += 8.0  # Moderately complex contract interaction
            
            # Token transfers often have suspicious patterns
            if input_data and input_data.startswith('0xa9059cbb'):  # ERC20 transfer
                risk_score += 5.0  # Base risk for token transfers
        
        # Cap the risk score at 100
        risk_score = min(100.0, risk_score)
        
        return risk_score
    
    except Exception as e:
        logger.error(f"Error calculating transaction risk score: {e}")
        return 0.0  # Default to zero risk in case of error

def calculate_contract_risk(contract_data: Dict[str, Any]) -> float:
    """Calculate risk score for a smart contract.
    
    Risk factors include:
    - Code verification status
    - Known vulnerabilities
    - Creator wallet risk
    - Contract age
    - Interaction patterns
    
    Args:
        contract_data: Dictionary containing contract data
        
    Returns:
        Risk score between 0 and 100
    """
    try:
        # Base risk score
        risk_score = 20.0  # Contracts start with a higher base risk
        
        # Risk factor: Verified status
        verified = contract_data.get('verified', False)
        if not verified:
            risk_score += 25.0  # Unverified contracts are much riskier
            
        # Risk factor: Known vulnerabilities
        vulnerabilities = contract_data.get('vulnerabilities', [])
        if vulnerabilities:
            # Calculate risk based on vulnerability count and severity
            vuln_count = len(vulnerabilities)
            
            # Severity weights
            severity_weights = {
                'critical': 10.0,
                'high': 7.0,
                'medium': 4.0,
                'low': 1.0
            }
            
            # Calculate weighted risk from vulnerabilities
            vuln_risk = 0.0
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'medium')
                vuln_risk += severity_weights.get(severity, 4.0)
                
            # Cap vulnerability risk at 40
            vuln_risk = min(40.0, vuln_risk)
            risk_score += vuln_risk
            
        # Risk factor: Creator risk
        # In a real system, you would look up the creator's risk score
        creator = contract_data.get('creator', '')
        creator_risk = contract_data.get('creator_risk', 0.0)
        
        # Known high-risk creators (would be from a database in a real system)
        high_risk_creators = [
            "0x0000000000000000000000000000000000000000",  # Zero address
        ]
        
        if creator in high_risk_creators:
            risk_score += 30.0  # Suspicious creator
        else:
            risk_score += creator_risk * 0.3  # Contribute at most 30% from creator risk
        
        # Risk factor: Contract age
        if contract_data.get('creation_timestamp'):
            creation_time = contract_data.get('creation_timestamp')
            # In a real system, calculate age properly based on timestamp
            # For now, just add a default risk for new contracts
            risk_score += 10.0
            
        # Risk factor: Contract type/characteristics
        contract_type = contract_data.get('contract_type', 'unknown')
        if contract_type == 'unknown':
            risk_score += 15.0
        elif contract_type in ['proxy', 'upgrade']:
            risk_score += 10.0  # Upgradeable contracts have extra risk
        
        # Risk factor: Chain-specific
        chain = contract_data.get('chain', 'ethereum').lower()
        if chain == 'ethereum':
            # Ethereum-specific contract analysis
            
            # Contract bytecode analysis
            bytecode = contract_data.get('bytecode', '')
            if bytecode:
                # Check for selfdestruct opcode (dangerous)
                if 'ff' in bytecode:  # Simplified check - real analysis would be more complex
                    risk_score += 15.0  # Self-destruct capability
                
                # Check for delegate call (often used in exploits)
                if 'f4' in bytecode:  # Simplified check for DELEGATECALL opcode
                    risk_score += 10.0  # Delegate call capability
            
            # Check for common risk patterns in ABI
            abi = contract_data.get('abi', [])
            if abi:
                # Look for admin functions, overloaded transfer functions, etc.
                for func in abi:
                    if isinstance(func, dict) and func.get('type') == 'function':
                        name = func.get('name', '').lower()
                        if name in ['withdraw', 'selfdestruct', 'suicide', 'transferownership']:
                            risk_score += 5.0  # Sensitive function
        
        # Cap the risk score at 100
        risk_score = min(100.0, risk_score)
        
        return risk_score
    
    except Exception as e:
        logger.error(f"Error calculating contract risk score: {e}")
        return 0.0  # Default to zero risk in case of error